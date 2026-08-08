"""Poprawka przyciskow menu tytulowego bez jasnej obwodki zapisanej w PNG.

Jasne tlo jest usuwane tylko raz z obrazu zrodlowego. Gotowe tekstury sa
nastepnie cachowane osobno dla kazdego rozmiaru przycisku, aby renderowanie
menu nie wykonywalo kosztownego skanowania pikseli w kazdej klatce.
"""

import pygame

from rg_ui import screens
from rg_ui.common import _remove_light_canvas


_CLEAN_SOURCE = None
_CLEAN_SOURCE_PATH = None
_TEXTURE_CACHE = {}


def _clean_source(path):
    global _CLEAN_SOURCE, _CLEAN_SOURCE_PATH, _TEXTURE_CACHE

    path_key = str(path) if path else None
    if _CLEAN_SOURCE_PATH == path_key and _CLEAN_SOURCE is not None:
        return _CLEAN_SOURCE

    _CLEAN_SOURCE_PATH = path_key
    _CLEAN_SOURCE = None
    _TEXTURE_CACHE = {}

    if not path:
        return None

    try:
        image = pygame.image.load(str(path)).convert_alpha()
        _CLEAN_SOURCE = _remove_light_canvas(image)
    except (OSError, pygame.error):
        _CLEAN_SOURCE = None

    return _CLEAN_SOURCE


def _load_menu_button_texture_without_light_canvas(size):
    path = screens._find_menu_button_path()
    if not path:
        return None

    size = (int(size[0]), int(size[1]))
    cache_key = (str(path), size)
    cached = _TEXTURE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    source = _clean_source(path)
    if source is None:
        return None

    texture = pygame.transform.smoothscale(source, size)
    _TEXTURE_CACHE[cache_key] = texture

    # Zachowujemy zgodnosc ze starym cache w rg_ui.screens, ale nie polegamy
    # juz na pojedynczym wpisie, ktory powodowal przeladowywanie przy zmianie
    # rozmiaru przycisku.
    screens._MENU_BUTTON_CACHE["size"] = cache_key
    screens._MENU_BUTTON_CACHE["surface"] = texture
    screens._MENU_BUTTON_CACHE["path"] = path
    return texture


def install_menu_button_fix():
    """Podmienia loader i usuwa jasne tlo tylko raz na obraz zrodlowy."""
    screens._load_menu_button_texture = _load_menu_button_texture_without_light_canvas
