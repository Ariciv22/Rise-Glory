from __future__ import annotations

from typing import Any

from rg_content.quests_final import QUESTS, register_all_quests
from rg_engine.quests import activate_quest, clear_quest_markers, return_quest_id_to_deck

register_all_quests()


def developer_quest_rows() -> list[dict[str, Any]]:
    """Zwraca stabilna liste finalnych Questow do menu programisty."""
    return [
        {
            "number": int(quest.get("quest_number", 0) or 0),
            "id": str(quest.get("id") or ""),
            "name": str(quest.get("name") or "Quest"),
            "board_location": str(quest.get("board_location") or ""),
        }
        for quest in sorted(QUESTS, key=lambda row: int(row.get("quest_number", 0) or 0))
    ]


def add_quest_for_testing(hero: dict[str, Any], quest_number: int) -> tuple[bool, str]:
    """Dodaje wskazany Quest bez losowania z Tablicy Ogloszen.

    Zachowujemy normalny limit 3 aktywnych Questow, bo interfejs i czesc zasad
    gry sa projektowane pod ten limit. Menu programisty ma osobny przycisk do
    szybkiego wyczyszczenia aktywnych Questow miedzy testami.
    """
    number = int(quest_number)
    definition = next(
        (quest for quest in QUESTS if int(quest.get("quest_number", 0) or 0) == number),
        None,
    )
    if definition is None:
        return False, f"Nie znaleziono Questa #{number}."

    active = hero.setdefault("active_quests", [])
    quest_id = str(definition.get("id") or "")
    if any(str(quest.get("id") or "") == quest_id for quest in active if isinstance(quest, dict)):
        return False, f"Quest #{number} jest juz aktywny."
    if len(active) >= 3:
        return False, "Masz juz 3 aktywne Questy. Uzyj 'Wyczysc aktywne' w menu programisty."

    runtime = activate_quest(quest_id)
    active.append(runtime)
    return True, f"Dodano Quest #{number}: {definition.get('name', 'Quest')}."


def clear_active_quests_for_testing(hero: dict[str, Any]) -> tuple[int, str]:
    """Usuwa aktywne Questy i ich znaczniki, aby szybko rozpoczec kolejny test."""
    active = list(hero.get("active_quests", []) or [])
    for quest in active:
        if not isinstance(quest, dict):
            continue
        clear_quest_markers(quest)
        quest_id = str(quest.get("id") or "")
        if quest_id:
            return_quest_id_to_deck(quest_id)
    hero["active_quests"] = []
    count = len(active)
    return count, f"Usunieto aktywne Questy: {count}."
