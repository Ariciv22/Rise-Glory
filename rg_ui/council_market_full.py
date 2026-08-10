from __future__ import annotations

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_ui import council_market as market_ui
from rg_ui.common import Button, draw_lines, wrap

_PANEL_TAB = "chat"
_CHAT_BUFFER = ""
_CHAT_FOCUSED = False
_CHAT_SENDER = 0
_PREVIOUS_KEYS: tuple[bool, ...] | None = None
_LAST_LOG_COUNT = 0
_UNREAD_LOGS = 0


class CommButton(Button):
    def __init__(self, text, rect, callback, enabled=True):
        super().__init__(text, "council_noop", rect)
        self.callback = callback
        self.enabled = enabled

    def draw(self, screen, font, mouse_pos, active=False):
        if self.enabled:
            super().draw(screen, font, mouse_pos, active=active)
            return
        pygame.draw.rect(screen, (29, 32, 35), self.rect, border_radius=8)
        pygame.draw.rect(screen, (69, 72, 74), self.rect, 1, border_radius=8)
        if self.text:
            label = font.render(self.text, True, (110, 110, 110))
            screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        if not self.enabled or not self.rect.collidepoint(pos):
            return False
        result = self.callback() if self.callback else None
        self.action = result if isinstance(result, str) else "council_noop"
        return True


def _button(screen, font, mouse, buttons, text, rect, callback, active=False, enabled=True):
    button = CommButton(text, rect, callback, enabled=enabled)
    button.draw(screen, font, mouse, active=active)
    buttons.append(button)
    return button


def _fit(font, text, width):
    value = str(text or "")
    if font.size(value)[0] <= width:
        return value
    while value and font.size(value + "…")[0] > width:
        value = value[:-1]
    return value.rstrip() + "…"


def _set_tab(tab):
    global _PANEL_TAB, _UNREAD_LOGS
    _PANEL_TAB = tab
    if tab == "logs":
        _UNREAD_LOGS = 0


def _focus_chat():
    global _CHAT_FOCUSED
    _CHAT_FOCUSED = True


def _blur_chat():
    global _CHAT_FOCUSED
    _CHAT_FOCUSED = False


def _change_sender(session, delta):
    global _CHAT_SENDER
    if not session.players:
        _CHAT_SENDER = 0
        return
    _CHAT_SENDER = (_CHAT_SENDER + int(delta)) % len(session.players)


def _send_chat(session):
    global _CHAT_BUFFER
    text = _CHAT_BUFFER.strip()
    if not text:
        return
    sender = min(max(0, _CHAT_SENDER), max(0, len(session.players) - 1))
    session.add_chat_message(sender, text)
    _CHAT_BUFFER = ""


def _key_to_character(key, shift):
    name = pygame.key.name(key)
    if len(name) == 1:
        return name.upper() if shift else name
    mapping = {
        "space": " ",
        "minus": "_" if shift else "-",
        "equals": "+" if shift else "=",
        "comma": "<" if shift else ",",
        "period": ">" if shift else ".",
        "slash": "?" if shift else "/",
        "semicolon": ":" if shift else ";",
        "quote": '"' if shift else "'",
    }
    return mapping.get(name, "")


def _poll_chat_keyboard(session):
    global _PREVIOUS_KEYS, _CHAT_BUFFER, _CHAT_FOCUSED
    pressed = tuple(bool(value) for value in pygame.key.get_pressed())
    if _PREVIOUS_KEYS is None:
        _PREVIOUS_KEYS = pressed
        return
    if not _CHAT_FOCUSED or _PANEL_TAB != "chat":
        _PREVIOUS_KEYS = pressed
        return

    mods = pygame.key.get_mods()
    shift = bool(mods & pygame.KMOD_SHIFT)
    for key, is_down in enumerate(pressed):
        if not is_down or (key < len(_PREVIOUS_KEYS) and _PREVIOUS_KEYS[key]):
            continue
        if key == pygame.K_BACKSPACE:
            _CHAT_BUFFER = _CHAT_BUFFER[:-1]
            continue
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            _send_chat(session)
            continue
        if key == pygame.K_ESCAPE:
            _CHAT_FOCUSED = False
            continue
        if len(_CHAT_BUFFER) >= 300:
            continue
        char = _key_to_character(key, shift)
        if char:
            _CHAT_BUFFER += char
    _PREVIOUS_KEYS = pressed


def _update_unread_logs(session):
    global _LAST_LOG_COUNT, _UNREAD_LOGS
    current = len(session.trade_logs)
    if current < _LAST_LOG_COUNT:
        _LAST_LOG_COUNT = current
        _UNREAD_LOGS = 0
        return
    added = current - _LAST_LOG_COUNT
    if added > 0 and _PANEL_TAB != "logs":
        _UNREAD_LOGS += added
    _LAST_LOG_COUNT = current


