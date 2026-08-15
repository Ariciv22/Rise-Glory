from __future__ import annotations

import copy
import math

import pygame

from rg_content import create_enemy
from rg_core.data import GOLD, MUTED, TEXT
from rg_engine.heroes import defeat_hero
from rg_engine.problem_knowledge import investigate_problem, problem_investigated, problem_knowledge_view
from rg_engine.threats import (
    finish_problem_combat,
    marker_count,
    method_state,
    parse_marker_ref,
    problem_retry_blocked,
    resolve_problem_method,
    set_problem_combat_launcher,
)
from rg_engine.world import current_world_level
from rg_engine.world_problems import begin_problem_attempt
from rg_engine.world_events import DURATION_UNTIL_RESOLVED, active_world_events
from rg_ui.combat import draw_combat_screen, is_combat_active, start_combat
from rg_world.world_event_markers import (
    active_problem_event,
    bound_tiles,
    marker_event_ids_on_tile,
    problem_marker_preview,
    sync_problem_markers,
)

_INSTALL_DONE = False
_CURRENT_PLAYER = None
_METHOD_PAGE = 0
_PROBLEM_LIST_PAGE = 0
_METHOD_PAGE_SIZE = 4
_PROBLEM_PAGE_SIZE = 6
_METHOD_RECTS: list[tuple[pygame.Rect, int]] = []
_METHOD_PREV_RECT = None
_METHOD_NEXT_RECT = None
_PROBLEM_PREV_RECT = None
_PROBLEM_NEXT_RECT = None
_MAP_COMBAT_BUTTONS = []


def _fit(font, text, width):
    value = str(text or "")
    if font.size(value)[0] <= width:
        return value
    while value and font.size(value + "…")[0] > width:
        value = value[:-1]
    return value.rstrip() + "…"


def threat_hex_action_state(player, token, marker_ref: str) -> dict:
    event = active_problem_event(marker_ref)
    if event is None:
        return {"event": None, "investigated": False, "label": "Problem nieaktywny", "enabled": False, "reason": "Ten problem nie jest już aktywny."}
    investigated = problem_investigated(player, event)
    problem = event.get("problem") or {}
    label = str(problem.get("action_label") or "Rozwiąż problem") if investigated else "Zbadaj problem"
    actions = int(getattr(token, "actions", 0) or 0)
    blocked = investigated and problem_retry_blocked(player, event)
    no_actions = actions < 1
    enabled = not blocked and not no_actions
    reason = ""
    if no_actions:
        reason = "Potrzebujesz 1 akcji, aby podjąć próbę." if investigated else "Potrzebujesz 1 akcji, aby zbadać problem."
    elif blocked:
        reason = "Możesz ponowić próbę dopiero w następnej turze."
    return {"event": event, "investigated": investigated, "label": label, "enabled": enabled, "reason": reason}


def begin_threat_interaction(player, marker_ref: str) -> bool:
    global _METHOD_PAGE
    from rg_ui import world_state

    event = active_problem_event(marker_ref)
    if event is None:
        world_state._MESSAGE = "Ten problem nie jest już aktywny."
        return False
    if not problem_investigated(player, event):
        success, message = investigate_problem(player, event)
        world_state._MESSAGE = message
        return success
    session, message = begin_problem_attempt(player, marker_ref)
    world_state._MESSAGE = message
    if session is None:
        return False
    _METHOD_PAGE = 0
    world_state._PROBLEM_SESSION = session
    return True


