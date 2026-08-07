from __future__ import annotations

from pathlib import Path
from typing import Callable

import pygame

from rg_content import register_all_world_events
from rg_data import BG, COUNCIL_ROUNDS, GOLD, MUTED, TEXT
from rg_engine.council import (
    COUNCIL_LIMITS,
    AssetRef,
    CouncilUsage,
    TradeOffer,
    abandon_quest,
    available_assets,
    execute_trade,
    quest_sale_price,
    validate_trade,
)
from rg_engine.world import current_world_level, registered_players
from rg_engine.world_events import draw_next_world_event
from rg_ui import Button, draw_lines, wrap

register_all_world_events()

ROOT_DIR = Path(__file__).resolve().parent
COUNCIL_BACKGROUND_PATH = ROOT_DIR / "Grafiki" / "rada_bohaterów.png"
_BACKGROUND_CACHE = {"size": None, "surface": None}
_SOURCE_CACHE = {"loaded": False, "surface": None}
_SESSION = None

CATEGORY_LABELS = {
    "quest": "Questy",
    "item": "Przedmioty",
    "helper": "Pomocnicy",
    "good": "Towary",
}


class CouncilButton(Button):
    def __init__(self, text, rect, callback: Callable[[], object]):
        super().__init__(text, "council_noop", rect)
        self.callback = callback

    def clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        result = self.callback()
        self.action = result if isinstance(result, str) else "council_noop"
        return True


class CouncilSession:
    def __init__(self, players, round_number):
        self.players = players
        self.round_number = int(round_number)
        self.world_level = current_world_level(players)
        self.usage = CouncilUsage.for_players(players)
        self.world_event, self.world_event_message = draw_next_world_event(players)
        if self.world_event:
            event_name = self.world_event.get("name", "Wydarzenie Swiata")
            event_effect = self.world_event.get("effect_text", self.world_event_message)
            self.usage.history.append(f"Wydarzenie Swiata: {event_name} — {event_effect}")
        self.left_index = 0
        self.right_index = 1 if len(players) > 1 else 0
        self.offer = TradeOffer(self.left_index, self.right_index)
        self.mode = "trade"
        self.category = "quest"
        self.pages = {}
        self.message = self.world_event_message or "Rada rozpoczęta. Każdy gracz może handlować z każdym."
        self.finish_mode = False
        self.finish_position = 0
        self.finish_confirmed = []

    def reset_offer(self):
        self.offer = TradeOffer(self.left_index, self.right_index)
        self.pages.clear()

    def change_player(self, side, delta):
        if len(self.players) < 2:
            return
        if side == "left":
            candidate = (self.left_index + delta) % len(self.players)
            while candidate == self.right_index:
                candidate = (candidate + delta) % len(self.players)
            self.left_index = candidate
        else:
            candidate = (self.right_index + delta) % len(self.players)
            while candidate == self.left_index:
                candidate = (candidate + delta) % len(self.players)
            self.right_index = candidate
        self.reset_offer()
        self.message = "Wybrano nową parę handlową."

    def set_mode(self, mode):
        self.mode = mode
        self.message = ""

    def set_category(self, category):
        self.category = category

    def _side(self, side):
        return self.offer.left if side == "left" else self.offer.right

    def _player_index(self, side):
        return self.left_index if side == "left" else self.right_index

    def _player(self, side):
        return self.players[self._player_index(side)]

    def _changed(self):
        self.offer.reset_acceptance()
        self.message = "Oferta zmieniona — obie akceptacje zostały cofnięte."

    def toggle_asset(self, side, asset):
        trade_side = self._side(side)
        if asset.category == "good":
            return
        if asset in trade_side.assets:
            trade_side.assets.remove(asset)
        else:
            trade_side.assets.append(asset)
        self._changed()

    def selected_good_quantity(self, side, name):
        return sum(
            int(asset.quantity or 0)
            for asset in self._side(side).assets
            if asset.category == "good" and str(asset.key) == str(name)
        )

    def adjust_good(self, side, name, delta):
        trade_side = self._side(side)
        player = self._player(side)
        available = sum(1 for good in player.get("goods", []) or [] if str(good) == str(name))
        current = self.selected_good_quantity(side, name)
        new_value = max(0, min(available, current + int(delta)))
        trade_side.assets = [
            asset for asset in trade_side.assets
            if not (asset.category == "good" and str(asset.key) == str(name))
        ]
        if new_value:
            trade_side.assets.append(AssetRef("good", "goods", str(name), new_value))
        self._changed()

    def adjust_gold(self, side, delta):
        trade_side = self._side(side)
        player = self._player(side)
        maximum = int(player.get("gold", 0) or 0)
        trade_side.gold = max(0, min(maximum, int(trade_side.gold or 0) + int(delta)))
        self._changed()

    def accept(self, side):
        valid, message = validate_trade(self.offer, self.players, self.usage, self.world_level)
        if not valid:
            self.offer.reset_acceptance()
            self.message = message
            return
        if side == "left":
            self.offer.accepted_left = not self.offer.accepted_left
        else:
            self.offer.accepted_right = not self.offer.accepted_right
        if not self.offer.accepted:
            self.message = f"{self._player(side).get('name', 'Gracz')} zaakceptował ofertę."
            return
        success, message = execute_trade(self.offer, self.players, self.usage, self.world_level)
        self.message = message
        if success:
            self.reset_offer()

    def abandon(self, quest_index):
        player = self.players[self.left_index]
        success, message = abandon_quest(player, quest_index)
        self.message = message
        if success:
            self.usage.history.append(message)

    def start_finish(self):
        self.finish_mode = True
        self.finish_position = 0
        self.finish_confirmed = []
        self.message = "Każdy gracz kolejno potwierdza zakończenie Rady."

    def cancel_finish(self):
        self.finish_mode = False
        self.finish_position = 0
        self.finish_confirmed = []
        self.message = "Powrót do Rady."

    def confirm_finish(self):
        if not self.players:
            return self._close_action()
        index = min(self.finish_position, len(self.players) - 1)
        self.finish_confirmed.append(index)
        self.finish_position += 1
        if self.finish_position >= len(self.players):
            return self._close_action()
        return None

    def _close_action(self):
        global _SESSION
        try:
            pygame.event.set_allowed(pygame.KEYDOWN)
        except (AttributeError, pygame.error):
            pass
        _SESSION = None
        return "close_council"


