from __future__ import annotations

import copy
import math
import random
import unicodedata
from typing import Any

from rg_engine.heroes import ensure_hero_state, helper_bonus
from rg_engine.items import add_item, equipment_stat_bonus, normalise_item
from rg_engine.models import QuestDefinition

_QUESTS: dict[str, dict[str, Any]] = {}


def _normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    return "".join(character for character in ascii_text if character.isalnum())


def register_quest(definition: QuestDefinition | dict[str, Any]) -> dict[str, Any]:
    quest = definition.to_dict() if isinstance(definition, QuestDefinition) else copy.deepcopy(definition)
    quest_id = str(quest.get("id") or quest.get("quest_id"))
    if not quest_id:
        raise ValueError("Definicja questa wymaga pola id.")
    quest["id"] = quest_id
    quest.pop("quest_id", None)
    stages = sorted(list(quest.get("stages", [])), key=lambda stage: int(stage.get("number", 0)))
    if not stages:
        raise ValueError(f"Quest {quest_id} nie posiada etapow.")
    for expected, stage in enumerate(stages, start=1):
        stage.setdefault("number", expected)
        stage.setdefault("title", f"Etap {expected}")
        stage.setdefault("text", "")
        stage.setdefault("options", [])
        stage.setdefault("required_location", quest.get("required_location"))
        stage.setdefault("image", quest.get("image", ""))
        for option_index, option in enumerate(stage["options"]):
            option.setdefault("option_id", f"{quest_id}_{expected}_{option_index}")
            option.setdefault("label", f"Opcja {option_index + 1}")
            option.setdefault("type", "test")
            option.setdefault("action_cost", 1)
            option.setdefault("materials", {})
            option.setdefault("gold_cost", 0)
            option.setdefault("on_success", "next")
            option.setdefault("on_failure", "retry")
    quest["stages"] = stages
    quest.setdefault("reward", {})
    quest.setdefault("world_level_min", 1)
    quest.setdefault("board_text", quest.get("description", ""))
    quest.setdefault("unique", False)
    quest.setdefault("shared", False)
    quest.setdefault("sellable", True)
    quest.setdefault("tradeable", True)
    quest.setdefault("abandonable", True)
    _QUESTS[quest_id] = quest
    return copy.deepcopy(quest)


def quest_definition(quest_id: str) -> dict[str, Any] | None:
    definition = _QUESTS.get(str(quest_id))
    return copy.deepcopy(definition) if definition else None


def is_registered_quest(quest_or_id: Any) -> bool:
    quest_id = quest_or_id.get("id") if isinstance(quest_or_id, dict) else quest_or_id
    return str(quest_id) in _QUESTS


def create_offer(quest_id: str) -> dict[str, Any]:
    definition = quest_definition(quest_id)
    if not definition:
        raise KeyError(f"Nieznany quest: {quest_id}")
    return {
        "id": definition["id"],
        "name": definition["name"],
        "deck": definition["deck"],
        "description": definition.get("board_text") or definition.get("description", ""),
        "objective": definition.get("objective", ""),
        "required_location": definition.get("required_location"),
        "world_level_min": int(definition.get("world_level_min", 1) or 1),
        "status": "offer",
        "unique": bool(definition.get("unique", False)),
    }


def activate_quest(quest_or_id: dict[str, Any] | str) -> dict[str, Any]:
    quest_id = quest_or_id.get("id") if isinstance(quest_or_id, dict) else quest_or_id
    definition = quest_definition(str(quest_id))
    if not definition:
        raise KeyError(f"Nieznany quest: {quest_id}")
    first_stage = definition["stages"][0]
    return {
        "id": definition["id"],
        "name": definition["name"],
        "deck": definition["deck"],
        "description": definition.get("description", ""),
        "objective": definition.get("objective", ""),
        "required_location": definition.get("required_location"),
        "world_level_min": int(definition.get("world_level_min", 1) or 1),
        "status": "active",
        "stage_number": int(first_stage.get("number", 1)),
        "stage": f"1/{len(definition['stages'])}",
        "failures": 0,
        "difficulty_modifier": 0,
        "last_result": f"Quest pobrany. Udaj sie do lokacji: {definition.get('required_location', '-')}",
        "pending_combat": None,
        "history": [],
    }


