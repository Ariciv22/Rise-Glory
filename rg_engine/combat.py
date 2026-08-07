from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from rg_engine.heroes import MAX_WOUNDS, apply_wounds, ensure_hero_state, helper_bonus
from rg_engine.items import armor_class, weapon_bonuses


@dataclass
class CombatSession:
    player: dict[str, Any]
    enemy: dict[str, Any]
    round_number: int = 0
    last_log: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def prepare_enemy(enemy: dict[str, Any]) -> dict[str, Any]:
    prepared = dict(enemy)
    max_hp = max(1, int(prepared.get("max_hp", prepared.get("hp", 1)) or 1))
    prepared["max_hp"] = max_hp
    prepared["hp"] = max(0, min(max_hp, int(prepared.get("hp", max_hp) or max_hp)))
    prepared.setdefault("name", "Przeciwnik")
    prepared.setdefault("armor_class", 10)
    prepared.setdefault("attack_bonus", 0)
    prepared.setdefault("wounds", 1)
    prepared.setdefault("can_escape", True)
    prepared.setdefault("image", "")
    prepared.setdefault("escape", {})
    return prepared


def create_session(player: dict[str, Any], enemy: dict[str, Any], intro_text: str = "", metadata: dict | None = None) -> CombatSession:
    ensure_hero_state(player)
    prepared = prepare_enemy(enemy)
    return CombatSession(
        player=player,
        enemy=prepared,
        last_log=intro_text or f"Rozpoczyna sie walka z przeciwnikiem: {prepared['name']}.",
        metadata=dict(metadata or {}),
    )


def _hero_attack(session: CombatSession, rng) -> dict[str, Any]:
    player = session.player
    enemy = session.enemy
    hit_bonus, damage_bonus = weapon_bonuses(player)
    companion_bonus = helper_bonus(player, "Walka")
    roll = int(rng.randint(1, 20))
    total = roll + int(player.get("stats", {}).get("Walka", 0) or 0) + hit_bonus + companion_bonus
    if roll == 1:
        hits = 0
    elif roll == 20:
        hits = 2
    else:
        hits = 1 if total >= int(enemy.get("armor_class", 10) or 10) else 0
    damage_per_hit = max(1, 1 + damage_bonus)
    damage = hits * damage_per_hit
    enemy["hp"] = max(0, int(enemy.get("hp", 0) or 0) - damage)
    return {
        "roll": roll,
        "total": total,
        "hits": hits,
        "damage": damage,
        "hit_bonus": hit_bonus,
        "helper_bonus": companion_bonus,
    }


def _enemy_attack(session: CombatSession, rng) -> dict[str, Any]:
    player = session.player
    enemy = session.enemy
    roll = int(rng.randint(1, 20))
    total = roll + int(enemy.get("attack_bonus", 0) or 0)
    if roll == 1:
        hits = 0
    elif roll == 20:
        hits = 2
    else:
        hits = 1 if total >= armor_class(player) else 0
    wounds = hits * int(enemy.get("wounds", 1) or 1)
    actual_wounds, defeated = apply_wounds(player, wounds)
    return {
        "roll": roll,
        "total": total,
        "hits": hits,
        "wounds": actual_wounds,
        "defeated": defeated,
    }


def resolve_round(session: CombatSession, rng=None) -> dict[str, Any]:
    rng = rng or random
    if session.enemy.get("hp", 0) <= 0:
        return {"outcome": "victory", "log": session.last_log}
    if session.player.get("wounds", 0) >= MAX_WOUNDS:
        return {"outcome": "defeat", "log": session.last_log}

    session.round_number += 1
    hero = _hero_attack(session, rng)
    log = (
        f"Runda {session.round_number}: bohater rzuca {hero['roll']}, wynik {hero['total']}; "
        f"zadaje {hero['damage']} obrazen."
    )
    if session.enemy["hp"] <= 0:
        log += f" {session.enemy['name']} zostaje pokonany."
        session.last_log = log
        return {"outcome": "victory", "log": log, "hero_attack": hero}

    enemy = _enemy_attack(session, rng)
    log += (
        f" {session.enemy['name']} rzuca {enemy['roll']}, wynik {enemy['total']}; "
        f"zadaje {enemy['wounds']} Ran."
    )
    session.last_log = log
    return {
        "outcome": "defeat" if enemy["defeated"] else "ongoing",
        "log": log,
        "hero_attack": hero,
        "enemy_attack": enemy,
    }


def _failed_escape_enemy_attack(session: CombatSession, rng) -> dict[str, Any]:
    enemy = _enemy_attack(session, rng)
    log = (
        f"Ucieczka nieudana. {session.enemy['name']} rzuca {enemy['roll']}, "
        f"wynik {enemy['total']} i zadaje {enemy['wounds']} Ran."
    )
    session.last_log = log
    return {
        "outcome": "defeat" if enemy["defeated"] else "ongoing",
        "log": log,
        "enemy_attack": enemy,
    }


def attempt_escape(session: CombatSession, rng=None) -> dict[str, Any]:
    rng = rng or random
    enemy = session.enemy
    player = session.player
    if not enemy.get("can_escape", True):
        return {"outcome": "blocked", "log": "Ucieczka z tej walki jest niemozliwa."}

    escape = dict(enemy.get("escape") or {})
    bribe = int(escape.get("gold", 0) or 0)
    if bribe > 0 and int(player.get("gold", 0) or 0) >= bribe:
        player["gold"] -= bribe
        log = f"Bohater przekupuje przeciwnika za {bribe} monet i ucieka."
        session.last_log = log
        return {"outcome": "escaped", "log": log, "paid_gold": bribe}

    stat = escape.get("stat")
    threshold = escape.get("threshold")
    if stat and threshold is not None:
        roll = int(rng.randint(1, 20))
        bonus = int(player.get("stats", {}).get(stat, 0) or 0) + helper_bonus(player, str(stat))
        total = roll + bonus
        if roll == 20 or total >= int(threshold):
            log = f"Ucieczka udana: {roll} + {stat} {bonus} = {total} przeciw {threshold}."
            session.last_log = log
            return {"outcome": "escaped", "log": log, "roll": roll, "total": total}
        return _failed_escape_enemy_attack(session, rng)

    return {"outcome": "blocked", "log": "Karta przeciwnika nie okresla sposobu ucieczki."}
