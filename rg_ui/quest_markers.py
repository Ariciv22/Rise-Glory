from __future__ import annotations

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_ui.quest import draw_quest_panel, quest_action
from rg_world.quest_markers import (
    marker_screen_rect,
    quest_for_marker,
    quest_marker_ids_on_tile,
    quest_marker_preview,
)
from rg_world.world_event_markers import active_camera, marker_event_ids_on_tile

_INSTALL_DONE = False
_QUEST_HEX_ACTION_RECTS = []
_QUEST_PREVIEW_ID = None
_QUEST_PANEL_ID = None
_QUEST_PANEL_PLAYER = None
_QUEST_PANEL_BUTTONS = []
_QUEST_CLOSE_RECT = None
_QUEST_OPEN_RECT = None


def is_quest_marker_modal_open() -> bool:
    return bool(_QUEST_PREVIEW_ID or _QUEST_PANEL_ID)


def _fit(font, text, width):
    value = str(text or "")
    if font.size(value)[0] <= width:
        return value
    while value and font.size(value + "...")[0] > width:
        value = value[:-1]
    return value.rstrip() + "..."


def _open_quest_from_marker(marker_id: str, active_player=None) -> bool:
    global _QUEST_PANEL_ID, _QUEST_PANEL_PLAYER, _QUEST_PREVIEW_ID
    owner, quest, marker = quest_for_marker(marker_id)
    if not owner or not quest or not marker:
        return False
    if active_player is not None and owner is not active_player:
        return False
    quest["current_marker_id"] = str(marker_id)
    _QUEST_PANEL_ID = str(quest.get("id") or "")
    _QUEST_PANEL_PLAYER = owner
    _QUEST_PREVIEW_ID = None
    return bool(_QUEST_PANEL_ID)


def _draw_hex_actions_with_quests(original, screen, small_font, players, tokens, active_player_index, right):
    global _QUEST_HEX_ACTION_RECTS
    result = original(screen, small_font, players, tokens, active_player_index, right)
    _QUEST_HEX_ACTION_RECTS = []
    if not players or active_player_index >= len(players) or active_player_index >= len(tokens):
        return result

    player = players[active_player_index]
    token = tokens[active_player_index]
    refs = quest_marker_ids_on_tile(token.tile)
    if not refs:
        return result

    threat_count = len(marker_event_ids_on_tile(token.tile))
    threat_height = 44 + threat_count * 40 if threat_count else 0
    panel_h = 44 + len(refs) * 40
    bottom_margin = 62 + threat_height + (8 if threat_height else 0)
    panel = pygame.Rect(right.x + 12, max(right.y + 8, right.bottom - panel_h - bottom_margin), right.width - 24, panel_h)
    pygame.draw.rect(screen, (15, 23, 30), panel, border_radius=10)
    pygame.draw.rect(screen, GOLD, panel, 1, border_radius=10)
    screen.blit(small_font.render("Questy na tym heksie", True, GOLD), (panel.x + 12, panel.y + 10))

    y = panel.y + 36
    mouse = pygame.mouse.get_pos()
    for marker_id in refs:
        preview = quest_marker_preview(marker_id)
        if not preview:
            continue
        owner = preview.get("owner")
        quest = preview.get("quest") or {}
        own = owner is player
        enabled = own and quest.get("status") == "active"
        reason = "" if enabled else "Ten Znacznik Questa należy do innego bohatera."
        label = f"{preview.get('action_label', 'Kontynuuj Quest')} #{preview.get('quest_number', 0)}"
        rect = pygame.Rect(panel.x + 10, y, panel.width - 20, 34)
        pygame.draw.rect(screen, (49, 62, 75) if enabled else (43, 44, 45), rect, border_radius=7)
        pygame.draw.rect(screen, GOLD if enabled else (76, 76, 76), rect, 1, border_radius=7)
        screen.blit(small_font.render(_fit(small_font, label, rect.width - 18), True, TEXT if enabled else MUTED), (rect.x + 9, rect.y + 8))
        _QUEST_HEX_ACTION_RECTS.append((rect, marker_id, enabled, reason))
        if not enabled and reason and rect.collidepoint(mouse):
            tooltip = small_font.render(reason, True, TEXT)
            tip = pygame.Rect(mouse[0] + 14, mouse[1] + 14, tooltip.get_width() + 16, tooltip.get_height() + 12)
            pygame.draw.rect(screen, (18, 20, 22), tip, border_radius=7)
            pygame.draw.rect(screen, GOLD, tip, 1, border_radius=7)
            screen.blit(tooltip, (tip.x + 8, tip.y + 6))
        y += 40
    return result


