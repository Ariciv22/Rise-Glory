import pygame

from rg_core.data import GOLD, PANEL_DARK, TEXT
from rg_ui import screens as s


def _draw_top_stat_with_panel2(
    screen,
    font,
    text,
    icon_name_or_x,
    x_or_width,
    width=None,
    y=64,
    height=46,
):
    """Rysuje gorne pole HUD-u na panel2.png i obsluguje ikone po lewej.

    Funkcja zachowuje zgodnosc ze starym wywolaniem:
        _draw_top_stat(screen, font, text, x, width)
    oraz z nowym:
        _draw_top_stat(screen, font, text, icon_name, x, width, y=..., height=...)
    """
    if width is None:
        icon_name = None
        x = icon_name_or_x
        width = x_or_width
    else:
        icon_name = icon_name_or_x
        x = x_or_width

    box = pygame.Rect(x, y, width, height)
    texture = s._load_menu_button_texture(box.size)

    if texture is not None:
        shadow = pygame.Surface(box.size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 72))
        screen.blit(shadow, box.move(2, 2))
        screen.blit(texture, box)
    else:
        pygame.draw.rect(screen, PANEL_DARK, box, border_radius=8)
        pygame.draw.rect(screen, GOLD, box, 2, border_radius=8)

    text_x = box.x + 10
    if icon_name:
        # Loader ikon pozostaje w hud.py, aby cala konfiguracja nazw i cache
        # byla w jednym miejscu.
        from rg_ui import hud

        icon = hud._load_top_stat_icon(icon_name, min(28, max(20, height - 14)))
        if icon is not None:
            icon_rect = icon.get_rect(midleft=(box.x + 8, box.centery))
            screen.blit(icon, icon_rect)
            text_x = icon_rect.right + 6

    label = font.render(str(text), True, TEXT)
    label_y = box.y + (box.height - label.get_height()) // 2

    label_shadow = font.render(str(text), True, (24, 18, 13))
    screen.blit(label_shadow, (text_x + 1, label_y + 1))
    screen.blit(label, (text_x, label_y))
    return box.right + 8


def install_hud_top_stat_theme():
    """Podmienia wszystkie gorne pola informacji na wspolny panel2.png."""
    from rg_ui import hud

    hud._draw_top_stat = _draw_top_stat_with_panel2