def find_player_quest(player: dict[str, Any], quest_id: str, include_history: bool = True) -> dict[str, Any] | None:
    for quest in player.get("active_quests", []) or []:
        if isinstance(quest, dict) and quest.get("id") == quest_id:
            return quest
    if include_history:
        for key in ("completed_quests", "failed_quests"):
            for quest in player.get(key, []) or []:
                if isinstance(quest, dict) and quest.get("id") == quest_id:
                    return quest
    return None


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
    return copy.deepcopy(definition["stages"][index]) if index >= 0 else None


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


def _check_option_costs(player: dict[str, Any], option: dict[str, Any]) -> tuple[bool, str]:
    for material, amount in (option.get("materials") or {}).items():
        if _material_count(player, material) < int(amount):
            return False, f"Ta opcja wymaga {amount} szt. materialu: {material}."
    gold_cost = int(option.get("gold_cost", 0) or 0)
    if int(player.get("gold", 0) or 0) < gold_cost:
        return False, f"Ta opcja wymaga {gold_cost} monet."
    item_cost = option.get("item_cost")
    if item_cost:
        found = False
        for key in ("inventory", "goods", "food"):
            for item in player.get(key, []) or []:
                name = item.get("name") if isinstance(item, dict) else item
                if _normalize(name) == _normalize(item_cost):
                    found = True
                    break
            if found:
                break
        if not found:
            return False, f"Ta opcja wymaga przedmiotu: {item_cost}."
    return True, ""


def _consume_option_costs(player: dict[str, Any], option: dict[str, Any]) -> None:
    for material, amount in (option.get("materials") or {}).items():
        _consume_material(player, material, int(amount))
    gold_cost = int(option.get("gold_cost", 0) or 0)
    if gold_cost:
        player["gold"] = max(0, int(player.get("gold", 0) or 0) - gold_cost)
    if option.get("item_cost"):
        _remove_named_item(player, str(option["item_cost"]))


def _remove_active_quest(player: dict[str, Any], quest: dict[str, Any]) -> None:
    active = player.setdefault("active_quests", [])
    for index, candidate in enumerate(list(active)):
        if candidate is quest or (isinstance(candidate, dict) and candidate.get("id") == quest.get("id")):
            active.pop(index)
            return


def scaled_gold_reward(base_gold: int, failures: int) -> int:
    fractions = (1.0, 0.75, 0.5, 0.25)
    index = max(0, min(3, int(failures or 0)))
    return max(0, int(math.ceil(max(0, int(base_gold or 0)) * fractions[index])))


