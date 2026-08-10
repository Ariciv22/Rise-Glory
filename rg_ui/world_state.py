from __future__ import annotations

from typing import Any

import pygame

from rg_core.data import GOLD, MUTED, PANEL_DARK, TEXT
from rg_engine.world import consume_world_level_changes, current_world_level
from rg_engine.world_events import (
    DURATION_UNTIL_NEXT_COUNCIL,
    DURATION_UNTIL_RESOLVED,
    active_world_events,
    world_event_history,
)
from rg_engine.world_problems import (
    available_problem_methods,
    begin_problem_attempt,
    clear_problem_retry_blocks,
    problem_retry_blocked,
    resolve_problem_method,
)
from rg_ui.common import wrap
from rg_world.world_event_markers import (
    active_camera,
    active_problem_event,
    marker_event_ids_on_tile,
    marker_tile,
    problem_marker_preview,
    sync_problem_markers,
)

_INSTALL_DONE = False
_STATE_OPEN = False
_STATE_TAB = "active"
_PROBLEM_PREVIEW_ID: str | None = None
_HISTORY_CARD_INDEX: int | None = None
_PROBLEM_SESSION = None
_MESSAGE = ""

_STATE_BUTTON_RECT = None
_STATE_CLOSE_RECT = None
_TAB_RECTS: dict[str, pygame.Rect] = {}
_PROBLEM_ROW_RECTS: list[tuple[pygame.Rect, str]] = []
_HISTORY_ROW_RECTS: list[tuple[pygame.Rect, int]] = []
_PREVIEW_CLOSE_RECT = None
_PROBLEM_METHOD_RECTS: list[pygame.Rect] = []
_PROBLEM_RESULT_CLOSE_RECT = None
_HEX_ACTION_RECTS: list[tuple[pygame.Rect, str, bool, str]] = []
_WORLD_LEVEL_BANNER = None


def is_world_state_open() -> bool:
    return bool(_STATE_OPEN or _PROBLEM_PREVIEW_ID or _PROBLEM_SESSION)


def open_world_state(tab: str = "active") -> None:
    global _STATE_OPEN, _STATE_TAB, _PROBLEM_PREVIEW_ID, _HISTORY_CARD_INDEX
    _STATE_OPEN = True
    _STATE_TAB = tab if tab in {"active", "problems", "history"} else "active"
    _PROBLEM_PREVIEW_ID = None
    _HISTORY_CARD_INDEX = None


def close_world_state() -> None:
    global _STATE_OPEN, _PROBLEM_PREVIEW_ID, _HISTORY_CARD_INDEX
    _STATE_OPEN = False
    _PROBLEM_PREVIEW_ID = None
    _HISTORY_CARD_INDEX = None


def _panel(screen, rect, alpha=235, border=GOLD):
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, (12, 16, 20, alpha), surface.get_rect(), border_radius=14)
    pygame.draw.rect(surface, border, surface.get_rect(), 2, border_radius=14)
    screen.blit(surface, rect.topleft)


def _draw_wrapped(screen, font, text, rect, color=TEXT, line_height=None, max_lines=None):
    line_height = line_height or font.get_height() + 4
    y = rect.y
    lines = wrap(font, str(text or ""), rect.width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        if y + line_height > rect.bottom:
            break
        screen.blit(font.render(line, True, color), (rect.x, y))
        y += line_height
    return y


def _fit(font, text, width):
    value = str(text or "")
    if font.size(value)[0] <= width:
        return value
    while value and font.size(value + "…")[0] > width:
        value = value[:-1]
    return value.rstrip() + "…"


def _world_state_layout(screen):
    sw, sh = screen.get_size()
    width = min(820, sw - 120)
    height = min(660, sh - 120)
    return pygame.Rect((sw - width) // 2, (sh - height) // 2, width, height)


def _draw_modal_shade(screen):
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 178))
    screen.blit(shade, (0, 0))


def _duration_text(event):
    duration = event.get("duration")
    if duration == DURATION_UNTIL_NEXT_COUNCIL:
        return "Do następnej Rady"
    if duration == DURATION_UNTIL_RESOLVED:
        return "Do wyeliminowania problemu"
    return "Natychmiast"


