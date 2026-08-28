import random

from rg_core.data import TERRAINS
from rg_content.locations import initialize_location
from rg_engine.production import (
    assign_jurisdictions,
    assign_tile_potentials,
    register_world_tiles,
    seed_location_sites,
)
from rg_world.location_names import location_name
from rg_world.map import Tile, generate_positions

LOCATIONS = [
    {"kind": "city", "type_name": "Miasto", "name": "Miasto", "symbol": "M", "count": 3, "color": (220, 180, 85)},
    {"kind": "village", "type_name": "Wies", "name": "Wies", "symbol": "W", "count": 3, "color": (105, 190, 95)},
    {"kind": "castle", "type_name": "Zamek", "name": "Zamek", "symbol": "Z", "count": 3, "color": (165, 165, 175)},
]


# Przy 9 lokacjach i zasadzie trzech zakladow na lokacje generator moze czasem
# wylosowac zbyt ciasny podzial jurysdykcji. Zamiast lamac zasade 1 heks =
# 1 zaklad, losujemy taki swiat ponownie.
WORLD_GENERATION_ATTEMPTS = 100


def create_random_tiles(map_key, rng=None):
    rng = rng or random
    terrain_keys = list(TERRAINS.keys())
    weights = [TERRAINS[key]["weight"] for key in terrain_keys]
    tiles = []
    for tile_id, (q, r, x, y) in enumerate(generate_positions(map_key), start=1):
        terrain_key = rng.choices(terrain_keys, weights=weights, k=1)[0]
        tiles.append(Tile(tile_id, q, r, x, y, terrain_key))
    return tiles


def build_location_data(location, number):
    location_number = number + 1
    legacy_name = f"{location['name']} {location_number}"
    data = {
        "kind": location["kind"],
        "type_name": location["type_name"],
        "name": location_name(location["kind"], location_number, legacy_name),
        "legacy_name": legacy_name,
        "symbol": location["symbol"],
        "color": location["color"],
        "number": location_number,
    }
    if location["kind"] == "city" and number == 0:
        data["background"] = "lirion_miasto"
    return initialize_location(data)


def assign_locations(tiles, rng=None):
    rng = rng or random
    used = set()
    for tile in tiles:
        tile.location = None
    for location in LOCATIONS:
        for number in range(location["count"]):
            candidates = [tile for tile in tiles if tile.terrain["passable"] and tile not in used]
            if not candidates:
                return tiles
            tile = rng.choice(candidates)
            used.add(tile)
            tile.location = build_location_data(location, number)
    return tiles


def _try_generate_world(map_key, rng):
    tiles = create_random_tiles(map_key, rng)
    assign_tile_potentials(tiles, rng)
    assign_locations(tiles, rng)
    if not assign_jurisdictions(tiles):
        return None
    register_world_tiles(tiles)
    if not seed_location_sites(tiles, rng):
        return None
    return tiles


def generate_world(map_key="rosette9"):
    for _attempt in range(WORLD_GENERATION_ATTEMPTS):
        tiles = _try_generate_world(map_key, random)
        if tiles is not None:
            return tiles
    raise RuntimeError(
        "Nie udalo sie wygenerowac swiata spelniajacego zasade: "
        "kazda lokacja ma 3 rozne zaklady, a jeden heks moze miec tylko 1 zaklad."
    )
