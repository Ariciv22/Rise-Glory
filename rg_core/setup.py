import math
import random
from pathlib import Path

from rg_ui import council as rg_council_background
from rg_world.adventure import install_adventure_system
from rg_world.world_event_markers import install_world_event_markers
from rg_ui.world_state import install_world_state_ui
from rg_ui.threats import install_threat_investigation_ui
from rg_ui.dev_threat_fix import install_dev_threat_fix
from rg_ui.combat_image_fit import install_combat_image_fit
from rg_core.data import HERO_ARCHETYPES, STAT_NAMES, clone_hero
from rg_engine.heroes import ensure_hero_state
from rg_engine.threats import is_tile_entry_blocked, threat_modifier
from rg_engine.world import register_players, reset_world_progression
from rg_engine.world_events import movement_cost_with_world_event, reset_world_event_deck
from rg_world.map import HeroToken
from rg_ui.premium_dice import install_premium_dice_animation

ROOT_DIR = Path(__file__).resolve().parents[1]
COUNCIL_TRADE_BACKGROUND_PATH = ROOT_DIR / "Grafiki" / "rada_bohaterów_handel.png"


class GameHeroToken(HeroToken):
    """Pionek korzystający ze wspólnych kosztów Akcji i blokad Zagrożeń."""

    def movement_cost(self, target):
        if not target:
            return 0
        base_cost = int(target.terrain.get("move", 1) or 1)
        cost = movement_cost_with_world_event(base_cost)
        local_modifier = threat_modifier("movement_cost_modifier", tile_id=int(getattr(target, "id", 0) or 0))
        return max(1, cost + local_modifier)

    def can_move_to(self, target):
        if not super().can_move_to(target):
            return False
        blocked, _reason = is_tile_entry_blocked(int(getattr(target, "id", 0) or 0))
        if blocked:
            return False
        return int(self.actions) >= self.movement_cost(target)

    def move_to(self, target):
        if not self.can_move_to(target):
            return False
        self.actions = max(0, int(self.actions) - self.movement_cost(target))
        self.tile = target
        return True


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
    passable = [tile for tile in tiles if tile.terrain["passable"] and not getattr(tile, "adventure", None)]
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
    reset_world_event_deck()
    reset_world_progression(1)
    for player in players:
        ensure_hero_state(player)
    starts = find_start_tiles(tiles, len(players))
    tokens = [GameHeroToken(player, start) for player, start in zip(players, starts)]
    register_players(players)
    for token in tokens:
        token.start_tile = token.tile
        token.hero["_token_ref"] = token
    return tokens


def install_council_trade_background():
    rg_council_background.COUNCIL_BACKGROUND_PATH = COUNCIL_TRADE_BACKGROUND_PATH
    rg_council_background._SOURCE_CACHE["loaded"] = False
    rg_council_background._SOURCE_CACHE["surface"] = None
    rg_council_background._BACKGROUND_CACHE["size"] = None
    rg_council_background._BACKGROUND_CACHE["surface"] = None


install_adventure_system()
install_world_event_markers()
install_world_state_ui()
install_threat_investigation_ui()
install_dev_threat_fix()
install_premium_dice_animation()
install_combat_image_fit()
install_council_trade_background()
