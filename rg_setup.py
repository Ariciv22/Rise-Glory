import math
import random

from rg_adventure import install_adventure_system
from rg_data import HERO_ARCHETYPES, STAT_NAMES, clone_hero
from rg_map import HeroToken


def default_custom_stats():
    return {name: 0 for name in STAT_NAMES}


def random_archetype():
    return random.choice(HERO_ARCHETYPES)


def build_player(archetype, world_name, player_index, custom_stats=None):
    return clone_hero(archetype, world_name=world_name, player_index=player_index, stats=custom_stats)


def _angle(tile):
    return math.atan2(tile.y, tile.x)


def _distance(tile):
    return math.hypot(tile.x, tile.y)


def find_start_tiles(tiles, player_count):
    passable = [
        tile for tile in tiles
        if tile.terrain["passable"] and not getattr(tile, "adventure", None)
    ]
    if not passable:
        passable = [tile for tile in tiles if tile.terrain["passable"]]
    if not passable:
        return tiles[:player_count]

    outer = sorted(passable, key=_distance, reverse=True)[: max(18, player_count * 4)]
    outer.sort(key=_angle)

    if player_count == 1:
        return [outer[0]]

    chosen = []
    step = len(outer) / player_count
    for idx in range(player_count):
        candidate = outer[int(round(idx * step)) % len(outer)]
        if candidate in chosen:
            candidate = next(tile for tile in outer if tile not in chosen)
        chosen.append(candidate)
    return chosen


def create_tokens(players, tiles):
    starts = find_start_tiles(tiles, len(players))
    return [HeroToken(player, start) for player, start in zip(players, starts)]


install_adventure_system()
