"""Tlo graficzne pod plansza heksowa na glownej mapie.

Grafika ``Grafiki/tlo_heksow.png`` jest skalowana dokladnie do calego obszaru
pomiedzy bocznymi panelami i pod gornym HUD-em. Nie przycinamy jej trybem
``cover`` - dzieki temu centralny pergamin zawsze pozostaje w tym samym miejscu
wzgledem obszaru gry, niezaleznie od rozdzielczosci.
"""

from pathlib import Path

import pygame

from rg_ui.common import game_layout_rects
from rg_world.map import Tile


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKGROUND_PATH = ROOT_DIR / "Grafiki" / "tlo_heksow.png"

_SOURCE = None
_SCALED_KEY = None
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
    global _SCALED_KEY, _SCALED_BACKGROUND

    size = (max(1, int(size[0])), max(1, int(size[1])))
    if _SCALED_KEY == size and _SCALED_BACKGROUND is not None:
        return _SCALED_BACKGROUND

    source = _load_source()
    if source is None:
        return None

    # Skala dokladnie do dostepnego prostokata. To celowe: tlo jest elementem
    # interfejsu, wiec wazniejsze jest stale polozenie pergaminu niz zachowanie
    # fotograficznych proporcji obrazka.
    background = pygame.transform.smoothscale(source, size)

    # Lekkie przyciemnienie poprawia czytelnosc heksow i znacznikow.
    shade = pygame.Surface(size, pygame.SRCALPHA)
    shade.fill((0, 0, 0, 18))
    background.blit(shade, (0, 0))

    _SCALED_KEY = size
    _SCALED_BACKGROUND = background
    return background


def _draw_map_background(screen):
    center = game_layout_rects(screen)["center"]
    if center.width <= 0 or center.height <= 0:
        return

    background = _background_for_size(center.size)
    if background is not None:
        screen.blit(background, center.topleft)


def install_map_background():
    """Rysuje tlo raz na klatke przed pierwszym heksem."""
    if not BACKGROUND_PATH.exists():
        return
    if getattr(Tile.draw, "_rise_glory_map_background", False):
        return

    original_draw = Tile.draw

    def draw_with_background(self, screen, textures, camera, font, *args, **kwargs):
        if self.id == 1:
            _draw_map_background(screen)
        return original_draw(self, screen, textures, camera, font, *args, **kwargs)

    draw_with_background._rise_glory_map_background = True
    Tile.draw = draw_with_background
