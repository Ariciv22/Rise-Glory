import unittest

from rg_content.quests import SATANIC_FORCES_ID, register_all_quests
from rg_core.quest_runtime import resolve_quest_option
from rg_engine.quests import activate_quest, complete_quest, resolve_option, scaled_gold_reward
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
        self.actions = 4
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
        "_token_ref": Token(),
    }


class QuestEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_all_quests()

    def setUp(self):
        reset_world_progression(1)
        register_players([])

    def test_gold_scaling_only_affects_gold(self):
        self.assertEqual([scaled_gold_reward(8, value) for value in range(4)], [8, 6, 4, 2])

    def test_stage_success_uses_one_action(self):
        hero = player()
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]
        success, _message = resolve_option(hero, quest, 0, FixedRng(10))
        self.assertTrue(success)
        self.assertEqual(hero["_token_ref"].actions, 3)
        self.assertEqual(quest["stage_number"], 2)

    def test_failure_penalty_does_not_accumulate(self):
        hero = player()
        hero["stats"]["Nauka"] = 0
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]
        resolve_option(hero, quest, 0, FixedRng(1))
        self.assertEqual(quest["difficulty_modifier"], 2)
        resolve_option(hero, quest, 0, FixedRng(2))
        self.assertEqual(quest["difficulty_modifier"], 1)

    def test_final_failure_opens_combat(self):
        hero = player()
        hero["stats"]["Nauka"] = 0
        quest = activate_quest(SATANIC_FORCES_ID)
        quest["stage_number"] = 3
        quest["stage"] = "3/3"
        hero["active_quests"] = [quest]
        success, _message = resolve_option(hero, quest, 0, FixedRng(2))
        self.assertFalse(success)
        self.assertEqual(quest["status"], "combat_pending")
        self.assertEqual(quest["pending_combat"]["enemy_id"], "przeklety_zolnierz")

    def test_completion_grants_item_and_legend(self):
        hero = player()
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]
        complete_quest(hero, quest)
        self.assertEqual(hero["legend"], 2)
        self.assertEqual(hero["gold"], 13)
        self.assertEqual(hero["inventory"][0]["name"], "Krótki miecz")
        self.assertEqual(len(hero["food"]), 3)

    def test_natural_twenty_clears_only_one_following_stage(self):
        hero = player()
        quest = activate_quest(SATANIC_FORCES_ID)
        hero["active_quests"] = [quest]
        success, _message = resolve_option(hero, quest, 0, FixedRng(20))
        self.assertTrue(success)
        self.assertEqual(quest["status"], "active")
        self.assertEqual(quest["stage_number"], 3)
        self.assertEqual(hero["legend"], 0)

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


if __name__ == "__main__":
    unittest.main()
