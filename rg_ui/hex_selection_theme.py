from __future__ import annotations

import math

import pygame

from rg_core.data import HEX_SIZE
from rg_world import map as world_map


_INSTALLED = False
_SOURCE_OVERLAY_CACHE = {}
_SCALED_OVERLAY_CACHE = {}
_SIDE_BAND_CACHE = {}
_SCALED_SIDE_OVERLAY_CACHE = {}
_PENDING = {
    "hovered": None,
    "selected": None,
    "screen": None,
    "textures": None,
    "camera": None,
    "flushed": False,
}

# Nie dodajemy nowej ramy na grafike heksa. Podswietlamy tylko cieple,
# metaliczne piksele istniejacej zlotej ramy zapisanej juz w assetcie terenu.
FRAME_RING_INNER_FACTOR = 0.84

# Hover ma byc wyrazny od razu po najechaniu: prawie biale, cieple zloto.
HOVER_TINT = (255, 249, 214)
HOVER_ALPHA_RANGE = (105, 192)

# Klikniety heks ma spokojniejsza baze, a mocniejszy efekt przechodzi po
# CALYCH bokach ramy. Nie rysujemy juz szesciu swiecacych punktow.
SELECTED_TINT = (255, 180, 68)
SELECTED_ALPHA_RANGE = (66, 124)
SELECTED_SIDE_TINT = (255, 235, 164)
SELECTED_SIDE_ALPHA_RANGE = (150, 235)

# Ta maska sluzy tylko do wybrania fragmentu ISTNIEJACEJ ramy. Sama linia
# nigdy nie jest renderowana, wiec nic nie nachodzi na krajobraz heksa.
SIDE_BAND_WIDTH_FACTOR = 0.18


def _reset_pending():
    _PENDING["hovered"] = None
    _PENDING["selected"] = None
    _PENDING["screen"] = None
    _PENDING["textures"] = None
    _PENDING["camera"] = None
    _PENDING["flushed"] = False


def _looks_like_frame_gold(color):
    r, g, b, a = color
    if a < 70:
        return False
    if r < 88 or g < 50 or b > 150:
        return False
    # Zloto / braz ramy jest wyraznie cieplejsze od tla. Warunek zostawia
    # czarne kontury nietkniete, wiec oryginalna plastyka ramy nadal zostaje.
    return (r - g) >= 16 and (g - b) >= 8 and (r - b) >= 48


def _frame_ring_mask(size):
    width, height = size
    ring_surface = pygame.Surface(size, pygame.SRCALPHA)
    radius = max(1.0, min(width, height) / 2.0 - 2.0)
    center_x = width / 2.0
    center_y = height / 2.0

    outer = [
        (int(x), int(y))
        for x, y in world_map.hex_corners(center_x, center_y, radius)
    ]
    inner = [
        (int(x), int(y))
        for x, y in world_map.hex_corners(
            center_x,
            center_y,
            radius * FRAME_RING_INNER_FACTOR,
        )
    ]
    pygame.draw.polygon(ring_surface, (255, 255, 255, 255), outer)
    pygame.draw.polygon(ring_surface, (0, 0, 0, 0), inner)
    return pygame.mask.from_surface(ring_surface, 16)


def _source_frame_overlay(source, mode):
    key = (id(source), source.get_size(), mode)
    cached = _SOURCE_OVERLAY_CACHE.get(key)
    if cached is not None:
        return cached

    size = source.get_size()
    ring_mask = _frame_ring_mask(size)
    overlay = pygame.Surface(size, pygame.SRCALPHA)

    if mode == "hover":
        tint = HOVER_TINT
        min_alpha, max_alpha = HOVER_ALPHA_RANGE
    elif mode == "selected_side":
        tint = SELECTED_SIDE_TINT
        min_alpha, max_alpha = SELECTED_SIDE_ALPHA_RANGE
    else:
        tint = SELECTED_TINT
        min_alpha, max_alpha = SELECTED_ALPHA_RANGE

    width, height = size
    for y in range(height):
        for x in range(width):
            if not ring_mask.get_at((x, y)):
                continue
            color = source.get_at((x, y))
            if not _looks_like_frame_gold(color):
                continue

            brightness = (color.r + color.g + color.b) / 3.0
            strength = max(0.0, min(1.0, (brightness - 75.0) / 170.0))
            alpha = int(min_alpha + (max_alpha - min_alpha) * strength)
            overlay.set_at((x, y), (*tint, alpha))

    _SOURCE_OVERLAY_CACHE[key] = overlay
    return overlay