def _draw_hex_actions(screen, small_font, players, tokens, active_player_index, right):
    global _CURRENT_PLAYER
    from rg_ui import world_state

    world_state._HEX_ACTION_RECTS = []
    if not players or active_player_index >= len(players) or active_player_index >= len(tokens):
        return
    token = tokens[active_player_index]
    player = players[active_player_index]
    _CURRENT_PLAYER = player
    refs = marker_event_ids_on_tile(token.tile)
    if not refs:
        return

    panel_h = 44 + len(refs) * 40
    panel = pygame.Rect(right.x + 12, max(right.y + 8, right.bottom - panel_h - 62), right.width - 24, panel_h)
    pygame.draw.rect(screen, (16, 21, 25), panel, border_radius=10)
    pygame.draw.rect(screen, GOLD, panel, 1, border_radius=10)
    screen.blit(small_font.render("Akcje na tym heksie", True, GOLD), (panel.x + 12, panel.y + 10))

    y = panel.y + 36
    mouse = pygame.mouse.get_pos()
    for marker_ref in refs:
        state = threat_hex_action_state(player, token, marker_ref)
        if state["event"] is None:
            continue
        _event_id, marker_id = parse_marker_ref(marker_ref)
        suffix = f" [{marker_id}/{marker_count(state['event'])}]" if marker_count(state["event"]) > 1 else ""
        rect = pygame.Rect(panel.x + 10, y, panel.width - 20, 34)
        pygame.draw.rect(screen, (63, 51, 35) if state["enabled"] else (43, 44, 45), rect, border_radius=7)
        pygame.draw.rect(screen, GOLD if state["enabled"] else (76, 76, 76), rect, 1, border_radius=7)
        label = _fit(small_font, state["label"] + suffix, rect.width - 18)
        screen.blit(small_font.render(label, True, TEXT if state["enabled"] else MUTED), (rect.x + 9, rect.y + 8))
        world_state._HEX_ACTION_RECTS.append((rect, marker_ref, state["enabled"], state["reason"]))
        if not state["enabled"] and state["reason"] and rect.collidepoint(mouse):
            tooltip = small_font.render(state["reason"], True, TEXT)
            tip = pygame.Rect(mouse[0] + 14, mouse[1] + 14, tooltip.get_width() + 16, tooltip.get_height() + 12)
            pygame.draw.rect(screen, (18, 20, 22), tip, border_radius=7)
            pygame.draw.rect(screen, GOLD, tip, 1, border_radius=7)
            screen.blit(tooltip, (tip.x + 8, tip.y + 6))
        y += 40


