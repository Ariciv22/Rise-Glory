from __future__ import annotations

import pygame


_INSTALLED = False


def install_quest_hex_info_visibility(app_module=None) -> None:
    """Finalna warstwa mapowego UI po instalacji pozostalych wrapperow.

    - panel heksa siedzi w prawym UI zamiast nad plansza,
    - Tabela graczy nie jest obecnie rysowana,
    - glowne okno Wydarzen Swiata nie przyciemnia mapy,
    - panel heksa nadal znika pod modalem Questa.

    Logika Questa, Zagrozen i przycisku Koniec tury pozostaje w istniejacym
    lancuchu kontrolerow; ta warstwa zmienia wylacznie prezentacje.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    from rg_ui import hex_info_panel, hud, world_state
    from rg_ui.combat import is_combat_active
    from rg_ui.common import draw_image_panel, game_layout_rects
    from rg_ui.quest_markers import is_quest_marker_modal_open

    original_draw_hex_info_panel = hex_info_panel.draw_hex_info_panel
    original_scoreboard = hud._draw_scoreboard
    original_world_state_overlay = world_state._draw_world_state_overlay

    def find_action_button(controller, action):
        current = controller
        visited = set()
        while current is not None and id(current) not in visited:
            visited.add(id(current))
            if getattr(current, "action", None) == action and hasattr(current, "rect"):
                return current
            current = getattr(current, "delegate", None)
        return None

    def right_hex_info_rect(screen):
        """Miesci rozpiske heksa w gornej czesci stalego prawego panelu."""
        right = game_layout_rects(screen)["right"]
        side_pad = 12

        # Dol prawego panelu zostaje dla akcji Questow/Zagrozen oraz Konca tury.
        reserved_bottom = max(280, min(360, int(round(right.height * 0.38))))
        height = max(260, right.height - reserved_bottom - 24)
        return pygame.Rect(
            right.x + side_pad,
            right.y + 12,
            max(1, right.width - side_pad * 2),
            height,
        )

    def scoreboard_without_table(
        screen,
        font,
        small_font,
        players,
        tokens,
        active_player_index,
        right,
    ):
        """Zachowuje kontrolery prawego HUD-u, ale usuwa Tabele graczy."""
        controller = original_scoreboard(
            screen,
            font,
            small_font,
            players,
            tokens,
            active_player_index,
            right,
        )

        if is_combat_active():
            return controller

        # Poprzednie wrappery mogly narysowac Tabele graczy. Czyscimy prawa
        # kolumne i odtwarzamy jedynie elementy funkcjonalne, ktore maja zostac.
        pygame.draw.rect(screen, hud.PANEL_DARK, right)
        draw_image_panel(screen, right, 5)

        end_turn = find_action_button(controller, "end_turn")
        if end_turn is not None:
            end_turn.rect = pygame.Rect(
                right.centerx - 70,
                right.bottom - 46,
                140,
                34,
            )
            end_turn.draw(screen, small_font, pygame.mouse.get_pos())

        # To jest finalny, juz opakowany renderer: zawiera Problemy, Questy
        # oraz rozwiazywanie zablokowanych Zagrozen z sasiedniego heksa.
        world_state._draw_hex_actions(
            screen,
            small_font,
            players,
            tokens,
            active_player_index,
            right,
        )
        return controller

    def draw_hex_info_panel_with_quest_visibility(
        screen,
        font,
        small_font,
        hero,
        token,
        selected_tile,
        mouse_pos,
    ):
        if is_quest_marker_modal_open():
            return []
        return original_draw_hex_info_panel(
            screen,
            font,
            small_font,
            hero,
            token,
            selected_tile,
            mouse_pos,
        )

    def draw_world_state_without_map_shade(screen, font, small_font):
        """Glowne okno Wydarzen Swiata zostawia mape jasna i czytelna."""
        original_shade = world_state._draw_modal_shade
        world_state._draw_modal_shade = lambda _screen: None
        try:
            return original_world_state_overlay(screen, font, small_font)
        finally:
            world_state._draw_modal_shade = original_shade

    hex_info_panel.hex_info_panel_rect = right_hex_info_rect
    hex_info_panel.draw_hex_info_panel = draw_hex_info_panel_with_quest_visibility
    hud._draw_scoreboard = scoreboard_without_table
    world_state._draw_world_state_overlay = draw_world_state_without_map_shade

    if app_module is not None:
        app_module.draw_hex_info_panel = draw_hex_info_panel_with_quest_visibility
        # app.py importuje hex_info_panel_rect przez `from ... import`, wiec ma
        # wlasna referencje do starej funkcji. Bez tej podmiany over_ui() nadal
        # traktowal dawny panel lezacy nad mapa jak niewidzialny hitbox i
        # blokowal hover oraz klikniecia heksow po ich zaznaczeniu.
        app_module.hex_info_panel_rect = right_hex_info_rect

    _INSTALLED = True
