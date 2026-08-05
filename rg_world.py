import random

from rg_data import TERRAINS
from rg_location_data import initialize_location
from rg_map import Tile, generate_positions
from rg_models import LocationState

LOCATIONS = [
    {"kind":"city","type_name":"Miasto","name":"Miasto","symbol":"M","count":3,"color":(220,180,85)},
    {"kind":"village","type_name":"Wies","name":"Wies","symbol":"W","count":3,"color":(105,190,95)},
    {"kind":"castle","type_name":"Zamek","name":"Zamek","symbol":"Z","count":3,"color":(165,165,175)},
]


def create_random_tiles(map_key):
    terrain_keys = list(TERRAINS)
    weights = [TERRAINS[key]["weight"] for key in terrain_keys]
    return [Tile(tile_id, q, r, x, y, random.choices(terrain_keys, weights=weights, k=1)[0]) for tile_id, (q, r, x, y) in enumerate(generate_positions(map_key), start=1)]


def build_location_data(location, number):
    name = f"{location['name']} {number + 1}"
    background = ""
    if location["kind"] == "city" and number == 0:
        name, background = "Lirion", "lirion_miasto"
    return initialize_location(LocationState(location["kind"], location["type_name"], name, location["symbol"], location["color"], number + 1, background))


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
    return assign_locations(tiles)
