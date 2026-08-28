from __future__ import annotations

import math
import random
from typing import Any, Iterable


MATERIALS = (
    "Żelazo",
    "Drewno",
    "Skóra",
    "Srebro",
    "Tkanina",
    "Klejnoty",
    "Kamień",
    "Mroczna Stal",
    "Proch",
    "Odłamek Upadku",
)

# Odłamek Upadku nie jest częścią zwykłego losowania mapy na Poziomie Świata 1.
# Jego pojawianie się wraz z Upadkiem świata będzie podpinane osobnym systemem.
TERRAIN_MATERIALS = {
    "mountain": ("Żelazo", "Srebro", "Kamień", "Klejnoty", "Mroczna Stal"),
    "hills": ("Kamień", "Żelazo", "Srebro"),
    "forest": ("Drewno", "Skóra"),
    "plains": ("Skóra", "Tkanina", "Drewno"),
    "tundra": ("Skóra", "Drewno", "Kamień", "Mroczna Stal"),
    "desert": ("Kamień", "Klejnoty", "Proch"),
}

POTENTIALS = {
    "Brak": {"die": 0, "share": 0.05},
    "Słaby": {"die": 4, "share": 0.55},
    "Średni": {"die": 6, "share": 0.30},
    "Mocny": {"die": 8, "share": 0.10},
}

# Wartości ALFA - celowo w jednym miejscu, aby późniejszy balans nie wymagał
# przebudowy systemu.
READY_SITE_PRICES = {"Słaby": 12, "Średni": 18, "Mocny": 28}
RIGHT_PRICES = {"Słaby": 4, "Średni": 7, "Mocny": 10}
BUILD_COSTS = {
    "Słaby": {
        "gold": 4,
        "actions": 2,
        "materials": {"Drewno": 2, "Kamień": 2, "Żelazo": 1},
    },
    "Średni": {
        "gold": 6,
        "actions": 3,
        "materials": {"Drewno": 3, "Kamień": 3, "Żelazo": 2},
    },
    "Mocny": {
        "gold": 8,
        "actions": 4,
        "materials": {"Drewno": 4, "Kamień": 4, "Żelazo": 3},
    },
}
TAKEOVER_ACTION_COST = 2

FACILITY_NAMES = {
    "Żelazo": "Kopalnia żelaza",
    "Drewno": "Tartak",
    "Skóra": "Łowisko",
    "Srebro": "Kopalnia srebra",
    "Tkanina": "Warsztat tkacki",
    "Klejnoty": "Kopalnia klejnotów",
    "Kamień": "Kamieniołom",
    "Mroczna Stal": "Kopalnia Mrocznej Stali",
    "Proch": "Prochownia",
    "Odłamek Upadku": "Ekstraktor Upadku",
}

_WORLD_TILES: dict[int, Any] = {}


def register_world_tiles(tiles: Iterable[Any]) -> None:
    global _WORLD_TILES
    _WORLD_TILES = {int(tile.id): tile for tile in tiles}


def clear_world_tiles() -> None:
    global _WORLD_TILES
    _WORLD_TILES = {}


def world_tile(tile_id: int | str | None):
    try:
        return _WORLD_TILES.get(int(tile_id))
    except (TypeError, ValueError):
        return None


def facility_name(material: str | None) -> str:
    return FACILITY_NAMES.get(str(material), "Zakład produkcyjny")


def _potential_counts(tile_count: int) -> dict[str, int]:
    tile_count = max(0, int(tile_count))
    if not tile_count:
        return {name: 0 for name in POTENTIALS}

    none_count = max(0, int(round(tile_count * POTENTIALS["Brak"]["share"])))
    medium_count = max(0, int(round(tile_count * POTENTIALS["Średni"]["share"])))
    strong_count = max(0, int(round(tile_count * POTENTIALS["Mocny"]["share"])))
    weak_count = max(0, tile_count - none_count - medium_count - strong_count)
    return {
        "Brak": none_count,
        "Słaby": weak_count,
        "Średni": medium_count,
        "Mocny": strong_count,
    }


