from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Any

from rg_engine.heroes import ensure_hero_state, helper_bonus
from rg_engine.items import add_item, equipment_stat_bonus, normalise_item
from rg_engine.world import update_world_level
from rg_engine.world_events import DURATION_UNTIL_RESOLVED, active_world_events, resolve_problem_event

PROBLEM_ACTION_COST = 1


def _event_id(event: dict[str, Any]) -> str:
    return str(event.get("id") or "")


def _problem(event: dict[str, Any]) -> dict[str, Any]:
    problem = event.get("problem") or {}
    return problem if isinstance(problem, dict) else {}


def _active_problem(event_id: str) -> dict[str, Any] | None:
    for event in active_world_events(DURATION_UNTIL_RESOLVED):
        if _event_id(event) == str(event_id):
            return event
    return None


def _retry_blocks(player: dict[str, Any]) -> set[str]:
    raw = player.setdefault("_problem_retry_blocks", set())
    if isinstance(raw, set):
        return raw
    normalised = set(str(value) for value in (raw or []))
    player["_problem_retry_blocks"] = normalised
    return normalised


def clear_problem_retry_blocks(player: dict[str, Any]) -> None:
    """Wywoływane na początku nowej tury danego bohatera."""
    player["_problem_retry_blocks"] = set()


def problem_retry_blocked(player: dict[str, Any], event_id: str) -> bool:
    return str(event_id) in _retry_blocks(player)


def available_problem_methods(event: dict[str, Any]) -> list[dict[str, Any]]:
    methods = _problem(event).get("methods") or []
    return [copy.deepcopy(method) for method in methods if isinstance(method, dict)]


def can_begin_problem_attempt(player: dict[str, Any], event: dict[str, Any]) -> tuple[bool, str]:
    event_id = _event_id(event)
    if not event_id or _active_problem(event_id) is None:
        return False, "Ten problem nie jest już aktywny."
    if problem_retry_blocked(player, event_id):
        return False, "Ten bohater może ponowić próbę dopiero w swojej następnej turze."

    token = player.get("_token_ref")
    if token is None or int(getattr(token, "actions", 0) or 0) < PROBLEM_ACTION_COST:
        return False, "Potrzebujesz 1 akcji, aby podjąć próbę."

    methods = available_problem_methods(event)
    if len(methods) < 2:
        return False, "Problem wymaga co najmniej dwóch sposobów rozwiązania."
    return True, ""


def _material_count(player: dict[str, Any], name: str) -> int:
    materials = player.get("materials", {})
    if isinstance(materials, dict):
        return int(materials.get(name, 0) or 0)
    if isinstance(materials, list):
        return sum(1 for item in materials if str(item) == str(name))
    return 0


def _remove_material(player: dict[str, Any], name: str, amount: int) -> int:
    amount = max(0, int(amount or 0))
    materials = player.get("materials", {})
    if isinstance(materials, dict):
        available = int(materials.get(name, 0) or 0)
        removed = min(available, amount)
        remaining = available - removed
        if remaining:
            materials[name] = remaining
        elif name in materials:
            del materials[name]
        return removed
    if isinstance(materials, list):
        removed = 0
        for index in range(len(materials) - 1, -1, -1):
            if removed >= amount:
                break
            if str(materials[index]) == str(name):
                materials.pop(index)
                removed += 1
        return removed
    return 0


def _apply_reward(player: dict[str, Any], reward: dict[str, Any]) -> dict[str, Any]:
    ensure_hero_state(player)
    result: dict[str, Any] = {
        "gold": 0,
        "legend": 0,
        "wounds_healed": 0,
        "food": [],
        "goods": [],
        "materials": {},
        "items": [],
    }

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
        before = max(0, int(player.get("wounds", 0) or 0))
        player["wounds"] = max(0, before - heal)
        result["wounds_healed"] = before - player["wounds"]

    food = reward.get("food", []) or []
    if isinstance(food, dict):
        for name, amount in food.items():
            values = [str(name)] * max(0, int(amount or 0))
            player.setdefault("food", []).extend(values)
            result["food"].extend(values)
    else:
        for name in food:
            player.setdefault("food", []).append(name)
            result["food"].append(name)

    goods = reward.get("goods", []) or []
    if isinstance(goods, dict):
        for name, amount in goods.items():
            values = [str(name)] * max(0, int(amount or 0))
            player.setdefault("goods", []).extend(values)
            result["goods"].extend(values)
    else:
        for name in goods:
            player.setdefault("goods", []).append(name)
            result["goods"].append(name)

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
        added_to_backpack, _ = add_item(player, item, enforce_capacity=True)
        result["items"].append({"item": item, "in_backpack": added_to_backpack})

    return result


