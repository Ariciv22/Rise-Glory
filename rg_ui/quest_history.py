from __future__ import annotations

import copy
import math
import sys
from typing import Any

import pygame

_MODE = "active"
_HISTORY_PAGE = 0
_TAB_RECTS: dict[str, pygame.Rect] = {}
_PAGE_RECTS: dict[str, pygame.Rect] = {}
_INSTALLED = False


def _history_quests(hero: dict[str, Any]) -> list[dict[str, Any]]:
    """Zwraca rozstrzygniete Questy bez mieszania ich z limitem 3 aktywnych."""
    result: list[dict[str, Any]] = []
    collections = (
        ("completed_quests", "completed"),
        ("failed_quests", "failed"),
        ("abandoned_quests", "abandoned"),
    )
    for key, fallback_status in collections:
        for raw in reversed(list(hero.get(key, []) or [])):
            if isinstance(raw, dict):
                quest = copy.deepcopy(raw)
            else:
                quest = {"name": str(raw)}
            quest["_history_status"] = str(quest.get("status") or fallback_status)
            result.append(quest)
    return result


def _status(quest: dict[str, Any]) -> tuple[str, tuple[int, int, int]]:
    status = str(quest.get("_history_status") or quest.get("status") or "").lower()
    if status == "completed":
        return "UKOŃCZONY", (166, 214, 122)
    if status == "failed":
        return "PRZEGRANY", (224, 112, 100)
    if status == "abandoned":
        return "PORZUCONY", (180, 174, 160)
    return status.upper() or "ZAKOŃCZONY", (211, 179, 113)


def _board_rect(player_board, screen):
    source = player_board._load_board_source()
    if source is None:
        return screen.get_rect().inflate(-24, -24)
    return player_board._board_rect(screen, source)


def _draw_tabs(player_board, screen, board, hero):
    global _TAB_RECTS, _PAGE_RECTS
    active_count = len(hero.get("active_quests", []) or [])
    history_count = len(_history_quests(hero))
    tab_y = 0.646
    active_rect = player_board._relative_rect(board, 0.282, tab_y, 0.165, 0.038)
    history_rect = player_board._relative_rect(board, 0.455, tab_y, 0.190, 0.038)
    _TAB_RECTS = {"active": active_rect, "history": history_rect}
    font = player_board._font(board, 12, bold=True)

    for key, rect, label in (
        ("active", active_rect, f"AKTYWNE {active_count}/3"),
        ("history", history_rect, f"HISTORIA {history_count}"),
    ):
        selected = _MODE == key
        pygame.draw.rect(screen, (74, 58, 37) if selected else (33, 31, 28), rect, border_radius=6)
        pygame.draw.rect(screen, (220, 163, 71) if selected else (105, 89, 61), rect, 2 if selected else 1, border_radius=6)
        player_board._draw_text(
            screen,
            font,
            label,
            rect.center,
            (238, 205, 140) if selected else (168, 154, 126),
            anchor="center",
            shadow=False,
        )

    _PAGE_RECTS = {}
    if _MODE != "history" or history_count <= 3:
        return
    pages = max(1, math.ceil(history_count / 3))
    page = max(0, min(_HISTORY_PAGE, pages - 1))
    prev_rect = player_board._relative_rect(board, 0.656, tab_y, 0.035, 0.038)
    next_rect = player_board._relative_rect(board, 0.752, tab_y, 0.035, 0.038)
    page_rect = player_board._relative_rect(board, 0.695, tab_y, 0.053, 0.038)
    _PAGE_RECTS = {"prev": prev_rect, "next": next_rect}
    for rect, label, enabled in (
        (prev_rect, "‹", page > 0),
        (next_rect, "›", page + 1 < pages),
    ):
        pygame.draw.rect(screen, (62, 51, 36) if enabled else (33, 31, 28), rect, border_radius=5)
        pygame.draw.rect(screen, (190, 134, 48) if enabled else (78, 72, 62), rect, 1, border_radius=5)
        player_board._draw_text(screen, font, label, rect.center, (230, 194, 126) if enabled else (100, 95, 86), anchor="center", shadow=False)
    player_board._draw_text(screen, font, f"{page + 1}/{pages}", page_rect.center, (205, 183, 137), anchor="center", shadow=False)


