"""Poprawka przyciskow menu tytulowego bez jasnej obwodki zapisanej w PNG."""

import pygame

from rg_ui import screens
from rg_ui.common import _remove_light_canvas


def _load_menu_button_texture_without_light_canvas(size):
    path = screens._find_menu_button_path()
    cache_key = (size, str(path) if path else None)
    if screens._MENU_BUTTON_CACHE["size"] == cache_key:
        return screens._MENU_BUTTON_CACHE["surface"]
    if not path:
        screens._MENU_BUTTON_CACHE["size"] = cache_key
        screens._MENU_BUTTON_CACHE["surface"] = None
        screens._MENU_BUTTON_CACHE["path"] = None
        return None

    try:
        image = pygame.image.load(str(path)).convert_alpha()
        image = _remove_light_canvas(image)
    except pygame.error:
        screens._MENU_BUTTON_CACHE["size"] = cache_key
        screens._MENU_BUTTON_CACHE["surface"] = None
        screens._MENU_BUTTON_CACHE["path"] = None
        return None

    texture = pygame.transform.smoothscale(image, size)
    screens._MENU_BUTTON_CACHE["size"] = cache_key
    screens._MENU_BUTTON_CACHE["surface"] = texture
    screens._MENU_BUTTON_CACHE["path"] = path
    return texture


def install_menu_button_fix():
    """Podmienia loader tekstury menu tak, aby usuwal jasne tlo/ramke z PNG."""
    screens._load_menu_button_texture = _load_menu_button_texture_without_light_canvas
