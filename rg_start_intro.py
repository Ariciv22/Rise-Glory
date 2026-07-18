import pygame

import rg_start_intro_base as _base
from rg_start_intro_base import *


def _load_cover_image(path, size):
    cache_key = (str(path), size, "fit")
    if cache_key in _base._IMAGE_CACHE:
        return _base._IMAGE_CACHE[cache_key]

    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None

    iw, ih = image.get_size()
    sw, sh = size
    if iw <= 0 or ih <= 0 or sw <= 0 or sh