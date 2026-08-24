from __future__ import annotations

import random
from typing import Iterable

from rg_core.data import ACTIONS_PER_TURN
from rg_engine.devtools import dev_flag
from rg_engine.items import discard_inventory_item, eligible_defeat_inventory_indices, ensure_equipment_state, normalise_item
from rg_engine.world import current_world_level, defeat_gold_loss
from rg_engine.world_events import healing_cost_with_world_event

MAX_WOUNDS = 4
BASE_MAX_HP = 10
MAX_STAT = 6
TRAINING_COSTS = {0: 5, 1: 8, 2: 11, 3: 14, 4: 17, 5: 20}

# Wartosci ALFA zatwierdzone dla systemu Ran.
WOUND_MAX_HP_PENALTIES = {0: 0, 1: 0, 2: 2, 3: 4, 4: 4}
WOUND_TEST_PENALTIES = {0: 0, 1: -1, 2: -1, 3: -2, 4: -2}
WOUND_ACTION_PENALTIES = {0: 0, 1: 0, 2: 0, 3: 2, 4: 2}
WOUND_HEALING_COSTS = {1: 2, 2: 3, 3: 4, 4: 5}


def _wound_count(hero_or_wounds) -> int:
    if isinstance(hero_or_wounds, dict):
        value = hero_or_wounds.get("wounds", 0)
    else:
        value = hero_or_wounds
    return max(0, min(MAX_WOUNDS, int(value or 0)))


def wound_max_hp_penalty(hero_or_wounds) -> int:
    return WOUND_MAX_HP_PENALTIES[_wound_count(hero_or_wounds)]


def wound_test_penalty(hero_or_wounds) -> int:
    return WOUND_TEST_PENALTIES[_wound_count(hero_or_wounds)]


def turn_action_limit(hero_or_wounds) -> int:
    """Techniczne odwzorowanie kary -2 do Ruchu w obecnym systemie wspolnej puli Akcji."""
    wounds = _wound_count(hero_or_wounds)
    return max(0, ACTIONS_PER_TURN - WOUND_ACTION_PENALTIES[wounds])


def _equipment_max_hp_bonus(hero: dict) -> int:
    total = 0
    for raw_item in (hero.get("equipment") or {}).values():
        if not raw_item:
            continue
        effects = normalise_item(raw_item).get("effects") or {}
        total += int(effects.get("max_hp_bonus", effects.get("max_hp", 0)) or 0)
    return total


def _recalculate_max_hp(hero: dict) -> int:
    base = max(1, int(hero.get("base_max_hp", BASE_MAX_HP) or BASE_MAX_HP))
    maximum = base + _equipment_max_hp_bonus(hero) - wound_max_hp_penalty(hero)
    hero["max_hp"] = max(1, int(maximum))
    if "hp" in hero:
        hero["hp"] = max(0, min(hero["max_hp"], int(hero.get("hp", 0) or 0)))
    return hero["max_hp"]


def ensure_hero_state(hero: dict) -> dict:
    hero.setdefault("stats", {})
    hero["gold"] = int(hero.get("gold", 0) or 0)
    hero["legend"] = int(hero.get("legend", 0) or 0)
    hero["wounds"] = _wound_count(hero)
    hero.setdefault("food", [])
    hero.setdefault("goods", [])
    hero.setdefault("materials", {})
    hero.setdefault("helpers", [])
    hero.setdefault("active_quests", [])
    hero.setdefault("completed_quests", [])
    hero.setdefault("failed_quests", [])
    hero.setdefault("inventory", [])
    hero.setdefault("equipment", {})
    hero.setdefault("overflow_items", [])
    hero.setdefault("discarded_items", [])
    hero.setdefault("defeated_enemies", [])
    hero.setdefault("status_effects", {})
    hero.setdefault("backpack_limit", 10)
    hero.setdefault("_unconscious_until_next_turn", hero["wounds"] >= MAX_WOUNDS)
    ensure_equipment_state(hero)

    if "base_max_hp" not in hero:
        hero["base_max_hp"] = max(1, int(hero.get("max_hp", BASE_MAX_HP) or BASE_MAX_HP))
    _recalculate_max_hp(hero)
    if "hp" not in hero:
        hero["hp"] = hero["max_hp"]
    hero["hp"] = max(0, min(hero["max_hp"], int(hero.get("hp", hero["max_hp"]) or 0)))
    return hero


def helper_bonus(hero: dict, stat: str) -> int:
    """Zwraca laczny modyfikator testu: najlepszy Pomocnik + kara z Ran."""
    ensure_hero_state(hero)
    helper = max(
        (
            int(helper.get("stat_bonus", {}).get(stat, 0) or 0)
            for helper in hero.get("helpers", [])
            if isinstance(helper, dict)
        ),
        default=0,
    )
    return helper + wound_test_penalty(hero)


