import pygame

from rg_core.data import (
    ACTIONS_PER_TURN,
    COUNCIL_ROUNDS,
    GOLD,
    MAX_WOUNDS,
    MUTED,
    ORANGE,
    PANEL_DARK,
    TEXT,
    map_name,
)
from rg_engine.world_events import active_world_event, movement_cost_with_world_event
from rg_content.locations import helper_bonus_summary, helper_effect_text
from rg_ui.player_board import (
    close_player_board,
    close_quest_details,
    draw_player_board,
    is_player_board_open,
    open_player_board,
    open_quest_details,
)
from rg_ui.common import Button, draw_image_panel, draw_lines, draw_panel, game_layout_rects, wrap


class _PlayerBoardButton(Button):
    def clicked(self, pos):
        if not super().clicked(pos):
            return False
        if self.action == "open_player_board":
            open_player_board()
        elif self.action == "close_player_board":
            close_player_board()
        elif self.action == "close_active_quest":
            close_quest_details()
        elif str(self.action).startswith("open_active_quest:"):
            open_quest_details(str(self.action).split(":", 1)[1])
        return True


def _draw_top_stat(screen, font, text, x, width):
    box = pygame.Rect(x, 78, width, 30)
    draw_panel(screen, box)
    screen.blit(font.render(text, True, TEXT), (box.x + 9, box.y + 6))
    return box.right + 8


def _draw_scoreboard(screen, font, small_font, players, tokens, active_player_index, right):
    pygame.draw.rect(screen, PANEL_DARK, right)
    draw_image_panel(screen, right, 5)
    screen.blit(font.render("Tabela graczy", True, TEXT), (right.x + 22, right.y + 18))

    row_h = 58
    y = right.y + 56
    for index, player in enumerate(players):
        if y + row_h > right.bottom - 52:
            break
        active = index == active_player_index
        border = player.get("player_color", GOLD) if active else GOLD
        row = pygame.Rect(right.x + 12, y, right.width - 24, row_h - 8)
        pygame.draw.rect(screen, PANEL_DARK, row, border_radius=9)
        pygame.draw.rect(screen, border, row, 3 if active else 1, border_radius=9)

        color = player.get("player_color", GOLD)
        pygame.draw.circle(screen, color, (row.x + 16, row.y + 15), 7)
        marker = "AKTYWNY" if active else f"Gracz {player.get('player_number', index + 1)}"
        screen.blit(small_font.render(marker, True, TEXT if active else MUTED), (row.x + 30, row.y + 5))
        name_text = player.get("name", "Bohater")
        screen.blit(font.render(name_text, True, TEXT), (row.x + 12, row.y + 24))

        token = tokens[index] if index < len(tokens) else None
        actions = token.actions if token else 0
        helper_count = len(player.get("helpers", []))
        summary = f"L {player.get('legend', 0)} | Z {player.get('gold', 0)} | R {player.get('wounds', 0)}/{MAX_WOUNDS} | A {actions} | P {helper_count}"
        summary_label = small_font.render(summary, True, MUTED)
        screen.blit(summary_label, (row.right - summary_label.get_width() - 10, row.y + 28))
        y += row_h

    button_y = min(right.bottom - 42, y + 6)
    end_turn = Button("Koniec tury", "end_turn", (right.centerx - 64, button_y, 128, 30))
    end_turn.draw(screen, small_font, pygame.mouse.get_pos())
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


