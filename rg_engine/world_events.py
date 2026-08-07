from __future__ import annotations

import copy
import random
from typing import Any, Iterable

_EVENT_REGISTRY: dict[str, dict[str, Any]] = {}
_DRAW_PILE: list[str] = []
_DISCARD_PILE: list[str] = []
_ACTIVE_EVENT: dict[str, Any] | None = None
_HISTORY: list[dict[str, Any]] = []
_LAST_EVENT_ID: str | None = None


def register_world_event(definition: dict[str, Any]) -> dict[str, Any]:
    event = copy.deepcopy(definition)
    event_id = str(event.get("id") or "").strip()
    if not event_id:
        raise ValueError("Wydarzenie Swiata wymaga pola id.")
    event["id"] = event_id
    event.setdefault("name", event_id)
    event.setdefault("description", "")
    event.setdefault("effect_text", "")
    event.setdefault("duration", "instant")
    event.setdefault("effects", [])
    event.setdefault("modifiers", {})
    _EVENT_REGISTRY[event_id] = event
    return copy.deepcopy(event)


def registered_world_events() -> list[dict[str, Any]]:
    return [copy.deepcopy(event) for event in _EVENT_REGISTRY.values()]


def reset_world_event_deck() -> None:
    global _DRAW_PILE, _DISCARD_PILE, _ACTIVE_EVENT, _HISTORY, _LAST_EVENT_ID
    _DRAW_PILE = []
    _DISCARD_PILE = []
    _ACTIVE_EVENT = None
    _HISTORY = []
    _LAST_EVENT_ID = None


def active_world_event() -> dict[str, Any] | None:
    return copy.deepcopy(_ACTIVE_EVENT) if _ACTIVE_EVENT else None


def world_event_history() -> list[dict[str, Any]]:
    return copy.deepcopy(_HISTORY)


def world_event_modifier(name: str, default: int = 0) -> int:
    if not _ACTIVE_EVENT:
        return int(default)
    return int((_ACTIVE_EVENT.get("modifiers") or {}).get(name, default) or 0)


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
    affected = 0

    if effect_type == "gold":
        for player in players:
            current = max(0, int(player.get("gold", 0) or 0))
            player["gold"] = max(0, current + amount)
            affected += 1
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
            affected += 1
        if amount >= 0:
            return f"Kazdy bohater otrzymuje {amount}x {item}."
        return f"Kazdy bohater traci do {abs(amount)}x {item}."

    return ""


def _refill_draw_pile(rng) -> None:
    global _DRAW_PILE
    ids = list(_EVENT_REGISTRY.keys())
    rng.shuffle(ids)
    if len(ids) > 1 and _LAST_EVENT_ID and ids[-1] == _LAST_EVENT_ID:
        ids[0], ids[-1] = ids[-1], ids[0]
    _DRAW_PILE = ids


def activate_world_event(event_id: str, players: Iterable[dict]) -> tuple[dict[str, Any], str]:
    global _ACTIVE_EVENT, _LAST_EVENT_ID
    if event_id not in _EVENT_REGISTRY:
        raise KeyError(f"Nieznane Wydarzenie Swiata: {event_id}")

    if _ACTIVE_EVENT:
        _DISCARD_PILE.append(str(_ACTIVE_EVENT.get("id")))

    event = copy.deepcopy(_EVENT_REGISTRY[event_id])
    effect_messages = []
    players_list = list(players)
    for effect in event.get("effects", []) or []:
        message = _apply_instant_effect(effect, players_list)
        if message:
            effect_messages.append(message)

    _ACTIVE_EVENT = event
    _LAST_EVENT_ID = event_id
    _HISTORY.append(copy.deepcopy(event))

    message = event.get("effect_text") or " ".join(effect_messages)
    return copy.deepcopy(event), str(message).strip()


def draw_next_world_event(players: Iterable[dict], rng=None) -> tuple[dict[str, Any] | None, str]:
    if not _EVENT_REGISTRY:
        return None, "Brak zarejestrowanych kart Wydarzen Swiata."
    rng = rng or random
    if not _DRAW_PILE:
        _refill_draw_pile(rng)
    event_id = _DRAW_PILE.pop()
    return activate_world_event(event_id, players)