def _draw_history_row_statuses(player_board, screen, board, rows, quests):
    font = player_board._font(board, 10, bold=True)
    for row, quest in zip(rows, quests):
        label, color = _status(quest)
        badge = pygame.Rect(0, 0, max(74, int(row.width * 0.105)), max(18, int(row.height * 0.26)))
        badge.topright = (row.right - 8, row.y + 6)
        pygame.draw.rect(screen, (24, 23, 20), badge, border_radius=5)
        pygame.draw.rect(screen, color, badge, 1, border_radius=5)
        player_board._draw_text(screen, font, label, badge.center, color, anchor="center", shadow=False)


def _draw_empty_history(player_board, screen, board):
    font = player_board._font(board, 14, bold=True)
    player_board._draw_text(
        screen,
        font,
        "Brak zakończonych Questów.",
        player_board._point(board, 0.61, 0.80),
        (170, 158, 132),
        anchor="center",
    )


def _draw_history_details(player_board, screen, board, quest):
    board_shade = pygame.Surface(board.size, pygame.SRCALPHA)
    board_shade.fill((0, 0, 0, 176))
    screen.blit(board_shade, board.topleft)

    panel = player_board._relative_rect(board, 0.305, 0.205, 0.505, 0.500)
    radius = max(8, int(14 * board.height / 941))
    pygame.draw.rect(screen, (12, 11, 10), panel, border_radius=radius)
    pygame.draw.rect(screen, (190, 134, 48), panel, max(2, int(3 * board.height / 941)), border_radius=radius)

    title_font = player_board._font(board, 24, bold=True)
    subtitle_font = player_board._font(board, 13, bold=True)
    body_font = player_board._font(board, 14)
    title = str(quest.get("name") or quest.get("title") or "Quest")
    number = int(quest.get("quest_number", 0) or 0)
    if number:
        title = f"#{number}  {title}"
    status_label, status_color = _status(quest)

    player_board._draw_text(screen, title_font, title, (panel.centerx, panel.y + int(panel.height * 0.10)), (235, 199, 126), anchor="center")
    player_board._draw_text(screen, subtitle_font, status_label, (panel.centerx, panel.y + int(panel.height * 0.22)), status_color, anchor="center")

    failures = int(quest.get("failures", 0) or 0)
    ending = str(quest.get("ending_id") or "")
    meta = f"Porażki: {failures}/5"
    if ending:
        meta += f"   |   Finał: {ending}"
    player_board._draw_text(screen, subtitle_font, meta, (panel.centerx, panel.y + int(panel.height * 0.29)), (203, 181, 137), anchor="center")

    body = str(quest.get("last_result") or quest.get("description") or quest.get("objective") or "Brak zapisanego podsumowania.")
    body_y = panel.y + int(panel.height * 0.37)
    max_width = int(panel.width * 0.82)
    for line in player_board._wrap(body_font, body, max_width)[:8]:
        player_board._draw_text(screen, body_font, line, (panel.centerx, body_y), (228, 221, 205), anchor="midtop")
        body_y += body_font.get_height() + max(3, int(4 * board.height / 941))

    close_rect = pygame.Rect(0, 0, int(panel.width * 0.34), max(34, int(panel.height * 0.11)))
    close_rect.center = (panel.centerx, panel.bottom - int(panel.height * 0.085))
    hovered = close_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, (75, 62, 43) if hovered else (46, 38, 28), close_rect, border_radius=max(5, int(8 * board.height / 941)))
    pygame.draw.rect(screen, (190, 134, 48), close_rect, max(1, int(2 * board.height / 941)), border_radius=max(5, int(8 * board.height / 941)))
    close_font = player_board._font(board, 15, bold=True)
    player_board._draw_text(screen, close_font, "Zamknij podgląd", close_rect.center, (228, 221, 205), anchor="center", shadow=False)
    return close_rect


