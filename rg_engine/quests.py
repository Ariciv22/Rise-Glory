from __future__ import annotations

import copy
import random
import unicodedata
from typing import Any

from rg_engine.heroes import ensure_hero_state, helper_bonus
from rg_engine.items import add_item, equipment_stat_bonus, normalise_item
from rg_engine.models import QuestDefinition, QuestExpansionDefinition

QUEST_LIMIT = 3
QUEST_FAILURE_LIMIT = 5
QUEST_DECK = "Questy"
PREPARE_ACTION_COST = 1
PREPARE_BONUS = 2

_QUESTS: dict[str, dict[str, Any]] = {}
_QUEST_EXPANSIONS: dict[str, dict[str, Any]] = {}
_QUEST_NUMBERS: dict[int, str] = {}


def _normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    return "".join(character for character in ascii_text if character.isalnum())


def _copy(value):
    return copy.deepcopy(value)


def register_quest(definition: QuestDefinition | dict[str, Any]) -> dict[str, Any]:
    quest = definition.to_dict() if isinstance(definition, QuestDefinition) else _copy(definition)
    quest_id = str(quest.get("id") or quest.get("quest_id") or "")
    if not quest_id:
        raise ValueError("Definicja Questa wymaga pola id.")

    quest["id"] = quest_id
    quest.pop("quest_id", None)
    quest["deck"] = QUEST_DECK
    quest.setdefault("world_level", int(quest.get("world_level_min", 1) or 1))
    quest.setdefault("world_level_min", int(quest.get("world_level", 1) or 1))
    quest.setdefault("length", "Krótki")
    quest.setdefault("reward_hint", "")
    quest.setdefault("time_limit", {})
    quest.setdefault("markers", [])
    quest.setdefault("flags_on_complete", {})
    quest.setdefault("reward", {})
    quest.setdefault("board_text", quest.get("description", ""))
    quest.setdefault("unique", False)
    quest.setdefault("shared", False)
    quest.setdefault("sellable", True)
    quest.setdefault("tradeable", True)
    quest.setdefault("abandonable", True)

    number = int(quest.get("quest_number", 0) or 0)
    if number > 0:
        owner = _QUEST_NUMBERS.get(number)
        if owner and owner != quest_id:
            raise ValueError(f"Numer Questa {number} jest już przypisany do {owner}.")
        _QUEST_NUMBERS[number] = quest_id
    quest["quest_number"] = number

    stages = sorted(list(quest.get("stages", [])), key=lambda stage: int(stage.get("number", 0)))
    if not stages:
        raise ValueError(f"Quest {quest_id} nie posiada etapów.")
    for expected, stage in enumerate(stages, start=1):
        stage.setdefault("number", expected)
        stage.setdefault("title", f"Etap {expected}")
        stage.setdefault("text", "")
        stage.setdefault("options", [])
        stage.setdefault("required_location", quest.get("required_location"))
        stage.setdefault("required_hex", None)
        stage.setdefault("image", quest.get("image", ""))
        stage.setdefault("point_of_no_return", False)
        for option_index, option in enumerate(stage["options"]):
            option.setdefault("option_id", f"{quest_id}_{expected}_{option_index}")
            option.setdefault("label", f"Opcja {option_index + 1}")
            option.setdefault("type", "test")
            option.setdefault("action_cost", 1)
            option.setdefault("materials", {})
            option.setdefault("gold_cost", 0)
            option.setdefault("requires", {})
            option.setdefault("consumes", {})
            option.setdefault("visible_if", {})
            option.setdefault("disabled_if", {})
            option.setdefault("disabled_reason", "")
            option.setdefault("success_effects", [])
            option.setdefault("failure_effects", [])
            option.setdefault("on_success", "next")
            option.setdefault("on_failure", "retry")
            option.setdefault("combat_defeat", "quest_failure")
            option.setdefault("combat_victory", "success")
    quest["stages"] = stages
    _QUESTS[quest_id] = quest
    return _copy(quest)


def register_quest_expansion(definition: QuestExpansionDefinition | dict[str, Any]) -> dict[str, Any]:
    expansion = definition.to_dict() if isinstance(definition, QuestExpansionDefinition) else _copy(definition)
    expansion_id = str(expansion.get("expansion_id") or expansion.get("id") or "")
    quest_id = str(expansion.get("quest_id") or "")
    if not expansion_id or not quest_id:
        raise ValueError("Rozwinięcie wymaga expansion_id i quest_id.")
    expansion["expansion_id"] = expansion_id
    expansion["quest_id"] = quest_id
    _QUEST_EXPANSIONS[expansion_id] = expansion
    return _copy(expansion)


def quest_definition(quest_id: str) -> dict[str, Any] | None:
    definition = _QUESTS.get(str(quest_id))
    return _copy(definition) if definition else None


def quest_expansion(expansion_id: str) -> dict[str, Any] | None:
    expansion = _QUEST_EXPANSIONS.get(str(expansion_id))
    return _copy(expansion) if expansion else None