def _load_source():
    if _SOURCE_CACHE["loaded"]:
        return _SOURCE_CACHE["surface"]
    _SOURCE_CACHE["loaded"] = True
    if not COUNCIL_BACKGROUND_PATH.exists():
        return None
    try:
        source = pygame.image.load(str(COUNCIL_BACKGROUND_PATH)).convert()
    except (OSError, pygame.error):
        source = None
    _SOURCE_CACHE["surface"] = source
    return source


def _load_background(size):
    size = tuple(size)
    if _BACKGROUND_CACHE["size"] == size:
        return _BACKGROUND_CACHE["surface"]
    source = _load_source()
    if source is None:
        _BACKGROUND_CACHE["size"] = size
        _BACKGROUND_CACHE["surface"] = None
        return None
    screen_width, screen_height = size
    image_width, image_height = source.get_size()
    scale = max(screen_width / image_width, screen_height / image_height)
    cover = pygame.transform.smoothscale(source, (max(1, int(image_width * scale)), max(1, int(image_height * scale))))
    background = pygame.Surface(size)
    background.blit(cover, ((screen_width - cover.get_width()) // 2, (screen_height - cover.get_height()) // 2))
    shade = pygame.Surface(size, pygame.SRCALPHA)
    shade.fill((4, 7, 10, 145))
    background.blit(shade, (0, 0))
    _BACKGROUND_CACHE["size"] = size
    _BACKGROUND_CACHE["surface"] = background
    return background


def _session(round_number):
    global _SESSION
    players = registered_players()
    if _SESSION is None or _SESSION.round_number != int(round_number) or _SESSION.players != players:
        _SESSION = CouncilSession(players, round_number)
        try:
            pygame.event.set_blocked(pygame.KEYDOWN)
        except (AttributeError, pygame.error):
            pass
    return _SESSION


def _panel(screen, rect, alpha=222, border=GOLD):
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, (14, 17, 20, alpha), surface.get_rect(), border_radius=12)
    pygame.draw.rect(surface, border, surface.get_rect(), 2, border_radius=12)
    screen.blit(surface, rect.topleft)


def _add_button(screen, font, mouse, buttons, text, rect, callback, active=False):
    button = CouncilButton(text, rect, callback)
    button.draw(screen, font, mouse, active=active)
    buttons.append(button)
    return button


def _fit(font, text, width):
    value = str(text)
    while value and font.size(value)[0] > width:
        value = value[:-2].rstrip() + "…"
    return value


def _usage_text(session, player_index):
    usage = session.usage
    return (
        f"Questy {usage.used(player_index, 'quest')}/{COUNCIL_LIMITS['quest']}   "
        f"Przedmioty {usage.used(player_index, 'item')}/{COUNCIL_LIMITS['item']}   "
        f"Pomocnik {usage.used(player_index, 'helper')}/{COUNCIL_LIMITS['helper']}   "
        f"Towary {usage.used(player_index, 'good')}/{COUNCIL_LIMITS['good']}"
    )


def _draw_player_selector(screen, font, small_font, mouse, buttons, session, side, rect):
    player_index = session.left_index if side == "left" else session.right_index
    player = session.players[player_index]
    color = player.get("player_color", GOLD)
    _panel(screen, rect, alpha=230, border=color)
    label = f"{player.get('name', 'Gracz')}  |  {player.get('gold', 0)} zł"
    screen.blit(font.render(_fit(font, label, rect.width - 110), True, TEXT), (rect.x + 54, rect.y + 13))
    pygame.draw.circle(screen, color, (rect.x + 28, rect.centery), 10)
    if len(session.players) > 1:
        _add_button(screen, small_font, mouse, buttons, "‹", (rect.right - 92, rect.y + 8, 38, rect.height - 16), lambda: session.change_player(side, -1))
        _add_button(screen, small_font, mouse, buttons, "›", (rect.right - 48, rect.y + 8, 38, rect.height - 16), lambda: session.change_player(side, 1))


def _asset_selected(session, side, asset):
    if asset.category == "good":
        return session.selected_good_quantity(side, asset.key) > 0
    return asset in session._side(side).assets


def _draw_asset_list(screen, font, small_font, mouse, buttons, session, side, rect):
    player = session._player(side)
    category = session.category
    assets = available_assets(player, category)
    page_key = (side, category)
    page = max(0, int(session.pages.get(page_key, 0)))
    page_size = 5
    max_page = max(0, (len(assets) - 1) // page_size)
    page = min(page, max_page)
    session.pages[page_key] = page
    visible = assets[page * page_size:(page + 1) * page_size]

    y = rect.y
    row_h = 44
    for asset, name, detail in visible:
        selected = _asset_selected(session, side, asset)
        row = pygame.Rect(rect.x, y, rect.width, row_h)
        pygame.draw.rect(screen, (55, 63, 55) if selected else (28, 32, 36), row, border_radius=8)
        pygame.draw.rect(screen, (120, 160, 110) if selected else (72, 78, 84), row, 1, border_radius=8)
        screen.blit(small_font.render(_fit(small_font, name, row.width - 150), True, TEXT), (row.x + 10, row.y + 6))
        if detail:
            screen.blit(small_font.render(_fit(small_font, detail, row.width - 150), True, MUTED), (row.x + 10, row.y + 24))
        if category == "good":
            quantity = session.selected_good_quantity(side, name)
            screen.blit(small_font.render(str(quantity), True, TEXT), (row.right - 76, row.y + 13))
            _add_button(screen, small_font, mouse, buttons, "-", (row.right - 112, row.y + 7, 28, 30), lambda n=name: session.adjust_good(side, n, -1))
            _add_button(screen, small_font, mouse, buttons, "+", (row.right - 38, row.y + 7, 28, 30), lambda n=name: session.adjust_good(side, n, 1))
        else:
            _add_button(screen, small_font, mouse, buttons, "✓" if selected else "+", (row.right - 48, row.y + 7, 38, 30), lambda a=asset: session.toggle_asset(side, a), active=selected)
        y += row_h + 6

    if not visible:
        screen.blit(small_font.render("Brak elementów w tej kategorii.", True, MUTED), (rect.x + 8, rect.y + 12))
    if len(assets) > page_size:
        bottom = rect.bottom - 34
        _add_button(screen, small_font, mouse, buttons, "‹", (rect.x, bottom, 42, 30), lambda: session.pages.__setitem__(page_key, max(0, page - 1)))
        screen.blit(small_font.render(f"{page + 1}/{max_page + 1}", True, MUTED), (rect.centerx - 18, bottom + 6))
        _add_button(screen, small_font, mouse, buttons, "›", (rect.right - 42, bottom, 42, 30), lambda: session.pages.__setitem__(page_key, min(max_page, page + 1)))


def _draw_gold_controls(screen, small_font, mouse, buttons, session, side, rect):
    trade_side = session._side(side)
    player = session._player(side)
    screen.blit(small_font.render(f"Złoto w ofercie: {trade_side.gold}/{player.get('gold', 0)}", True, TEXT), (rect.x, rect.y))
    x = rect.right - 184
    for label, delta in (("-5", -5), ("-1", -1), ("+1", 1), ("+5", 5)):
        _add_button(screen, small_font, mouse, buttons, label, (x, rect.y - 4, 42, 30), lambda d=delta: session.adjust_gold(side, d))
        x += 46


def _draw_trade(screen, font, small_font, mouse, buttons, session, content):
    if len(session.players) < 2:
        _panel(screen, content)
        message = "W grze jednoosobowej nie ma partnera handlowego. Możesz porzucać questy albo zakończyć Radę."
        draw_lines(screen, font, wrap(font, message, content.width - 50), content.x + 25, content.y + 30, MUTED, line_h=30)
        return

    gap = 18
    half = (content.width - gap) // 2
    left = pygame.Rect(content.x, content.y, half, content.height)
    right = pygame.Rect(left.right + gap, content.y, half, content.height)

    for side, rect in (("left", left), ("right", right)):
        _panel(screen, rect)
        index = session._player_index(side)
        player = session._player(side)
        color = player.get("player_color", GOLD)
        screen.blit(font.render(player.get("name", "Gracz"), True, TEXT), (rect.x + 18, rect.y + 14))
        pygame.draw.circle(screen, color, (rect.right - 24, rect.y + 25), 9)
        screen.blit(small_font.render(_usage_text(session, index), True, MUTED), (rect.x + 18, rect.y + 48))
        list_rect = pygame.Rect(rect.x + 18, rect.y + 78, rect.width - 36, rect.height - 168)
        _draw_asset_list(screen, font, small_font, mouse, buttons, session, side, list_rect)
        gold_rect = pygame.Rect(rect.x + 18, rect.bottom - 76, rect.width - 36, 30)
        _draw_gold_controls(screen, small_font, mouse, buttons, session, side, gold_rect)
        accepted = session.offer.accepted_left if side == "left" else session.offer.accepted_right
        label = "AKCEPTOWANO" if accepted else "AKCEPTUJĘ"
        _add_button(screen, small_font, mouse, buttons, label, (rect.x + 18, rect.bottom - 42, rect.width - 36, 32), lambda s=side: session.accept(s), active=accepted)


def _draw_abandon(screen, font, small_font, mouse, buttons, session, content):
    _panel(screen, content)
    player = session.players[session.left_index]
    screen.blit(font.render(f"Porzuć questy — {player.get('name', 'Gracz')}", True, TEXT), (content.x + 24, content.y + 22))
    screen.blit(small_font.render("Możesz porzucić dowolną liczbę questów. Nie kosztuje to akcji i nie daje nagrody.", True, MUTED), (content.x + 24, content.y + 54))
    y = content.y + 92
    quests = player.get("active_quests", []) or []
    for index, quest in enumerate(quests[:7]):
        row = pygame.Rect(content.x + 24, y, content.width - 48, 48)
        pygame.draw.rect(screen, (28, 32, 36), row, border_radius=8)
        pygame.draw.rect(screen, (82, 74, 70), row, 1, border_radius=8)
        name = quest.get("name", "Quest") if isinstance(quest, dict) else str(quest)
        stage = quest.get("stage", "") if isinstance(quest, dict) else ""
        screen.blit(small_font.render(_fit(small_font, f"{name}  {stage}", row.width - 150), True, TEXT), (row.x + 12, row.y + 14))
        _add_button(screen, small_font, mouse, buttons, "PORZUĆ", (row.right - 116, row.y + 8, 104, 32), lambda i=index: session.abandon(i))
        y += 56
    if not quests:
        screen.blit(small_font.render("Ten gracz nie ma aktywnych questów.", True, MUTED), (content.x + 24, y))


def _draw_history(screen, font, small_font, session, content):
    _panel(screen, content)
    screen.blit(font.render("Historia Rady", True, TEXT), (content.x + 24, content.y + 22))
    entries = session.usage.history[-12:]
    if not entries:
        screen.blit(small_font.render("Nie zawarto jeszcze żadnej transakcji.", True, MUTED), (content.x + 24, content.y + 64))
        return
    y = content.y + 62
    for entry in entries:
        lines = wrap(small_font, entry, content.width - 48)[:2]
        draw_lines(screen, small_font, lines, content.x + 24, y, MUTED, line_h=19)
        y += 42


def _draw_world_event(screen, font, small_font, session, rect):
    _panel(screen, rect, alpha=224, border=(170, 126, 58))
    event = session.world_event or {}
    if not event:
        screen.blit(font.render("Wydarzenie Świata", True, TEXT), (rect.x + 16, rect.y + 12))
        screen.blit(small_font.render("Brak karty wydarzenia.", True, MUTED), (rect.x + 16, rect.y + 42))
        return
    duration = "do następnej Rady" if event.get("duration") == "until_next_council" else "natychmiastowe"
    title = f"Wydarzenie Świata: {event.get('name', 'Wydarzenie')}"
    screen.blit(font.render(_fit(font, title, rect.width - 180), True, TEXT), (rect.x + 16, rect.y + 9))
    duration_label = small_font.render(duration, True, GOLD)
    screen.blit(duration_label, (rect.right - duration_label.get_width() - 16, rect.y + 13))
    description = event.get("description", "")
    effect = event.get("effect_text", session.world_event_message)
    screen.blit(small_font.render(_fit(small_font, description, rect.width - 32), True, MUTED), (rect.x + 16, rect.y + 36))
    screen.blit(small_font.render(_fit(small_font, f"Efekt: {effect}", rect.width - 32), True, TEXT), (rect.x + 16, rect.y + 57))


def _draw_finish_overlay(screen, font, small_font, mouse, buttons, session):
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 190))
    screen.blit(shade, (0, 0))
    sw, sh = screen.get_size()
    panel = pygame.Rect(sw // 2 - 330, sh // 2 - 180, 660, 360)
    _panel(screen, panel, alpha=245)
    screen.blit(font.render("Potwierdzenie zakończenia Rady", True, TEXT), (panel.x + 28, panel.y + 26))
    current = min(session.finish_position, max(0, len(session.players) - 1))
    player = session.players[current] if session.players else {"name": "Gracz"}
    confirmed_names = [session.players[index].get("name", "Gracz") for index in session.finish_confirmed]
    screen.blit(small_font.render(f"Potwierdzili: {', '.join(confirmed_names) if confirmed_names else 'nikt'}", True, MUTED), (panel.x + 28, panel.y + 70))
    prompt = f"{player.get('name', 'Gracz')}: potwierdź zakończenie Rady."
    screen.blit(font.render(_fit(font, prompt, panel.width - 56), True, TEXT), (panel.x + 28, panel.y + 120))
    _add_button(screen, font, mouse, buttons, "POTWIERDZAM", (panel.x + 80, panel.bottom - 100, 240, 54), session.confirm_finish)
    _add_button(screen, font, mouse, buttons, "WRÓĆ DO RADY", (panel.right - 320, panel.bottom - 100, 240, 54), session.cancel_finish)


def draw_council(screen, title_font, font, small_font, mouse, round_number):
    session = _session(round_number)
    background = _load_background(screen.get_size())
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BG)

    sw, sh = screen.get_size()
    buttons = []
    council_number = max(1, (int(round_number) - 1) // COUNCIL_ROUNDS)
    title = title_font.render("Rada Bohaterów", True, TEXT)
    screen.blit(title, title.get_rect(center=(sw // 2, 38)))
    subtitle = f"Rada nr {council_number}  •  Poziom świata {session.world_level}  •  Następna runda: {round_number}"
    subtitle_surface = small_font.render(subtitle, True, MUTED)
    screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(sw // 2, 76)))

    event_rect = pygame.Rect(max(24, sw // 2 - 470), 94, min(940, sw - 48), 82)
    _draw_world_event(screen, font, small_font, session, event_rect)

    nav_y = 188
    nav_w = 170
    nav_gap = 10
    nav_x = sw // 2 - (nav_w * 3 + nav_gap * 2) // 2
    for index, (label, mode) in enumerate((("HANDEL", "trade"), ("PORZUĆ QUEST", "abandon"), ("HISTORIA", "history"))):
        _add_button(screen, small_font, mouse, buttons, label, (nav_x + index * (nav_w + nav_gap), nav_y, nav_w, 36), lambda m=mode: session.set_mode(m), active=session.mode == mode)

    selector_y = 236
    selector_w = min(500, (sw - 90) // 2)
    _draw_player_selector(screen, font, small_font, mouse, buttons, session, "left", pygame.Rect(30, selector_y, selector_w, 52))
    if len(session.players) > 1:
        _draw_player_selector(screen, font, small_font, mouse, buttons, session, "right", pygame.Rect(sw - selector_w - 30, selector_y, selector_w, 52))

    if session.mode == "trade" and len(session.players) > 1:
        tab_y = 302
        tab_w = 142
        tabs_total = tab_w * 4 + 10 * 3
        tab_x = sw // 2 - tabs_total // 2
        for index, category in enumerate(("quest", "item", "helper", "good")):
            label = CATEGORY_LABELS[category]
            _add_button(screen, small_font, mouse, buttons, label, (tab_x + index * (tab_w + 10), tab_y, tab_w, 34), lambda c=category: session.set_category(c), active=session.category == category)
        price = quest_sale_price(session.world_level)
        price_text = f"Sprzedaż questa na tym poziomie: {price} złota. Wymiana: quest za quest."
        price_surface = small_font.render(price_text, True, MUTED)
        screen.blit(price_surface, price_surface.get_rect(center=(sw // 2, tab_y + 50)))
        content_top = tab_y + 72
    else:
        content_top = 302

    content = pygame.Rect(30, content_top, sw - 60, max(220, sh - content_top - 108))
    if session.mode == "trade":
        _draw_trade(screen, font, small_font, mouse, buttons, session, content)
    elif session.mode == "abandon":
        _draw_abandon(screen, font, small_font, mouse, buttons, session, content)
    else:
        _draw_history(screen, font, small_font, session, content)

    message_rect = pygame.Rect(30, sh - 92, sw - 270, 62)
    _panel(screen, message_rect, alpha=210, border=(100, 110, 116))
    if session.message:
        lines = wrap(small_font, session.message, message_rect.width - 24)[:2]
        draw_lines(screen, small_font, lines, message_rect.x + 12, message_rect.y + 11, TEXT, line_h=20)

    _add_button(screen, font, mouse, buttons, "ZAKOŃCZ RADĘ", (sw - 220, sh - 82, 190, 48), session.start_finish)

    if session.finish_mode:
        buttons = []
        _draw_finish_overlay(screen, font, small_font, mouse, buttons, session)
    return buttons