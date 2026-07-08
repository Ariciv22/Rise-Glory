import pygame

from rg_data import (
    GOLD,
    HERO_MOVES_PER_TURN,
    LEFT_PANEL_W,
    MUTED,
    ORANGE,
    PANEL_DARK,
    SIDE_MARGIN,
    TEXT,
    TOP_BAR_H,
    map_name,
)
from rg_ui import Button, draw_lines, draw_panel, wrap


def draw_game_ui(screen, font, small_font, hero, token, selected_tile, current_map, active_player):
    sw, sh = screen.get_size()
    top = pygame.Rect(0, 0, sw, TOP_BAR_H)
    draw_panel(screen, top, ORANGE)
    screen.blit(font.render(f"Rise & Glory - {map_name(current_map)}", True, TEXT), (36, 26))

    end_turn = Button("Koniec tury", "end_turn", (sw - 180, 77, 150, 36))
    end_turn.draw(screen, small_font, pygame.mouse.get_pos())

    top_stats = [
        f"Tura gracza: {active_player}",
        f"Bohater: {hero['name']}",
        f"Legenda: {hero['legend']}",
        f"Zloto: {hero['gold']}",
        f"Rany: {hero['wounds']}/5",
        f"Ruch: {token.moves}/{HERO_MOVES_PER_TURN}",
    ]
    x = 36
    for item in top_stats:
        box_w = 150 if not item.startswith("Bohater") else 190
        if x + box_w > sw - 200:
            break
        box = pygame.Rect(x, 78, box_w, 30)
        draw_panel(screen, box)
        screen.blit(small_font.render(item, True, TEXT), (box.x + 9, box.y + 6))
        x += box.width + 10

    left = pygame.Rect(SIDE_MARGIN, TOP_BAR_H + SIDE_MARGIN, LEFT_PANEL_W, sh - TOP_BAR_H - SIDE_MARGIN * 2)
    draw_panel(screen, left)
    screen.blit(font.render("Bohater", True, TEXT), (left.x + 28, left.y + 24))
    pygame.draw.circle(screen, hero["color"], (left.x + 34, left.y + 74), 12)
    screen.blit(font.render(hero["name"], True, TEXT), (left.x + 58, left.y + 62))
    y = left.y + 104
    y = draw_lines(screen, small_font, wrap(small_font, hero["role"], left.width - 56), left.x + 28, y, MUTED, max_width=left.width - 56)
    y += 16
    screen.blit(small_font.render("Zdolnosci", True, TEXT), (left.x + 28, y))
    y += 26
    for stat, value in hero["stats"].items():
        row = pygame.Rect(left.x + 24, y - 4, left.width - 48, 25)
        pygame.draw.rect(screen, PANEL_DARK, row, border_radius=8)
        pygame.draw.rect(screen, GOLD, row, 1, border_radius=8)
        screen.blit(small_font.render(stat, True, TEXT), (row.x + 10, row.y + 4))
        screen.blit(small_font.render(str(value), True, TEXT), (row.right - 30, row.y + 4))
        y += 29
    y += 10
    equip = [f"Item: {hero['basic_item']}", f"Klasowy: {hero['class_item']}"]
    draw_lines(screen, small_font, equip, left.x + 28, y, MUTED, max_width=left.width - 56)

    if selected_tile:
        info_y = left.bottom - 112
        pygame.draw.line(screen, GOLD, (left.x + 24, info_y - 12), (left.right - 24, info_y - 12), 1)
        location = selected_tile.location
        location_name = location["name"] if location else "brak"
        lines = [
            f"Heks: {selected_tile.terrain['name']}",
            f"Koszt ruchu: {selected_tile.terrain['move']}",
            f"Lokacja: {location_name}",
            "Questy dodamy pozniej.",
        ]
        draw_lines(screen, small_font, lines, left.x + 28, info_y, TEXT, max_width=left.width - 56)
    return [end_turn]
