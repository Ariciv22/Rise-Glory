import random

from rg_data import TERRAINS
from rg_map import Tile, generate_positions

LOCATIONS = [
    {"kind": "city", "name": "Miasto", "symbol": "M", "count": 2, "color": (220, 180, 85)},
    {"kind": "village", "name": "Wies", "symbol": "W", "count": 2, "color": (105, 190, 95)},
    {"kind": "fort", "name": "Grod", "symbol": "G", "count": 1, "color": (165, 165, 175)},
    {"kind": "ruins", "name": "Ruiny", "symbol": "R", "count": 2, "color": (145, 105, 180)},
    {"kind": "special", "name": "Miejsce specjalne", "symbol": "S", "count": 1, "color": (75, 155, 120)},
]


def create_random_tiles(map_key):
    terrain_keys = list(TERRAINS.keys())
    weights = [TERRAINS[key]["weight"] for key in terrain_keys]
    tiles = []
    for tile_id, (q, r, x, y) in enumerate(generate_positions(map_key), start=1):
        terrain_key = random.choices(terrain_keys, weights=weights, k=1)[0]
        tiles.append(Tile(tile_id, q, r, x, y, terrain_key))
    return tiles


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
            tile.location = {
                "kind": location["kind"],
                "name": location["name"],
                "symbol": location["symbol"],
                "color": location["color"],
                "number": number + 1,
            }
    return tiles


def generate_world(map_key):
    tiles = create_random_tiles(map_key)
    assign_locations(tiles)
    return tiles
