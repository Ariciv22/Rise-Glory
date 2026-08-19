from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Any

from rg_engine.heroes import apply_damage, ensure_hero_state, heal_hp, helper_bonus, helper_combat_bonus
from rg_engine.items import (
    add_item, armor_class, combat_item_effects, combat_usable_inventory_indices,
    consume_inventory_item, equip_inventory_item, equipment_slot_for, normalise_item,
    weapon_bonuses, weapon_damage, weapon_effects,
)
from rg_engine.world import update_world_level


@dataclass
class CombatSession:
    player: dict[str, Any]
    enemy: dict[str, Any]
    round_number: int = 0
    last_log: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    hero_statuses: dict[str, dict[str, Any]] = field(default_factory=dict)
    enemy_statuses: dict[str, dict[str, Any]] = field(default_factory=dict)
    defense_bonus: int = 0


def prepare_enemy(enemy: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(enemy)
    maximum = max(1, int(result.get("max_hp", result.get("hp", 1)) or 1))
    result["max_hp"] = maximum
    result["hp"] = max(0, min(maximum, int(result.get("hp", maximum) or maximum)))
    result.setdefault("name", "Przeciwnik")
    result.setdefault("armor_class", 10)
    result.setdefault("attack_bonus", 0)
    result["damage"] = max(1, int(result.get("damage", result.get("wounds", 1)) or 1))
    result.setdefault("can_escape", True)
    result.setdefault("image", "")
    result.setdefault("escape", {})
    result.setdefault("rewards", {})
    result.setdefault("special", {})
    result.setdefault("boss_phases", [])
    result.setdefault("phase_index", 0)
    return result


def create_session(player: dict[str, Any], enemy: dict[str, Any], intro_text: str = "", metadata: dict | None = None) -> CombatSession:
    ensure_hero_state(player)
    enemy = prepare_enemy(enemy)
    return CombatSession(player, enemy, last_log=intro_text or f"Rozpoczyna sie walka z: {enemy['name']}.", metadata=dict(metadata or {}))


def clear_combat_statuses(session: CombatSession) -> None:
    session.hero_statuses.clear()
    session.enemy_statuses.clear()
    session.defense_bonus = 0


def _status(status: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(status or {})
    result["name"] = str(result.get("name") or result.get("id") or "efekt")
    result["duration"] = max(1, int(result.get("duration", 1) or 1))
    result["damage"] = max(0, int(result.get("damage", 0) or 0))
    result["skip_action"] = bool(result.get("skip_action", False) or result["name"].lower() in {"ogluszenie", "stun"})
    result["kp_modifier"] = int(result.get("kp_modifier", 0) or 0)
    return result


def _apply_status(store: dict[str, dict[str, Any]], status: dict[str, Any], applications: int = 1) -> None:
    incoming = _status(status)
    key = incoming["name"].lower()
    applications = max(1, int(applications or 1))
    if key not in store:
        incoming["duration"] *= applications
        store[key] = incoming
        return
    current = store[key]
    base = incoming["duration"]
    current["duration"] = max(int(current.get("duration", 0) or 0), base) + base * (applications - 1)
    current.update({k: incoming[k] for k in ("damage", "skip_action", "kp_modifier")})


def _tick_statuses(session: CombatSession, target: str) -> tuple[str, bool, bool]:
    store = session.hero_statuses if target == "hero" else session.enemy_statuses
    logs, skip, defeated = [], False, False
    for key, value in list(store.items()):
        damage = max(0, int(value.get("damage", 0) or 0))
        if damage:
            if target == "hero":
                actual, defeated = apply_damage(session.player, damage)
            else:
                before = int(session.enemy.get("hp", 0) or 0)
                session.enemy["hp"] = max(0, before - damage)
                actual, defeated = before - session.enemy["hp"], session.enemy["hp"] <= 0
            logs.append(f"{value.get('name', 'Efekt')} zadaje {actual} obrazen.")
        if value.get("skip_action"):
            skip = True
            logs.append(f"{value.get('name', 'Efekt')} odbiera dzialanie.")
        value["duration"] = int(value.get("duration", 1) or 1) - 1
        if value["duration"] <= 0:
            store.pop(key, None)
        if defeated:
            break
    return " ".join(logs), skip, defeated


def _kp_modifier(store: dict[str, dict[str, Any]]) -> int:
    return sum(int(value.get("kp_modifier", 0) or 0) for value in store.values())


def _hero_kp(session: CombatSession) -> int:
    return max(1, armor_class(session.player) + helper_combat_bonus(session.player, "kp") + session.defense_bonus + _kp_modifier(session.hero_statuses))


def _enemy_kp(session: CombatSession) -> int:
    return max(1, int(session.enemy.get("armor_class", 10) or 10) + _kp_modifier(session.enemy_statuses))


def _apply_boss_phase(session: CombatSession) -> str:
    phases = list(session.enemy.get("boss_phases") or [])
    index = int(session.enemy.get("phase_index", 0) or 0)
    changed = False
    while index < len(phases):
        phase = dict(phases[index] or {})
        hp, maximum = int(session.enemy.get("hp", 0) or 0), max(1, int(session.enemy.get("max_hp", 1) or 1))
        reached = hp <= int(phase["hp_lte"]) if phase.get("hp_lte") is not None else (
            hp * 100 <= maximum * float(phase.get("hp_percent_lte", phase.get("threshold_percent")))
            if phase.get("hp_percent_lte", phase.get("threshold_percent")) is not None else False
        )
        if not reached:
            break
        for key in ("armor_class", "attack_bonus", "damage", "special"):
            if key in phase:
                session.enemy[key] = copy.deepcopy(phase[key])
        index += 1
        session.enemy["phase_index"] = index
        changed = True
    return "Przeciwnik przechodzi do kolejnej fazy." if changed else ""


def _enemy_attack(session: CombatSession, rng, attack_bonus: int | None = None, damage: int | None = None) -> dict[str, Any]:
    roll = int(rng.randint(1, 20))
    bonus = int(session.enemy.get("attack_bonus", 0) or 0) if attack_bonus is None else int(attack_bonus)
    total = roll + bonus
    hits = 0 if roll == 1 else (2 if roll == 20 else int(total >= _hero_kp(session)))
    per_hit = max(1, int(session.enemy.get("damage", 1) or 1) if damage is None else int(damage))
    actual, defeated = apply_damage(session.player, hits * per_hit)
    session.defense_bonus = 0
    return {"roll": roll, "total": total, "hits": hits, "damage": actual, "defeated": defeated}


def _table_effect(table: Any, roll: int) -> dict[str, Any]:
    entries = table if isinstance(table, list) else []
    if isinstance(table, dict):
        entries = [{"range": key, "effect": value} for key, value in table.items()]
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if "range" in entry:
            text = str(entry["range"])
            if "-" in text:
                low, high = [int(v) for v in text.split("-", 1)]
            else:
                low = high = int(text)
        else:
            low = int(entry.get("min", entry.get("roll", roll)) or roll)
            high = int(entry.get("max", entry.get("roll", low)) or low)
        if low <= roll <= high:
            return copy.deepcopy(entry.get("effect") or entry)
    return {}


def _special_effect(session: CombatSession, effect: dict[str, Any], rng) -> dict[str, Any]:
    effect = dict(effect or {})
    logs = []
    if effect.get("attack"):
        attack = _enemy_attack(session, rng, int(session.enemy.get("attack_bonus", 0) or 0) + int(effect.get("attack_bonus", 0) or 0), max(1, int(effect.get("damage", session.enemy.get("damage", 1)) or 1)))
        logs.append(f"Specjalny atak {'trafia' if attack['hits'] else 'pudluje'} i zadaje {attack['damage']} obrazen.")
        return {"outcome": "defeat" if attack["defeated"] else "ongoing", "log": " ".join(logs), "enemy_attack": attack}
    damage = max(0, int(effect.get("damage", 0) or 0))
    if damage:
        actual, defeated = apply_damage(session.player, damage)
        logs.append(f"Specjalny efekt zadaje {actual} obrazen.")
        if defeated:
            return {"outcome": "defeat", "log": " ".join(logs)}
    if isinstance(effect.get("status"), dict):
        _apply_status(session.hero_statuses, effect["status"])
        logs.append(f"Bohater otrzymuje efekt {effect['status'].get('name', 'status')}.")
    if isinstance(effect.get("self_status"), dict):
        _apply_status(session.enemy_statuses, effect["self_status"])
    heal = max(0, int(effect.get("heal", 0) or 0))
    if heal:
        before = int(session.enemy.get("hp", 0) or 0)
        session.enemy["hp"] = min(int(session.enemy.get("max_hp", before) or before), before + heal)
        logs.append(f"Przeciwnik odzyskuje {session.enemy['hp'] - before} HP.")
    return {"outcome": "ongoing", "log": " ".join(logs) or "Specjalny efekt nie przynosi dodatkowego skutku."}


def _special_action(session: CombatSession, rng) -> dict[str, Any] | None:
    special = dict(session.enemy.get("special") or {})
    every = max(0, int(special.get("every", 0) or 0))
    if not every or session.round_number % every:
        return None
    sides = max(2, int(special.get("activation_die", 6) or 6))
    roll = int(rng.randint(1, sides))
    values, threshold = special.get("activation_values"), special.get("activation_threshold")
    active = roll in {int(v) for v in values} if values is not None else (roll >= int(threshold) if threshold is not None else False)
    if not active:
        return {"outcome": "ongoing", "log": f"Specjalna zdolnosc nie aktywuje sie (rzut {roll}).", "special_roll": roll}
    effect, result_roll = copy.deepcopy(special.get("effect") or {}), None
    if special.get("table"):
        result_roll = int(rng.randint(1, max(2, int(special.get("result_die", 6) or 6))))
        effect = _table_effect(special["table"], result_roll)
    result = _special_effect(session, effect, rng)
    prefix = f"Specjalna zdolnosc aktywuje sie (rzut {roll})."
    if result_roll is not None:
        prefix += f" Wynik efektu: {result_roll}."
    result["log"] = " ".join(v for v in (prefix, result.get("log", "")) if v)
    result["special_roll"], result["special_result_roll"] = roll, result_roll
    return result


def _enemy_action(session: CombatSession, rng) -> dict[str, Any]:
    status_log, skip, defeated = _tick_statuses(session, "enemy")
    logs = [status_log] if status_log else []
    if defeated or session.enemy.get("hp", 0) <= 0:
        logs.append(f"{session.enemy['name']} zostaje pokonany przez efekt statusu.")
        return {"outcome": "victory", "log": " ".join(logs)}
    phase = _apply_boss_phase(session)
    if phase:
        logs.append(phase)
    if skip:
        logs.append(f"{session.enemy['name']} traci swoje dzialanie.")
        return {"outcome": "ongoing", "log": " ".join(logs)}
    special = _special_action(session, rng)
    if special is not None:
        logs.append(special.get("log", ""))
        return {**special, "log": " ".join(v for v in logs if v)}
    attack = _enemy_attack(session, rng)
    logs.append(f"{session.enemy['name']} {'trafia i zadaje ' + str(attack['damage']) + ' obrazen HP' if attack['hits'] else 'pudluje'}.")
    if attack["defeated"]:
        logs.append("Bohater traci przytomnosc.")
    return {"outcome": "defeat" if attack["defeated"] else "ongoing", "log": " ".join(logs), "enemy_attack": attack}


def _begin_action(session: CombatSession, rng) -> dict[str, Any] | None:
    if session.enemy.get("hp", 0) <= 0:
        return {"outcome": "victory", "log": session.last_log}
    if session.player.get("hp", 0) <= 0:
        return {"outcome": "defeat", "log": session.last_log}
    session.round_number += 1
    status_log, skip, defeated = _tick_statuses(session, "hero")
    prefix = f"Runda {session.round_number}." + (" " + status_log if status_log else "")
    if defeated:
        session.last_log = prefix + " Bohater traci przytomnosc."
        return {"outcome": "defeat", "log": session.last_log}
    if skip:
        enemy = _enemy_action(session, rng)
        log = " ".join(v for v in (prefix, "Bohater traci swoje dzialanie.", enemy.get("log", "")) if v)
        session.last_log = log
        return {**enemy, "log": log}
    return None


def _weapon_effects_on_hit(session: CombatSession, hits: int) -> tuple[int, str]:
    if hits <= 0:
        return 0, ""
    effects, logs = weapon_effects(session.player), []
    extra = max(0, int(effects.get("bonus_damage", effects.get("on_hit_damage", 0)) or 0)) * hits
    if extra:
        before = int(session.enemy.get("hp", 0) or 0)
        session.enemy["hp"] = max(0, before - extra)
        extra = before - session.enemy["hp"]
        logs.append(f"Efekt broni zadaje dodatkowo {extra} obrazen.")
    statuses = effects.get("status") or effects.get("on_hit_status") or []
    if isinstance(statuses, dict):
        statuses = [statuses]
    for status in statuses:
        if isinstance(status, dict):
            _apply_status(session.enemy_statuses, status, applications=hits)
            logs.append(f"Bron naklada efekt {status.get('name', 'status')}.")
    return extra, " ".join(logs)


def _hero_attack(session: CombatSession, rng) -> dict[str, Any]:
    hit_bonus, _ = weapon_bonuses(session.player)
    helper_hit = helper_bonus(session.player, "Walka") + helper_combat_bonus(session.player, "hit")
    roll = int(rng.randint(1, 20))
    total = roll + int(session.player.get("stats", {}).get("Walka", 0) or 0) + hit_bonus + helper_hit
    hits = 0 if roll == 1 else (2 if roll == 20 else int(total >= _enemy_kp(session)))
    per_hit = max(1, weapon_damage(session.player) + helper_combat_bonus(session.player, "damage"))
    base_damage = hits * per_hit
    session.enemy["hp"] = max(0, int(session.enemy.get("hp", 0) or 0) - base_damage)
    extra, effect_log = _weapon_effects_on_hit(session, hits)
    return {"roll": roll, "total": total, "hits": hits, "damage": base_damage + extra, "weapon_damage": base_damage, "bonus_damage": extra, "hit_bonus": hit_bonus, "helper_bonus": helper_hit, "effect_log": effect_log}


def resolve_round(session: CombatSession, rng=None) -> dict[str, Any]:
    rng = rng or random
    early = _begin_action(session, rng)
    if early is not None:
        return early
    hero = _hero_attack(session, rng)
    log = f"Runda {session.round_number}: bohater rzuca {hero['roll']} i {'trafia' if hero['hits'] else 'pudluje'}; zadaje {hero['damage']} obrazen."
    if hero["effect_log"]:
        log += " " + hero["effect_log"]
    if session.enemy["hp"] <= 0:
        session.last_log = log + f" {session.enemy['name']} zostaje pokonany."
        return {"outcome": "victory", "log": session.last_log, "hero_attack": hero}
    phase = _apply_boss_phase(session)
    if phase:
        log += " " + phase
    enemy = _enemy_action(session, rng)
    session.last_log = " ".join(v for v in (log, enemy.get("log", "")) if v)
    return {"outcome": enemy["outcome"], "log": session.last_log, "hero_attack": hero, "enemy_attack": enemy.get("enemy_attack"), "special_roll": enemy.get("special_roll")}


def defend(session: CombatSession, rng=None) -> dict[str, Any]:
    rng = rng or random
    early = _begin_action(session, rng)
    if early is not None:
        return early
    session.defense_bonus = 2
    enemy = _enemy_action(session, rng)
    session.last_log = " ".join(v for v in (f"Runda {session.round_number}: bohater przyjmuje Obrone (+2 KP).", enemy.get("log", "")) if v)
    return {**enemy, "log": session.last_log, "defended": True}


def use_item(session: CombatSession, inventory_index: int, rng=None) -> dict[str, Any]:
    rng = rng or random
    if inventory_index not in combat_usable_inventory_indices(session.player):
        return {"outcome": "blocked", "log": "Tego przedmiotu nie mozna uzyc w walce."}
    item = normalise_item(session.player["inventory"][inventory_index])
    effects = combat_item_effects(session.player, inventory_index)
    early = _begin_action(session, rng)
    if early is not None:
        return early
    logs = [f"Runda {session.round_number}: bohater uzywa {item.get('name', 'przedmiotu')}."]
    if int(effects.get("heal_hp", 0) or 0) > 0:
        logs.append(f"Odnawia {heal_hp(session.player, int(effects['heal_hp']))} HP.")
    damage = max(0, int(effects.get("damage", 0) or 0))
    if damage:
        before = int(session.enemy.get("hp", 0) or 0)
        session.enemy["hp"] = max(0, before - damage)
        logs.append(f"Przedmiot trafia automatycznie i zadaje {before - session.enemy['hp']} obrazen.")
    statuses = effects.get("status") or []
    if isinstance(statuses, dict):
        statuses = [statuses]
    for status in statuses:
        if isinstance(status, dict):
            _apply_status(session.enemy_statuses, status)
    consumed = consume_inventory_item(session.player, inventory_index)
    if consumed:
        logs.append("Zuzyty przedmiot trafia na stos odrzuconych Przedmiotow.")
    if session.enemy["hp"] <= 0:
        logs.append(f"{session.enemy['name']} zostaje pokonany.")
        session.last_log = " ".join(logs)
        return {"outcome": "victory", "log": session.last_log, "item": consumed}
    enemy = _enemy_action(session, rng)
    logs.append(enemy.get("log", ""))
    session.last_log = " ".join(v for v in logs if v)
    return {**enemy, "log": session.last_log, "item": consumed}


def change_equipment(session: CombatSession, inventory_index: int, rng=None) -> dict[str, Any]:
    rng = rng or random
    inventory = session.player.get("inventory", []) or []
    if inventory_index < 0 or inventory_index >= len(inventory) or not equipment_slot_for(normalise_item(inventory[inventory_index]), session.player.get("equipment") or {}):
        return {"outcome": "blocked", "log": "Tego przedmiotu nie mozna zalozyc."}
    early = _begin_action(session, rng)
    if early is not None:
        return early
    ok, message = equip_inventory_item(session.player, inventory_index)
    if not ok:
        return {"outcome": "blocked", "log": message}
    enemy = _enemy_action(session, rng)
    session.last_log = " ".join(v for v in (f"Runda {session.round_number}: {message}", enemy.get("log", "")) if v)
    return {**enemy, "log": session.last_log, "equipment_changed": True}


def attempt_escape(session: CombatSession, rng=None) -> dict[str, Any]:
    rng = rng or random
    escape = dict(session.enemy.get("escape") or {})
    threshold = escape.get("threshold")
    if not session.enemy.get("can_escape", True) or threshold is None:
        return {"outcome": "blocked", "log": "Ucieczka z tej walki jest niemozliwa."}
    early = _begin_action(session, rng)
    if early is not None:
        return early
    stat = str(escape.get("stat") or "Intryga")
    roll = int(rng.randint(1, 20))
    bonus = int(session.player.get("stats", {}).get(stat, 0) or 0) + helper_bonus(session.player, stat)
    total = roll + bonus
    if roll == 20 or (roll != 1 and total >= int(threshold)):
        session.last_log = f"Ucieczka udana: rzut {roll} + {stat} {bonus} = {total}."
        return {"outcome": "escaped", "log": session.last_log, "roll": roll, "total": total}
    enemy = _enemy_action(session, rng)
    session.last_log = " ".join(v for v in (f"Ucieczka nieudana: rzut {roll} + {stat} {bonus} = {total}.", enemy.get("log", "")) if v)
    return {**enemy, "log": session.last_log, "roll": roll, "total": total}


def attempt_bribe(session: CombatSession, rng=None) -> dict[str, Any]:
    rng = rng or random
    cost = max(0, int((session.enemy.get("escape") or {}).get("gold", 0) or 0))
    if cost <= 0:
        return {"outcome": "blocked", "log": "Tego przeciwnika nie mozna przekupic."}
    if int(session.player.get("gold", 0) or 0) < cost:
        return {"outcome": "blocked", "log": f"Przekupstwo kosztuje {cost} Zlota."}
    early = _begin_action(session, rng)
    if early is not None:
        return early
    session.player["gold"] -= cost
    session.last_log = f"Bohater przekupuje przeciwnika za {cost} Zlota i opuszcza walke."
    return {"outcome": "escaped", "log": session.last_log, "paid_gold": cost}


def finalize_victory(session: CombatSession) -> dict[str, Any]:
    if isinstance(session.metadata.get("victory_summary"), dict):
        return copy.deepcopy(session.metadata["victory_summary"])
    player = ensure_hero_state(session.player)
    enemy_record = copy.deepcopy(session.enemy)
    enemy_record["hp"] = 0
    player.setdefault("defeated_enemies", []).append(enemy_record)
    rewards = copy.deepcopy(session.enemy.get("rewards") or session.enemy.get("loot") or {})
    summary = {"gold": max(0, int(rewards.get("gold", 0) or 0)), "legend": max(0, int(rewards.get("legend", 0) or 0)), "items": [], "goods": [], "food": [], "materials": {}, "enemy": session.enemy.get("name", "Przeciwnik")}
    player["gold"] += summary["gold"]
    player["legend"] += summary["legend"]
    items = list(rewards.get("items", []) or []) + ([rewards["item"]] if rewards.get("item") else [])
    for raw in items:
        item = normalise_item(raw)
        added, _ = add_item(player, item, enforce_capacity=True)
        summary["items"].append({"name": item.get("name", "Przedmiot"), "in_backpack": added})
    for key in ("goods", "food"):
        for value in rewards.get(key, []) or []:
            player.setdefault(key, []).append(value)
            summary[key].append(value)
    for name, amount in (rewards.get("materials") or {}).items():
        player.setdefault("materials", {})[name] = int(player["materials"].get(name, 0) or 0) + int(amount)
        summary["materials"][name] = int(amount)
    if summary["legend"]:
        update_world_level()
    clear_combat_statuses(session)
    summary["defeated_count"] = len(player.get("defeated_enemies", []))
    session.metadata["victory_summary"] = copy.deepcopy(summary)
    return summary