def assign_tile_potentials(tiles: list[Any], rng=None) -> list[Any]:
    """Nadaje całej mapie dokładny rozkład 5/55/30/10 potencjałów."""
    rng = rng or random
    counts = _potential_counts(len(tiles))
    levels: list[str] = []
    for level in ("Brak", "Słaby", "Średni", "Mocny"):
        levels.extend([level] * counts[level])
    rng.shuffle(levels)

    for tile, level in zip(tiles, levels):
        material = None
        die = int(POTENTIALS[level]["die"])
        if level != "Brak":
            pool = TERRAIN_MATERIALS.get(str(tile.terrain_key), ())
            material = rng.choice(pool) if pool else None
            if material is None:
                level = "Brak"
                die = 0
        tile.resource_potential = {
            "level": level,
            "die": die,
            "material": material,
        }
        tile.production_site = None
        tile.extraction_right_owner = None
        tile.extraction_right_owner_name = None
        tile.jurisdiction_name = None
        tile.jurisdiction_kind = None
        tile.jurisdiction_number = None
        tile.jurisdiction_tile_id = None
    return tiles


def potential(tile) -> dict[str, Any]:
    value = getattr(tile, "resource_potential", None)
    if isinstance(value, dict):
        return value
    return {"level": "Brak", "die": 0, "material": None}


def potential_summary(tile) -> str:
    value = potential(tile)
    if not value.get("material") or not int(value.get("die", 0) or 0):
        return "Brak"
    return f"{value['material']} / {value['level']} (k{value['die']})"


def _distance(a, b) -> float:
    return math.hypot(float(a.x) - float(b.x), float(a.y) - float(b.y))


def assign_jurisdictions(tiles: list[Any]) -> bool:
    location_tiles = [tile for tile in tiles if getattr(tile, "location", None)]
    if not location_tiles:
        return False

    for location_tile in location_tiles:
        location_tile.location["jurisdiction_tile_ids"] = []
        location_tile.location["production_site_ids"] = []
        location_tile.location["location_tile_id"] = int(location_tile.id)

    for tile in tiles:
        location_tile = min(
            location_tiles,
            key=lambda candidate: (_distance(tile, candidate), int(candidate.id)),
        )
        location = location_tile.location
        tile.jurisdiction_name = str(location.get("name") or "Lokacja")
        tile.jurisdiction_kind = str(location.get("kind") or "")
        tile.jurisdiction_number = int(location.get("number", 0) or 0)
        tile.jurisdiction_tile_id = int(location_tile.id)
        location["jurisdiction_tile_ids"].append(int(tile.id))
    return True


def _site_choices_for_location(location_tile, candidates: list[Any], rng) -> list[tuple[Any, str]] | None:
    """Dobiera 3 najbliższe heksy, którym da się przypisać 3 różne materiały."""
    ordered = sorted(candidates, key=lambda tile: (_distance(tile, location_tile), int(tile.id)))

    def visit(start: int, chosen: list[tuple[Any, str]], used: set[str]):
        if len(chosen) >= 3:
            return list(chosen)
        if len(ordered) - start < 3 - len(chosen):
            return None

        for index in range(start, len(ordered)):
            tile = ordered[index]
            pool = list(TERRAIN_MATERIALS.get(str(tile.terrain_key), ()))
            if not pool:
                continue
            current = potential(tile).get("material")
            if current in pool:
                pool.remove(current)
                pool.insert(0, current)
            if len(pool) > 1:
                tail = pool[1:]
                rng.shuffle(tail)
                pool = [pool[0], *tail]
            for material in pool:
                if material in used:
                    continue
                result = visit(
                    index + 1,
                    [*chosen, (tile, material)],
                    {*used, material},
                )
                if result is not None:
                    return result
        return None

    return visit(0, [], set())


def create_site(
    tile,
    *,
    owner_type: str,
    owner_name: str,
    owner_player_number: int | None = None,
    status: str = "active",
) -> dict[str, Any]:
    value = potential(tile)
    material = value.get("material")
    level = value.get("level", "Brak")
    die = int(value.get("die", 0) or 0)
    site = {
        "id": f"zaklad-{int(tile.id)}",
        "tile_id": int(tile.id),
        "name": facility_name(material),
        "material": material,
        "potential_level": level,
        "die": die,
        "status": status,
        "owner_type": owner_type,
        "owner_name": str(owner_name),
        "owner_player_number": owner_player_number,
        "jurisdiction_name": getattr(tile, "jurisdiction_name", None),
        "purchase_price": int(READY_SITE_PRICES.get(level, 0)),
        "last_production_council": None,
        "last_production_roll": None,
    }
    tile.production_site = site
    return site


