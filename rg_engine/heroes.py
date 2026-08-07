from __future__ import annotations

from typing import Iterable

from rg_engine.items import ensure_equipment_state
from rg_engine.world import defeat_gold_loss
from rg_engine.world_events import healing_cost_with_world_event

MAX_WOUNDS = 4
MAX_STAT = 6
TRAINING_COSTS = {0: 5, 1: 8, 2: 11, 3: 14, 4: 17, 5: 20}


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
    hero.setdefault("status_effects", {})
    hero.setdefault("backpack_limit", 10)
    ensure_equipment_state(hero)
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


def apply_wounds(hero: dict, amount: int) -> tuple[int, bool]:
    ensure_hero_state(hero)
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
    hero["wounds"] = 0
    if token is not None and getattr(token, "start_tile", None) is not None:
        token.tile = token.start_tile
    return {
        "lost_gold": lost_gold,
        "returned_to_start": bool(token is not None and getattr(token, "start_tile", None) is not None),
        "message": (
            f"Bohater zostaje pokonany, wraca na pole startowe i traci {lost_gold} monet."
            if lost_gold
            else "Bohater zostaje pokonany i wraca na pole startowe."
        ),
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


def heal_at_location(hero: dict, token, amount: int | None = None) -> tuple[bool, str]:
    ensure_hero_state(hero)
    current = int(hero.get("wounds", 0) or 0)
    if current <= 0:
        return False, "Bohater nie ma Ran do wyleczenia."
    if token is None or int(getattr(token, "actions", 0) or 0) < 1:
        return False, "Leczenie wymaga 1 akcji."
    requested = current if amount is None else min(current, max(1, int(amount)))
    base_cost = max(1, 2 - _healing_discount(hero))
    cost_per_wound = healing_cost_with_world_event(base_cost)
    affordable = int(hero.get("gold", 0) or 0) // cost_per_wound
    healed = min(requested, affordable)
    if healed <= 0:
        return False, f"Leczenie jednej Rany kosztuje {cost_per_wound} monet."
    total_cost = healed * cost_per_wound
    token.actions = max(0, int(token.actions) - 1)
    hero["gold"] -= total_cost
    heal_wounds(hero, healed)
    return True, f"Wyleczono {healed} Ran za {total_cost} monet i 1 akcje."