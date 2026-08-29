from __future__ import annotations

from pathlib import Path

import pygame

from rg_core.data import HEX_SIZE
from rg_ui import map_camera_lock
from rg_world import map as world_map


_INSTALLED = False
_ORIGINAL_TERRAIN_SCALER = map_camera_lock._scaled_terrain_texture
_ASSET_CACHE = {}
_COMPOSITE_CACHE = {}
_OVERLAY_CACHE = {}
_PENDING_OVERLAYS = {"hover": None, "selected": None}
_FRAME_OPEN = False
_LAST_CAMERA = None

ROOT_DIR = Path(__file__).resolve().parents[1]
HOVER_ASSET = ROOT_DIR / "Grafiki" / "Grafiki UI" / "hover_hex.png"
SELECTED_ASSET = ROOT_DIR / "Grafiki" / "Grafiki UI" / "click_hex.png"

# Logiczny rozmiar heksa pozostaje bez zmian. Pomniejszamy wyłącznie grafikę
# terenu, aby między sąsiadami została cienka szczelina na stan interakcji.
GAP_FACTOR = 0.009
GAP_MIN_PX = 2
GAP_MAX_PX = 8
NORMAL_GAP_COLOR = (12, 9, 6, 255)


def _gap_inset(size: int) -> int:
    return max(GAP_MIN_PX, min(GAP_MAX_PX, int(round(size * GAP_FACTOR))))


def _load_asset(mode: str):
    path = SELECTED_ASSET if mode == "selected" else HOVER_ASSET
    key = str(path)
    if key in _ASSET_CACHE:
        return _ASSET_CACHE[key]

    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except (OSError, pygame.error):
        image = None

    _ASSET_CACHE[key] = image
    return image


def _hex_points(size: int, radius: float):
    center = size / 2.0
    return [
        (int(x), int(y))
        for x, y in world_map.hex_corners(center, center, max(1.0, radius))
    ]


def _hex_background(size: int) -> pygame.Surface:
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.polygon(
        surface,
        NORMAL_GAP_COLOR,
        _hex_points(size, size / 2.0 - 1.0),
    )
    return surface


def _scaled_terrain_with_gap(textures, terrain_key, size):
    """Normalny kafel z cienką ciemną szczeliną wokół assetu terenu."""
    source = textures.get(terrain_key)
    size = max(1, int(size))

    cached = _COMPOSITE_CACHE.get(terrain_key)
    if cached is not None and cached[0] == size and cached[1] is source:
        return cached[2]

    inset = _gap_inset(size)
    inner_size = max(1, size - inset * 2)
    composite = _hex_background(size)

    terrain = _ORIGINAL_TERRAIN_SCALER(textures, terrain_key, inner_size)
    offset = (size - inner_size) // 2
    composite.blit(terrain, (offset, offset))

    _COMPOSITE_CACHE[terrain_key] = (size, source, composite)
    return composite


def _scaled_overlay_asset(mode: str, size: int):
    """Skaluje cały dostarczony PNG bez dodatkowego wycinania jego ramy."""
    asset = _load_asset(mode)
    if asset is None:
        return None

    size = max(1, int(size))
    cache_key = (mode, size, id(asset))
    cached = _OVERLAY_CACHE.get(cache_key)
    if cached is not None:
        return cached

    if asset.get_size() == (size, size):
        rendered = asset.copy()
    else:
        rendered = pygame.transform.smoothscale(asset, (size, size))

    _OVERLAY_CACHE[cache_key] = rendered
    return rendered


def _begin_map_frame():
    global _FRAME_OPEN
    _PENDING_OVERLAYS["hover"] = None
    _PENDING_OVERLAYS["selected"] = None
    _FRAME_OPEN = True


def _queue_overlay(tile, hovered: bool, selected: bool):
    global _FRAME_OPEN
    if not _FRAME_OPEN:
        _begin_map_frame()

    if selected:
        _PENDING_OVERLAYS["selected"] = tile
        if _PENDING_OVERLAYS.get("hover") is tile:
            _PENDING_OVERLAYS["hover"] = None
    elif hovered:
        _PENDING_OVERLAYS["hover"] = tile


def draw_hex_state_overlays(screen, camera=None):
    """Rysuje PNG hover/selected jako osobną końcową warstwę mapy."""
    global _FRAME_OPEN
    camera = camera or _LAST_CAMERA
    if not _FRAME_OPEN or camera is None:
        return

    # Hover najpierw, selected jako ostatni stan mapy.
    for mode in ("hover", "selected"):
        tile = _PENDING_OVERLAYS.get(mode)
        if tile is None:
            continue
        if mode == "hover" and tile is _PENDING_OVERLAYS.get("selected"):
            continue

        size = max(1, int(HEX_SIZE * 2 * camera.zoom))
        overlay = _scaled_overlay_asset(mode, size)
        if overlay is None:
            continue

        sx, sy = tile.center(camera)
        screen.blit(overlay, overlay.get_rect(center=(int(sx), int(sy))))

    _PENDING_OVERLAYS["hover"] = None
    _PENDING_OVERLAYS["selected"] = None
    _FRAME_OPEN = False


def install_hex_selection_theme():
    """Instaluje assetowe hover/klik bez programowych obrysów.

    W poprzedniej wersji flush warstwy był ukryty w ``HeroToken.draw``. To było
    kruche, bo pionek jest wielokrotnie opakowywany przez inne moduły UI.
    Teraz Tile.draw wyłącznie zapamiętuje stan, a finalny PNG jest jawnie
    rysowany tuż przed HUD-em gry. Oznacza to: wszystkie heksy i pionki są już
    gotowe, więc żaden sąsiad nie może zasłonić ramy.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    current_tile_draw = world_map.Tile.draw
    map_camera_lock._scaled_terrain_texture = _scaled_terrain_with_gap

    def tile_draw_with_asset_state(
        self,
        screen,
        textures,
        camera,
        font,
        hovered=False,
        selected=False,
        valid_move=False,
    ):
        global _LAST_CAMERA
        _LAST_CAMERA = camera
        _queue_overlay(self, hovered, selected)

        # Wygląd interakcji pochodzi wyłącznie z PNG. Nie przepuszczamy starych
        # niebieskich/złotych programowych outline'ów ani valid_move.
        return current_tile_draw(
            self,
            screen,
            textures,
            camera,
            font,
            hovered=False,
            selected=False,
            valid_move=False,
        )

    tile_draw_with_asset_state._rise_glory_hex_asset_states = True
    world_map.Tile.draw = tile_draw_with_asset_state

    # production_hud jest instalowany chwilę PO tym module w main.py. Podmieniamy
    # więc jego funkcję wejściową już teraz. Kiedy install_production_hud(_app)
    # przypisze ją do aplikacji, będzie to właśnie ten wrapper.
    from rg_ui import production_hud

    current_game_ui_draw = production_hud.draw_game_ui_with_production

    def draw_game_ui_after_hex_overlays(screen, *args, **kwargs):
        draw_hex_state_overlays(screen, _LAST_CAMERA)
        return current_game_ui_draw(screen, *args, **kwargs)

    draw_game_ui_after_hex_overlays._rise_glory_hex_overlay_flush = True
    production_hud.draw_game_ui_with_production = draw_game_ui_after_hex_overlays

    _INSTALLED = True