def seed_location_sites(tiles: list[Any], rng=None) -> bool:
    """Każda lokacja dostaje dokładnie 3 różne gotowe zakłady na osobnych heksach."""
    rng = rng or random
    register_world_tiles(tiles)
    location_tiles = [tile for tile in tiles if getattr(tile, "location", None)]

    for location_tile in location_tiles:
        location = location_tile.location
        candidate_ids = set(int(value) for value in location.get("jurisdiction_tile_ids", []))
        candidates = [
            tile
            for tile in tiles
            if int(tile.id) in candidate_ids
            and tile is not location_tile
            and not getattr(tile, "location", None)
            and getattr(tile, "production_site", None) is None
            and potential(tile).get("material")
        ]
        choices = _site_choices_for_location(location_tile, candidates, rng)
        if choices is None:
            return False

        site_ids = []
        for tile, material in choices:
            tile.resource_potential["material"] = material
            site = create_site(
                tile,
                owner_type="location",
                owner_name=location.get("name", "Lokacja"),
                status="active",
            )
            site_ids.append(site["id"])
        location["production_site_ids"] = site_ids
    return True


def location_sites(location: dict) -> list[dict[str, Any]]:
    result = []
    wanted = set(str(value) for value in location.get("production_site_ids", []))
    for tile in _WORLD_TILES.values():
        site = getattr(tile, "production_site", None)
        if site and str(site.get("id")) in wanted:
            result.append(site)
    return sorted(result, key=lambda site: int(site.get("tile_id", 0) or 0))


def available_right_tiles(location: dict) -> list[Any]:
    result = []
    for tile_id in location.get("jurisdiction_tile_ids", []):
        tile = world_tile(tile_id)
        if tile is None or getattr(tile, "location", None):
            continue
        if getattr(tile, "production_site", None) is not None:
            continue
        if not potential(tile).get("material"):
            continue
        result.append(tile)
    return sorted(
        result,
        key=lambda tile: (
            {"Mocny": 0, "Średni": 1, "Słaby": 2}.get(potential(tile).get("level"), 3),
            int(tile.id),
        ),
    )


def _player_number(hero: dict) -> int:
    return int(hero.get("player_number", 0) or 0)


def _is_merchant(hero: dict) -> bool:
    return int(hero.get("archetype_id", 0) or 0) == 2 or str(hero.get("archetype_name", "")).lower() == "handlarz"


def ensure_production_state(hero: dict) -> dict:
    hero.setdefault("materials", {})
    hero.setdefault("production_sites", [])
    hero.setdefault("extraction_rights", [])
    hero.setdefault("production_history", [])
    return hero


def _append_owned_site(hero: dict, site: dict) -> None:
    ensure_production_state(hero)
    if not any(str(value.get("id")) == str(site.get("id")) for value in hero["production_sites"] if isinstance(value, dict)):
        hero["production_sites"].append(site)


def owned_sites(hero: dict) -> list[dict[str, Any]]:
    ensure_production_state(hero)
    number = _player_number(hero)
    result = []
    seen = set()
    for site in hero.get("production_sites", []):
        if not isinstance(site, dict):
            continue
        if site.get("owner_type") != "player" or int(site.get("owner_player_number", 0) or 0) != number:
            continue
        site_id = str(site.get("id"))
        if site_id in seen:
            continue
        seen.add(site_id)
        result.append(site)
    return result


def buy_location_site(location: dict, hero: dict, site_id: str) -> tuple[bool, str]:
    ensure_production_state(hero)
    site = next((value for value in location_sites(location) if str(value.get("id")) == str(site_id)), None)
    if site is None:
        return False, "Nie znaleziono zakładu należącego do tej lokacji."
    if site.get("owner_type") != "location":
        return False, "Ten zakład nie należy już do lokacji."
    if str(site.get("owner_name")) != str(location.get("name")):
        return False, "Ten zakład podlega innej lokacji."

    price = int(site.get("purchase_price", 0) or 0)
    if int(hero.get("gold", 0) or 0) < price:
        return False, f"Zakup wymaga {price} Złota."

    hero["gold"] = int(hero.get("gold", 0) or 0) - price
    site["owner_type"] = "player"
    site["owner_player_number"] = _player_number(hero)
    site["owner_name"] = str(hero.get("name") or f"Gracz {_player_number(hero)}")
    _append_owned_site(hero, site)
    return True, f"Kupiono {site['name']} za {price} Złota. Produkcja zostanie rozliczona podczas Rady."


