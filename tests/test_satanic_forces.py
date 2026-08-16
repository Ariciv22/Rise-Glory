import random
import unittest

from rg_content.locations import initialize_location, take_quest
from rg_engine.quests import reset_quest_deck
from rg_engine.world import register_players
from rg_legacy.satanic_forces import QUEST_ID, activate_quest, resolve_test


class FixedRng:
    def __init__(self, *rolls):
        self.rolls = list(rolls)

    def randint(self, _minimum, _maximum):
        return self.rolls.pop(0)


class TokenStub:
    def __init__(self, actions=4):
        self.actions = actions
        self.tile = None
        self.start_tile = None


def make_player():
    token = TokenStub()
    return {
        "name": "Tester",
        "stats": {"Nauka": 5, "Intryga": 2, "Kultura": 2, "Walka": 2},
        "gold": 5,
        "legend": 0,
        "wounds": 0,
        "food": [],
        "goods": [],
        "inventory": [],
        "materials": {},
        "helpers": [],
        "equipment": {},
        "active_quests": [],
        "completed_quests": [],
        "failed_quests": [],
        "abandoned_quests": [],
        "_token_ref": token,
    }


class SatanicForcesTests(unittest.TestCase):
    def setUp(self):
        reset_quest_deck()
        register_players([])

    def test_location_board_uses_one_quest_deck(self):
        location = {"name": "Artium", "kind": "castle"}
        initialize_location(location, random.Random(4))
        self.assertTrue(location["quest_offers"])
        self.assertTrue(all(card["deck"] == "Questy" for card in location["quest_offers"]))

    def test_taking_board_quest_creates_runtime_state(self):
        location = {"name": "Artium", "kind": "castle"}
        player = make_player()
        register_players([player])
        initialize_location(location, random.Random(4))
        expected_id = location["quest_offers"][0]["id"]
        success, _message = take_quest(location, player, 0, random.Random(4))
        self.assertTrue(success)
        self.assertEqual(player["active_quests"][0]["id"], expected_id)
        self.assertEqual(player["active_quests"][0]["status"], "active")
        self.assertFalse(player["active_quests"][0]["started"])

    def test_success_consumes_one_action_and_advances_stage(self):
        player = make_player()
        player["active_quests"] = [activate_quest()]
        success, _message = resolve_test(player, 0, FixedRng(10))
        self.assertTrue(success)
        self.assertEqual(player["_token_ref"].actions, 3)
        self.assertEqual(player["active_quests"][0]["stage_number"], 2)

    def test_failure_penalty_does_not_accumulate(self):
        player = make_player()
        player["stats"]["Nauka"] = 0
        player["active_quests"] = [activate_quest()]
        resolve_test(player, 0, FixedRng(1))
        self.assertEqual(player["active_quests"][0]["difficulty_modifier"], 2)
        resolve_test(player, 0, FixedRng(2))
        self.assertEqual(player["active_quests"][0]["difficulty_modifier"], 1)

    def test_final_success_grants_rewards(self):
        player = make_player()
        quest = activate_quest()
        quest["stage_number"] = 3
        quest["stage"] = "3/3"
        player["active_quests"] = [quest]
        success, _message = resolve_test(player, 0, FixedRng(20))
        self.assertTrue(success)
        self.assertEqual(player["gold"], 13)
        self.assertEqual(player["legend"], 2)
        self.assertEqual(len(player["food"]), 3)
        self.assertTrue(player["inventory"])
        self.assertFalse(player["active_quests"])


if __name__ == "__main__":
    unittest.main()