def _draw_bottom_tile_info(screen, font, small_font, selected_tile, rect):
    if rect.width <= 260 or rect.height <= 0:
        return

    pygame.draw.rect(screen, PANEL_DARK, rect)
    draw_image_panel(screen, rect, 2)
    if selected_tile:
        location = selected_tile.location
        location_name = location["name"] if location else "brak"
        base_cost = int(selected_tile.terrain["move"])
        actual_cost = movement_cost_with_world_event(base_cost)
        cost_text = str(actual_cost) if actual_cost == base_cost else f"{actual_cost} (bazowo {base_cost})"
        line = f"Heks: {selected_tile.terrain['name']}    |    Koszt akcji: {cost_text}    |    Lokacja: {location_name}"
    else:
        line = "Kliknij heks na mapie, aby zobaczyc teren, koszt akcji i lokacje."
    screen.blit(font.render(line, True, TEXT), (rect.x + 20, rect.y + max(0, (rect.height - font.get_height()) // 2)))


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
    layout = game_layout_rects(screen)
    top = layout["top"]
    left = layout["left"]
    right = layout["right"]
    bottom = layout["bottom"]

    # Pelne prostokaty pod teksturami usuwaja przeswity na zaokraglonych rogach
    # i lacza top, lewy oraz prawy panel w jedna rame wokol planszy.
    pygame.draw.rect(screen, PANEL_DARK, top)
    draw_image_panel(screen, top, 2, ORANGE)
    screen.blit(font.render(f"Rise & Glory - {map_name(current_map)}", True, TEXT), (36, 18))

    world_event = active_world_event()
    if world_event:
        duration = "do następnej Rady" if world_event.get("duration") == "until_next_council" else "rozpatrzone"
        event_text = f"Wydarzenie Świata: {world_event.get('name', 'Wydarzenie')} — {duration}"
        screen.blit(small_font.render(event_text, True, GOLD), (36, 48))

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

    pygame.draw.rect(screen, PANEL_DARK, left)
    draw_image_panel(screen, left, 5)
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

    bonuses = helper_bonus_summary(hero)
    for stat, value in hero["stats"].items():
        row = pygame.Rect(left.x + 24, y - 4, left.width - 48, 25)
        pygame.draw.rect(screen, PANEL_DARK, row, border_radius=8)
        pygame.draw.rect(screen, GOLD, row, 1, border_radius=8)
        screen.blit(small_font.render(stat, True, TEXT), (row.x + 10, row.y + 4))
        stat_value = _format_stat_value(stat, value, bonuses)
        screen.blit(small_font.render(stat_value, True, TEXT), (row.right - 58, row.y + 4))
        y += 29

    y += 8
    equipment = [
        f"Item: {hero['basic_item']}",
        f"Klasowy: {hero['class_item']}",
        f"Jedzenie: {', '.join(hero.get('food', [])) or 'brak'}",
        f"Towar: {', '.join(hero.get('goods', [])) or 'brak'}",
    ]
    y = draw_lines(screen, small_font, equipment, left.x + 28, y, MUTED, max_width=left.width - 56)
    y += 8
    y = _draw_helpers(screen, font, small_font, hero, left.x + 28, y, left.width - 56)

    hero_button_y = min(left.bottom - 64, max(left.y + 420, y + 12))
    hero_button = _PlayerBoardButton(
        "Bohater",
        "open_player_board",
        (left.x + 24, hero_button_y, left.width - 48, 46),
    )
    hero_button.draw(screen, font, pygame.mouse.get_pos())

    end_turn = _draw_scoreboard(screen, font, small_font, players, tokens, active_player_index, right)
    _draw_bottom_tile_info(screen, font, small_font, selected_tile, bottom)

    if is_player_board_open():
        controls = draw_player_board(screen, hero)
        close_button = _PlayerBoardButton("Powrot do mapy", "close_player_board", controls["close_rect"])
        close_button.draw(screen, small_font, pygame.mouse.get_pos())

        board_buttons = []
        if controls["quest_close_rect"] is not None:
            board_buttons.append(_PlayerBoardButton("", "close_active_quest", controls["quest_close_rect"]))
        else:
            for index, rect in enumerate(controls["quest_rows"]):
                board_buttons.append(_PlayerBoardButton("", f"open_active_quest:{index}", rect))

        blocker = Button("", "player_board_block", screen.get_rect())
        return [*board_buttons, close_button, blocker]

    return [hero_button, end_turn]
