import random

from rg_core.data import TERRAINS
from rg_content.locations import initialize_location
from rg_world.map import Tile, generate_positions

LOCATIONS = [
    {"kind": "city", "type_name": "Miasto", "name": "Miasto", "symbol": "M", "count": 3, "color": (220, 180, 85)},
    {"kind": "village", "type_name": "Wies", "name": "Wies", "symbol": "W", "count": 3, "color": (105, 190, 95)},
    {"kind": "castle", "type_name": "Zamek", "name": "Zamek", "symbol": "Z", "count": 3, "color": (165, 165, 175)},
]


def create_random_tiles(map_key):
    terrain_keys = list(TERRAINS.keys())
    weights = [TERRAINS[key]["weight"] for key in terrain_keys]
    tiles = []
    for tile_id, (q, r, x, y) in enumerate(generate_positions(map_key), start=1):
        terrain_key = random.choices(terrain_keys, weights=weights, k=1)[0]
        tiles.append(Tile(tile_id, q, r, x, y, terrain_key))
    return tiles


def build_location_data(location, number):
    data = {
        "kind": location["kind"],
        "type_name": location["type_name"],
        "name": f"{location['name']} {number + 1}",
        "symbol": location["symbol"],
        "color": location["color"],
        "number": number + 1,
    }
    if location["kind"] == "city" and number == 0:
        data["name"] = "Lirion"
        data["background"] = "lirion_miasto"
    elif location["kind"] == "castle" and number == 0:
        data["name"] = "Artium"
    return initialize_location(data)


def assign_locations(tiles):
    used = set()
    for tile in tiles:
        tile.location = None
    for location in LOCATIONS:
        for number in range(location["count"]):
            candidates = [tile for tile in tiles if tile.terrain["passable"] and tile not in used]
            if not candidates:
                return tiles
            tile = random.choice(candidates)
            used.add(tile)
            tile.location = build_location_data(location, number)
    return tiles


def generate_world(map_key="rosette9"):
    tiles = create_random_tiles(map_key)
    assign_locations(tiles)
    return tiles
