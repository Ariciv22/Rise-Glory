"""Finalne Questy produkcyjne Rise & Glory.

Ten modul jest jedynym aktywnym rejestrem tresci Questow w grze.
Stare/testowe definicje pozostaja poza aktywna gra i nie sa tutaj importowane.
Questy 1-30 stanowia aktywna zawartosc produkcyjna.
"""

from __future__ import annotations

import copy

from rg_content.quest_runtime_ext import install

# Rozszerzenia musza zostac podpiete zanim inne moduly pobiora referencje
# do funkcji create_offer / draw_quest_id / activate_quest.
install()

from rg_content.quests_pack_01_08 import QUESTS_01_08
from rg_content.quests_pack_09_16 import QUESTS_09_16
from rg_content.quests_pack_17_23 import QUESTS_17_23
from rg_content.quests_pack_24_30 import QUESTS_24_30
from rg_engine.quests import register_quest, register_quest_expansion


QUESTS = QUESTS_01_08 + QUESTS_09_16 + QUESTS_17_23 + QUESTS_24_30
EXPANSIONS = ()

_REGISTERED = False


def register_all_quests() -> None:
    """Rejestruje wylacznie finalne Questy produkcyjne 1-30."""
    global _REGISTERED
    if _REGISTERED:
        return

    for quest in QUESTS:
        # board_location odpowiada za Tablice Ogloszen. required_location na
        # poziomie calego Questa pozostawiamy puste, bo dalsze etapy moga
        # prowadzic na trakt, do lasu albo do innej lokacji. Ograniczenie
        # miejsca jest zapisane bezposrednio na konkretnym etapie.
        definition = copy.deepcopy(quest)
        definition["required_location"] = ""
        register_quest(definition)

    for expansion in EXPANSIONS:
        register_quest_expansion(expansion)
    _REGISTERED = True
