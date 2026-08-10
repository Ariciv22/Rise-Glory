from __future__ import annotations

from typing import Callable

import pygame

from rg_core.data import BG, GOLD, MUTED, TEXT
from rg_engine.council import AssetRef, TradeSide, available_assets
from rg_engine.council_market import CouncilMarketSession, MAX_LOOSE_NEGOTIATIONS
from rg_engine.world import registered_players
from rg_ui.common import Button, draw_lines, wrap

_SESSION: CouncilMarketSession | None = None
_SESSION_ROUND: int | None = None
_PREP_CATEGORY = "quest"
_NEG_CATEGORY = "quest"
_EQUIPPED_WARNING: tuple[int, AssetRef] | None = None
_PUBLIC_PURCHASE_SELLER: int | None = None
_PUBLIC_DISCARD_SELECTION: list[AssetRef] = []
_NEG_DISCARD_PLAYER: int | None = None
_NEG_DISCARD_SELECTION: list[AssetRef] = []
_END_TURN_CONFIRM = False
_COMM_TAB = "chat"

CATEGORY_LABELS = {
    "quest": "Questy",
    "item": "Przedmioty",
    "helper": "Pomocnicy",
    "good": "Towary",
}


class MarketButton(Button):
    def __init__(self, text, rect, callback: Callable[[], object] | None = None, enabled=True):
        super().__init__(text, "council_noop", rect)
        self.callback = callback
        self.enabled = bool(enabled)

    def draw(self, screen, font, mouse_pos, active=False):
        if self.enabled:
            super().draw(screen, font, mouse_pos, active=active)
            return
        pygame.draw.rect(screen, (31, 34, 37), self.rect, border_radius=10)
        pygame.draw.rect(screen, (72, 75, 78), self.rect, 1, border_radius=10)
        if self.text:
            label = font.render(self.text, True, (112, 112, 112))
            screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        if not self.enabled or not self.rect.collidepoint(pos):
            return False
        result = self.callback() if self.callback else None
        self.action = result if isinstance(result, str) else "council_noop"
        return True


def reset_council_market() -> None:
    global _SESSION, _SESSION_ROUND, _EQUIPPED_WARNING, _PUBLIC_PURCHASE_SELLER
    global _PUBLIC_DISCARD_SELECTION, _NEG_DISCARD_PLAYER, _NEG_DISCARD_SELECTION, _END_TURN_CONFIRM
    _SESSION = None
    _SESSION_ROUND = None
    _EQUIPPED_WARNING = None
    _PUBLIC_PURCHASE_SELLER = None
    _PUBLIC_DISCARD_SELECTION = []
    _NEG_DISCARD_PLAYER = None
    _NEG_DISCARD_SELECTION = []
    _END_TURN_CONFIRM = False


def _session(round_number: int) -> CouncilMarketSession:
    global _SESSION, _SESSION_ROUND
    players = registered_players()
    if _SESSION is None or _SESSION_ROUND != int(round_number) or _SESSION.players != players:
        _SESSION = CouncilMarketSession(players)
        _SESSION_ROUND = int(round_number)
    return _SESSION


def _load_background(screen):
    from rg_ui import council as legacy_council

    background = legacy_council._load_background(screen.get_size())
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BG)


def _panel(screen, rect, alpha=232, border=GOLD):
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, (12, 15, 18, alpha), surface.get_rect(), border_radius=12)
    pygame.draw.rect(surface, border, surface.get_rect(), 2, border_radius=12)
    screen.blit(surface, rect.topleft)


def _button(screen, font, mouse, buttons, text, rect, callback, active=False, enabled=True):
    button = MarketButton(text, rect, callback, enabled=enabled)
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


def _player_label(player, index):
    return f"Gracz {player.get('player_number', index + 1)} — {player.get('name', 'Bohater')}"


def _identity(asset: AssetRef):
    return asset.category, asset.source, str(asset.key)


def _side_has_asset(side: TradeSide, asset: AssetRef) -> bool:
    return any(_identity(value) == _identity(asset) for value in side.assets)


def _good_quantity(side: TradeSide, name: str) -> int:
    return sum(
        max(0, int(asset.quantity or 0))
        for asset in side.assets
        if asset.category == "good" and str(asset.key) == str(name)
    )


def _current_preparation_player(session: CouncilMarketSession):
    for index, offer in enumerate(session.public_offers):
        if offer.status == "draft":
            return index
    return None


def _set_prep_category(category):
    global _PREP_CATEGORY
    _PREP_CATEGORY = category


def _set_neg_category(category):
    global _NEG_CATEGORY
    _NEG_CATEGORY = category


def _set_message(session, result):
    if isinstance(result, tuple) and len(result) >= 2:
        session.message = str(result[1])
    return None


def _toggle_public_asset(session, player_index, asset):
    global _EQUIPPED_WARNING
    offer = session.public_offer(player_index)
    if _side_has_asset(offer.draft, asset):
        return _set_message(session, session.toggle_public_asset(player_index, asset))
    if asset.category == "item" and asset.source == "equipment":
        _EQUIPPED_WARNING = (player_index, asset)
        return None
    return _set_message(session, session.toggle_public_asset(player_index, asset))


def _confirm_equipped_public(session):
    global _EQUIPPED_WARNING
    if _EQUIPPED_WARNING is None:
        return None
    player_index, asset = _EQUIPPED_WARNING
    result = session.toggle_public_asset(player_index, asset)
    _EQUIPPED_WARNING = None
    return _set_message(session, result)


def _cancel_equipped_warning():
    global _EQUIPPED_WARNING
    _EQUIPPED_WARNING = None