def _scaled_frame_overlay(textures, terrain_key, size, mode):
    source = textures.get(terrain_key)
    if source is None:
        return None

    cache_key = (terrain_key, mode)
    cached = _SCALED_OVERLAY_CACHE.get(cache_key)
    if cached is not None and cached[0] == size and cached[1] is source:
        return cached[2]

    base = _source_frame_overlay(source, mode)
    if base.get_size() == (size, size):
        scaled = base
    else:
        scaled = pygame.transform.smoothscale(base, (size, size))
    _SCALED_OVERLAY_CACHE[cache_key] = (size, source, scaled)
    return scaled


def _side_band_surface(size, side_index):
    """Maska jednego boku heksa; sluzy tylko do wyciecia zlota z assetu."""
    key = (size, int(side_index) % 6)
    cached = _SIDE_BAND_CACHE.get(key)
    if cached is not None:
        return cached

    width, height = size
    surface = pygame.Surface(size, pygame.SRCALPHA)
    radius = max(1.0, min(width, height) / 2.0 - 2.0)
    center_x = width / 2.0
    center_y = height / 2.0
    corners = world_map.hex_corners(center_x, center_y, radius)
    index = int(side_index) % 6
    start = corners[index]
    end = corners[(index + 1) % 6]
    line_width = max(8, int(min(width, height) * SIDE_BAND_WIDTH_FACTOR))

    pygame.draw.line(
        surface,
        (255, 255, 255, 255),
        (int(start[0]), int(start[1])),
        (int(end[0]), int(end[1])),
        line_width,
    )
    _SIDE_BAND_CACHE[key] = surface
    return surface


def _scaled_side_overlay(textures, terrain_key, size, side_index):
    """Zwraca tylko zlote piksele nalezace do jednego boku oryginalnej ramy."""
    source = textures.get(terrain_key)
    if source is None:
        return None

    side_index = int(side_index) % 6
    cache_key = (terrain_key, size, side_index, id(source))
    cached = _SCALED_SIDE_OVERLAY_CACHE.get(cache_key)
    if cached is not None:
        return cached

    full = _scaled_frame_overlay(textures, terrain_key, size, "selected_side")
    if full is None:
        return None

    side = full.copy()
    side.blit(
        _side_band_surface((size, size), side_index),
        (0, 0),
        special_flags=pygame.BLEND_RGBA_MULT,
    )
    _SCALED_SIDE_OVERLAY_CACHE[cache_key] = side
    return side


def _tile_overlay_position(tile, camera, size):
    sx, sy = tile.center(camera)
    return (
        int(round(sx - size / 2.0)),
        int(round(sy - size / 2.0)),
    )


def _blit_with_opacity(screen, surface, pos, opacity=255):
    if surface is None or opacity <= 0:
        return
    if opacity >= 255:
        screen.blit(surface, pos)
        return

    rendered = surface.copy()
    rendered.set_alpha(max(0, min(255, int(opacity))))
    screen.blit(rendered, pos)


def _draw_hover_highlight(tile, screen, textures, camera):
    size = max(1, int(HEX_SIZE * 2 * camera.zoom))
    overlay = _scaled_frame_overlay(textures, tile.terrain_key, size, "hover")
    if overlay is None:
        return

    # Delikatne oddychanie zostaje, ale minimalna jasnosc jest teraz znacznie
    # wyzsza niz poprzednio - hover ma byc czytelny na kazdym typie terenu.
    pulse = (math.sin(pygame.time.get_ticks() / 260.0) + 1.0) * 0.5
    opacity = int(224 + 31 * pulse)
    _blit_with_opacity(
        screen,
        overlay,
        _tile_overlay_position(tile, camera, size),
        opacity,
    )


