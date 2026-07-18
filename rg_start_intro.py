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
    if iw <= 0 or ih <= 0 or sw <= 0 or sh <= 0:
        return None

    scale = min(sw / iw, sh / ih)
    fitted_w = max(1, int(round(iw * scale)))
    fitted_h = max(1, int(round(ih * scale)))
    scaled = pygame.transform.smoothscale(image, (fitted_w, fitted_h))

    result = pygame.Surface(size)
    result.fill((8, 9, 11))
    result.blit(scaled, ((sw - fitted_w) // 2, (sh - fitted_h) // 2))
    _base._IMAGE_CACHE[cache_key] = result
    return result


def draw_start_intro(screen, title_font, font, intro_index):
    images = _base.find_intro_images()
    if not images:
        _base._draw_fallback(screen, title_font, font)
        return

    index = max(0, min(intro_index, len(images) - 1))
    image = _load_cover_image(images[index], screen.get_size())
    if image:
        screen.blit(image, (0, 0))
    else:
        _base._draw_fallback(screen, title_font, font)


try:
    from rg_title_flow import install_into_main

    install_into_main()
except Exception:
    pass
