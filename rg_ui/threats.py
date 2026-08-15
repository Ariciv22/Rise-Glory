from __future__ import annotations

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_engine.problem_knowledge import investigate_problem, problem_investigated
from rg_engine.world_problems import begin_problem_attempt, problem_retry_blocked
from rg_world.world_event_markers import active_problem_event, marker_event_ids_on_tile

_INSTALL_DONE = False


def threat_hex_action_state(player, token, event_id: str) -> dict:
    """Zwraca stan przycisku Zagrożenia dla aktywnego bohatera na jego heksie."""
    event = active_problem_event(event_id)
    if event is None:
        return {
            "event": None,
            "investigated": False,
            "label": "Problem nieaktywny",
            "enabled": False,
            "reason": "Ten problem nie jest już aktywny.",
        }

    investigated = problem_investigated(player, event)
    problem = event.get("problem") or {}
    if investigated:
        label = str(problem.get("action_label") or "Rozwiąż problem")
    else:
        label = "Zbadaj problem"

    actions = int(getattr(token, "actions", 0) or 0)
    blocked = investigated and problem_retry_blocked(player, event_id)
    no_actions = actions < 1
    enabled = not blocked and not no_actions

    reason = ""
    if no_actions:
        if investigated:
            reason = "Potrzebujesz 1 akcji, aby podjąć próbę."
        else:
            reason = "Potrzebujesz 1 akcji, aby zbadać problem."
    elif blocked:
        reason = "Możesz ponowić próbę dopiero w następnej turze."

    return {
        "event": event,
        "investigated": investigated,
        "label": label,
        "enabled": enabled,
        "reason": reason,
    }


def begin_threat_interaction(player, event_id: str) -> bool:
    """Pierwsze kliknięcie bada problem, kolejne rozpoczyna właściwą próbę."""
    from rg_ui import world_state

    event = active_problem_event(event_id)
    if event is None:
        world_state._MESSAGE = "Ten problem nie jest już aktywny."
        return False

    if not problem_investigated(player, event):
        success, message = investigate_problem(player, event)
        world_state._MESSAGE = message
        return success

    session, message = begin_problem_attempt(player, event)
    world_state._MESSAGE = message
    if session is None:
        return False
    world_state._PROBLEM_SESSION = session
    return True


def _draw_hex_actions(screen, small_font, players, tokens, active_player_index, right):
    from rg_ui import world_state

    world_state._HEX_ACTION_RECTS = []
    if not players or active_player_index >= len(players) or active_player_index >= len(tokens):
        return

    token = tokens[active_player_index]
    player = players[active_player_index]
    event_ids = marker_event_ids_on_tile(token.tile)
    if not event_ids:
        return

    panel_h = 44 + min(3, len(event_ids)) * 44
    panel = pygame.Rect(right.x + 12, right.bottom - panel_h - 62, right.width - 24, panel_h)
    pygame.draw.rect(screen, (16, 21, 25), panel, border_radius=10)
    pygame.draw.rect(screen, GOLD, panel, 1, border_radius=10)
    screen.blit(small_font.render("Akcje na tym heksie", True, GOLD), (panel.x + 12, panel.y + 10))

    y = panel.y + 36
    mouse = pygame.mouse.get_pos()
    for event_id in event_ids[:3]:
        state = threat_hex_action_state(player, token, event_id)
        if state["event"] is None:
            continue

        rect = pygame.Rect(panel.x + 10, y, panel.width - 20, 34)
        pygame.draw.rect(screen, (63, 51, 35) if state["enabled"] else (43, 44, 45), rect, border_radius=7)
        pygame.draw.rect(screen, GOLD if state["enabled"] else (76, 76, 76), rect, 1, border_radius=7)

        label = world_state._fit(small_font, state["label"], rect.width - 18)
        rendered = small_font.render(label, True, TEXT if state["enabled"] else MUTED)
        screen.blit(rendered, (rect.x + 9, rect.y + 8))
        world_state._HEX_ACTION_RECTS.append((rect, event_id, state["enabled"], state["reason"]))

        if not state["enabled"] and state["reason"] and rect.collidepoint(mouse):
            tooltip = small_font.render(state["reason"], True, TEXT)
            tip = pygame.Rect(mouse[0] + 14, mouse[1] + 14, tooltip.get_width() + 16, tooltip.get_height() + 12)
            pygame.draw.rect(screen, (18, 20, 22), tip, border_radius=7)
            pygame.draw.rect(screen, GOLD, tip, 1, border_radius=7)
            screen.blit(tooltip, (tip.x + 8, tip.y + 6))
        y += 40


def install_threat_investigation_ui() -> None:
    """Podmienia tylko interakcję Zagrożeń, pozostawiając resztę panelu świata bez zmian."""
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return

    from rg_ui import world_state

    world_state._begin_problem_from_hex = begin_threat_interaction
    world_state._draw_hex_actions = _draw_hex_actions
    _INSTALL_DONE = True
