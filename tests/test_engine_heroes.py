import unittest

from rg_engine.heroes import (
    begin_hero_turn,
    defeat_hero,
    ensure_hero_state,
    heal_at_location,
    healing_cost_per_wound,
    helper_bonus,
    train_stat,
    turn_action_limit,
    wound_test_penalty,
)


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

    def test_two_and_three_wounds_reduce_max_hp(self):
        hero_two = ensure_hero_state({"wounds": 2, "max_hp": 10, "hp": 10})
        hero_three = ensure_hero_state({"wounds": 3, "max_hp": 10, "hp": 10})
        self.assertEqual(hero_two["max_hp"], 8)
        self.assertEqual(hero_two["hp"], 8)
        self.assertEqual(hero_three["max_hp"], 6)
        self.assertEqual(hero_three["hp"], 6)

    def test_wounds_apply_global_test_penalty_through_test_bonus(self):
        one_wound = ensure_hero_state({"wounds": 1, "helpers": []})
        three_wounds = ensure_hero_state({"wounds": 3, "helpers": []})
        helped = ensure_hero_state(
            {
                "wounds": 1,
                "helpers": [{"name": "Pomocnik", "stat_bonus": {"Nauka": 2}}],
            }
        )
        self.assertEqual(wound_test_penalty(one_wound), -1)
        self.assertEqual(helper_bonus(one_wound, "Nauka"), -1)
        self.assertEqual(helper_bonus(three_wounds, "Nauka"), -2)
        self.assertEqual(helper_bonus(helped, "Nauka"), 1)

    def test_three_wounds_reduce_turn_action_limit_to_two(self):
        self.assertEqual(turn_action_limit({"wounds": 2}), 4)
        self.assertEqual(turn_action_limit({"wounds": 3}), 2)

    def test_healing_cost_scales_with_world_level(self):
        hero = ensure_hero_state({"wounds": 1})
        self.assertEqual(healing_cost_per_wound(hero, world_level=1), 2)
        self.assertEqual(healing_cost_per_wound(hero, world_level=2), 3)
        self.assertEqual(healing_cost_per_wound(hero, world_level=3), 4)
        self.assertEqual(healing_cost_per_wound(hero, world_level=4), 5)

    def test_healing_wounds_does_not_restore_hp(self):
        hero = {"wounds": 2, "gold": 10, "hp": 3, "max_hp": 10}
        token = Token()
        success, _message = heal_at_location(hero, token)
        self.assertTrue(success)
        self.assertEqual(hero["wounds"], 0)
        self.assertEqual(hero["hp"], 3)
        self.assertEqual(hero["max_hp"], 10)
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
        self.assertEqual(hero["max_hp"], 8)
        self.assertEqual(hero["gold"], 3)
        self.assertIs(token.tile, tile)
        self.assertEqual(token.actions, 0)
        self.assertEqual(result["lost_gold"], 2)
        self.assertFalse(result["full_defeat"])
        self.assertFalse(hero["inventory"])
        self.assertEqual(hero["discarded_items"][0]["name"], "Latarnia")

    def test_fourth_wound_causes_full_defeat_until_next_turn(self):
        hero = ensure_hero_state({"wounds": 3, "gold": 10, "hp": 5, "inventory": []})
        token = Token()
        hero["_token_ref"] = token

        result = defeat_hero(hero, token, world_level=4)

        self.assertTrue(result["full_defeat"])
        self.assertEqual(hero["wounds"], 4)
        self.assertEqual(hero["hp"], 0)
        self.assertTrue(hero["_unconscious_until_next_turn"])
        self.assertEqual(hero["gold"], 6)
        self.assertEqual(token.actions, 0)

        state = begin_hero_turn(hero, token)
        self.assertTrue(state["woke_up"])
        self.assertEqual(hero["wounds"], 3)
        self.assertEqual(hero["hp"], 1)
        self.assertFalse(hero["_unconscious_until_next_turn"])
        self.assertEqual(token.actions, 2)

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
