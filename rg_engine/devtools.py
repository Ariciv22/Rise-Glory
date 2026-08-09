from __future__ import annotations

from typing import Any

from rg_engine.world import update_world_level

DEV_FLAGS = {
    "infinite_actions": False,
    "infinite_gold": False,
    "no_wounds": False,
    "council_every_round": False,
}


def reset_devtools() -> None:
    for key in DEV_FLAGS:
        DEV_FLAGS[key] = False


def dev_flag(name: str) -> bool:
    return bool(DEV_FLAGS.get(str(name), False))


def set_dev_flag(name: str, enabled: bool) -> bool:
    key = str(name)
    if key not in DEV_FLAGS:
        raise KeyError(f"Nieznana opcja programisty: {key}")
    DEV_FLAGS[key] = bool(enabled)
    return DEV_FLAGS[key]


def toggle_dev_flag(name: str) -> bool:
    return set_dev_flag(name, not dev_flag(name))


def change_legend(hero: dict[str, Any], amount: int) -> int:
    previous = int(hero.get("legend", 0) or 0)
    hero["legend"] = max(0, previous + int(amount or 0))
    if hero["legend"] != previous:
        update_world_level()
    return hero["legend"]


def set_legend(hero: dict[str, Any], value: int) -> int:
    previous = int(hero.get("legend", 0) or 0)
    hero["legend"] = max(0, int(value or 0))
    if hero["legend"] != previous:
        update_world_level()
    return hero["legend"]


def add_gold(hero: dict[str, Any], amount: int) -> int:
    hero["gold"] = max(0, int(hero.get("gold", 0) or 0) + int(amount or 0))
    return hero["gold"]


def heal_all(hero: dict[str, Any]) -> int:
    previous = max(0, int(hero.get("wounds", 0) or 0))
    hero["wounds"] = 0
    return previous


def refill_actions(token, maximum: int) -> int:
    if token is None:
        return 0
    token.actions = max(0, int(maximum or 0))
    return int(token.actions)


def apply_runtime_dev_flags(hero: dict[str, Any] | None, token, maximum_actions: int) -> None:
    if hero is None:
        return
    if dev_flag("infinite_actions") and token is not None:
        token.actions = max(0, int(maximum_actions or 0))
    if dev_flag("infinite_gold"):
        hero["gold"] = max(999, int(hero.get("gold", 0) or 0))
    if dev_flag("no_wounds"):
        hero["wounds"] = 0
