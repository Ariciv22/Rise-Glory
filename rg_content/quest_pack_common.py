"""Wspolne konstruktory danych dla finalnych Questow 1-23."""

from __future__ import annotations

import copy
from typing import Any

from rg_content.quest_runtime_ext import random_item_spec, random_material_spec


def fx(effect_type: str, **kwargs: Any) -> dict[str, Any]:
    return {"type": effect_type, **kwargs}


def O(
    option_id: str,
    label: str,
    *,
    option_type: str = "test",
    stat: str | None = None,
    threshold: int | None = None,
    on_success: str = "next",
    on_failure: str = "retry",
    text: str = "",
    requires: dict[str, Any] | None = None,
    consumes: dict[str, Any] | None = None,
    visible_if: dict[str, Any] | None = None,
    success_effects: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    failure_effects: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    action_cost: int = 1,
    enemy_id: str | None = None,
    combat_defeat: str = "quest_failure",
    combat_victory: str = "success",
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "option_id": option_id,
        "label": label,
        "type": option_type,
        "on_success": on_success,
        "on_failure": on_failure,
        "action_cost": int(action_cost),
        "text": text,
        "requires": copy.deepcopy(requires or {}),
        "consumes": copy.deepcopy(consumes or {}),
        "visible_if": copy.deepcopy(visible_if or {}),
        "success_effects": [copy.deepcopy(value) for value in success_effects],
        "failure_effects": [copy.deepcopy(value) for value in failure_effects],
        "combat_defeat": combat_defeat,
        "combat_victory": combat_victory,
    }
    if stat is not None:
        result["stat"] = stat
    if threshold is not None:
        result["threshold"] = int(threshold)
    if enemy_id:
        result["enemy_id"] = enemy_id
    return result


def S(
    number: int,
    title: str,
    text: str,
    *options: dict[str, Any],
    location: str | None = None,
    required_hex: str | None = None,
    point_of_no_return: bool = False,
) -> dict[str, Any]:
    return {
        "number": int(number),
        "title": title,
        "text": text,
        "options": [copy.deepcopy(option) for option in options],
        "required_location": location,
        "required_hex": required_hex,
        "point_of_no_return": bool(point_of_no_return),
    }


def R(
    gold: int,
    legend: int,
    *,
    random_items: list[dict[str, Any]] | None = None,
    random_materials: list[dict[str, Any]] | None = None,
    items: list[dict[str, Any] | str] | None = None,
    materials: dict[str, int] | None = None,
    food: dict[str, int] | list[str] | None = None,
    goods: dict[str, int] | list[str] | None = None,
    helpers: list[dict[str, Any]] | None = None,
    statuses: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "gold": int(gold),
        "legend": int(legend),
        "random_items": copy.deepcopy(random_items or []),
        "random_materials": copy.deepcopy(random_materials or []),
        "items": copy.deepcopy(items or []),
        "materials": copy.deepcopy(materials or {}),
        "food": copy.deepcopy(food or {}),
        "goods": copy.deepcopy(goods or {}),
        "helpers": copy.deepcopy(helpers or []),
        "statuses": copy.deepcopy(statuses or []),
    }


def Q(
    number: int,
    quest_id: str,
    name: str,
    *,
    board_location: str,
    issuer: str,
    board_text: str,
    description: str,
    objective: str,
    length: str,
    stages: list[dict[str, Any]],
    ending_rewards: dict[str, dict[str, Any]],
    reward_hint: str = "Zloto, ekwipunek i skutki fabularne zalezne od zakonczenia.",
    accept_text: str = "",
    time_limit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": quest_id,
        "name": name,
        "deck": "Questy",
        "description": description,
        "objective": objective,
        "required_location": board_location,
        "board_location": board_location,
        "issuer": issuer,
        "board_text": board_text,
        "accept_text": accept_text,
        "stages": copy.deepcopy(stages),
        "reward": {},
        "ending_rewards": copy.deepcopy(ending_rewards),
        "world_level_min": 1,
        "world_level": 1,
        "unique": True,
        "shared": False,
        "sellable": True,
        "tradeable": True,
        "abandonable": True,
        "quest_number": int(number),
        "length": length,
        "reward_hint": reward_hint,
        "time_limit": copy.deepcopy(time_limit or {}),
        "markers": [],
        "flags_on_complete": {},
    }


ri = random_item_spec
rm = random_material_spec

BRAN = {
    "id": "bran",
    "name": "Bran",
    "category": "companion",
    "effect_text": "+1 do dowolnego rzutu, maksymalnie 2 razy na runde Gracza.",
    "effects": {"any_roll_bonus": 1, "uses_per_player_round": 2},
}

LEKKOMYSLNY_ZNACHOR = {
    "id": "lekkomyslny_znachor",
    "name": "Lekkomyslny znachor",
    "category": "helper",
    "effect_text": "Leczenie kosztuje 2 Zlota mniej.",
    "effects": {"healing_gold_discount": 2},
}

TOPOR_KATA = {
    "id": "topor_kata",
    "name": "Topor kata",
    "category": "weapon",
    "quality": "zwykla",
    "hit_bonus": -1,
    "damage_bonus": 1,
    "description": "Ciezki topor otrzymany od Garrana.",
}

KROTKI_MIECZ = {
    "id": "krotki_miecz_questa",
    "name": "Krotki miecz",
    "category": "weapon",
    "quality": "zwykla",
    "hit_bonus": 0,
    "damage_bonus": 0,
    "description": "Lekka bron zdobyta podczas Questa.",
}

LAMPA_ALRENA = {
    "id": "lampa_alrena",
    "name": "Lampa Alrena",
    "category": "misc",
    "quality": "unikalna",
    "description": "Stabilny samopodtrzymujacy sie plomien Alrena. Zastosowania eksploracyjne rozwija osobny system.",
    "effects": {"alren_lamp": True},
}

KONTRAKT_DLUZNY = {
    "id": "kontrakt_dluzny",
    "name": "Kontrakt Dluzny",
    "category": "misc",
    "quality": "unikalna",
    "description": "Prawo do roszczenia przejetego od Olana. Moze zostac wykorzystane przez przyszla zawartosc handlowa.",
    "effects": {"debt_contract": True},
}

TROFEUM_BESTII = {
    "id": "trofeum_skalnego_drapieznika",
    "name": "Trofeum skalnego drapieznika",
    "category": "misc",
    "quality": "rzadka",
    "description": "Trofeum z doroslego skalnego drapieznika.",
}

MINIATUROWY_WEDROWNY_DOM = {
    "id": "miniaturowy_wedrowny_dom",
    "name": "Miniaturowy Wedrowny Dom",
    "category": "misc",
    "quality": "unikalna",
    "description": "Raz na runde Gracza pozwala natychmiast przeniesc sie do najblizszego Miejsca na mapie. Przy remisie wlasciciel wybiera cel.",
    "effects": {"teleport_nearest_place_once_per_round": True},
}

SWIADEK_DROGI = {
    "id": "swiadek_drogi",
    "name": "Swiadek Drogi",
    "description": "Rozpoznawany przez Ludzi Szarego Traktu. Moze odblokowywac przyszle dialogi, Miejsca i Questy.",
}