def is_registered_quest(quest_or_id: Any) -> bool:
    quest_id = quest_or_id.get("id") if isinstance(quest_or_id, dict) else quest_or_id
    return str(quest_id) in _QUESTS


def quest_ids_for_world_level(world_level: int) -> list[str]:
    level = int(world_level or 1)
    return [
        quest_id
        for quest_id, definition in _QUESTS.items()
        if int(definition.get("world_level", definition.get("world_level_min", 1)) or 1) == level
    ]


def draw_quest_id(world_level: int, unavailable_ids=(), rng=None) -> str | None:
    rng = rng or random
    blocked = {str(value) for value in unavailable_ids or ()}
    candidates = [quest_id for quest_id in quest_ids_for_world_level(world_level) if quest_id not in blocked]
    return str(rng.choice(candidates)) if candidates else None


def create_offer(quest_id: str) -> dict[str, Any]:
    definition = quest_definition(quest_id)
    if not definition:
        raise KeyError(f"Nieznany Quest: {quest_id}")
    return {
        "id": definition["id"],
        "quest_number": int(definition.get("quest_number", 0) or 0),
        "name": definition["name"],
        "deck": QUEST_DECK,
        "description": definition.get("board_text") or definition.get("description", ""),
        "objective": definition.get("objective", ""),
        "required_location": definition.get("required_location"),
        "world_level": int(definition.get("world_level", 1) or 1),
        "world_level_min": int(definition.get("world_level", 1) or 1),
        "length": definition.get("length", "Krótki"),
        "reward_hint": definition.get("reward_hint", ""),
        "time_limit": _copy(definition.get("time_limit") or {}),
        "status": "offer",
        "unique": bool(definition.get("unique", False)),
    }


def activate_quest(quest_or_id: dict[str, Any] | str) -> dict[str, Any]:
    quest_id = quest_or_id.get("id") if isinstance(quest_or_id, dict) else quest_or_id
    definition = quest_definition(str(quest_id))
    if not definition:
        raise KeyError(f"Nieznany Quest: {quest_id}")
    first_stage = definition["stages"][0]
    time_limit = _copy(definition.get("time_limit") or {})
    return {
        "id": definition["id"],
        "quest_number": int(definition.get("quest_number", 0) or 0),
        "name": definition["name"],
        "deck": QUEST_DECK,
        "description": definition.get("description", ""),
        "objective": definition.get("objective", ""),
        "required_location": definition.get("required_location"),
        "world_level": int(definition.get("world_level", 1) or 1),
        "world_level_min": int(definition.get("world_level", 1) or 1),
        "length": definition.get("length", "Krótki"),
        "reward_hint": definition.get("reward_hint", ""),
        "status": "active",
        "started": False,
        "stage_number": int(first_stage.get("number", 1)),
        "stage": f"1/{len(definition['stages'])}",
        "failures": 0,
        "difficulty_modifier": 0,
        "prepared": False,
        "preparation_used": False,
        "point_of_no_return": False,
        "last_result": f"Quest pobrany. Udaj się do lokacji: {definition.get('required_location', '-')}",
        "pending_combat": None,
        "history": [],
        "story_flags": {},
        "quest_items": [],
        "disabled_options": {},
        "discovered_expansions": [],
        "current_paragraph": None,
        "ending_id": None,
        "markers": [],
        "time_limit": time_limit,
        "time_remaining": int(time_limit.get("amount", 0) or 0) if time_limit else None,
    }


def find_player_quest(player: dict[str, Any], quest_id: str, include_history: bool = True) -> dict[str, Any] | None:
    for quest in player.get("active_quests", []) or []:
        if isinstance(quest, dict) and quest.get("id") == quest_id:
            return quest
    if include_history:
        for key in ("completed_quests", "failed_quests", "abandoned_quests"):
            for quest in player.get(key, []) or []:
                if isinstance(quest, dict) and quest.get("id") == quest_id:
                    return quest
    return None


def can_accept_quest(player: dict[str, Any]) -> tuple[bool, str]:
    if len(player.get("active_quests", []) or []) >= QUEST_LIMIT:
        return False, f"Masz już maksymalnie {QUEST_LIMIT} Questy."
    return True, ""


def can_trade_quest(quest: dict[str, Any]) -> tuple[bool, str]:
    definition = quest_definition(str(quest.get("id")))
    if definition and not definition.get("tradeable", True):
        return False, "Tego Questa nie można handlować."
    if bool(quest.get("started", False)):
        return False, "Rozpoczętego Questa nie można handlować."
    return True, ""


def return_unstarted_quest(player: dict[str, Any], quest: dict[str, Any]) -> tuple[bool, str]:
    if bool(quest.get("started", False)):
        return False, "Rozpoczęty Quest nie może wrócić do talii."
    _remove_active_quest(player, quest)
    quest["status"] = "returned_to_deck"
    clear_quest_markers(quest)
    return True, f"Quest {quest.get('name', 'Quest')} wraca do Talii Questów i może zostać potasowany."


