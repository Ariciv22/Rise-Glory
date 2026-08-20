import pygame

from rg_core.data import GOLD, TEXT
from rg_ui import screens as s


_FRAME_CACHE = {}
_ICON_CACHE = {}


def _clear_dark_neutral_pixels(surface, max_value=48, max_spread=18):
    """Usuwa czarne/prawie czarne neutralne tlo z kopii Surface."""
    cleaned = surface.copy().convert_alpha()
    try:
        rgb = pygame.surfarray.pixels3d(cleaned)
        alpha = pygame.surfarray.pixels_alpha(cleaned)
        channel_min = rgb.min(axis=2)
        channel_max = rgb.max(axis=2)
        dark_fill = (channel_max <= max_value) & ((channel_max - channel_min) <= max_spread)
        alpha[dark_fill] = 0
        del alpha
        del rgb
    except (ImportError, NotImplementedError, ValueError, pygame.error):
        pixels = pygame.PixelArray(cleaned)
        width, height = cleaned.get_size()
        for px in range(width):
            for py in range(height):
                color = cleaned.unmap_rgb(pixels[px, py])
                low = min(color.r, color.g, color.b)
                high = max(color.r, color.g, color.b)
                if high <= max_value and high - low <= max_spread:
                    pixels[px, py] = (0, 0, 0, 0)
        del pixels
    return cleaned


def _crop_visible_content(surface, padding=3):
    """Przycina przezroczyste marginesy, aby sam symbol mogl wypelnic duzy kwadrat."""
    mask = pygame.mask.from_surface(surface, 8)
    components = mask.get_bounding_rects()
    if not components:
        return surface

    # Starsze wersje Pygame nie maja Mask.get_bounding_rect(). Laczymy wiec
    # prostokaty wszystkich widocznych skladowych w jeden wspolny obszar.
    bounds = components[0].copy()
    for rect in components[1:]:
        bounds.union_ip(rect)

    if bounds.width <= 0 or bounds.height <= 0:
        return surface

    bounds.inflate_ip(padding * 2, padding * 2)
    bounds.clamp_ip(surface.get_rect())
    return surface.subsurface(bounds).copy()


def _scale_into_square(surface, size):
    size = max(1, int(size))
    source_w, source_h = surface.get_size()
    if source_w <= 0 or source_h <= 0:
        return None

    scale = min(size / source_w, size / source_h)
    scaled_size = (
        max(1, int(round(source_w * scale))),
        max(1, int(round(source_h * scale))),
    )
    return pygame.transform.smoothscale(surface, scaled_size)


def _frame_only_texture(size):
    """Zwraca panel2 bez ciemnego wypelnienia srodka kafla."""
    size = (int(size[0]), int(size[1]))
    if size in _FRAME_CACHE:
        return _FRAME_CACHE[size]

    texture = s._load_menu_button_texture(size)
    if texture is None:
        _FRAME_CACHE[size] = None
        return None

    # Panel gornego HUD-u zostaje pod spodem. Z panel2 zachowujemy ozdobna
    # brazowo-zlota rame, a ciemny neutralny srodek robimy przezroczysty.
    cleaned = _clear_dark_neutral_pixels(texture, max_value=48, max_spread=18)
    _FRAME_CACHE[size] = cleaned
    return cleaned


def _transparent_top_icon(icon_name, size):
    """Laduje, oczyszcza, przycina i skaluje sam symbol ikony gornego HUD-u."""
    cache_key = (str(icon_name), int(size))
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    from rg_ui import hud

    filename = hud._TOP_STAT_ICON_FILES.get(str(icon_name))
    icon = None
    if filename:
        path = hud.ROOT_DIR / "Grafiki" / "ikony_gornego_ui" / filename
        if path.exists():
            try:
                source = pygame.image.load(str(path)).convert_alpha()
                source = _clear_dark_neutral_pixels(source, max_value=52, max_spread=20)
                source = _crop_visible_content(source, padding=3)
                icon = _scale_into_square(source, size)
            except (OSError, pygame.error):
                icon = None

    # Awaryjnie korzystamy ze starego loadera, jesli konkretnego pliku zabraknie.
    if icon is None:
        fallback = hud._load_top_stat_icon(icon_name, size)
        if fallback is not None:
            fallback = _clear_dark_neutral_pixels(fallback, max_value=52, max_spread=20)
            fallback = _crop_visible_content(fallback, padding=1)
            icon = _scale_into_square(fallback, size)

    _ICON_CACHE[cache_key] = icon
    return icon


def _responsive_width(screen_width, requested_width, x):
    """Na szerokich ekranach rozciaga kafle, a na 1600 px zachowuje bezpieczny uklad."""
    progress = max(0.0, min(1.0, (screen_width - 1600) / 448.0))
    width_scale = 1.0 + 0.24 * progress
    desired = int(round(requested_width * width_scale))
    return max(1, min(desired, screen_width - int(x) - 12))


def _draw_top_stat_with_panel2(
    screen,
    font,
    text,
    icon_name_or_x,
    x_or_width,
    width=None,
    y=54,
    height=64,
):
    """Rysuje powiekszony kafel HUD-u z duza ikona wypelniajaca osobny kwadrat."""
    if width is None:
        icon_name = None
        x = icon_name_or_x
        width = x_or_width
    else:
        icon_name = icon_name_or_x
        x = x_or_width

    # Zachowujemy dolna krawedz wskazana przez hud.py, ale zwiekszamy wysokosc
    # z 64 do 86 px. Kafel rosnie w gore i nadal miesci sie w panelu HUD-u.
    original_bottom = int(y) + int(height)
    height = max(86, int(height))
    y = original_bottom - height
    width = _responsive_width(screen.get_width(), int(width), int(x))

    box = pygame.Rect(x, y, width, height)
    texture = _frame_only_texture(box.size)

    if texture is not None:
        # Bez pelnego prostokatnego cienia: tlo pochodzi z glownego panelu HUD-u.
        screen.blit(texture, box)
    else:
        pygame.draw.rect(screen, GOLD, box, 2, border_radius=8)

    text_x = box.x + 14
    if icon_name:
        # Ikona ma prawie cala wysokosc kafla. Po przycieciu pustych marginesow
        # faktyczny symbol wypelnia teraz duzy kwadrat ok. 72x72 px.
        icon_square = min(72, box.height - 12)
        icon = _transparent_top_icon(icon_name, icon_square)
        if icon is not None:
            slot = pygame.Rect(box.x + 8, box.centery - icon_square // 2, icon_square, icon_square)
            icon_rect = icon.get_rect(center=slot.center)
            screen.blit(icon, icon_rect)
            text_x = slot.right + 10

    label = font.render(str(text), True, TEXT)
    label_y = box.y + (box.height - label.get_height()) // 2

    label_shadow = font.render(str(text), True, (24, 18, 13))
    screen.blit(label_shadow, (text_x + 1, label_y + 1))
    screen.blit(label, (text_x, label_y))
    return box.right + 8


def install_hud_top_stat_theme():
    """Podmienia gorne pola informacji na duze ramki z duzymi ikonami."""
    from rg_ui import hud

    # W repo ikona Punktow Legendy ma nazwe punkty_legend.png, nie legenda.png.
    hud._TOP_STAT_ICON_FILES["legenda"] = "punkty_legend.png"
    hud._TOP_STAT_ICON_CACHE.clear()
    _ICON_CACHE.clear()
    _FRAME_CACHE.clear()

    hud._draw_top_stat = _draw_top_stat_with_panel2
