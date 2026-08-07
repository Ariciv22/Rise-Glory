import unittest

from rg_world.adventure import (
    ADVENTURE_GOLD_REWARD,
    close_active_adventure,
    get_active_adventure,
    reset_adventure_event,
    resolve_active_adventure,
    start_adventure,
)


class _Tile:
    id = 7

    def __init__(self):
        self.adventure = {"card": "traveler_and_vagabond"}


class AdventureEventTests(unittest.TestCase):
    def tearDown(self):
        reset_adventure_event()

    def test_low_roll_adds_one_wound_and_consumes_token(self):
        hero = {"wounds": 0, "gold": 5}
        tile = _Tile()

        start_adventure(hero, tile)
        resolve_active_adventure(12)

        self.assertIsNone(tile.adventure)
        self.assertEqual(hero["wounds"], 1)
        self.assertEqual(hero["gold"], 5)
        self.assertTrue(close_active_adventure())

    def test_high_roll_adds_gold(self):
        hero = {"wounds": 0, "gold": 5}
        tile = _Tile()

        start_adventure(hero, tile)
        resolve_active_adventure(13)

        self.assertEqual(hero["wounds"], 0)
        self.assertEqual(hero["gold"], 5 + ADVENTURE_GOLD_REWARD)

    def test_event_cannot_be_closed_before_roll(self):
        hero = {"wounds": 0, "gold": 5}
        start_adventure(hero, _Tile())

        self.assertFalse(close_active_adventure())
        self.assertIsNotNone(get_active_adventure())

    def test_roll_is_resolved_only_once(self):
        hero = {"wounds": 0, "gold": 5}
        start_adventure(hero, _Tile())

        resolve_active_adventure(20)
        resolve_active_adventure(1)

        self.assertEqual(hero["gold"], 5 + ADVENTURE_GOLD_REWARD)
        self.assertEqual(hero["wounds"], 0)


if __name__ == "__main__":
    unittest.main()
