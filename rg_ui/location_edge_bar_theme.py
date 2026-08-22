import pygame

from rg_ui import city_hub
from rg_ui.common import draw_image_panel


def _draw_ornate_edge_bar(screen, rect, message=""):
    """Rysuje gorny/dolny pasek lokacji jako pelny dekoracyjny panel UI.

    Uzywamy tego samego panel2.png, ktory jest juz stosowany w innych czesciach
    gry. Dzieki temu na calej szerokosci widoczne sa zlote naroza, ornamenty i
    obramowanie zamiast samych prostych linii.
    """
    rect = pygame.Rect(rect)
    if rect.width <= 0 or rect.height <= 0:
        return

    draw_image_panel(screen, rect, 2)

    if message:
        bar_font = pygame.font.SysFont("arial", 16, bold=True)
        label = bar_font.render(str(message)[:150], True, city_hub.city.MUTED)

        # Tekst trzymamy z dala od ozdobnych naroznikow panelu.
        side_pad = max(28, int(round(rect.width * 0.035)))
        max_width = max(1, rect.width - side_pad * 2)
        text = str(message)[:150]
        while text and bar_font.size(text)[0] > max_width:
            text = text[:-1]
        if text != str(message)[:150] and len(text) > 3:
            text = text[:-3].rstrip() + "..."
            label = bar_font.render(text, True, city_hub.city.MUTED)

        screen.blit(
            label,
            (rect.x + side_pad, rect.centery - label.get_height() // 2),
        )


def install_location_edge_bar_theme():
    if getattr(city_hub, "_rise_glory_location_edge_bar_theme_installed", False):
        return

    city_hub._draw_edge_bar = _draw_ornate_edge_bar
    city_hub._draw_bottom_bar = _draw_ornate_edge_bar
    city_hub._rise_glory_location_edge_bar_theme_installed = True
