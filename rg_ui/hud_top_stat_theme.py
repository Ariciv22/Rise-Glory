import pygame

from rg_core.data import GOLD, PANEL_DARK, TEXT
from rg_ui import screens as s


_FRAME_CACHE = {}


def _frame_only_texture(size):
    """Zwraca panel2 bez ciemnego wypelnienia srodka kafla.

    Panel gornego HUD-u zostaje pod spodem. Tutaj zachowujemy jedynie ozdobna
    rame panel2.png, aby przezroczysty srodek pokazywal teksture glownego panelu,
    a nie czarny prostokat.
    """
    size = (int(size[0]), int(size[1]))
    cached = _FRAME_CACHE.get(size)
    if cached is not None:
        return cached

    texture = s._load_menu_button_texture(size)
    if texture is None:
        _FRAME_CACHE[size] = None
        return None

    cleaned = texture.copy().convert_alpha()
    try:
        rgb = pygame.surfarray.pixels3d(cleaned)
        alpha = pygame.surfarray.pixels_alpha(cleaned)
        channel_min = rgb.min(axis=2)
        channel_max = rgb.max(axis=2)
        # Usuwamy tylko bardzo ciemne, prawie neutralne piksele. Brazowo-zlote
        # elementy ramki maja wieksza roznice kanalow i pozostaja widoczne.
        dark_fill = (channel_max <= 48) & ((channel_max - channel_min) <= 18)
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
                if high <= 48 and high - low <= 18:
                    pixels[px, py] = (0, 0, 0, 0)
        del pixels

    _FRAME_CACHE[size] = cleaned
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
        # Nie rysujemy juz pelnego prostokatnego cienia. Wczesniej ten cien byl
        # widoczny przez przezroczyste fragmenty panel2 i tworzyl czarne tlo.
        screen.blit(texture, box)
    else:
        # Fallback, gdy grafika panel2 jest niedostepna.
        pygame.draw.rect(screen, GOLD, box, 2, border_radius=8)

    text_x = box.x + 12
    if icon_name:
        from rg_ui import hud

        icon = hud._load_top_stat_icon(icon_name, min(38, max(28, height - 20)))
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