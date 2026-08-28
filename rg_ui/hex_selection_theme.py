from __future__ import annotations

import math

import pygame

from rg_core.data import HEX_SIZE
from rg_world import map as world_map


_INSTALLED = False
_SOURCE_OVERLAY_CACHE = {}
_SCALED_OVERLAY_CACHE = {}
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
HOVER_TINT = (255, 232, 164)
SELECTED_TINT = (255, 174, 66)


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
    tint = SELECTED_TINT if mode == "selected" else HOVER_TINT
    min_alpha, max_alpha = ((72, 132) if mode == "selected" else (38, 78))

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


def _draw_corner_glints(tile, screen, camera):
    """Subtelne iskry siedza na istniejacych naroznikach ramy, nie na grafice."""
    points = tile.screen_points(camera)
    if len(points) != 6:
        return

    center_x = sum(point[0] for point in points) / 6.0
    center_y = sum(point[1] for point in points) / 6.0
    anchors = [
        (
            int(center_x + (x - center_x) * 0.90),
            int(center_y + (y - center_y) * 0.90),
        )
        for x, y in points
    ]

    ticks = pygame.time.get_ticks()
    pulse = (math.sin(ticks / 180.0) + 1.0) * 0.5
    active_index = (ticks // 230) % len(anchors)
    zoom = max(0.35, float(camera.zoom))
    base_radius = max(3, min(9, int(2.0 + 1.7 * zoom)))

    for index, center in enumerate(anchors):
        radius = base_radius + (2 if index == active_index else 0)
        glow_radius = radius * 3
        glow = pygame.Surface((glow_radius * 2 + 2, glow_radius * 2 + 2), pygame.SRCALPHA)
        glow_center = (glow_radius + 1, glow_radius + 1)
        alpha_boost = int(18 + 18 * pulse)
        if index == active_index:
            alpha_boost += 30
        pygame.draw.circle(glow, (255, 181, 65, alpha_boost), glow_center, glow_radius)
        pygame.draw.circle(glow, (255, 220, 135, min(130, alpha_boost * 2)), glow_center, radius + 2)
        screen.blit(glow, (center[0] - glow_center[0], center[1] - glow_center[1]))

        core = (255, 232, 169)
        pygame.draw.circle(screen, core, center, max(1, radius // 2))
        if index == active_index:
            arm = radius + 3
            pygame.draw.line(screen, (255, 246, 213), (center[0] - arm, center[1]), (center[0] + arm, center[1]), 1)
            pygame.draw.line(screen, (255, 246, 213), (center[0], center[1] - arm), (center[0], center[1] + arm), 1)


def _draw_frame_highlight(tile, screen, textures, camera, mode):
    size = max(1, int(HEX_SIZE * 2 * camera.zoom))
    overlay = _scaled_frame_overlay(textures, tile.terrain_key, size, mode)
    if overlay is not None:
        sx, sy = tile.center(camera)
        pos = (int(round(sx - size / 2.0)), int(round(sy - size / 2.0)))
        screen.blit(overlay, pos)

    if mode == "selected":
        _draw_corner_glints(tile, screen, camera)


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