def _stage_index(definition: dict[str, Any], stage_number: int) -> int:
    for index, stage in enumerate(definition.get("stages", [])):
        if int(stage.get("number", 0)) == int(stage_number):
            return index
    return -1


def current_stage(quest: dict[str, Any]) -> dict[str, Any] | None:
    definition = quest_definition(str(quest.get("id")))
    if not definition:
        return None
    index = _stage_index(definition, int(quest.get("stage_number", 1) or 1))
    return _copy(definition["stages"][index]) if index >= 0 else None


def quest_tabs_for_location(player: dict[str, Any], location_name: str) -> list[dict[str, Any]]:
    tabs = []
    for quest in player.get("active_quests", []) or []:
        if not is_registered_quest(quest):
            continue
        definition = quest_definition(quest["id"])
        stage = current_stage(quest)
        required = (stage or {}).get("required_location") or definition.get("required_location")
        if not required or _normalize(required) == _normalize(location_name):
            tabs.append(quest)
    return tabs


def _token(player: dict[str, Any]):
    return player.get("_token_ref")


def _current_location_name(player: dict[str, Any]) -> str | None:
    token = _token(player)
    tile = getattr(token, "tile", None)
    location = getattr(tile, "location", None)
    return location.get("name") if isinstance(location, dict) else None


def _material_count(player: dict[str, Any], requested_name: str) -> int:
    target = _normalize(requested_name)
    accepted = {target}
    if target in {"skora", "skory"}:
        accepted.update({"skora", "skory"})
    materials = player.get("materials", {})
    if isinstance(materials, dict):
        return sum(int(amount or 0) for name, amount in materials.items() if _normalize(name) in accepted)
    if isinstance(materials, (list, tuple)):
        return sum(1 for item in materials if _normalize(item) in accepted)
    return 0


def _consume_material(player: dict[str, Any], requested_name: str, amount: int) -> bool:
    if _material_count(player, requested_name) < amount:
        return False
    accepted = {_normalize(requested_name)}
    if "skora" in accepted or "skory" in accepted:
        accepted.update({"skora", "skory"})
    materials = player.get("materials", {})
    if isinstance(materials, dict):
        remaining = amount
        for name in list(materials):
            if _normalize(name) not in accepted:
                continue
            take = min(remaining, int(materials[name] or 0))
            materials[name] -= take
            remaining -= take
            if materials[name] <= 0:
                del materials[name]
            if remaining <= 0:
                break
        return remaining <= 0
    if isinstance(materials, list):
        remaining = amount
        for index in range(len(materials) - 1, -1, -1):
            if _normalize(materials[index]) in accepted:
                materials.pop(index)
                remaining -= 1
                if remaining <= 0:
                    break
        return remaining <= 0
    return False


def _named_item_exists(player: dict[str, Any], item_name: str) -> bool:
    target = _normalize(item_name)
    for collection_name in ("inventory", "goods", "food"):
        for item in player.get(collection_name, []) or []:
            name = item.get("name") if isinstance(item, dict) else item
            if _normalize(name) == target:
                return True
    return False


def _remove_named_item(player: dict[str, Any], item_name: str) -> bool:
    target = _normalize(item_name)
    for collection_name in ("inventory", "goods", "food"):
        collection = player.get(collection_name, []) or []
        for index, item in enumerate(list(collection)):
            name = item.get("name") if isinstance(item, dict) else item
            if _normalize(name) == target:
                collection.pop(index)
                return True
    return False


def _helper_index(player: dict[str, Any], requested: str) -> int:
    target = _normalize(requested)
    for index, helper in enumerate(player.get("helpers", []) or []):
        if not isinstance(helper, dict):
            continue
        values = (helper.get("name"), helper.get("type"), helper.get("category"), helper.get("archetype"))
        if any(_normalize(value) == target for value in values if value):
            return index
    return -1


def _condition_matches(player: dict[str, Any], quest: dict[str, Any], condition: dict[str, Any]) -> bool:
    if not condition:
        return True
    if "flag" in condition:
        key = str(condition["flag"])
        expected = condition.get("equals", True)
        actual = quest.get("story_flags", {}).get(key, player.get("story_flags", {}).get(key))
        if actual != expected:
            return False
    if "quest_item" in condition and str(condition["quest_item"]) not in set(quest.get("quest_items", []) or []):
        return False
    if "failures_gte" in condition and int(quest.get("failures", 0) or 0) < int(condition["failures_gte"]):
        return False
    if "failures_lt" in condition and int(quest.get("failures", 0) or 0) >= int(condition["failures_lt"]):
        return False
    if "started" in condition and bool(quest.get("started", False)) != bool(condition["started"]):
        return False
    return True


def option_state(player: dict[str, Any], quest: dict[str, Any], option: dict[str, Any]) -> dict[str, Any]:
    visible = _condition_matches(player, quest, option.get("visible_if") or {})
    disabled = False
    reason = ""
    if visible and option.get("disabled_if") and _condition_matches(player, quest, option.get("disabled_if") or {}):
        disabled = True
        reason = option.get("disabled_reason") or "Ta możliwość nie jest już dostępna."
    manual_reason = quest.get("disabled_options", {}).get(str(option.get("option_id")))
    if manual_reason:
        disabled = True
        reason = str(manual_reason)
    return {"visible": visible, "disabled": disabled, "reason": reason}