def _draw_category_tabs(screen, small_font, mouse, buttons, y, active, callback):
    sw = screen.get_width()
    width = 142
    gap = 10
    total = width * 4 + gap * 3
    start = sw // 2 - total // 2
    for index, category in enumerate(("quest", "item", "helper", "good")):
        _button(
            screen,
            small_font,
            mouse,
            buttons,
            CATEGORY_LABELS[category],
            (start + index * (width + gap), y, width, 34),
            lambda c=category: callback(c),
            active=active == category,
        )


def _draw_asset_rows(
    screen,
    small_font,
    mouse,
    buttons,
    player,
    category,
    rect,
    side: TradeSide,
    toggle_callback,
    good_callback,
    disabled_sources=None,
):
    disabled_sources = set(disabled_sources or [])
    assets = available_assets(player, category)
    if category == "item" and disabled_sources:
        assets = [entry for entry in assets if entry[0].source not in disabled_sources]
    visible = assets[:7]
    if not visible:
        screen.blit(small_font.render("Brak elementów w tej kategorii.", True, MUTED), (rect.x + 10, rect.y + 10))
        return

    row_h = 42
    y = rect.y
    for asset, name, detail in visible:
        selected = _side_has_asset(side, asset) if category != "good" else _good_quantity(side, name) > 0
        row = pygame.Rect(rect.x, y, rect.width, row_h)
        pygame.draw.rect(screen, (48, 57, 48) if selected else (27, 31, 35), row, border_radius=8)
        pygame.draw.rect(screen, (113, 142, 99) if selected else (70, 74, 78), row, 1, border_radius=8)
        screen.blit(small_font.render(_fit(small_font, name, row.width - 170), True, TEXT), (row.x + 9, row.y + 5))
        if detail:
            screen.blit(small_font.render(_fit(small_font, detail, row.width - 170), True, MUTED), (row.x + 9, row.y + 23))

        if category == "good":
            quantity = _good_quantity(side, name)
            total = max(0, int(asset.quantity or 0))
            screen.blit(small_font.render(f"{quantity}/{total}", True, TEXT), (row.right - 118, row.y + 12))
            _button(screen, small_font, mouse, buttons, "−", (row.right - 64, row.y + 6, 26, 30), lambda n=name, q=quantity: good_callback(n, q - 1))
            _button(screen, small_font, mouse, buttons, "+", (row.right - 32, row.y + 6, 26, 30), lambda n=name, q=quantity: good_callback(n, q + 1))
        else:
            _button(
                screen,
                small_font,
                mouse,
                buttons,
                "✓" if selected else "+",
                (row.right - 42, row.y + 6, 32, 30),
                lambda a=asset: toggle_callback(a),
                active=selected,
            )
        y += row_h + 5


