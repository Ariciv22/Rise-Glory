from __future__ import annotations

import math

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_engine.council_market import MAX_LOOSE_NEGOTIATIONS
from rg_ui import council_market as market_ui
from rg_ui import council_market_ui_fixes as ui_fixes

_INSTALLED = False

LEFT_MARGIN = 24
RIGHT_MARGIN = 24
CHAT_GAP = 16
CONTENT_TOP = 124
BOTTOM_MARGIN = 18
FOOTER_RESERVED = 122


def _chat_width(screen) -> int:
    sw = screen.get_width()
    return max(300, min(360, int(sw * 0.19)))


def _chat_rect(screen, _session=None) -> pygame.Rect:
    sw, sh = screen.get_size()
    width = _chat_width(screen)
    top = 92
    return pygame.Rect(sw - RIGHT_MARGIN - width, top, width, max(260, sh - top - BOTTOM_MARGIN))


def _main_right(screen) -> int:
    return _chat_rect(screen).x - CHAT_GAP


def _main_width(screen) -> int:
    return max(420, _main_right(screen) - LEFT_MARGIN)


def _draw_turn_header_docked(screen, font, small_font, session):
    active_index = session.active_player_index
    active = session.players[active_index] if active_index is not None else {"name": "—"}
    phase = "PUBLICZNE OFERTY" if session.turn_phase == "public" else "LUŹNY HANDEL"

    screen.blit(font.render(f"Kolej: {active.get('name', 'Gracz')}", True, TEXT), (LEFT_MARGIN, 22))
    screen.blit(small_font.render(phase, True, GOLD), (LEFT_MARGIN, 54))

    finished = session.turn_position
    ready = small_font.render(f"Gotowi: {finished}/{len(session.players)}", True, MUTED)
    screen.blit(ready, (max(LEFT_MARGIN, _main_right(screen) - ready.get_width()), 30))


