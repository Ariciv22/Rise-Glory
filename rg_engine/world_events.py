from __future__ import annotations

import copy
import random
from typing import Any, Iterable

from rg_engine.world import current_world_level

_EVENT_REGISTRY: dict[str, dict[str, Any]] = {}
_DRAW_PILES: dict[int, list[str]] = {level: [] for level in range(1, 5)}
_DISCARD_PILES: dict[int, list[str]] = {level: [] for level in range(1, 5)}
_ACTIVE_EVENTS: list[dict[str, Any]] = []
_HISTORY: list[dict[str, Any]] = []
_LAST_EVENT_ID_BY_LEVEL: dict[int, str | None] = {level: None for level in range(1, 5)}

DURATION_INSTANT = "instant"
DURATION_UNTIL_NEXT_COUNCIL = "until_next_council"
DURATION_UNTIL_RESOLVED = "until_resolved"


def _level(value: Any) -> int:
    return max(1, min(4, int(value or 1)))


def register_world_event(definition: dict[str, Any]) -> dict[str, Any]:
    event = copy.deepcopy(definition)
    event_id = str(event.get("id") or "").strip()
    if not event_id:
        raise ValueError("Wydarzenie Swiata wymaga pola id.")
    event["id"] = event_id
    event.setdefault("name", event_id)
    event.setdefault("description", "")
    event.setdefault("effect_text", "")
    event.setdefault("duration", DURATION_INSTANT)
    event.setdefault("effects", [])
    event.setdefault("modifiers", {})
    event["world_level"] = _level(event.get("world_level", 1))
    event.setdefault("problem", None)
    _EVENT_REGISTRY[event_id] = event
    return copy.deepcopy(event)


def registered_world_events(world_level: int | None = None) -> list[dict[str, Any]]:
    events = list(_EVENT_REGISTRY.values())
    if world_level is not None:
        target = _level(world_level)
        events = [event for event in events if _level(event.get("world_level")) == target]
    return [copy.deepcopy(event) for event in events]


def reset_world_event_deck() -> None:
    global _DRAW_PILES, _DISCARD_PILES, _ACTIVE_EVENTS, _HISTORY, _LAST_EVENT_ID_BY_LEVEL
    _DRAW_PILES = {level: [] for level in range(1, 5)}
    _DISCARD_PILES = {level: [] for level in range(1, 5)}
    _ACTIVE_EVENTS = []
    _HISTORY = []
    _LAST_EVENT_ID_BY_LEVEL = {level: None for level in range(1, 5)}


def active_world_events(duration: str | None = None) -> list[dict[str, Any]]:
    events = _ACTIVE_EVENTS
    if duration is not None:
        events = [event for event in events if event.get("duration") == duration]
    return copy.deepcopy(events)


def active_world_event() -> dict[str, Any] | None:
    """Zgodność ze starszym API: zwraca ostatnie aktywne wydarzenie."""
    return copy.deepcopy(_ACTIVE_EVENTS[-1]) if _ACTIVE_EVENTS else None


def world_event_history() -> list[dict[str, Any]]:
    return copy.deepcopy(_HISTORY)


def _history_entry(event: dict[str, Any], status: str, ending: str = "") -> dict[str, Any]:
    entry = copy.deepcopy(event)
    entry["history_status"] = status
    entry["ending"] = ending
    return entry


def _append_history(event: dict[str, Any], status: str, ending: str = "") -> None:
    _HISTORY.append(_history_entry(event, status, ending))


def _discard(event: dict[str, Any]) -> None:
    level = _level(event.get("world_level", 1))
    event_id = str(event.get("id") or "")
    if event_id and event_id not in _DISCARD_PILES[level]:
        _DISCARD_PILES[level].append(event_id)


def world_event_modifier(name: str, default: int = 0) -> int:
    total = int(default)
    for event in _ACTIVE_EVENTS:
        total += int((event.get("modifiers") or {}).get(name, 0) or 0)
    return total


def price_with_world_event(base_price: int) -> int:
    base = max(0, int(base_price or 0))
    if base <= 0:
        return 0
    return max(1, base + world_event_modifier("market_price_modifier"))


def movement_cost_with_world_event(base_cost: int) -> int:
    base = max(1, int(base_cost or 1))
    if base < 2:
        return base
    return max(1, base + world_event_modifier("difficult_terrain_action_modifier"))


def healing_cost_with_world_event(base_cost: int) -> int:
    base = max(1, int(base_cost or 1))
    return max(1, base + world_event_modifier("healing_cost_modifier"))


