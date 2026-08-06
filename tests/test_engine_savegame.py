import unittest

from rg_engine.savegame import build_snapshot


class Tile:
    def __init__(self, tile_id):
        self.id = tile_id
        self.q = tile_id
        self.r = 0
        self.x = float(tile_id)
        self.y = 0.0
        self.terrain_key = "plains"
        self.location = None
        self.adventure = None


class Token:
    def __init__(self, tile):
        self.tile = tile
        self.start_tile = tile
        self.actions = 3


class SaveGameTests(unittest.TestCase):
    def test_runtime_references_are_removed(self):
        tile = Tile(1)
        hero = {"name": "Tester", "_token_ref": Token(tile), "inventory": []}
        snapshot = build_snapshot("rosette9", [hero], [tile], [hero["_token_ref"]])
        self.assertNotIn("_token_ref", snapshot["players"][0])
        self.assertEqual(snapshot["tokens"][0]["tile_id"], 1)


if __name__ == "__main__":
    unittest.main()
