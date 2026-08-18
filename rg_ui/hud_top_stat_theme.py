import pygame

from rg_core.data import GOLD, PANEL_DARK, TEXT
from rg_ui import screens as s


def _draw_top_stat_with_panel2(screen, font, text, x, width):
    """Rysuje gorne pole HUD-u na tej samej grafice panel2.png co przyciski UI."""
    box = pygame.Rect(x, 78, width, 30)
    texture = s._load_menu_button_texture(box.size)

    if texture is not None:
        # Ten sam lekki cien co w kaflach klas i dolnych przyciskach.
        shadow = pygame.Surface(box.size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 72))
        screen.blit(shadow, box.move(2, 2))
        screen.blit(texture, box)
    else:
        # Fallback tylko na wypadek braku panel2.png w paczce gry.
        pygame.draw.rect(screen, PANEL_DARK, box, border_radius=8)
        pygame.draw.rect(screen, GOLD, box, 2, border_radius=8)

    label = font.render(str(text), True, TEXT)
    label_y = box.y + (box.height - label.get_height()) // 2

    # Cien jak w pozostalych przyciskach Rise & Glory; sam tekst zostaje
    # dynamiczny, wiec Zloto/Rany/Akcje itd. nadal aktualizuja sie normalnie.
    label_shadow = font.render(str(text), True, (24, 18, 13))
    screen.blit(label_shadow, (box.x + 10, label_y + 1))
    screen.blit(label, (box.x + 9, label_y))
    return box.right + 8


def install_hud_top_stat_theme():
    """Podmienia wszystkie gorne pola informacji na wspolny panel2.png."""
    from rg_ui import hud

    hud._draw_top_stat = _draw_top_stat_with_panel2
