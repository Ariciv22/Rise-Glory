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
    """Usuwa czarne kwadratowe tlo zapisane w ikonach gornego HUD-u."""
    cache_key = (str(icon_name), int(size))
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    from rg_ui import hud

    icon = hud._load_top_stat_icon(icon_name, size)
    if icon is None:
        _ICON_CACHE[cache_key] = None
        return None

    # Ikony sa glownie zlote/kolorowe, wiec usuniecie bardzo ciemnych neutralnych
    # pikseli wycina ich czarne tlo bez naruszania glownego symbolu.
    cleaned = _clear_dark_neutral_pixels(icon, max_value=52, max_spread=20)
    _ICON_CACHE[cache_key] = cleaned
    return cleaned


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
    """Rysuje duzy kafel HUD-u jako przezroczysta ozdobna ramke panel2.png."""
    if width is None:
        icon_name = None
        x = icon_name_or_x
        width = x_or_width
    else:
        icon_name = icon_name_or_x
        x = x_or_width

    box = pygame.Rect(x, y, width, height)
    texture = _frame_only_texture(box.size)

    if texture is not None:
        # Bez pelnego prostokatnego cienia: to on wczesniej tworzyl czarne
        # wypelnienie widoczne przez przezroczyste fragmenty ramki.
        screen.blit(texture, box)
    else:
        pygame.draw.rect(screen, GOLD, box, 2, border_radius=8)

    text_x = box.x + 12
    if icon_name:
        icon_size = min(38, max(28, height - 20))
        icon = _transparent_top_icon(icon_name, icon_size)
        if icon is not None:
            icon_rect = icon.get_rect(midleft=(box.x + 10, box.centery))
            screen.blit(icon, icon_rect)
            text_x = icon_rect.right + 8

    label = font.render(str(text), True, TEXT)
    label_y = box.y + (box.height - label.get_height()) // 2

    label_shadow = font.render(str(text), True, (24, 18, 13))
    screen.blit(label_shadow, (text_x + 1, label_y + 1))
    screen.blit(label, (text_x, label_y))
    return box.right + 8


def install_hud_top_stat_theme():
    """Podmienia gorne pola informacji na duze, przezroczyste ramki panel2.png."""
    from rg_ui import hud

    hud._draw_top_stat = _draw_top_stat_with_panel2