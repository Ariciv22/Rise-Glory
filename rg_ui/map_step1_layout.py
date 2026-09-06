from __future__ import annotations

import pygame

from rg_ui import hex_info_panel, hud, world_state
from rg_ui.combat import is_combat_active
from rg_ui.common import Button, draw_image_panel, game_layout_rects


_INSTALLED = False
_SCOREBOARD_OPEN = False
_ORIGINAL_DRAW_GAME_UI = None
_ORIGINAL_DRAW_HEX_INFO = None
_ORIGINAL_WORLD_STATE_OVERLAY = None
_ORIGINAL_HEX_INFO_RECT = None


def is_scoreboard_open() -> bool:
    return bool(_SCOREBOARD_OPEN)


def set_scoreboard_open(value: bool) -> None:
    global _SCOREBOARD_OPEN
    _SCOREBOARD_OPEN = bool(value)


def toggle_scoreboard() -> bool:
    set_scoreboard_open(not is_scoreboard_open())
    return is_scoreboard_open()


class _ScoreboardToggleButton(hud._HudPanelButton):
    def clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        toggle_scoreboard()
        return True


class _RightPanelBlocker(Button):
    def clicked(self, pos):
        return self.rect.collidepoint(pos)


def _find_action_button(controller, action):
    current = controller
    visited = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        if getattr(current, "action", None) == action and hasattr(current, "rect"):
            return current
        current = getattr(current, "delegate", None)
    return None


def _fit(font, text, width):
    value = str(text or "")
    if font.size(value)[0] <= width:
        return value
    suffix = "..."
    while value and font.size(value + suffix)[0] > width:
        value = value[:-1]
    return value.rstrip() + suffix


def _right_content_rect(screen):
    right = game_layout_rects(screen)["right"]
    # Dol zostaje dla dynamicznych akcji Questa/Zagrozenia i przycisku konca tury.
    reserved_bottom = max(205, min(285, int(round(right.height * 0.27))))
    return pygame.Rect(
        right.x + 10,
        right.y + 12,
        right.width - 20,
        max(180, right.height - reserved_bottom - 20),
    )


def _draw_right_placeholder(screen, font, small_font, selected_tile):
    right = game_layout_rects(screen)["right"]
    draw_image_panel(screen, right, 5)

    content = _right_content_rect(screen)
    draw_image_panel(screen, content, 2)
    title = font.render("Informacje o heksie", True, hud.TEXT)
    screen.blit(title, title.get_rect(center=(content.centerx, content.y + 34)))

    if selected_tile is None:
        text = "Wybierz heks na mapie, aby zobaczyć jego szczegóły."
    else:
        text = "Szczegóły wybranego heksa są wyświetlane w tym panelu."
    text = _fit(small_font, text, content.width - 32)
    label = small_font.render(text, True, hud.MUTED)
    screen.blit(label, label.get_rect(center=(content.centerx, content.y + 72)))


def _draw_scoreboard_in_right(screen, font, small_font, players, tokens, active_player_index):
    right = game_layout_rects(screen)["right"]
    draw_image_panel(screen, right, 5)

    content = _right_content_rect(screen)
    draw_image_panel(screen, content, 2)

    header = pygame.Rect(content.x + 10, content.y + 10, content.width - 20, 40)
    draw_image_panel(screen, header, 2)
    title = font.render("Tabela graczy", True, hud.TEXT)
    screen.blit(title, title.get_rect(center=header.center))

    row_h = 56
    gap = 6
    y = header.bottom + 10
    for index, player in enumerate(players):
        if y + row_h > content.bottom - 10:
            break
        active = index == active_player_index
        row = pygame.Rect(content.x + 10, y, content.width - 20, row_h)
        draw_image_panel(screen, row, 2)
        if active:
            pygame.draw.rect(
                screen,
                player.get("player_color", hud.GOLD),
                row,
                3,
                border_radius=9,
            )

        color = player.get("player_color", hud.GOLD)
        pygame.draw.circle(screen, color, (row.x + 16, row.y + 16), 7)
        marker = "AKTYWNY" if active else f"GRACZ {player.get('player_number', index + 1)}"
        name = str(player.get("name", "Bohater"))
        headline = _fit(small_font, f"{marker}  {name}", row.width - 48)
        screen.blit(
            small_font.render(headline, True, hud.TEXT if active else hud.MUTED),
            (row.x + 30, row.y + 7),
        )

        token = tokens[index] if index < len(tokens) else None
        actions = int(getattr(token, "actions", 0) or 0) if token is not None else 0
        helpers = len(player.get("helpers", []))
        summary = (
            f"L {player.get('legend', 0)} | Z {player.get('gold', 0)} | "
            f"R {player.get('wounds', 0)}/{hud.MAX_WOUNDS} | A {actions} | P {helpers}"
        )
        summary = _fit(small_font, summary, row.width - 24)
        screen.blit(small_font.render(summary, True, hud.MUTED), (row.x + 12, row.y + 32))
        y += row_h + gap


def _redraw_end_turn(screen, small_font, buttons):
    right = game_layout_rects(screen)["right"]
    rect = pygame.Rect(right.centerx - 70, right.bottom - 46, 140, 34)
    found = None
    for button in buttons:
        found = _find_action_button(button, "end_turn")
        if found is not None:
            break
    if found is None:
        found = hud._HudPanelButton("Koniec tury", "end_turn", rect)
        buttons.append(found)
    found.rect = rect
    found.draw(screen, small_font, pygame.mouse.get_pos())
    return found


