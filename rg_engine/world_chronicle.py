from __future__ import annotations

import copy
from typing import Any

_ENTRIES: list[dict[str, Any]] = []


def reset_world_chronicle() -> None:
    _ENTRIES.clear()


def add_threat_resolution(event: dict[str, Any], resolution: dict[str, Any]) -> dict[str, Any]:
    hero = str(resolution.get("hero") or "Bohater")
    method = str(resolution.get("method") or "nieznaną metodą")
    name = str(event.get("name") or "Zagrożenie")
    entry = {
        "type": "threat_resolved",
        "event_id": str(event.get("id") or ""),
        "name": name,
        "hero": hero,
        "method": method,
        "text": f"{name}: {hero} rozwiązał problem metodą „{method}”.",
    }
    _ENTRIES.append(entry)
    return copy.deepcopy(entry)


def add_quest_resolution(player: dict[str, Any], quest: dict[str, Any]) -> dict[str, Any]:
    """Dodaje krótki, fabularny wpis o rozstrzygnięciu Questa.

    Kronika zapisuje wynik historii, a nie techniczne rzuty. Konkretna końcówka
    zostaje zachowana, dzięki czemu późniejsze systemy mogą pokazać sensowną
    opowieść z przebiegu partii.
    """
    hero = str(player.get("name") or player.get("hero_name") or "Bohater")
    name = str(quest.get("name") or "Quest")
    status = str(quest.get("status") or "completed")
    ending = str(quest.get("ending_id") or "")

    token = player.get("_token_ref")
    tile = getattr(token, "tile", None)
    location = getattr(tile, "location", None)
    location_name = str(location.get("name") or "") if isinstance(location, dict) else ""

    if status == "completed":
        outcome = f"ukończył Quest „{name}”"
    elif status == "abandoned":
        outcome = f"porzucił Quest „{name}”"
    else:
        outcome = f"nie zdołał ukończyć Questa „{name}”"

    details = []
    if ending:
        details.append(f"zakończenie: {ending}")
    if location_name:
        details.append(f"miejsce: {location_name}")
    suffix = f" ({', '.join(details)})" if details else ""

    entry = {
        "type": "quest_resolved",
        "quest_id": str(quest.get("id") or ""),
        "quest_number": int(quest.get("quest_number", 0) or 0),
        "name": name,
        "hero": hero,
        "status": status,
        "ending": ending,
        "location": location_name,
        "text": f"{hero} {outcome}{suffix}.",
    }
    _ENTRIES.append(entry)
    return copy.deepcopy(entry)


def world_chronicle_entries() -> list[dict[str, Any]]:
    return copy.deepcopy(_ENTRIES)