def _draw_equipped_warning(screen, font, small_font, mouse, buttons, session):
    if _EQUIPPED_WARNING is None:
        return
    player_index, asset = _EQUIPPED_WARNING
    player = session.players[player_index]
    item = (player.get("equipment", {}) or {}).get(str(asset.key)) or {}
    item_name = item.get("name", "Wyposażony przedmiot") if isinstance(item, dict) else str(item)
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 190))
    screen.blit(shade, (0, 0))
    sw, sh = screen.get_size()
    panel = pygame.Rect(sw // 2 - 360, sh // 2 - 180, 720, 360)
    _panel(screen, panel, alpha=250, border=(188, 126, 70))
    screen.blit(font.render("Wyposażony przedmiot", True, TEXT), (panel.x + 28, panel.y + 28))
    lines = wrap(
        small_font,
        f"{item_name} jest aktualnie wyposażony. Po zatwierdzeniu publicznej oferty zostanie zdjęty z bohatera. Po zakończeniu transakcji — niezależnie od tego, czy oferta zostanie sprzedana — musisz założyć go ponownie samodzielnie.",
        panel.width - 56,
    )
    draw_lines(screen, small_font, lines, panel.x + 28, panel.y + 84, MUTED, line_h=24)
    _button(screen, font, mouse, buttons, "DODAJ DO OFERTY", (panel.x + 55, panel.bottom - 82, 280, 46), lambda: _confirm_equipped_public(session))
    _button(screen, font, mouse, buttons, "ANULUJ", (panel.right - 285, panel.bottom - 82, 230, 46), _cancel_equipped_warning)


def _draw_preparation(screen, font, small_font, mouse, buttons, session):
    player_index = _current_preparation_player(session)
    if player_index is None:
        return
    player = session.players[player_index]
    offer = session.public_offer(player_index)
    sw, sh = screen.get_size()

    screen.blit(font.render("Przygotowanie publicznych ofert", True, TEXT), (34, 24))
    ready = len(session.prepared_players)
    counter = small_font.render(f"Oferty gotowe: {ready}/{len(session.players)}", True, GOLD)
    screen.blit(counter, (sw - counter.get_width() - 34, 30))
    subtitle = f"{_player_label(player, player_index)} — przejdź przez kategorie i przygotuj maksymalnie jedną ofertę."
    screen.blit(small_font.render(_fit(small_font, subtitle, sw - 68), True, MUTED), (34, 58))

    _draw_category_tabs(screen, small_font, mouse, buttons, 92, _PREP_CATEGORY, _set_prep_category)
    content = pygame.Rect(34, 140, sw - 68, sh - 300)
    _panel(screen, content, alpha=238)

    left = pygame.Rect(content.x + 18, content.y + 18, int(content.width * 0.62), content.height - 36)
    right = pygame.Rect(left.right + 18, content.y + 18, content.right - left.right - 36, content.height - 36)
    pygame.draw.rect(screen, (20, 23, 26), left, border_radius=10)
    pygame.draw.rect(screen, (20, 23, 26), right, border_radius=10)

    _draw_asset_rows(
        screen,
        small_font,
        mouse,
        buttons,
        player,
        _PREP_CATEGORY,
        pygame.Rect(left.x + 12, left.y + 12, left.width - 24, left.height - 24),
        offer.draft,
        lambda asset: _toggle_public_asset(session, player_index, asset),
        lambda name, quantity: _set_message(session, session.set_public_good_quantity(player_index, name, quantity)),
    )

    screen.blit(font.render("Twoja publiczna oferta", True, TEXT), (right.x + 16, right.y + 15))
    selected = []
    for asset in offer.draft.assets:
        if asset.category == "good":
            selected.append(f"{asset.quantity}x {asset.key}")
        else:
            selected.append(f"{CATEGORY_LABELS.get(asset.category, asset.category)}: {asset.source}")
    y = right.y + 56
    if selected:
        draw_lines(screen, small_font, selected[:9], right.x + 16, y, MUTED, line_h=22, max_width=right.width - 32)
    else:
        screen.blit(small_font.render("Nie wybrano jeszcze zawartości.", True, MUTED), (right.x + 16, y))
    price_y = right.bottom - 118
    screen.blit(font.render(f"Cena: {offer.price} Złota", True, GOLD), (right.x + 16, price_y))
    _button(screen, small_font, mouse, buttons, "−5", (right.x + 16, price_y + 38, 52, 32), lambda: _set_message(session, session.set_public_price(player_index, offer.price - 5)))
    _button(screen, small_font, mouse, buttons, "−1", (right.x + 74, price_y + 38, 52, 32), lambda: _set_message(session, session.set_public_price(player_index, offer.price - 1)))
    _button(screen, small_font, mouse, buttons, "+1", (right.x + 132, price_y + 38, 52, 32), lambda: _set_message(session, session.set_public_price(player_index, offer.price + 1)))
    _button(screen, small_font, mouse, buttons, "+5", (right.x + 190, price_y + 38, 52, 32), lambda: _set_message(session, session.set_public_price(player_index, offer.price + 5)))

    message_rect = pygame.Rect(34, sh - 142, sw - 68, 48)
    _panel(screen, message_rect, alpha=215, border=(92, 99, 104))
    screen.blit(small_font.render(_fit(small_font, session.message, message_rect.width - 20), True, TEXT), (message_rect.x + 10, message_rect.y + 14))

    _button(screen, font, mouse, buttons, "BRAK OFERTY", (34, sh - 78, 220, 44), lambda: _set_message(session, session.finalize_public_offer(player_index, no_offer=True)))
    _button(
        screen,
        font,
        mouse,
        buttons,
        "ZATWIERDŹ OFERTĘ",
        (sw - 294, sh - 78, 260, 44),
        lambda: _set_message(session, session.finalize_public_offer(player_index)),
        enabled=bool(offer.draft.assets),
    )

    _draw_equipped_warning(screen, font, small_font, mouse, buttons, session)


def _offer_card(screen, font, small_font, mouse, buttons, session, player_index, rect, clickable=False):
    player = session.players[player_index]
    offer = session.public_offer(player_index)
    active = player_index == session.active_player_index
    border = player.get("player_color", GOLD) if active else GOLD
    _panel(screen, rect, alpha=225, border=border)
    screen.blit(font.render(_fit(font, player.get("name", "Gracz"), rect.width - 24), True, TEXT), (rect.x + 12, rect.y + 10))
    status = {
        "none": "Brak oferty",
        "sold": "SPRZEDANA",
        "expired": "Wygasła",
        "revealed": f"{offer.price} Złota",
    }.get(offer.status, offer.status)
    screen.blit(small_font.render(status, True, GOLD if offer.status == "revealed" else MUTED), (rect.x + 12, rect.y + 38))
    summary = offer.summary()
    draw_lines(screen, small_font, wrap(small_font, summary, rect.width - 24)[:3], rect.x + 12, rect.y + 64, MUTED, line_h=19)
    if clickable and offer.status == "revealed" and player_index != session.active_player_index:
        _button(screen, small_font, mouse, buttons, "PODGLĄD / KUP", (rect.x + 12, rect.bottom - 36, rect.width - 24, 28), lambda i=player_index: _open_public_purchase(i))


def _open_public_purchase(seller_index):
    global _PUBLIC_PURCHASE_SELLER, _PUBLIC_DISCARD_SELECTION
    _PUBLIC_PURCHASE_SELLER = int(seller_index)
    _PUBLIC_DISCARD_SELECTION = []


def _close_public_purchase():
    global _PUBLIC_PURCHASE_SELLER, _PUBLIC_DISCARD_SELECTION
    _PUBLIC_PURCHASE_SELLER = None
    _PUBLIC_DISCARD_SELECTION = []


def _discard_selected(asset):
    return any(_identity(value) == _identity(asset) for value in _PUBLIC_DISCARD_SELECTION)


def _toggle_public_discard(asset):
    global _PUBLIC_DISCARD_SELECTION
    current = next((value for value in _PUBLIC_DISCARD_SELECTION if _identity(value) == _identity(asset)), None)
    if current:
        _PUBLIC_DISCARD_SELECTION.remove(current)
    else:
        _PUBLIC_DISCARD_SELECTION.append(asset)


def _set_public_discard_good(name, quantity):
    global _PUBLIC_DISCARD_SELECTION
    _PUBLIC_DISCARD_SELECTION = [
        asset for asset in _PUBLIC_DISCARD_SELECTION
        if not (asset.category == "good" and str(asset.key) == str(name))
    ]
    if quantity > 0:
        _PUBLIC_DISCARD_SELECTION.append(AssetRef("good", "goods", str(name), int(quantity)))


def _buy_selected_public_offer(session):
    global _PUBLIC_PURCHASE_SELLER
    if _PUBLIC_PURCHASE_SELLER is None:
        return None
    result = session.buy_public_offer(session.active_player_index, _PUBLIC_PURCHASE_SELLER, _PUBLIC_DISCARD_SELECTION)
    _set_message(session, result)
    if result[0]:
        _close_public_purchase()
    return None


def _draw_discard_picker(screen, font, small_font, mouse, buttons, player, required, selection, toggle, set_good, rect):
    _panel(screen, rect, alpha=247, border=(184, 104, 78))
    screen.blit(font.render("Przekroczysz limit — wybierz własne elementy do odrzucenia", True, TEXT), (rect.x + 20, rect.y + 16))
    required_text = ", ".join(f"{CATEGORY_LABELS.get(cat, cat)}: {amount}" for cat, amount in required.items())
    screen.blit(small_font.render(_fit(small_font, f"Musisz zrobić miejsce: {required_text}", rect.width - 40), True, (230, 166, 112)), (rect.x + 20, rect.y + 48))
    y = rect.y + 82
    for category, amount in required.items():
        screen.blit(small_font.render(f"{CATEGORY_LABELS.get(category, category)} — wybierz min. {amount}", True, GOLD), (rect.x + 20, y))
        y += 26
        entries = available_assets(player, category)
        if category == "item":
            entries = [entry for entry in entries if entry[0].source == "inventory"]
        for asset, name, _detail in entries[:5]:
            row = pygame.Rect(rect.x + 20, y, rect.width - 40, 34)
            pygame.draw.rect(screen, (31, 34, 37), row, border_radius=7)
            if category == "good":
                current = sum(int(value.quantity or 0) for value in selection if value.category == "good" and str(value.key) == str(name))
                screen.blit(small_font.render(f"{name}: {current}", True, TEXT), (row.x + 8, row.y + 8))
                _button(screen, small_font, mouse, buttons, "−", (row.right - 64, row.y + 3, 26, 28), lambda n=name, q=current: set_good(n, max(0, q - 1)))
                _button(screen, small_font, mouse, buttons, "+", (row.right - 32, row.y + 3, 26, 28), lambda n=name, q=current: set_good(n, q + 1))
            else:
                selected = any(_identity(value) == _identity(asset) for value in selection)
                screen.blit(small_font.render(_fit(small_font, name, row.width - 70), True, TEXT), (row.x + 8, row.y + 8))
                _button(screen, small_font, mouse, buttons, "✓" if selected else "+", (row.right - 38, row.y + 3, 28, 28), lambda a=asset: toggle(a), active=selected)
            y += 38
        y += 8


def _draw_public_purchase_modal(screen, font, small_font, mouse, buttons, session):
    if _PUBLIC_PURCHASE_SELLER is None:
        return
    seller_index = _PUBLIC_PURCHASE_SELLER
    buyer_index = session.active_player_index
    if buyer_index is None:
        return
    offer = session.public_offer(seller_index)
    buyer = session.players[buyer_index]
    seller = session.players[seller_index]
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 190))
    screen.blit(shade, (0, 0))
    sw, sh = screen.get_size()
    panel = pygame.Rect(sw // 2 - 390, sh // 2 - 310, 780, 620)
    _panel(screen, panel, alpha=250)
    screen.blit(font.render(f"Oferta: {seller.get('name', 'Gracz')}", True, TEXT), (panel.x + 24, panel.y + 22))
    screen.blit(font.render(f"Cena: {offer.price} Złota", True, GOLD), (panel.x + 24, panel.y + 58))
    screen.blit(small_font.render(f"Twoje Złoto: {buyer.get('gold', 0)}", True, MUTED), (panel.right - 190, panel.y + 64))
    draw_lines(screen, small_font, wrap(small_font, offer.summary(), panel.width - 48)[:5], panel.x + 24, panel.y + 100, TEXT, line_h=22)

    overflow = session.public_purchase_overflow(buyer_index, seller_index)
    if overflow:
        picker = pygame.Rect(panel.x + 20, panel.y + 205, panel.width - 40, 310)
        _draw_discard_picker(
            screen,
            font,
            small_font,
            mouse,
            buttons,
            buyer,
            overflow,
            _PUBLIC_DISCARD_SELECTION,
            _toggle_public_discard,
            _set_public_discard_good,
            picker,
        )
    else:
        screen.blit(small_font.render("Zakup nie przekracza żadnego limitu miejsca.", True, MUTED), (panel.x + 24, panel.y + 220))

    _button(screen, font, mouse, buttons, "KUP OFERTĘ", (panel.x + 80, panel.bottom - 70, 260, 42), lambda: _buy_selected_public_offer(session), enabled=int(buyer.get("gold", 0) or 0) >= offer.price)
    _button(screen, font, mouse, buttons, "ANULUJ", (panel.right - 300, panel.bottom - 70, 220, 42), _close_public_purchase)


def _draw_turn_header(screen, font, small_font, session):
    active_index = session.active_player_index
    active = session.players[active_index] if active_index is not None else {"name": "—"}
    phase = "PUBLICZNE OFERTY" if session.turn_phase == "public" else "LUŹNY HANDEL"
    screen.blit(font.render(f"Kolej: {active.get('name', 'Gracz')}", True, TEXT), (34, 22))
    screen.blit(small_font.render(phase, True, GOLD), (34, 54))
    finished = session.turn_position
    screen.blit(small_font.render(f"Gotowi: {finished}/{len(session.players)}", True, MUTED), (screen.get_width() - 150, 30))


def _draw_public_turn(screen, font, small_font, mouse, buttons, session):
    sw, sh = screen.get_size()
    _draw_turn_header(screen, font, small_font, session)
    screen.blit(small_font.render("Możesz zaakceptować maksymalnie jedną publiczną ofertę albo świadomie zrezygnować.", True, MUTED), (34, 82))

    cards = len(session.players)
    gap = 12
    card_w = max(180, min(300, (sw - 68 - gap * max(0, cards - 1)) // max(1, cards)))
    total = cards * card_w + gap * max(0, cards - 1)
    start_x = max(34, (sw - total) // 2)
    for index in range(cards):
        rect = pygame.Rect(start_x + index * (card_w + gap), 124, card_w, min(260, sh - 330))
        _offer_card(screen, font, small_font, mouse, buttons, session, index, rect, clickable=True)

    msg = pygame.Rect(34, sh - 150, sw - 68, 48)
    _panel(screen, msg, alpha=215, border=(92, 99, 104))
    screen.blit(small_font.render(_fit(small_font, session.message, msg.width - 20), True, TEXT), (msg.x + 10, msg.y + 14))
    _button(screen, font, mouse, buttons, "NIE KUPUJĘ ŻADNEJ OFERTY", (sw // 2 - 180, sh - 84, 360, 44), lambda: _set_message(session, session.skip_public_purchase(session.active_player_index)))
    _draw_public_purchase_modal(screen, font, small_font, mouse, buttons, session)


def _invite_player(session, partner_index):
    result = session.invite_to_negotiation(partner_index)
    return _set_message(session, result)


def _respond_invitation(session, accept):
    negotiation = session.negotiation
    if negotiation is None:
        return None
    result = session.respond_to_invitation(negotiation.partner_index, accept)
    return _set_message(session, result)


def _continue_after_negotiation(session):
    session.clear_finished_negotiation()
    remaining = session.remaining_negotiations()
    session.message = f"Pozostało: {remaining} z {MAX_LOOSE_NEGOTIATIONS} negocjacji."


def _draw_invitation(screen, font, small_font, mouse, buttons, session, rect):
    negotiation = session.negotiation
    if negotiation is None:
        return
    initiator = session.players[negotiation.initiator_index]
    partner = session.players[negotiation.partner_index]
    _panel(screen, rect, alpha=240, border=(180, 134, 67))
    title = f"{initiator.get('name', 'Gracz')} zaprasza {partner.get('name', 'Gracz')} do negocjacji"
    screen.blit(font.render(_fit(font, title, rect.width - 40), True, TEXT), (rect.x + 20, rect.y + 24))
    screen.blit(small_font.render("Odrzucenie zaproszenia nie zużywa próby aktywnego gracza.", True, MUTED), (rect.x + 20, rect.y + 66))
    _button(screen, font, mouse, buttons, "PRZYJMIJ", (rect.x + 70, rect.bottom - 70, 220, 42), lambda: _respond_invitation(session, True))
    _button(screen, font, mouse, buttons, "ODRZUĆ", (rect.right - 290, rect.bottom - 70, 220, 42), lambda: _respond_invitation(session, False))


def _neg_side_summary(session, player_index):
    side = session.negotiation_side(player_index)
    values = []
    for asset in side.assets:
        values.append(f"{asset.quantity}x {asset.key}" if asset.category == "good" else f"{CATEGORY_LABELS.get(asset.category, asset.category)}")
    if side.gold:
        values.append(f"{side.gold} Złota")
    return ", ".join(values) if values else "—"


def _change_neg_gold(session, player_index, delta):
    side = session.negotiation_side(player_index)
    return _set_message(session, session.set_negotiation_gold(player_index, int(side.gold or 0) + int(delta)))


def _draw_negotiation_side(screen, font, small_font, mouse, buttons, session, player_index, rect):
    negotiation = session.negotiation
    player = session.players[player_index]
    side = negotiation.side_for(player_index)
    _panel(screen, rect, alpha=233, border=player.get("player_color", GOLD))
    screen.blit(font.render(_fit(font, player.get("name", "Gracz"), rect.width - 24), True, TEXT), (rect.x + 12, rect.y + 10))
    screen.blit(small_font.render(f"Oferta: {_fit(small_font, _neg_side_summary(session, player_index), rect.width - 24)}", True, MUTED), (rect.x + 12, rect.y + 40))

    list_rect = pygame.Rect(rect.x + 12, rect.y + 72, rect.width - 24, rect.height - 154)
    editable = negotiation.state == "open"
    if editable:
        _draw_asset_rows(
            screen,
            small_font,
            mouse,
            buttons,
            player,
            _NEG_CATEGORY,
            list_rect,
            side,
            lambda asset: _set_message(session, session.toggle_negotiation_asset(player_index, asset)),
            lambda name, quantity: _set_message(session, session.set_negotiation_good_quantity(player_index, name, quantity)),
        )
    else:
        screen.blit(small_font.render("Oferta zablokowana po dwóch wstępnych akceptacjach.", True, MUTED), (list_rect.x, list_rect.y + 8))

    gold_y = rect.bottom - 68
    screen.blit(small_font.render(f"Złoto: {side.gold}/{player.get('gold', 0)}", True, TEXT), (rect.x + 12, gold_y + 8))
    if editable:
        x = rect.right - 196
        for label, delta in (("−5", -5), ("−1", -1), ("+1", 1), ("+5", 5)):
            _button(screen, small_font, mouse, buttons, label, (x, gold_y, 42, 30), lambda d=delta: _change_neg_gold(session, player_index, d))
            x += 46


def _open_neg_discard(player_index):
    global _NEG_DISCARD_PLAYER, _NEG_DISCARD_SELECTION
    _NEG_DISCARD_PLAYER = int(player_index)
    _NEG_DISCARD_SELECTION = []


def _toggle_neg_discard(asset):
    global _NEG_DISCARD_SELECTION
    current = next((value for value in _NEG_DISCARD_SELECTION if _identity(value) == _identity(asset)), None)
    if current:
        _NEG_DISCARD_SELECTION.remove(current)
    else:
        _NEG_DISCARD_SELECTION.append(asset)


def _set_neg_discard_good(name, quantity):
    global _NEG_DISCARD_SELECTION
    _NEG_DISCARD_SELECTION = [
        asset for asset in _NEG_DISCARD_SELECTION
        if not (asset.category == "good" and str(asset.key) == str(name))
    ]
    if quantity > 0:
        _NEG_DISCARD_SELECTION.append(AssetRef("good", "goods", str(name), int(quantity)))


def _confirm_neg_discard(session):
    global _NEG_DISCARD_PLAYER, _NEG_DISCARD_SELECTION
    if _NEG_DISCARD_PLAYER is None:
        return None
    result = session.set_negotiation_discard_plan(_NEG_DISCARD_PLAYER, _NEG_DISCARD_SELECTION)
    _set_message(session, result)
    if result[0]:
        _NEG_DISCARD_PLAYER = None
        _NEG_DISCARD_SELECTION = []


def _close_neg_discard():
    global _NEG_DISCARD_PLAYER, _NEG_DISCARD_SELECTION
    _NEG_DISCARD_PLAYER = None
    _NEG_DISCARD_SELECTION = []


def _definitive_accept(session, player_index):
    overflow = session.negotiation_overflow(player_index)
    negotiation = session.negotiation
    if overflow and not negotiation.discard_plans.get(player_index):
        _open_neg_discard(player_index)
        session.message = "Przed definitywną akceptacją wybierz elementy do odrzucenia."
        return None
    return _set_message(session, session.definitively_accept(player_index))


def _draw_neg_discard_modal(screen, font, small_font, mouse, buttons, session):
    if _NEG_DISCARD_PLAYER is None:
        return
    player_index = _NEG_DISCARD_PLAYER
    player = session.players[player_index]
    required = session.negotiation_overflow(player_index)
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 190))
    screen.blit(shade, (0, 0))
    sw, sh = screen.get_size()
    panel = pygame.Rect(sw // 2 - 380, sh // 2 - 300, 760, 600)
    _draw_discard_picker(
        screen,
        font,
        small_font,
        mouse,
        buttons,
        player,
        required,
        _NEG_DISCARD_SELECTION,
        _toggle_neg_discard,
        _set_neg_discard_good,
        panel,
    )
    _button(screen, font, mouse, buttons, "ZATWIERDŹ ODRZUTY", (panel.x + 70, panel.bottom - 58, 280, 40), lambda: _confirm_neg_discard(session))
    _button(screen, font, mouse, buttons, "ANULUJ", (panel.right - 290, panel.bottom - 58, 220, 40), _close_neg_discard)


def _draw_negotiation(screen, font, small_font, mouse, buttons, session, rect):
    negotiation = session.negotiation
    if negotiation is None:
        return
    if negotiation.state == "invited":
        _draw_invitation(screen, font, small_font, mouse, buttons, session, rect)
        return
    if negotiation.state in {"completed", "cancelled", "rejected", "expired", "failed"}:
        _panel(screen, rect, alpha=240)
        screen.blit(font.render("Negocjacja zakończona", True, TEXT), (rect.x + 24, rect.y + 24))
        draw_lines(screen, small_font, wrap(small_font, negotiation.last_message or session.message, rect.width - 48), rect.x + 24, rect.y + 76, MUTED, line_h=22)
        _button(screen, font, mouse, buttons, "KONTYNUUJ", (rect.centerx - 130, rect.bottom - 70, 260, 42), lambda: _continue_after_negotiation(session))
        return

    _draw_category_tabs(screen, small_font, mouse, buttons, rect.y + 4, _NEG_CATEGORY, _set_neg_category)
    top = rect.y + 48
    gap = 16
    half = (rect.width - gap) // 2
    left = pygame.Rect(rect.x, top, half, rect.height - 158)
    right = pygame.Rect(left.right + gap, top, half, rect.height - 158)
    _draw_negotiation_side(screen, font, small_font, mouse, buttons, session, negotiation.initiator_index, left)
    _draw_negotiation_side(screen, font, small_font, mouse, buttons, session, negotiation.partner_index, right)

    controls_y = rect.bottom - 98
    if negotiation.state == "open":
        for offset, player_index in enumerate(negotiation.participants):
            accepted = player_index in negotiation.preliminary_acceptance
            label = "WSTĘPNIE ZAAKCEPTOWANO" if accepted else "WSTĘPNIE AKCEPTUJĘ"
            x = rect.x + 16 if offset == 0 else rect.centerx + 8
            _button(screen, small_font, mouse, buttons, label, (x, controls_y, half - 24, 36), lambda i=player_index: _set_message(session, session.preliminarily_accept(i)), active=accepted)
    else:
        for offset, player_index in enumerate(negotiation.participants):
            accepted = player_index in negotiation.final_acceptance
            label = "AKCEPTOWANO DEFIN.'" if accepted else "AKCEPTUJ DEFINIT."
            x = rect.x + 16 if offset == 0 else rect.centerx + 8
            _button(screen, small_font, mouse, buttons, label, (x, controls_y, half - 24, 36), lambda i=player_index: _definitive_accept(session, i), active=accepted)
        _button(screen, small_font, mouse, buttons, "COFNIJ DO NEGOCJACJI", (rect.centerx - 125, controls_y + 44, 250, 34), lambda: _set_message(session, session.rollback_to_negotiation(negotiation.initiator_index)))

    _button(screen, small_font, mouse, buttons, "ZAKOŃCZ BEZ TRANSAKCJI", (rect.x + 16, rect.bottom - 42, 230, 32), lambda: _set_message(session, session.cancel_negotiation(negotiation.initiator_index)))
    _draw_neg_discard_modal(screen, font, small_font, mouse, buttons, session)


def _try_end_turn(session):
    global _END_TURN_CONFIRM
    result = session.end_active_turn(confirm_unused=False)
    if not result[0] and "Potwierdź" in result[1]:
        _END_TURN_CONFIRM = True
    _set_message(session, result)


def _confirm_end_turn(session):
    global _END_TURN_CONFIRM
    result = session.end_active_turn(confirm_unused=True)
    _END_TURN_CONFIRM = False
    return _set_message(session, result)


def _cancel_end_turn():
    global _END_TURN_CONFIRM
    _END_TURN_CONFIRM = False


def _draw_end_turn_confirm(screen, font, small_font, mouse, buttons, session):
    if not _END_TURN_CONFIRM:
        return
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 188))
    screen.blit(shade, (0, 0))
    sw, sh = screen.get_size()
    panel = pygame.Rect(sw // 2 - 350, sh // 2 - 155, 700, 310)
    _panel(screen, panel, alpha=250, border=(188, 126, 70))
    remaining = session.remaining_negotiations()
    screen.blit(font.render("Zakończyć turę w Radzie?", True, TEXT), (panel.x + 28, panel.y + 26))
    text = f"Masz jeszcze {remaining} niewykorzystane negocjacje. Po zakończeniu tury przepadają."
    draw_lines(screen, small_font, wrap(small_font, text, panel.width - 56), panel.x + 28, panel.y + 86, MUTED, line_h=24)
    _button(screen, font, mouse, buttons, "TAK, ZAKOŃCZ TURĘ", (panel.x + 52, panel.bottom - 78, 285, 44), lambda: _confirm_end_turn(session))
    _button(screen, font, mouse, buttons, "WRÓĆ", (panel.right - 287, panel.bottom - 78, 235, 44), _cancel_end_turn)


def _draw_loose_turn(screen, font, small_font, mouse, buttons, session):
    sw, sh = screen.get_size()
    _draw_turn_header(screen, font, small_font, session)
    remaining = session.remaining_negotiations()
    screen.blit(font.render(f"Pozostało: {remaining} z {MAX_LOOSE_NEGOTIATIONS} negocjacji", True, GOLD), (34, 84))

    content = pygame.Rect(34, 124, sw - 68, sh - 300)
    if session.negotiation is not None and session.negotiation.state in {"invited", "open", "locked", "completed", "cancelled", "rejected", "expired", "failed"}:
        _draw_negotiation(screen, font, small_font, mouse, buttons, session, content)
    else:
        _panel(screen, content, alpha=235)
        screen.blit(font.render("Wybierz gracza do luźnego handlu", True, TEXT), (content.x + 24, content.y + 22))
        y = content.y + 70
        for index, player in enumerate(session.players):
            if index == session.active_player_index:
                continue
            row = pygame.Rect(content.x + 24, y, content.width - 48, 50)
            pygame.draw.rect(screen, (27, 31, 35), row, border_radius=9)
            pygame.draw.rect(screen, player.get("player_color", GOLD), row, 1, border_radius=9)
            screen.blit(font.render(_fit(font, _player_label(player, index), row.width - 190), True, TEXT), (row.x + 12, row.y + 12))
            _button(screen, small_font, mouse, buttons, "NEGOCJUJ", (row.right - 150, row.y + 8, 136, 34), lambda i=index: _invite_player(session, i), enabled=remaining > 0)
            y += 58
        if remaining <= 0:
            screen.blit(small_font.render("Wykorzystano obie próby. Możesz już tylko zakończyć swoją turę.", True, MUTED), (content.x + 24, content.bottom - 42))

    msg = pygame.Rect(34, sh - 156, sw - 68, 48)
    _panel(screen, msg, alpha=215, border=(92, 99, 104))
    screen.blit(small_font.render(_fit(small_font, session.message, msg.width - 20), True, TEXT), (msg.x + 10, msg.y + 14))
    can_end, _ = session.can_end_active_turn()
    _button(screen, font, mouse, buttons, "ZAKOŃCZ SWOJĄ TURĘ W RADZIE", (sw // 2 - 210, sh - 88, 420, 46), lambda: _try_end_turn(session), enabled=can_end)
    _draw_end_turn_confirm(screen, font, small_font, mouse, buttons, session)


def _draw_trade_log_table(screen, font, small_font, session, rect, entries):
    y = rect.y
    if not entries:
        screen.blit(small_font.render("Brak zakończonych transakcji.", True, MUTED), (rect.x, y))
        return
    for entry in entries[-8:]:
        if y + 72 > rect.bottom:
            break
        row = pygame.Rect(rect.x, y, rect.width, 66)
        pygame.draw.rect(screen, (26, 30, 33), row, border_radius=8)
        pygame.draw.rect(screen, (78, 79, 73), row, 1, border_radius=8)
        if entry.left_index is not None and entry.right_index is not None:
            left_name = session.players[entry.left_index].get("name", "Gracz")
            right_name = session.players[entry.right_index].get("name", "Gracz")
            half = row.width // 2
            screen.blit(small_font.render(_fit(small_font, left_name, half - 24), True, GOLD), (row.x + 10, row.y + 8))
            screen.blit(small_font.render(_fit(small_font, right_name, half - 24), True, GOLD), (row.x + half + 10, row.y + 8))
            screen.blit(small_font.render(_fit(small_font, entry.left_summary, half - 24), True, TEXT), (row.x + 10, row.y + 34))
            screen.blit(small_font.render(_fit(small_font, entry.right_summary, half - 24), True, TEXT), (row.x + half + 10, row.y + 34))
            pygame.draw.line(screen, (72, 72, 68), (row.x + half, row.y + 6), (row.x + half, row.bottom - 6), 1)
        else:
            screen.blit(small_font.render(_fit(small_font, entry.text, row.width - 20), True, MUTED), (row.x + 10, row.y + 24))
        y += 72


def _draw_summary(screen, font, small_font, mouse, buttons, session):
    sw, sh = screen.get_size()
    screen.blit(font.render("Podsumowanie Rady Bohaterów", True, TEXT), (34, 24))
    screen.blit(small_font.render("Pokazane są wyłącznie transakcje, które faktycznie doszły do skutku.", True, MUTED), (34, 58))
    panel = pygame.Rect(34, 100, sw - 68, sh - 210)
    _panel(screen, panel, alpha=238)
    _draw_trade_log_table(screen, font, small_font, session, pygame.Rect(panel.x + 18, panel.y + 18, panel.width - 36, panel.height - 36), session.successful_trade_logs())
    _button(screen, font, mouse, buttons, "RADA ZAKOŃCZONA", (sw // 2 - 170, sh - 82, 340, 44), lambda: _set_message(session, session.continue_from_summary()))


def _set_comm_tab(value):
    global _COMM_TAB
    _COMM_TAB = value


def _draw_comm_panel(screen, font, small_font, mouse, buttons, session, rect):
    _panel(screen, rect, alpha=228, border=(101, 93, 76))
    _button(screen, small_font, mouse, buttons, "CZAT", (rect.x + 10, rect.y + 10, 100, 30), lambda: _set_comm_tab("chat"), active=_COMM_TAB == "chat")
    _button(screen, small_font, mouse, buttons, "LOGI HANDLU", (rect.x + 118, rect.y + 10, 140, 30), lambda: _set_comm_tab("logs"), active=_COMM_TAB == "logs")
    area = pygame.Rect(rect.x + 12, rect.y + 52, rect.width - 24, rect.height - 64)
    if _COMM_TAB == "logs":
        entries = session.trade_logs[-6:]
        y = area.y
        for entry in entries:
            if y + 38 > area.bottom:
                break
            draw_lines(screen, small_font, wrap(small_font, entry.text, area.width)[:2], area.x, y, MUTED, line_h=18)
            y += 40
        if not entries:
            screen.blit(small_font.render("Brak logów handlu.", True, MUTED), (area.x, area.y))
    else:
        y = area.y
        for entry in session.chat_messages[-6:]:
            line = f"{entry.get('name', 'Gracz')}: {entry.get('text', '')}"
            screen.blit(small_font.render(_fit(small_font, line, area.width), True, TEXT), (area.x, y))
            y += 22
        if not session.chat_messages:
            screen.blit(small_font.render("Czat Rady jest przygotowany w silniku; wpisywanie tekstu zostanie podpięte do pętli wejścia.", True, MUTED), (area.x, area.y))


def _confirm_departure(session, player_index):
    result = session.confirm_departure(player_index)
    if result[0] and result[1] == "close_council":
        reset_council_market()
        return "close_council"
    return _set_message(session, result)


def _draw_departure(screen, font, small_font, mouse, buttons, session):
    sw, sh = screen.get_size()
    screen.blit(font.render("Rada zakończona", True, TEXT), (34, 24))
    story = "Rozmowy cichną, sakwy zostają zapięte, a bohaterowie szykują się do powrotu na szlak."
    screen.blit(small_font.render(_fit(small_font, story, sw - 68), True, MUTED), (34, 58))
    count = len(session.departure_ready)
    screen.blit(font.render(f"Gotowi do opuszczenia Rady: {count}/{len(session.players)}", True, GOLD), (34, 92))

    left = pygame.Rect(34, 138, int((sw - 86) * 0.56), sh - 190)
    right = pygame.Rect(left.right + 18, 138, sw - left.right - 52, sh - 190)
    _panel(screen, left, alpha=236)
    y = left.y + 18
    for index, player in enumerate(session.players):
        row = pygame.Rect(left.x + 16, y, left.width - 32, 48)
        ready = index in session.departure_ready
        pygame.draw.rect(screen, (43, 57, 43) if ready else (29, 33, 36), row, border_radius=8)
        pygame.draw.rect(screen, (103, 145, 92) if ready else (74, 76, 78), row, 1, border_radius=8)
        screen.blit(small_font.render(_fit(small_font, player.get("name", "Gracz"), row.width - 190), True, TEXT), (row.x + 10, row.y + 15))
        if ready:
            label = small_font.render("Gotowy ✓", True, (176, 221, 155))
            screen.blit(label, (row.right - label.get_width() - 12, row.y + 15))
        else:
            _button(screen, small_font, mouse, buttons, "GOTOWY DO WYJŚCIA", (row.right - 176, row.y + 8, 164, 32), lambda i=index: _confirm_departure(session, i))
        y += 56
    _draw_comm_panel(screen, font, small_font, mouse, buttons, session, right)


def draw_council(screen, title_font, font, small_font, mouse, round_number):
    session = _session(round_number)
    _load_background(screen)
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((4, 7, 10, 94))
    screen.blit(shade, (0, 0))
    buttons = []

    if session.stage == "preparation":
        _draw_preparation(screen, font, small_font, mouse, buttons, session)
    elif session.stage == "turns":
        if session.turn_phase == "public":
            _draw_public_turn(screen, font, small_font, mouse, buttons, session)
        else:
            _draw_loose_turn(screen, font, small_font, mouse, buttons, session)
    elif session.stage == "summary":
        _draw_summary(screen, font, small_font, mouse, buttons, session)
    elif session.stage == "departure":
        _draw_departure(screen, font, small_font, mouse, buttons, session)
    else:
        sw, sh = screen.get_size()
        panel = pygame.Rect(sw // 2 - 360, sh // 2 - 120, 720, 240)
        _panel(screen, panel, alpha=245)
        label = title_font.render("Bohaterowie opuszczają Radę", True, TEXT)
        screen.blit(label, label.get_rect(center=panel.center))
    return buttons
