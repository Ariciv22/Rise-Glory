import unittest

from rg_engine.heroes import defeat_hero, ensure_hero_state, heal_at_location, train_stat


class Token:
    def __init__(self):
        self.actions = 4
        self.tile = object()
        self.start_tile = object()


class HeroEngineTests(unittest.TestCase):
    def test_training_uses_one_action_and_expected_gold(self):
        hero = {"stats": {"Nauka": 2}, "gold": 20}
        token = Token()
        success, _message = train_stat(hero, token, "Nauka", ("Nauka",))
        self.assertTrue(success)
        self.assertEqual(hero["stats"]["Nauka"], 3)
        self.assertEqual(hero["gold"], 9)
        self.assertEqual(token.actions, 3)

    def test_hero_starts_with_ten_hp(self):
        hero = {}
        ensure_hero_state(hero)
        self.assertEqual(hero["max_hp"], 10)
        self.assertEqual(hero["hp"], 10)

    def test_healing_wounds_does_not_restore_hp(self):
        hero = {"wounds": 2, "gold": 10, "hp": 3, "max_hp": 10}
        token = Token()
        success, _message = heal_at_location(hero, token)
        self.assertTrue(success)
        self.assertEqual(hero["wounds"], 0)
        self.assertEqual(hero["hp"], 3)
        self.assertEqual(hero["gold"], 6)
        self.assertEqual(token.actions, 3)

    def test_defeat_keeps_hex_adds_wound_sets_one_hp_and_ends_turn(self):
        hero = {
            "wounds": 1,
            "gold": 5,
            "hp": 0,
            "inventory": [{"name": "Latarnia", "category": "misc"}],
        }
        token = Token()
        tile = token.tile
        hero["_combat_defeat_item_index"] = 0
        result = defeat_hero(hero, token, world_level=2)
        self.assertEqual(hero["wounds"], 2)
        self.assertEqual(hero["hp"], 1)
        self.assertEqual(hero["gold"], 3)
        self.assertIs(token.tile, tile)
        self.assertEqual(token.actions, 0)
        self.assertEqual(result["lost_gold"], 2)
        self.assertFalse(hero["inventory"])
        self.assertEqual(hero["discarded_items"][0]["name"], "Latarnia")

    def test_protected_item_is_not_lost(self):
        hero = {
            "gold": 5,
            "hp": 0,
            "inventory": [{"name": "Klucz", "category": "misc", "quest_item": True}],
        }
        token = Token()
        hero["_combat_defeat_item_index"] = 0
        result = defeat_hero(hero, token, world_level=1)
        self.assertIsNone(result["lost_item"])
        self.assertEqual(len(hero["inventory"]), 1)


if __name__ == "__main__":
    unittest.main()