from __future__ import annotations

import copy

from rg_engine.models import EnemyDefinition
from rg_engine.world import current_world_level, scaled_enemy_hp

_ENEMIES: dict[str, dict] = {}


def register_enemy(definition: EnemyDefinition | dict) -> dict:
    enemy = definition.to_dict() if isinstance(definition, EnemyDefinition) else copy.deepcopy(definition)
    enemy_id = str(enemy.get("enemy_id") or enemy.get("id"))
    enemy["id"] = enemy_id
    enemy.pop("enemy_id", None)
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
    max_hp = (
        scaled_enemy_hp(base_hp, level, bool(definition.get("legendary", False)))
        if definition.get("scale_with_world", True)
        else base_hp
    )
    definition["world_level"] = level
    definition["max_hp"] = max_hp
    definition["hp"] = max_hp
    return definition


def _register_defaults() -> None:
    register_enemy(
        EnemyDefinition(
            enemy_id="przeklety_zolnierz",
            name="Przeklęty żołnierz",
            base_hp=4,
            armor_class=12,
            attack_bonus=1,
            wounds=1,
            image="przeklety_rycerz",
            can_escape=False,
            scale_with_world=True,
        )
    )


_register_defaults()