def _check_requirements(player: dict[str, Any], quest: dict[str, Any], option: dict[str, Any]) -> tuple[bool, str]:
    requirements = _copy(option.get("requires") or {})
    consumes = _copy(option.get("consumes") or {})

    # Stare pola zachowujemy jako koszt/Zużywa dla kompatybilności.
    legacy_materials = option.get("materials") or {}
    if legacy_materials:
        consumes.setdefault("materials", {}).update(legacy_materials)
    if int(option.get("gold_cost", 0) or 0):
        consumes["gold"] = int(option.get("gold_cost", 0) or 0)
    if option.get("item_cost"):
        consumes["item"] = option.get("item_cost")

    for source in (requirements, consumes):
        for material, amount in (source.get("materials") or {}).items():
            if _material_count(player, material) < int(amount):
                return False, f"Ta opcja wymaga {amount} szt. materiału: {material}."
        gold = int(source.get("gold", 0) or 0)
        if int(player.get("gold", 0) or 0) < gold:
            return False, f"Ta opcja wymaga {gold} Złota."
        item = source.get("item")
        if item and not _named_item_exists(player, str(item)):
            return False, f"Ta opcja wymaga przedmiotu: {item}."
        helper = source.get("helper")
        if helper and _helper_index(player, str(helper)) < 0:
            return False, f"Ta opcja wymaga Pomocnika: {helper}."
        qitem = source.get("quest_item")
        if qitem and str(qitem) not in set(quest.get("quest_items", []) or []):
            return False, f"Ta opcja wymaga elementu questowego: {qitem}."
    return True, ""


def _consume_requirements(player: dict[str, Any], quest: dict[str, Any], option: dict[str, Any]) -> None:
    consumes = _copy(option.get("consumes") or {})
    legacy_materials = option.get("materials") or {}
    if legacy_materials:
        consumes.setdefault("materials", {}).update(legacy_materials)
    if int(option.get("gold_cost", 0) or 0):
        consumes["gold"] = int(option.get("gold_cost", 0) or 0)
    if option.get("item_cost"):
        consumes["item"] = option.get("item_cost")

    for material, amount in (consumes.get("materials") or {}).items():
        _consume_material(player, material, int(amount))
    gold = int(consumes.get("gold", 0) or 0)
    if gold:
        player["gold"] = max(0, int(player.get("gold", 0) or 0) - gold)
    if consumes.get("item"):
        _remove_named_item(player, str(consumes["item"]))
    if consumes.get("helper"):
        index = _helper_index(player, str(consumes["helper"]))
        if index >= 0:
            player.get("helpers", []).pop(index)
    if consumes.get("quest_item"):
        value = str(consumes["quest_item"])
        items = quest.setdefault("quest_items", [])
        if value in items:
            items.remove(value)


def _remove_active_quest(player: dict[str, Any], quest: dict[str, Any]) -> None:
    active = player.setdefault("active_quests", [])
    for index, candidate in enumerate(list(active)):
        if candidate is quest or (isinstance(candidate, dict) and candidate.get("id") == quest.get("id")):
            active.pop(index)
            return


def scaled_gold_reward(base_gold: int, failures: int) -> int:
    """Kompatybilne API V1: porażki nie zmniejszają już globalnie nagrody."""
    return max(0, int(base_gold or 0))


def _apply_reward(player: dict[str, Any], quest: dict[str, Any], definition: dict[str, Any], reward_override=None) -> dict[str, Any]:
    ensure_hero_state(player)
    reward = _copy(definition.get("reward") if reward_override is None else reward_override) or {}
    result = {
        "gold": max(0, int(reward.get("gold", 0) or 0)),
        "legend": int(reward.get("legend", 0) or 0),
        "items": [],
        "food": [],
        "goods": [],
        "materials": {},
    }
    player["gold"] += result["gold"]
    player["legend"] += result["legend"]

    food = reward.get("food", [])
    if isinstance(food, dict):
        for name, amount in food.items():
            player["food"].extend([name] * int(amount))
            result["food"].extend([name] * int(amount))
    else:
        for item in food or []:
            player["food"].append(item)
            result["food"].append(item)

    for good in reward.get("goods", []) or []:
        player["goods"].append(good)
        result["goods"].append(good)

    for material, amount in (reward.get("materials") or {}).items():
        player["materials"][material] = int(player["materials"].get(material, 0) or 0) + int(amount)
        result["materials"][material] = int(amount)

    raw_items = reward.get("items", []) or []
    if reward.get("item"):
        raw_items = [*raw_items, reward["item"]]
    for item in raw_items:
        normalised = normalise_item(item)
        added, _ = add_item(player, normalised, enforce_capacity=True)
        result["items"].append({"item": normalised, "in_backpack": added})
    return result


