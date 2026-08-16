import random
import unittest

from rg_content.quest_book import quest_paragraph
from rg_content.quests import SATANIC_FORCES_ID, SPOR_O_STUDNIE_ID, register_all_quests
from rg_core.quest_runtime import resolve_quest_option
from rg_engine.quest_effect_bridge import install_quest_effect_bridge
from rg_engine.quests import (
    abandon_quest,
    activate_quest,
    can_trade_quest,
    complete_quest,
    draw_quest_id,
    prepare_quest_test,
    quest_definition,
    reset_quest_deck,
    resolve_option,
    return_quest_id_to_deck,
    scaled_gold_reward,
)
from rg_engine.world import register_players, reset_world_progression


class FixedRng:
    def __init__(self, *rolls):
        self.rolls = list(rolls)

    def randint(self, _minimum, _maximum):
        return self.rolls.pop(0)


class Tile:
    location = {"name": "Artium"}


class Token:
    def __init__(self):
        self.actions = 10
        self.tile = Tile()
        self.start_tile = self.tile


def player():
    return {
        "stats": {"Nauka": 5, "Intryga": 2, "Kultura": 2, "Walka": 2},
        "gold": 5,
        "legend": 0,
        "wounds": 0,
        "food": [],
        "goods": [],
        "materials": {},
        "helpers": [],
        "inventory": [],
        "equipment": {},
        "active_quests": [],
        "completed_quests": [],
        "failed_quests": [],
        "abandoned_quests": [],
        "_token_ref": Token(),
    }


class QuestEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_all_quests()
        install_quest_effect_bridge()

    def setUp(self):
        reset_world_progression(1)
        reset_quest_deck()
        register_players([])

    def test_failures_do_not_reduce_gold_reward(self):
        self.assertEqual([scaled_gold_reward(8, value) for value in range(5)], [8, 8, 8, 8, 8])

    def test_stage_success_uses_one_action_and_discovers_expansion(self):
        hero = player()
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]

        success, _message = resolve_option(hero, quest, 0, FixedRng(10))

        self.assertTrue(success)
        self.assertEqual(hero["_token_ref"].actions, 9)
        self.assertTrue(quest["started"])
        self.assertEqual(quest["stage_number"], 2)
        self.assertIn("1A", quest["discovered_expansions"])

    def test_failure_penalty_does_not_accumulate(self):
        hero = player()
        hero["stats"]["Nauka"] = 0
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]

        resolve_option(hero, quest, 0, FixedRng(1))
        self.assertEqual(quest["difficulty_modifier"], 2)
        resolve_option(hero, quest, 0, FixedRng(2))
        self.assertEqual(quest["difficulty_modifier"], 1)

    def test_fifth_failure_loses_quest(self):
        hero = player()
        hero["stats"]["Nauka"] = 0
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]

        for _ in range(5):
            if quest.get("status") == "active":
                resolve_option(hero, quest, 0, FixedRng(2))

        self.assertEqual(quest["failures"], 5)
        self.assertEqual(quest["status"], "failed")
        self.assertNotIn(quest, hero["active_quests"])
        self.assertIn(quest, hero["failed_quests"])

    def test_final_failed_test_opens_combat(self):
        hero = player()
        hero["stats"]["Nauka"] = 0
        quest = activate_quest(SATANIC_FORCES_ID)
        quest["stage_number"] = 3
        quest["stage"] = "3/3"
        hero["active_quests"] = [quest]

        success, _message = resolve_option(hero, quest, 0, FixedRng(2))

        self.assertFalse(success)
        self.assertEqual(quest["failures"], 1)
        self.assertEqual(quest["status"], "combat_pending")
        self.assertEqual(quest["pending_combat"]["enemy_id"], "przeklety_zolnierz")

    def test_completion_grants_full_item_legend_and_gold_after_failures(self):
        hero = player()
        quest = activate_quest(SATANIC_FORCES_ID)
        quest["failures"] = 4
        hero["active_quests"] = [quest]

        complete_quest(hero, quest)

        self.assertEqual(hero["legend"], 2)
        self.assertEqual(hero["gold"], 13)
        self.assertEqual(hero["inventory"][0]["name"], "Krótki miecz")
        self.assertEqual(len(hero["food"]), 3)

    def test_natural_twenty_completes_only_current_test(self):
        hero = player()
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]

        success, _message = resolve_option(hero, quest, 0, FixedRng(20))

        self.assertTrue(success)
        self.assertEqual(quest["status"], "active")
        self.assertEqual(quest["stage_number"], 2)
        self.assertEqual(hero["legend"], 0)

    def test_natural_one_is_automatic_failure_even_with_huge_bonus(self):
        hero = player()
        hero["stats"]["Nauka"] = 100
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]

        success, _message = resolve_option(hero, quest, 0, FixedRng(1))

        self.assertFalse(success)
        self.assertEqual(quest["failures"], 1)
        self.assertEqual(quest["difficulty_modifier"], 2)

    def test_prepare_is_once_per_quest_and_adds_two(self):
        hero = player()
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]

        prepared, _message = prepare_quest_test(hero, quest)
        self.assertTrue(prepared)
        self.assertEqual(hero["_token_ref"].actions, 9)

        success, _message = resolve_option(hero, quest, 0, FixedRng(4))
        self.assertTrue(success)
        self.assertEqual(quest["history"][-1]["total"], 11)
        self.assertEqual(hero["_token_ref"].actions, 8)

        prepared_again, _message = prepare_quest_test(hero, quest)
        self.assertFalse(prepared_again)

    def test_trade_is_allowed_only_before_first_quest_action(self):
        hero = player()
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]

        allowed, _message = can_trade_quest(quest)
        self.assertTrue(allowed)

        resolve_option(hero, quest, 0, FixedRng(10))
        allowed, _message = can_trade_quest(quest)
        self.assertFalse(allowed)

    def test_abandon_unstarted_quest_returns_it_to_deck(self):
        hero = player()
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]

        success, _message = abandon_quest(hero, quest)

        self.assertTrue(success)
        self.assertEqual(quest["status"], "returned_to_deck")
        self.assertNotIn(quest, hero["active_quests"])
        self.assertNotIn(quest, hero["abandoned_quests"])

    def test_runtime_adds_four_to_threshold_when_hero_is_two_levels_ahead(self):
        hero = player()
        hero["legend"] = 20
        hero["stats"]["Nauka"] = 5
        others = [{"legend": 0} for _ in range(5)]
        register_players([hero, *others])
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]

        success, _message = resolve_quest_option(hero, quest, 0, FixedRng(6))

        self.assertFalse(success)
        self.assertEqual(quest["history"][-1]["threshold"], 15)
        self.assertEqual(quest["history"][-1]["total"], 11)

    def test_main_deck_reserves_each_visible_offer_only_once(self):
        rng = random.Random(7)
        drawn = [draw_quest_id(1, rng=rng) for _ in range(4)]
        self.assertEqual(len(set(drawn)), 4)
        self.assertNotIn(None, drawn)
        self.assertIsNone(draw_quest_id(1, rng=rng))

    def test_returned_unstarted_offer_can_enter_draw_pile_again(self):
        rng = random.Random(11)
        first = draw_quest_id(1, rng=rng)
        return_quest_id_to_deck(first, rng=rng)
        drawn = [draw_quest_id(1, rng=rng) for _ in range(4)]
        self.assertIn(first, drawn)

    def test_spor_o_studnie_has_fixed_number_13(self):
        definition = quest_definition(SPOR_O_STUDNIE_ID)
        self.assertIsNotNone(definition)
        self.assertEqual(definition["quest_number"], 13)
        self.assertEqual(definition["deck"], "Questy")

    def test_quest_book_uses_independent_paragraph_numbers(self):
        paragraph = quest_paragraph("130A")
        self.assertIsNotNone(paragraph)
        self.assertEqual(paragraph["quest_id"], SPOR_O_STUDNIE_ID)
        self.assertTrue(paragraph["text"])


if __name__ == "__main__":
    unittest.main()
