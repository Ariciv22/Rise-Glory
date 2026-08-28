"""Rozszerzenia runtime dla finalnych Questow Rise & Glory.

Warstwa jest ladowana przez rg_content.quests_final i rozszerza istniejacy,
przetestowany silnik bez duplikowania jego logiki. Obsluguje:
- nagrody zalezne od zakonczenia,
- losowy ekwipunek wg kategorii/jakosci,
- losowe materialy,
- nagrody w postaci Pomocnikow i statusow,
- issuer/accept_text na Tablicy Ogloszen,
- filtrowanie Questow po lokacji Tablicy,
- qXX_result jako jedyny trwaly wynik Questa,
- specjalny rabat Lekkomyslnego znachora.
"""

from __future__ import annotations

import copy
import random
import unicodedata
from typing import Any

import rg_engine.heroes as heroes
import rg_engine.quests as quests
from rg_engine.items import add_item, normalise_item

_INSTALLED = False
_ORIGINALS: dict[str, Any] = {}

COMMON_MATERIALS = (
    "Zelazo",
    "Drewno",
    "Skora",
    "Srebro",
    "Tkanina",
    "Klejnoty",
    "Kamien",
    "Proch",
)
RARE_MATERIALS = ("Srebro", "Klejnoty", "Mroczna Stal", "Proch")


