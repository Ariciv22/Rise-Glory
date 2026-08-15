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


def world_chronicle_entries() -> list[dict[str, Any]]:
    return copy.deepcopy(_ENTRIES)