def _offer_grid(screen, font, small_font, mouse, buttons, session, area):
    cards = len(session.players)
    if cards <= 0:
        return

    columns = min(cards, 3 if area.width >= 930 else 2)
    rows = int(math.ceil(cards / columns))
    gap = 12
    card_w = max(180, (area.width - gap * (columns - 1)) // columns)
    card_h = max(150, min(230, (area.height - gap * (rows - 1)) // rows))

    total_h = rows * card_h + gap * (rows - 1)
    start_y = area.y + max(0, (area.height - total_h) // 2)

    for index in range(cards):
        row = index // columns
        col = index % columns
        rect = pygame.Rect(
            area.x + col * (card_w + gap),
            start_y + row * (card_h + gap),
            card_w,
            card_h,
        )
        market_ui._offer_card(screen, font, small_font, mouse, buttons, session, index, rect, clickable=True)


def _draw_public_turn_docked(screen, font, small_font, mouse, buttons, session):
    sw, sh = screen.get_size()
    main_w = _main_width(screen)
    _draw_turn_header_docked(screen, font, small_font, session)

    info = "Możesz zaakceptować maksymalnie jedną publiczną ofertę albo świadomie zrezygnować."
    screen.blit(small_font.render(market_ui._fit(small_font, info, main_w), True, MUTED), (LEFT_MARGIN, 82))

    cards_area = pygame.Rect(LEFT_MARGIN, CONTENT_TOP, main_w, max(220, sh - CONTENT_TOP - 188))
    _offer_grid(screen, font, small_font, mouse, buttons, session, cards_area)

    msg = pygame.Rect(LEFT_MARGIN, sh - 150, main_w, 48)
    market_ui._panel(screen, msg, alpha=215, border=(92, 99, 104))
    screen.blit(
        small_font.render(market_ui._fit(small_font, session.message, msg.width - 20), True, TEXT),
        (msg.x + 10, msg.y + 14),
    )

    button_w = min(360, main_w - 40)
    market_ui._button(
        screen,
        font,
        mouse,
        buttons,
        "NIE KUPUJĘ ŻADNEJ OFERTY",
        (LEFT_MARGIN + (main_w - button_w) // 2, sh - 84, button_w, 44),
        lambda: market_ui._set_message(session, session.skip_public_purchase(session.active_player_index)),
    )
    market_ui._draw_public_purchase_modal(screen, font, small_font, mouse, buttons, session)


def _draw_category_tabs_in_rect(screen, small_font, mouse, buttons, rect, active, callback):
    categories = ("quest", "item", "helper", "good")
    gap = 8
    width = min(142, max(92, (rect.width - gap * 3) // 4))
    total = width * 4 + gap * 3
    start = rect.centerx - total // 2
    for index, category in enumerate(categories):
        market_ui._button(
            screen,
            small_font,
            mouse,
            buttons,
            market_ui.CATEGORY_LABELS[category],
            (start + index * (width + gap), rect.y, width, 34),
            lambda c=category: callback(c),
            active=active == category,
        )


def _draw_negotiation_docked(screen, font, small_font, mouse, buttons, session, rect):
    negotiation = session.negotiation
    if negotiation is None:
        return

    if negotiation.state == "invited":
        market_ui._draw_invitation(screen, font, small_font, mouse, buttons, session, rect)
        return

    if negotiation.state in {"completed", "cancelled", "rejected", "expired", "failed"}:
        market_ui._panel(screen, rect, alpha=240)
        screen.blit(font.render("Negocjacja zakończona", True, TEXT), (rect.x + 24, rect.y + 24))
        from rg_ui.common import draw_lines, wrap

        draw_lines(
            screen,
            small_font,
            wrap(small_font, negotiation.last_message or session.message, rect.width - 48),
            rect.x + 24,
            rect.y + 76,
            MUTED,
            line_h=22,
        )
        market_ui._button(
            screen,
            font,
            mouse,
            buttons,
            "KONTYNUUJ",
            (rect.centerx - 130, rect.bottom - 70, 260, 42),
            lambda: market_ui._continue_after_negotiation(session),
        )
        return

    tabs_rect = pygame.Rect(rect.x, rect.y + 4, rect.width, 34)
    _draw_category_tabs_in_rect(
        screen,
        small_font,
        mouse,
        buttons,
        tabs_rect,
        market_ui._NEG_CATEGORY,
        market_ui._set_neg_category,
    )

    top = rect.y + 48
    gap = 16
    half = (rect.width - gap) // 2
    left = pygame.Rect(rect.x, top, half, rect.height - 158)
    right = pygame.Rect(left.right + gap, top, half, rect.height - 158)
    market_ui._draw_negotiation_side(
        screen, font, small_font, mouse, buttons, session, negotiation.initiator_index, left
    )
    market_ui._draw_negotiation_side(
        screen, font, small_font, mouse, buttons, session, negotiation.partner_index, right
    )

    controls_y = rect.bottom - 98
    if negotiation.state == "open":
        for offset, player_index in enumerate(negotiation.participants):
            accepted = player_index in negotiation.preliminary_acceptance
            label = "WSTĘPNIE ZAAKCEPTOWANO" if accepted else "WSTĘPNIE AKCEPTUJĘ"
            x = rect.x + 16 if offset == 0 else rect.centerx + 8
            market_ui._button(
                screen,
                small_font,
                mouse,
                buttons,
                label,
                (x, controls_y, half - 24, 36),
                lambda i=player_index: market_ui._set_message(session, session.preliminarily_accept(i)),
                active=accepted,
            )
    else:
        for offset, player_index in enumerate(negotiation.participants):
            accepted = player_index in negotiation.final_acceptance
            label = "AKCEPTOWANO DEFIN.'" if accepted else "AKCEPTUJ DEFINIT."
            x = rect.x + 16 if offset == 0 else rect.centerx + 8
            market_ui._button(
                screen,
                small_font,
                mouse,
                buttons,
                label,
                (x, controls_y, half - 24, 36),
                lambda i=player_index: market_ui._definitive_accept(session, i),
                active=accepted,
            )
        market_ui._button(
            screen,
            small_font,
            mouse,
            buttons,
            "COFNIJ DO NEGOCJACJI",
            (rect.centerx - 125, controls_y + 44, 250, 34),
            lambda: market_ui._set_message(
                session, session.rollback_to_negotiation(negotiation.initiator_index)
            ),
        )

    market_ui._button(
        screen,
        small_font,
        mouse,
        buttons,
        "ZAKOŃCZ BEZ TRANSAKCJI",
        (rect.x + 16, rect.bottom - 42, 230, 32),
        lambda: market_ui._set_message(session, session.cancel_negotiation(negotiation.initiator_index)),
    )
    market_ui._draw_neg_discard_modal(screen, font, small_font, mouse, buttons, session)


def _draw_loose_turn_docked(screen, font, small_font, mouse, buttons, session):
    sw, sh = screen.get_size()
    main_w = _main_width(screen)
    _draw_turn_header_docked(screen, font, small_font, session)

    remaining = session.remaining_negotiations()
    screen.blit(
        font.render(f"Pozostało: {remaining} z {MAX_LOOSE_NEGOTIATIONS} negocjacji", True, GOLD),
        (LEFT_MARGIN, 84),
    )

    content = pygame.Rect(LEFT_MARGIN, CONTENT_TOP, main_w, max(240, sh - CONTENT_TOP - 176))
    negotiation = session.negotiation
    if negotiation is not None and negotiation.state in {
        "invited",
        "open",
        "locked",
        "completed",
        "cancelled",
        "rejected",
        "expired",
        "failed",
    }:
        _draw_negotiation_docked(screen, font, small_font, mouse, buttons, session, content)
    else:
        market_ui._panel(screen, content, alpha=235)
        screen.blit(font.render("Wybierz gracza do luźnego handlu", True, TEXT), (content.x + 24, content.y + 22))
        y = content.y + 70
        for index, player in enumerate(session.players):
            if index == session.active_player_index:
                continue
            row = pygame.Rect(content.x + 24, y, content.width - 48, 50)
            pygame.draw.rect(screen, (27, 31, 35), row, border_radius=9)
            pygame.draw.rect(screen, player.get("player_color", GOLD), row, 1, border_radius=9)
            screen.blit(
                font.render(
                    market_ui._fit(font, market_ui._player_label(player, index), row.width - 190),
                    True,
                    TEXT,
                ),
                (row.x + 12, row.y + 12),
            )
            market_ui._button(
                screen,
                small_font,
                mouse,
                buttons,
                "NEGOCJUJ",
                (row.right - 150, row.y + 8, 136, 34),
                lambda i=index: market_ui._invite_player(session, i),
                enabled=remaining > 0,
            )
            y += 58

        if remaining <= 0:
            screen.blit(
                small_font.render(
                    "Wykorzystano obie próby. Możesz już tylko zakończyć swoją turę.",
                    True,
                    MUTED,
                ),
                (content.x + 24, content.bottom - 42),
            )

    msg = pygame.Rect(LEFT_MARGIN, sh - 156, main_w, 48)
    market_ui._panel(screen, msg, alpha=215, border=(92, 99, 104))
    screen.blit(
        small_font.render(market_ui._fit(small_font, session.message, msg.width - 20), True, TEXT),
        (msg.x + 10, msg.y + 14),
    )

    can_end, _ = session.can_end_active_turn()
    button_w = min(420, main_w - 40)
    market_ui._button(
        screen,
        font,
        mouse,
        buttons,
        "ZAKOŃCZ SWOJĄ TURĘ W RADZIE",
        (LEFT_MARGIN + (main_w - button_w) // 2, sh - 88, button_w, 46),
        lambda: market_ui._try_end_turn(session),
        enabled=can_end,
    )
    market_ui._draw_end_turn_confirm(screen, font, small_font, mouse, buttons, session)


def _draw_summary_docked(screen, font, small_font, mouse, buttons, session):
    sh = screen.get_height()
    main_w = _main_width(screen)

    screen.blit(font.render("Podsumowanie Rady Bohaterów", True, TEXT), (LEFT_MARGIN, 24))
    subtitle = "Pokazane są wyłącznie transakcje, które faktycznie doszły do skutku."
    screen.blit(small_font.render(market_ui._fit(small_font, subtitle, main_w), True, MUTED), (LEFT_MARGIN, 58))

    panel = pygame.Rect(LEFT_MARGIN, 100, main_w, max(220, sh - 210))
    market_ui._panel(screen, panel, alpha=238)
    market_ui._draw_trade_log_table(
        screen,
        font,
        small_font,
        session,
        pygame.Rect(panel.x + 18, panel.y + 18, panel.width - 36, panel.height - 36),
        session.successful_trade_logs(),
    )

    button_w = min(340, main_w - 40)
    market_ui._button(
        screen,
        font,
        mouse,
        buttons,
        "RADA ZAKOŃCZONA",
        (LEFT_MARGIN + (main_w - button_w) // 2, sh - 82, button_w, 44),
        lambda: market_ui._set_message(session, session.continue_from_summary()),
    )


def _draw_departure_docked(screen, font, small_font, mouse, buttons, session):
    sh = screen.get_height()
    main_w = _main_width(screen)

    screen.blit(font.render("Rada zakończona", True, TEXT), (LEFT_MARGIN, 24))
    story = "Rozmowy cichną, sakwy zostają zapięte, a bohaterowie szykują się do powrotu na szlak."
    screen.blit(small_font.render(market_ui._fit(small_font, story, main_w), True, MUTED), (LEFT_MARGIN, 58))

    count = len(session.departure_ready)
    screen.blit(
        font.render(f"Gotowi do opuszczenia Rady: {count}/{len(session.players)}", True, GOLD),
        (LEFT_MARGIN, 92),
    )

    panel = pygame.Rect(LEFT_MARGIN, 138, main_w, max(220, sh - 190))
    market_ui._panel(screen, panel, alpha=236)
    y = panel.y + 18
    for index, player in enumerate(session.players):
        row = pygame.Rect(panel.x + 16, y, panel.width - 32, 48)
        ready = index in session.departure_ready
        pygame.draw.rect(screen, (43, 57, 43) if ready else (29, 33, 36), row, border_radius=8)
        pygame.draw.rect(screen, (103, 145, 92) if ready else (74, 76, 78), row, 1, border_radius=8)
        screen.blit(
            small_font.render(market_ui._fit(small_font, player.get("name", "Gracz"), row.width - 190), True, TEXT),
            (row.x + 10, row.y + 15),
        )
        if ready:
            label = small_font.render("Gotowy ✓", True, (176, 221, 155))
            screen.blit(label, (row.right - label.get_width() - 12, row.y + 15))
        else:
            market_ui._button(
                screen,
                small_font,
                mouse,
                buttons,
                "GOTOWY DO WYJŚCIA",
                (row.right - 176, row.y + 8, 164, 32),
                lambda i=index: market_ui._confirm_departure(session, i),
            )
        y += 56


def _draw_invitation_docked(screen, font, small_font, mouse, buttons, session, rect):
    negotiation = session.negotiation
    if negotiation is None:
        return

    initiator = session.players[negotiation.initiator_index]
    partner = session.players[negotiation.partner_index]
    market_ui._panel(screen, rect, alpha=240, border=(180, 134, 67))

    title = f"{initiator.get('name', 'Gracz')} zaprasza {partner.get('name', 'Gracz')} do negocjacji"
    screen.blit(font.render(market_ui._fit(font, title, rect.width - 40), True, TEXT), (rect.x + 20, rect.y + 24))
    screen.blit(
        small_font.render("Odrzucenie zaproszenia nie zużywa próby aktywnego gracza.", True, MUTED),
        (rect.x + 20, rect.y + 66),
    )

    market_ui._button(
        screen,
        font,
        mouse,
        buttons,
        "PRZYJMIJ",
        (rect.x + 70, rect.bottom - 70, 220, 42),
        lambda: market_ui._respond_invitation(session, True),
    )
    market_ui._button(
        screen,
        font,
        mouse,
        buttons,
        "ODRZUĆ",
        (rect.right - 290, rect.bottom - 70, 220, 42),
        lambda: market_ui._respond_invitation(session, False),
    )


def install_council_docked_layout() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    # Czat jest stałą prawą sekcją ekranu. Renderer z ui_fixes korzysta z tej
    # funkcji przy każdym rysowaniu, więc panel nigdy nie wychodzi poza okno i
    # nie przykrywa interakcji w lewej części Rady.
    ui_fixes._comm_rect = _chat_rect

    market_ui._draw_turn_header = _draw_turn_header_docked
    market_ui._draw_public_turn = _draw_public_turn_docked
    market_ui._draw_loose_turn = _draw_loose_turn_docked
    market_ui._draw_negotiation = _draw_negotiation_docked
    market_ui._draw_invitation = _draw_invitation_docked
    market_ui._draw_summary = _draw_summary_docked
    market_ui._draw_departure = _draw_departure_docked

    _INSTALLED = True
