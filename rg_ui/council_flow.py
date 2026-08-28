from __future__ import annotations

from pathlib import Path
from typing import Callable

import pygame

from rg_core.data import BG, GOLD, MUTED, TEXT
from rg_engine.production import activate_constructions, owned_sites, roll_site_production
from rg_ui.common import Button, draw_lines, wrap
from rg_ui import council as council_ui

NEWS_DURATION_MS = 1500
EVENT_VISIBLE_MS = 3600
EVENT_SLIDE_MS = 700
PRODUCTION_PAGE_SIZE = 5

ROOT_DIR = Path(__file__).resolve().parents[1]
_PARCHMENT_SOUND_CANDIDATES = (
    ROOT_DIR / "Dzwieki" / "szelest_pergaminu.ogg",
    ROOT_DIR / "Dzwieki" / "szelest_pergaminu.wav",
    ROOT_DIR / "Dźwięki" / "szelest_pergaminu.ogg",
    ROOT_DIR / "Dźwięki" / "szelest_pergaminu.wav",
    ROOT_DIR / "Grafiki" / "szelest_pergaminu.ogg",
    ROOT_DIR / "Grafiki" / "szelest_pergaminu.wav",
)

_FLOW = None
_PARCHMENT_SOUND = None
_PARCHMENT_SOUND_LOADED = False


class FlowButton(Button):
    def __init__(self, text, rect, callback: Callable[[], object]):
        super().__init__(text, "council_flow", rect)
        self.callback = callback

    def clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        result = self.callback()
        self.action = result if isinstance(result, str) else "council_flow"
        return True


class CouncilIntroFlow:
    def __init__(self, round_number: int, session):
        self.round_number = int(round_number)
        self.session = session
        self.phase = "news"
        self.phase_started_at = pygame.time.get_ticks()
        self.ready_players: list[int] = []
        self.rustle_played = False

        self.production_player_index = 0
        self.production_pages: dict[int, int] = {}
        self.production_message = ""
        self.production_prepared = False
        self.production_activated: dict[int, list[str]] = {}

    @property
    def players(self):
        return self.session.players

    @property
    def event(self):
        return self.session.world_event or {}

    @property
    def is_instant(self):
        return self.event.get("duration") == "instant"

    def prepare_production(self):
        if self.production_prepared:
            return
        self.production_prepared = True
        self.production_activated = {}
        for index, player in enumerate(self.players):
            activated = activate_constructions(player)
            if activated:
                self.production_activated[index] = [str(site.get("name", "Zakład")) for site in activated]

    def change_phase(self, phase: str):
        self.phase = phase
        self.phase_started_at = pygame.time.get_ticks()
        if phase == "production":
            self.prepare_production()

    def current_ready_player(self):
        for index in range(len(self.players)):
            if index not in self.ready_players:
                return index
        return None

    def confirm_ready(self):
        index = self.current_ready_player()
        if index is None:
            self.change_phase("council")
            return None
        if index not in self.ready_players:
            self.ready_players.append(index)
        if len(self.ready_players) >= len(self.players):
            self.change_phase("council")
        return None

    def current_production_player(self):
        if not self.players:
            return None
        if self.production_player_index >= len(self.players):
            return None
        return self.production_player_index

    def production_sites(self, player_index=None):
        if player_index is None:
            player_index = self.current_production_player()
        if player_index is None or not (0 <= int(player_index) < len(self.players)):
            return []
        return owned_sites(self.players[int(player_index)])

    def site_rolled(self, site):
        return str(site.get("last_production_council")) == str(self.round_number)

    def production_complete(self, player_index=None):
        sites = self.production_sites(player_index)
        return all(self.site_rolled(site) for site in sites)

    def roll_site(self, site_id):
        player_index = self.current_production_player()
        if player_index is None:
            return None
        player = self.players[player_index]
        site = next((site for site in self.production_sites(player_index) if str(site.get("id")) == str(site_id)), None)
        if site is None:
            self.production_message = "Nie znaleziono zakładu tego bohatera."
            return None
        _success, message, _amount = roll_site_production(player, site, self.round_number)
        self.production_message = message
        return None

    def change_production_page(self, delta):
        player_index = self.current_production_player()
        if player_index is None:
            return None
        sites = self.production_sites(player_index)
        max_page = max(0, (len(sites) - 1) // PRODUCTION_PAGE_SIZE)
        current = max(0, int(self.production_pages.get(player_index, 0) or 0))
        self.production_pages[player_index] = max(0, min(max_page, current + int(delta)))
        return None

    def next_production_player(self):
        player_index = self.current_production_player()
        if player_index is None:
            self.change_phase("ready")
            return None
        if not self.production_complete(player_index):
            self.production_message = "Najpierw wykonaj rzut za każdy własny zakład."
            return None
        self.production_player_index += 1
        self.production_message = ""
        if self.production_player_index >= len(self.players):
            self.change_phase("ready")
        return None


def reset_council_intro_flow():
    global _FLOW
    _FLOW = None


def _flow(round_number):
    global _FLOW
    session = council_ui._session(round_number)
    if (
        _FLOW is None
        or _FLOW.round_number != int(round_number)
        or _FLOW.session is not session
    ):
        _FLOW = CouncilIntroFlow(round_number, session)
    return _FLOW


def _load_background(screen):
    background = council_ui._load_background(screen.get_size())
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BG)


