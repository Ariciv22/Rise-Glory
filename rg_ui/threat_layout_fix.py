from __future__ import annotations

import math

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_engine.problem_knowledge import problem_knowledge_view
from rg_world.world_event_markers import (
    active_camera,
    active_problem_event,
    marker_event_ids_on_tile,
    marker_tile,
    problem_marker_preview,
)

_INSTALL_DONE = False
_PREVIEW_PAGE = 0
_PREVIEW_PAGE_SIZE = 4
_PREVIEW_PREV_RECT = None
_PREVIEW_NEXT_RECT = None


def _marker_screen_rect(marker_ref: str):
    tile = marker_tile(marker_ref)
    camera = active_camera()
    if tile is None or camera is None:
        return None
    refs = marker_event_ids_on_tile(tile)
    try:
        index = refs.index(str(marker_ref))
    except ValueError:
        index = 0
    col = index % 3
    row = index // 3
    sx, sy = tile.center(camera)
    diameter = max(28, int(50 * camera.zoom))
    center = (
        int(sx + (-40 + col * 28) * camera.zoom),
        int(sy + (-35 + row * 30) * camera.zoom),
    )
    size = diameter + 10
    return pygame.Rect(center[0] - size // 2, center[1] - size // 2, size, size)


def _draw_problem_preview(screen, font, small_font):
    global _PREVIEW_PAGE, _PREVIEW_PREV_RECT, _PREVIEW_NEXT_RECT
    from rg_ui import threats as threat_ui
    from rg_ui import world_state

    marker_ref = world_state._PROBLEM_PREVIEW_ID
    if not marker_ref or world_state._PROBLEM_SESSION:
        return
    preview = problem_marker_preview(marker_ref)
    if preview is None:
        return

    world_state._draw_modal_shade(screen)
    sw, sh = screen.get_size()
    card = pygame.Rect(sw // 2 - 410, sh // 2 - 310, 820, 620)
    world_state._panel(screen, card, alpha=246)

    title = preview["name"]
    if preview.get("display_number"):
        title = f"#{preview['display_number']}  {title}"
    screen.blit(font.render(title, True, TEXT), (card.x + 28, card.y + 22))
    world_state._PREVIEW_CLOSE_RECT = pygame.Rect(card.right - 50, card.y + 16, 32, 32)
    pygame.draw.rect(screen, (53, 41, 35), world_state._PREVIEW_CLOSE_RECT, border_radius=8)
    close = font.render("×", True, TEXT)
    screen.blit(close, close.get_rect(center=world_state._PREVIEW_CLOSE_RECT.center))

    y = card.y + 66
    if preview["markers_total"] > 1:
        status = f"Punkt {preview['marker_id']} | Pozostało {preview['markers_remaining']}/{preview['markers_total']}"
        screen.blit(small_font.render(status, True, GOLD), (card.x + 28, y))
        y += 26
    y = world_state._draw_wrapped(
        screen, small_font, preview["description"],
        pygame.Rect(card.x + 28, y, card.width - 56, 66), MUTED, max_lines=3,
    )
    y += 6
    screen.blit(small_font.render("Aktywny efekt:", True, GOLD), (card.x + 28, y))
    y += 22
    y = world_state._draw_wrapped(
        screen, small_font, preview["effect"],
        pygame.Rect(card.x + 28, y, card.width - 56, 58), TEXT, max_lines=3,
    )
    y += 6
    condition = f"Warunek zakończenia: {preview['condition']}"
    y = world_state._draw_wrapped(
        screen, small_font, condition,
        pygame.Rect(card.x + 28, y, card.width - 56, 44), TEXT, max_lines=2,
    )
    y += 8

    player = threat_ui._CURRENT_PLAYER
    event = active_problem_event(marker_ref)
    view = problem_knowledge_view(player, event) if player is not None and event is not None else None
    _PREVIEW_PREV_RECT = None
    _PREVIEW_NEXT_RECT = None

    if not view or not view["investigated"]:
        screen.blit(small_font.render("Status dla tego bohatera: NIEZBADANE", True, (218, 150, 105)), (card.x + 28, y))
        y += 28
        world_state._draw_wrapped(
            screen, small_font,
            "Sposoby rozwiązania są ukryte. Bohater musi osobiście użyć „Zbadaj problem” na tym heksie za 1 Akcję.",
            pygame.Rect(card.x + 28, y, card.width - 56, 60), MUTED, max_lines=3,
        )
    else:
        screen.blit(small_font.render("Status dla tego bohatera: ZBADANE", True, GOLD), (card.x + 28, y))
        y += 28
        methods = view.get("methods", [])
        pages = max(1, math.ceil(len(methods) / _PREVIEW_PAGE_SIZE))
        _PREVIEW_PAGE = max(0, min(_PREVIEW_PAGE, pages - 1))
        start = _PREVIEW_PAGE * _PREVIEW_PAGE_SIZE
        for method in methods[start:start + _PREVIEW_PAGE_SIZE]:
            state = method.get("availability") or {}
            mode = state.get("mode")
            if mode == "automatic":
                check = "Automatyczna"
            elif mode == "combat":
                check = "Pełna Walka"
            else:
                check = f"{state.get('stat', '-')} DC {state.get('difficulty', '-')}"
            line = (
                f"• {method.get('label', 'Metoda')} — {check} | "
                f"Wymaga: {state.get('requirements_text', 'brak')} | "
                f"Zużywa: {state.get('costs_text', 'brak')}"
            )
            y = world_state._draw_wrapped(
                screen, small_font, line,
                pygame.Rect(card.x + 34, y, card.width - 68, 44), TEXT, max_lines=2,
            )
            if state.get("failure_revealed"):
                failure = str(method.get("failure_text") or "Konsekwencja została poznana.")
                y = world_state._draw_wrapped(
                    screen, small_font, f"  Poznana porażka: {failure}",
                    pygame.Rect(card.x + 42, y, card.width - 84, 36), (218, 150, 105), max_lines=2,
                )
            y += 5

        if pages > 1:
            nav_y = card.bottom - 70
            _PREVIEW_PREV_RECT = pygame.Rect(card.centerx - 170, nav_y, 110, 34)
            _PREVIEW_NEXT_RECT = pygame.Rect(card.centerx + 60, nav_y, 110, 34)
            for rect, label, enabled in (
                (_PREVIEW_PREV_RECT, "←", _PREVIEW_PAGE > 0),
                (_PREVIEW_NEXT_RECT, "→", _PREVIEW_PAGE < pages - 1),
            ):
                pygame.draw.rect(screen, (55, 47, 37) if enabled else (38, 38, 38), rect, border_radius=7)
                pygame.draw.rect(screen, GOLD if enabled else (70, 70, 70), rect, 1, border_radius=7)
                rendered = small_font.render(label, True, TEXT if enabled else MUTED)
                screen.blit(rendered, rendered.get_rect(center=rect.center))
            page = small_font.render(f"Metody {_PREVIEW_PAGE + 1}/{pages}", True, MUTED)
            screen.blit(page, page.get_rect(center=(card.centerx, nav_y + 17)))

    screen.blit(
        small_font.render("Nagroda pozostaje ukryta do całkowitego rozwiązania Zagrożenia.", True, GOLD),
        (card.x + 28, card.bottom - 30),
    )


def install_threat_layout_fix() -> None:
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return
    from rg_ui import world_state

    original_clicked = world_state._WorldStateController.clicked

    def clicked_with_preview_pages(self, pos):
        global _PREVIEW_PAGE
        if world_state._PROBLEM_PREVIEW_ID and world_state._PROBLEM_SESSION is None:
            if _PREVIEW_PREV_RECT and _PREVIEW_PREV_RECT.collidepoint(pos) and _PREVIEW_PAGE > 0:
                _PREVIEW_PAGE -= 1
                self.action = "world_state"
                return True
            if _PREVIEW_NEXT_RECT and _PREVIEW_NEXT_RECT.collidepoint(pos):
                player = __import__("rg_ui.threats", fromlist=["_CURRENT_PLAYER"])._CURRENT_PLAYER
                event = active_problem_event(world_state._PROBLEM_PREVIEW_ID)
                view = problem_knowledge_view(player, event) if player is not None and event is not None else None
                pages = max(1, math.ceil(len((view or {}).get("methods", [])) / _PREVIEW_PAGE_SIZE))
                if _PREVIEW_PAGE < pages - 1:
                    _PREVIEW_PAGE += 1
                    self.action = "world_state"
                    return True
        return original_clicked(self, pos)

    world_state._marker_screen_rect = _marker_screen_rect
    world_state._draw_problem_preview = _draw_problem_preview
    world_state._WorldStateController.clicked = clicked_with_preview_pages
    _INSTALL_DONE = True
