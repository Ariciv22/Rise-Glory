"""Finalne Questy produkcyjne Rise & Glory.

Ten modul jest jedynym aktywnym rejestrem tresci Questow w grze.
Stare/testowe definicje pozostaja poza aktywna gra i nie sa tutaj importowane.
Kolejne Questy trafiaja tu dopiero po zatwierdzeniu w trello/QUESTY_FINAL.md.
"""

from __future__ import annotations

from rg_engine.quests import register_quest, register_quest_expansion


QUESTS = ()
EXPANSIONS = ()

_REGISTERED = False


def register_all_quests() -> None:
    """Rejestruje wyłącznie finalne Questy produkcyjne."""
    global _REGISTERED
    if _REGISTERED:
        return
    for quest in QUESTS:
        register_quest(quest)
    for expansion in EXPANSIONS:
        register_quest_expansion(expansion)
    _REGISTERED = True
