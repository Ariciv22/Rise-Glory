"""Tlo graficzne pod plansza heksowa na glownej mapie.

Aplikacja nadal wypelnia klatke kolorem ``BG`` przed rysowaniem heksow.
Ten modul podpina sie pod pierwsze rysowanie heksa w klatce i zamienia
jednolite tlo na grafike ``Grafiki/tlo_heksow.png`` zanim pojawia sie plansza.
Dzieki temu nie trzeba mieszac logiki prezentacji z ``rg_core.app``.
"""

from pathlib import Path

import pygame

from rg_core.data import BG
from rg_world.map import Tile


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKGROUND_PATH = ROOT_DIR / "Grafiki" / "tlo_heksow.png"

_SOURCE = None
_SCALED_SIZE = None
_SCALED_BACKGROUND = None


def _load_source():
    global _SOURCE
    if _SOURCE is not None:
        return _SOURCE
    if not BACKGROUND_PATH.exists():
        return None
    try:
        _SOURCE = pygame.image.load(str(BACKGROUND_PATH)).convert()
    except (OSError, pygame.error):
        _SOURCE = None
    return _SOURCE


def _background_for_size(size):
    global _SCALED_SIZE, _SCALED_BACKGROUND
    if _SCALED_SIZE == size and _SCALED_BACKGROUND is not None:
        return _SCALED_BACKGROUND

    source = _load_source()
    if source is None:
        return None

    sw, sh = size
    iw, ih = source.get_size()
    scale = max(sw / max(1, iw), sh / max(1, ih))
    scaled_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    scaled = pygame.transform.smoothscale(source, scaled_size)

    background = pygame.Surface(size)
    background.fill(BG)
    background.blit(
        scaled,
        ((sw - scaled.get_width()) // 2, (sh - scaled.get_height()) // 2),
    )

    # Delikatne przyciemnienie utrzymuje czytelnosc heksow i znacznikow.
    shade = pygame.Surface(size, pygame.SRCALPHA)
    shade.fill((0, 0, 0, 22))
    background.blit(shade, (0, 0))

    _SCALED_SIZE = size
    _SCALED_BACKGROUND = background
    return background


def _draw_map_background(screen):
    background = _background_for_size(screen.get_size())
    if background is not None:
        screen.blit(background, (0, 0))


def install_map_background():
    """Rysuje ``tlo_heksow`` raz na klatke, tuz przed pierwszym heksem."""
    if not BACKGROUND_PATH.exists():
        return
    if getattr(Tile.draw, "_rise_glory_map_background", False):
        return

    original_draw = Tile.draw

    def draw_with_background(self, screen, textures, camera, font, *args, **kwargs):
        try:
            pixel = screen.get_at((0, 0))
            if tuple(pixel[:3]) == tuple(BG[:3]):
                _draw_map_background(screen)
        except (IndexError, TypeError, pygame.error):
            pass
        return original_draw(self, screen, textures, camera, font, *args, **kwargs)

    draw_with_background._rise_glory_map_background = True
    Tile.draw = draw_with_background
