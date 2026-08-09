from __future__ import annotations

from pathlib import Path

import pygame

from rg_core.data import GOLD, TEXT
from rg_ui import council_market as market_ui
from rg_ui.council_market_full import draw_council as _draw_full_council

ROOT_DIR = Path(__file__).resolve().parents[1]
TURN_BANNER_MS = 1450

_BELL_CANDIDATES = (
    ROOT_DIR / "Dzwieki" / "rada_dzwonek.ogg",
    ROOT_DIR / "Dzwieki" / "rada_dzwonek.wav",
    ROOT_DIR / "Dźwięki" / "rada_dzwonek.ogg",
    ROOT_DIR / "Dźwięki" / "rada_dzwonek.wav",
)
_LAST_ACTIVE_PLAYER = None
_BANNER_STARTED_AT = 0
_BELL = None
_BELL_LOADED = False


def _load_bell():
    global _BELL, _BELL_LOADED
    if _BELL_LOADED:
        return _BELL
    _BELL_LOADED = True
    for path in _BELL_CANDIDATES:
        if not path.exists():
            continue
        try:
            _BELL = pygame.mixer.Sound(str(path))
        except (pygame.error, OSError):
            _BELL = None
        if _BELL is not None:
            break
    return _BELL


def _play_bell():
    bell = _load_bell()
    if bell is None:
        return
    try:
        bell.play()
    except pygame.error:
        pass


def _update_turn_banner(session):
    global _LAST_ACTIVE_PLAYER, _BANNER_STARTED_AT
    if session.stage != "turns":
        return
    active = session.active_player_index
    if active is None or active == _LAST_ACTIVE_PLAYER:
        return
    _LAST_ACTIVE_PLAYER = active
    _BANNER_STARTED_AT = pygame.time.get_ticks()
    _play_bell()


def _draw_turn_banner(screen, title_font, font, session):
    if session.stage != "turns" or session.active_player_index is None:
        return
    elapsed = pygame.time.get_ticks() - _BANNER_STARTED_AT
    if elapsed < 0 or elapsed >= TURN_BANNER_MS:
        return

    progress = elapsed / TURN_BANNER_MS
    alpha = 245
    if progress > 0.72:
        alpha = max(0, int(245 * (1.0 - (progress - 0.72) / 0.28)))

    sw, sh = screen.get_size()
    width = min(620, sw - 80)
    rect = pygame.Rect((sw - width) // 2, max(86, sh // 2 - 92), width, 184)
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, min(128, alpha // 2)))
    screen.blit(shade, (0, 0))

    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (13, 15, 18, alpha), panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, (*GOLD, alpha), panel.get_rect(), 2, border_radius=16)
    screen.blit(panel, rect.topleft)

    player = session.players[session.active_player_index]
    title = title_font.render("Kolej Gracza", True, TEXT)
    name = font.render(str(player.get("name", "Gracz")), True, GOLD)
    screen.blit(title, title.get_rect(center=(rect.centerx, rect.y + 62)))
    screen.blit(name, name.get_rect(center=(rect.centerx, rect.y + 122)))


def draw_council(screen, title_font, font, small_font, mouse, round_number):
    session = market_ui._session(round_number)
    _update_turn_banner(session)
    buttons = _draw_full_council(screen, title_font, font, small_font, mouse, round_number)
    _draw_turn_banner(screen, title_font, font, session)
    return buttons
