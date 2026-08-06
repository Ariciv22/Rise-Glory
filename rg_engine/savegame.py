from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

SAVE_SCHEMA_VERSION = 1


def _serializable(value: Any):
    if callable(value):
        return None
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if str(key).startswith("_"):
                continue
            converted = _serializable(item)
            if converted is not None:
                result[str(key)] = converted
        return result
    if isinstance(value, (list, tuple, set)):
        return [converted for item in value if (converted := _serializable(item)) is not None]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def build_snapshot(
    current_map: str,
    players: list[dict],
    tiles: list[Any],
    tokens: list[Any],
    turn_manager=None,
    active_player_index: int = 0,
) -> dict[str, Any]:
    tile_rows = []
    for tile in tiles:
        tile_rows.append(
            {
                "id": int(getattr(tile, "id")),
                "q": int(getattr(tile, "q")),
                "r": int(getattr(tile, "r")),
                "x": float(getattr(tile, "x")),
                "y": float(getattr(tile, "y")),
                "terrain_key": str(getattr(tile, "terrain_key")),
                "location": _serializable(getattr(tile, "location", None)),
                "adventure": _serializable(getattr(tile, "adventure", None)),
            }
        )
    token_rows = []
    for index, token in enumerate(tokens):
        token_rows.append(
            {
                "player_index": index,
                "tile_id": int(getattr(getattr(token, "tile", None), "id", 0) or 0),
                "start_tile_id": int(getattr(getattr(token, "start_tile", None), "id", 0) or 0),
                "actions": int(getattr(token, "actions", 0) or 0),
            }
        )
    turn = {
        "turn_order": list(getattr(turn_manager, "turn_order", range(len(players)))) if turn_manager else list(range(len(players))),
        "position": int(getattr(turn_manager, "position", 0) or 0),
        "round_number": int(getattr(turn_manager, "round_number", 1) or 1),
        "council_cycle": int(getattr(turn_manager, "council_cycle", 1) or 1),
    }
    return {
        "schema_version": SAVE_SCHEMA_VERSION,
        "current_map": current_map,
        "players": _serializable(players),
        "tiles": tile_rows,
        "tokens": token_rows,
        "turn_manager": turn,
        "active_player_index": int(active_player_index),
    }


def save_snapshot(path: str | Path, snapshot: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def load_snapshot(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    if int(data.get("schema_version", 0) or 0) != SAVE_SCHEMA_VERSION:
        raise ValueError("Nieobslugiwana wersja zapisu gry.")
    return copy.deepcopy(data)
