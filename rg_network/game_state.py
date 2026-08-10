from __future__ import annotations

import copy
import math
import random
import secrets
from typing import Any

from rg_content.locations import initialize_location
from rg_core.data import ACTIONS_PER_TURN, COUNCIL_ROUNDS, HEX_SIZE, HERO_ARCHETYPES, TERRAINS, clone_hero
from rg_engine.turns import resolve_initiative

MAP_KEY = "rosette9"
ROW_LENGTHS = [5, 6, 7, 8, 9, 8, 7, 6, 5]

LOCATIONS = [
    {"kind": "city", "type_name": "Miasto", "name": "Miasto", "symbol": "M", "count": 3, "color": (220, 180, 85)},
    {"kind": "village", "type_name": "Wies", "name": "Wies", "symbol": "W", "count": 3, "color": (105, 190, 95)},
    {"kind": "castle", "type_name": "Zamek", "name": "Zamek", "symbol": "Z", "count": 3, "color": (165, 165, 175)},
]


def _rosette_positions() -> list[tuple[int, int, float, float]]:
    raw: list[tuple[int, int, float, float]] = []
    horizontal = HEX_SIZE * math.sqrt(3)
    vertical = HEX_SIZE * 1.5
    center_row = (len(ROW_LENGTHS) - 1) / 2
    for row, length in enumerate(ROW_LENGTHS):
        row_width = (length - 1) * horizontal
        y = (row - center_row) * vertical
        for col in range(length):
            x = col * horizontal - row_width / 2
            raw.append((col, row, x, y))
    return raw


def _build_location_data(template: dict[str, Any], number: int) -> dict[str, Any]:
    data = {
        "kind": template["kind"],
        "type_name": template["type_name"],
        "name": f"{template['name']} {number + 1}",
        "symbol": template["symbol"],
        "color": template["color"],
        "number": number + 1,
    }
    if template["kind"] == "city" and number == 0:
        data["name"] = "Lirion"
        data["background"] = "lirion_miasto"
    elif template["kind"] == "castle" and number == 0:
        data["name"] = "Artium"
    return data


def _generate_tiles(rng: random.Random) -> list[dict[str, Any]]:
    terrain_keys = list(TERRAINS.keys())
    weights = [TERRAINS[key]["weight"] for key in terrain_keys]
    tiles: list[dict[str, Any]] = []
    for tile_id, (q, r, x, y) in enumerate(_rosette_positions(), start=1):
        terrain_key = rng.choices(terrain_keys, weights=weights, k=1)[0]
        tiles.append(
            {
                "id": tile_id,
                "q": q,
                "r": r,
                "x": x,
                "y": y,
                "terrain_key": terrain_key,
                "location": None,
                "adventure": None,
            }
        )

    used: set[int] = set()
    for template in LOCATIONS:
        for number in range(template["count"]):
            candidates = [
                tile for tile in tiles
                if TERRAINS[tile["terrain_key"]]["passable"] and tile["id"] not in used
            ]
            if not candidates:
                break
            tile = rng.choice(candidates)
            used.add(tile["id"])
            tile["location"] = initialize_location(_build_location_data(template, number), rng)
    return tiles


def _find_start_tile_ids(tiles: list[dict[str, Any]], player_count: int) -> list[int]:
    passable = [tile for tile in tiles if TERRAINS[tile["terrain_key"]]["passable"]]
    if not passable:
        return [tile["id"] for tile in tiles[:player_count]]

    outer = sorted(passable, key=lambda tile: math.hypot(tile["x"], tile["y"]), reverse=True)[
        : max(18, player_count * 4)
    ]
    outer.sort(key=lambda tile: math.atan2(tile["y"], tile["x"]))
    if player_count == 1:
        return [outer[0]["id"]]

    chosen: list[dict[str, Any]] = []
    step = len(outer) / player_count
    for index in range(player_count):
        candidate = outer[int(round(index * step)) % len(outer)]
        if candidate in chosen:
            candidate = next(tile for tile in outer if tile not in chosen)
        chosen.append(candidate)
    return [tile["id"] for tile in chosen]


def _are_adjacent(first: dict[str, Any], second: dict[str, Any]) -> bool:
    return math.hypot(first["x"] - second["x"], first["y"] - second["y"]) <= HEX_SIZE * 1.85


