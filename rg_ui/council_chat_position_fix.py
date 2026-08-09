from __future__ import annotations

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_ui import council_market as market_ui
from rg_ui import council_market_ui_fixes as ui_fixes

_INSTALLED = False


def _comm_rect_moved(screen, session):
    """Przesuwa panel Czatu, gdy kolidowałby z decyzją o zaproszeniu."""
    sw, sh = screen.get_size()

    if session.stage == "departure":
        left = pygame.Rect(34, 138, int((sw - 86) * 0.56), sh - 190)
        return pygame.Rect(left.right + 18, 138, sw - left.right - 52, sh - 190)

    width = min(390, max(330, sw // 4))
    height = 250

    negotiation = getattr(session, "negotiation", None)
    if (
        session.stage == "turns"
        and getattr(session, "turn_phase", None) == "loose"
        and negotiation is not None
        and getattr(negotiation, "state", None) == "invited"
    ):
        # Zaproszenie ma ważne akcje przy dolnej krawędzi. Zamiast ruszać
        # PRZYJMIJ/ODRZUĆ przenosimy pomocniczy Czat do prawego górnego rogu.
        return pygame.Rect(sw - width - 18, 124, width, height)

    return pygame.Rect(sw - width - 18, sh - height - 18, width, height)


def _draw_invitation_normal(screen, font, small_font, mouse, buttons, session, rect):
    negotiation = session.negotiation
    if negotiation is None:
        return

    initiator = session.players[negotiation.initiator_index]
    partner = session.players[negotiation.partner_index]
    market_ui._panel(screen, rect, alpha=240, border=(180, 134, 67))

    title = f"{initiator.get('name', 'Gracz')} zaprasza {partner.get('name', 'Gracz')} do negocjacji"
    screen.blit(
        font.render(market_ui._fit(font, title, rect.width - 40), True, TEXT),
        (rect.x + 20, rect.y + 24),
    )
    screen.blit(
        small_font.render(
            "Odrzucenie zaproszenia nie zużywa próby aktywnego gracza.",
            True,
            MUTED,
        ),
        (rect.x + 20, rect.y + 66),
    )

    # Przywracamy naturalny układ akcji po przeciwnych stronach okna.
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


def install_council_chat_position_fix() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    # _draw_comm_overlay_fixed rozwiązuje nazwę _comm_rect z modułu w czasie
    # rysowania, więc podmiana po instalacji pozostałych fixów jest bezpieczna.
    ui_fixes._comm_rect = _comm_rect_moved
    market_ui._draw_invitation = _draw_invitation_normal
    _INSTALLED = True
