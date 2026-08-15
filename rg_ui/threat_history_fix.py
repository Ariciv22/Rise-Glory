from __future__ import annotations

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_engine.threats import reward_text
from rg_engine.world_events import world_event_history
from rg_world.world_event_markers import active_problem_event

_INSTALL_DONE = False


def _append_deferred_reward(session):
    deferred = str((session.problem or {}).get("deferred_reward") or "").strip()
    if not deferred or not session.resolved or not session.success:
        return
    if active_problem_event(session.event_id) is not None:
        return
    line = f"Nagroda zależna od przyszłego modułu: {deferred}"
    if line not in session.result_text:
        session.result_text = f"{session.result_text} {line}".strip()


def _resolution_lines(event):
    resolution = event.get("resolution") or {}
    if not isinstance(resolution, dict) or not resolution:
        return []
    lines = []
    hero = str(resolution.get("hero") or "")
    method = str(resolution.get("method") or "")
    if hero:
        lines.append(f"Bohater: {hero}")
    if method:
        lines.append(f"Metoda: {method}")
    for row in resolution.get("reward", []) or []:
        if not isinstance(row, dict):
            continue
        name = str(row.get("player") or "Bohater")
        result = row.get("reward") or {}
        text = reward_text(result) if isinstance(result, dict) else str(result)
        if text != "brak dodatkowej nagrody":
            lines.append(f"Nagroda — {name}: {text}")
    deferred = str((event.get("problem") or {}).get("deferred_reward") or "").strip()
    if deferred:
        lines.append(f"Nagroda integracyjna: {deferred}")
    return lines


def install_threat_history_fix() -> None:
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return
    from rg_ui import threats as threat_ui
    from rg_ui import world_state

    original_resolve = threat_ui.resolve_problem_method
    original_finish = threat_ui.finish_problem_combat
    original_overlay = world_state._draw_world_state_overlay

    def resolve_with_deferred(session, method_index, rng=None):
        success, message = original_resolve(session, method_index, rng)
        _append_deferred_reward(session)
        return success, session.result_text or message

    def finish_with_deferred(session, victory, message=""):
        success, result = original_finish(session, victory, message)
        _append_deferred_reward(session)
        return success, session.result_text or result

    def overlay_with_resolution_details(screen, font, small_font):
        result = original_overlay(screen, font, small_font)
        if not world_state._STATE_OPEN or world_state._STATE_TAB != "history":
            return result
        index = world_state._HISTORY_CARD_INDEX
        history = world_event_history()
        if index is None or index < 0 or index >= len(history):
            return result
        event = history[index]
        lines = _resolution_lines(event)
        if not lines:
            return result
        card = world_state._world_state_layout(screen)
        content_y = card.y + 64 + 52
        panel = pygame.Rect(card.x + 34, content_y + 245, card.width - 68, min(150, 34 + len(lines) * 25))
        pygame.draw.rect(screen, (20, 25, 29), panel, border_radius=9)
        pygame.draw.rect(screen, GOLD, panel, 1, border_radius=9)
        screen.blit(small_font.render("Rozwiązanie Zagrożenia", True, GOLD), (panel.x + 12, panel.y + 9))
        y = panel.y + 34
        for line in lines[:4]:
            rendered = small_font.render(world_state._fit(small_font, line, panel.width - 24), True, TEXT if not line.startswith("Nagroda integracyjna") else MUTED)
            screen.blit(rendered, (panel.x + 12, y))
            y += 24
        return result

    threat_ui.resolve_problem_method = resolve_with_deferred
    threat_ui.finish_problem_combat = finish_with_deferred
    world_state._draw_world_state_overlay = overlay_with_resolution_details
    _INSTALL_DONE = True