def _wrap(font, text, width):
    words = str(text or "").split()
    lines = []
    line = ""
    for word in words:
        candidate = word if not line else f"{line} {word}"
        if font.size(candidate)[0] <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _draw_preview(screen, font, small_font):
    global _QUEST_CLOSE_RECT, _QUEST_OPEN_RECT
    if not _QUEST_PREVIEW_ID or _QUEST_PANEL_ID:
        return
    preview = quest_marker_preview(_QUEST_PREVIEW_ID)
    if not preview:
        return
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 178))
    screen.blit(shade, (0, 0))
    sw, sh = screen.get_size()
    card = pygame.Rect(sw // 2 - 320, sh // 2 - 190, 640, 380)
    pygame.draw.rect(screen, (12, 16, 20), card, border_radius=14)
    pygame.draw.rect(screen, GOLD, card, 2, border_radius=14)
    title = f"Quest #{preview.get('quest_number', 0)} - {preview.get('quest_name', 'Quest')}"
    screen.blit(font.render(title, True, TEXT), (card.x + 26, card.y + 24))

    _QUEST_CLOSE_RECT = pygame.Rect(card.right - 50, card.y + 16, 32, 32)
    pygame.draw.rect(screen, (53, 41, 35), _QUEST_CLOSE_RECT, border_radius=8)
    close = font.render("x", True, TEXT)
    screen.blit(close, close.get_rect(center=_QUEST_CLOSE_RECT.center))

    description = str(preview.get("description") or "")
    y = card.y + 82
    for line in _wrap(small_font, description, card.width - 52)[:6]:
        screen.blit(small_font.render(line, True, MUTED), (card.x + 26, y))
        y += small_font.get_height() + 5

    owner = preview.get("owner")
    quest = preview.get("quest") or {}
    owner_name = owner.get("name", "Bohater") if isinstance(owner, dict) else "Bohater"
    screen.blit(small_font.render(f"Właściciel: {owner_name}", True, GOLD), (card.x + 26, card.bottom - 92))

    _QUEST_OPEN_RECT = pygame.Rect(card.x + 26, card.bottom - 56, card.width - 52, 38)
    pygame.draw.rect(screen, (54, 66, 79), _QUEST_OPEN_RECT, border_radius=8)
    pygame.draw.rect(screen, GOLD, _QUEST_OPEN_RECT, 1, border_radius=8)
    label = "Otwórz Quest" if quest.get("status") == "active" else "Quest nieaktywny"
    rendered = small_font.render(label, True, TEXT if quest.get("status") == "active" else MUTED)
    screen.blit(rendered, rendered.get_rect(center=_QUEST_OPEN_RECT.center))


def _draw_quest_panel_modal(screen, font, small_font):
    global _QUEST_PANEL_BUTTONS, _QUEST_CLOSE_RECT
    if not _QUEST_PANEL_ID or not _QUEST_PANEL_PLAYER:
        return
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 188))
    screen.blit(shade, (0, 0))
    content = pygame.Rect(50, 50, screen.get_width() - 100, screen.get_height() - 100)
    _QUEST_PANEL_BUTTONS = draw_quest_panel(
        screen,
        font,
        small_font,
        pygame.mouse.get_pos(),
        content,
        _QUEST_PANEL_PLAYER,
        _QUEST_PANEL_ID,
    )
    _QUEST_CLOSE_RECT = pygame.Rect(content.right - 54, content.y + 8, 38, 34)
    pygame.draw.rect(screen, (53, 41, 35), _QUEST_CLOSE_RECT, border_radius=8)
    pygame.draw.rect(screen, GOLD, _QUEST_CLOSE_RECT, 1, border_radius=8)
    label = small_font.render("X", True, TEXT)
    screen.blit(label, label.get_rect(center=_QUEST_CLOSE_RECT.center))