def right_price(tile) -> int:
    return int(RIGHT_PRICES.get(potential(tile).get("level"), 0))


def player_has_right(hero: dict, tile) -> bool:
    return int(getattr(tile, "extraction_right_owner", 0) or 0) == _player_number(hero)


def grant_extraction_right(hero: dict, tile_id: int, source: str = "quest") -> tuple[bool, str]:
    ensure_production_state(hero)
    tile = world_tile(tile_id)
    if tile is None:
        return False, "Nie znaleziono heksa."
    if getattr(tile, "production_site", None) is not None:
        return False, "Na tym heksie istnieje już zakład."
    if not potential(tile).get("material"):
        return False, "Ten heks nie posiada potencjału produkcyjnego."
    current = getattr(tile, "extraction_right_owner", None)
    if current not in (None, _player_number(hero)):
        return False, "Prawo do tego heksa posiada już inny gracz."

    tile.extraction_right_owner = _player_number(hero)
    tile.extraction_right_owner_name = str(hero.get("name") or f"Gracz {_player_number(hero)}")
    if int(tile.id) not in hero["extraction_rights"]:
        hero["extraction_rights"].append(int(tile.id))
    return True, f"Zdobyto prawo eksploatacji heksa {tile.id} ({source})."


def buy_extraction_right(location: dict, hero: dict, tile_id: int) -> tuple[bool, str]:
    tile = world_tile(tile_id)
    if tile is None:
        return False, "Nie znaleziono heksa."
    if int(tile.id) not in {int(value) for value in location.get("jurisdiction_tile_ids", [])}:
        return False, "Ten heks nie podlega tej lokacji."
    if getattr(tile, "production_site", None) is not None:
        return False, "Na tym heksie stoi już zakład."
    if getattr(tile, "extraction_right_owner", None) is not None:
        if player_has_right(hero, tile):
            return False, "Posiadasz już prawo do tego heksa."
        return False, "Prawo do tego heksa posiada już inny gracz."

    price = right_price(tile)
    if int(hero.get("gold", 0) or 0) < price:
        return False, f"Prawo eksploatacji kosztuje {price} Złota."
    hero["gold"] = int(hero.get("gold", 0) or 0) - price
    success, message = grant_extraction_right(hero, int(tile.id), source="zakup w lokacji")
    if not success:
        hero["gold"] += price
        return False, message
    return True, f"Kupiono prawo do heksa {tile.id} za {price} Złota: {potential_summary(tile)}."


def build_cost(hero: dict, tile) -> dict[str, Any]:
    level = potential(tile).get("level", "Brak")
    source = BUILD_COSTS.get(level)
    if not source:
        return {"gold": 0, "actions": 0, "materials": {}}
    result = {
        "gold": int(source["gold"]),
        "actions": int(source["actions"]),
        "materials": dict(source["materials"]),
    }
    if _is_merchant(hero):
        result["actions"] = max(1, result["actions"] - 1)
        result["materials"] = {
            name: max(1, int(amount) - 1)
            for name, amount in result["materials"].items()
        }
    return result


def build_cost_text(hero: dict, tile) -> str:
    cost = build_cost(hero, tile)
    materials = ", ".join(f"{amount} {name}" for name, amount in cost["materials"].items())
    merchant = " (bonus Handlarza)" if _is_merchant(hero) else ""
    return f"{cost['actions']} Akcji, {cost['gold']} Złota, {materials}{merchant}"


