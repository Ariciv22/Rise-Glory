import pygame

from rg_data import (
    ACTIONS_PER_TURN,
    COUNCIL_ROUNDS,
    GOLD,
    LEFT_PANEL_W,
    MAX_WOUNDS,
    MUTED,
    ORANGE,
    PANEL_DARK,
    RIGHT_PANEL_W,
    SIDE_MARGIN,
    TEXT,
    TOP_BAR_H,
    map_name,
)
from rg_ui import Button, draw_lines, draw_panel, wrap


def _draw_top_stat(screen, font, text, x, width):
    box = pygame.Rect(x, 78, width, 30)
    draw_panel(screen, box)
    screen.blit(font.render(text, True, TEXT), (box.x + 9, box.y + 6))
    return box.right + 8


def _draw_scoreboard(screen, font, small_font, players, tokens, active_player_index):
    sw, sh = screen.get_size()
    right = pygame.Rect(sw - RIGHT_PANEL_W - SIDE_MARGIN, TOP_BAR_H + SIDE_MARGIN, RIGHT_PANEL_W, sh - TOP_BAR_H - SIDE_MARGIN * 2)
    draw_panel(screen, right)
    screen.blit(font.render("Tabela graczy", True, TEXT), (right.x + 22, right.y + 22))

    row_h = 92
    y = right.y + 64
    for index, player in enumerate(players):
        if y + row_h > right.bottom - 12:
            break
        active = index == active_player_index
        border = player.get("player_color", GOLD) if active else GOLD
        row = pygame.Rect(right.x + 14, y, right.width - 28, row_h - 8)
        pygame.draw.rect(screen, PANEL_DARK, row, border_radius=10)
        pygame.draw.rect(screen, border, row, 3 if active else 1, border_radius=10)

        color = player.get("player_color", GOLD)
        pygame.draw.circle(screen, color, (row.x + 18, row.y + 20), 9)
        marker = "AKTYWNY" if active else f"Gracz {player.get('player_number', index + 1)}"
        screen.blit(small_font.render(marker, True, TEXT if active else MUTED), (row.x + 34, row.y + 10))
        screen.blit(font.render(player.get("name", "Bohater"), True, TEXT), (row.x + 14, row.y + 34))
        hero_class = player.get("archetype_name", player.get("name", "Bohater"))
        screen.blit(small_font.render(hero_class, True, MUTED), (row.x + 14, row.y + 60))

        token = tokens[index] if index < len(tokens) else None
        actions = token.actions if token else 0
        summary = f"L {player.get('legend', 0)} | Z {player.get('gold', 0)} | R {player.get('wounds', 0)}/{MAX_WOUNDS} | A {actions}"
        summary_label = small_font.render(summary, True, TEXT)
        screen.blit(summary_label, (row.right - summary_label.get_width() - 10, row.y + 60))
        y += row_h


def draw_game_ui(
    screen,
    font,
    small_font,
    hero,
    token,
    selected_tile,
    current_map,
    active_player_index,
    players,
    tokens,
    round_number,
    council_cycle,
):
    sw, sh = screen.get_size()
    top = pygame.Rect(0, 0, sw, TOP_BAR_H)
    draw_panel(screen, top, ORANGE)
    screen.blit(font.render(f"Rise & Glory - {map_name(current_map)}", True, TEXT), (36, 22))

    end_turn = Button("Koniec tury", "end_turn", (sw - 180, 77, 150, 36))
    end_turn.draw(screen, small_font, pygame.mouse.get_pos())

    x = 36
    top_stats = [
        (f"Gracz: {hero.get('player_number', active_player_index + 1)}", 112),
        (f"Bohater: {hero['name']}", 180),
        (f"Klasa: {hero.get('archetype_name', '-')}", 170),
        (f"Legenda: {hero.get('legend', 0)}", 126),
        (f"Zloto: {hero.get('gold', 0)}", 108),
        (f"Rany: {hero.get('wounds', 0)}/{MAX_WOUNDS}", 112),
        (f"Akcje: {token.actions}/{ACTIONS_PER_TURN}", 126),
        (f"Runda: {round_number}", 108),
        (f"Rada: {council_cycle}/{COUNCIL_ROUNDS}", 110),
    ]
    for text, width in top_stats:
        if x + width > sw - 195:
            break
        x = _draw_top_stat(screen, small_font, text, x, width)

    left = pygame.Rect(SIDE_MARGIN, TOP_BAR_H + SIDE_MARGIN, LEFT_PANEL_W, sh - TOP_BAR_H - SIDE_MARGIN * 2)
    draw_panel(screen, left)
    screen.blit(font.render("Aktywny bohater", True, TEXT), (left.x + 28, left.y + 24))
    pygame.draw.circle(screen, hero.get("player_color", GOLD), (left.x + 34, left.y + 74), 12)
    screen.blit(font.render(hero["name"], True, TEXT), (left.x + 58, left.y + 62))
    y = left.y + 102
    screen.blit(small_font.render(f"Klasa: {hero.get('archetype_name', '-')}", True, MUTED), (left.x + 28, y))
    y += 28
    y = draw_lines(screen, small_font, wrap(small_font, hero.get("role", ""), left.width - 56), left.x + 28, y, MUTED, max_width=left.width - 56)
    y += 14
    screen.blit(small_font.render("Statystyki", True, TEXT), (left.x + 28, y))
    y += 26
    for stat, value in hero["stats"].items():
        row = pygame.Rect(left.x + 24, y - 4, left.width - 48, 25)
        pygame.draw.rect(screen, PANEL_DARK, row, border_radius=8)
        pygame.draw.rect(screen, GOLD, row, 1, border_radius=8)
        screen.blit(small_font.render(stat, True, TEXT), (row.x + 10, row.y + 4))
        screen.blit(small_font.render(str(value), True, TEXT), (row.right - 30, row.y + 4))
        y += 29

    y += 8
    equipment = [
        f"Item: {hero['basic_item']}",
        f"Klasowy: {hero['class_item']}",
        f"Jedzenie: {', '.join(hero.get('food', [])) or 'brak'}",
        f"Towar: {', '.join(hero.get('goods', [])) or 'brak'}",
    ]
    draw_lines(screen, small_font, equipment, left.x + 28, y, MUTED, max_width=left.width - 56)

    if selected_tile:
        info_y = left.bottom - 112
        pygame.draw.line(screen, GOLD, (left.x + 24, info_y - 12), (left.right - 24, info_y - 12), 1)
        location = selected_tile.location
        location_name = location["name"] if location else "brak"
        lines = [
            f"Heks: {selected_tile.terrain['name']}",
            f"Koszt akcji: {selected_tile.terrain['move']}",
            f"Lokacja: {location_name}",
        ]
        draw_lines(screen, small_font, lines, left.x + 28, info_y, TEXT, max_width=left.width - 56)

    _draw_scoreboard(screen, font, small_font, players, tokens, active_player_index)
    return [end_turn]
