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
        return

    sw, _ = screen.get_size()
    counter = font.render(
        f"Intro {index + 1}/{len(images)}  |  spacja / enter / klik - dalej",
        True,
        TEXT,
    )
    pad_x, pad_y = 16, 10
    box = pygame.Rect(
        max(14, sw - counter.get_width() - pad_x * 2 - 18),
        18,
        counter.get_width() + pad_x * 2,
        counter.get_height() + pad_y * 2,
    )
    overlay = pygame.Surface(box.size, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 155))
    screen.blit(overlay, box.topleft)
    pygame.draw.rect(screen, GOLD, box, 2, border_radius=8)
    screen.blit(counter, (box.x + pad_x, box.y + pad_y))