def _norm(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(ch for ch in text.encode("ascii", "ignore").decode("ascii").lower() if ch.isalnum())


def _item(name: str, category: str, quality: str = "zwykla", **kwargs: Any) -> dict[str, Any]:
    result = {
        "name": name,
        "category": category,
        "quality": quality,
        "description": kwargs.pop("description", "Nagroda questowa z oficjalnego katalogu EQ."),
    }
    result.update(kwargs)
    return result


# Minimalny runtime'owy wycinek oficjalnego katalogu 280 kart EQ.
# Pelny katalog pozostaje osobnym zadaniem z trello/14_EKWIPUNEK_I_ARCHETYPY.md.
ITEM_POOLS: dict[tuple[str, str], tuple[dict[str, Any], ...]] = {
    ("weapon", "zwykla"): (
        _item("Prosty miecz", "weapon", hit_bonus=0, damage_bonus=0, stat_bonus={"Walka": 1}),
        _item("Sztylet cienia", "weapon", hit_bonus=1, damage_bonus=0, stat_bonus={"Intryga": 1}),
        _item("Topor rzeznika", "weapon", hit_bonus=-1, damage_bonus=1),
        _item("Kostur adepta", "weapon", hit_bonus=0, damage_bonus=0, stat_bonus={"Nauka": 1}),
        _item("Rapier posla", "weapon", hit_bonus=1, damage_bonus=0, stat_bonus={"Dyplomacja": 1}),
        _item("Ostrze piesniarza", "weapon", hit_bonus=0, damage_bonus=0, stat_bonus={"Kultura": 1}),
    ),
    ("weapon", "rzadka"): (
        _item("Krwawy topor", "weapon", "rzadka", hit_bonus=0, damage_bonus=1),
        _item("Miecz bastionu", "weapon", "rzadka", hit_bonus=1, damage_bonus=1, effects={"kp_bonus": 1}),
        _item("Igla nocy", "weapon", "rzadka", hit_bonus=2, damage_bonus=0),
        _item("Harpun bestiobojcy", "weapon", "rzadka", hit_bonus=1, damage_bonus=1),
        _item("Runiczne ostrze", "weapon", "rzadka", hit_bonus=1, damage_bonus=0, stat_bonus={"Nauka": 1}),
        _item("Rapier pojedynkowicza", "weapon", "rzadka", hit_bonus=2, damage_bonus=0, stat_bonus={"Walka": 1}),
    ),
    ("armor", "zwykla"): (
        _item("Przeszywanica wojownika", "armor", armor_class=12, stat_bonus={"Walka": 1}),
        _item("Kaftan intryganta", "armor", armor_class=12, stat_bonus={"Intryga": 1}),
        _item("Szata adepta", "armor", armor_class=12, stat_bonus={"Nauka": 1}),
        _item("Kamizela kupiecka", "armor", armor_class=12, stat_bonus={"Handel": 1}),
        _item("Surkot posla", "armor", armor_class=12, stat_bonus={"Dyplomacja": 1}),
        _item("Stroj kronikarza", "armor", armor_class=12, stat_bonus={"Kultura": 1}),
    ),
    ("armor", "rzadka"): (
        _item("Pancerz berserkera", "armor", "rzadka", armor_class=14),
        _item("Kolczuga gwardzisty", "armor", "rzadka", armor_class=14),
        _item("Pancerz nocnego szlaku", "armor", "rzadka", armor_class=14, stat_bonus={"Intryga": 1}),
        _item("Luskowa zbroja lowcy", "armor", "rzadka", armor_class=14),
        _item("Runiczna kolczuga", "armor", "rzadka", armor_class=14, stat_bonus={"Nauka": 1}),
        _item("Zbroja ambasadora", "armor", "rzadka", armor_class=14, stat_bonus={"Dyplomacja": 1, "Kultura": 1}),
    ),
    ("helmet", "zwykla"): (
        _item("Zelazny helm fechmistrza", "helmet", stat_bonus={"Walka": 1}),
        _item("Kaptur intryganta", "helmet", stat_bonus={"Intryga": 1}),
        _item("Czapka uczonego", "helmet", stat_bonus={"Nauka": 1}),
        _item("Kapelusz kupca", "helmet", stat_bonus={"Handel": 1}),
        _item("Opaska posla", "helmet", stat_bonus={"Dyplomacja": 1}),
        _item("Wieniec piesniarza", "helmet", stat_bonus={"Kultura": 1}),
    ),
    ("helmet", "rzadka"): (
        _item("Przylbica furii", "helmet", "rzadka"),
        _item("Helm gwardzisty", "helmet", "rzadka", effects={"kp_bonus": 1}),
        _item("Maska bez twarzy", "helmet", "rzadka", stat_bonus={"Intryga": 1, "Dyplomacja": 1}),
        _item("Diadem badacza", "helmet", "rzadka", stat_bonus={"Nauka": 2}),
        _item("Korona rachmistrza", "helmet", "rzadka", stat_bonus={"Handel": 1}),
        _item("Maska aktora", "helmet", "rzadka", stat_bonus={"Kultura": 1}),
    ),
    ("boots", "zwykla"): (
        _item("Buty wojownika", "boots", stat_bonus={"Walka": 1}),
        _item("Buty przemytnika", "boots", stat_bonus={"Intryga": 1}),
        _item("Sandaly badacza", "boots", stat_bonus={"Nauka": 1}),
        _item("Buty karawaniarza", "boots", stat_bonus={"Handel": 1}),
        _item("Buty posla", "boots", stat_bonus={"Dyplomacja": 1}),
        _item("Buty piesniarza", "boots", stat_bonus={"Kultura": 1}),
    ),
    ("amulet", "zwykla"): (
        _item("Kamien wojownika", "amulet", stat_bonus={"Walka": 1}),
        _item("Oko szpiega", "amulet", stat_bonus={"Intryga": 1}),
        _item("Znak medrca", "amulet", stat_bonus={"Nauka": 1}),
        _item("Moneta gildii", "amulet", stat_bonus={"Handel": 1}),
        _item("Pieczec posla", "amulet", stat_bonus={"Dyplomacja": 1}),
        _item("Medalion piesni", "amulet", stat_bonus={"Kultura": 1}),
    ),
    ("amulet", "rzadka"): (
        _item("Krwawy rubin", "amulet", "rzadka"),
        _item("Kamien Stalowego Serca", "amulet", "rzadka", effects={"kp_bonus": 1, "max_hp_bonus": 1}),
        _item("Oko Nocy", "amulet", "rzadka", stat_bonus={"Intryga": 1}),
        _item("Kamien pamieci", "amulet", "rzadka", stat_bonus={"Nauka": 1}),
        _item("Amulet szesciu monet", "amulet", "rzadka", stat_bonus={"Handel": 1}),
        _item("Pieczec dworu", "amulet", "rzadka", stat_bonus={"Dyplomacja": 1, "Kultura": 1}),
    ),
    ("ring", "zwykla"): (
        _item("Pierscien wojownika", "ring", stat_bonus={"Walka": 1}),
        _item("Pierscien intryganta", "ring", stat_bonus={"Intryga": 1}),
        _item("Pierscien uczonego", "ring", stat_bonus={"Nauka": 1}),
        _item("Pierscien kupiecki", "ring", stat_bonus={"Handel": 1}),
        _item("Pierscien dyplomaty", "ring", stat_bonus={"Dyplomacja": 1}),
        _item("Pierscien opowiesci", "ring", stat_bonus={"Kultura": 1}),
    ),
    ("ring", "rzadka"): (
        _item("Pierscien krwi", "ring", "rzadka"),
        _item("Pierscien tarczy", "ring", "rzadka", effects={"kp_bonus": 1}),
        _item("Pierscien szeptow", "ring", "rzadka", stat_bonus={"Intryga": 1}),
        _item("Pierscien run", "ring", "rzadka", stat_bonus={"Nauka": 1}),
        _item("Pierscien zlotego szlaku", "ring", "rzadka", stat_bonus={"Handel": 1}),
        _item("Pierscien ambasadora", "ring", "rzadka", stat_bonus={"Dyplomacja": 1, "Kultura": 1}),
    ),
}


def random_item_spec(category: str, quality: str = "zwykla", count: int = 1) -> dict[str, Any]:
    return {"category": category, "quality": quality, "count": int(count)}


def random_material_spec(count: int, rare: bool = False, distinct: bool = True) -> dict[str, Any]:
    return {
        "count": int(count),
        "pool": list(RARE_MATERIALS if rare else COMMON_MATERIALS),
        "distinct": bool(distinct),
    }


def _draw_equipment(spec: dict[str, Any]) -> list[dict[str, Any]]:
    category = str(spec.get("category") or "misc")
    quality = str(spec.get("quality") or "zwykla")
    count = max(0, int(spec.get("count", 1) or 1))
    pool = ITEM_POOLS.get((category, quality), ())
    if not pool:
        return [_item(f"Losowy {quality} {category}", category, quality) for _ in range(count)]
    return [copy.deepcopy(random.choice(pool)) for _ in range(count)]


def _draw_materials(spec: dict[str, Any]) -> dict[str, int]:
    count = max(0, int(spec.get("count", 0) or 0))
    pool = list(spec.get("pool") or COMMON_MATERIALS)
    if not pool or count <= 0:
        return {}
    if spec.get("distinct", True):
        chosen = random.sample(pool, k=min(count, len(pool)))
    else:
        chosen = [random.choice(pool) for _ in range(count)]
    result: dict[str, int] = {}
    for name in chosen:
        result[name] = result.get(name, 0) + 1
    return result


def _materialize_reward(reward: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    resolved = copy.deepcopy(reward or {})
    items = list(resolved.get("items") or [])
    for spec in resolved.pop("random_items", []) or []:
        items.extend(_draw_equipment(spec))
    resolved["items"] = items

    materials = dict(resolved.get("materials") or {})
    for spec in resolved.pop("random_materials", []) or []:
        for name, amount in _draw_materials(spec).items():
            materials[name] = int(materials.get(name, 0) or 0) + int(amount)
    resolved["materials"] = materials

    helpers_to_add = list(resolved.pop("helpers", []) or [])
    statuses_to_add = list(resolved.pop("statuses", []) or [])
    return resolved, helpers_to_add, statuses_to_add


def quest_created_places(players: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Wylicza Miejsca utworzone przez Questy bez duplikowania flag stanu swiata."""
    if players is None:
        try:
            from rg_engine.world import registered_players
            players = registered_players()
        except Exception:
            players = []
    mapping = {
        ("q05_result", "ogrod_odrodzony"): {"id": "stary_ogrod", "name": "Stary Ogrod", "source_quest": 5},
        ("q06_result", "lazaret"): {"id": "lazaret_lirion", "name": "Lazaret Lirion", "source_quest": 6},
        ("q08_result", "mewa_uratowana"): {"id": "srebrna_mewa", "name": "Srebrna Mewa", "source_quest": 8},
        ("q09_result", "trzy_kanaly"): {"id": "folwark_elarin", "name": "Folwark w Elarin", "source_quest": 9},
        ("q12_result", "pierwszy_stol"): {"id": "pierwszy_stol", "name": "Pierwszy Stol w gospodzie Pod Bialym Jeleniem", "source_quest": 12},
        ("q17_result", "czerwony_miod"): {"id": "pasieka_czerwonego_miodu", "name": "Pasieka Czerwonego Miodu", "source_quest": 17},
        ("q20_result", "dzien_dobrego_losu"): {"id": "jarmark_dobrego_losu", "name": "Jarmark Dobrego Losu w Valdren", "source_quest": 20},
        ("q23_result", "trasa_naprawiona"): {"id": "wedrowne_laboratorium_mervena", "name": "Wedrowne Laboratorium Mervena", "source_quest": 23, "mobile": True},
    }
    found: dict[str, dict[str, Any]] = {}
    for player in players or []:
        flags = player.get("story_flags", {}) or {}
        for (key, value), place in mapping.items():
            if flags.get(key) == value:
                found[place["id"]] = copy.deepcopy(place)
    return list(found.values())


def _extended_apply_effect(player: dict[str, Any], quest: dict[str, Any], effect: dict[str, Any]) -> str:
    effect_type = str(effect.get("type") or "")
    if effect_type == "goods":
        values = effect.get("values") or {}
        for name, amount in values.items():
            player.setdefault("goods", []).extend([str(name)] * max(0, int(amount)))
        return "Goods changed."
    if effect_type == "food":
        values = effect.get("values") or {}
        for name, amount in values.items():
            player.setdefault("food", []).extend([str(name)] * max(0, int(amount)))
        return "Food changed."
    if effect_type == "random_item":
        specs = effect.get("spec") or {}
        messages = []
        for item in _draw_equipment(specs):
            added, message = add_item(player, normalise_item(item), enforce_capacity=True)
            messages.append(message if added else f"{item.get('name')} trafia do przedmiotow oczekujacych.")
        return " ".join(messages)
    if effect_type == "wound":
        amount = max(0, int(effect.get("amount", 1) or 1))
        added, _full = heroes.apply_wounds(player, amount, token=player.get("_token_ref"))
        return f"Rany: +{added}."
    return _ORIGINALS["apply_effect"](player, quest, effect)


def _extended_complete_quest(
    player: dict[str, Any],
    quest: dict[str, Any],
    note: str = "",
    *,
    ending_id: str | None = None,
    reward_override: dict[str, Any] | None = None,
) -> str:
    definition = quests.quest_definition(str(quest.get("id"))) or {}
    resolved_ending = str(ending_id or quest.get("ending_id") or "")
    selected = reward_override
    if selected is None and resolved_ending:
        selected = copy.deepcopy((definition.get("ending_rewards") or {}).get(resolved_ending))
    if selected is None:
        selected = copy.deepcopy(definition.get("reward") or {})
    standard_reward, helpers_to_add, statuses_to_add = _materialize_reward(selected)
    message = _ORIGINALS["complete_quest"](
        player,
        quest,
        note,
        ending_id=resolved_ending or None,
        reward_override=standard_reward,
    )

    special_messages: list[str] = []
    for helper in helpers_to_add:
        player.setdefault("helpers", []).append(copy.deepcopy(helper))
        special_messages.append(f"Pomocnik: {helper.get('name', 'Pomocnik')}.")
    for status in statuses_to_add:
        status_id = str(status.get("id") or _norm(status.get("name")) or "status")
        player.setdefault("status_effects", {})[status_id] = copy.deepcopy(status)
        special_messages.append(f"Status: {status.get('name', status_id)}.")

    number = int(definition.get("quest_number", quest.get("quest_number", 0)) or 0)
    if number > 0 and resolved_ending:
        player.setdefault("story_flags", {})[f"q{number:02d}_result"] = resolved_ending

    if special_messages:
        message = " ".join([message, *special_messages]).strip()
        quest["last_result"] = message
    return message


def _extended_create_offer(quest_id: str) -> dict[str, Any]:
    offer = _ORIGINALS["create_offer"](quest_id)
    definition = quests.quest_definition(quest_id) or {}
    offer["issuer"] = definition.get("issuer", "")
    offer["accept_text"] = definition.get("accept_text", "")
    return offer


def _extended_activate_quest(quest_or_id: dict[str, Any] | str) -> dict[str, Any]:
    runtime = _ORIGINALS["activate_quest"](quest_or_id)
    definition = quests.quest_definition(str(runtime.get("id"))) or {}
    runtime["issuer"] = definition.get("issuer", "")
    runtime["accept_text"] = definition.get("accept_text", "")
    if runtime["accept_text"]:
        runtime["last_result"] = runtime["accept_text"]
    return runtime


def _extended_draw_quest_id(world_level: int, unavailable_ids=(), rng=None, location_name: str | None = None) -> str | None:
    if not location_name:
        return _ORIGINALS["draw_quest_id"](world_level, unavailable_ids=unavailable_ids, rng=rng)
    rng = rng or random
    level = max(1, min(4, int(world_level or 1)))
    blocked = {str(value) for value in unavailable_ids or ()}
    blocked.update(quests._active_quest_ids())
    blocked.update(quests._RESERVED_OFFERS)
    blocked.update(quests._unique_resolved_ids())
    target = _norm(location_name)
    candidates = []
    for quest_id in quests.quest_ids_for_world_level(level):
        if quest_id in blocked:
            continue
        definition = quests.quest_definition(quest_id) or {}
        board_location = definition.get("board_location") or definition.get("required_location")
        if _norm(board_location) == target:
            candidates.append(quest_id)
    if not candidates:
        return None
    quest_id = str(rng.choice(candidates))
    quests._RESERVED_OFFERS.add(quest_id)
    return quest_id


def _extended_healing_discount(hero: dict[str, Any]) -> int:
    discount = int(_ORIGINALS["healing_discount"](hero) or 0)
    for helper in hero.get("helpers", []) or []:
        if not isinstance(helper, dict):
            continue
        discount = max(discount, int((helper.get("effects") or {}).get("healing_gold_discount", 0) or 0))
    return discount


def _patch_accept_quest_card() -> None:
    import rg_engine.locations as locations

    original = locations.accept_quest_card
    if getattr(original, "_quest_final_extended", False):
        return

    def accept_quest_card(player: dict[str, Any], quest_card: dict[str, Any]):
        success, message = original(player, quest_card)
        if not success:
            return success, message
        quest_id = str(quest_card.get("id") or "")
        active = [q for q in player.get("active_quests", []) or [] if isinstance(q, dict) and str(q.get("id")) == quest_id]
        runtime = active[-1] if active else None
        accept_text = str((runtime or {}).get("accept_text") or "")
        if accept_text:
            message = f"{message} {accept_text}"
        return success, message

    accept_quest_card._quest_final_extended = True
    locations.accept_quest_card = accept_quest_card


def install() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _ORIGINALS.update(
        {
            "apply_effect": quests._apply_effect,
            "complete_quest": quests.complete_quest,
            "create_offer": quests.create_offer,
            "activate_quest": quests.activate_quest,
            "draw_quest_id": quests.draw_quest_id,
            "healing_discount": heroes._healing_discount,
        }
    )
    quests._apply_effect = _extended_apply_effect
    quests.complete_quest = _extended_complete_quest
    quests.create_offer = _extended_create_offer
    quests.activate_quest = _extended_activate_quest
    quests.draw_quest_id = _extended_draw_quest_id
    heroes._healing_discount = _extended_healing_discount
    _patch_accept_quest_card()
    _INSTALLED = True


# Narzedzia pod przyszle UI efektow specjalnych.
def bran_bonus_available(player: dict[str, Any], round_number: int) -> bool:
    bran = next((h for h in player.get("helpers", []) or [] if isinstance(h, dict) and h.get("id") == "bran"), None)
    if not bran:
        return False
    usage = player.setdefault("special_reward_usage", {}).setdefault("bran", {})
    if int(usage.get("round", -1)) != int(round_number):
        usage.clear()
        usage.update({"round": int(round_number), "uses": 0})
    return int(usage.get("uses", 0)) < 2


def use_bran_bonus(player: dict[str, Any], round_number: int) -> int:
    if not bran_bonus_available(player, round_number):
        return 0
    usage = player["special_reward_usage"]["bran"]
    usage["uses"] = int(usage.get("uses", 0)) + 1
    return 1


def miniature_house_available(player: dict[str, Any], round_number: int) -> bool:
    owns = any(
        _norm((item.get("name") if isinstance(item, dict) else item)) == _norm("Miniaturowy Wedrowny Dom")
        for item in player.get("inventory", []) or []
    )
    if not owns:
        return False
    usage = player.setdefault("special_reward_usage", {}).setdefault("miniaturowy_wedrowny_dom", {})
    return int(usage.get("round", -1)) != int(round_number)


def mark_miniature_house_used(player: dict[str, Any], round_number: int) -> None:
    player.setdefault("special_reward_usage", {})["miniaturowy_wedrowny_dom"] = {"round": int(round_number)}
