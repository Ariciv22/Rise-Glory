from __future__ import annotations

import copy
import math
import unicodedata
from typing import Any

from rg_engine.models import ItemDefinition

BACKPACK_LIMIT = 10
EQUIPMENT_SLOTS = (
    "weapon",
    "armor",
    "helmet",
    "boots",
    "gloves",
    "amulet",
    "ring_1",
    "ring_2",
)

_ITEM_REGISTRY: dict[str, dict[str, Any]] = {}
_ITEM_NAME_INDEX: dict[str, str] = {}


def normalize_name(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    return "".join(character for character in ascii_text if character.isalnum())


def _slug(value: Any) -> str:
    normalized = normalize_name(value)
    return normalized or "przedmiot"


def register_item(definition: ItemDefinition | dict[str, Any]) -> dict[str, Any]:
    if isinstance(definition, ItemDefinition):
        item = definition.to_dict()
    else:
        item = copy.deepcopy(definition)
    item_id = str(item.get("item_id") or item.get("id") or _slug(item.get("name")))
    item["id"] = item_id
    item.pop("item_id", None)
    item.setdefault("name", item_id)
    item.setdefault("category", "misc")
    item.setdefault("slot", None)
    item.setdefault("quality", "zwykla")
    item.setdefault("price", 0)
    item.setdefault("description", "")
    item.setdefault("hit_bonus", 0)
    item.setdefault("damage_bonus", 0)
    item.setdefault("armor_class", 0)
    item.setdefault("stat_bonus", {})
    item.setdefault("effects", {})
    _ITEM_REGISTRY[item_id] = item
    _ITEM_NAME_INDEX[normalize_name(item["name"])] = item_id
    return copy.deepcopy(item)


def registered_item(item_id_or_name: str) -> dict[str, Any] | None:
    key = str(item_id_or_name or "")
    item_id = key if key in _ITEM_REGISTRY else _ITEM_NAME_INDEX.get(normalize_name(key))
    if not item_id:
        return None
    return copy.deepcopy(_ITEM_REGISTRY[item_id])


def normalise_item(item: Any, category: str | None = None, **overrides: Any) -> dict[str, Any]:
    if isinstance(item, str):
        result = registered_item(item) or {
            "id": _slug(item),
            "name": item,
            "category": category or "misc",
            "slot": None,
            "quality": "zwykla",
            "price": 0,
            "description": "",
            "hit_bonus": 0,
            "damage_bonus": 0,
            "armor_class": 0,
            "stat_bonus": {},
            "effects": {},
        }
    elif isinstance(item, dict):
        lookup = registered_item(str(item.get("id") or item.get("name") or ""))
        result = lookup or {}
        result.update(copy.deepcopy(item))
        result.setdefault("id", _slug(result.get("name")))
        result.setdefault("name", result["id"])
        result.setdefault("category", category or "misc")
        result.setdefault("slot", None)
        result.setdefault("quality", "zwykla")
        result.setdefault("price", 0)
        result.setdefault("description", "")
        result.setdefault("hit_bonus", 0)
        result.setdefault("damage_bonus", 0)
        result.setdefault("armor_class", 0)
        result.setdefault("stat_bonus", {})
        result.setdefault("effects", {})
    else:
        raise TypeError("Przedmiot musi byc napisem albo slownikiem.")
    if category and result.get("category") in {None, "", "misc"}:
        result["category"] = category
    result.update(overrides)
    return result


def equipment_slot_for(item: dict[str, Any], equipment: dict[str, Any] | None = None) -> str | None:
    explicit = item.get("slot")
    if explicit in EQUIPMENT_SLOTS:
        return explicit
    category = str(item.get("category", ""))
    direct = {
        "weapon": "weapon",
        "armor": "armor",
        "helmet": "helmet",
        "boots": "boots",
        "gloves": "gloves",
        "amulet": "amulet",
    }
    if category in direct:
        return direct[category]
    if category == "ring":
        equipment = equipment or {}
        if not equipment.get("ring_1"):
            return "ring_1"
        if not equipment.get("ring_2"):
            return "ring_2"
        return "ring_1"
    return None


def _contains_item(hero: dict[str, Any], item_name: str) -> bool:
    target = normalize_name(item_name)
    equipment = hero.get("equipment") or {}
    for equipped in equipment.values():
        if equipped and normalize_name(normalise_item(equipped).get("name")) == target:
            return True
    for inventory_item in hero.get("inventory", []) or []:
        if normalize_name(normalise_item(inventory_item).get("name")) == target:
            return True
    return False


def ensure_equipment_state(hero: dict[str, Any]) -> dict[str, Any]:
    inventory = hero.setdefault("inventory", [])
    hero["inventory"] = [normalise_item(item) for item in inventory]
    equipment = hero.setdefault("equipment", {})
    for slot in EQUIPMENT_SLOTS:
        if equipment.get(slot):
            equipment[slot] = normalise_item(equipment[slot])
        else:
            equipment.setdefault(slot, None)

    if not hero.get("_equipment_migrated"):
        for source_key in ("basic_item", "class_item"):
            source_name = hero.get(source_key)
            if not source_name or _contains_item(hero, source_name):
                continue
            item = normalise_item(source_name)
            slot = equipment_slot_for(item, equipment)
            if slot and not equipment.get(slot):
                equipment[slot] = item
            else:
                inventory.append(item)
        hero["_equipment_migrated"] = True
    return hero


def backpack_size(hero: dict[str, Any]) -> int:
    ensure_equipment_state(hero)
    return len(hero.get("inventory", []))


def can_add_item(hero: dict[str, Any], amount: int = 1) -> bool:
    return backpack_size(hero) + max(0, int(amount)) <= int(hero.get("backpack_limit", BACKPACK_LIMIT))


def add_item(hero: dict[str, Any], item: Any, enforce_capacity: bool = True) -> tuple[bool, str]:
    ensure_equipment_state(hero)
    normalised = normalise_item(item)
    if enforce_capacity and not can_add_item(hero):
        hero.setdefault("overflow_items", []).append(normalised)
        return False, f"Plecak jest pelny. {normalised['name']} trafia do przedmiotow oczekujacych."
    hero["inventory"].append(normalised)
    return True, f"Dodano do plecaka: {normalised['name']}."


def equip_inventory_item(hero: dict[str, Any], inventory_index: int) -> tuple[bool, str]:
    ensure_equipment_state(hero)
    inventory = hero["inventory"]
    if inventory_index < 0 or inventory_index >= len(inventory):
        return False, "Nie znaleziono przedmiotu w plecaku."
    item = normalise_item(inventory[inventory_index])
    slot = equipment_slot_for(item, hero["equipment"])
    if not slot:
        return False, f"Przedmiotu {item['name']} nie mozna zalozyc."
    previous = hero["equipment"].get(slot)
    inventory.pop(inventory_index)
    hero["equipment"][slot] = item
    if previous:
        inventory.insert(inventory_index, normalise_item(previous))
        return True, f"Zalozono {item['name']}. {previous['name']} przeniesiono do plecaka."
    return True, f"Zalozono {item['name']}."


def unequip_slot(hero: dict[str, Any], slot: str) -> tuple[bool, str]:
    ensure_equipment_state(hero)
    if slot not in EQUIPMENT_SLOTS:
        return False, "Nieprawidlowy slot ekwipunku."
    item = hero["equipment"].get(slot)
    if not item:
        return False, "Ten slot jest pusty."
    if not can_add_item(hero):
        return False, "Brak miejsca w plecaku."
    hero["equipment"][slot] = None
    hero["inventory"].append(normalise_item(item))
    return True, f"Zdjeto {normalise_item(item)['name']}."


def weapon_bonuses(hero: dict[str, Any]) -> tuple[int, int]:
    ensure_equipment_state(hero)
    weapon = hero["equipment"].get("weapon")
    if not weapon:
        return 0, 0
    item = normalise_item(weapon)
    return int(item.get("hit_bonus", 0) or 0), int(item.get("damage_bonus", 0) or 0)


def armor_class(hero: dict[str, Any]) -> int:
    ensure_equipment_state(hero)
    armor = hero["equipment"].get("armor")
    if not armor:
        return 10
    value = int(normalise_item(armor).get("armor_class", 0) or 0)
    return value if value > 0 else 12


def equipment_stat_bonus(hero: dict[str, Any], stat: str) -> int:
    ensure_equipment_state(hero)
    total = 0
    for item in hero["equipment"].values():
        if not item:
            continue
        total += int(normalise_item(item).get("stat_bonus", {}).get(stat, 0) or 0)
    return total


def sell_value(item: Any) -> int:
    normalised = normalise_item(item)
    price = max(0, int(normalised.get("price", 0) or 0))
    return max(1, math.floor(price / 2)) if price else 1


def sell_inventory_item(hero: dict[str, Any], inventory_index: int) -> tuple[bool, str, int]:
    ensure_equipment_state(hero)
    inventory = hero["inventory"]
    if inventory_index < 0 or inventory_index >= len(inventory):
        return False, "Nie znaleziono przedmiotu w plecaku.", 0
    item = normalise_item(inventory.pop(inventory_index))
    value = sell_value(item)
    hero["gold"] = int(hero.get("gold", 0) or 0) + value
    return True, f"Sprzedano {item['name']} za {value} monet.", value


def item_display_name(item: Any) -> str:
    return str(normalise_item(item).get("name", "Przedmiot"))


def _register_defaults() -> None:
    definitions = [
        ItemDefinition("prosty_miecz", "Prosty miecz", "weapon", "weapon", price=6, description="Podstawowa bron bez dodatkowej premii."),
        ItemDefinition("krotki_miecz_kapitana", "Krótki miecz", "weapon", "weapon", price=6, description="+1 do trafienia i +1 do obrazen.", hit_bonus=1, damage_bonus=1),
        ItemDefinition("sztylet", "Sztylet", "weapon", "weapon", price=6, description="Lekka bron bez dodatkowej premii."),
        ItemDefinition("topor_wojenny", "Topor wojenny", "weapon", "weapon", price=6, description="Ciezka bron do walki wrecz."),
        ItemDefinition("wlocznia_straznika", "Wlocznia straznika", "weapon", "weapon", price=6, description="Bron o duzym zasiegu."),
        ItemDefinition("mlot_bojowy", "Mlot bojowy", "weapon", "weapon", price=6, description="Bron przeznaczona przeciw pancerzom."),
        ItemDefinition("krotki_luk", "Krotki luk", "weapon", "weapon", price=6, description="Lekka bron dystansowa."),
        ItemDefinition("skorzana_zbroja", "Skorzana zbroja", "armor", "armor", price=6, armor_class=12, description="Zwykla zbroja: 12 KP."),
        ItemDefinition("przeszywanica", "Przeszywanica", "armor", "armor", price=6, armor_class=12, description="Zwykla zbroja: 12 KP."),
        ItemDefinition("kolczuga", "Kolczuga", "armor", "armor", price=10, armor_class=14, quality="rzadka", description="Rzadka zbroja: 14 KP."),
        ItemDefinition("pancerz_straznika", "Pancerz straznika", "armor", "armor", price=6, armor_class=12, description="Zwykla zbroja: 12 KP."),
        ItemDefinition("skorzany_kaftan", "Skorzany kaftan", "armor", "armor", price=6, armor_class=12, description="Zwykla zbroja: 12 KP."),
        ItemDefinition("pierscien_kupca", "Pierscien kupiecki", "ring", price=6, stat_bonus={"Handel": 1}, description="+1 do Handlu po zalozeniu."),
        ItemDefinition("pierscien_uczonego", "Pierscien uczonego", "ring", price=6, stat_bonus={"Nauka": 1}, description="+1 do Nauki po zalozeniu."),
        ItemDefinition("pierscien_dyplomaty", "Pierscien dyplomaty", "ring", price=6, stat_bonus={"Dyplomacja": 1}, description="+1 do Dyplomacji po zalozeniu."),
        ItemDefinition("pierscien_intryganta", "Pierscien intryganta", "ring", price=6, stat_bonus={"Intryga": 1}, description="+1 do Intrygi po zalozeniu."),
        ItemDefinition("pierscien_opowiesci", "Pierscien opowiesci", "ring", price=6, stat_bonus={"Kultura": 1}, description="+1 do Kultury po zalozeniu."),
        ItemDefinition("sakwa_kupca", "Sakwa kupca", "misc", price=0, description="Przedmiot klasowy handlarza."),
        ItemDefinition("elegancki_stroj", "Elegancki stroj", "misc", price=0, description="Przedmiot klasowy dyplomaty."),
        ItemDefinition("ozdobny_stroj", "Ozdobny stroj", "misc", price=0, description="Przedmiot klasowy kulturowca."),
        ItemDefinition("torba_badacza", "Torba badacza", "misc", price=0, description="Przedmiot klasowy uczonego."),
        ItemDefinition("kaptur_intryganta", "Kaptur intryganta / pierscien sekretow", "misc", price=0, description="Przedmiot klasowy intryganta."),
        ItemDefinition("pieczec_rodu", "Pieczec rodu / glejt", "misc", price=0, description="Przedmiot klasowy dyplomaty."),
        ItemDefinition("instrument_kronika", "Instrument / kronika", "misc", price=0, description="Przedmiot klasowy kulturowca."),
        ItemDefinition("ksiega_mapa_ruin", "Ksiega / mapa ruin", "misc", price=0, description="Przedmiot klasowy uczonego."),
    ]
    for definition in definitions:
        register_item(definition)


_register_defaults()
