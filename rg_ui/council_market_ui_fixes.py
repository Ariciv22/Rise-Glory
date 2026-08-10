from __future__ import annotations

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_engine.council import _asset_name
from rg_ui import council_flow
from rg_ui import council_market as market_ui
from rg_ui import council_market_full as market_full
from rg_ui.common import draw_lines, wrap

_INSTALLED = False
_CHAT_SCROLL = 0
_LOG_SCROLL = 0
_LAST_CHAT_COUNT = 0
_LAST_LOG_COUNT_LOCAL = 0


def _scroll_chat(delta: int) -> None:
    global _CHAT_SCROLL
    _CHAT_SCROLL = max(0, _CHAT_SCROLL + int(delta))


def _scroll_logs(delta: int) -> None:
    global _LOG_SCROLL
    _LOG_SCROLL = max(0, _LOG_SCROLL + int(delta))


def _visible_tail(values, capacity: int, offset: int):
    values = list(values or [])
    capacity = max(1, int(capacity))
    offset = max(0, min(int(offset), max(0, len(values) - 1)))
    end = max(0, len(values) - offset)
    start = max(0, end - capacity)
    return values[start:end]


def _sync_scroll_after_new_messages(session) -> None:
    global _CHAT_SCROLL, _LOG_SCROLL, _LAST_CHAT_COUNT, _LAST_LOG_COUNT_LOCAL
    chat_count = len(session.chat_messages)
    log_count = len(session.trade_logs)
    if chat_count > _LAST_CHAT_COUNT and _CHAT_SCROLL == 0:
        _CHAT_SCROLL = 0
    if log_count > _LAST_LOG_COUNT_LOCAL and _LOG_SCROLL == 0:
        _LOG_SCROLL = 0
    if chat_count < _LAST_CHAT_COUNT:
        _CHAT_SCROLL = 0
    if log_count < _LAST_LOG_COUNT_LOCAL:
        _LOG_SCROLL = 0
    _LAST_CHAT_COUNT = chat_count
    _LAST_LOG_COUNT_LOCAL = log_count