def _draw_selected_side_shimmer(tile, screen, textures, camera):
    """Animuje cale boki istniejacej zlotej ramy zamiast punktow w rogach."""
    size = max(1, int(HEX_SIZE * 2 * camera.zoom))
    pos = _tile_overlay_position(tile, camera, size)

    # Ciepla baza utrzymuje czytelnosc kliknietego heksa nawet pomiedzy
    # kolejnymi falami swiatla.
    base = _scaled_frame_overlay(textures, tile.terrain_key, size, "selected")
    _blit_with_opacity(screen, base, pos, 245)

    ticks = pygame.time.get_ticks()

    # Kazdy z 6 bokow swieci jako CALY fragment prawdziwej ramy. Fazy sa
    # przesuniete, wiec jasnosc plynie dookola heksa zamiast migac punktami.
    for side_index in range(6):
        phase = ticks / 210.0 - side_index * 0.92
        wave = (math.sin(phase) + 1.0) * 0.5
        opacity = int(86 + 169 * wave)
        side = _scaled_side_overlay(
            textures,
            tile.terrain_key,
            size,
            side_index,
        )
        _blit_with_opacity(screen, side, pos, opacity)


def _draw_frame_highlight(tile, screen, textures, camera, mode):
    if mode == "hover":
        _draw_hover_highlight(tile, screen, textures, camera)
    else:
        _draw_selected_side_shimmer(tile, screen, textures, camera)


def _flush_interaction_highlights():
    if _PENDING["flushed"]:
        return
    _PENDING["flushed"] = True

    screen = _PENDING["screen"]
    textures = _PENDING["textures"]
    camera = _PENDING["camera"]
    if screen is None or textures is None or camera is None:
        return

    hovered = _PENDING["hovered"]
    selected = _PENDING["selected"]
    if hovered is not None and hovered is not selected:
        _draw_frame_highlight(hovered, screen, textures, camera, "hover")
    if selected is not None:
        _draw_frame_highlight(selected, screen, textures, camera, "selected")


def install_hex_selection_theme():
    """Zastepuje techniczny outline podswietleniem oryginalnej zlotej ramy.

    Tile.draw zapisuje tylko, ktory heks jest hover/selected, ale nie pozwala
    nizszemu rendererowi narysowac dawnej niebieskiej kreski. Efekt jest
    dopiero flushowany przy pierwszym pionku, czyli po narysowaniu WSZYSTKICH
    kafli mapy. Dlatego sasiedni heks nie moze go juz przykryc.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    current_tile_draw = world_map.Tile.draw
    current_token_draw = world_map.HeroToken.draw

    def tile_draw_without_debug_outline(
        self,
        screen,
        textures,
        camera,
        font,
        hovered=False,
        selected=False,
        valid_move=False,
    ):
        if int(getattr(self, "id", 0)) == 1:
            _reset_pending()

        _PENDING["screen"] = screen
        _PENDING["textures"] = textures
        _PENDING["camera"] = camera
        if hovered:
            _PENDING["hovered"] = self
        if selected:
            _PENDING["selected"] = self

        return current_tile_draw(
            self,
            screen,
            textures,
            camera,
            font,
            hovered=False,
            selected=False,
            valid_move=bool(valid_move and not selected),
        )

    def token_draw_after_hex_highlight(self, screen, camera, font, selected=False):
        _flush_interaction_highlights()
        return current_token_draw(self, screen, camera, font, selected=selected)

    tile_draw_without_debug_outline._rise_glory_gold_selection = True
    token_draw_after_hex_highlight._rise_glory_gold_selection = True
    world_map.Tile.draw = tile_draw_without_debug_outline
    world_map.HeroToken.draw = token_draw_after_hex_highlight
    _INSTALLED = True
