import math

import pygame

from rg_ui import city_hub


_ARROW_CROP_CACHE = {}
_ARROW_SCALED_CACHE = {}
_FOOTER_BAND_CACHE = None


def _fallback_footer_band():
    # Awaryjnie zwracamy krawedzie dwoch zlotych linii ograniczajacych stopke.
    return 0.905, 0.966


def _footer_band_ratios():
    """Wyznacza krawedzie wolnej stopki prawego panelu z samej grafiki.

    Zwracamy polozenie dolnej krawedzi separatora oraz gornej krawedzi dolnej
    ramy. Dokladny 1 px odstep od obu linii jest nakladany juz po przeskalowaniu
    panelu do rozdzielczosci ekranu.
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

    if frame_top - separator[1] < max(12, int(round(height * 0.025))):
        _FOOTER_BAND_CACHE = _fallback_footer_band()
        return _FOOTER_BAND_CACHE

    # Bez dodatkowego paddingu tutaj. Docelowy odstep wynosi dokladnie 1 px
    # na ekranie, niezaleznie od skali assetu panelu.
    _FOOTER_BAND_CACHE = (
        max(0.0, min(1.0, separator[1] / height)),
        max(0.0, min(1.0, frame_top / height)),
    )
    return _FOOTER_BAND_CACHE


def _arrow_crop_rect(path, source):
    """Wycina czarne tlo assetu i zostawia sam obrys przycisku strzalki."""
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

    # Nie dodajemy czarnego marginesu z oryginalnego PNG. Bounding box zlotej
    # ramki obejmuje caly wizualny przycisk i dzieki temu skaluje sie sam guzik.
    rect = pygame.Rect(left, top, right - left + 1, bottom - top + 1)
    _ARROW_CROP_CACHE[key] = rect
    return rect


def _cropped_arrow_size(path):
    source = city_hub._load_asset(path) if path is not None else None
    if source is None:
        return None
    crop_rect = _arrow_crop_rect(path, source)
    if crop_rect.width <= 0 or crop_rect.height <= 0:
        return None
    return crop_rect.size


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
    """Powieksza guziki do wysokosci stopki z dokladnie 1 px luzu od linii."""
    separator_ratio, frame_ratio = _footer_band_ratios()
    separator_y = right_rect.y + int(round(right_rect.height * separator_ratio))
    frame_y = right_rect.y + int(round(right_rect.height * frame_ratio))

    if frame_y <= separator_y + 4:
        separator_y = right_rect.bottom - max(46, int(round(right_rect.height * 0.095)))
        frame_y = right_rect.bottom - max(8, int(round(right_rect.height * 0.014)))

    # Jeden pusty piksel nad i pod przyciskiem:
    # separator | 1 px luzu | GUZIK | 1 px luzu | dolna rama.
    button_top = separator_y + 2
    button_bottom = frame_y - 1
    button_h = max(1, button_bottom - button_top)

    left_path = city_hub._arrow_asset_file("left")
    right_path = city_hub._arrow_asset_file("right")
    arrow_sizes = [
        size
        for size in (_cropped_arrow_size(left_path), _cropped_arrow_size(right_path))
        if size is not None
    ]
    max_aspect = max((w / h for w, h in arrow_sizes if h > 0), default=2.4)

    # Szerokosc wynika z docelowej wysokosci guzika, zeby to wysokosc stopki
    # byla ograniczeniem skali. Dwa guziki zachowuja rowny odstep od srodka.
    desired_w = max(1, int(math.ceil(button_h * max_aspect)))
    outer_gap = max(8, int(round(right_rect.width * 0.10)))
    center_gap = max(12, int(round(right_rect.width * 0.08)))
    max_button_w = max(1, (right_rect.width - outer_gap * 2 - center_gap) // 2)
    button_w = min(desired_w, max_button_w)

    pair_w = button_w * 2 + center_gap
    pair_x = right_rect.centerx - pair_w // 2
    left = pygame.Rect(pair_x, button_top, button_w, button_h)
    right = pygame.Rect(pair_x + button_w + center_gap, button_top, button_w, button_h)
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
