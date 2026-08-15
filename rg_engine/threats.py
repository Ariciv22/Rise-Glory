from __future__ import annotations

import copy
import random
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Callable

from rg_engine.heroes import apply_wounds, ensure_hero_state, heal_wounds, helper_bonus
from rg_engine.items import add_item, ensure_equipment_state, equipment_stat_bonus, normalise_item
from rg_engine.world import registered_players, update_world_level
from rg_engine.world_events import DURATION_UNTIL_RESOLVED, active_world_events, resolve_problem_event

PROBLEM_ACTION_COST = 1
PROBLEM_INVESTIGATION_ACTION_COST = 1
VALID_STATS = {"Walka", "Handel", "Intryga", "Dyplomacja", "Kultura", "Nauka"}

_THREAT_RUNTIME: dict[str, dict[str, Any]] = {}
_COMBAT_LAUNCHER: Callable[["ProblemAttemptSession", int, dict[str, Any]], tuple[bool, str]] | None = None


def _norm(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(ch for ch in text.encode("ascii", "ignore").decode("ascii").casefold() if ch.isalnum())


def _event_id(event_or_id: dict[str, Any] | str) -> str:
    if isinstance(event_or_id, dict):
        return str(event_or_id.get("id") or "")
    value = str(event_or_id or "")
    return value.split("::", 1)[0]


def parse_marker_ref(event_or_ref: dict[str, Any] | str, marker_id: str | int | None = None) -> tuple[str, str]:
    event_id = _event_id(event_or_ref)
    if marker_id is not None:
        return event_id, str(marker_id)
    if isinstance(event_or_ref, str) and "::" in event_or_ref:
        _event, _marker = event_or_ref.split("::", 1)
        return str(_event), str(_marker)
    return event_id, "1"


def make_marker_ref(event_id: str, marker_id: str | int) -> str:
    return f"{event_id}::{marker_id}"


def _problem(event: dict[str, Any]) -> dict[str, Any]:
    value = event.get("problem") or {}
    return value if isinstance(value, dict) else {}


def active_problem(event_or_id: dict[str, Any] | str) -> dict[str, Any] | None:
    event_id = _event_id(event_or_id)
    for event in active_world_events(DURATION_UNTIL_RESOLVED):
        if _event_id(event) == event_id:
            return event
    return None


def marker_count(event: dict[str, Any]) -> int:
    problem = _problem(event)
    raw = problem.get("marker_count", problem.get("markers", 1))
    if isinstance(raw, list):
        return max(1, len(raw))
    if isinstance(raw, dict):
        return max(1, int(raw.get("count", 1) or 1))
    return max(1, int(raw or 1))


def _used_display_numbers(exclude: str = "") -> set[int]:
    active_ids = {_event_id(event) for event in active_world_events(DURATION_UNTIL_RESOLVED)}
    return {
        int(runtime.get("display_number", 0) or 0)
        for event_id, runtime in _THREAT_RUNTIME.items()
        if event_id != exclude and event_id in active_ids and int(runtime.get("display_number", 0) or 0) > 0
    }


def _next_display_number(event_id: str) -> int:
    used = _used_display_numbers(event_id)
    number = 1
    while number in used:
        number += 1
    return number


def ensure_threat_runtime(event_or_id: dict[str, Any] | str) -> dict[str, Any] | None:
    event = active_problem(event_or_id)
    if event is None:
        return None
    event_id = _event_id(event)
    runtime = _THREAT_RUNTIME.get(event_id)
    expected_count = marker_count(event)
    if runtime is None:
        runtime = {
            "display_number": _next_display_number(event_id),
            "markers": {},
            "revealed_failures": set(),
            "contributors": set(),
            "last_resolution": None,
        }
        _THREAT_RUNTIME[event_id] = runtime
    markers = runtime.setdefault("markers", {})
    for index in range(1, expected_count + 1):
        marker_id = str(index)
        markers.setdefault(marker_id, {"resolved": False, "tile_id": None, "resolved_by": "", "method_id": ""})
    for marker_id in list(markers):
        if marker_id.isdigit() and int(marker_id) > expected_count and not markers[marker_id].get("resolved"):
            markers.pop(marker_id, None)
    return runtime


def reset_threat_runtime() -> None:
    _THREAT_RUNTIME.clear()


def threat_runtime_snapshot(event_or_id: dict[str, Any] | str) -> dict[str, Any] | None:
    runtime = ensure_threat_runtime(event_or_id)
    if runtime is None:
        return None
    result = copy.deepcopy(runtime)
    result["revealed_failures"] = sorted(result.get("revealed_failures", []))
    result["contributors"] = sorted(result.get("contributors", []))
    return result


def threat_display_number(event_or_id: dict[str, Any] | str) -> int:
    runtime = ensure_threat_runtime(event_or_id)
    return int(runtime.get("display_number", 0) or 0) if runtime else 0


def set_marker_tile(event_or_id: dict[str, Any] | str, marker_id: str | int, tile_id: int | None) -> None:
    runtime = ensure_threat_runtime(event_or_id)
    if runtime is None:
        return
    state = runtime["markers"].setdefault(str(marker_id), {"resolved": False})
    state["tile_id"] = None if tile_id is None else int(tile_id)


def marker_state(event_or_id: dict[str, Any] | str, marker_id: str | int = "1") -> dict[str, Any] | None:
    runtime = ensure_threat_runtime(event_or_id)
    if runtime is None:
        return None
    value = runtime["markers"].get(str(marker_id))
    return copy.deepcopy(value) if value else None


def unresolved_marker_ids(event_or_id: dict[str, Any] | str) -> list[str]:
    runtime = ensure_threat_runtime(event_or_id)
    if runtime is None:
        return []
    return [marker_id for marker_id, state in runtime["markers"].items() if not bool(state.get("resolved"))]


def marker_is_resolved(event_or_id: dict[str, Any] | str, marker_id: str | int = "1") -> bool:
    state = marker_state(event_or_id, marker_id)
    return bool(state and state.get("resolved"))


def _player_key(player: dict[str, Any]) -> str:
    number = player.get("player_number")
    if number is not None:
        return f"player:{number}"
    name = str(player.get("name") or "Bohater")
    return f"name:{name}"


def _find_player(key: str) -> dict[str, Any] | None:
    for player in registered_players():
        if _player_key(player) == key:
            return player
    return None


def _knowledge(player: dict[str, Any]) -> dict[str, Any]:
    raw = player.setdefault("threat_knowledge", {})
    if not isinstance(raw, dict):
        raw = {}
        player["threat_knowledge"] = raw
    return raw


def problem_investigated(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> bool:
    event_id = _event_id(event_or_id)
    return bool(active_problem(event_id) is not None and _knowledge(player).get(event_id, {}).get("investigated"))


def can_investigate_problem(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> tuple[bool, str]:
    event = active_problem(event_or_id)
    if event is None:
        return False, "Ten problem nie jest już aktywny."
    if problem_investigated(player, event):
        return True, "Problem został już zbadany przez tego bohatera."
    token = player.get("_token_ref")
    if token is None or int(getattr(token, "actions", 0) or 0) < PROBLEM_INVESTIGATION_ACTION_COST:
        return False, "Potrzebujesz 1 akcji, aby zbadać problem."
    return True, ""


def investigate_problem(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> tuple[bool, str]:
    event = active_problem(event_or_id)
    if event is None:
        return False, "Ten problem nie jest już aktywny."
    event_id = _event_id(event)
    if problem_investigated(player, event):
        return True, "Problem został już zbadany przez tego bohatera."
    allowed, message = can_investigate_problem(player, event)
    if not allowed:
        return False, message
    token = player.get("_token_ref")
    token.actions = max(0, int(token.actions) - PROBLEM_INVESTIGATION_ACTION_COST)
    _knowledge(player)[event_id] = {"investigated": True}
    ensure_threat_runtime(event)
    return True, "Problem zbadany. Odkryto dostępne sposoby rozwiązania."


def clear_problem_knowledge(player: dict[str, Any], event_or_id: dict[str, Any] | str | None = None) -> None:
    if event_or_id is None:
        player["threat_knowledge"] = {}
        return
    _knowledge(player).pop(_event_id(event_or_id), None)


def _retry_blocks(player: dict[str, Any]) -> set[str]:
    raw = player.setdefault("threat_retry_blocks", [])
    if isinstance(raw, set):
        return raw
    values = {str(value) for value in (raw or [])}
    player["threat_retry_blocks"] = sorted(values)
    return values


def _save_retry_blocks(player: dict[str, Any], values: set[str]) -> None:
    player["threat_retry_blocks"] = sorted(values)


def clear_problem_retry_blocks(player: dict[str, Any]) -> None:
    player["threat_retry_blocks"] = []


def problem_retry_blocked(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> bool:
    return _event_id(event_or_id) in _retry_blocks(player)


def _raw_methods(event: dict[str, Any]) -> list[dict[str, Any]]:
    methods = _problem(event).get("methods") or []
    return [copy.deepcopy(method) for method in methods if isinstance(method, dict)]


def validate_problem_definition(event: dict[str, Any]) -> tuple[bool, str]:
    problem = _problem(event)
    if not problem:
        return False, "Zagrożenie wymaga sekcji problem."
    methods = _raw_methods(event)
    if len(methods) < 2:
        return False, "Zagrożenie wymaga co najmniej dwóch sposobów rozwiązania."
    effects = problem.get("effects") or []
    if not effects and not event.get("modifiers"):
        return False, "Zagrożenie wymaga co najmniej jednego aktywnego negatywnego efektu."
    return True, ""


def available_problem_methods(event: dict[str, Any]) -> list[dict[str, Any]]:
    return _raw_methods(event)


def failure_revealed(event_or_id: dict[str, Any] | str, method_id: str) -> bool:
    runtime = ensure_threat_runtime(event_or_id)
    return bool(runtime and str(method_id) in runtime.get("revealed_failures", set()))


def _reveal_failure(event_or_id: dict[str, Any] | str, method_id: str) -> None:
    runtime = ensure_threat_runtime(event_or_id)
    if runtime is not None:
        runtime.setdefault("revealed_failures", set()).add(str(method_id))


def _specs(raw: Any) -> list[dict[str, Any]]:
    if raw in (None, "", [], {}):
        return []
    if isinstance(raw, str):
        return [{"type": "owned", "name": raw, "amount": 1}]
    if isinstance(raw, list):
        result: list[dict[str, Any]] = []
        for value in raw:
            result.extend(_specs(value))
        return result
    if not isinstance(raw, dict):
        return []
    if raw.get("type") or raw.get("kind"):
        value = copy.deepcopy(raw)
        value["type"] = str(value.get("type") or value.get("kind"))
        value.setdefault("amount", 1)
        return [value]

    result: list[dict[str, Any]] = []
    for key, value in raw.items():
        key_norm = str(key).casefold()
        if key_norm in {"gold", "zloto", "złoto"}:
            result.append({"type": "gold", "amount": int(value or 0)})
        elif key_norm in {"materials", "materialy", "materiały"} and isinstance(value, dict):
            result.extend({"type": "material", "name": str(name), "amount": int(amount or 0)} for name, amount in value.items())
        elif key_norm in {"goods", "towary", "good"}:
            if isinstance(value, dict):
                result.extend({"type": "good", "name": str(name), "amount": int(amount or 0)} for name, amount in value.items())
            elif isinstance(value, list):
                result.extend({"type": "good", "name": str(name), "amount": 1} for name in value)
            else:
                result.append({"type": "good", "name": str(value), "amount": 1})
        elif key_norm in {"items", "item", "przedmioty", "przedmiot"}:
            values = value if isinstance(value, list) else [value]
            result.extend({"type": "item", "name": str(name), "amount": 1} for name in values)
        elif key_norm in {"helpers", "helper", "pomocnicy", "pomocnik"}:
            values = value if isinstance(value, list) else [value]
            result.extend({"type": "helper", "name": str(name), "amount": 1} for name in values)
        elif key_norm in {"food", "jedzenie"}:
            if isinstance(value, dict):
                result.extend({"type": "food", "name": str(name), "amount": int(amount or 0)} for name, amount in value.items())
            else:
                values = value if isinstance(value, list) else [value]
                result.extend({"type": "food", "name": str(name), "amount": 1} for name in values)
        else:
            result.append({"type": str(key), "name": str(value), "amount": 1})
    return result


def method_requirements(method: dict[str, Any]) -> list[dict[str, Any]]:
    return _specs(method.get("requirements", method.get("requires", method.get("wymaga"))))


def method_costs(method: dict[str, Any]) -> list[dict[str, Any]]:
    return _specs(method.get("costs", method.get("consume", method.get("consumes", method.get("zuzywa", method.get("zużywa"))))))


def _named_count(values: list[Any], name: str) -> int:
    target = _norm(name)
    count = 0
    for value in values or []:
        if isinstance(value, dict):
            candidate = value.get("name") or value.get("id")
        else:
            candidate = value
        if _norm(candidate) == target:
            count += 1
    return count


def _item_count(player: dict[str, Any], name: str) -> int:
    ensure_equipment_state(player)
    target = _norm(name)
    count = 0
    for item in player.get("inventory", []) or []:
        normalised = normalise_item(item)
        if _norm(normalised.get("name")) == target or _norm(normalised.get("id")) == target:
            count += 1
    for item in (player.get("equipment") or {}).values():
        if not item:
            continue
        normalised = normalise_item(item)
        if _norm(normalised.get("name")) == target or _norm(normalised.get("id")) == target:
            count += 1
    return count


def _owned_count(player: dict[str, Any], name: str) -> int:
    return max(
        _item_count(player, name),
        _named_count(player.get("goods", []), name),
        _named_count(player.get("food", []), name),
        _named_count(player.get("helpers", []), name),
        int((player.get("materials") or {}).get(name, 0) or 0) if isinstance(player.get("materials"), dict) else _named_count(player.get("materials", []), name),
    )


def _spec_available(player: dict[str, Any], spec: dict[str, Any]) -> tuple[bool, str]:
    ensure_hero_state(player)
    kind = str(spec.get("type") or spec.get("kind") or "owned").casefold()
    name = str(spec.get("name") or "")
    amount = max(1, int(spec.get("amount", 1) or 1))
    available = 0
    label = name or kind
    if kind in {"gold", "zloto", "złoto"}:
        available = int(player.get("gold", 0) or 0)
        label = "Złoto"
    elif kind in {"material", "materialy", "materiały"}:
        materials = player.get("materials", {})
        available = int(materials.get(name, 0) or 0) if isinstance(materials, dict) else _named_count(materials, name)
    elif kind in {"good", "goods", "towar", "towary"}:
        available = _named_count(player.get("goods", []), name)
    elif kind in {"food", "jedzenie"}:
        available = _named_count(player.get("food", []), name)
    elif kind in {"item", "przedmiot"}:
        available = _item_count(player, name)
    elif kind in {"helper", "pomocnik"}:
        available = _named_count(player.get("helpers", []), name)
    else:
        available = _owned_count(player, name)
    if available >= amount:
        return True, ""
    return False, f"{label}: {available}/{amount}"


def _spec_text(spec: dict[str, Any]) -> str:
    kind = str(spec.get("type") or "owned").casefold()
    name = str(spec.get("name") or "")
    amount = max(1, int(spec.get("amount", 1) or 1))
    if kind in {"gold", "zloto", "złoto"}:
        return f"{amount} Złota"
    suffix = f"{amount}× " if amount > 1 else ""
    return f"{suffix}{name or kind}"


def method_state(player: dict[str, Any], event_or_id: dict[str, Any] | str, method: dict[str, Any]) -> dict[str, Any]:
    event = active_problem(event_or_id)
    method_id = str(method.get("id") or method.get("label") or "method")
    requirements = method_requirements(method)
    costs = method_costs(method)
    missing: list[str] = []
    if event is None:
        missing.append("Problem nieaktywny")
    if event is not None and problem_retry_blocked(player, event):
        missing.append("Kolejna próba dopiero w następnej turze")
    token = player.get("_token_ref")
    if token is None or int(getattr(token, "actions", 0) or 0) < PROBLEM_ACTION_COST:
        missing.append("Brak 1 Akcji")
    for spec in [*requirements, *costs]:
        ok, reason = _spec_available(player, spec)
        if not ok and reason not in missing:
            missing.append(reason)
    mode = str(method.get("mode") or method.get("type") or "").casefold()
    if not mode:
        mode = "automatic" if not method.get("stat") and method.get("difficulty") is None else "test"
    if mode == "test" and str(method.get("stat") or "") not in VALID_STATS:
        missing.append("Nieprawidłowa statystyka")
    return {
        "method_id": method_id,
        "available": not missing,
        "missing": missing,
        "requirements": requirements,
        "costs": costs,
        "requirements_text": ", ".join(_spec_text(spec) for spec in requirements) or "brak",
        "costs_text": ", ".join(_spec_text(spec) for spec in costs) or "brak",
        "mode": mode,
        "stat": str(method.get("stat") or ""),
        "difficulty": int(method.get("difficulty", 0) or 0) if method.get("difficulty") is not None else None,
        "failure_revealed": bool(event and failure_revealed(event, method_id)),
        "failure": copy.deepcopy(method.get("failure") or {}) if event and failure_revealed(event, method_id) else None,
        "failure_text": str(method.get("failure_text") or "") if event and failure_revealed(event, method_id) else "",
    }


def problem_methods_for_player(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> list[dict[str, Any]]:
    event = active_problem(event_or_id)
    if event is None or not problem_investigated(player, event):
        return []
    result = []
    for method in _raw_methods(event):
        method["availability"] = method_state(player, event, method)
        result.append(method)
    return result


def problem_knowledge_view(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> dict[str, Any] | None:
    event = active_problem(event_or_id)
    if event is None:
        return None
    problem = _problem(event)
    investigated = problem_investigated(player, event)
    runtime = ensure_threat_runtime(event)
    return {
        "id": _event_id(event),
        "name": str(event.get("name") or "Problem"),
        "description": str(problem.get("description") or event.get("description") or ""),
        "effect": str(event.get("effect_text") or ""),
        "condition": str(problem.get("condition") or "Rozwiąż problem na wskazanym heksie."),
        "investigated": investigated,
        "methods": problem_methods_for_player(player, event) if investigated else [],
        "reward_revealed": False,
        "display_number": int(runtime.get("display_number", 0) or 0) if runtime else 0,
        "markers_remaining": len(unresolved_marker_ids(event)),
        "markers_total": marker_count(event),
    }


def can_begin_problem_attempt(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> tuple[bool, str]:
    event = active_problem(event_or_id)
    if event is None:
        return False, "Ten problem nie jest już aktywny."
    if not problem_investigated(player, event):
        return False, "Najpierw zbadaj problem."
    if problem_retry_blocked(player, event):
        return False, "Ten bohater może ponowić próbę dopiero w swojej następnej turze."
    methods = problem_methods_for_player(player, event)
    if len(methods) < 2:
        return False, "Problem wymaga co najmniej dwóch sposobów rozwiązania."
    return True, ""


def _consume_named(values: list[Any], name: str, amount: int) -> int:
    target = _norm(name)
    removed = 0
    for index in range(len(values) - 1, -1, -1):
        value = values[index]
        candidate = value.get("name") or value.get("id") if isinstance(value, dict) else value
        if _norm(candidate) != target:
            continue
        values.pop(index)
        removed += 1
        if removed >= amount:
            break
    return removed


def _consume_item(player: dict[str, Any], name: str, amount: int) -> int:
    ensure_equipment_state(player)
    target = _norm(name)
    removed = 0
    inventory = player.get("inventory", [])
    for index in range(len(inventory) - 1, -1, -1):
        item = normalise_item(inventory[index])
        if _norm(item.get("name")) != target and _norm(item.get("id")) != target:
            continue
        inventory.pop(index)
        removed += 1
        if removed >= amount:
            return removed
    equipment = player.get("equipment", {})
    for slot, item in list(equipment.items()):
        if not item or removed >= amount:
            continue
        normalised = normalise_item(item)
        if _norm(normalised.get("name")) == target or _norm(normalised.get("id")) == target:
            equipment[slot] = None
            removed += 1
    return removed


def _consume_spec(player: dict[str, Any], spec: dict[str, Any]) -> int:
    kind = str(spec.get("type") or "owned").casefold()
    name = str(spec.get("name") or "")
    amount = max(1, int(spec.get("amount", 1) or 1))
    if kind in {"gold", "zloto", "złoto"}:
        player["gold"] = max(0, int(player.get("gold", 0) or 0) - amount)
        return amount
    if kind in {"material", "materialy", "materiały"}:
        materials = player.setdefault("materials", {})
        if isinstance(materials, dict):
            current = int(materials.get(name, 0) or 0)
            removed = min(current, amount)
            if current - removed:
                materials[name] = current - removed
            else:
                materials.pop(name, None)
            return removed
        return _consume_named(materials, name, amount)
    if kind in {"good", "goods", "towar", "towary"}:
        return _consume_named(player.setdefault("goods", []), name, amount)
    if kind in {"food", "jedzenie"}:
        return _consume_named(player.setdefault("food", []), name, amount)
    if kind in {"item", "przedmiot"}:
        return _consume_item(player, name, amount)
    if kind in {"helper", "pomocnik"}:
        return _consume_named(player.setdefault("helpers", []), name, amount)
    for collection in ("goods", "food", "helpers"):
        removed = _consume_named(player.setdefault(collection, []), name, amount)
        if removed:
            return removed
    return _consume_item(player, name, amount)


def _apply_reward(player: dict[str, Any], reward: dict[str, Any]) -> dict[str, Any]:
    ensure_hero_state(player)
    result: dict[str, Any] = {"gold": 0, "legend": 0, "wounds_healed": 0, "food": [], "goods": [], "materials": {}, "items": []}
    gold = max(0, int(reward.get("gold", 0) or 0))
    if gold:
        player["gold"] = int(player.get("gold", 0) or 0) + gold
        result["gold"] = gold
    legend = max(0, int(reward.get("legend", 0) or 0))
    if legend:
        player["legend"] = int(player.get("legend", 0) or 0) + legend
        result["legend"] = legend
        update_world_level()
    heal = max(0, int(reward.get("heal", 0) or 0))
    if heal:
        result["wounds_healed"] = heal_wounds(player, heal)
    food = reward.get("food", []) or []
    if isinstance(food, dict):
        for name, amount in food.items():
            values = [str(name)] * max(0, int(amount or 0))
            player.setdefault("food", []).extend(values)
            result["food"].extend(values)
    else:
        player.setdefault("food", []).extend(list(food))
        result["food"].extend(list(food))
    goods = reward.get("goods", []) or []
    if isinstance(goods, dict):
        for name, amount in goods.items():
            values = [str(name)] * max(0, int(amount or 0))
            player.setdefault("goods", []).extend(values)
            result["goods"].extend(values)
    else:
        player.setdefault("goods", []).extend(list(goods))
        result["goods"].extend(list(goods))
    for name, amount in (reward.get("materials") or {}).items():
        amount = max(0, int(amount or 0))
        if not amount:
            continue
        materials = player.setdefault("materials", {})
        if isinstance(materials, dict):
            materials[name] = int(materials.get(name, 0) or 0) + amount
        else:
            materials.extend([name] * amount)
        result["materials"][name] = amount
    raw_items = list(reward.get("items", []) or [])
    if reward.get("item"):
        raw_items.append(reward["item"])
    for raw_item in raw_items:
        item = normalise_item(raw_item)
        added, _message = add_item(player, item, enforce_capacity=True)
        result["items"].append({"item": item, "in_backpack": added})
    return result


def _apply_failure(player: dict[str, Any], consequence: dict[str, Any], event_id: str) -> dict[str, Any]:
    ensure_hero_state(player)
    result = {"wounds": 0, "gold_lost": 0, "legend_lost": 0, "actions_lost": 0, "materials_lost": {}, "goods_lost": [], "difficulty_penalty": 0}
    wounds = max(0, int(consequence.get("wounds", 0) or 0))
    if wounds:
        applied, _defeated = apply_wounds(player, wounds)
        result["wounds"] = applied
    gold = max(0, int(consequence.get("gold", 0) or 0))
    if gold:
        current = max(0, int(player.get("gold", 0) or 0))
        result["gold_lost"] = min(current, gold)
        player["gold"] = current - result["gold_lost"]
    legend = max(0, int(consequence.get("legend", 0) or 0))
    if legend:
        current = max(0, int(player.get("legend", 0) or 0))
        result["legend_lost"] = min(current, legend)
        player["legend"] = current - result["legend_lost"]
    actions = max(0, int(consequence.get("actions", 0) or 0))
    token = player.get("_token_ref")
    if actions and token is not None:
        before = int(getattr(token, "actions", 0) or 0)
        token.actions = max(0, before - actions)
        result["actions_lost"] = before - token.actions
    for name, amount in (consequence.get("materials") or {}).items():
        removed = _consume_spec(player, {"type": "material", "name": str(name), "amount": int(amount or 0)})
        if removed:
            result["materials_lost"][str(name)] = removed
    for name, amount in (consequence.get("goods") or {}).items():
        removed = _consume_spec(player, {"type": "good", "name": str(name), "amount": int(amount or 0)})
        result["goods_lost"].extend([str(name)] * removed)
    penalty = max(0, int(consequence.get("difficulty_penalty", 0) or 0))
    if penalty:
        penalties = player.setdefault("threat_difficulty_penalties", {})
        penalties[event_id] = int(penalties.get(event_id, 0) or 0) + penalty
        result["difficulty_penalty"] = penalty
    return result


def reward_text(result: dict[str, Any]) -> str:
    parts = []
    if result.get("gold"):
        parts.append(f"{result['gold']} Złota")
    if result.get("legend"):
        parts.append(f"{result['legend']} Punktów Legendy")
    if result.get("wounds_healed"):
        parts.append(f"uleczono {result['wounds_healed']} Ran")
    if result.get("food"):
        parts.append(f"jedzenie: {', '.join(map(str, result['food']))}")
    if result.get("goods"):
        parts.append(f"Towary: {', '.join(map(str, result['goods']))}")
    parts.extend(f"{amount}× {name}" for name, amount in result.get("materials", {}).items())
    for entry in result.get("items", []):
        parts.append(str(entry["item"].get("name", "Przedmiot")))
    return ", ".join(parts) if parts else "brak dodatkowej nagrody"


def failure_text(result: dict[str, Any]) -> str:
    parts = []
    if result.get("wounds"):
        parts.append(f"+{result['wounds']} Ran")
    if result.get("gold_lost"):
        parts.append(f"-{result['gold_lost']} Złota")
    if result.get("legend_lost"):
        parts.append(f"-{result['legend_lost']} Punktów Legendy")
    if result.get("actions_lost"):
        parts.append(f"-{result['actions_lost']} Akcji")
    parts.extend(f"-{amount}× {name}" for name, amount in result.get("materials_lost", {}).items())
    if result.get("goods_lost"):
        parts.append(f"utracono Towary: {', '.join(map(str, result['goods_lost']))}")
    if result.get("difficulty_penalty"):
        parts.append(f"+{result['difficulty_penalty']} do trudności kolejnej próby")
    return ", ".join(parts) if parts else "brak dodatkowej kary"


@dataclass
class ProblemAttemptSession:
    player: dict[str, Any]
    event: dict[str, Any]
    marker_id: str
    methods: list[dict[str, Any]]
    resolved: bool = False
    success: bool | None = None
    selected_method: int | None = None
    roll: int | None = None
    total: int | None = None
    difficulty: int | None = None
    result_text: str = ""
    reward_result: dict[str, Any] = field(default_factory=dict)
    failure_result: dict[str, Any] = field(default_factory=dict)
    combat_pending: bool = False

    @property
    def event_id(self) -> str:
        return _event_id(self.event)

    @property
    def marker_ref(self) -> str:
        return make_marker_ref(self.event_id, self.marker_id)

    @property
    def problem(self) -> dict[str, Any]:
        return _problem(self.event)


def begin_problem_attempt(player: dict[str, Any], event_or_ref: dict[str, Any] | str, marker_id: str | int | None = None) -> tuple[ProblemAttemptSession | None, str]:
    event = active_problem(event_or_ref)
    if event is None:
        return None, "Ten problem nie jest już aktywny."
    event_id, parsed_marker = parse_marker_ref(event_or_ref, marker_id)
    if marker_is_resolved(event_id, parsed_marker):
        return None, "Ten punkt Zagrożenia został już rozwiązany."
    allowed, message = can_begin_problem_attempt(player, event)
    if not allowed:
        return None, message
    return ProblemAttemptSession(player=player, event=event, marker_id=parsed_marker, methods=problem_methods_for_player(player, event)), "Wybierz sposób rozwiązania. Podgląd metod jest darmowy; 1 Akcja zostanie pobrana po wybraniu metody."


def _method_difficulty(session: ProblemAttemptSession, method: dict[str, Any]) -> int:
    base = max(0, int(method.get("difficulty", 0) or 0))
    penalty = int((session.player.get("threat_difficulty_penalties", {}) or {}).get(session.event_id, 0) or 0)
    return base + penalty


def _mark_retry_block(player: dict[str, Any], event_id: str) -> None:
    values = _retry_blocks(player)
    values.add(event_id)
    _save_retry_blocks(player, values)


def _grant_completion_rewards(session: ProblemAttemptSession, method: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    runtime = ensure_threat_runtime(session.event)
    problem = session.problem
    reward = copy.deepcopy(problem.get("reward") or {})
    mode = str(problem.get("reward_mode") or ("contributors" if marker_count(session.event) > 1 else "resolver"))
    keys = list(runtime.get("contributors", set())) if runtime else []
    if mode != "contributors":
        keys = [_player_key(session.player)]
    if not keys:
        keys = [_player_key(session.player)]
    reward_rows = []
    for key in keys:
        target = _find_player(key)
        if target is None and key == _player_key(session.player):
            target = session.player
        if target is None:
            continue
        result = _apply_reward(target, reward)
        reward_rows.append({"player": target.get("name", "Bohater"), "player_key": key, "reward": result})
    text = "; ".join(f"{row['player']}: {reward_text(row['reward'])}" for row in reward_rows)
    return reward_rows, text or "brak dodatkowej nagrody"


def _complete_marker_success(session: ProblemAttemptSession, method: dict[str, Any], flavour: str = "") -> tuple[bool, str]:
    runtime = ensure_threat_runtime(session.event)
    if runtime is None:
        return False, "Ten problem nie jest już aktywny."
    state = runtime["markers"].setdefault(session.marker_id, {"resolved": False, "tile_id": None})
    state["resolved"] = True
    state["resolved_by"] = str(session.player.get("name") or "Bohater")
    state["method_id"] = str(method.get("id") or method.get("label") or "")
    runtime.setdefault("contributors", set()).add(_player_key(session.player))
    remaining = unresolved_marker_ids(session.event)
    session.success = True
    session.resolved = True
    session.selected_method = session.methods.index(method) if method in session.methods else session.selected_method

    if remaining:
        session.result_text = flavour or "Ten punkt Zagrożenia został rozwiązany. Pozostałe znaczniki nadal są aktywne."
        return True, session.result_text

    reward_rows, reward_summary = _grant_completion_rewards(session, method)
    method_label = str(method.get("label") or method.get("id") or "metodą bohatera")
    resolution = {
        "hero": str(session.player.get("name") or "Bohater"),
        "method": method_label,
        "method_id": str(method.get("id") or ""),
        "reward": reward_rows,
        "contributors": sorted(runtime.get("contributors", set())),
        "display_number": int(runtime.get("display_number", 0) or 0),
    }
    resolved = resolve_problem_event(session.event_id, str(session.player.get("name") or "Bohater"), resolution=resolution)
    penalties = session.player.setdefault("threat_difficulty_penalties", {})
    penalties.pop(session.event_id, None)
    base_text = flavour or str(method.get("success_text") or session.problem.get("success_text") or "Zagrożenie zostało rozwiązane.")
    session.result_text = f"{base_text} Nagroda: {reward_summary}."
    session.reward_result = {"recipients": reward_rows}
    runtime["last_resolution"] = copy.deepcopy(resolution)
    try:
        from rg_engine.world_chronicle import add_threat_resolution
        add_threat_resolution(resolved or session.event, resolution)
    except ImportError:
        pass
    _THREAT_RUNTIME.pop(session.event_id, None)
    for player in registered_players():
        clear_problem_knowledge(player, session.event_id)
    return True, session.result_text


def _resolve_failure(session: ProblemAttemptSession, method: dict[str, Any], flavour: str = "") -> tuple[bool, str]:
    method_id = str(method.get("id") or method.get("label") or "method")
    _reveal_failure(session.event, method_id)
    consequence = copy.deepcopy(method.get("failure") or {})
    session.failure_result = _apply_failure(session.player, consequence, session.event_id)
    _mark_retry_block(session.player, session.event_id)
    session.success = False
    session.resolved = True
    base = flavour or str(method.get("failure_text") or session.problem.get("failure_text") or "Próba kończy się niepowodzeniem.")
    session.result_text = f"{base} Konsekwencja: {failure_text(session.failure_result)}."
    return False, session.result_text


def _pay_selected_method(session: ProblemAttemptSession, method: dict[str, Any]) -> tuple[bool, str]:
    state = method_state(session.player, session.event, method)
    if not state["available"]:
        return False, "Nie możesz użyć tej metody: " + "; ".join(state["missing"])
    for spec in method_costs(method):
        _consume_spec(session.player, spec)
    token = session.player.get("_token_ref")
    token.actions = max(0, int(token.actions) - PROBLEM_ACTION_COST)
    return True, ""


def set_problem_combat_launcher(launcher: Callable[[ProblemAttemptSession, int, dict[str, Any]], tuple[bool, str]] | None) -> None:
    global _COMBAT_LAUNCHER
    _COMBAT_LAUNCHER = launcher


def resolve_problem_method(session: ProblemAttemptSession, method_index: int, rng=None) -> tuple[bool, str]:
    if session.resolved or session.combat_pending:
        return bool(session.success), session.result_text or "Ta próba jest już rozpatrywana."
    if method_index < 0 or method_index >= len(session.methods):
        return False, "Nieprawidłowy sposób rozwiązania problemu."
    if active_problem(session.event_id) is None or marker_is_resolved(session.event_id, session.marker_id):
        return False, "Ten punkt Zagrożenia nie jest już aktywny."

    method = session.methods[method_index]
    state = method_state(session.player, session.event, method)
    mode = state["mode"]
    if not state["available"]:
        return False, "Nie możesz użyć tej metody: " + "; ".join(state["missing"])

    if mode == "combat":
        if _COMBAT_LAUNCHER is None:
            return False, "Brak podłączonego ekranu walki dla tej metody."
        started, message = _COMBAT_LAUNCHER(session, method_index, method)
        if not started:
            return False, message
        paid, payment_message = _pay_selected_method(session, method)
        if not paid:
            return False, payment_message
        session.selected_method = method_index
        session.combat_pending = True
        session.result_text = message
        return False, message

    paid, payment_message = _pay_selected_method(session, method)
    if not paid:
        return False, payment_message
    session.selected_method = method_index

    if mode == "automatic":
        session.roll = None
        session.total = None
        session.difficulty = None
        return _complete_marker_success(session, method, str(method.get("success_text") or "Warunki zostały spełnione. Zagrożenie ustępuje."))

    rng = rng or random
    stat = str(method.get("stat") or "")
    difficulty = _method_difficulty(session, method)
    roll = int(rng.randint(1, 20))
    stat_value = int((session.player.get("stats") or {}).get(stat, 0) or 0)
    helper = helper_bonus(session.player, stat)
    equipment = equipment_stat_bonus(session.player, stat)
    total = roll + stat_value + helper + equipment
    success = roll == 20 or total >= difficulty
    session.roll = roll
    session.total = total
    session.difficulty = difficulty
    if success:
        return _complete_marker_success(session, method, str(method.get("success_text") or "Próba kończy się sukcesem."))
    return _resolve_failure(session, method)


def finish_problem_combat(session: ProblemAttemptSession, victory: bool, message: str = "") -> tuple[bool, str]:
    if not session.combat_pending:
        return False, "Ta sesja nie oczekuje na wynik walki."
    session.combat_pending = False
    index = int(session.selected_method or 0)
    if index < 0 or index >= len(session.methods):
        return False, "Nie znaleziono metody walki."
    method = session.methods[index]
    if victory:
        return _complete_marker_success(session, method, message or str(method.get("success_text") or "Przeciwnik został pokonany."))
    return _resolve_failure(session, method, message or str(method.get("failure_text") or "Bohater przegrywa walkę."))


def _effect_scope_matches(effect: dict[str, Any], runtime: dict[str, Any], tile_id: int | None) -> bool:
    scope = str(effect.get("scope") or "global").casefold()
    if scope in {"global", "world"}:
        return True
    if scope in {"marker", "marker_tile", "marker_tiles", "local"}:
        if tile_id is None:
            return False
        return any(
            not state.get("resolved") and state.get("tile_id") is not None and int(state.get("tile_id")) == int(tile_id)
            for state in runtime.get("markers", {}).values()
        )
    explicit_tile = effect.get("tile_id")
    return tile_id is not None and explicit_tile is not None and int(explicit_tile) == int(tile_id)


def active_threat_effects(effect_type: str | None = None, tile_id: int | None = None) -> list[dict[str, Any]]:
    result = []
    for event in active_world_events(DURATION_UNTIL_RESOLVED):
        runtime = ensure_threat_runtime(event)
        if runtime is None:
            continue
        for effect in _problem(event).get("effects", []) or []:
            if not isinstance(effect, dict):
                continue
            if effect_type is not None and str(effect.get("type") or "") != str(effect_type):
                continue
            if not _effect_scope_matches(effect, runtime, tile_id):
                continue
            row = copy.deepcopy(effect)
            row["event_id"] = _event_id(event)
            row["event_name"] = str(event.get("name") or "Zagrożenie")
            result.append(row)
    return result


def is_tile_entry_blocked(tile_id: int) -> tuple[bool, str]:
    effects = active_threat_effects("block_entry", tile_id=tile_id)
    if not effects:
        return False, ""
    names = ", ".join(dict.fromkeys(str(effect.get("event_name")) for effect in effects))
    return True, f"Wejście zablokowane przez Zagrożenie: {names}."


def is_interaction_blocked(interaction: str, tile_id: int | None = None) -> tuple[bool, str]:
    target = str(interaction or "")
    matches = []
    for effect in active_threat_effects("block_interaction", tile_id=tile_id):
        value = str(effect.get("interaction") or effect.get("key") or "")
        if value in {"*", target}:
            matches.append(effect)
    if not matches:
        return False, ""
    names = ", ".join(dict.fromkeys(str(effect.get("event_name")) for effect in matches))
    return True, f"Interakcja „{target}” jest zablokowana przez: {names}."


def threat_modifier(name: str, tile_id: int | None = None) -> int:
    total = 0
    for effect in active_threat_effects("modifier", tile_id=tile_id):
        if str(effect.get("name") or effect.get("key") or "") == str(name):
            total += int(effect.get("amount", 0) or 0)
    return total
