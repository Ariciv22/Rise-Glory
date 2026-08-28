from __future__ import annotations

from pathlib import Path

import pygame

from rg_ui import map_camera_lock
from rg_world import map as world_map


_INSTALLED = False
_ACTIVE_MODE = "normal"
_ORIGINAL_TERRAIN_SCALER = map_camera_lock._scaled_terrain_texture
_ASSET_CACHE = {}
_COMPOSITE_CACHE = {}

ROOT_DIR = Path(__file__).resolve().parents[1]
HOVER_ASSET = ROOT_DIR / "Grafiki" / "Grafiki UI" / "hex_hover.png"
SELECTED_ASSET = ROOT_DIR / "Grafiki" / "Grafiki UI" / "hex_selected.png"

# Wizualna grafika heksa jest lekko mniejsza od jego logicznego hitboxa.
# Przy duzym przyblizeniu daje to ok. kilkanascie pikseli szczeliny miedzy
# sasiednimi kaflami, ale nie zmienia ruchu, klikniecia ani pozycji znacznikow.
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


def _hex_background(size: int) -> pygame.Surface:
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    radius = max(1.0, size / 2.0 - 1.0)
    points = [
        (int(x), int(y))
        for x, y in world_map.hex_corners(size / 2.0, size / 2.0, radius)
    ]
    pygame.draw.polygon(surface, NORMAL_GAP_COLOR, points)
    return surface


def _scaled_terrain_with_state(textures, terrain_key, size):
    """Buduje gotowy kafel: stan pod spodem + pomniejszony oryginalny heks."""
    mode = _ACTIVE_MODE if _ACTIVE_MODE in {"hover", "selected"} else "normal"
    source = textures.get(terrain_key)
    cache_key = (terrain_key, int(size), mode, id(source))
    cached = _COMPOSITE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    size = max(1, int(size))
    inset = _gap_inset(size)
    inner_size = max(1, size - inset * 2)

    # Zawsze zostawiamy mala, ciemna szczeline. Dla hover/selected w te sama
    # szczeline trafia odpowiedni PNG, ale srodek grafiki jest przykryty
    # pomniejszonym normalnym heksem.
    composite = _hex_background(size)

    if mode in {"hover", "selected"}:
        asset = _load_asset(mode)
        if asset is not None:
            if asset.get_size() == (size, size):
                state_surface = asset
            else:
                state_surface = pygame.transform.smoothscale(asset, (size, size))
            composite.blit(state_surface, (0, 0))

    terrain = _ORIGINAL_TERRAIN_SCALER(textures, terrain_key, inner_size)
    offset = (size - inner_size) // 2
    composite.blit(terrain, (offset, offset))

    _COMPOSITE_CACHE[cache_key] = composite
    return composite


def install_hex_selection_theme():
    """Instaluje assetowe stany hover/klik bez technicznych obrysow.

    Logiczny heks zachowuje dotychczasowy rozmiar. Zmniejszana jest tylko jego
    grafika, a pod nia znajduje sie ciemna szczelina. Na hover w szczelinie
    pojawia sie ``hex_hover.png``, a po kliknieciu ``hex_selected.png``.
    """
    global _INSTALLED, _ACTIVE_MODE
    if _INSTALLED:
        return

    current_tile_draw = world_map.Tile.draw
    map_camera_lock._scaled_terrain_texture = _scaled_terrain_with_state

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
        global _ACTIVE_MODE
        previous_mode = _ACTIVE_MODE
        if selected:
            _ACTIVE_MODE = "selected"
        elif hovered:
            _ACTIVE_MODE = "hover"
        else:
            _ACTIVE_MODE = "normal"

        try:
            # Bazowy renderer nie dostaje zadnych flag wizualnych, wiec nie
            # wracaja stare niebieskie/zolte linie ani highlight ruchu.
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
        finally:
            _ACTIVE_MODE = previous_mode

    tile_draw_with_asset_state._rise_glory_hex_asset_states = True
    world_map.Tile.draw = tile_draw_with_asset_state
    _INSTALLED = True