def _draw_problem_preview(screen, font, small_font):
    from rg_ui import world_state
    global _CURRENT_PLAYER

    marker_ref = world_state._PROBLEM_PREVIEW_ID
    if not marker_ref or world_state._PROBLEM_SESSION:
        return
    preview = problem_marker_preview(marker_ref)
    if preview is None:
        return
    world_state._draw_modal_shade(screen)
    sw, sh = screen.get_size()
    card = pygame.Rect(sw // 2 - 390, sh // 2 - 290, 780, 580)
    world_state._panel(screen, card, alpha=246)
    title = preview["name"]
    if preview.get("display_number"):
        title = f"#{preview['display_number']}  {title}"
    screen.blit(font.render(title, True, TEXT), (card.x + 28, card.y + 22))
    world_state._PREVIEW_CLOSE_RECT = pygame.Rect(card.right - 50, card.y + 16, 32, 32)
    pygame.draw.rect(screen, (53, 41, 35), world_state._PREVIEW_CLOSE_RECT, border_radius=8)
    close_label = font.render("×", True, TEXT)
    screen.blit(close_label, close_label.get_rect(center=world_state._PREVIEW_CLOSE_RECT.center))

    y = card.y + 68
    if preview["markers_total"] > 1:
        marker_text = f"Punkt {preview['marker_id']} | Pozostało: {preview['markers_remaining']}/{preview['markers_total']}"
        screen.blit(small_font.render(marker_text, True, GOLD), (card.x + 28, y))
        y += 28
    y = world_state._draw_wrapped(screen, small_font, preview["description"], pygame.Rect(card.x + 28, y, card.width - 56, 72), MUTED)
    y += 8
    screen.blit(small_font.render("Aktywny efekt:", True, GOLD), (card.x + 28, y))
    y += 22
    y = world_state._draw_wrapped(screen, small_font, preview["effect"], pygame.Rect(card.x + 28, y, card.width - 56, 60), TEXT)
    y += 8
    screen.blit(small_font.render(f"Warunek zakończenia: {preview['condition']}", True, TEXT), (card.x + 28, y))
    y += 30

    event = active_problem_event(marker_ref)
    view = problem_knowledge_view(_CURRENT_PLAYER, event) if _CURRENT_PLAYER is not None and event is not None else None
    if not view or not view["investigated"]:
        screen.blit(small_font.render("Status dla tego bohatera: NIEZBADANE", True, (218, 150, 105)), (card.x + 28, y))
        y += 28
        screen.blit(small_font.render("Sposoby rozwiązania są ukryte. Zbadaj problem na jego heksie za 1 Akcję.", True, MUTED), (card.x + 28, y))
    else:
        screen.blit(small_font.render("Status dla tego bohatera: ZBADANE", True, GOLD), (card.x + 28, y))
        y += 28
        methods = view.get("methods", [])
        for method in methods:
            state = method.get("availability") or method_state(_CURRENT_PLAYER, event, method)
            stat_text = "Automatyczna" if state["mode"] == "automatic" else ("Pełna Walka" if state["mode"] == "combat" else f"{state['stat']} DC {state['difficulty']}")
            line = f"• {method.get('label', 'Metoda')} — {stat_text} | Wymaga: {state['requirements_text']} | Zużywa: {state['costs_text']}"
            y = world_state._draw_wrapped(screen, small_font, line, pygame.Rect(card.x + 34, y, card.width - 68, 44), TEXT, max_lines=2)
            if state["failure_revealed"]:
                fail = method.get("failure_text") or "Poznana konsekwencja porażki."
                y = world_state._draw_wrapped(screen, small_font, f"  Poznana porażka: {fail}", pygame.Rect(card.x + 42, y, card.width - 84, 36), (218, 150, 105), max_lines=2)
            y += 5
            if y > card.bottom - 64:
                break
    screen.blit(small_font.render("Nagroda pozostaje ukryta do całkowitego rozwiązania Zagrożenia.", True, GOLD), (card.x + 28, card.bottom - 38))


def _draw_problem_attempt(screen, font, small_font):
    global _METHOD_RECTS, _METHOD_PREV_RECT, _METHOD_NEXT_RECT, _METHOD_PAGE
    from rg_ui import world_state

    session = world_state._PROBLEM_SESSION
    if session is None:
        return
    world_state._draw_modal_shade(screen)
    sw, sh = screen.get_size()
    card = pygame.Rect(sw // 2 - 430, sh // 2 - 310, 860, 620)
    world_state._panel(screen, card, alpha=248)
    screen.blit(font.render(str(session.event.get("name") or "Problem"), True, TEXT), (card.x + 28, card.y + 20))
    description = session.problem.get("description") or session.event.get("description") or ""
    y = card.y + 58
    y = world_state._draw_wrapped(screen, small_font, description, pygame.Rect(card.x + 28, y, card.width - 56, 64), MUTED, max_lines=3)
    y += 8

    world_state._PROBLEM_METHOD_RECTS = []
    world_state._PROBLEM_RESULT_CLOSE_RECT = None
    _METHOD_RECTS = []
    _METHOD_PREV_RECT = None
    _METHOD_NEXT_RECT = None

    if not session.resolved:
        screen.blit(small_font.render("Wybierz metodę. Dopiero kliknięcie metody pobiera 1 Akcję i jej koszty.", True, GOLD), (card.x + 28, y))
        y += 34
        total = len(session.methods)
        pages = max(1, math.ceil(total / _METHOD_PAGE_SIZE))
        _METHOD_PAGE = max(0, min(_METHOD_PAGE, pages - 1))
        start = _METHOD_PAGE * _METHOD_PAGE_SIZE
        visible = list(enumerate(session.methods))[start : start + _METHOD_PAGE_SIZE]
        for real_index, method in visible:
            state = method_state(session.player, session.event, method)
            rect = pygame.Rect(card.x + 30, y, card.width - 60, 94)
            bg = (28, 34, 38) if state["available"] else (39, 39, 39)
            border = GOLD if state["available"] else (82, 82, 82)
            pygame.draw.rect(screen, bg, rect, border_radius=10)
            pygame.draw.rect(screen, border, rect, 1, border_radius=10)
            label = str(method.get("label") or f"Sposób {real_index + 1}")
            screen.blit(small_font.render(label, True, TEXT if state["available"] else MUTED), (rect.x + 14, rect.y + 9))
            if state["mode"] == "automatic":
                test_line = "Bez rzutu — automatyczny sukces po spełnieniu warunków"
            elif state["mode"] == "combat":
                test_line = "Pełna Walka — 1 Akcja obejmuje całe starcie"
            else:
                difficulty = int(state["difficulty"] or 0) + int((session.player.get("threat_difficulty_penalties", {}) or {}).get(session.event_id, 0) or 0)
                test_line = f"Test: {state['stat']} | DC {difficulty}"
            screen.blit(small_font.render(_fit(small_font, test_line, rect.width - 28), True, GOLD if state["available"] else MUTED), (rect.x + 14, rect.y + 34))
            details = f"Wymaga: {state['requirements_text']}   |   Zużywa: {state['costs_text']}"
            screen.blit(small_font.render(_fit(small_font, details, rect.width - 28), True, MUTED), (rect.x + 14, rect.y + 57))
            if not state["available"]:
                missing = "Brakuje: " + ", ".join(state["missing"])
                screen.blit(small_font.render(_fit(small_font, missing, rect.width - 28), True, (218, 130, 110)), (rect.x + 14, rect.y + 76))
            elif state["failure_revealed"]:
                screen.blit(small_font.render(_fit(small_font, "Poznana porażka: " + str(method.get("failure_text") or "konsekwencja ujawniona"), rect.width - 28), True, (218, 150, 105)), (rect.x + 14, rect.y + 76))
            _METHOD_RECTS.append((rect, real_index))
            y += 104

        if pages > 1:
            nav_y = card.bottom - 70
            _METHOD_PREV_RECT = pygame.Rect(card.centerx - 170, nav_y, 110, 34)
            _METHOD_NEXT_RECT = pygame.Rect(card.centerx + 60, nav_y, 110, 34)
            for rect, label, enabled in ((_METHOD_PREV_RECT, "←", _METHOD_PAGE > 0), (_METHOD_NEXT_RECT, "→", _METHOD_PAGE < pages - 1)):
                pygame.draw.rect(screen, (55, 47, 37) if enabled else (38, 38, 38), rect, border_radius=7)
                pygame.draw.rect(screen, GOLD if enabled else (70, 70, 70), rect, 1, border_radius=7)
                rendered = small_font.render(label, True, TEXT if enabled else MUTED)
                screen.blit(rendered, rendered.get_rect(center=rect.center))
            page_label = small_font.render(f"{_METHOD_PAGE + 1}/{pages}", True, MUTED)
            screen.blit(page_label, page_label.get_rect(center=(card.centerx, nav_y + 17)))
        screen.blit(small_font.render("Nagroda: ???", True, MUTED), (card.x + 30, card.bottom - 30))
        return

    result_color = GOLD if session.success else (218, 115, 105)
    screen.blit(font.render("Sukces" if session.success else "Porażka", True, result_color), (card.x + 28, y + 2))
    y += 42
    if session.roll is not None:
        roll_line = f"Rzut k20: {session.roll} | Wynik: {session.total} | Trudność: {session.difficulty}"
        screen.blit(small_font.render(roll_line, True, TEXT), (card.x + 28, y))
        y += 30
    world_state._draw_wrapped(screen, small_font, session.result_text, pygame.Rect(card.x + 28, y, card.width - 56, 220), TEXT)
    world_state._PROBLEM_RESULT_CLOSE_RECT = pygame.Rect(card.centerx - 120, card.bottom - 62, 240, 40)
    pygame.draw.rect(screen, (65, 52, 35), world_state._PROBLEM_RESULT_CLOSE_RECT, border_radius=9)
    pygame.draw.rect(screen, GOLD, world_state._PROBLEM_RESULT_CLOSE_RECT, 2, border_radius=9)
    label = small_font.render("Wróć do swojej tury", True, TEXT)
    screen.blit(label, label.get_rect(center=world_state._PROBLEM_RESULT_CLOSE_RECT.center))


def _draw_problems_overlay(screen, font, small_font):
    global _PROBLEM_LIST_PAGE, _PROBLEM_PREV_RECT, _PROBLEM_NEXT_RECT
    from rg_ui import world_state

    world_state._draw_modal_shade(screen)
    card = world_state._world_state_layout(screen)
    world_state._panel(screen, card, alpha=246)
    from rg_engine.world import current_world_level
    screen.blit(font.render(f"Aktualny stan świata — Poziom {current_world_level()}", True, TEXT), (card.x + 26, card.y + 20))
    world_state._STATE_CLOSE_RECT = pygame.Rect(card.right - 52, card.y + 14, 34, 34)
    pygame.draw.rect(screen, (51, 40, 34), world_state._STATE_CLOSE_RECT, border_radius=8)
    close = font.render("×", True, TEXT)
    screen.blit(close, close.get_rect(center=world_state._STATE_CLOSE_RECT.center))

    tabs = (("active", "Aktywne wydarzenia"), ("problems", "Problemy"), ("history", "Historia"))
    world_state._TAB_RECTS = {}
    tab_y = card.y + 64
    tab_w = (card.width - 52) // 3
    for index, (key, label) in enumerate(tabs):
        rect = pygame.Rect(card.x + 26 + index * tab_w, tab_y, tab_w - 6, 38)
        world_state._TAB_RECTS[key] = rect
        active = key == "problems"
        pygame.draw.rect(screen, (68, 55, 37) if active else (31, 36, 40), rect, border_radius=8)
        pygame.draw.rect(screen, GOLD if active else (75, 75, 70), rect, 2 if active else 1, border_radius=8)
        rendered = small_font.render(label, True, TEXT if active else MUTED)
        screen.blit(rendered, rendered.get_rect(center=rect.center))

    content = pygame.Rect(card.x + 26, tab_y + 52, card.width - 52, card.height - 136)
    world_state._PROBLEM_ROW_RECTS = []
    events = active_world_events(DURATION_UNTIL_RESOLVED)
    if not events:
        screen.blit(small_font.render("Na mapie nie ma aktywnych Problemów.", True, MUTED), (content.x + 4, content.y + 8))
        return
    pages = max(1, math.ceil(len(events) / _PROBLEM_PAGE_SIZE))
    _PROBLEM_LIST_PAGE = max(0, min(_PROBLEM_LIST_PAGE, pages - 1))
    start = _PROBLEM_LIST_PAGE * _PROBLEM_PAGE_SIZE
    y = content.y
    for event in events[start : start + _PROBLEM_PAGE_SIZE]:
        row = pygame.Rect(content.x, y, content.width, 66)
        number = 0
        try:
            from rg_engine.threats import threat_display_number, unresolved_marker_ids
            number = threat_display_number(event)
            remaining = len(unresolved_marker_ids(event))
        except ImportError:
            remaining = 1
        secondary = f"#{number} | Pozostałe znaczniki: {remaining}/{marker_count(event)} | Kliknij, aby przejść na mapę"
        world_state._draw_event_row(screen, small_font, row, event, secondary)
        world_state._PROBLEM_ROW_RECTS.append((row, str(event.get("id"))))
        y += 74
    _PROBLEM_PREV_RECT = _PROBLEM_NEXT_RECT = None
    if pages > 1:
        nav_y = content.bottom - 36
        _PROBLEM_PREV_RECT = pygame.Rect(content.centerx - 150, nav_y, 90, 30)
        _PROBLEM_NEXT_RECT = pygame.Rect(content.centerx + 60, nav_y, 90, 30)
        for rect, label, enabled in ((_PROBLEM_PREV_RECT, "←", _PROBLEM_LIST_PAGE > 0), (_PROBLEM_NEXT_RECT, "→", _PROBLEM_LIST_PAGE < pages - 1)):
            pygame.draw.rect(screen, (55, 47, 37) if enabled else (38, 38, 38), rect, border_radius=7)
            pygame.draw.rect(screen, GOLD if enabled else (70, 70, 70), rect, 1, border_radius=7)
            rendered = small_font.render(label, True, TEXT if enabled else MUTED)
            screen.blit(rendered, rendered.get_rect(center=rect.center))
        label = small_font.render(f"{_PROBLEM_LIST_PAGE + 1}/{pages}", True, MUTED)
        screen.blit(label, label.get_rect(center=(content.centerx, nav_y + 15)))


def _launch_threat_combat(session, method_index: int, method: dict) -> tuple[bool, str]:
    from rg_ui import world_state

    if is_combat_active():
        return False, "Inna walka jest już aktywna."
    enemy = method.get("enemy")
    if isinstance(enemy, dict):
        enemy = copy.deepcopy(enemy)
    else:
        enemy_id = str(method.get("enemy_id") or enemy or "")
        if not enemy_id:
            return False, "Ta metoda Walki nie ma przypisanego przeciwnika."
        try:
            enemy = create_enemy(enemy_id, int(session.event.get("world_level", current_world_level()) or current_world_level()))
        except KeyError:
            return False, f"Nieznany przeciwnik: {enemy_id}."
    enemy["return_action"] = "world_problem"
    token = session.player.get("_token_ref")

    def show_result(success: bool, text: str):
        finish_problem_combat(session, success, text)
        sync_problem_markers()
        world_state._MESSAGE = session.result_text
        world_state._PROBLEM_SESSION = session

    def on_victory(combat_log):
        show_result(True, combat_log)

    def on_defeat(combat_log):
        defeat = defeat_hero(session.player, token, int(session.event.get("world_level", current_world_level()) or current_world_level()), lose_gold=True)
        show_result(False, f"{combat_log} {defeat['message']}")

    def on_escape(combat_log):
        show_result(False, f"{combat_log} Wycofanie z walki nie rozwiązuje Zagrożenia.")

    started, message = start_combat(
        session.player,
        enemy,
        on_victory=on_victory,
        on_defeat=on_defeat,
        on_escape=on_escape,
        intro_text=str(method.get("combat_intro") or f"Rozpoczyna się walka: {method.get('label', 'Zagrożenie')}"),
        metadata={"context_label": f"Zagrożenie: {session.event.get('name', 'Problem')}"},
    )
    if started:
        world_state._PROBLEM_SESSION = None
    return started, message


def _all_marker_rects():
    from rg_ui import world_state
    for tile in bound_tiles():
        for marker_ref in marker_event_ids_on_tile(tile):
            rect = world_state._marker_screen_rect(marker_ref)
            if rect is not None:
                yield marker_ref, rect


def install_threat_investigation_ui() -> None:
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return
    from rg_ui import world_state

    original_overlay = world_state._draw_world_state_overlay
    original_clicked = world_state._WorldStateController.clicked

    from rg_ui import hud as rg_hud
    from rg_engine import turns as rg_turns
    original_scoreboard = rg_hud._draw_scoreboard
    original_bottom_info = rg_hud._draw_bottom_tile_info
    original_player_board_clicked = rg_hud._PlayerBoardButton.clicked
    original_end_turn = rg_turns.TurnManager.end_turn

    class _MapCombatController:
        action = "world_problem"

        def clicked(self, pos):
            if not is_combat_active():
                return False
            for button in list(_MAP_COMBAT_BUTTONS):
                if button.clicked(pos):
                    return True
            return True

    def scoreboard_with_map_combat(screen, font, small_font, players, tokens, active_player_index, right):
        controller = original_scoreboard(screen, font, small_font, players, tokens, active_player_index, right)
        if is_combat_active():
            return _MapCombatController()
        return controller

    def bottom_info_with_map_combat(screen, font, small_font, selected_tile, rect):
        global _MAP_COMBAT_BUTTONS
        result = original_bottom_info(screen, font, small_font, selected_tile, rect)
        if is_combat_active():
            title_font = pygame.font.SysFont("arial", 42, bold=True)
            _MAP_COMBAT_BUTTONS = draw_combat_screen(screen, title_font, font, small_font, pygame.mouse.get_pos())
        else:
            _MAP_COMBAT_BUTTONS = []
        return result

    def player_board_clicked_without_combat(self, pos):
        if is_combat_active():
            return False
        return original_player_board_clicked(self, pos)

    def end_turn_without_combat(self, tokens):
        if is_combat_active():
            return {"active_player_index": self.active_player_index, "round_completed": False, "council_due": False}
        return original_end_turn(self, tokens)

    def overlay_with_unlimited_problems(screen, font, small_font):
        if world_state._STATE_OPEN and not world_state._PROBLEM_PREVIEW_ID and not world_state._PROBLEM_SESSION and world_state._STATE_TAB == "problems":
            _draw_problems_overlay(screen, font, small_font)
            return
        return original_overlay(screen, font, small_font)

    def clicked_with_threat_pages(self, pos):
        global _METHOD_PAGE, _PROBLEM_LIST_PAGE
        session = world_state._PROBLEM_SESSION
        if session is not None and not session.resolved:
            if _METHOD_PREV_RECT and _METHOD_PREV_RECT.collidepoint(pos) and _METHOD_PAGE > 0:
                _METHOD_PAGE -= 1
                self.action = "world_problem"
                return True
            pages = max(1, math.ceil(len(session.methods) / _METHOD_PAGE_SIZE))
            if _METHOD_NEXT_RECT and _METHOD_NEXT_RECT.collidepoint(pos) and _METHOD_PAGE < pages - 1:
                _METHOD_PAGE += 1
                self.action = "world_problem"
                return True
            for rect, method_index in _METHOD_RECTS:
                if not rect.collidepoint(pos):
                    continue
                resolve_problem_method(session, method_index)
                sync_problem_markers()
                self.action = "world_problem"
                return True
            self.action = "world_problem"
            return True

        if world_state._STATE_OPEN and world_state._STATE_TAB == "problems" and not world_state._PROBLEM_PREVIEW_ID:
            events = active_world_events(DURATION_UNTIL_RESOLVED)
            pages = max(1, math.ceil(len(events) / _PROBLEM_PAGE_SIZE))
            if _PROBLEM_PREV_RECT and _PROBLEM_PREV_RECT.collidepoint(pos) and _PROBLEM_LIST_PAGE > 0:
                _PROBLEM_LIST_PAGE -= 1
                self.action = "world_state"
                return True
            if _PROBLEM_NEXT_RECT and _PROBLEM_NEXT_RECT.collidepoint(pos) and _PROBLEM_LIST_PAGE < pages - 1:
                _PROBLEM_LIST_PAGE += 1
                self.action = "world_state"
                return True

        if not world_state._STATE_OPEN and not world_state._PROBLEM_PREVIEW_ID and world_state._PROBLEM_SESSION is None:
            for marker_ref, rect in _all_marker_rects():
                if rect.collidepoint(pos):
                    world_state._open_problem_preview(marker_ref)
                    self.action = "world_state"
                    return True
        return original_clicked(self, pos)

    world_state._begin_problem_from_hex = begin_threat_interaction
    world_state._draw_hex_actions = _draw_hex_actions
    world_state._draw_problem_preview = _draw_problem_preview
    world_state._draw_problem_attempt = _draw_problem_attempt
    world_state._draw_world_state_overlay = overlay_with_unlimited_problems
    world_state._WorldStateController.clicked = clicked_with_threat_pages
    rg_hud._draw_scoreboard = scoreboard_with_map_combat
    rg_hud._draw_bottom_tile_info = bottom_info_with_map_combat
    rg_hud._PlayerBoardButton.clicked = player_board_clicked_without_combat
    rg_turns.TurnManager.end_turn = end_turn_without_combat
    set_problem_combat_launcher(_launch_threat_combat)
    _INSTALL_DONE = True
