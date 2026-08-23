import pygame

from rg_ui import city_hub


_ARROW_CROP_CACHE = {}
_ARROW_SCALED_CACHE = {}
_FOOTER_BAND_CACHE = None


def _fallback_footer_band():
    # Bezpieczny zakres pomiedzy dolnym separatorem ostatniego slotu a
    # ozdobna rama dolna prawego panelu.
    return 0.905, 0.966


def _footer_band_ratios():
    """Wyznacza wolna stopke prawego panelu na podstawie zlotej grafiki.

    Nie opieramy pozycji strzalek na samym dolnym marginesie. Wyszukujemy
    poziome zlote linie w dolnej czesci panelu i bierzemy przestrzen pomiedzy
    ostatnim separatorem zawartosci a zewnetrzna rama dolna.
    """
    global _FOOTER_BAND_CACHE
    if _FOOTER_BAND_CACHE is not None:
        return _FOOTER_BAND_CACHE

    source = city_hub._load_asset(city_hub.RIGHT_PANEL_FILE)
    if source is None:
        _FOOTER_BAND_CACHE = _fallback_footer_band()
        return _FOOTER_BAND_CACHE

    crop_rect = city_hub._panel_crop_rect(city_hub.RIGHT_PANEL_FILE, source)
    panel = source.subsurface(crop_rect)
    width, height = panel.get_size()
    if width <= 2 or height <= 2:
        _FOOTER_BAND_CACHE = _fallback_footer_band()
        return _FOOTER_BAND_CACHE

    start_y = int(round(height * 0.80))
    step_x = max(1, width // 220)
    sample_count = max(1, (width + step_x - 1) // step_x)
    required = max(10, int(round(sample_count * 0.16)))

    line_rows = []
    for y in range(start_y, height):
        count = 0
        for x in range(0, width, step_x):
            if city_hub._goldish(panel.get_at((x, y))):
                count += 1
                if count >= required:
                    line_rows.append(y)
                    break

    groups = []
    for y in line_rows:
        if not groups or y > groups[-1][1] + 1:
            groups.append([y, y])
        else:
            groups[-1][1] = y

    if len(groups) < 2:
        _FOOTER_BAND_CACHE = _fallback_footer_band()
        return _FOOTER_BAND_CACHE

    # Dolna rama moze skladac sie z kilku blisko polozonych linii. Traktujemy
    # je jako jeden klaster, zeby strzalki nie trafily pomiedzy dwie linie ramy.
    frame_index = len(groups) - 1
    cluster_gap = max(3, int(round(height * 0.018)))
    while frame_index > 0:
        gap = groups[frame_index][0] - groups[frame_index - 1][1]
        if gap > cluster_gap:
            break
        frame_index -= 1

    if frame_index <= 0:
        _FOOTER_BAND_CACHE = _fallback_footer_band()
        return _FOOTER_BAND_CACHE

    separator = groups[frame_index - 1]
    frame_top = groups[frame_index][0]
    padding = max(2, int(round(height * 0.004)))
    band_top = separator[1] + padding
    band_bottom = frame_top - padding

    if band_bottom - band_top < max(12, int(round(height * 0.025))):
        _FOOTER_BAND_CACHE = _fallback_footer_band()
        return _FOOTER_BAND_CACHE

    _FOOTER_BAND_CACHE = (
        max(0.0, min(1.0, band_top / height)),
        max(0.0, min(1.0, band_bottom / height)),
    )
    return _FOOTER_BAND_CACHE


def _arrow_crop_rect(path, source):
    """Usuwa czarne pole dookola assetu, zostawiajac sam przycisk strzalki."""
    key = str(path)
    if key in _ARROW_CROP_CACHE:
        return _ARROW_CROP_CACHE[key]

    width, height = source.get_size()
    if width <= 2 or height <= 2:
        rect = pygame.Rect(0, 0, width, height)
        _ARROW_CROP_CACHE[key] = rect
        return rect

    def column_has_gold(x):
        for y in range(height):
            if city_hub._goldish(source.get_at((x, y))):
                return True
        return False

    def row_has_gold(y):
        for x in range(width):
            if city_hub._goldish(source.get_at((x, y))):
                return True
        return False

    left = next((x for x in range(width) if column_has_gold(x)), None)
    right = next((x for x in range(width - 1, -1, -1) if column_has_gold(x)), None)
    top = next((y for y in range(height) if row_has_gold(y)), None)
    bottom = next((y for y in range(height - 1, -1, -1) if row_has_gold(y)), None)

    if None in (left, right, top, bottom):
        rect = pygame.Rect(0, 0, width, height)
        _ARROW_CROP_CACHE[key] = rect
        return rect

    pad_x = max(2, int(round(width * 0.02)))
    pad_y = max(2, int(round(height * 0.04)))
    left = max(0, left - pad_x)
    right = min(width - 1, right + pad_x)
    top = max(0, top - pad_y)
    bottom = min(height - 1, bottom + pad_y)

    rect = pygame.Rect(left, top, right - left + 1, bottom - top + 1)
    _ARROW_CROP_CACHE[key] = rect
    return rect


def _draw_arrow_contained(screen, path, rect):
    source = city_hub._load_asset(path) if path is not None else None
    if source is None or rect.width <= 0 or rect.height <= 0:
        return False

    crop_rect = _arrow_crop_rect(path, source)
    cropped = source.subsurface(crop_rect)
    iw, ih = cropped.get_size()
    if iw <= 0 or ih <= 0:
        return False

    scale = min(rect.width / iw, rect.height / ih)
    size = (
        max(1, int(round(iw * scale))),
        max(1, int(round(ih * scale))),
    )
    cache_key = (
        str(path),
        crop_rect.x,
        crop_rect.y,
        crop_rect.width,
        crop_rect.height,
        size,
    )
    image = _ARROW_SCALED_CACHE.get(cache_key)
    if image is None:
        image = (
            cropped.copy()
            if cropped.get_size() == size
            else pygame.transform.smoothscale(cropped, size)
        )
        _ARROW_SCALED_CACHE[cache_key] = image

    x = rect.centerx - image.get_width() // 2
    y = rect.centery - image.get_height() // 2
    screen.blit(image, (x, y))
    return True


def _right_navigation_rects(right_rect):
    """Centruje oba guziki dokladnie w wolnej stopce pomiedzy liniami."""
    top_ratio, bottom_ratio = _footer_band_ratios()
    footer_top = right_rect.y + int(round(right_rect.height * top_ratio))
    footer_bottom = right_rect.y + int(round(right_rect.height * bottom_ratio))

    if footer_bottom <= footer_top:
        footer_top = right_rect.bottom - max(46, int(round(right_rect.height * 0.095)))
        footer_bottom = right_rect.bottom - max(14, int(round(right_rect.height * 0.032)))

    footer_h = max(1, footer_bottom - footer_top)
    vertical_pad = max(2, int(round(right_rect.height * 0.006)))
    button_h = min(
        max(18, int(round(right_rect.height * 0.032))),
        max(1, footer_h - vertical_pad * 2),
    )
    y = footer_top + max(0, (footer_h - button_h) // 2)

    side_gap = max(12, int(round(right_rect.width * 0.16)))
    center_gap = max(14, int(round(right_rect.width * 0.10)))
    available = max(2, right_rect.width - side_gap * 2 - center_gap)
    button_w = min(
        max(44, int(round(right_rect.width * 0.24))),
        max(1, available // 2),
    )

    left = pygame.Rect(right_rect.x + side_gap, y, button_w, button_h)
    right = pygame.Rect(right_rect.right - side_gap - button_w, y, button_w, button_h)
    return left, right


def _draw_right_navigation(screen, right_rect):
    left_rect, right_rect_button = _right_navigation_rects(right_rect)
    _draw_arrow_contained(screen, city_hub._arrow_asset_file("left"), left_rect)
    _draw_arrow_contained(screen, city_hub._arrow_asset_file("right"), right_rect_button)


def install_location_navigation_fix():
    if getattr(city_hub, "_rise_glory_location_navigation_fix_installed", False):
        return

    city_hub._right_navigation_rects = _right_navigation_rects
    city_hub._draw_right_navigation = _draw_right_navigation
    city_hub._rise_glory_location_navigation_fix_installed = True