class NetworkGameSession:
    """Autorytatywny, niezalezny od Pygame stan pierwszej gry LAN."""

    def __init__(self, lobby_players: list[dict[str, Any]], seed: int | None = None) -> None:
        if len(lobby_players) < 2:
            raise ValueError("Do gry LAN potrzeba co najmniej 2 graczy.")
        self.seed = int(seed if seed is not None else secrets.randbits(31))
        self.rng = random.Random(self.seed)
        self.current_map = MAP_KEY
        self.players: list[dict[str, Any]] = []

        for index, lobby_player in enumerate(lobby_players):
            archetype_id = int(lobby_player.get("archetype_id", 0) or 0)
            archetype = next((item for item in HERO_ARCHETYPES if item["id"] == archetype_id), None)
            if archetype is None:
                raise ValueError("Kazdy gracz musi wybrac bohatera przed startem.")
            hero = clone_hero(archetype, world_name=str(lobby_player.get("name") or f"Gracz {index + 1}"), player_index=index)
            hero["network_player_id"] = str(lobby_player["player_id"])
            self.players.append(
                {
                    "network_player_id": str(lobby_player["player_id"]),
                    "hero": hero,
                }
            )

        self.tiles = _generate_tiles(self.rng)
        self.tiles_by_id = {int(tile["id"]): tile for tile in self.tiles}
        start_tile_ids = _find_start_tile_ids(self.tiles, len(self.players))
        self.tokens = [
            {
                "player_index": index,
                "tile_id": tile_id,
                "start_tile_id": tile_id,
                "actions": ACTIONS_PER_TURN,
            }
            for index, tile_id in enumerate(start_tile_ids)
        ]

        hero_rows = [entry["hero"] for entry in self.players]
        self.initiative = resolve_initiative(hero_rows, self.rng)
        self.turn_order = list(self.initiative["turn_order"])
        self.position = 0
        self.round_number = 1
        self.council_cycle = 1
        self.last_council_due = False

    @property
    def active_player_index(self) -> int:
        return int(self.turn_order[self.position])

    @property
    def active_network_player_id(self) -> str:
        return str(self.players[self.active_player_index]["network_player_id"])

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "seed": self.seed,
            "current_map": self.current_map,
            "players": copy.deepcopy(self.players),
            "tiles": copy.deepcopy(self.tiles),
            "tokens": copy.deepcopy(self.tokens),
            "initiative": copy.deepcopy(self.initiative),
            "turn": {
                "turn_order": list(self.turn_order),
                "position": self.position,
                "active_player_index": self.active_player_index,
                "round_number": self.round_number,
                "council_cycle": self.council_cycle,
                "council_due": self.last_council_due,
            },
        }

    def move(self, network_player_id: str, target_tile_id: int) -> tuple[bool, str]:
        if str(network_player_id) != self.active_network_player_id:
            return False, "To nie jest Twoja tura."

        token = self.tokens[self.active_player_index]
        current = self.tiles_by_id.get(int(token["tile_id"]))
        target = self.tiles_by_id.get(int(target_tile_id))
        if current is None or target is None:
            return False, "Nieprawidlowy heks."
        terrain = TERRAINS[target["terrain_key"]]
        if not terrain["passable"]:
            return False, "Na ten heks nie mozna wejsc."
        if not _are_adjacent(current, target):
            return False, "Mozna ruszyc sie tylko na sasiedni heks."
        cost = int(terrain.get("move", 1) or 1)
        if int(token["actions"]) < cost:
            return False, "Brak wystarczajacej liczby akcji."

        token["actions"] = int(token["actions"]) - cost
        token["tile_id"] = int(target["id"])
        return True, "Ruch zatwierdzony."

    def end_turn(self, network_player_id: str) -> tuple[bool, str]:
        if str(network_player_id) != self.active_network_player_id:
            return False, "To nie jest Twoja tura."

        current_index = self.active_player_index
        self.tokens[current_index]["actions"] = 0
        round_completed = self.position == len(self.turn_order) - 1
        self.position = (self.position + 1) % len(self.turn_order)
        self.tokens[self.active_player_index]["actions"] = ACTIONS_PER_TURN
        self.last_council_due = False

        if round_completed:
            self.round_number += 1
            if self.council_cycle >= COUNCIL_ROUNDS:
                self.last_council_due = True
                self.council_cycle = 1
            else:
                self.council_cycle += 1
        return True, "Tura zakonczona."
