import pygame

from rg_data import GOLD, MUTED, PANEL, PANEL_DARK, TEXT
from rg_ui import draw_lines

TOOLTIP_W = 250
TOOLTIP_PADDING = 14


def get_location_lines(tile):
    location = tile.location
    terrain = tile.terrain
    return [
        location["name"],
        f"Typ: {location['name']}",
        f"Teren: {terrain['name']}",
        f"Koszt ruchu: {terrain['move']}",
        "Questy i akcje dodamy pozniej.",
    ]


def clamp_tooltip_position(mouse_pos, tooltip_w, tooltip_h, screen_w, screen_h):
    x = mouse_pos[0] + 22
    y = mouse_pos[1] + 18
    if x + tooltip_w > screen_w - 10:
        x = mouse_pos[0] - tooltip_w - 22
    if y + tooltip_h > screen_h - 10:
        y = mouse_pos[1] - tooltip_h - 18
    return max(10, x), max(10, y)


def draw_location_tooltip(screen, font, small_font, hovered_tile, mouse_pos):
    if not hovered_tile or not hovered_tile.location:
        return

    lines = get_location_lines(hovered_tile)
    tooltip_h = 132
    screen_w, screen_h = screen.get_size()
    x, y = clamp_tooltip_position(mouse_pos, TOOLTIP_W, tooltip_h, screen_w, screen_h)
    rect = pygame.Rect(x, y, TOOLTIP_W, tooltip_h)

    pygame.draw.rect(screen, PANEL, rect, border_radius=12)
    pygame.draw.rect(screen, GOLD, rect, 2, border_radius=12)

    title_rect = pygame.Rect(rect.x + 10, rect.y + 10, rect.width - 20, 30)
    pygame.draw.rect(screen, PANEL_DARK, title_rect, border_radius=8)

    color = hovered_tile.location["color"]
    pygame.draw.circle(screen, color, (title_rect.x + 15, title_rect.centery), 8)
    screen.blit(font.render(lines[0], True, TEXT), (title_rect.x + 32, title_rect.y + 5))

    draw_lines(screen, small_font, lines[1:], rect.x + TOOLTIP_PADDING, rect.y + 50, MUTED, line_h=20, max_width=rect.width - TOOLTIP_PADDING * 2)
