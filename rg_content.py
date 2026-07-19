from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from rg_models import HelperDefinition, HeroArchetype, ItemDefinition, QuestDefinition

CONTENT_DIR = Path(__file__).resolve().parent / "content"


class ContentError(RuntimeError):
    pass


def _load_json(filename: str) -> Any:
    path = CONTENT_DIR / filename
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ContentError(f"Brak pliku tresci: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContentError(f"Nieprawidlowy JSON w {path}: {exc}") from exc


def _require(data, required, source):
    missing = set(required).difference(data)
    if missing:
        raise ContentError(f"Brak pol {sorted(missing)} w {source}")


@lru_cache(maxsize=1)
def load_archetypes():
    result = []
    for index, item in enumerate(_load_json("archetypes.json")):
        _require(item, {"id", "name", "color", "stats", "basic_item", "class_item", "role"}, f"archetypes[{index}]")
        result.append(HeroArchetype(int(item["id"]), str(item["name"]), tuple(item["color"]), dict(item["stats"]), str(item["basic_item"]), str(item["class_item"]), str(item["role"])))
    return tuple(result)


@lru_cache(maxsize=1)
def load_item_pools():
    result = {}
    for category, entries in _load_json("items.json").items():
        result[category] = tuple(ItemDefinition(str(item["id"]), str(item["name"]), category, int(item["price"]), str(item["description"]), list(item.get("effects", []))) for item in entries)
    return result


@lru_cache(maxsize=1)
def load_shop_layouts():
    return {kind: tuple(layout) for kind, layout in _load_json("shop_layouts.json").items()}


@lru_cache(maxsize=1)
def load_helpers():
    return tuple(HelperDefinition(str(item["id"]), str(item["name"]), int(item["price"]), str(item["description"]), str(item.get("effect_text", "")), dict(item.get("stat_bonus", {}))) for item in _load_json("helpers.json"))


@lru_cache(maxsize=1)
def load_quests():
    return tuple(QuestDefinition(str(item["id"]), str(item["name"]), str(item["deck"]), str(item["description"]), int(item.get("level", 1)), list(item.get("stages", [])), dict(item.get("reward", {}))) for item in _load_json("quests.json"))