def helper_combat_bonus(hero: dict, key: str) -> int:
    ensure_hero_state(hero)
    return max(
        (
            int((helper.get("combat_bonus") or {}).get(key, 0) or 0)
            for helper in hero.get("helpers", [])
            if isinstance(helper, dict)
        ),
        default=0,
    )


def apply_damage(hero: dict, amount: int) -> tuple[int, bool]:
    ensure_hero_state(hero)
    damage = max(0, int(amount or 0))
    previous = int(hero.get("hp", 0) or 0)
    hero["hp"] = max(0, previous - damage)
    return previous - hero["hp"], hero["hp"] <= 0


def heal_hp(hero: dict, amount: int | None = None) -> int:
    ensure_hero_state(hero)
    current = int(hero.get("hp", 0) or 0)
    maximum = int(hero.get("max_hp", BASE_MAX_HP) or BASE_MAX_HP)
    if current >= maximum:
        return 0
    healed = maximum - current if amount is None else min(maximum - current, max(0, int(amount)))
    hero["hp"] = current + healed
    return healed


def _resolve_defeat_item(hero: dict, allow_random: bool = False):
    chosen_index = hero.pop("_combat_defeat_item_index", None)
    eligible = eligible_defeat_inventory_indices(hero)
    if chosen_index is not None and int(chosen_index) in eligible:
        return discard_inventory_item(hero, int(chosen_index))
    if allow_random and eligible:
        return discard_inventory_item(hero, random.choice(eligible))
    return None


def _resolve_defeat_losses(
    hero: dict,
    world_level: int,
    lose_gold: bool = True,
    allow_random_item: bool = False,
) -> tuple[int, dict | None]:
    lost_gold = min(
        int(hero.get("gold", 0) or 0),
        defeat_gold_loss(world_level) if lose_gold else 0,
    )
    hero["gold"] = max(0, int(hero.get("gold", 0) or 0) - lost_gold)
    return lost_gold, _resolve_defeat_item(hero, allow_random=allow_random_item)


def apply_wounds(
    hero: dict,
    amount: int,
    token=None,
    world_level: int | None = None,
    apply_full_defeat_penalties: bool = True,
) -> tuple[int, bool]:
    ensure_hero_state(hero)
    if dev_flag("no_wounds"):
        hero["wounds"] = 0
        hero["_unconscious_until_next_turn"] = False
        _recalculate_max_hp(hero)
        return 0, False

    previous = int(hero.get("wounds", 0) or 0)
    requested = max(0, int(amount or 0))
    hero["wounds"] = max(0, min(MAX_WOUNDS, previous + requested))
    added = hero["wounds"] - previous
    full_defeat = previous < MAX_WOUNDS <= hero["wounds"]
    _recalculate_max_hp(hero)

    token_ref = token or hero.get("_token_ref")
    if token_ref is not None and hero["wounds"] >= 3:
        token_ref.actions = min(int(getattr(token_ref, "actions", 0) or 0), turn_action_limit(hero))

    if full_defeat:
        hero["_unconscious_until_next_turn"] = True
        hero["hp"] = 0
        if token_ref is not None:
            token_ref.actions = 0
        if apply_full_defeat_penalties:
            level = current_world_level() if world_level is None else max(1, min(4, int(world_level)))
            lost_gold, lost_item = _resolve_defeat_losses(
                hero,
                level,
                lose_gold=True,
                allow_random_item=True,
            )
            hero["_last_full_defeat_losses"] = {
                "lost_gold": lost_gold,
                "lost_item": lost_item,
            }

    return added, full_defeat


def heal_wounds(hero: dict, amount: int | None = None) -> int:
    ensure_hero_state(hero)
    current = int(hero.get("wounds", 0) or 0)
    if current <= 0:
        return 0
    healed = current if amount is None else min(current, max(0, int(amount)))
    hero["wounds"] = current - healed
    if hero["wounds"] < MAX_WOUNDS:
        hero["_unconscious_until_next_turn"] = False
    _recalculate_max_hp(hero)
    return healed


def begin_hero_turn(hero: dict, token=None) -> dict:
    """Rozpatruje wybudzenie po 4. Ranie i ustawia pule Akcji wynikajaca z Ran."""
    ensure_hero_state(hero)
    woke_up = bool(hero.get("_unconscious_until_next_turn")) or int(hero.get("wounds", 0) or 0) >= MAX_WOUNDS
    if woke_up:
        hero["wounds"] = min(3, int(hero.get("wounds", 0) or 0))
        hero["_unconscious_until_next_turn"] = False
        _recalculate_max_hp(hero)
        hero["hp"] = min(int(hero.get("max_hp", BASE_MAX_HP) or BASE_MAX_HP), 1)

    actions = turn_action_limit(hero)
    token_ref = token or hero.get("_token_ref")
    if token_ref is not None:
        token_ref.actions = actions

    return {
        "woke_up": woke_up,
        "actions": actions,
        "wounds": int(hero.get("wounds", 0) or 0),
        "hp": int(hero.get("hp", 0) or 0),
    }


