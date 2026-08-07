"""Dane gry niezalezne od interfejsu."""

from rg_content.enemies import create_enemy, enemy_definition
from rg_content.quests import SATANIC_FORCES_ID, register_all_quests
from rg_content.world_events import WORLD_EVENTS, register_all_world_events

register_all_quests()
register_all_world_events()

__all__ = [
    "SATANIC_FORCES_ID",
    "WORLD_EVENTS",
    "create_enemy",
    "enemy_definition",
    "register_all_quests",
    "register_all_world_events",
]
