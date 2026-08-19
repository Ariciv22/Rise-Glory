from __future__ import annotations

import copy

from rg_engine.models import EnemyDefinition
from rg_engine.world import current_world_level, enemy_world_modifier

_ENEMIES: dict[str, dict] = {}


def register_enemy(definition: EnemyDefinition | dict) -> dict:
    enemy = definition.to_dict() if isinstance(definition, EnemyDefinition) else copy.deepcopy(definition)
    enemy_id = str(enemy.get("enemy_id") or enemy.get("id"))
    enemy["id"] = enemy_id
    enemy.pop("enemy_id", None)
    if "damage" not in enemy:
        enemy["damage"] = int(enemy.get("wounds", 1) or 1)
    elif int(enemy.get("damage", 1) or 1) == 1 and int(enemy.get("wounds", 1) or 1) != 1:
        enemy["damage"] = int(enemy.get("wounds", 1) or 1)
    enemy.setdefault("special", {})
    enemy.setdefault("boss_phases", [])
    enemy.setdefault("rewards", {})
    _ENEMIES[enemy_id] = enemy
    return copy.deepcopy(enemy)


def enemy_definition(enemy_id: str) -> dict | None:
    enemy = _ENEMIES.get(str(enemy_id))
    return copy.deepcopy(enemy) if enemy else None


def create_enemy(enemy_id: str, world_level: int | None = None) -> dict:
    definition = enemy_definition(enemy_id)
    if not definition:
        raise KeyError(f"Nieznany przeciwnik: {enemy_id}")
    level = int(world_level or current_world_level())
    base_hp = int(definition.get("base_hp", definition.get("hp", 1)) or 1)
    base_kp = int(definition.get("armor_class", 10) or 10)
    base_attack = int(definition.get("attack_bonus", 0) or 0)
    modifier = enemy_world_modifier(level) if definition.get("scale_with_world", True) else 0

    definition["world_level"] = level
    definition["base_armor_class"] = base_kp
    definition["base_attack_bonus"] = base_attack
    definition["max_hp"] = max(1, base_hp + modifier)
    definition["hp"] = definition["max_hp"]
    definition["armor_class"] = base_kp + modifier
    definition["attack_bonus"] = base_attack + modifier
    definition["damage"] = max(1, int(definition.get("damage", definition.get("wounds", 1)) or 1))
    definition.setdefault("special", {})
    definition.setdefault("boss_phases", [])
    definition.setdefault("rewards", {})
    return definition


def _register_defaults() -> None:
    register_enemy(
        EnemyDefinition(
            enemy_id="przeklety_zolnierz",
            name="Przeklety zolnierz",
            base_hp=4,
            armor_class=12,
            attack_bonus=1,
            damage=1,
            image="przeklety_rycerz",
            can_escape=False,
            scale_with_world=True,
        )
    )


_register_defaults()