def _apply_instant_effect(effect: dict[str, Any], players: Iterable[dict]) -> str:
    effect_type = str(effect.get("type") or "")
    amount = int(effect.get("amount", 0) or 0)

    if effect_type == "gold":
        for player in players:
            current = max(0, int(player.get("gold", 0) or 0))
            player["gold"] = max(0, current + amount)
        if amount >= 0:
            return f"Kazdy bohater otrzymuje {amount} monet."
        return f"Kazdy bohater traci do {abs(amount)} monet."

    if effect_type == "food":
        item = str(effect.get("item") or "Bochenek chleba")
        for player in players:
            food = player.setdefault("food", [])
            if amount > 0:
                food.extend([item] * amount)
            elif amount < 0:
                for _ in range(abs(amount)):
                    if item in food:
                        food.remove(item)
        if amount >= 0:
            return f"Kazdy bohater otrzymuje {amount}x {item}."
        return f"Kazdy bohater traci do {abs(amount)}x {item}."

    return ""


def _eligible_ids(world_level: int) -> list[str]:
    target = _level(world_level)
    return [
        event_id
        for event_id, event in _EVENT_REGISTRY.items()
        if _level(event.get("world_level", 1)) == target
    ]


def _refill_draw_pile(world_level: int, rng) -> None:
    level = _level(world_level)
    if _DISCARD_PILES[level]:
        ids = list(_DISCARD_PILES[level])
        _DISCARD_PILES[level] = []
    else:
        # Pierwsze tasowanie danego poziomu bierze wszystkie jego karty.
        ids = _eligible_ids(level)
        active_ids = {str(event.get("id")) for event in _ACTIVE_EVENTS}
        ids = [event_id for event_id in ids if event_id not in active_ids]

    rng.shuffle(ids)
    last_id = _LAST_EVENT_ID_BY_LEVEL.get(level)
    if len(ids) > 1 and last_id and ids[-1] == last_id:
        ids[0], ids[-1] = ids[-1], ids[0]
    _DRAW_PILES[level] = ids


def expire_until_next_council() -> list[dict[str, Any]]:
    """Wygasza karty czasowe przed odsłonięciem kolejnych Wieści ze świata."""
    expired = []
    remaining = []
    for event in _ACTIVE_EVENTS:
        if event.get("duration") == DURATION_UNTIL_NEXT_COUNCIL:
            expired.append(event)
            _discard(event)
            _append_history(event, "expired", "Wygasło przy rozpoczęciu kolejnej Rady.")
        else:
            remaining.append(event)
    _ACTIVE_EVENTS[:] = remaining
    return copy.deepcopy(expired)


def resolve_problem_event(event_id: str, resolved_by: str = "") -> dict[str, Any] | None:
    """Kończy aktywny problem; warstwa mapy odpowiada za test i nagrodę."""
    for index, event in enumerate(list(_ACTIVE_EVENTS)):
        if str(event.get("id")) != str(event_id):
            continue
        if event.get("duration") != DURATION_UNTIL_RESOLVED:
            return None
        resolved = _ACTIVE_EVENTS.pop(index)
        _discard(resolved)
        ending = "Problem rozwiązany."
        if resolved_by:
            ending = f"Rozwiązane przez {resolved_by}."
        _append_history(resolved, "resolved", ending)
        return copy.deepcopy(resolved)
    return None


def activate_world_event(event_id: str, players: Iterable[dict]) -> tuple[dict[str, Any], str]:
    if event_id not in _EVENT_REGISTRY:
        raise KeyError(f"Nieznane Wydarzenie Swiata: {event_id}")

    event = copy.deepcopy(_EVENT_REGISTRY[event_id])
    effect_messages = []
    players_list = list(players)
    for effect in event.get("effects", []) or []:
        message = _apply_instant_effect(effect, players_list)
        if message:
            effect_messages.append(message)

    duration = str(event.get("duration") or DURATION_INSTANT)
    if duration == DURATION_INSTANT:
        _discard(event)
        _append_history(event, "instant", "Rozpatrzone natychmiast.")
    else:
        _ACTIVE_EVENTS.append(event)

    level = _level(event.get("world_level", 1))
    _LAST_EVENT_ID_BY_LEVEL[level] = event_id
    message = event.get("effect_text") or " ".join(effect_messages)
    return copy.deepcopy(event), str(message).strip()


def draw_next_world_event(
    players: Iterable[dict],
    rng=None,
    world_level: int | None = None,
    begin_council: bool = True,
) -> tuple[dict[str, Any] | None, str]:
    """Dobiera losową kartę wyłącznie z talii aktualnego Poziomu Świata.

    Domyślnie wywołanie oznacza rozpoczęcie kolejnej Rady, dlatego najpierw
    wygaszane są efekty `until_next_council`.
    """
    rng = rng or random
    if begin_council:
        expire_until_next_council()

    level = _level(world_level if world_level is not None else current_world_level(players))
    if not _eligible_ids(level):
        return None, f"Brak zarejestrowanych kart Wydarzen Swiata poziomu {level}."

    if not _DRAW_PILES[level]:
        _refill_draw_pile(level, rng)
    if not _DRAW_PILES[level]:
        return None, f"Brak dostepnych kart Wydarzen Swiata poziomu {level}."

    event_id = _DRAW_PILES[level].pop()
    return activate_world_event(event_id, players)