def _panel(screen, rect, alpha=238, border=GOLD):
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, (12, 15, 19, alpha), surface.get_rect(), border_radius=14)
    pygame.draw.rect(surface, border, surface.get_rect(), 2, border_radius=14)
    screen.blit(surface, rect.topleft)


def _fit(font, text, width):
    value = str(text or "")
    if font.size(value)[0] <= width:
        return value
    while value and font.size(value + "…")[0] > width:
        value = value[:-1]
    return value.rstrip() + "…"


def _play_parchment_rustle():
    global _PARCHMENT_SOUND, _PARCHMENT_SOUND_LOADED
    if not _PARCHMENT_SOUND_LOADED:
        _PARCHMENT_SOUND_LOADED = True
        for path in _PARCHMENT_SOUND_CANDIDATES:
            if not path.exists():
                continue
            try:
                _PARCHMENT_SOUND = pygame.mixer.Sound(str(path))
            except (pygame.error, OSError):
                _PARCHMENT_SOUND = None
            if _PARCHMENT_SOUND is not None:
                break
    if _PARCHMENT_SOUND is not None:
        try:
            _PARCHMENT_SOUND.play()
        except pygame.error:
            pass


def _duration_label(event):
    duration = event.get("duration")
    if duration == "until_next_council":
        return "DO NASTĘPNEJ RADY"
    if duration == "until_resolved":
        return "DO WYELIMINOWANIA PROBLEMU"
    return "NATYCHMIAST"


def _draw_news(screen, title_font, font, flow):
    sw, sh = screen.get_size()
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 92))
    screen.blit(shade, (0, 0))

    panel = pygame.Rect(sw // 2 - 420, sh // 2 - 150, 840, 300)
    _panel(screen, panel, alpha=238, border=(174, 128, 65))
    title = title_font.render("Wieści ze świata", True, TEXT)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 78)))
    subtitle = font.render("Wieści docierają do bohaterów przed rozpoczęciem Rady…", True, MUTED)
    screen.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.y + 146)))
    level = font.render(f"Poziom Świata {flow.session.world_level}", True, GOLD)
    screen.blit(level, level.get_rect(center=(panel.centerx, panel.y + 206)))


