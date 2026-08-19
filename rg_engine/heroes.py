from __future__ import annotations

from typing import Iterable

from rg_engine.devtools import dev_flag
from rg_engine.items import discard_inventory_item, eligible_defeat_inventory_indices, ensure_equipment_state, normalise_item
from rg_engine.world import defeat_gold_loss
from rg_engine.world_events import healing_cost_with_world_event

MAX_WOUNDS = 4
BASE_MAX_HP = 10
MAX_STAT = 6
TRAINING_COSTS = {0: 5, 1: 8, 2: 11, 3: 14, 4: 17, 5: 20}


def _equipment_max_hp_bonus(hero: dict) -> int:
    total = 0
    for raw_item in (hero.get("equipment") or {}).values():
        if not raw_item:
            continue
        effects = normalise_item(raw_item).get("effects") or {}
        total += int(effects.get("max_hp_bonus", effects.get("max_hp", 0)) or 0)
    return total


def ensure_hero_state(hero: dict) -> dict:
    hero.setdefault("stats", {})
    hero["gold"] = int(hero.get("gold", 0) or 0)
    hero["legend"] = int(hero.get("legend", 0) or 0)
    hero["wounds"] = max(0, min(MAX_WOUNDS, int(hero.get("wounds", 0) or 0)))
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
    ensure_equipment_state(hero)

    if "base_max_hp" not in hero:
        hero["base_max_hp"] = max(1, int(hero.get("max_hp", BASE_MAX_HP) or BASE_MAX_HP))
    hero["max_hp"] = max(1, int(hero.get("base_max_hp", BASE_MAX_HP) or BASE_MAX_HP) + _equipment_max_hp_bonus(hero))
    if "hp" not in hero:
        hero["hp"] = hero["max_hp"]
    hero["hp"] = max(0, min(hero["max_hp"], int(hero.get("hp", hero["max_hp"]) or 0)))
    return hero


def helper_bonus(hero: dict, stat: str) -> int:
    ensure_hero_state(hero)
    return max(
        (
            int(helper.get("stat_bonus", {}).get(stat, 0) or 0)
            for helper in hero.get("helpers", [])
            if isinstance(helper, dict)
        ),
        default=0,
    )


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


def apply_wounds(hero: dict, amount: int) -> tuple[int, bool]:
    ensure_hero_state(hero)
    if dev_flag("no_wounds"):
        hero["wounds"] = 0
        return 0, False
    previous = int(hero.get("wounds", 0) or 0)
    hero["wounds"] = max(0, min(MAX_WOUNDS, previous + int(amount or 0)))
    return hero["wounds"] - previous, hero["wounds"] >= MAX_WOUNDS


def heal_wounds(hero: dict, amount: int | None = None) -> int:
    ensure_hero_state(hero)
    current = int(hero.get("wounds", 0) or 0)
    if current <= 0:
        return 0
    healed = current if amount is None else min(current, max(0, int(amount)))
    hero["wounds"] = current - healed
    return healed


def defeat_hero(
    hero: dict,
    token=None,
    world_level: int = 1,
    lose_gold: bool = True,
) -> dict:
    ensure_hero_state(hero)
    lost_gold = min(
        int(hero.get("gold", 0) or 0),
        defeat_gold_loss(world_level) if lose_gold else 0,
    )
    hero["gold"] = max(0, int(hero.get("gold", 0) or 0) - lost_gold)
    wound_added, _ = apply_wounds(hero, 1)
    hero["hp"] = min(int(hero.get("max_hp", BASE_MAX_HP) or BASE_MAX_HP), 1)
    if token is not None:
        token.actions = 0

    lost_item = None
    chosen_index = hero.pop("_combat_defeat_item_index", None)
    eligible = eligible_defeat_inventory_indices(hero)
    if chosen_index is not None and int(chosen_index) in eligible:
        lost_item = discard_inventory_item(hero, int(chosen_index))

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


def healing_cost_per_wound(hero: dict) -> int:
    ensure_hero_state(hero)
    base_cost = max(1, 2 - _healing_discount(hero))
    return healing_cost_with_world_event(base_cost)


def heal_at_location(hero: dict, token, amount: int | None = None) -> tuple[bool, str]:
    ensure_hero_state(hero)
    current = int(hero.get("wounds", 0) or 0)
    if current <= 0:
        return False, "Bohater nie ma Ran do wyleczenia."
    if token is None or int(getattr(token, "actions", 0) or 0) < 1:
        return False, "Leczenie wymaga 1 akcji."
    requested = current if amount is None else min(current, max(1, int(amount)))
    cost_per_wound = healing_cost_per_wound(hero)
    affordable = int(hero.get("gold", 0) or 0) // cost_per_wound
    healed = min(requested, affordable)
    if healed <= 0:
        return False, f"Leczenie jednej Rany kosztuje {cost_per_wound} monet."
    total_cost = healed * cost_per_wound
    token.actions = max(0, int(token.actions) - 1)
    hero["gold"] -= total_cost
    heal_wounds(hero, healed)
    return True, f"Wyleczono {healed} Ran za {total_cost} monet i 1 akcje."