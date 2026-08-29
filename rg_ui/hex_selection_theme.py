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

ROOT_DIR = Path(__file__).resolve().parents[1]
HOVER_ASSET = ROOT_DIR / "Grafiki" / "Grafiki UI" / "hex_hover.png"
SELECTED_ASSET = ROOT_DIR / "Grafiki" / "Grafiki UI" / "hex_selected.png"

# Wizualna grafika heksa jest lekko mniejsza od jego logicznego hitboxa.
# Powstaje dzieki temu waska, ciemna szczelina, w ktorej pokazujemy osobny
# asset hover/selected. Logika ruchu, klikniecia i pozycje znacznikow zostaja
# bez zmian.
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
    """Buduje normalny kafel z mala ciemna szczelina dookola grafiki.

    Assety hover/selected nie sa juz skladane bezposrednio z pojedynczym
    kaflem. Gdy robilismy to tutaj, kolejne heksy renderowane w petli mogly
    przykrywac ich boki. Warstwa interakcji jest teraz odkladana na pozniej.
    """
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


def _scaled_overlay_ring(mode: str, size: int):
    """Zwraca PNG przyciety wylacznie do szczeliny przy krawedzi heksa."""
    asset = _load_asset(mode)
    if asset is None:
        return None

    size = max(1, int(size))
    inset = _gap_inset(size)
    cache_key = (mode, size, inset, id(asset))
    cached = _OVERLAY_CACHE.get(cache_key)
    if cached is not None:
        return cached

    if asset.get_size() == (size, size):
        rendered = asset.copy()
    else:
        rendered = pygame.transform.smoothscale(asset, (size, size))

    # Przycinamy asset do pierscienia odpowiadajacego faktycznej szczelinie.
    # Dzieki temu warstwa moze byc rysowana NA KONCU i nadal nigdy nie przykrywa
    # krajobrazu wewnatrz kafla.
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    outer_radius = max(1.0, size / 2.0 - 1.0)
    inner_radius = max(1.0, outer_radius - inset)
    pygame.draw.polygon(mask, (255, 255, 255, 255), _hex_points(size, outer_radius))
    pygame.draw.polygon(mask, (0, 0, 0, 0), _hex_points(size, inner_radius))
    rendered.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

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


def draw_hex_state_overlays(screen, camera):
    """Rysuje hover/selected dopiero po narysowaniu WSZYSTKICH heksow.

    Funkcja jest odpalana tuz przed pierwszym pionkiem bohatera. W glownej
    petli gry pionki sa renderowane bezposrednio po petli kafli, wiec jest to
    bezpieczny punkt: zaden sasiedni heks nie moze juz przykryc obramowania,
    a pionki nadal pozostaja nad nim.
    """
    global _FRAME_OPEN
    if not _FRAME_OPEN:
        return

    # Selected jest wazniejsze wizualnie, dlatego rysujemy je jako ostatnie.
    for mode in ("hover", "selected"):
        tile = _PENDING_OVERLAYS.get(mode)
        if tile is None:
            continue
        if mode == "hover" and tile is _PENDING_OVERLAYS.get("selected"):
            continue

        size = max(1, int(HEX_SIZE * 2 * camera.zoom))
        overlay = _scaled_overlay_ring(mode, size)
        if overlay is None:
            continue

        sx, sy = tile.center(camera)
        rect = overlay.get_rect(center=(int(sx), int(sy)))
        screen.blit(overlay, rect)

    _PENDING_OVERLAYS["hover"] = None
    _PENDING_OVERLAYS["selected"] = None
    _FRAME_OPEN = False


def install_hex_selection_theme():
    """Instaluje assetowe stany hover/klik bez technicznych obrysow.

    Kazdy heks ma stale niewielka szczeline. Podczas petli kafli tylko
    zapamietujemy, ktory heks jest hover/selected. Wlasciwe PNG sa rysowane
    dopiero po wszystkich kaflach, przed pionkami, wiec sasiad nie moze ich
    juz zaslonic.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    current_tile_draw = world_map.Tile.draw
    current_token_draw = world_map.HeroToken.draw
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
        # Tile ID 1 jest pierwszym kaflem generowanej rozety. Reset w tym
        # miejscu zabezpiecza tez sytuacje, w ktorej poprzednia klatka nie
        # doszla do renderowania pionkow.
        if int(getattr(self, "id", -1)) == 1:
            _begin_map_frame()
        _queue_overlay(self, hovered, selected)

        # Bazowy renderer nie dostaje zadnych flag wizualnych, wiec nie wracaja
        # stare niebieskie/zolte linie ani highlight mozliwego ruchu.
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

    def token_draw_after_hex_overlays(
        self,
        screen,
        camera,
        font,
        selected=False,
    ):
        # W app.py tokeny sa rysowane bezposrednio po calej petli tile.draw.
        # Pierwszy token sluzy wiec jako pewny flush odroczonej warstwy stanu.
        draw_hex_state_overlays(screen, camera)
        return current_token_draw(
            self,
            screen,
            camera,
            font,
            selected=selected,
        )

    tile_draw_with_asset_state._rise_glory_hex_asset_states = True
    token_draw_after_hex_overlays._rise_glory_hex_overlay_flush = True
    world_map.Tile.draw = tile_draw_with_asset_state
    world_map.HeroToken.draw = token_draw_after_hex_overlays
    _INSTALLED = True