def _draw_chat_fixed(screen, small_font, session, area):
    global _CHAT_SCROLL
    capacity = max(1, area.height // 38)
    max_offset = max(0, len(session.chat_messages) - 1)
    _CHAT_SCROLL = min(_CHAT_SCROLL, max_offset)
    entries = _visible_tail(session.chat_messages, capacity, _CHAT_SCROLL)
    if not entries:
        screen.blit(small_font.render("Czat jest jawny dla wszystkich graczy.", True, MUTED), (area.x, area.y))
        return

    y = area.y
    for entry in entries:
        name = str(entry.get("name", "Gracz"))
        text = str(entry.get("text", ""))
        lines = wrap(small_font, f"{name}: {text}", area.width)[:2]
        next_y = y + len(lines) * 18 + 5
        if next_y > area.bottom:
            break
        y = draw_lines(screen, small_font, lines, area.x, y, TEXT, line_h=18)
        y += 5


def _draw_logs_fixed(screen, small_font, session, area):
    global _LOG_SCROLL
    capacity = max(1, area.height // 42)
    max_offset = max(0, len(session.trade_logs) - 1)
    _LOG_SCROLL = min(_LOG_SCROLL, max_offset)
    entries = _visible_tail(session.trade_logs, capacity, _LOG_SCROLL)
    if not entries:
        screen.blit(small_font.render("Brak wpisów w Logach handlu.", True, MUTED), (area.x, area.y))
        return

    y = area.y
    for entry in entries:
        lines = wrap(small_font, entry.text, area.width)[:2]
        next_y = y + len(lines) * 18 + 5
        if next_y > area.bottom:
            break
        y = draw_lines(screen, small_font, lines, area.x, y, MUTED, line_h=18)
        y += 5


def _send_chat_fixed(session):
    global _CHAT_SCROLL
    text = market_full._CHAT_BUFFER.strip()
    if not text:
        return
    sender = min(max(0, market_full._CHAT_SENDER), max(0, len(session.players) - 1))
    session.add_chat_message(sender, text)
    market_full._CHAT_BUFFER = ""
    _CHAT_SCROLL = 0


def _comm_rect(screen, session):
    sw, sh = screen.get_size()
    if session.stage == "departure":
        left = pygame.Rect(34, 138, int((sw - 86) * 0.56), sh - 190)
        return pygame.Rect(left.right + 18, 138, sw - left.right - 52, sh - 190)

    width = min(390, max(330, sw // 4))
    height = 250
    return pygame.Rect(sw - width - 18, sh - height - 18, width, height)


def _draw_comm_overlay_fixed(screen, font, small_font, mouse, buttons, session):
    if session.stage not in {"turns", "summary", "departure"} or not session.players:
        return

    _sync_scroll_after_new_messages(session)
    market_full._CHAT_SENDER = min(max(0, market_full._CHAT_SENDER), len(session.players) - 1)

    rect = _comm_rect(screen, session)
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, (10, 12, 15, 241), surface.get_rect(), border_radius=12)
    pygame.draw.rect(surface, (115, 92, 57), surface.get_rect(), 2, border_radius=12)
    screen.blit(surface, rect.topleft)

    log_label = "LOGI HANDLU"
    if market_full._UNREAD_LOGS:
        log_label += f" ({market_full._UNREAD_LOGS})"

    market_full._button(
        screen, small_font, mouse, buttons, "CZAT",
        (rect.x + 10, rect.y + 10, 104, 30),
        lambda: market_full._set_tab("chat"),
        active=market_full._PANEL_TAB == "chat",
    )
    market_full._button(
        screen, small_font, mouse, buttons, log_label,
        (rect.x + 122, rect.y + 10, 160, 30),
        lambda: market_full._set_tab("logs"),
        active=market_full._PANEL_TAB == "logs",
    )

    # Przewijanie starszych/nowszych wpisów bez potrzeby obsługi kółka myszy w starej pętli aplikacji.
    if market_full._PANEL_TAB == "chat":
        market_full._button(screen, small_font, mouse, buttons, "▲", (rect.right - 72, rect.y + 10, 28, 30), lambda: _scroll_chat(1))
        market_full._button(screen, small_font, mouse, buttons, "▼", (rect.right - 38, rect.y + 10, 28, 30), lambda: _scroll_chat(-1), enabled=_CHAT_SCROLL > 0)
    else:
        market_full._button(screen, small_font, mouse, buttons, "▲", (rect.right - 72, rect.y + 10, 28, 30), lambda: _scroll_logs(1))
        market_full._button(screen, small_font, mouse, buttons, "▼", (rect.right - 38, rect.y + 10, 28, 30), lambda: _scroll_logs(-1), enabled=_LOG_SCROLL > 0)

    footer_height = 72 if market_full._PANEL_TAB == "chat" else 16
    area = pygame.Rect(rect.x + 12, rect.y + 52, rect.width - 24, max(30, rect.height - 52 - footer_height))
    if market_full._PANEL_TAB == "logs":
        _draw_logs_fixed(screen, small_font, session, area)
        return

    _draw_chat_fixed(screen, small_font, session, area)

    sender = session.players[market_full._CHAT_SENDER]
    sender_y = rect.bottom - 62
    sender_text = market_full._fit(small_font, f"Pisze: {sender.get('name', 'Gracz')}", rect.width - 168)
    screen.blit(small_font.render(sender_text, True, GOLD), (rect.x + 12, sender_y))
    market_full._button(screen, small_font, mouse, buttons, "‹", (rect.right - 146, sender_y - 4, 30, 28), lambda: market_full._change_sender(session, -1))
    market_full._button(screen, small_font, mouse, buttons, "›", (rect.right - 110, sender_y - 4, 30, 28), lambda: market_full._change_sender(session, 1))

    input_rect = pygame.Rect(rect.x + 12, rect.bottom - 28, rect.width - 88, 22)

    # Klikalny obszar dodajemy bez rysowania przycisku. Poprzednio pusty Button był
    # rysowany PO tekście i przykrywał wpisywane znaki aż do wysłania wiadomości.
    hit_target = market_full.CommButton("", input_rect, market_full._focus_chat)
    buttons.append(hit_target)

    pygame.draw.rect(screen, (24, 27, 30), input_rect, border_radius=5)
    pygame.draw.rect(screen, GOLD if market_full._CHAT_FOCUSED else (74, 77, 79), input_rect, 1, border_radius=5)
    if market_full._CHAT_BUFFER:
        shown = market_full._CHAT_BUFFER + ("|" if market_full._CHAT_FOCUSED else "")
        color = TEXT
    elif market_full._CHAT_FOCUSED:
        shown = "|"
        color = TEXT
    else:
        shown = "Kliknij i napisz…"
        color = MUTED
    screen.blit(
        small_font.render(market_full._fit(small_font, shown, input_rect.width - 8), True, color),
        (input_rect.x + 4, input_rect.y + 2),
    )
    market_full._button(
        screen, small_font, mouse, buttons, "WYŚLIJ",
        (rect.right - 70, rect.bottom - 30, 60, 24),
        lambda: _send_chat_fixed(session),
        enabled=bool(market_full._CHAT_BUFFER.strip()),
    )


def _draw_preparation_fixed(screen, font, small_font, mouse, buttons, session):
    player_index = market_ui._current_preparation_player(session)
    if player_index is None:
        return
    player = session.players[player_index]
    offer = session.public_offer(player_index)
    sw, sh = screen.get_size()

    screen.blit(font.render("Przygotowanie publicznych ofert", True, TEXT), (34, 24))
    ready = len(session.prepared_players)
    counter = small_font.render(f"Oferty gotowe: {ready}/{len(session.players)}", True, GOLD)
    screen.blit(counter, (sw - counter.get_width() - 34, 30))
    subtitle = f"{market_ui._player_label(player, player_index)} — przejdź przez kategorie i przygotuj maksymalnie jedną ofertę."
    screen.blit(small_font.render(market_ui._fit(small_font, subtitle, sw - 68), True, MUTED), (34, 58))

    market_ui._draw_category_tabs(screen, small_font, mouse, buttons, 92, market_ui._PREP_CATEGORY, market_ui._set_prep_category)
    content = pygame.Rect(34, 140, sw - 68, sh - 300)
    market_ui._panel(screen, content, alpha=238)

    left = pygame.Rect(content.x + 18, content.y + 18, int(content.width * 0.62), content.height - 36)
    right = pygame.Rect(left.right + 18, content.y + 18, content.right - left.right - 36, content.height - 36)
    pygame.draw.rect(screen, (20, 23, 26), left, border_radius=10)
    pygame.draw.rect(screen, (20, 23, 26), right, border_radius=10)

    market_ui._draw_asset_rows(
        screen,
        small_font,
        mouse,
        buttons,
        player,
        market_ui._PREP_CATEGORY,
        pygame.Rect(left.x + 12, left.y + 12, left.width - 24, left.height - 24),
        offer.draft,
        lambda asset: market_ui._toggle_public_asset(session, player_index, asset),
        lambda name, quantity: market_ui._set_message(session, session.set_public_good_quantity(player_index, name, quantity)),
    )

    screen.blit(font.render("Twoja publiczna oferta", True, TEXT), (right.x + 16, right.y + 15))
    selected = []
    for asset in offer.draft.assets:
        if asset.category == "good":
            selected.append(f"{asset.quantity}x {asset.key}")
            continue
        name = _asset_name(asset, player)
        if asset.category == "item" and asset.source == "equipment":
            name = f"{name} (wyposażone)"
        selected.append(f"{market_ui.CATEGORY_LABELS.get(asset.category, asset.category)}: {name}")

    y = right.y + 56
    if selected:
        draw_lines(screen, small_font, selected[:9], right.x + 16, y, MUTED, line_h=22, max_width=right.width - 32)
    else:
        screen.blit(small_font.render("Nie wybrano jeszcze zawartości.", True, MUTED), (right.x + 16, y))

    price_y = right.bottom - 118
    screen.blit(font.render(f"Cena: {offer.price} Złota", True, GOLD), (right.x + 16, price_y))
    market_ui._button(screen, small_font, mouse, buttons, "−5", (right.x + 16, price_y + 38, 52, 32), lambda: market_ui._set_message(session, session.set_public_price(player_index, offer.price - 5)))
    market_ui._button(screen, small_font, mouse, buttons, "−1", (right.x + 74, price_y + 38, 52, 32), lambda: market_ui._set_message(session, session.set_public_price(player_index, offer.price - 1)))
    market_ui._button(screen, small_font, mouse, buttons, "+1", (right.x + 132, price_y + 38, 52, 32), lambda: market_ui._set_message(session, session.set_public_price(player_index, offer.price + 1)))
    market_ui._button(screen, small_font, mouse, buttons, "+5", (right.x + 190, price_y + 38, 52, 32), lambda: market_ui._set_message(session, session.set_public_price(player_index, offer.price + 5)))

    message_rect = pygame.Rect(34, sh - 142, sw - 68, 48)
    market_ui._panel(screen, message_rect, alpha=215, border=(92, 99, 104))
    screen.blit(small_font.render(market_ui._fit(small_font, session.message, message_rect.width - 20), True, TEXT), (message_rect.x + 10, message_rect.y + 14))

    market_ui._button(screen, font, mouse, buttons, "BRAK OFERTY", (34, sh - 78, 220, 44), lambda: market_ui._set_message(session, session.finalize_public_offer(player_index, no_offer=True)))
    market_ui._button(
        screen,
        font,
        mouse,
        buttons,
        "ZATWIERDŹ OFERTĘ",
        (sw - 294, sh - 78, 260, 44),
        lambda: market_ui._set_message(session, session.finalize_public_offer(player_index)),
        enabled=bool(offer.draft.assets),
    )

    market_ui._draw_equipped_warning(screen, font, small_font, mouse, buttons, session)


def _draw_invitation_fixed(screen, font, small_font, mouse, buttons, session, rect):
    negotiation = session.negotiation
    if negotiation is None:
        return
    initiator = session.players[negotiation.initiator_index]
    partner = session.players[negotiation.partner_index]
    market_ui._panel(screen, rect, alpha=240, border=(180, 134, 67))
    title = f"{initiator.get('name', 'Gracz')} zaprasza {partner.get('name', 'Gracz')} do negocjacji"
    screen.blit(font.render(market_ui._fit(font, title, rect.width - 40), True, TEXT), (rect.x + 20, rect.y + 24))
    screen.blit(small_font.render("Odrzucenie zaproszenia nie zużywa próby aktywnego gracza.", True, MUTED), (rect.x + 20, rect.y + 66))

    # Przyciski są na środku, a nie przy prawej krawędzi pod panelem Czatu.
    button_w = 220
    gap = 28
    total = button_w * 2 + gap
    start = rect.centerx - total // 2
    market_ui._button(screen, font, mouse, buttons, "PRZYJMIJ", (start, rect.bottom - 70, button_w, 42), lambda: market_ui._respond_invitation(session, True))
    market_ui._button(screen, font, mouse, buttons, "ODRZUĆ", (start + button_w + gap, rect.bottom - 70, button_w, 42), lambda: market_ui._respond_invitation(session, False))


def _draw_comm_panel_disabled(*_args, **_kwargs):
    # Ekran końca Rady korzysta z tego samego interaktywnego panelu co reszta Rady.
    # Usuwa to drugi, statyczny Czat widoczny wcześniej pod prawdziwym panelem.
    return None


def _hide_finished_instant_event(*_args, **_kwargs):
    # Karta Natychmiast została już pokazana i zsunęła się ze sceny. Nie dokładamy
    # później kolejnego prostokąta na ekran przygotowania ofert, bo zasłania zakładki.
    return None


def install_council_market_ui_fixes() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    market_ui._draw_preparation = _draw_preparation_fixed
    market_ui._draw_invitation = _draw_invitation_fixed
    market_ui._draw_comm_panel = _draw_comm_panel_disabled

    market_full._draw_chat = _draw_chat_fixed
    market_full._draw_logs = _draw_logs_fixed
    market_full._draw_comm_overlay = _draw_comm_overlay_fixed
    market_full._send_chat = _send_chat_fixed

    council_flow._cover_finished_instant_event = _hide_finished_instant_event
    _INSTALLED = True
