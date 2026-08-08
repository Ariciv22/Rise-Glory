"""Tlo graficzne pod plansza heksowa na glownej mapie.

Grafika ``Grafiki/tlo_heksow.png`` wypelnia dokladnie caly obszar pomiedzy
polaczonym lewym i prawym panelem oraz pod gornym HUD-em. Heksy sa rysowane
na wierzchu, a panele HUD pozostaja poza obszarem tla.
"""

from pathlib import Path

import pygame

from rg_core.data import BG
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

    target_w, target_h = size
    iw, ih = source.get_size()

    # Tryb cover: zachowujemy proporcje grafiki, ale wypelniamy caly dostepny
    # prostokat bez czarnych pasow. Nadmiar jest symetrycznie przycinany.
    scale = max(target_w / max(1, iw), target_h / max(1, ih))
    scaled_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    scaled = pygame.transform.smoothscale(source, scaled_size)

    crop_x = max(0, (scaled.get_width() - target_w) // 2)
    crop_y = max(0, (scaled.get_height() - target_h) // 2)
    crop = pygame.Rect(crop_x, crop_y, target_w, target_h)

    background = pygame.Surface(size)
    background.fill(BG)
    background.blit(scaled, (0, 0), crop)

    # Delikatne przyciemnienie utrzymuje czytelnosc heksow i znacznikow.
    shade = pygame.Surface(size, pygame.SRCALPHA)
    shade.fill((0, 0, 0, 22))
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
    """Rysuje tlo raz na klatke, bez kosztownego sprawdzania kazdego heksa."""
    if not BACKGROUND_PATH.exists():
        return
    if getattr(Tile.draw, "_rise_glory_map_background", False):
        return

    original_draw = Tile.draw

    def draw_with_background(self, screen, textures, camera, font, *args, **kwargs):
        # generate_world nadaje heksom identyfikatory od 1 i rysuje je w tej
        # samej kolejnosci, wiec pierwszy heks jest bezpiecznym punktem do
        # jednokrotnego narysowania tla przed cala plansza.
        if self.id == 1:
            _draw_map_background(screen)
        return original_draw(self, screen, textures, camera, font, *args, **kwargs)

    draw_with_background._rise_glory_map_background = True
    Tile.draw = draw_with_background
