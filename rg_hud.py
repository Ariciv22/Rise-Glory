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
from rg_location_data import helper_bonus_summary, helper_effect_text
from rg_ui import (
    Button,
    draw_lines,
    draw_textured_button,
    draw_textured_frame,
    draw_textured_panel,
    wrap,
)


def _draw_top_stat(screen, font, text, x, width):
    box = pygame.Rect(x, 76, width, 32)
    draw_textured_panel(screen, box, style="control", fill_color=PANEL_DARK, fill_alpha=255)
    label = font.render(text, True, TEXT)
    screen.blit(label, label.get_rect(center=box.center))
    return box.right + 8


def _draw_scoreboard(screen, font, small_font, players, tokens, active_player_index):
    sw, sh = screen.get_size()
    row_h = 70
    panel_h = min(sh - TOP_BAR_H - SIDE_MARGIN * 2, 94 + len(players) * row_h + 58)
    right = pygame.Rect(sw - RIGHT_PANEL_W - SIDE_MARGIN, TOP_BAR_H + SIDE_MARGIN, RIGHT_PANEL_W, panel_h)
    draw_textured_panel(screen, right, style="panel", fill_color=PANEL_DARK, fill_alpha=248)
    screen.blit(font.render("Tabela graczy", True, TEXT), (right.x + 24, right.y + 20))

    separator_y = right.y + 50
    pygame.draw.line(screen, GOLD, (right.x + 24, separator_y), (right.right - 24, separator_y), 1)

    y = right.y + 62
    for index, player in enumerate(players):
        if y + row_h > right.bottom - 54:
            break
        active = index == active_player_index
        row = pygame.Rect(right.x + 14, y, right.width - 28, row_h - 8)
        draw_textured_panel(
            screen,
            row,
            style="control",
            fill_color=(42, 35, 29) if active else PANEL_DARK,
            fill_alpha=255,
        )

        color = player.get("player_color", GOLD)
        pygame.draw.circle(screen, color, (row.x + 18, row.y + 16), 7)
        marker = "AKTYWNY" if active else f"Gracz {player.get('player_number', index + 1)}"
        marker_color = (255, 226, 165) if active else MUTED
        screen.blit(small_font.render(marker, True, marker_color), (row.x + 32, row.y + 6))

        name_text = player.get("name", "Bohater")
        screen.blit(font.render(name_text, True, TEXT), (row.x + 14, row.y + 27))

        token = tokens[index] if index < len(tokens) else None
        actions = token.actions if token else 0
        helper_count = len(player.get("helpers", []))
        summary = (
            f"L {player.get('legend', 0)}  |  Z {player.get('gold', 0)}  |  "
            f"R {player.get('wounds', 0)}/{MAX_WOUNDS}  |  A {actions}  |  P {helper_count}"
        )
        summary_label = small_font.render(summary, True, MUTED)
        screen.blit(summary_label, (row.x + 14, row.bottom - summary_label.get_height() - 5))
        y += row_h

    end_turn = Button("Koniec tury", "end_turn", (right.x + 66, right.bottom - 46, right.width - 132, 34))
    draw_textured_button(screen, small_font, pygame.mouse.get_pos(), end_turn)
    return end_turn


def _format_stat_value(stat, base_value, bonuses):
    bonus = bonuses.get(stat, 0)
    if bonus <= 0:
        return str(base_value)
    return f"{base_value} +{bonus}"


def _draw_helpers(screen, font, small_font, hero, x, y, width):
    helpers = hero.get("helpers", [])
    screen.blit(small_font.render(f"Pomocnicy: {len(helpers)}/5", True, TEXT), (x, y))
    y += 22
    if not helpers:
        screen.blit(small_font.render("brak", True, MUTED), (x, y))
        return y + 22

    for helper in helpers[:5]:
        line = f"- {helper['name']}: {helper_effect_text(helper)}"
        wrapped = wrap(small_font, line, width)
        for wrapped_line in wrapped[:2]:
            screen.blit(small_font.render(wrapped_line, True, MUTED), (x, y))
            y += 18
        y += 3
    return y


