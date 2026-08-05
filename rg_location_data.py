import copy
import random
from collections.abc import MutableMapping

from rg_content import load_helpers, load_item_pools, load_quests, load_shop_layouts
from rg_models import LocationState, QuestInstance

_ITEM_POOLS = load_item_pools()
FOOD_CARDS = list(_ITEM_POOLS["food"])
BASIC_GOODS_CARDS = list(_ITEM_POOLS["basic_good"])
LUXURY_CARDS = list(_ITEM_POOLS["luxury"])
RING_CARDS = list(_ITEM_POOLS["ring"])
WEAPON_CARDS = list(_ITEM_POOLS["weapon"])
ARMOR_CARDS = list(_ITEM_POOLS["armor"])
HELPER_CARDS = list(load_helpers())
QUEST_CARDS = list(load_quests())
SHOP_POOLS = {key: list(value) for key, value in _ITEM_POOLS.items()}
SHOP_LAYOUTS = {key: list(value) for key, value in load_shop_layouts().items()}


def helper_effect_text(helper):
    return helper.get("effect_text") or helper.get("description", "Brak opisanego efektu.")


def helper_bonus_summary(player):
    bonuses = {}
    for helper in player.get("helpers", []):
        for stat, value in helper.get("stat_bonus", {}).items():
            bonuses[stat] = bonuses.get(stat, 0) + value
    return bonuses


def _copy_card(card):
    return copy.deepcopy(card)


def _draw_unique(pool, visible, rng):
    visible_names = {card["name"] for card in visible if card}
    candidates = [card for card in pool if card["name"] not in visible_names]
    return _copy_card(rng.choice(candidates or pool))


def _draw_quest(visible, rng):
    visible_decks = {card["deck"] for card in visible if card}
    candidates = [card for card in QUEST_CARDS if card["deck"] not in visible_decks]
    if not candidates:
        visible_names = {card["name"] for card in visible if card}
        candidates = [card for card in QUEST_CARDS if card["name"] not in visible_names]
    return _copy_card(rng.choice(candidates or QUEST_CARDS))


def _as_location_state(location):
    if isinstance(location, LocationState):
        return location
    if isinstance(location, MutableMapping):
        return LocationState.from_mapping(location)
    raise TypeError("location musi byc LocationState albo mapowaniem")


def initialize_location(location, rng=None):
    state = _as_location_state(location)
    if state.offers_ready:
        return state
    rng = rng or random
    state.shop_layout = list(SHOP_LAYOUTS.get(state.kind, SHOP_LAYOUTS["city"]))
    state.shop_offers = []
    for category in state.shop_layout:
        state.shop_offers.append(_draw_unique(SHOP_POOLS[category], state.shop_offers, rng))
    state.helper_offers = []
    for _ in range(3):
        state.helper_offers.append(_draw_unique(HELPER_CARDS, state.helper_offers, rng))
    state.quest_offers = []
    for _ in range(3):
        state.quest_offers.append(_draw_quest(state.quest_offers, rng))
    state.offers_ready = True
    return state


def buy_shop_item(location, player, slot_index, rng=None):
    rng = rng or random
    location = initialize_location(location, rng)
    offers = location.shop_offers
    if slot_index < 0 or slot_index >= len(offers):
        return False, "Nieprawidlowy slot sklepu."
    card = offers[slot_index]
    if player.get("gold", 0) < card.price:
        return False, "Nie masz wystarczajacej liczby monet."
    player["gold"] -= card.price
    if card.category == "food":
        player.setdefault("food", []).append(card.name)
    elif card.category in {"basic_good", "luxury"}:
        player.setdefault("goods", []).append(card.name)
    else:
        player.setdefault("inventory", []).append(_copy_card(card))
    visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
    offers[slot_index] = _draw_unique(SHOP_POOLS[card.category], visible_without_slot, rng)
    return True, f"Kupiono: {card.name} za {card.price} monet."


def hire_helper(location, player, slot_index, rng=None):
    rng = rng or random
    location = initialize_location(location, rng)
    offers = location.helper_offers
    if slot_index < 0 or slot_index >= len(offers):
        return False, "Nieprawidlowy slot pomocnika."
    if len(player.setdefault("helpers", [])) >= 5:
        return False, "Masz juz maksymalnie 5 pomocnikow."
    helper = offers[slot_index]
    if player.get("gold", 0) < helper.price:
        return False, "Nie masz wystarczajacej liczby monet."
    player["gold"] -= helper.price
    player["helpers"].append(_copy_card(helper))
    visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
    offers[slot_index] = _draw_unique(HELPER_CARDS, visible_without_slot, rng)
    return True, f"Zatrudniono: {helper.name} - {helper_effect_text(helper)}"


def take_quest(location, player, slot_index, rng=None):
    rng = rng or random
    location = initialize_location(location, rng)
    offers = location.quest_offers
    if slot_index < 0 or slot_index >= len(offers):
        return False, "Nieprawidlowy slot questa."
    if len(player.setdefault("active_quests", [])) >= 3:
        return False, "Masz juz maksymalnie 3 aktywne questy."
    quest = offers[slot_index]
    player["active_quests"].append(QuestInstance.from_definition(quest))
    visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
    offers[slot_index] = _draw_quest(visible_without_slot, rng)
    return True, f"Pobrano quest: {quest.name}."