def defeat_hero(
    hero: dict,
    token=None,
    world_level: int = 1,
    lose_gold: bool = True,
) -> dict:
    ensure_hero_state(hero)
    lost_gold, lost_item = _resolve_defeat_losses(
        hero,
        world_level,
        lose_gold=lose_gold,
        allow_random_item=False,
    )
    wound_added, full_defeat = apply_wounds(
        hero,
        1,
        token=token,
        world_level=world_level,
        apply_full_defeat_penalties=False,
    )

    if token is not None:
        token.actions = 0

    if full_defeat:
        hero["hp"] = 0
        parts = ["Bohater otrzymuje 4. Rane i pozostaje nieprzytomny do poczatku swojej nastepnej tury."]
    else:
        hero["hp"] = min(int(hero.get("max_hp", BASE_MAX_HP) or BASE_MAX_HP), 1)
        parts = ["Bohater traci przytomnosc, otrzymuje 1 Rane i odzyskuje przytomnosc z 1 HP."]

    if lost_gold:
        parts.append(f"Traci {lost_gold} Zlota.")
    if lost_item:
        parts.append(f"Traci przedmiot z plecaka: {lost_item.get('name', 'Przedmiot')}.")
    parts.append("Pozostaje na aktualnym heksie, a jego tura sie konczy.")
    return {
        "lost_gold": lost_gold,
        "lost_item": lost_item,
        "wound_added": wound_added,
        "full_defeat": full_defeat,
        "returned_to_start": False,
        "message": " ".join(parts),
    }


def training_cost(current_value: int) -> int | None:
    return TRAINING_COSTS.get(int(current_value or 0))


def train_stat(hero: dict, token, stat: str, allowed_stats: Iterable[str]) -> tuple[bool, str]:
    ensure_hero_state(hero)
    if stat not in set(allowed_stats):
        return False, "Ta statystyka nie jest trenowana w tej lokacji."
    current = int(hero.get("stats", {}).get(stat, 0) or 0)
    if current >= MAX_STAT:
        return False, f"{stat} ma juz maksymalna wartosc {MAX_STAT}."
    cost = training_cost(current)
    if cost is None:
        return False, "Nieprawidlowa wartosc statystyki."
    if token is None or int(getattr(token, "actions", 0) or 0) < 1:
        return False, "Trening wymaga 1 akcji."
    if int(hero.get("gold", 0) or 0) < cost:
        return False, f"Trening {stat} kosztuje {cost} monet."
    token.actions = max(0, int(token.actions) - 1)
    hero["gold"] -= cost
    hero["stats"][stat] = current + 1
    return True, f"{stat} wzrasta z {current} do {current + 1}. Zaplacono {cost} monet i 1 akcje."


def _healing_discount(hero: dict) -> int:
    for helper in hero.get("helpers", []) or []:
        if isinstance(helper, dict) and "medyk" in str(helper.get("name", "")).lower():
            return 1
    return 0


def healing_cost_per_wound(hero: dict, world_level: int | None = None) -> int:
    ensure_hero_state(hero)
    level = current_world_level() if world_level is None else max(1, min(4, int(world_level)))
    base_cost = max(1, WOUND_HEALING_COSTS[level] - _healing_discount(hero))
    return healing_cost_with_world_event(base_cost)


def heal_at_location(
    hero: dict,
    token,
    amount: int | None = None,
    world_level: int | None = None,
) -> tuple[bool, str]:
    ensure_hero_state(hero)
    current = int(hero.get("wounds", 0) or 0)
    if current <= 0:
        return False, "Bohater nie ma Ran do wyleczenia."
    if token is None or int(getattr(token, "actions", 0) or 0) < 1:
        return False, "Leczenie wymaga 1 akcji."
    requested = current if amount is None else min(current, max(1, int(amount)))
    cost_per_wound = healing_cost_per_wound(hero, world_level=world_level)
    affordable = int(hero.get("gold", 0) or 0) // cost_per_wound
    healed = min(requested, affordable)
    if healed <= 0:
        return False, f"Leczenie jednej Rany kosztuje {cost_per_wound} monet."
    total_cost = healed * cost_per_wound
    token.actions = max(0, int(token.actions) - 1)
    hero["gold"] -= total_cost
    heal_wounds(hero, healed)
    return True, f"Wyleczono {healed} Ran za {total_cost} monet i 1 akcje."
