from __future__ import annotations

from pathlib import Path
from typing import Callable

import pygame

from rg_core.data import BG, GOLD, MUTED, TEXT
from rg_ui.common import Button, draw_lines, wrap
from rg_ui import council as council_ui

NEWS_DURATION_MS = 1500
EVENT_VISIBLE_MS = 3600
EVENT_SLIDE_MS = 700

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

    @property
    def players(self):
        return self.session.players

    @property
    def event(self):
        return self.session.world_event or {}

    @property
    def is_instant(self):
        return self.event.get("duration") == "instant"

    def change_phase(self, phase: str):
        self.phase = phase
        self.phase_started_at = pygame.time.get_ticks()

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
            flow.change_phase("ready")
        return

    if flow.phase == "event_slide" and elapsed >= EVENT_SLIDE_MS:
        flow.change_phase("ready")


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
    """Frontowy przepływ Rady, a po potwierdzeniach delegacja do istniejącego ekranu handlu."""
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

    return _draw_ready(screen, title_font, font, small_font, mouse, flow)