def _draw_event_row(screen, small_font, rect, event, secondary=""):
    pygame.draw.rect(screen, (24, 29, 34), rect, border_radius=9)
    pygame.draw.rect(screen, (82, 71, 51), rect, 1, border_radius=9)
    name = _fit(small_font, event.get("name", "Wydarzenie Świata"), rect.width - 26)
    screen.blit(small_font.render(name, True, TEXT), (rect.x + 12, rect.y + 8))
    effect = event.get("effect_text") or event.get("description") or secondary
    effect = _fit(small_font, effect, rect.width - 26)
    screen.blit(small_font.render(effect, True, MUTED), (rect.x + 12, rect.y + 30))
    if secondary:
        label = _fit(small_font, secondary, rect.width - 26)
        screen.blit(small_font.render(label, True, GOLD), (rect.x + 12, rect.y + 50))


def _draw_world_state_overlay(screen, font, small_font):
    global _STATE_CLOSE_RECT, _TAB_RECTS, _PROBLEM_ROW_RECTS, _HISTORY_ROW_RECTS
    if not _STATE_OPEN or _PROBLEM_PREVIEW_ID or _PROBLEM_SESSION:
        return

    _draw_modal_shade(screen)
    card = _world_state_layout(screen)
    _panel(screen, card, alpha=246)
    screen.blit(font.render(f"Aktualny stan świata — Poziom {current_world_level()}", True, TEXT), (card.x + 26, card.y + 20))

    _STATE_CLOSE_RECT = pygame.Rect(card.right - 52, card.y + 14, 34, 34)
    pygame.draw.rect(screen, (51, 40, 34), _STATE_CLOSE_RECT, border_radius=8)
    screen.blit(font.render("×", True, TEXT), font.render("×", True, TEXT).get_rect(center=_STATE_CLOSE_RECT.center))

    tabs = (("active", "Aktywne wydarzenia"), ("problems", "Problemy"), ("history", "Historia"))
    _TAB_RECTS = {}
    tab_y = card.y + 64
    tab_w = (card.width - 52) // 3
    for index, (key, label) in enumerate(tabs):
        rect = pygame.Rect(card.x + 26 + index * tab_w, tab_y, tab_w - 6, 38)
        _TAB_RECTS[key] = rect
        active = _STATE_TAB == key
        pygame.draw.rect(screen, (68, 55, 37) if active else (31, 36, 40), rect, border_radius=8)
        pygame.draw.rect(screen, GOLD if active else (75, 75, 70), rect, 2 if active else 1, border_radius=8)
        rendered = small_font.render(label, True, TEXT if active else MUTED)
        screen.blit(rendered, rendered.get_rect(center=rect.center))

    content = pygame.Rect(card.x + 26, tab_y + 52, card.width - 52, card.height - 136)
    _PROBLEM_ROW_RECTS = []
    _HISTORY_ROW_RECTS = []

    if _STATE_TAB == "active":
        events = [event for event in active_world_events() if event.get("duration") != DURATION_UNTIL_RESOLVED]
        if not events:
            screen.blit(small_font.render("Brak aktywnych efektów czasowych.", True, MUTED), (content.x + 4, content.y + 8))
            return
        y = content.y
        for event in events[:6]:
            row = pygame.Rect(content.x, y, content.width, 76)
            _draw_event_row(screen, small_font, row, event, _duration_text(event))
            y += 84
        return

    if _STATE_TAB == "problems":
        events = active_world_events(DURATION_UNTIL_RESOLVED)
        if not events:
            screen.blit(small_font.render("Na mapie nie ma aktywnych Problemów.", True, MUTED), (content.x + 4, content.y + 8))
            return
        y = content.y
        for event in events[:6]:
            row = pygame.Rect(content.x, y, content.width, 78)
            _draw_event_row(screen, small_font, row, event, "Kliknij, aby przejść do znacznika na mapie")
            _PROBLEM_ROW_RECTS.append((row, str(event.get("id"))))
            y += 86
        return

    history = world_event_history()
    if _HISTORY_CARD_INDEX is not None and 0 <= _HISTORY_CARD_INDEX < len(history):
        event = history[_HISTORY_CARD_INDEX]
        screen.blit(font.render(str(event.get("name") or "Wydarzenie Świata"), True, TEXT), (content.x + 8, content.y + 4))
        y = content.y + 44
        y = _draw_wrapped(screen, small_font, event.get("description", ""), pygame.Rect(content.x + 8, y, content.width - 16, 100), MUTED)
        y += 10
        screen.blit(small_font.render("Efekt", True, GOLD), (content.x + 8, y))
        y += 24
        y = _draw_wrapped(screen, small_font, event.get("effect_text", ""), pygame.Rect(content.x + 8, y, content.width - 16, 110), TEXT)
        y += 12
        ending = event.get("ending") or event.get("history_status") or ""
        screen.blit(small_font.render(f"Zakończenie: {ending}", True, GOLD), (content.x + 8, y))
        back = pygame.Rect(content.x + 8, content.bottom - 42, 180, 34)
        pygame.draw.rect(screen, (55, 47, 37), back, border_radius=8)
        pygame.draw.rect(screen, GOLD, back, 1, border_radius=8)
        screen.blit(small_font.render("← Historia", True, TEXT), (back.x + 18, back.y + 8))
        _HISTORY_ROW_RECTS.append((back, -1))
        return

    if not history:
        screen.blit(small_font.render("Historia Wydarzeń Świata jest jeszcze pusta.", True, MUTED), (content.x + 4, content.y + 8))
        return
    y = content.y
    for index, event in enumerate(reversed(history[-7:])):
        real_index = len(history) - 1 - index
        row = pygame.Rect(content.x, y, content.width, 62)
        ending = str(event.get("ending") or event.get("history_status") or "")
        _draw_event_row(screen, small_font, row, event, ending)
        _HISTORY_ROW_RECTS.append((row, real_index))
        y += 70


