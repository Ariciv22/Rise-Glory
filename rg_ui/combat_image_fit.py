import pygame

from rg_ui import combat as rg_combat

_ORIGINAL_DRAW_COVER = rg_combat._draw_cover
_INSTALLED = False


def _draw_fitted_combat_image(screen, rect, image_name):
    image = rg_combat._find_image(image_name)
    if image is None:
        _ORIGINAL_DRAW_COVER(screen, rect, image_name)
        return

    cache_key = ("combat_fit", rg_combat._normalize(image_name), rect.width, rect.height)
    composed = rg_combat._SCALED_CACHE.get(cache_key)
    if composed is None:
        composed = pygame.Surface(rect.size, pygame.SRCALPHA)
        iw, ih = image.get_size()

        background_scale = max(rect.width / iw, rect.height / ih)
        background_size = (
            max(1, int(iw * background_scale)),
            max(1, int(ih * background_scale)),
        )
        background = pygame.transform.smoothscale(image, background_size)
        background_crop = pygame.Rect(
            max(0, (background.get_width() - rect.width) // 2),
            max(0, (background.get_height() - rect.height) // 2),
            rect.width,
            rect.height,
        )
        composed.blit(background, (0, 0), background_crop)
        darken = pygame.Surface(rect.size, pygame.SRCALPHA)
        darken.fill((0, 0, 0, 175))
        composed.blit(darken, (0, 0))

        inset = 12
        available_width = max(1, rect.width - inset * 2)
        available_height = max(1, rect.height - inset * 2)
        foreground_scale = min(available_width / iw, available_height / ih)
        foreground_size = (
            max(1, int(iw * foreground_scale)),
            max(1, int(ih * foreground_scale)),
        )
        foreground = pygame.transform.smoothscale(image, foreground_size)
        foreground_rect = foreground.get_rect(center=composed.get_rect().center)

        frame = foreground_rect.inflate(8, 8)
        pygame.draw.rect(composed, (8, 7, 6, 220), frame, border_radius=10)
        composed.blit(foreground, foreground_rect)
        pygame.draw.rect(composed, (174, 121, 48), foreground_rect, 1, border_radius=8)

        rg_combat._SCALED_CACHE[cache_key] = composed

    screen.blit(composed, rect.topleft)


def install_combat_image_fit():
    global _INSTALLED
    if _INSTALLED:
        return
    rg_combat._draw_cover = _draw_fitted_combat_image
    _INSTALLED = True
