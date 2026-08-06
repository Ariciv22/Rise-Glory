"""Dane gry niezalezne od interfejsu."""

from rg_content.enemies import create_enemy, enemy_definition
from rg_content.quests import SATANIC_FORCES_ID, register_all_quests

register_all_quests()

__all__ = ["SATANIC_FORCES_ID", "create_enemy", "enemy_definition", "register_all_quests"]