def _draw_problem_preview(screen, font, small_font):
    global _PREVIEW_CLOSE_RECT
    if not _PROBLEM_PREVIEW_ID or _PROBLEM_SESSION:
        return
    preview = problem_marker_preview(_PROBLEM_PREVIEW_ID)
    if preview is None:
        return

    _draw_modal_shade(screen)
    sw, sh = screen.get_size()
    card = pygame.Rect(sw // 2 - 330, sh // 2 - 205, 660, 410)
    _panel(screen, card, alpha=246)
    screen.blit(font.render(preview["name"], True, TEXT), (card.x + 28, card.y + 22))
    _PREVIEW_CLOSE_RECT = pygame.Rect(card.right - 50, card.y + 16, 32, 32)
    pygame.draw.rect(screen, (53, 41, 35), _PREVIEW_CLOSE_RECT, border_radius=8)
    close_label = font.render("×", True, TEXT)
    screen.blit(close_label, close_label.get_rect(center=_PREVIEW_CLOSE_RECT.center))

    y = card.y + 70
    y = _draw_wrapped(screen, small_font, preview["description"], pygame.Rect(card.x + 28, y, card.width - 56, 82), MUTED)
    y += 10
    screen.blit(small_font.render("Aktualny efekt:", True, GOLD), (card.x + 28, y))
    y += 24
    y = _draw_wrapped(screen, small_font, preview["effect"], pygame.Rect(card.x + 28, y, card.width - 56, 65), TEXT)
    y += 10
    screen.blit(small_font.render(f"Warunek zakończenia: {preview['condition']}", True, TEXT), (card.x + 28, y))
    y += 30
    screen.blit(small_font.render(preview["reward_hint"], True, GOLD), (card.x + 28, y))
    screen.blit(small_font.render("X wraca bezpośrednio do zakładki Problemy.", True, MUTED), (card.x + 28, card.bottom - 42))


def _problem_difficulty_for_display(session, method):
    event_id = session.event_id
    penalty = int((session.player.get("_problem_difficulty_penalties", {}) or {}).get(event_id, 0) or 0)
    return int(method.get("difficulty", 0) or 0) + penalty


def _draw_problem_attempt(screen, font, small_font):
    global _PROBLEM_METHOD_RECTS, _PROBLEM_RESULT_CLOSE_RECT
    session = _PROBLEM_SESSION
    if session is None:
        return

    _draw_modal_shade(screen)
    sw, sh = screen.get_size()
    card = pygame.Rect(sw // 2 - 380, sh // 2 - 260, 760, 520)
    _panel(screen, card, alpha=248)
    screen.blit(font.render(str(session.event.get("name") or "Problem"), True, TEXT), (card.x + 28, card.y + 22))

    problem = session.problem
    description = problem.get("description") or session.event.get("description") or ""
    y = card.y + 62
    y = _draw_wrapped(screen, small_font, description, pygame.Rect(card.x + 28, y, card.width - 56, 70), MUTED)
    y += 8

    _PROBLEM_METHOD_RECTS = []
    _PROBLEM_RESULT_CLOSE_RECT = None

    if not session.resolved:
        screen.blit(small_font.render("Wybierz sposób rozwiązania. Akcja została już zużyta — nie możesz wyjść bez testu.", True, GOLD), (card.x + 28, y))
        y += 36
        for index, method in enumerate(session.methods[:3]):
            rect = pygame.Rect(card.x + 30, y, card.width - 60, 78)
            pygame.draw.rect(screen, (28, 34, 38), rect, border_radius=10)
            pygame.draw.rect(screen, GOLD, rect, 1, border_radius=10)
            label = str(method.get("label") or f"Sposób {index + 1}")
            stat = str(method.get("stat") or "-")
            difficulty = _problem_difficulty_for_display(session, method)
            screen.blit(small_font.render(label, True, TEXT), (rect.x + 16, rect.y + 12))
            screen.blit(small_font.render(f"Test: {stat}   |   Trudność: {difficulty}", True, GOLD), (rect.x + 16, rect.y + 39))
            _PROBLEM_METHOD_RECTS.append(rect)
            y += 88
        reward_hint = str(problem.get("reward_hint") or "Nagroda: ???")
        screen.blit(small_font.render(reward_hint, True, MUTED), (card.x + 30, card.bottom - 36))
        return

    result_color = GOLD if session.success else (218, 115, 105)
    result_title = "Sukces" if session.success else "Porażka"
    screen.blit(font.render(result_title, True, result_color), (card.x + 28, y + 4))
    y += 44
    roll_line = f"Rzut k20: {session.roll}   |   Wynik: {session.total}   |   Trudność: {session.difficulty}"
    screen.blit(small_font.render(roll_line, True, TEXT), (card.x + 28, y))
    y += 34
    _draw_wrapped(screen, small_font, session.result_text, pygame.Rect(card.x + 28, y, card.width - 56, 160), TEXT)

    _PROBLEM_RESULT_CLOSE_RECT = pygame.Rect(card.centerx - 120, card.bottom - 62, 240, 40)
    pygame.draw.rect(screen, (65, 52, 35), _PROBLEM_RESULT_CLOSE_RECT, border_radius=9)
    pygame.draw.rect(screen, GOLD, _PROBLEM_RESULT_CLOSE_RECT, 2, border_radius=9)
    label = small_font.render("Wróć do swojej tury", True, TEXT)
    screen.blit(label, label.get_rect(center=_PROBLEM_RESULT_CLOSE_RECT.center))


def _draw_world_level_banner(screen, font):
    global _WORLD_LEVEL_BANNER
    changes = consume_world_level_changes()
    if changes:
        _WORLD_LEVEL_BANNER = (changes[-1][1], pygame.time.get_ticks() + 3200)
    if not _WORLD_LEVEL_BANNER:
        return
    level, expires_at = _WORLD_LEVEL_BANNER
    if pygame.time.get_ticks() >= expires_at:
        _WORLD_LEVEL_BANNER = None
        return
    rect = pygame.Rect(screen.get_width() // 2 - 250, 126, 500, 70)
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, (15, 17, 21, 232), surface.get_rect(), border_radius=12)
    pygame.draw.rect(surface, GOLD, surface.get_rect(), 3, border_radius=12)
    screen.blit(surface, rect.topleft)
    label = font.render(f"Poziom Świata wzrósł do {level}", True, TEXT)
    screen.blit(label, label.get_rect(center=rect.center))


def _marker_screen_rect(event_id: str):
    tile = marker_tile(event_id)
    camera = active_camera()
    if tile is None or camera is None:
        return None
    ids = marker_event_ids_on_tile(tile)
    try:
        index = ids.index(str(event_id))
    except ValueError:
        index = 0
    sx, sy = tile.center(camera)
    diameter = max(28, int(50 * camera.zoom))
    center = (
        int(sx + (-40 + index * 28) * camera.zoom),
        int(sy - 35 * camera.zoom),
    )
    return pygame.Rect(0, 0, diameter + 10, diameter + 10).copy().move(center[0] - (diameter + 10) // 2, center[1] - (diameter + 10) // 2)


def _open_problem_preview(event_id: str):
    global _STATE_OPEN, _STATE_TAB, _PROBLEM_PREVIEW_ID, _HISTORY_CARD_INDEX
    _STATE_OPEN = True
    _STATE_TAB = "problems"
    _HISTORY_CARD_INDEX = None
    _PROBLEM_PREVIEW_ID = str(event_id)
    tile = marker_tile(event_id)
    camera = active_camera()
    if tile is not None and camera is not None:
        camera.center_on_tile(tile)


def _begin_problem_from_hex(player, event_id: str):
    global _PROBLEM_SESSION, _MESSAGE
    event = active_problem_event(event_id)
    if event is None:
        _MESSAGE = "Ten problem nie jest już aktywny."
        return False
    session, message = begin_problem_attempt(player, event)
    _MESSAGE = message
    if session is None:
        return False
    _PROBLEM_SESSION = session
    return True


def _draw_hex_actions(screen, small_font, players, tokens, active_player_index, right):
    global _HEX_ACTION_RECTS
    _HEX_ACTION_RECTS = []
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
        event = active_problem_event(event_id)
        if event is None:
            continue
        problem = event.get("problem") or {}
        label = str(problem.get("action_label") or "Rozwiąż problem")
        blocked = problem_retry_blocked(player, event_id)
        no_actions = int(getattr(token, "actions", 0) or 0) < 1
        enabled = not blocked and not no_actions
        reason = ""
        if no_actions:
            reason = "Potrzebujesz 1 akcji, aby podjąć próbę."
        elif blocked:
            reason = "Możesz ponowić próbę dopiero w następnej turze."
        rect = pygame.Rect(panel.x + 10, y, panel.width - 20, 34)
        pygame.draw.rect(screen, (63, 51, 35) if enabled else (43, 44, 45), rect, border_radius=7)
        pygame.draw.rect(screen, GOLD if enabled else (76, 76, 76), rect, 1, border_radius=7)
        rendered = small_font.render(_fit(small_font, label, rect.width - 18), True, TEXT if enabled else MUTED)
        screen.blit(rendered, (rect.x + 9, rect.y + 8))
        _HEX_ACTION_RECTS.append((rect, event_id, enabled, reason))
        if not enabled and reason and rect.collidepoint(mouse):
            tooltip = small_font.render(reason, True, TEXT)
            tip = pygame.Rect(mouse[0] + 14, mouse[1] + 14, tooltip.get_width() + 16, tooltip.get_height() + 12)
            pygame.draw.rect(screen, (18, 20, 22), tip, border_radius=7)
            pygame.draw.rect(screen, GOLD, tip, 1, border_radius=7)
            screen.blit(tooltip, (tip.x + 8, tip.y + 6))
        y += 40


def _draw_state_button(screen, small_font, rect):
    global _STATE_BUTTON_RECT
    active_count = len(active_world_events())
    width = min(230, max(190, rect.width // 4))
    _STATE_BUTTON_RECT = pygame.Rect(rect.right - width - 16, rect.y + max(4, (rect.height - 34) // 2), width, 34)
    hovered = _STATE_BUTTON_RECT.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, (70, 56, 37) if hovered else (48, 43, 34), _STATE_BUTTON_RECT, border_radius=8)
    pygame.draw.rect(screen, GOLD, _STATE_BUTTON_RECT, 1, border_radius=8)
    label = small_font.render(f"Wydarzenia Świata: {active_count}", True, TEXT)
    screen.blit(label, label.get_rect(center=_STATE_BUTTON_RECT.center))


class _WorldStateController:
    def __init__(self, delegate, players, tokens, active_player_index):
        self.delegate = delegate
        self.players = players
        self.tokens = tokens
        self.active_player_index = active_player_index
        self.action = getattr(delegate, "action", "end_turn")

    def _active_player(self):
        if not self.players or self.active_player_index >= len(self.players):
            return None
        return self.players[self.active_player_index]

    def clicked(self, pos):
        global _STATE_OPEN, _STATE_TAB, _PROBLEM_PREVIEW_ID, _HISTORY_CARD_INDEX
        global _PROBLEM_SESSION, _MESSAGE

        if _PROBLEM_SESSION is not None:
            if not _PROBLEM_SESSION.resolved:
                for index, rect in enumerate(_PROBLEM_METHOD_RECTS):
                    if rect.collidepoint(pos):
                        resolve_problem_method(_PROBLEM_SESSION, index)
                        sync_problem_markers()
                        self.action = "world_problem"
                        return True
                self.action = "world_problem"
                return True
            if _PROBLEM_RESULT_CLOSE_RECT and _PROBLEM_RESULT_CLOSE_RECT.collidepoint(pos):
                _PROBLEM_SESSION = None
            self.action = "world_problem"
            return True

        if _PROBLEM_PREVIEW_ID:
            if _PREVIEW_CLOSE_RECT and _PREVIEW_CLOSE_RECT.collidepoint(pos):
                _PROBLEM_PREVIEW_ID = None
                _STATE_OPEN = True
                _STATE_TAB = "problems"
            self.action = "world_state"
            return True

        if _STATE_OPEN:
            if _STATE_CLOSE_RECT and _STATE_CLOSE_RECT.collidepoint(pos):
                close_world_state()
                self.action = "world_state"
                return True
            for key, rect in _TAB_RECTS.items():
                if rect.collidepoint(pos):
                    _STATE_TAB = key
                    _HISTORY_CARD_INDEX = None
                    self.action = "world_state"
                    return True
            if _STATE_TAB == "problems":
                for rect, event_id in _PROBLEM_ROW_RECTS:
                    if rect.collidepoint(pos):
                        _open_problem_preview(event_id)
                        self.action = "world_state"
                        return True
            if _STATE_TAB == "history":
                for rect, index in _HISTORY_ROW_RECTS:
                    if not rect.collidepoint(pos):
                        continue
                    _HISTORY_CARD_INDEX = None if index < 0 else index
                    self.action = "world_state"
                    return True
            self.action = "world_state"
            return True

        if _STATE_BUTTON_RECT and _STATE_BUTTON_RECT.collidepoint(pos):
            open_world_state("active")
            self.action = "world_state"
            return True

        for event in active_world_events(DURATION_UNTIL_RESOLVED):
            event_id = str(event.get("id") or "")
            rect = _marker_screen_rect(event_id)
            if rect and rect.collidepoint(pos):
                _open_problem_preview(event_id)
                self.action = "world_state"
                return True

        player = self._active_player()
        if player is not None:
            for rect, event_id, enabled, reason in _HEX_ACTION_RECTS:
                if not rect.collidepoint(pos):
                    continue
                if enabled:
                    _begin_problem_from_hex(player, event_id)
                else:
                    _MESSAGE = reason
                self.action = "world_problem"
                return True

        clicked = self.delegate.clicked(pos)
        self.action = getattr(self.delegate, "action", "end_turn")
        return clicked


def install_world_state_ui():
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return

    from rg_engine import turns as rg_turns
    from rg_ui import hud as rg_hud
    from rg_world import map as rg_map

    original_scoreboard = rg_hud._draw_scoreboard
    original_bottom_info = rg_hud._draw_bottom_tile_info
    original_player_board_clicked = rg_hud._PlayerBoardButton.clicked
    original_reset_actions = rg_map.HeroToken.reset_actions
    original_end_turn = rg_turns.TurnManager.end_turn

    def scoreboard_with_world_actions(screen, font, small_font, players, tokens, active_player_index, right):
        sync_problem_markers()
        delegate = original_scoreboard(screen, font, small_font, players, tokens, active_player_index, right)
        _draw_hex_actions(screen, small_font, players, tokens, active_player_index, right)
        return _WorldStateController(delegate, players, tokens, active_player_index)

    def bottom_info_with_world_state(screen, font, small_font, selected_tile, rect):
        result = original_bottom_info(screen, font, small_font, selected_tile, rect)
        _draw_state_button(screen, small_font, rect)
        _draw_world_level_banner(screen, font)
        _draw_world_state_overlay(screen, font, small_font)
        _draw_problem_preview(screen, font, small_font)
        _draw_problem_attempt(screen, font, small_font)
        return result

    def player_board_clicked_without_world_modal(self, pos):
        if is_world_state_open():
            return False
        return original_player_board_clicked(self, pos)

    def reset_actions_and_problem_retry(self):
        result = original_reset_actions(self)
        clear_problem_retry_blocks(self.hero)
        return result

    def end_turn_without_world_modal(self, tokens):
        if is_world_state_open():
            return {
                "active_player_index": self.active_player_index,
                "round_completed": False,
                "council_due": False,
            }
        return original_end_turn(self, tokens)

    rg_hud._draw_scoreboard = scoreboard_with_world_actions
    rg_hud._draw_bottom_tile_info = bottom_info_with_world_state
    rg_hud._PlayerBoardButton.clicked = player_board_clicked_without_world_modal
    rg_map.HeroToken.reset_actions = reset_actions_and_problem_retry
    rg_turns.TurnManager.end_turn = end_turn_without_world_modal
    _INSTALL_DONE = True
