"""Dane gry niezalezne od interfejsu."""

from rg_content.enemies import create_enemy, enemy_definition
from rg_content.quests import SATANIC_FORCES_ID, register_all_quests
from rg_content.threats import (
    CHOROBA_DRZEW_ID,
    LAWINY_ID,
    ROZBOJNICY_ID,
    THREATS,
    ZAWALONE_PRZEJSCIA_ID,
    register_all_threats,
)
from rg_content.world_events import WORLD_EVENTS, register_all_world_events

register_all_quests()
register_all_world_events()
register_all_threats()

__all__ = [
    "SATANIC_FORCES_ID",
    "WORLD_EVENTS",
    "THREATS",
    "ROZBOJNICY_ID",
    "LAWINY_ID",
    "CHOROBA_DRZEW_ID",
    "ZAWALONE_PRZEJSCIA_ID",
    "create_enemy",
    "enemy_definition",
    "register_all_quests",
    "register_all_world_events",
    "register_all_threats",
]
