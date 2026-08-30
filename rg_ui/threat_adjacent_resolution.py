from __future__ import annotations

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_engine.threats import marker_count, parse_marker_ref
from rg_ui import world_state
from rg_ui.threats import threat_hex_action_state
from rg_world import map as world_map
from rg_world.quest_markers import quest_marker_ids_on_tile
from rg_world.world_event_markers import (
    active_problem_event,
    bound_tiles,
    marker_event_ids_on_tile,
)


_INSTALLED = False
_ORIGINAL_DRAW_HEX_ACTIONS = None


def _fit(font, text, width):
    value = str(text or "")
    if font.size(value)[0] <= width:
        return value
    suffix = "..."
    while value and font.size(value + suffix)[0] > width:
        value = value[:-1]
    return value.rstrip() + suffix


def _blocks_own_marker_tile(event):
    """Czy Zagrozenie blokuje wejscie dokladnie na swoje znaczniki."""
    problem = event.get("problem") or {}
    for effect in problem.get("effects", []) or []:
        if not isinstance(effect, dict):
            continue
        if str(effect.get("type") or "") != "block_entry":
            continue
        scope = str(effect.get("scope") or "global").casefold()
        if scope in {"marker", "marker_tile", "marker_tiles", "local"}:
            return True
    return False


def _adjacent_blocked_marker_refs(token):
    """Znaczniki zablokowanych Problemow na heksach sasiednich bohaterowi."""
    origin = getattr(token, "tile", None)
    if origin is None:
        return []

    result = []
    seen = set()
    for tile in bound_tiles():
        if tile is origin or not world_map.are_adjacent(origin, tile):
            continue
        for marker_ref in marker_event_ids_on_tile(tile):
            if marker_ref in seen:
                continue
            event = active_problem_event(marker_ref)
            if event is None or not _blocks_own_marker_tile(event):
                continue
            seen.add(marker_ref)
            result.append(marker_ref)
    return result


def _existing_action_stack_height(token):
    """Wysokosc juz narysowanych paneli Problemow i Questow nad kompasem."""
    tile = getattr(token, "tile", None)
    if tile is None:
        return 0

    height = 0
    threat_count = len(marker_event_ids_on_tile(tile))
    if threat_count:
        height += 44 + threat_count * 40

    quest_count = len(quest_marker_ids_on_tile(tile))
    if quest_count:
        if height:
            height += 8
        height += 44 + quest_count * 40
    return height


def _draw_adjacent_blocked_actions(
    screen,
    small_font,
    players,
    tokens,
    active_player_index,
    right,
):
    if not players or active_player_index >= len(players) or active_player_index >= len(tokens):
        return

    player = players[active_player_index]
    token = tokens[active_player_index]
    refs = _adjacent_blocked_marker_refs(token)
    if not refs:
        return

    # Maksymalnie cztery jednoczesnie. Przy Lawinach znacznikow jest piec,
    # ale z jednego heksa praktycznie nie powinno byc widocznych wiecej niz kilka.
    refs = refs[:4]
    panel_h = 44 + len(refs) * 40
    stack_h = _existing_action_stack_height(token)
    bottom_margin = 62 + stack_h + (8 if stack_h else 0)
    panel = pygame.Rect(
        right.x + 12,
        max(right.y + 8, right.bottom - panel_h - bottom_margin),
        right.width - 24,
        panel_h,
    )

    pygame.draw.rect(screen, (18, 24, 28), panel, border_radius=10)
    pygame.draw.rect(screen, GOLD, panel, 1, border_radius=10)
    title = "Zablokowany heks obok" if len(refs) == 1 else "Zablokowane heksy obok"
    screen.blit(small_font.render(title, True, GOLD), (panel.x + 12, panel.y + 10))

    y = panel.y + 36
    mouse = pygame.mouse.get_pos()
    for marker_ref in refs:
        state = threat_hex_action_state(player, token, marker_ref)
        if state["event"] is None:
            continue

        _event_id, marker_id = parse_marker_ref(marker_ref)
        total = marker_count(state["event"])
        suffix = f" [{marker_id}/{total}]" if total > 1 else ""
        label = _fit(
            small_font,
            f"{state['label']}{suffix} - z sasiedniego heksa",
            panel.width - 38,
        )
        rect = pygame.Rect(panel.x + 10, y, panel.width - 20, 34)
        pygame.draw.rect(
            screen,
            (63, 51, 35) if state["enabled"] else (43, 44, 45),
            rect,
            border_radius=7,
        )
        pygame.draw.rect(
            screen,
            GOLD if state["enabled"] else (76, 76, 76),
            rect,
            1,
            border_radius=7,
        )
        screen.blit(
            small_font.render(label, True, TEXT if state["enabled"] else MUTED),
            (rect.x + 9, rect.y + 8),
        )

        # Istniejacy kontroler Problemow obsluzy klik i uruchomi badanie/probe.
        world_state._HEX_ACTION_RECTS.append(
            (rect, marker_ref, state["enabled"], state["reason"])
        )

        if not state["enabled"] and state["reason"] and rect.collidepoint(mouse):
            tooltip = small_font.render(state["reason"], True, TEXT)
            tip = pygame.Rect(
                mouse[0] + 14,
                mouse[1] + 14,
                tooltip.get_width() + 16,
                tooltip.get_height() + 12,
            )
            pygame.draw.rect(screen, (18, 20, 22), tip, border_radius=7)
            pygame.draw.rect(screen, GOLD, tip, 1, border_radius=7)
            screen.blit(tooltip, (tip.x + 8, tip.y + 6))
        y += 40


def _draw_hex_actions_with_adjacent_resolution(
    screen,
    small_font,
    players,
    tokens,
    active_player_index,
    right,
):
    result = _ORIGINAL_DRAW_HEX_ACTIONS(
        screen,
        small_font,
        players,
        tokens,
        active_player_index,
        right,
    )
    _draw_adjacent_blocked_actions(
        screen,
        small_font,
        players,
        tokens,
        active_player_index,
        right,
    )
    return result


def install_threat_adjacent_resolution():
    global _INSTALLED, _ORIGINAL_DRAW_HEX_ACTIONS
    if _INSTALLED:
        return

    # Instalujemy po rg_core.setup, kiedy world_state zawiera juz finalny lancuch
    # Zagrozen + Questow. Owijamy go, zamiast zastapic ktorakolwiek funkcje.
    _ORIGINAL_DRAW_HEX_ACTIONS = world_state._draw_hex_actions
    world_state._draw_hex_actions = _draw_hex_actions_with_adjacent_resolution
    _INSTALLED = True