def install_quest_marker_ui() -> None:
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return

    from rg_engine import turns as rg_turns
    from rg_ui import hud as rg_hud
    from rg_ui import world_state

    original_draw_hex_actions = world_state._draw_hex_actions
    original_controller_clicked = world_state._WorldStateController.clicked
    original_bottom_info = rg_hud._draw_bottom_tile_info
    original_player_board_clicked = rg_hud._PlayerBoardButton.clicked
    original_end_turn = rg_turns.TurnManager.end_turn
    original_is_world_state_open = world_state.is_world_state_open

    def draw_hex_actions_with_quests(screen, small_font, players, tokens, active_player_index, right):
        return _draw_hex_actions_with_quests(
            original_draw_hex_actions,
            screen,
            small_font,
            players,
            tokens,
            active_player_index,
            right,
        )

    def bottom_info_with_quest_markers(screen, font, small_font, selected_tile, rect):
        result = original_bottom_info(screen, font, small_font, selected_tile, rect)
        _draw_preview(screen, font, small_font)
        _draw_quest_panel_modal(screen, font, small_font)
        return result

    def clicked_with_quest_markers(self, pos):
        global _QUEST_PREVIEW_ID, _QUEST_PANEL_ID, _QUEST_PANEL_PLAYER
        if _QUEST_PANEL_ID:
            if _QUEST_CLOSE_RECT and _QUEST_CLOSE_RECT.collidepoint(pos):
                _QUEST_PANEL_ID = None
                _QUEST_PANEL_PLAYER = None
                self.action = "world_state"
                return True
            for button in _QUEST_PANEL_BUTTONS:
                if button.clicked(pos):
                    self.action = quest_action(_QUEST_PANEL_ID)
                    return True
            self.action = "world_state"
            return True

        if _QUEST_PREVIEW_ID:
            if _QUEST_CLOSE_RECT and _QUEST_CLOSE_RECT.collidepoint(pos):
                _QUEST_PREVIEW_ID = None
                self.action = "world_state"
                return True
            if _QUEST_OPEN_RECT and _QUEST_OPEN_RECT.collidepoint(pos):
                player = self._active_player()
                if _open_quest_from_marker(_QUEST_PREVIEW_ID, active_player=player):
                    self.action = quest_action(_QUEST_PANEL_ID)
                else:
                    world_state._MESSAGE = "Nie możesz rozwiązywać cudzego Questa."
                return True
            self.action = "world_state"
            return True

        if not original_is_world_state_open():
            camera = active_camera()
            if camera is not None:
                for player in self.players:
                    for quest in player.get("active_quests", []) or []:
                        for marker in quest.get("markers", []) or []:
                            marker_id = str(marker.get("marker_id") or "")
                            rect = marker_screen_rect(marker_id, camera)
                            if rect and rect.collidepoint(pos):
                                _QUEST_PREVIEW_ID = marker_id
                                self.action = "world_state"
                                return True

        active_player = self._active_player()
        if active_player is not None:
            for rect, marker_id, enabled, reason in _QUEST_HEX_ACTION_RECTS:
                if not rect.collidepoint(pos):
                    continue
                if enabled:
                    _open_quest_from_marker(marker_id, active_player=active_player)
                    self.action = quest_action(_QUEST_PANEL_ID)
                else:
                    world_state._MESSAGE = reason
                    self.action = "world_state"
                return True

        return original_controller_clicked(self, pos)

    def player_board_clicked_without_quest_modal(self, pos):
        if is_quest_marker_modal_open():
            return False
        return original_player_board_clicked(self, pos)

    def end_turn_without_quest_modal(self, tokens):
        if is_quest_marker_modal_open():
            return {
                "active_player_index": self.active_player_index,
                "round_completed": False,
                "council_due": False,
            }
        return original_end_turn(self, tokens)

    def is_world_or_quest_state_open():
        return original_is_world_state_open() or is_quest_marker_modal_open()

    world_state._draw_hex_actions = draw_hex_actions_with_quests
    world_state._WorldStateController.clicked = clicked_with_quest_markers
    world_state.is_world_state_open = is_world_or_quest_state_open
    rg_hud._draw_bottom_tile_info = bottom_info_with_quest_markers
    rg_hud._PlayerBoardButton.clicked = player_board_clicked_without_quest_modal
    rg_turns.TurnManager.end_turn = end_turn_without_quest_modal
    _INSTALL_DONE = True
