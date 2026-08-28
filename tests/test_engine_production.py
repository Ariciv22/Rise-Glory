from types import SimpleNamespace

from rg_engine.production import (
    TERRAIN_MATERIALS,
    activate_constructions,
    assign_tile_potentials,
    build_cost,
    create_site,
    potential,
    register_world_tiles,
    roll_site_production,
    start_site_construction,
)


class FixedRng:
    def __init__(self, value=3):
        self.value = value

    def randint(self, low, high):
        return max(low, min(high, self.value))

    def shuffle(self, values):
        return None

    def choice(self, values):
        return values[0]


class DummyTile:
    def __init__(self, tile_id, terrain_key="mountain"):
        self.id = tile_id
        self.terrain_key = terrain_key
        self.terrain = {"name": terrain_key, "move": 1, "passable": True}
        self.location = None
        self.x = tile_id * 10
        self.y = 0
        self.production_site = None
        self.extraction_right_owner = None
        self.extraction_right_owner_name = None
        self.jurisdiction_name = "Artium"


def _set_potential(tile, level="Średni", material="Żelazo", die=6):
    tile.resource_potential = {"level": level, "material": material, "die": die}
    return tile


def test_tundra_can_generate_dark_steel():
    assert "Mroczna Stal" in TERRAIN_MATERIALS["tundra"]


def test_potential_distribution_is_roughly_95_percent_on_61_tiles():
    tiles = [DummyTile(index + 1, "mountain") for index in range(61)]
    assign_tile_potentials(tiles, FixedRng())
    levels = [potential(tile)["level"] for tile in tiles]
    assert levels.count("Brak") == 3
    assert levels.count("Słaby") == 34
    assert levels.count("Średni") == 18
    assert levels.count("Mocny") == 6


def test_merchant_builds_with_one_less_action_and_material_piece():
    tile = _set_potential(DummyTile(1), level="Mocny", die=8)
    normal = {"player_number": 1, "archetype_id": 1}
    merchant = {"player_number": 2, "archetype_id": 2, "archetype_name": "Handlarz"}

    normal_cost = build_cost(normal, tile)
    merchant_cost = build_cost(merchant, tile)

    assert merchant_cost["actions"] == normal_cost["actions"] - 1
    assert merchant_cost["gold"] == normal_cost["gold"]
    for material, amount in normal_cost["materials"].items():
        assert merchant_cost["materials"][material] == max(1, amount - 1)


def test_construction_activates_at_next_council_and_can_produce_once():
    tile = _set_potential(DummyTile(7), level="Średni", material="Żelazo", die=6)
    hero = {
        "name": "Kupiec",
        "player_number": 1,
        "archetype_id": 2,
        "gold": 20,
        "materials": {"Drewno": 10, "Kamień": 10, "Żelazo": 10},
    }
    tile.extraction_right_owner = 1
    tile.extraction_right_owner_name = hero["name"]
    token = SimpleNamespace(tile=tile, actions=4)
    register_world_tiles([tile])

    success, _message = start_site_construction(hero, token, tile)
    assert success is True
    assert tile.production_site["status"] == "construction"

    activated = activate_constructions(hero)
    assert activated == [tile.production_site]
    assert tile.production_site["status"] == "active"

    success, _message, amount = roll_site_production(hero, tile.production_site, 5, FixedRng(3))
    assert success is True
    assert amount == 3
    assert hero["materials"]["Żelazo"] >= 3

    second_success, _message, second_amount = roll_site_production(hero, tile.production_site, 5, FixedRng(6))
    assert second_success is False
    assert second_amount == 3


def test_one_tile_holds_only_one_site_reference():
    tile = _set_potential(DummyTile(4), level="Słaby", material="Drewno", die=4)
    site = create_site(tile, owner_type="location", owner_name="Lirion")
    assert tile.production_site is site
    assert site["tile_id"] == tile.id