def install_quest_history_ui() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    from rg_ui import hud
    from rg_ui import player_board

    original_draw_player_board = player_board.draw_player_board
    original_draw_game_ui = hud.draw_game_ui
    original_button_clicked = hud._PlayerBoardButton.clicked

    def draw_player_board_with_history(screen, hero):
        global _HISTORY_PAGE
        board = _board_rect(player_board, screen)
        history = _history_quests(hero)
        pages = max(1, math.ceil(len(history) / 3))
        _HISTORY_PAGE = max(0, min(_HISTORY_PAGE, pages - 1))

        if _MODE != "history":
            controls = original_draw_player_board(screen, hero)
            _draw_tabs(player_board, screen, board, hero)
            return controls

        start = _HISTORY_PAGE * 3
        visible = history[start : start + 3]
        fake_hero = dict(hero)
        fake_hero["active_quests"] = visible
        selected = player_board.get_open_quest_index()

        if selected is None:
            controls = original_draw_player_board(screen, fake_hero)
            _draw_history_row_statuses(player_board, screen, board, controls.get("quest_rows", []), visible)
        else:
            player_board._OPEN_QUEST_INDEX = None
            try:
                controls = original_draw_player_board(screen, fake_hero)
            finally:
                player_board._OPEN_QUEST_INDEX = selected
            controls["quest_rows"] = []
            if 0 <= int(selected) < len(visible):
                controls["quest_close_rect"] = _draw_history_details(player_board, screen, board, visible[int(selected)])
            else:
                player_board.close_quest_details()

        if not visible and selected is None:
            _draw_empty_history(player_board, screen, board)
        _draw_tabs(player_board, screen, board, hero)
        return controls

    def button_clicked_with_history(self, pos):
        global _MODE, _HISTORY_PAGE
        action = str(getattr(self, "action", ""))
        if action == "quest_view:active" and self.rect.collidepoint(pos):
            _MODE = "active"
            _HISTORY_PAGE = 0
            player_board.close_quest_details()
            return True
        if action == "quest_view:history" and self.rect.collidepoint(pos):
            _MODE = "history"
            _HISTORY_PAGE = 0
            player_board.close_quest_details()
            return True
        if action == "quest_history:prev" and self.rect.collidepoint(pos):
            _HISTORY_PAGE = max(0, _HISTORY_PAGE - 1)
            player_board.close_quest_details()
            return True
        if action == "quest_history:next" and self.rect.collidepoint(pos):
            pages = max(1, math.ceil(len(_history_quests(getattr(self, "_history_hero", {}) or {})) / 3))
            _HISTORY_PAGE = min(pages - 1, _HISTORY_PAGE + 1)
            player_board.close_quest_details()
            return True

        clicked = original_button_clicked(self, pos)
        if clicked and action == "open_player_board":
            _MODE = "active"
            _HISTORY_PAGE = 0
        return clicked

    def draw_game_ui_with_history(*args, **kwargs):
        result = list(original_draw_game_ui(*args, **kwargs) or [])
        if not player_board.is_player_board_open():
            return result

        hero = kwargs.get("hero")
        if hero is None and len(args) >= 4:
            hero = args[3]
        hero = hero or {}
        extras = []
        for key, rect in _TAB_RECTS.items():
            extras.append(hud._PlayerBoardButton("", f"quest_view:{key}", rect))
        if _MODE == "history":
            history = _history_quests(hero)
            pages = max(1, math.ceil(len(history) / 3))
            if "prev" in _PAGE_RECTS and _HISTORY_PAGE > 0:
                button = hud._PlayerBoardButton("", "quest_history:prev", _PAGE_RECTS["prev"])
                button._history_hero = hero
                extras.append(button)
            if "next" in _PAGE_RECTS and _HISTORY_PAGE + 1 < pages:
                button = hud._PlayerBoardButton("", "quest_history:next", _PAGE_RECTS["next"])
                button._history_hero = hero
                extras.append(button)

        if result and str(getattr(result[-1], "action", "")) == "player_board_block":
            return [*result[:-1], *extras, result[-1]]
        return [*result, *extras]

    player_board.draw_player_board = draw_player_board_with_history
    hud.draw_player_board = draw_player_board_with_history
    hud._PlayerBoardButton.clicked = button_clicked_with_history
    hud.draw_game_ui = draw_game_ui_with_history

    app = sys.modules.get("rg_core.app")
    if app is not None and getattr(app, "draw_game_ui", None) is original_draw_game_ui:
        app.draw_game_ui = draw_game_ui_with_history

    _INSTALLED = True