def _draw_chat(screen, small_font, session, area):
    y = area.y
    entries = session.chat_messages[-6:]
    if not entries:
        screen.blit(small_font.render("Czat jest jawny dla wszystkich graczy.", True, MUTED), (area.x, y))
        return
    for entry in entries:
        name = str(entry.get("name", "Gracz"))
        text = str(entry.get("text", ""))
        lines = wrap(small_font, f"{name}: {text}", area.width)[:2]
        y = draw_lines(screen, small_font, lines, area.x, y, TEXT, line_h=18)
        y += 4
        if y + 20 > area.bottom:
            break


def _draw_logs(screen, small_font, session, area):
    y = area.y
    entries = session.trade_logs[-6:]
    if not entries:
        screen.blit(small_font.render("Brak wpisów w Logach handlu.", True, MUTED), (area.x, y))
        return
    for entry in entries:
        lines = wrap(small_font, entry.text, area.width)[:2]
        y = draw_lines(screen, small_font, lines, area.x, y, MUTED, line_h=18)
        y += 4
        if y + 20 > area.bottom:
            break


def _draw_comm_overlay(screen, font, small_font, mouse, buttons, session):
    global _CHAT_SENDER
    if session.stage not in {"turns", "summary", "departure"}:
        return
    if not session.players:
        return
    _CHAT_SENDER = min(max(0, _CHAT_SENDER), len(session.players) - 1)

    sw, sh = screen.get_size()
    width = min(390, max(330, sw // 4))
    height = 236
    rect = pygame.Rect(sw - width - 18, sh - height - 18, width, height)
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, (10, 12, 15, 241), surface.get_rect(), border_radius=12)
    pygame.draw.rect(surface, (115, 92, 57), surface.get_rect(), 2, border_radius=12)
    screen.blit(surface, rect.topleft)

    log_label = "LOGI HANDLU"
    if _UNREAD_LOGS:
        log_label += f" ({_UNREAD_LOGS})"
    _button(screen, small_font, mouse, buttons, "CZAT", (rect.x + 10, rect.y + 10, 104, 30), lambda: _set_tab("chat"), active=_PANEL_TAB == "chat")
    _button(screen, small_font, mouse, buttons, log_label, (rect.x + 122, rect.y + 10, 160, 30), lambda: _set_tab("logs"), active=_PANEL_TAB == "logs")

    area_bottom = rect.bottom - (58 if _PANEL_TAB == "chat" else 14)
    area = pygame.Rect(rect.x + 12, rect.y + 52, rect.width - 24, area_bottom - rect.y - 52)
    if _PANEL_TAB == "logs":
        _draw_logs(screen, small_font, session, area)
        return

    _draw_chat(screen, small_font, session, area)
    sender = session.players[_CHAT_SENDER]
    sender_text = _fit(small_font, f"Pisze: {sender.get('name', 'Gracz')}", rect.width - 168)
    screen.blit(small_font.render(sender_text, True, GOLD), (rect.x + 12, rect.bottom - 48))
    _button(screen, small_font, mouse, buttons, "‹", (rect.right - 146, rect.bottom - 52, 30, 28), lambda: _change_sender(session, -1))
    _button(screen, small_font, mouse, buttons, "›", (rect.right - 110, rect.bottom - 52, 30, 28), lambda: _change_sender(session, 1))

    input_rect = pygame.Rect(rect.x + 12, rect.bottom - 22, rect.width - 88, 18)
    pygame.draw.rect(screen, (24, 27, 30), input_rect, border_radius=5)
    pygame.draw.rect(screen, GOLD if _CHAT_FOCUSED else (74, 77, 79), input_rect, 1, border_radius=5)
    shown = _CHAT_BUFFER if _CHAT_BUFFER else ("Kliknij i napisz…" if not _CHAT_FOCUSED else "")
    screen.blit(small_font.render(_fit(small_font, shown, input_rect.width - 8), True, TEXT if _CHAT_BUFFER else MUTED), (input_rect.x + 4, input_rect.y + 1))
    _button(screen, small_font, mouse, buttons, "", input_rect, _focus_chat)
    _button(screen, small_font, mouse, buttons, "WYŚLIJ", (rect.right - 70, rect.bottom - 24, 60, 20), lambda: _send_chat(session), enabled=bool(_CHAT_BUFFER.strip()))


def draw_council(screen, title_font, font, small_font, mouse, round_number):
    session = market_ui._session(round_number)
    _poll_chat_keyboard(session)
    _update_unread_logs(session)
    buttons = market_ui.draw_council(screen, title_font, font, small_font, mouse, round_number)
    _draw_comm_overlay(screen, font, small_font, mouse, buttons, session)
    return buttons