def _event_card_rect(screen, y_offset=0):
    sw, sh = screen.get_size()
    width = min(820, sw - 120)
    height = min(520, sh - 170)
    return pygame.Rect((sw - width) // 2, (sh - height) // 2 + int(y_offset), width, height)


def _draw_event_card(screen, title_font, font, small_font, flow, y_offset=0):
    event = flow.event
    card = _event_card_rect(screen, y_offset)
    _panel(screen, card, alpha=248, border=(184, 134, 66))

    header = small_font.render(f"WYDARZENIE ŚWIATA {flow.session.world_level}", True, GOLD)
    screen.blit(header, header.get_rect(center=(card.centerx, card.y + 30)))

    name = str(event.get("name") or "Wydarzenie Świata")
    rendered_name = title_font.render(_fit(title_font, name, card.width - 70), True, TEXT)
    screen.blit(rendered_name, rendered_name.get_rect(center=(card.centerx, card.y + 82)))

    duration = small_font.render(_duration_label(event), True, (225, 174, 95))
    screen.blit(duration, duration.get_rect(center=(card.centerx, card.y + 124)))

    divider_y = card.y + 154
    pygame.draw.line(screen, (104, 79, 47), (card.x + 34, divider_y), (card.right - 34, divider_y), 1)

    description = str(event.get("description") or "Brak opisu wydarzenia.")
    desc_lines = wrap(font, description, card.width - 90)[:6]
    y = divider_y + 30
    y = draw_lines(screen, font, desc_lines, card.x + 45, y, MUTED, line_h=font.get_height() + 8)

    effect_title = font.render("Efekt", True, GOLD)
    screen.blit(effect_title, (card.x + 45, y + 12))
    y += 48
    effect = str(event.get("effect_text") or flow.session.world_event_message or "Brak dodatkowego efektu.")
    draw_lines(screen, font, wrap(font, effect, card.width - 90)[:5], card.x + 45, y, TEXT, line_h=font.get_height() + 8)

    if event.get("duration") == "until_resolved":
        problem = event.get("problem") or {}
        condition = str(problem.get("condition") or "Rozwiąż problem na mapie.")
        reward_hint = str(problem.get("reward_hint") or "Nagroda: ???")
        screen.blit(small_font.render(_fit(small_font, f"Warunek: {condition}", card.width - 90), True, GOLD), (card.x + 45, card.bottom - 66))
        screen.blit(small_font.render(_fit(small_font, reward_hint, card.width - 90), True, MUTED), (card.x + 45, card.bottom - 38))


def _draw_production(screen, title_font, font, small_font, mouse, flow):
    sw, sh = screen.get_size()
    panel = pygame.Rect(sw // 2 - 470, sh // 2 - 305, 940, 610)
    _panel(screen, panel, alpha=246, border=(173, 126, 60))
    buttons = []

    title = title_font.render("Produkcja zakładów", True, TEXT)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 46)))
    subtitle = small_font.render("Na początku każdej Rady każdy własny zakład wykonuje jeden rzut produkcji.", True, MUTED)
    screen.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.y + 82)))

    player_index = flow.current_production_player()
    if player_index is None:
        flow.change_phase("ready")
        return []

    player = flow.players[player_index]
    player_name = str(player.get("name") or f"Gracz {player_index + 1}")
    player_header = font.render(f"{player_name} — zakłady: {len(flow.production_sites(player_index))}", True, GOLD)
    screen.blit(player_header, (panel.x + 38, panel.y + 112))

    activated = flow.production_activated.get(player_index, [])
    if activated:
        text = "Budowa zakończona: " + ", ".join(activated)
        screen.blit(small_font.render(_fit(small_font, text, panel.width - 76), True, (154, 210, 141)), (panel.x + 38, panel.y + 141))

    sites = flow.production_sites(player_index)
    page = max(0, int(flow.production_pages.get(player_index, 0) or 0))
    max_page = max(0, (len(sites) - 1) // PRODUCTION_PAGE_SIZE)
    page = min(page, max_page)
    flow.production_pages[player_index] = page
    visible = sites[page * PRODUCTION_PAGE_SIZE:(page + 1) * PRODUCTION_PAGE_SIZE]

    list_top = panel.y + 174
    row_h = 67
    for row_index, site in enumerate(visible):
        rect = pygame.Rect(panel.x + 38, list_top + row_index * (row_h + 7), panel.width - 76, row_h)
        rolled = flow.site_rolled(site)
        pygame.draw.rect(screen, (42, 55, 43) if rolled else (27, 31, 35), rect, border_radius=9)
        pygame.draw.rect(screen, (103, 145, 94) if rolled else (86, 74, 55), rect, 1, border_radius=9)

        screen.blit(font.render(_fit(font, site.get("name", "Zakład"), rect.width - 230), True, TEXT), (rect.x + 12, rect.y + 8))
        meta = f"{site.get('material')} | {site.get('potential_level')} | rzut k{site.get('die')}"
        screen.blit(small_font.render(_fit(small_font, meta, rect.width - 230), True, MUTED), (rect.x + 12, rect.y + 39))

        if rolled:
            amount = int(site.get("last_production_roll", 0) or 0)
            result = small_font.render(f"Wynik: {amount}", True, (157, 215, 145))
            screen.blit(result, result.get_rect(midright=(rect.right - 16, rect.centery)))
        else:
            button = FlowButton(
                f"RZUĆ k{site.get('die')}",
                (rect.right - 170, rect.y + 13, 150, 40),
                lambda site_id=site.get("id"): flow.roll_site(site_id),
            )
            button.draw(screen, small_font, mouse)
            buttons.append(button)

    if not sites:
        empty = font.render("Nie posiadasz jeszcze żadnego zakładu.", True, MUTED)
        screen.blit(empty, empty.get_rect(center=(panel.centerx, panel.y + 285)))

    if max_page > 0:
        page_y = panel.bottom - 92
        prev_button = FlowButton("‹", (panel.x + 38, page_y, 44, 34), lambda: flow.change_production_page(-1))
        next_button = FlowButton("›", (panel.x + 142, page_y, 44, 34), lambda: flow.change_production_page(1))
        prev_button.draw(screen, small_font, mouse)
        next_button.draw(screen, small_font, mouse)
        buttons.extend([prev_button, next_button])
        page_label = small_font.render(f"{page + 1}/{max_page + 1}", True, MUTED)
        screen.blit(page_label, page_label.get_rect(center=(panel.x + 114, page_y + 17)))

    if flow.production_message:
        message = small_font.render(_fit(small_font, flow.production_message, panel.width - 330), True, GOLD)
        screen.blit(message, (panel.x + 205, panel.bottom - 84))

    done = flow.production_complete(player_index)
    button_text = "DALEJ" if player_index < len(flow.players) - 1 else "PRZEJDŹ DALEJ"
    next_rect = pygame.Rect(panel.right - 250, panel.bottom - 92, 212, 46)
    if done:
        button = FlowButton(button_text, next_rect, flow.next_production_player)
        button.draw(screen, font, mouse)
        buttons.append(button)
    else:
        pygame.draw.rect(screen, (37, 39, 41), next_rect, border_radius=8)
        pygame.draw.rect(screen, (78, 78, 78), next_rect, 1, border_radius=8)
        locked = small_font.render("Rzuć za wszystkie", True, MUTED)
        screen.blit(locked, locked.get_rect(center=next_rect.center))

    return buttons


def _draw_ready(screen, title_font, font, small_font, mouse, flow):
    sw, sh = screen.get_size()
    buttons = []
    panel = pygame.Rect(sw // 2 - 430, sh // 2 - 245, 860, 490)
    _panel(screen, panel, alpha=244)

    title = title_font.render("Przejście do Rady Bohaterów", True, TEXT)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 54)))

    event_name = str(flow.event.get("name") or "Brak wydarzenia")
    summary = f"Wieści ze świata: {event_name}"
    screen.blit(font.render(_fit(font, summary, panel.width - 70), True, GOLD), (panel.x + 35, panel.y + 106))

    ready_count = len(flow.ready_players)
    count_label = font.render(f"Gotowi do Rady: {ready_count}/{len(flow.players)}", True, TEXT)
    screen.blit(count_label, count_label.get_rect(center=(panel.centerx, panel.y + 162)))

    y = panel.y + 205
    row_w = panel.width - 100
    for index, player in enumerate(flow.players[:6]):
        row = pygame.Rect(panel.x + 50, y, row_w, 38)
        is_ready = index in flow.ready_players
        pygame.draw.rect(screen, (43, 57, 43) if is_ready else (31, 35, 39), row, border_radius=8)
        pygame.draw.rect(screen, (104, 145, 93) if is_ready else (78, 73, 64), row, 1, border_radius=8)
        name = str(player.get("name") or f"Gracz {index + 1}")
        status = "Gotowy ✓" if is_ready else "Oczekiwanie…"
        screen.blit(small_font.render(name, True, TEXT), (row.x + 12, row.y + 9))
        status_rendered = small_font.render(status, True, (170, 218, 151) if is_ready else MUTED)
        screen.blit(status_rendered, (row.right - status_rendered.get_width() - 12, row.y + 9))
        y += 44

    current = flow.current_ready_player()
    if current is not None:
        player = flow.players[current]
        name = str(player.get("name") or f"Gracz {current + 1}")
        prompt = small_font.render(f"{name}: potwierdź gotowość do wejścia na Radę.", True, MUTED)
        screen.blit(prompt, prompt.get_rect(center=(panel.centerx, panel.bottom - 84)))
        button = FlowButton("PRZEJDŹ DO RADY", (panel.centerx - 160, panel.bottom - 58, 320, 42), flow.confirm_ready)
        button.draw(screen, font, mouse)
        buttons.append(button)

    return buttons