def _apply_reward(player: dict[str, Any], quest: dict[str, Any], definition: dict[str, Any]) -> dict[str, Any]:
    ensure_hero_state(player)
    reward = copy.deepcopy(definition.get("reward") or {})
    failures = int(quest.get("failures", 0) or 0)
    result = {
        "gold": scaled_gold_reward(int(reward.get("gold", 0) or 0), failures),
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


def complete_quest(player: dict[str, Any], quest: dict[str, Any], note: str = "") -> str:
    definition = quest_definition(str(quest.get("id")))
    if not definition:
        raise KeyError(f"Brak definicji questa {quest.get('id')}")
    reward = _apply_reward(player, quest, definition)
    quest["status"] = "completed"
    quest["stage"] = "Ukonczony"
    quest["objective"] = "Quest ukonczony."
    item_names = [entry["item"]["name"] for entry in reward["items"]]
    parts = []
    if reward["gold"]:
        parts.append(f"{reward['gold']} zlota")
    if reward["legend"]:
        parts.append(f"{reward['legend']} Punkty Legendy")
    if item_names:
        parts.append(", ".join(item_names))
    if reward["food"]:
        parts.append(f"{len(reward['food'])} szt. jedzenia")
    quest["last_result"] = " ".join(filter(None, [note.strip(), "Nagroda: " + ", ".join(parts) + "."]))
    _remove_active_quest(player, quest)
    player.setdefault("completed_quests", []).append(quest)
    return quest["last_result"]


def fail_quest(player: dict[str, Any], quest: dict[str, Any], note: str) -> str:
    quest["status"] = "failed"
    quest["stage"] = "Przegrany"
    quest["objective"] = "Quest przegrany."
    quest["last_result"] = note
    _remove_active_quest(player, quest)
    player.setdefault("failed_quests", []).append(quest)
    return note


def _stage_is_immediate_ordinary_test(stage: dict[str, Any] | None) -> bool:
    if not stage:
        return False
    options = stage.get("options", []) or []
    if not options:
        return False
    for option in options:
        if option.get("type", "test") != "test":
            continue
        if option.get("materials") or option.get("gold_cost") or option.get("item_cost"):
            continue
        return True
    return False


def _advance_one_stage(quest: dict[str, Any], definition: dict[str, Any]) -> bool:
    current = int(quest.get("stage_number", 1) or 1)
    index = _stage_index(definition, current)
    if index < 0 or index + 1 >= len(definition["stages"]):
        return False
    next_stage = definition["stages"][index + 1]
    quest["stage_number"] = int(next_stage["number"])
    quest["stage"] = f"{index + 2}/{len(definition['stages'])}"
    quest["objective"] = f"Wykonaj etap {next_stage['number']} w lokacji {next_stage.get('required_location') or definition.get('required_location')}."
    return True


def _auto_complete_next_test(player: dict[str, Any], quest: dict[str, Any], definition: dict[str, Any]) -> str:
    current = int(quest.get("stage_number", 1) or 1)
    index = _stage_index(definition, current)
    next_stage = definition["stages"][index + 1] if 0 <= index < len(definition["stages"]) - 1 else None
    if not _stage_is_immediate_ordinary_test(next_stage):
        return ""
    if index + 1 == len(definition["stages"]) - 1:
        return complete_quest(player, quest, "Naturalne 20 zalicza rowniez kolejny dostepny test.")
    _advance_one_stage(quest, definition)
    return "Naturalne 20 zalicza rowniez kolejny dostepny test."


def _success(player: dict[str, Any], quest: dict[str, Any], definition: dict[str, Any], option: dict[str, Any], roll: int) -> str:
    action = str(option.get("on_success", "next"))
    if action == "complete":
        return complete_quest(player, quest, "Etap zakonczony sukcesem.")
    if action.startswith("combat:"):
        quest["status"] = "combat_pending"
        quest["pending_combat"] = {"enemy_id": action.split(":", 1)[1], "action_paid": True}
        return "Sukces prowadzi do walki."
    if not _advance_one_stage(quest, definition):
        return complete_quest(player, quest, "Quest zakonczony sukcesem.")
    message = f"Sukces. Przechodzisz do etapu {quest['stage_number']}."
    if roll == 20:
        auto_message = _auto_complete_next_test(player, quest, definition)
        if auto_message:
            return f"{message} {auto_message}".strip()
    return message


def _failure(player: dict[str, Any], quest: dict[str, Any], option: dict[str, Any], roll: int, details: str) -> tuple[bool, str]:
    quest["failures"] = int(quest.get("failures", 0) or 0) + 1
    if quest["failures"] >= 4:
        return False, fail_quest(player, quest, f"{details} Czwarty znacznik porazki. Quest przegrany.")
    quest["difficulty_modifier"] = 2 if roll == 1 else 1
    action = str(option.get("on_failure", "retry"))
    enemy_id = option.get("failure_enemy_id")
    if action.startswith("combat:"):
        enemy_id = action.split(":", 1)[1]
        action = "combat"
    if action == "combat" and enemy_id:
        quest["status"] = "combat_pending"
        quest["pending_combat"] = {"enemy_id": enemy_id, "action_paid": True}
        quest["last_result"] = f"{details} Porażka uruchamia walke."
        return False, quest["last_result"]
    quest["last_result"] = (
        f"{details} Porażka. Dodano znacznik porazki. "
        f"Nastepny test ma prog wyzszy o {quest['difficulty_modifier']}."
    )
    return False, quest["last_result"]


def resolve_option(player: dict[str, Any], quest: dict[str, Any], option_index: int, rng=None) -> tuple[bool, str]:
    rng = rng or random
    ensure_hero_state(player)
    if quest.get("status") != "active":
        return False, "Ten quest nie oczekuje teraz na wybor testu."
    definition = quest_definition(str(quest.get("id")))
    stage = current_stage(quest)
    if not definition or not stage:
        return False, "Brak definicji aktualnego etapu questa."
    options = stage.get("options", []) or []
    if option_index < 0 or option_index >= len(options):
        return False, "Nieprawidlowy wariant etapu."
    option = options[option_index]

    required_location = stage.get("required_location") or definition.get("required_location")
    current_location = _current_location_name(player)
    if required_location and current_location and _normalize(required_location) != _normalize(current_location):
        return False, f"Ten etap trzeba wykonac w lokacji: {required_location}."

    token = _token(player)
    action_cost = max(0, int(option.get("action_cost", 1) or 0))
    if action_cost and (token is None or int(getattr(token, "actions", 0) or 0) < action_cost):
        return False, f"Ta opcja wymaga {action_cost} akcji."
    costs_ok, costs_message = _check_option_costs(player, option)
    if not costs_ok:
        quest["last_result"] = costs_message
        return False, costs_message

    if action_cost:
        token.actions = max(0, int(token.actions) - action_cost)
    _consume_option_costs(player, option)

    if option.get("type", "test") == "combat":
        enemy_id = option.get("enemy_id")
        if not enemy_id:
            return False, "Opcja walki nie wskazuje przeciwnika."
        quest["status"] = "combat_pending"
        quest["pending_combat"] = {"enemy_id": enemy_id, "action_paid": True}
        quest["last_result"] = option.get("text") or "Rozpoczyna sie walka."
        return False, quest["last_result"]

    modifier = int(quest.get("difficulty_modifier", 0) or 0)
    quest["difficulty_modifier"] = 0
    threshold = int(option.get("threshold", 0) or 0) + modifier
    roll = int(rng.randint(1, 20))
    stat = str(option.get("stat") or "")
    stat_value = int(player.get("stats", {}).get(stat, 0) or 0)
    helper = helper_bonus(player, stat)
    equipment = equipment_stat_bonus(player, stat)
    total = roll + stat_value + helper + equipment
    success = roll == 20 or total >= threshold
    details = (
        f"Rzut {roll} + {stat} {stat_value} + pomocnik {helper} + ekwipunek {equipment} "
        f"= {total} przeciw {threshold}."
    )
    quest.setdefault("history", []).append(
        {
            "stage": int(quest.get("stage_number", 1) or 1),
            "option": option.get("option_id"),
            "roll": roll,
            "total": total,
            "threshold": threshold,
            "success": success,
        }
    )
    if success:
        result = _success(player, quest, definition, option, roll)
        if quest.get("status") == "active" and roll == 1:
            quest["difficulty_modifier"] = 2
        quest["last_result"] = f"{details} {result}".strip()
        return True, quest["last_result"]
    return _failure(player, quest, option, roll, details)


def abandon_quest(player: dict[str, Any], quest: dict[str, Any]) -> tuple[bool, str]:
    definition = quest_definition(str(quest.get("id")))
    if not definition or not definition.get("abandonable", True):
        return False, "Tego questa nie mozna porzucic."
    return False, fail_quest(player, quest, "Quest zostal porzucony bez nagrody.")