def _reward_text(reward: dict[str, Any]) -> str:
    parts = []
    if reward.get("gold"):
        parts.append(f"{reward['gold']} Złota")
    if reward.get("legend"):
        parts.append(f"{reward['legend']} Punktów Legendy")
    item_names = [entry["item"]["name"] for entry in reward.get("items", [])]
    if item_names:
        parts.append(", ".join(item_names))
    if reward.get("food"):
        parts.append(f"{len(reward['food'])} szt. jedzenia")
    return ", ".join(parts)


def clear_quest_markers(quest: dict[str, Any]) -> list[dict[str, Any]]:
    removed = list(quest.get("markers", []) or [])
    quest["markers"] = []
    return removed


def create_quest_markers(quest: dict[str, Any], count: int = 1, payload: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    markers = quest.setdefault("markers", [])
    number = int(quest.get("quest_number", 0) or 0)
    created = []
    for _ in range(max(0, int(count))):
        marker = {
            "marker_id": f"q{number}:{len(markers) + 1}",
            "quest_id": quest.get("id"),
            "quest_number": number,
            "resolved": False,
            **_copy(payload or {}),
        }
        markers.append(marker)
        created.append(marker)
    return _copy(created)


def resolve_quest_marker(quest: dict[str, Any], marker_id: str) -> bool:
    for marker in quest.get("markers", []) or []:
        if str(marker.get("marker_id")) == str(marker_id):
            marker["resolved"] = True
            return True
    return False


def discover_expansion(quest: dict[str, Any], expansion_id: str) -> tuple[bool, str]:
    expansion = quest_expansion(expansion_id)
    if not expansion:
        return False, f"Brak karty rozwinięcia {expansion_id} w Talii Rozwinięć Questów."
    if str(expansion.get("quest_id")) != str(quest.get("id")):
        return False, f"Rozwinięcie {expansion_id} nie należy do tego Questa."
    discovered = quest.setdefault("discovered_expansions", [])
    if expansion_id not in discovered:
        discovered.append(expansion_id)
    return True, f"Dobierz rozwinięcie {expansion_id}."


def _apply_effect(player: dict[str, Any], quest: dict[str, Any], effect: dict[str, Any]) -> str:
    effect_type = str(effect.get("type") or "")
    if effect_type == "set_flag":
        key = str(effect.get("key") or "")
        value = effect.get("value", True)
        scope = str(effect.get("scope") or "quest")
        if scope == "player":
            player.setdefault("story_flags", {})[key] = value
        else:
            quest.setdefault("story_flags", {})[key] = value
        return f"Flaga {key} została zapisana."
    if effect_type == "quest_item":
        item = str(effect.get("item") or "")
        if item and item not in quest.setdefault("quest_items", []):
            quest["quest_items"].append(item)
        return f"Zdobyto element questowy: {item}."
    if effect_type == "remove_quest_item":
        item = str(effect.get("item") or "")
        if item in quest.setdefault("quest_items", []):
            quest["quest_items"].remove(item)
        return f"Usunięto element questowy: {item}."
    if effect_type == "gold":
        amount = int(effect.get("amount", 0) or 0)
        player["gold"] = max(0, int(player.get("gold", 0) or 0) + amount)
        return f"Zmiana Złota: {amount:+d}."
    if effect_type == "legend":
        amount = int(effect.get("amount", 0) or 0)
        player["legend"] = max(0, int(player.get("legend", 0) or 0) + amount)
        return f"Zmiana Legendy: {amount:+d}."
    if effect_type == "materials":
        for name, amount in (effect.get("values") or {}).items():
            player.setdefault("materials", {})[name] = int(player["materials"].get(name, 0) or 0) + int(amount)
        return "Zmieniono Towary/materiały."
    if effect_type == "paragraph":
        quest["current_paragraph"] = str(effect.get("id") or "")
        return f"Przeczytaj akapit {quest['current_paragraph']}."
    if effect_type == "expansion":
        ok, message = discover_expansion(quest, str(effect.get("id") or ""))
        return message if ok else message
    if effect_type == "ending":
        quest["ending_id"] = str(effect.get("id") or "")
        return f"Zakończenie: {quest['ending_id']}."
    if effect_type == "disable_option":
        option_id = str(effect.get("option_id") or "")
        quest.setdefault("disabled_options", {})[option_id] = str(effect.get("reason") or "Ta możliwość została utracona.")
        return f"Opcja {option_id} została zablokowana."
    if effect_type == "enable_option":
        option_id = str(effect.get("option_id") or "")
        quest.setdefault("disabled_options", {}).pop(option_id, None)
        return f"Opcja {option_id} została odblokowana."
    return ""


def _apply_effects(player: dict[str, Any], quest: dict[str, Any], effects) -> str:
    messages = [_apply_effect(player, quest, effect) for effect in effects or []]
    return " ".join(message for message in messages if message)


def complete_quest(
    player: dict[str, Any],
    quest: dict[str, Any],
    note: str = "",
    *,
    ending_id: str | None = None,
    reward_override: dict[str, Any] | None = None,
) -> str:
    definition = quest_definition(str(quest.get("id")))
    if not definition:
        raise KeyError(f"Brak definicji Questa {quest.get('id')}")
    reward = _apply_reward(player, quest, definition, reward_override=reward_override)
    quest["status"] = "completed"
    quest["stage"] = "Ukończony"
    quest["objective"] = "Quest ukończony."
    quest["ending_id"] = ending_id or quest.get("ending_id")
    quest["quest_items"] = []
    clear_quest_markers(quest)
    for key, value in (definition.get("flags_on_complete") or {}).items():
        player.setdefault("story_flags", {})[key] = value
    reward_text = _reward_text(reward)
    pieces = [note.strip()]
    if quest.get("ending_id"):
        pieces.append(f"Zakończenie: {quest['ending_id']}.")
    if reward_text:
        pieces.append(f"Nagroda: {reward_text}.")
    quest["last_result"] = " ".join(piece for piece in pieces if piece)
    _remove_active_quest(player, quest)
    player.setdefault("completed_quests", []).append(quest)
    return quest["last_result"]


def fail_quest(player: dict[str, Any], quest: dict[str, Any], note: str, ending_id: str | None = None) -> str:
    quest["status"] = "failed"
    quest["stage"] = "Przegrany"
    quest["objective"] = "Quest przegrany."
    quest["ending_id"] = ending_id or quest.get("ending_id")
    quest["quest_items"] = []
    clear_quest_markers(quest)
    quest["last_result"] = note
    _remove_active_quest(player, quest)
    player.setdefault("failed_quests", []).append(quest)
    return note


def _advance_to_stage(quest: dict[str, Any], definition: dict[str, Any], stage_number: int) -> bool:
    index = _stage_index(definition, int(stage_number))
    if index < 0:
        return False
    next_stage = definition["stages"][index]
    quest["stage_number"] = int(next_stage["number"])
    quest["stage"] = f"{index + 1}/{len(definition['stages'])}"
    quest["objective"] = f"Wykonaj etap {next_stage['number']} w lokacji {next_stage.get('required_location') or definition.get('required_location')}."
    if next_stage.get("point_of_no_return"):
        quest["point_of_no_return"] = True
    return True


def _advance_one_stage(quest: dict[str, Any], definition: dict[str, Any]) -> bool:
    current = int(quest.get("stage_number", 1) or 1)
    index = _stage_index(definition, current)
    if index < 0 or index + 1 >= len(definition["stages"]):
        return False
    return _advance_to_stage(quest, definition, int(definition["stages"][index + 1]["number"]))


def _stage_is_immediate_ordinary_test(stage: dict[str, Any] | None) -> bool:
    """Pozostawione dla kompatybilności starego contentu. Nat 20 już tego nie używa."""
    return bool(stage and any(option.get("type", "test") == "test" for option in stage.get("options", []) or []))


def _auto_complete_next_test(player, quest, definition) -> str:
    """V2: Nat 20 nigdy nie zalicza kolejnego testu."""
    return ""


def _set_pending_combat(quest: dict[str, Any], option: dict[str, Any], enemy_id: str, triggered_by: str) -> str:
    quest["status"] = "combat_pending"
    quest["pending_combat"] = {
        "enemy_id": enemy_id,
        "action_paid": True,
        "triggered_by": triggered_by,
        "on_victory": option.get("on_success", "next"),
        "on_defeat": option.get("combat_defeat", "quest_failure"),
        "option_id": option.get("option_id"),
    }
    return option.get("text") or "Rozpoczyna się walka."


def _resolve_action(player: dict[str, Any], quest: dict[str, Any], definition: dict[str, Any], option: dict[str, Any], action: str, success: bool) -> str:
    action = str(action or ("next" if success else "retry"))
    effects = option.get("success_effects" if success else "failure_effects") or []
    effect_message = _apply_effects(player, quest, effects)

    paragraph_key = "success_paragraph" if success else "failure_paragraph"
    paragraph = option.get(paragraph_key)
    if paragraph:
        quest["current_paragraph"] = str(paragraph)

    if action == "complete":
        message = complete_quest(player, quest, "Quest zakończony sukcesem.")
    elif action.startswith("complete:"):
        ending_id = action.split(":", 1)[1]
        message = complete_quest(player, quest, "Quest zakończony.", ending_id=ending_id)
    elif action == "fail":
        message = fail_quest(player, quest, "Konsekwencja karty kończy Quest niepowodzeniem.")
    elif action.startswith("stage:"):
        target = int(action.split(":", 1)[1])
        message = f"Przechodzisz do etapu {target}." if _advance_to_stage(quest, definition, target) else "Brak wskazanego etapu."
    elif action.startswith("expansion:"):
        expansion_id = action.split(":", 1)[1]
        _ok, message = discover_expansion(quest, expansion_id)
    elif action.startswith("paragraph:"):
        paragraph_id = action.split(":", 1)[1]
        quest["current_paragraph"] = paragraph_id
        message = f"Przeczytaj akapit {paragraph_id}."
    elif action.startswith("combat:"):
        enemy_id = action.split(":", 1)[1]
        message = _set_pending_combat(quest, option, enemy_id, "success" if success else "failure")
    elif action == "next" and success:
        if _advance_one_stage(quest, definition):
            message = f"Sukces. Przechodzisz do etapu {quest['stage_number']}."
        else:
            message = complete_quest(player, quest, "Quest zakończony sukcesem.")
    else:
        message = "Możesz podjąć kolejną próbę."

    paragraph_message = f" Przeczytaj akapit {quest['current_paragraph']}." if paragraph else ""
    return " ".join(part for part in [message, effect_message, paragraph_message.strip()] if part).strip()


def prepare_quest_test(player: dict[str, Any], quest: dict[str, Any]) -> tuple[bool, str]:
    if quest.get("status") != "active":
        return False, "Ten Quest nie jest gotowy do przygotowania testu."
    if quest.get("preparation_used"):
        return False, "Przygotowanie zostało już wykorzystane w tym Queście."
    if quest.get("prepared"):
        return False, "Bohater jest już przygotowany do najbliższego testu."
    token = _token(player)
    if token is None or int(getattr(token, "actions", 0) or 0) < PREPARE_ACTION_COST:
        return False, "Przygotuj się wymaga 1 Akcji."
    token.actions -= PREPARE_ACTION_COST
    quest["started"] = True
    quest["prepared"] = True
    quest["preparation_used"] = True
    return True, f"Przygotowanie wykorzystane: +{PREPARE_BONUS} do najbliższego testu."


def _add_quest_failure(player: dict[str, Any], quest: dict[str, Any], details: str, penalty: int = 1) -> tuple[bool, str]:
    quest["failures"] = int(quest.get("failures", 0) or 0) + 1
    if quest["failures"] >= QUEST_FAILURE_LIMIT:
        return False, fail_quest(player, quest, f"{details} Piąty żeton porażki. Quest przegrany.")
    quest["difficulty_modifier"] = int(penalty)
    quest["last_result"] = (
        f"{details} Dodano żeton porażki ({quest['failures']}/{QUEST_FAILURE_LIMIT}). "
        f"Następny test ma próg wyższy o {quest['difficulty_modifier']}."
    )
    return False, quest["last_result"]


def resolve_option(player: dict[str, Any], quest: dict[str, Any], option_index: int, rng=None) -> tuple[bool, str]:
    rng = rng or random
    ensure_hero_state(player)
    if quest.get("status") != "active":
        return False, "Ten Quest nie oczekuje teraz na wybór."
    definition = quest_definition(str(quest.get("id")))
    stage = current_stage(quest)
    if not definition or not stage:
        return False, "Brak definicji aktualnego etapu Questa."
    options = stage.get("options", []) or []
    if option_index < 0 or option_index >= len(options):
        return False, "Nieprawidłowy wariant etapu."
    option = options[option_index]

    state = option_state(player, quest, option)
    if not state["visible"]:
        return False, "Ta możliwość nie została jeszcze odkryta."
    if state["disabled"]:
        return False, state["reason"]

    required_location = stage.get("required_location") or definition.get("required_location")
    current_location = _current_location_name(player)
    if required_location and current_location and _normalize(required_location) != _normalize(current_location):
        return False, f"Ten etap trzeba wykonać w lokacji: {required_location}."

    token = _token(player)
    action_cost = max(0, int(option.get("action_cost", 1) or 0))
    if action_cost and (token is None or int(getattr(token, "actions", 0) or 0) < action_cost):
        return False, f"Ta opcja wymaga {action_cost} Akcji."
    requirements_ok, requirements_message = _check_requirements(player, quest, option)
    if not requirements_ok:
        quest["last_result"] = requirements_message
        return False, requirements_message

    # Pierwsza faktyczna akcja rozpoczyna Quest i blokuje jego handel.
    quest["started"] = True
    if stage.get("point_of_no_return"):
        quest["point_of_no_return"] = True
    if action_cost:
        token.actions = max(0, int(token.actions) - action_cost)
    _consume_requirements(player, quest, option)

    option_type = str(option.get("type", "test"))
    if option_type == "combat":
        enemy_id = str(option.get("enemy_id") or "")
        if not enemy_id:
            return False, "Opcja walki nie wskazuje przeciwnika."
        return False, _set_pending_combat(quest, option, enemy_id, "direct")

    if option_type in {"choice", "automatic", "payment"}:
        message = _resolve_action(player, quest, definition, option, option.get("on_success", "next"), True)
        quest["last_result"] = message
        quest.setdefault("history", []).append({
            "stage": int(quest.get("stage_number", 1) or 1),
            "option": option.get("option_id"),
            "type": option_type,
            "success": True,
            "paragraph": quest.get("current_paragraph"),
        })
        return True, message

    persistent_modifier = int(quest.get("difficulty_modifier", 0) or 0)
    quest["difficulty_modifier"] = 0
    prepare_bonus = PREPARE_BONUS if quest.get("prepared") else 0
    quest["prepared"] = False
    threshold = int(option.get("threshold", 0) or 0) + persistent_modifier
    roll = int(rng.randint(1, 20))
    stat = str(option.get("stat") or "")
    stat_value = int(player.get("stats", {}).get(stat, 0) or 0)
    helper = helper_bonus(player, stat)
    equipment = equipment_stat_bonus(player, stat)
    total = roll + stat_value + helper + equipment + prepare_bonus
    success = roll == 20 or (roll != 1 and total >= threshold)

    paragraph = None
    if roll == 20 and option.get("nat20_paragraph"):
        paragraph = str(option["nat20_paragraph"])
    elif roll == 1 and option.get("nat1_paragraph"):
        paragraph = str(option["nat1_paragraph"])
    elif success and option.get("success_paragraph"):
        paragraph = str(option["success_paragraph"])
    elif not success and option.get("failure_paragraph"):
        paragraph = str(option["failure_paragraph"])
    if paragraph:
        quest["current_paragraph"] = paragraph

    details = (
        f"Rzut {roll} + {stat} {stat_value} + Pomocnik {helper} + ekwipunek {equipment}"
        f" + przygotowanie {prepare_bonus} = {total} przeciw {threshold}."
    )
    quest.setdefault("history", []).append({
        "stage": int(quest.get("stage_number", 1) or 1),
        "option": option.get("option_id"),
        "roll": roll,
        "total": total,
        "threshold": threshold,
        "success": success,
        "paragraph": paragraph,
    })

    if success:
        result = _resolve_action(player, quest, definition, option, option.get("on_success", "next"), True)
        quest["last_result"] = f"{details} {result}".strip()
        return True, quest["last_result"]

    failed, message = _add_quest_failure(player, quest, details, penalty=2 if roll == 1 else 1)
    if quest.get("status") == "failed":
        return failed, message
    action_message = _resolve_action(player, quest, definition, option, option.get("on_failure", "retry"), False)
    quest["last_result"] = f"{message} {action_message}".strip()
    return False, quest["last_result"]


def resolve_pending_combat_victory(player: dict[str, Any], quest: dict[str, Any], combat_log: str = "") -> str:
    pending = dict(quest.get("pending_combat") or {})
    definition = quest_definition(str(quest.get("id")))
    stage = current_stage(quest)
    option = None
    for candidate in (stage or {}).get("options", []) or []:
        if candidate.get("option_id") == pending.get("option_id"):
            option = candidate
            break
    option = option or {"on_success": pending.get("on_victory", "next"), "success_effects": []}
    quest["status"] = "active"
    quest["pending_combat"] = None
    action = str(pending.get("on_victory") or option.get("on_success") or "next")
    message = _resolve_action(player, quest, definition, option, action, True) if definition else "Walka wygrana."
    return " ".join(part for part in [combat_log, message] if part).strip()


def resolve_pending_combat_defeat(player: dict[str, Any], quest: dict[str, Any], combat_log: str = "") -> str:
    pending = dict(quest.get("pending_combat") or {})
    quest["pending_combat"] = None
    forced = str(pending.get("on_defeat") or "quest_failure")
    if forced == "fail_quest":
        return fail_quest(player, quest, f"{combat_log} Przegrana tej walki kończy Quest.".strip())
    quest["status"] = "active"
    _ok, message = _add_quest_failure(player, quest, combat_log or "Przegrana walka.", penalty=1)
    return message


def tick_quest_time(player: dict[str, Any], quest: dict[str, Any], clock: str) -> tuple[bool, str]:
    limit = quest.get("time_limit") or {}
    if not limit or str(limit.get("clock") or "") != str(clock):
        return True, ""
    if quest.get("time_remaining") is None:
        quest["time_remaining"] = int(limit.get("amount", 0) or 0)
    quest["time_remaining"] = int(quest.get("time_remaining", 0) or 0) - 1
    if quest["time_remaining"] > 0:
        return True, f"Pozostało: {quest['time_remaining']}."
    action = str(limit.get("on_expire") or "fail")
    if action == "fail":
        return False, fail_quest(player, quest, "Minął czas na wykonanie Questa.")
    quest["ending_id"] = action
    return False, f"Limit czasu uruchamia zakończenie: {action}."


def abandon_quest(player: dict[str, Any], quest: dict[str, Any]) -> tuple[bool, str]:
    definition = quest_definition(str(quest.get("id")))
    if not definition or not definition.get("abandonable", True):
        return False, "Tego Questa nie można porzucić."
    if quest.get("point_of_no_return"):
        return False, "Ten etap jest punktem bez powrotu. Nie możesz teraz porzucić Questa."
    if not quest.get("started", False):
        return return_unstarted_quest(player, quest)
    quest["status"] = "abandoned"
    quest["stage"] = "Porzucony"
    quest["objective"] = "Quest porzucony."
    quest["quest_items"] = []
    clear_quest_markers(quest)
    quest["last_result"] = "Quest został porzucony bez nagrody."
    _remove_active_quest(player, quest)
    player.setdefault("abandoned_quests", []).append(quest)
    return True, quest["last_result"]