def _draw_left_scoreboard_button(screen, font, buttons):
    left = game_layout_rects(screen)["left"]
    rect = pygame.Rect(left.x + 24, left.bottom - 116, left.width - 48, 44)
    button = _ScoreboardToggleButton("Tabela wyników", "toggle_scoreboard", rect)
    button.draw(screen, font, pygame.mouse.get_pos(), active=is_scoreboard_open())
    buttons.insert(0, button)
    return button


def _draw_bottom_action_bar(screen, font, small_font, hero, token, selected_tile, mouse):
    # Krok 1: rozpiska heksa nie jest juz kopiowana do dolnego HUD-u.
    # Zostaja tu tylko akcje, komunikat gry i przycisk Wydarzen Swiata.
    from rg_engine.production import player_has_right, potential, start_site_construction
    from rg_ui import production_hud

    _ = font
    rect = game_layout_rects(screen)["bottom"]
    if rect.width <= 300 or rect.height <= 0:
        return []
    draw_image_panel(screen, rect, 2)

    buttons = []
    state_rect = production_hud._world_state_slot(rect)
    on_selected = selected_tile is not None and token is not None and getattr(token, "tile", None) is selected_tile
    selected_value = potential(selected_tile) if selected_tile is not None else {}
    selected_site = getattr(selected_tile, "production_site", None) if selected_tile is not None else None
    can_build = (
        on_selected
        and selected_site is None
        and selected_value.get("material")
        and player_has_right(hero, selected_tile)
    )

    if can_build:
        action_rect = pygame.Rect(rect.x + 190, rect.y + max(6, (rect.height - 38) // 2), 190, 38)
        button = production_hud.ProductionActionButton(
            "Buduj zakład",
            f"production_build:{selected_tile.id}",
            action_rect,
            lambda: start_site_construction(hero, token, selected_tile),
            hero,
        )
        button.draw(screen, small_font, mouse)
        buttons.append(button)

    message = str(hero.get("_map_message", ""))
    if message:
        left = 400 if can_build else 205
        max_width = max(80, state_rect.x - rect.x - left - 18)
        message = production_hud._shorten(small_font, message, max_width)
        screen.blit(
            small_font.render(message, True, hud.MUTED),
            (rect.x + left, rect.y + max(8, (rect.height - small_font.get_height()) // 2)),
        )

    world_state._draw_state_button(screen, small_font, rect)
    return buttons


def draw_game_ui_step1(
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
    buttons = list(
        _ORIGINAL_DRAW_GAME_UI(
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
        )
        or []
    )

    if hud.is_player_board_open() or world_state.is_world_state_open() or is_combat_active():
        return buttons

    _draw_left_scoreboard_button(screen, font, buttons)

    if is_scoreboard_open():
        _draw_scoreboard_in_right(screen, font, small_font, players, tokens, active_player_index)
        _redraw_end_turn(screen, small_font, buttons)
        right = game_layout_rects(screen)["right"]
        blocker_rect = pygame.Rect(right.x, right.y, right.width, max(0, right.height - 58))
        buttons.insert(1, _RightPanelBlocker("", "scoreboard_block", blocker_rect))
    else:
        _draw_right_placeholder(screen, font, small_font, selected_tile)
        _redraw_end_turn(screen, small_font, buttons)
        # Przy normalnym widoku zachowujemy istniejace przyciski Questa/Zagrozenia.
        world_state._draw_hex_actions(
            screen,
            small_font,
            players,
            tokens,
            active_player_index,
            game_layout_rects(screen)["right"],
        )

    return buttons


def _right_hex_info_rect(screen):
    return _right_content_rect(screen)


def draw_hex_info_step1(screen, font, small_font, hero, token, selected_tile, mouse_pos):
    if is_scoreboard_open():
        return []
    return _ORIGINAL_DRAW_HEX_INFO(screen, font, small_font, hero, token, selected_tile, mouse_pos)


def draw_world_state_without_map_shade(screen, font, small_font):
    original_shade = world_state._draw_modal_shade
    world_state._draw_modal_shade = lambda _screen: None
    try:
        return _ORIGINAL_WORLD_STATE_OVERLAY(screen, font, small_font)
    finally:
        world_state._draw_modal_shade = original_shade


def install_map_step1_layout(app_module=None):
    global _INSTALLED, _ORIGINAL_DRAW_GAME_UI, _ORIGINAL_DRAW_HEX_INFO
    global _ORIGINAL_WORLD_STATE_OVERLAY, _ORIGINAL_HEX_INFO_RECT
    if _INSTALLED:
        return

    from rg_ui import production_hud

    _ORIGINAL_DRAW_GAME_UI = hud.draw_game_ui
    _ORIGINAL_DRAW_HEX_INFO = hex_info_panel.draw_hex_info_panel
    _ORIGINAL_WORLD_STATE_OVERLAY = world_state._draw_world_state_overlay
    _ORIGINAL_HEX_INFO_RECT = hex_info_panel.hex_info_panel_rect

    # Dolny HUD traci duplikat informacji o heksie; funkcjonalne przyciski zostaja.
    production_hud._draw_tile_economy = _draw_bottom_action_bar

    # Szczegoly heksa trafiaja do stalego prawego panelu.
    hex_info_panel.hex_info_panel_rect = _right_hex_info_rect
    hex_info_panel.draw_hex_info_panel = draw_hex_info_step1

    # Tabela graczy jest od teraz widokiem wywolywanym guzikiem z lewego HUD-u.
    hud.draw_game_ui = draw_game_ui_step1

    # Glowne okno Wydarzen Swiata nie przyciemnia mapy.
    world_state._draw_world_state_overlay = draw_world_state_without_map_shade

    if app_module is not None:
        app_module.draw_game_ui = draw_game_ui_step1
        app_module.draw_hex_info_panel = draw_hex_info_step1

    _INSTALLED = True
