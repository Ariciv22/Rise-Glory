"""Jednorazowy most importow po reorganizacji katalogow.

Stara petla aplikacji zostala przeniesiona bez zmian do ``rg_core.app``.
Ten bootstrap mapuje dawne nazwy modulow na ich nowe, uporzadkowane miejsca,
dzieki czemu reorganizacja nie zmienia zasad ani zachowania gry.
Nowy kod powinien importowac juz tylko docelowe pakiety.
"""

from __future__ import annotations

import importlib
import sys


MODULE_ALIASES = {
    "rg_data": "rg_core.data",
    "rg_setup": "rg_core.setup",
    "rg_quest_runtime": "rg_core.quest_runtime",
    "rg_turns": "rg_engine.turns",
    "rg_location_data": "rg_content.locations",
    "rg_map": "rg_world.map",
    "rg_adventure": "rg_world.adventure",
    "rg_city_screen": "rg_ui.city",
    "rg_combat": "rg_ui.combat",
    "rg_combat_image_fit": "rg_ui.combat_image_fit",
    "rg_council_background": "rg_ui.council",
    "rg_dev_menu": "rg_ui.dev_menu",
    "rg_dice_animation": "rg_ui.dice_animation",
    "rg_hud": "rg_ui.hud",
    "rg_intro": "rg_ui.intro",
    "rg_player_board": "rg_ui.player_board",
    "rg_premium_dice": "rg_ui.premium_dice",
    "rg_quest_ui": "rg_ui.quest",
    "rg_screens": "rg_ui.screens_bridge",
    "rg_start_intro": "rg_ui.start_intro",
    "rg_start_intro_base": "rg_ui.start_intro_base",
    "rg_title_flow": "rg_ui.title_flow",
    "rg_tooltip": "rg_ui.tooltip",
    "rg_satanic_forces": "rg_legacy.satanic_forces",
    "rg_satanic_combat": "rg_legacy.satanic_combat",
}


def install_legacy_module_aliases() -> None:
    for old_name, new_name in MODULE_ALIASES.items():
        if old_name in sys.modules:
            continue
        sys.modules[old_name] = importlib.import_module(new_name)
