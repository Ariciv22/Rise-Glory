from pathlib import Path

import pygame

from rg_core.data import GOLD, PANEL_DARK, TEXT
from rg_ui.common import ROOT_DIR, draw_panel


HUD_STATS_DIR = ROOT_DIR / "Grafiki" / "Grafiki UI" / "HUD"

# Każdy kafel górnego HUD-u może mieć własną grafikę.
# Grafiki nie powinny zawierać tekstu ani wartości — tekst jest nadal rysowany
# dynamicznie przez grę. Dzięki temu np. liczba złota może się zmieniać bez
# przygotowywania kolejnych wersji PNG.
_STAT_IMAGE_NAMES = {
    "Gracz:": "hud_gracz.png",
    "Bohater:": "hud_bohater.png",
    "Klasa:": "hud_klasa.png",
    "Legenda:": "hud_legenda.png",
    "Zloto:": "hud_zloto.png",
    "Rany:": "hud_rany.png",
    "Akcje:": "hud_akcje.png",
    "Runda:": "hud_runda.png",
    "Rada:": "hud_rada.png",
}

_IMAGE_CACHE = {}
_SCALED_CACHE = {}


def _stat_key(text):
    text = str(text)
    for prefix, filename in _STAT_IMAGE_NAMES.items():
        if text.startswith(prefix):
            return filename
    return None


def _load_stat_image(filename):
    if not filename:
        return None
    if filename in _IMAGE_CACHE:
        return _IMAGE_CACHE[filename]

    path = Path(HUD_STATS_DIR) / filename
    image = None
    if path.exists():
        try:
            image = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            image = None

    _IMAGE_CACHE[filename] = image
    return image


def _draw_top_stat_with_image(screen, font, text, x, width):
    box = pygame.Rect(x, 78, width, 30)
    filename = _stat_key(text)
    source = _load_stat_image(filename)

    if source is None:
        # Bez grafiki zachowujemy dotychczasowy placeholder, więc projekt
        # pozostaje grywalny podczas sukcesywnego dodawania assetów HUD.
        draw_panel(screen, box)
        text_x = box.x + 9
    else:
        # Ciemne tło zabezpiecza półprzezroczyste fragmenty grafiki.
        pygame.draw.rect(screen, PANEL_DARK, box, border_radius=11)
        cache_key = (filename, box.size)
        texture = _SCALED_CACHE.get(cache_key)
        if texture is None:
            texture = pygame.transform.smoothscale(source, box.size)
            _SCALED_CACHE[cache_key] = texture
        screen.blit(texture, box.topleft)

        # Lewa część grafiki jest przeznaczona na małą ikonę przypisaną
        # konkretnemu typowi informacji, dlatego tekst zaczyna się dalej.
        text_x = box.x + 31

    label = font.render(str(text), True, TEXT)
    label_y = box.y + (box.height - label.get_height()) // 2

    # Delikatny cień poprawia czytelność na bardziej malarskich assetach.
    shadow = font.render(str(text), True, (18, 14, 10))
    screen.blit(shadow, (text_x + 1, label_y + 1))
    screen.blit(label, (text_x, label_y))
    return box.right + 8


def install_hud_top_stat_theme():
    """Podmienia wyłącznie renderer górnych kafli informacyjnych HUD-u."""
    from rg_ui import hud

    hud._draw_top_stat = _draw_top_stat_with_image