def _apply_failure(player: dict[str, Any], consequence: dict[str, Any], event_id: str) -> dict[str, Any]:
    ensure_hero_state(player)
    result: dict[str, Any] = {
        "wounds": 0,
        "gold_lost": 0,
        "legend_lost": 0,
        "materials_lost": {},
        "goods_lost": [],
        "difficulty_penalty": 0,
    }

    wounds = max(0, int(consequence.get("wounds", 0) or 0))
    if wounds:
        player["wounds"] = int(player.get("wounds", 0) or 0) + wounds
        result["wounds"] = wounds

    gold = max(0, int(consequence.get("gold", 0) or 0))
    if gold:
        current = max(0, int(player.get("gold", 0) or 0))
        lost = min(current, gold)
        player["gold"] = current - lost
        result["gold_lost"] = lost

    legend = max(0, int(consequence.get("legend", 0) or 0))
    if legend:
        current = max(0, int(player.get("legend", 0) or 0))
        lost = min(current, legend)
        player["legend"] = current - lost
        result["legend_lost"] = lost

    for name, amount in (consequence.get("materials") or {}).items():
        removed = _remove_material(player, str(name), int(amount or 0))
        if removed:
            result["materials_lost"][str(name)] = removed

    for name, amount in (consequence.get("goods") or {}).items():
        remaining = max(0, int(amount or 0))
        goods = player.setdefault("goods", [])
        removed = 0
        for index in range(len(goods) - 1, -1, -1):
            if remaining <= 0:
                break
            if str(goods[index]) == str(name):
                goods.pop(index)
                remaining -= 1
                removed += 1
        result["goods_lost"].extend([str(name)] * removed)

    penalty = max(0, int(consequence.get("difficulty_penalty", 0) or 0))
    if penalty:
        penalties = player.setdefault("_problem_difficulty_penalties", {})
        penalties[event_id] = int(penalties.get(event_id, 0) or 0) + penalty
        result["difficulty_penalty"] = penalty

    return result


def _reward_text(result: dict[str, Any]) -> str:
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
    if result.get("materials"):
        parts.extend(f"{amount}x {name}" for name, amount in result["materials"].items())
    for entry in result.get("items", []):
        parts.append(str(entry["item"].get("name", "Przedmiot")))
    return ", ".join(parts) if parts else "brak dodatkowej nagrody"


def _failure_text(result: dict[str, Any]) -> str:
    parts = []
    if result.get("wounds"):
        parts.append(f"+{result['wounds']} Ran")
    if result.get("gold_lost"):
        parts.append(f"-{result['gold_lost']} Złota")
    if result.get("legend_lost"):
        parts.append(f"-{result['legend_lost']} Punktów Legendy")
    parts.extend(f"-{amount}x {name}" for name, amount in result.get("materials_lost", {}).items())
    if result.get("goods_lost"):
        parts.append(f"utracono Towary: {', '.join(map(str, result['goods_lost']))}")
    if result.get("difficulty_penalty"):
        parts.append(f"+{result['difficulty_penalty']} do trudności kolejnej próby")
    return ", ".join(parts) if parts else "brak dodatkowej kary"


@dataclass
class ProblemAttemptSession:
    player: dict[str, Any]
    event: dict[str, Any]
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

    @property
    def event_id(self) -> str:
        return _event_id(self.event)

    @property
    def problem(self) -> dict[str, Any]:
        return _problem(self.event)


def begin_problem_attempt(player: dict[str, Any], event: dict[str, Any]) -> tuple[ProblemAttemptSession | None, str]:
    current = _active_problem(_event_id(event))
    if current is None:
        return None, "Ten problem nie jest już aktywny."
    allowed, message = can_begin_problem_attempt(player, current)
    if not allowed:
        return None, message

    token = player.get("_token_ref")
    token.actions = max(0, int(token.actions) - PROBLEM_ACTION_COST)
    session = ProblemAttemptSession(player=player, event=current, methods=available_problem_methods(current))
    return session, "Wybierz sposób rozwiązania problemu. Akcja została zużyta."


def resolve_problem_method(session: ProblemAttemptSession, method_index: int, rng=None) -> tuple[bool, str]:
    if session.resolved:
        return bool(session.success), session.result_text
    if method_index < 0 or method_index >= len(session.methods):
        return False, "Nieprawidłowy sposób rozwiązania problemu."

    rng = rng or random
    method = session.methods[method_index]
    stat = str(method.get("stat") or "")
    base_difficulty = max(0, int(method.get("difficulty", 0) or 0))
    penalty = int((session.player.get("_problem_difficulty_penalties", {}) or {}).get(session.event_id, 0) or 0)
    difficulty = base_difficulty + penalty
    roll = int(rng.randint(1, 20))
    stat_value = int((session.player.get("stats") or {}).get(stat, 0) or 0)
    helper = helper_bonus(session.player, stat)
    equipment = equipment_stat_bonus(session.player, stat)
    total = roll + stat_value + helper + equipment
    success = roll == 20 or total >= difficulty

    session.selected_method = method_index
    session.roll = roll
    session.total = total
    session.difficulty = difficulty
    session.success = success
    session.resolved = True

    if success:
        reward = copy.deepcopy(session.problem.get("reward") or {})
        session.reward_result = _apply_reward(session.player, reward)
        resolved = resolve_problem_event(session.event_id, session.player.get("name", "Bohatera"))
        penalties = session.player.setdefault("_problem_difficulty_penalties", {})
        penalties.pop(session.event_id, None)
        flavour = str(method.get("success_text") or session.problem.get("success_text") or "Problem został rozwiązany.")
        session.result_text = f"{flavour} Nagroda: {_reward_text(session.reward_result)}."
        if resolved is None:
            session.result_text = f"{session.result_text} Problem został już wcześniej zakończony."
        return True, session.result_text

    consequence = copy.deepcopy(method.get("failure") or {})
    session.failure_result = _apply_failure(session.player, consequence, session.event_id)
    _retry_blocks(session.player).add(session.event_id)
    flavour = str(method.get("failure_text") or session.problem.get("failure_text") or "Próba kończy się niepowodzeniem.")
    session.result_text = f"{flavour} Konsekwencja: {_failure_text(session.failure_result)}."
    return False, session.result_text