def start_site_construction(hero: dict, token, tile) -> tuple[bool, str]:
    ensure_production_state(hero)
    if tile is None or token is None or getattr(token, "tile", None) is not tile:
        return False, "Aby rozpocząć budowę, bohater musi stać na wybranym heksie."
    if getattr(tile, "location", None):
        return False, "Nie można budować zakładu na heksie lokacji."
    if getattr(tile, "production_site", None) is not None:
        return False, "Na tym heksie stoi już zakład."
    if not potential(tile).get("material"):
        return False, "Ten heks nie ma potencjału produkcyjnego."
    if not player_has_right(hero, tile):
        return False, f"Najpierw zdobądź prawo eksploatacji w lokacji: {getattr(tile, 'jurisdiction_name', 'brak')}."

    cost = build_cost(hero, tile)
    if int(getattr(token, "actions", 0) or 0) < int(cost["actions"]):
        return False, f"Budowa wymaga {cost['actions']} Akcji."
    if int(hero.get("gold", 0) or 0) < int(cost["gold"]):
        return False, f"Budowa wymaga {cost['gold']} Złota."
    materials = hero.setdefault("materials", {})
    missing = [
        f"{name} {materials.get(name, 0)}/{amount}"
        for name, amount in cost["materials"].items()
        if int(materials.get(name, 0) or 0) < int(amount)
    ]
    if missing:
        return False, "Brakuje materiałów: " + ", ".join(missing) + "."

    token.actions = max(0, int(token.actions) - int(cost["actions"]))
    hero["gold"] = int(hero.get("gold", 0) or 0) - int(cost["gold"])
    for name, amount in cost["materials"].items():
        materials[name] = max(0, int(materials.get(name, 0) or 0) - int(amount))

    site = create_site(
        tile,
        owner_type="player",
        owner_name=hero.get("name", "Gracz"),
        owner_player_number=_player_number(hero),
        status="construction",
    )
    site["construction_waiting_for_council"] = True
    _append_owned_site(hero, site)
    return True, f"Rozpoczęto budowę: {site['name']}. Zakład ruszy na początku następnej Rady."


def activate_constructions(hero: dict) -> list[dict[str, Any]]:
    activated = []
    for site in owned_sites(hero):
        if site.get("status") != "construction":
            continue
        site["status"] = "active"
        site["construction_waiting_for_council"] = False
        activated.append(site)
    return activated


def roll_site_production(hero: dict, site: dict, council_key: int | str, rng=None) -> tuple[bool, str, int]:
    ensure_production_state(hero)
    rng = rng or random
    if site.get("status") != "active":
        return False, "Zakład jest jeszcze w budowie.", 0
    if site.get("owner_type") != "player" or int(site.get("owner_player_number", 0) or 0) != _player_number(hero):
        return False, "Ten zakład nie należy do tego bohatera.", 0
    if str(site.get("last_production_council")) == str(council_key):
        previous = int(site.get("last_production_roll", 0) or 0)
        return False, "Ten zakład produkował już podczas tej Rady.", previous

    die = max(1, int(site.get("die", 1) or 1))
    amount = int(rng.randint(1, die))
    material = str(site.get("material") or "Materiał")
    hero["materials"][material] = int(hero["materials"].get(material, 0) or 0) + amount
    site["last_production_council"] = council_key
    site["last_production_roll"] = amount
    entry = {
        "council": council_key,
        "site_id": site.get("id"),
        "site_name": site.get("name"),
        "material": material,
        "die": die,
        "roll": amount,
    }
    hero["production_history"].append(entry)
    return True, f"{site['name']}: k{die} → {amount}. Otrzymujesz {amount} × {material}.", amount


def takeover_placeholder(hero: dict, token, tile) -> tuple[bool, str]:
    site = getattr(tile, "production_site", None) if tile is not None else None
    if site is None:
        return False, "Na tym heksie nie ma zakładu do przejęcia."
    if token is None or getattr(token, "tile", None) is not tile:
        return False, "Aby próbować przejęcia, bohater musi stać na heksie zakładu."
    if site.get("owner_type") == "player" and int(site.get("owner_player_number", 0) or 0) == _player_number(hero):
        return False, "Ten zakład już należy do Ciebie."
    if int(getattr(token, "actions", 0) or 0) < TAKEOVER_ACTION_COST:
        return False, f"Próba przejęcia wymaga {TAKEOVER_ACTION_COST} Akcji."

    token.actions = max(0, int(token.actions) - TAKEOVER_ACTION_COST)
    site.setdefault("takeover_attempts", []).append(
        {
            "player_number": _player_number(hero),
            "player_name": hero.get("name", "Gracz"),
            "action_cost": TAKEOVER_ACTION_COST,
            "placeholder": True,
        }
    )
    return True, (
        f"Próba przejęcia ALFA zużyła {TAKEOVER_ACTION_COST} Akcji. "
        "Właściciel nie zmienia się jeszcze — test, atrybut i trudność zostaną podpięte później."
    )


def site_owner_label(site: dict | None) -> str:
    if not site:
        return "Brak"
    if site.get("owner_type") == "location":
        return f"Lokacja: {site.get('owner_name', '-')}"
    return f"Gracz: {site.get('owner_name', '-')}"
