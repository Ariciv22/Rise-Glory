from __future__ import annotations

import pygame

from rg_core.data import HEX_SIZE
from rg_world import map as world_map


_INSTALLED = False
_SOURCE_BORDER_OVERLAY_CACHE = {}
_SCALED_BORDER_OVERLAY_CACHE = {}
_PENDING = {
    "hovered": None,
    "selected": None,
    "screen": None,
    "textures": None,
    "camera": None,
    "flushed": False,
}

# Nie rozjasniamy juz zlotej ramy ani calego heksa. Efekt interakcji dotyczy
# tylko ciemnej/czarnej szczeliny biegnacej wewnatrz ozdobnej ramy heksa.
# Maska ogranicza wyszukiwanie do zewnetrznego pasa assetu, zeby ciemne
# fragmenty krajobrazu w srodku kafla pozostaly nietkniete.
BORDER_RING_INNER_FACTOR = 0.72
BLACK_BORDER_MAX_VALUE = 118
BLACK_BORDER_MAX_CHROMA = 45

# Hover jest spokojniejszy, klikniety heks ma wyrazniejszy braz. Nie ma
# pulsowania, swiecenia, iskier ani animacji po bokach.
HOVER_BORDER_TINT = (142, 82, 43)
HOVER_ALPHA_RANGE = (205, 238)
SELECTED_BORDER_TINT = (188, 108, 48)
SELECTED_ALPHA_RANGE = (222, 250)


def _reset_pending():
    _PENDING["hovered"] = None
    _PENDING["selected"] = None
    _PENDING["screen"] = None
    _PENDING["textures"] = None
    _PENDING["camera"] = None
    _PENDING["flushed"] = False


def _looks_like_black_border(color):
    """Rozpoznaje czarny/grafitowy kontur ramy bez lapana zlota i terenu."""
    r, g, b, a = color
    if a < 70:
        return False

    brightest = max(r, g, b)
    darkest = min(r, g, b)
    if brightest > BLACK_BORDER_MAX_VALUE:
        return False

    # Czarna szczelina moze miec lekko cieply odcien przez antyaliasing,
    # ale nie powinna miec nasycenia typowego dla zlota, trawy czy ziemi.
    if brightest - darkest > BLACK_BORDER_MAX_CHROMA:
        return False

    return True


def _border_ring_mask(size):
    """Maska szerokiego pasa, w ktorym znajduje sie ozdobna rama heksa."""
    width, height = size
    ring_surface = pygame.Surface(size, pygame.SRCALPHA)
    radius = max(1.0, min(width, height) / 2.0 - 1.0)
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
            radius * BORDER_RING_INNER_FACTOR,
        )
    ]

    pygame.draw.polygon(ring_surface, (255, 255, 255, 255), outer)
    pygame.draw.polygon(ring_surface, (0, 0, 0, 0), inner)
    return pygame.mask.from_surface(ring_surface, 16)


def _source_border_overlay(source, mode):
    """Tworzy brazowa warstwe tylko z czarnych pikseli oryginalnej ramy."""
    key = (id(source), source.get_size(), mode)
    cached = _SOURCE_BORDER_OVERLAY_CACHE.get(key)
    if cached is not None:
        return cached

    size = source.get_size()
    ring_mask = _border_ring_mask(size)
    overlay = pygame.Surface(size, pygame.SRCALPHA)

    if mode == "selected":
        tint = SELECTED_BORDER_TINT
        min_alpha, max_alpha = SELECTED_ALPHA_RANGE
    else:
        tint = HOVER_BORDER_TINT
        min_alpha, max_alpha = HOVER_ALPHA_RANGE

    width, height = size
    for y in range(height):
        for x in range(width):
            if not ring_mask.get_at((x, y)):
                continue

            color = source.get_at((x, y))
            if not _looks_like_black_border(color):
                continue

            # Najciemniejsza czesc czarnej szczeliny dostaje niemal pelny braz,
            # a antyaliasowane krawedzie sa odrobine slabsze. Dzieki temu
            # zachowujemy ksztalt i fakture oryginalnej granicy.
            brightness = max(color.r, color.g, color.b)
            darkness = 1.0 - min(1.0, brightness / BLACK_BORDER_MAX_VALUE)
            alpha = int(min_alpha + (max_alpha - min_alpha) * darkness)
            overlay.set_at((x, y), (*tint, alpha))

    _SOURCE_BORDER_OVERLAY_CACHE[key] = overlay
    return overlay


def _scaled_border_overlay(textures, terrain_key, size, mode):
    source = textures.get(terrain_key)
    if source is None:
        return None

    cache_key = (terrain_key, mode)
    cached = _SCALED_BORDER_OVERLAY_CACHE.get(cache_key)
    if cached is not None and cached[0] == size and cached[1] is source:
        return cached[2]

    base = _source_border_overlay(source, mode)
    if base.get_size() == (size, size):
        scaled = base
    else:
        scaled = pygame.transform.smoothscale(base, (size, size))

    _SCALED_BORDER_OVERLAY_CACHE[cache_key] = (size, source, scaled)
    return scaled


def _tile_overlay_position(tile, camera, size):
    sx, sy = tile.center(camera)
    return (
        int(round(sx - size / 2.0)),
        int(round(sy - size / 2.0)),
    )


def _draw_brown_border(tile, screen, textures, camera, mode):
    size = max(1, int(HEX_SIZE * 2 * camera.zoom))
    overlay = _scaled_border_overlay(textures, tile.terrain_key, size, mode)
    if overlay is None:
        return

    screen.blit(overlay, _tile_overlay_position(tile, camera, size))


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

    # Jezeli ten sam heks jest klikniety i jednoczesnie pod kursorem, pokazujemy
    # tylko mocniejszy stan selected zamiast nakladac dwa kolory na siebie.
    if hovered is not None and hovered is not selected:
        _draw_brown_border(hovered, screen, textures, camera, "hover")
    if selected is not None:
        _draw_brown_border(selected, screen, textures, camera, "selected")


def install_hex_selection_theme():
    """Zamienia techniczne podswietlenie na brazowienie czarnych granic heksa.

    Tile.draw zapisuje tylko, ktory heks jest hover/selected, ale nie pozwala
    bazowemu rendererowi narysowac dawnego outline'u. Brazowy kolor jest
    nakladany dopiero po narysowaniu wszystkich kafli mapy, przy pierwszym
    pionku, dzieki czemu sasiedni heks nie przykrywa zmienionej granicy.
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

    def token_draw_after_hex_border(self, screen, camera, font, selected=False):
        _flush_interaction_highlights()
        return current_token_draw(self, screen, camera, font, selected=selected)

    tile_draw_without_debug_outline._rise_glory_brown_border_selection = True
    token_draw_after_hex_border._rise_glory_brown_border_selection = True
    world_map.Tile.draw = tile_draw_without_debug_outline
    world_map.HeroToken.draw = token_draw_after_hex_border
    _INSTALLED = True
