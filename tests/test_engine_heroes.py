import unittest

from rg_engine.heroes import defeat_hero, heal_at_location, train_stat


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

    def test_healing_uses_one_action(self):
        hero = {"wounds": 2, "gold": 10}
        token = Token()
        success, _message = heal_at_location(hero, token)
        self.assertTrue(success)
        self.assertEqual(hero["wounds"], 0)
        self.assertEqual(hero["gold"], 6)
        self.assertEqual(token.actions, 3)

    def test_defeat_returns_to_start_and_resets_wounds(self):
        hero = {"wounds": 4, "gold": 5}
        token = Token()
        start = token.start_tile
        result = defeat_hero(hero, token, world_level=2)
        self.assertEqual(hero["wounds"], 0)
        self.assertEqual(hero["gold"], 3)
        self.assertIs(token.tile, start)
        self.assertEqual(result["lost_gold"], 2)


if __name__ == "__main__":
    unittest.main()