def _advance_timed_phase(flow):
    now = pygame.time.get_ticks()
    elapsed = now - flow.phase_started_at

    if flow.phase == "news" and elapsed >= NEWS_DURATION_MS:
        flow.change_phase("event")
        return

    if flow.phase == "event" and elapsed >= EVENT_VISIBLE_MS:
        if flow.is_instant:
            flow.change_phase("event_slide")
        else:
            flow.change_phase("production")
        return

    if flow.phase == "event_slide" and elapsed >= EVENT_SLIDE_MS:
        flow.change_phase("production")


def _cover_finished_instant_event(screen, font, small_font, flow):
    if not flow.is_instant:
        return
    sw = screen.get_width()
    rect = pygame.Rect(max(24, sw // 2 - 470), 94, min(940, sw - 48), 82)
    _panel(screen, rect, alpha=232, border=(100, 110, 116))
    screen.blit(font.render("Wydarzenie Świata rozpatrzone", True, TEXT), (rect.x + 16, rect.y + 14))
    label = small_font.render("Karta natychmiastowa trafiła na stos odrzuconych.", True, MUTED)
    screen.blit(label, (rect.x + 16, rect.y + 48))


def draw_council(screen, title_font, font, small_font, mouse, round_number):
    """Wieści -> Wydarzenie -> Produkcja -> gotowość -> właściwa Rada."""
    flow = _flow(round_number)
    _advance_timed_phase(flow)

    if flow.phase == "council":
        buttons = council_ui.draw_council(screen, title_font, font, small_font, mouse, round_number)
        _cover_finished_instant_event(screen, font, small_font, flow)
        return buttons

    _load_background(screen)

    if flow.phase == "news":
        _draw_news(screen, title_font, font, flow)
        return []

    if flow.phase == "event":
        _draw_event_card(screen, title_font, font, small_font, flow)
        return []

    if flow.phase == "event_slide":
        elapsed = pygame.time.get_ticks() - flow.phase_started_at
        progress = max(0.0, min(1.0, elapsed / EVENT_SLIDE_MS))
        if not flow.rustle_played:
            flow.rustle_played = True
            _play_parchment_rustle()
        y_offset = int(progress * (screen.get_height() + 180))
        _draw_event_card(screen, title_font, font, small_font, flow, y_offset=y_offset)
        return []

    if flow.phase == "production":
        return _draw_production(screen, title_font, font, small_font, mouse, flow)

    return _draw_ready(screen, title_font, font, small_font, mouse, flow)