def _draw_bottom_tile_info(screen, font, small_font, selected_tile):
    sw, sh = screen.get_size()
    x = LEFT_PANEL_W + SIDE_MARGIN * 2
    w = sw - LEFT_PANEL_W - RIGHT_PANEL_W - SIDE_MARGIN * 4
    h = 58
    y = sh - h - SIDE_MARGIN
    if w <= 260:
        return

    rect = pygame.Rect(x, y, w, h)
    draw_textured_panel(screen, rect, style="panel", fill_color=PANEL_DARK, fill_alpha=250)
    if selected_tile:
        location = selected_tile.location
        location_name = location["name"] if location else "brak"
        line = (
            f"Heks: {selected_tile.terrain['name']}    |    "
            f"Koszt akcji: {selected_tile.terrain['move']}    |    Lokacja: {location_name}"
        )
    else:
        line = "Kliknij heks na mapie, aby zobaczyc teren, koszt akcji i lokacje."
    label = font.render(line, True, TEXT)
    screen.blit(label, (rect.x + 24, rect.centery - label.get_height() // 2))


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

    map_frame = pygame.Rect(
        LEFT_PANEL_W + SIDE_MARGIN * 2,
        TOP_BAR_H + SIDE_MARGIN,
        sw - LEFT_PANEL_W - RIGHT_PANEL_W - SIDE_MARGIN * 4,
        sh - TOP_BAR_H - SIDE_MARGIN * 2,
    )
    if map_frame.width > 100 and map_frame.height > 100:
        draw_textured_frame(screen, map_frame, style="panel", slice_size=30)

    top = pygame.Rect(0, 0, sw, TOP_BAR_H)
    draw_textured_panel(screen, top, style="panel", fallback_border=ORANGE, fill_color=PANEL_DARK, fill_alpha=252)
    screen.blit(font.render(f"Rise & Glory - {map_name(current_map)}", True, TEXT), (36, 22))

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
        if x + width > sw - 24:
            break
        x = _draw_top_stat(screen, small_font, text, x, width)

    left = pygame.Rect(SIDE_MARGIN, TOP_BAR_H + SIDE_MARGIN, LEFT_PANEL_W, sh - TOP_BAR_H - SIDE_MARGIN * 2)
    draw_textured_panel(screen, left, style="panel", fill_color=PANEL_DARK, fill_alpha=250)
    screen.blit(font.render("Aktywny bohater", True, TEXT), (left.x + 30, left.y + 24))
    pygame.draw.line(screen, GOLD, (left.x + 28, left.y + 52), (left.right - 28, left.y + 52), 1)

    pygame.draw.circle(screen, hero.get("player_color", GOLD), (left.x + 36, left.y + 78), 12)
    screen.blit(font.render(hero["name"], True, TEXT), (left.x + 60, left.y + 66))
    y = left.y + 106
    screen.blit(small_font.render(f"Klasa: {hero.get('archetype_name', '-')}", True, MUTED), (left.x + 30, y))
    y += 28
    y = draw_lines(
        screen,
        small_font,
        wrap(small_font, hero.get("role", ""), left.width - 60),
        left.x + 30,
        y,
        MUTED,
        max_width=left.width - 60,
    )
    y += 14
    screen.blit(small_font.render("Statystyki", True, TEXT), (left.x + 30, y))
    y += 28

    bonuses = helper_bonus_summary(hero)
    for stat, value in hero["stats"].items():
        row = pygame.Rect(left.x + 24, y - 4, left.width - 48, 27)
        draw_textured_panel(screen, row, style="control", fill_color=PANEL_DARK, fill_alpha=255)
        screen.blit(small_font.render(stat, True, TEXT), (row.x + 12, row.y + 5))
        stat_value = _format_stat_value(stat, value, bonuses)
        value_label = small_font.render(stat_value, True, TEXT)
        screen.blit(value_label, (row.right - value_label.get_width() - 12, row.y + 5))
        y += 31

    y += 10
    pygame.draw.line(screen, GOLD, (left.x + 28, y), (left.right - 28, y), 1)
    y += 14
    equipment = [
        f"Item: {hero['basic_item']}",
        f"Klasowy: {hero['class_item']}",
        f"Jedzenie: {', '.join(hero.get('food', [])) or 'brak'}",
        f"Towar: {', '.join(hero.get('goods', [])) or 'brak'}",
    ]
    y = draw_lines(screen, small_font, equipment, left.x + 30, y, MUTED, max_width=left.width - 60)
    y += 10
    _draw_helpers(screen, font, small_font, hero, left.x + 30, y, left.width - 60)

    end_turn = _draw_scoreboard(screen, font, small_font, players, tokens, active_player_index)
    _draw_bottom_tile_info(screen, font, small_font, selected_tile)
    return [end_turn]
