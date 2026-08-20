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
)
from rg_engine.world_events import active_world_event, movement_cost_with_world_event
from rg_content.locations import helper_bonus_summary
from rg_ui.player_board import (
    close_player_board,
    close_quest_details,
    draw_player_board,
    is_player_board_open,
    open_player_board,
    open_quest_details,
)
from rg_ui.common import Button, ROOT_DIR, draw_image_panel, draw_panel, game_layout_rects


_TOP_STAT_ICON_FILES = {
    "gracz": "gracz.png",
    "bohater": "bohater.png",
    "klasa": "klasa.png",
    "legenda": "legenda.png",
    "zloto": "zloto.png",
    "rany": "rany.png",
    "akcje": "akcje.png",
    "runda": "runda.png",
    "rada": "rada.png",
}
_TOP_STAT_ICON_CACHE = {}


class _HudPanelButton(Button):
    """Przycisk HUD-u korzystający z tej samej tekstury panel2.png co menu."""

    def draw(self, screen, font, mouse_pos, active=False):
        draw_image_panel(screen, self.rect, 2)

        hovered = self.rect.collidepoint(mouse_pos)
        if hovered or active:
            glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            glow.fill((255, 220, 135, 22 if hovered else 14))
            screen.blit(glow, self.rect.topleft)

        if active:
            pygame.draw.rect(screen, GOLD, self.rect, 2, border_radius=8)

        if self.text:
            shadow = font.render(self.text, True, (22, 17, 12))
            label = font.render(self.text, True, TEXT)
            center = self.rect.center
            screen.blit(shadow, shadow.get_rect(center=(center[0] + 1, center[1] + 1)))
            screen.blit(label, label.get_rect(center=center))


class _PlayerBoardButton(_HudPanelButton):
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


def _load_top_stat_icon(icon_name, size=20):
    cache_key = (str(icon_name), int(size))
    if cache_key in _TOP_STAT_ICON_CACHE:
        return _TOP_STAT_ICON_CACHE[cache_key]

    filename = _TOP_STAT_ICON_FILES.get(str(icon_name))
    if not filename:
        _TOP_STAT_ICON_CACHE[cache_key] = None
        return None

    path = ROOT_DIR / "Grafiki" / "ikony_gornego_ui" / filename
    if not path.exists():
        _TOP_STAT_ICON_CACHE[cache_key] = None
        return None

    try:
        source = pygame.image.load(str(path)).convert_alpha()
        source_w, source_h = source.get_size()
        if source_w <= 0 or source_h <= 0:
            icon = None
        else:
            scale = min(size / source_w, size / source_h)
            scaled_size = (
                max(1, int(round(source_w * scale))),
                max(1, int(round(source_h * scale))),
            )
            icon = pygame.transform.smoothscale(source, scaled_size)
    except pygame.error:
        icon = None

    _TOP_STAT_ICON_CACHE[cache_key] = icon
    return icon


def _draw_top_stat(screen, font, text, icon_name, x, width, y=54, height=64):
    box = pygame.Rect(x, y, width, height)
    draw_panel(screen, box)

    icon = _load_top_stat_icon(icon_name, min(38, max(28, height - 20)))
    text_x = box.x + 12
    if icon is not None:
        icon_rect = icon.get_rect(midleft=(box.x + 10, box.centery))
        screen.blit(icon, icon_rect)
        text_x = icon_rect.right + 8

    label = font.render(text, True, TEXT)
    shadow = font.render(text, True, (22, 17, 12))
    label_y = box.y + max(0, (box.height - label.get_height()) // 2)
    screen.blit(shadow, (text_x + 1, label_y + 1))
    screen.blit(label, (text_x, label_y))
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

        draw_image_panel(screen, row, 2)
        if active:
            pygame.draw.rect(screen, border, row, 3, border_radius=9)

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
    end_turn = _HudPanelButton("Koniec tury", "end_turn", (right.centerx - 64, button_y, 128, 30))
    end_turn.draw(screen, small_font, pygame.mouse.get_pos())
    return end_turn


def _format_stat_value(stat, base_value, bonuses):
    bonus = bonuses.get(stat, 0)
    if bonus <= 0:
        return str(base_value)
    return f"{base_value} +{bonus}"


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

    # Pelny dekoracyjny panel gornego HUD-u zostaje. Kafle statystyk sa
    # nakladane na niego jako osobne ramki bez pelnego czarnego wypelnienia.
    draw_image_panel(screen, top, 2, ORANGE)

    world_event = active_world_event()
    if world_event:
        duration = "do następnej Rady" if world_event.get("duration") == "until_next_council" else "rozpatrzone"
        event_text = f"Wydarzenie Świata: {world_event.get('name', 'Wydarzenie')} — {duration}"
        screen.blit(small_font.render(event_text, True, GOLD), (14, 16))

    x = 12
    top_stat_h = 64
    top_stat_y = top.bottom - top_stat_h - 8
    top_stats = [
        ("gracz", f"Gracz: {hero.get('player_number', active_player_index + 1)}", 142),
        ("bohater", f"Bohater: {hero['name']}", 224),
        ("klasa", f"Klasa: {hero.get('archetype_name', '-')}", 210),
        ("legenda", f"Legenda: {hero.get('legend', 0)}", 158),
        ("zloto", f"Zloto: {hero.get('gold', 0)}", 140),
        ("rany", f"Rany: {hero.get('wounds', 0)}/{MAX_WOUNDS}", 146),
        ("akcje", f"Akcje: {token.actions}/{ACTIONS_PER_TURN}", 164),
        ("runda", f"Runda: {round_number}", 142),
        ("rada", f"Rada: {council_cycle}/{COUNCIL_ROUNDS}", 146),
    ]
    for icon_name, text, width in top_stats:
        if x + width > sw - 12:
            break
        x = _draw_top_stat(screen, font, text, icon_name, x, width, y=top_stat_y, height=top_stat_h)

    pygame.draw.rect(screen, PANEL_DARK, left)
    draw_image_panel(screen, left, 5)

    # Lewy HUD pokazuje tylko najwazniejsze dane bohatera. Rozbudowane dane
    # ekwipunku, pomocnikow i opis klasy pozostaja dostepne po kliknieciu Bohater.
    pygame.draw.circle(screen, hero.get("player_color", GOLD), (left.x + 34, left.y + 38), 12)
    screen.blit(font.render(hero["name"], True, TEXT), (left.x + 58, left.y + 26))
    y = left.y + 68
    screen.blit(small_font.render(f"Klasa: {hero.get('archetype_name', '-')}", True, MUTED), (left.x + 28, y))
    y += 36
    screen.blit(small_font.render("Statystyki", True, TEXT), (left.x + 28, y))
    y += 26

    bonuses = helper_bonus_summary(hero)
    for stat, value in hero["stats"].items():
        row = pygame.Rect(left.x + 24, y - 4, left.width - 48, 25)
        draw_image_panel(screen, row, 2)
        screen.blit(small_font.render(stat, True, TEXT), (row.x + 10, row.y + 4))
        stat_value = _format_stat_value(stat, value, bonuses)
        value_surface = small_font.render(stat_value, True, TEXT)
        screen.blit(value_surface, (row.right - value_surface.get_width() - 12, row.y + 4))
        y += 29

    hero_button_y = left.bottom - 64
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