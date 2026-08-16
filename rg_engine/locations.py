from __future__ import annotations

import copy
from typing import Any

from rg_engine.heroes import heal_at_location, train_stat
from rg_engine.items import (
    add_item,
    equip_inventory_item,
    normalise_item,
    sell_inventory_item,
    unequip_slot,
)
from rg_engine.quests import activate_quest, can_accept_quest, is_registered_quest, quest_definition
from rg_engine.world import registered_players
from rg_engine.world_events import price_with_world_event

TRAINING_STATS = {
    "city": ("Dyplomacja", "Nauka", "Handel"),
    "village": ("Handel", "Intryga", "Kultura"),
    "castle": ("Walka", "Intryga", "Nauka"),
}


def training_stats_for(location_kind: str) -> tuple[str, ...]:
    return TRAINING_STATS.get(str(location_kind), ())


def purchase_card(player: dict[str, Any], card: dict[str, Any]) -> tuple[bool, str]:
    base_price = max(0, int(card.get("price", 0) or 0))
    price = price_with_world_event(base_price)
    if int(player.get("gold", 0) or 0) < price:
        return False, "Nie masz wystarczajacej liczby monet."
    category = str(card.get("category", "misc"))
    if category in {"weapon", "armor", "helmet", "boots", "gloves", "amulet", "ring"}:
        added, message = add_item(player, normalise_item(card), enforce_capacity=True)
        if not added:
            player.get("overflow_items", []).pop()
            return False, "Plecak jest pelny. Najpierw zwolnij miejsce."
    elif category == "food":
        player.setdefault("food", []).append(card.get("name", "Jedzenie"))
        message = f"Dodano jedzenie: {card.get('name', 'Jedzenie')}."
    else:
        player.setdefault("goods", []).append(card.get("name", "Towar"))
        message = f"Dodano towar: {card.get('name', 'Towar')}."
    player["gold"] = int(player.get("gold", 0) or 0) - price
    return True, f"Kupiono {card.get('name', 'karte')} za {price} monet. {message}"


def hire_helper_card(player: dict[str, Any], helper: dict[str, Any], limit: int = 5) -> tuple[bool, str]:
    helpers = player.setdefault("helpers", [])
    if len(helpers) >= limit:
        return False, f"Masz juz maksymalnie {limit} pomocnikow."
    base_price = max(0, int(helper.get("price", 0) or 0))
    price = price_with_world_event(base_price)
    if int(player.get("gold", 0) or 0) < price:
        return False, "Nie masz wystarczajacej liczby monet."
    player["gold"] -= price
    helpers.append(copy.deepcopy(helper))
    return True, f"Zatrudniono: {helper.get('name', 'Pomocnik')} za {price} monet."


def _quest_seen(player: dict[str, Any], quest_id: str, collections: tuple[str, ...]) -> bool:
    for key in collections:
        for item in player.get(key, []) or []:
            if isinstance(item, dict) and str(item.get("id")) == str(quest_id):
                return True
    return False


def _quest_active_in_world(quest_id: str, owner: dict[str, Any]) -> bool:
    for other in registered_players():
        if other is owner:
            continue
        if _quest_seen(other, quest_id, ("active_quests",)):
            return True
    return False


def _quest_resolved_in_world(quest_id: str) -> bool:
    for hero in registered_players():
        if _quest_seen(hero, quest_id, ("completed_quests", "failed_quests", "abandoned_quests")):
            return True
    return False


def accept_quest_card(player: dict[str, Any], quest_card: dict[str, Any]) -> tuple[bool, str]:
    allowed, reason = can_accept_quest(player)
    if not allowed:
        return False, reason
    active = player.setdefault("active_quests", [])
    if is_registered_quest(quest_card):
        quest_id = str(quest_card.get("id"))
        definition = quest_definition(quest_id) or {}
        if _quest_seen(player, quest_id, ("active_quests",)):
            return False, "Ten Quest jest juz aktywny u tego bohatera."
        if _quest_active_in_world(quest_id, player):
            return False, "Ten Quest jest juz w posiadaniu innego bohatera."
        if definition.get("unique", False) and _quest_resolved_in_world(quest_id):
            return False, "Ten unikalny Quest zostal juz rozstrzygniety w tej rozgrywce."
        runtime = activate_quest(quest_card)
    else:
        runtime = copy.deepcopy(quest_card)
        runtime.setdefault("deck", "Questy")
        runtime.setdefault("status", "active")
        runtime.setdefault("started", False)
        runtime.setdefault("failures", 0)
        runtime.setdefault("preparation_used", False)
        runtime.setdefault("discovered_expansions", [])
        runtime.setdefault("markers", [])
    active.append(runtime)
    return True, f"Pobrano Quest: {runtime.get('name', 'Quest')}."


def train_in_location(player: dict[str, Any], token, location: dict[str, Any], stat: str) -> tuple[bool, str]:
    return train_stat(player, token, stat, training_stats_for(location.get("kind", "")))


def heal_in_location(player: dict[str, Any], token, amount: int | None = None) -> tuple[bool, str]:
    return heal_at_location(player, token, amount)


def equip_from_backpack(player: dict[str, Any], inventory_index: int) -> tuple[bool, str]:
    return equip_inventory_item(player, inventory_index)


def unequip_to_backpack(player: dict[str, Any], slot: str) -> tuple[bool, str]:
    return unequip_slot(player, slot)


def sell_from_backpack(player: dict[str, Any], inventory_index: int) -> tuple[bool, str]:
    success, message, _value = sell_inventory_item(player, inventory_index)
    return success, message
