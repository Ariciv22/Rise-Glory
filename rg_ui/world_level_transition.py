from __future__ import annotations

import pygame

from rg_core.data import GOLD, TEXT
from rg_engine.world import consume_world_level_changes

_TRANSITION = None
_DURATION_MS = 3200
_ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}


def reset_world_level_transition() -> None:
    global _TRANSITION
    _TRANSITION = None


def _poll_transition():
    global _TRANSITION
    changes = consume_world_level_changes()
    if changes:
        previous, level = changes[-1]
        _TRANSITION = {
            "previous": int(previous),
            "level": int(level),
            "expires_at": pygame.time.get_ticks() + _DURATION_MS,
        }

    if _TRANSITION and pygame.time.get_ticks() >= int(_TRANSITION["expires_at"]):
        _TRANSITION = None
    return _TRANSITION


def is_world_level_transition_active() -> bool:
    """Ekran awansu jest modalny, ale znika sam i nie ma przycisku."""
    return _poll_transition() is not None


def draw_world_level_transition(screen, title_font, font, small_font) -> bool:
    transition = _poll_transition()
    if not transition:
        return False

    level = int(transition["level"])
    sw, sh = screen.get_size()

    shade = pygame.Surface((sw, sh), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 218))
    screen.blit(shade, (0, 0))

    width = min(760, max(520, sw - 220))
    height = min(270, max(210, int(sh * 0.28)))
    card = pygame.Rect((sw - width) // 2, (sh - height) // 2, width, height)

    surface = pygame.Surface(card.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, (12, 15, 18, 246), surface.get_rect(), border_radius=16)
    pygame.draw.rect(surface, GOLD, surface.get_rect(), 3, border_radius=16)
    inner = surface.get_rect().inflate(-18, -18)
    pygame.draw.rect(surface, (83, 67, 41, 150), inner, 1, border_radius=12)
    screen.blit(surface, card.topleft)

    heading = title_font.render(f"POZIOM ŚWIATA {_ROMAN.get(level, str(level))}", True, TEXT)
    screen.blit(heading, heading.get_rect(center=(card.centerx, card.y + 82)))

    pygame.draw.line(
        screen,
        GOLD,
        (card.x + 110, card.y + 128),
        (card.right - 110, card.y + 128),
        2,
    )

    message = font.render("Świat wkroczył na kolejny etap.", True, TEXT)
    screen.blit(message, message.get_rect(center=(card.centerx, card.y + 166)))

    info = small_font.render("Nowe oferty i kolejne wyzwania korzystają z aktualnego Poziomu Świata.", True, (190, 181, 160))
    screen.blit(info, info.get_rect(center=(card.centerx, card.y + 204)))
    return True
