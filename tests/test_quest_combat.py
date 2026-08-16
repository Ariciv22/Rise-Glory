import unittest

from rg_ui.combat import clear_combat, get_active_combat, is_combat_active, resolve_combat_round
from rg_legacy.satanic_combat import begin_cursed_soldier_combat, resolve_final_option
from rg_legacy.satanic_forces import activate_quest


class FixedRng:
    def __init__(self, *rolls):
        self.rolls = list(rolls)

    def randint(self, _minimum, _maximum):
        return self.rolls.pop(0)


class LocationTile:
    location = {"name": "Artium"}


class TokenStub:
    def __init__(self, actions=4):
        self.actions = actions
        self.tile = LocationTile()
        self.start_tile = self.tile


def make_player():
    token = TokenStub()
    return {
        "name": "Tester",
        "stats": {"Walka": 4, "Nauka": 5, "Intryga": 2, "Kultura": 2},
        "gold": 5,
        "legend": 0,
        "wounds": 0,
        "food": [],
        "inventory": [],
        "materials": {},
        "helpers": [],
        "active_quests": [],
        "completed_quests": [],
        "failed_quests": [],
        "_token_ref": token,
    }


class QuestCombatTests(unittest.TestCase):
    def tearDown(self):
        clear_combat()

    def _stage_three_player(self):
        player = make_player()
        quest = activate_quest()
        quest["stage_number"] = 3
        quest["stage"] = "3/3"
        player["active_quests"] = [quest]
        return player, quest

    def test_third_stage_has_voluntary_combat_option(self):
        player, quest = self._stage_three_player()
        success, _message = begin_cursed_soldier_combat(player)
        self.assertTrue(success)
        self.assertTrue(is_combat_active())
        self.assertEqual(player["_token_ref"].actions, 3)
        self.assertEqual(quest["status"], "combat")
        self.assertEqual(get_active_combat()["enemy"]["name"], "Przeklęty żołnierz")

    def test_failed_final_test_opens_new_combat_module(self):
        player, quest = self._stage_three_player()
        player["stats"]["Nauka"] = 0
        success, _message = resolve_final_option(player, 0, FixedRng(2))
        self.assertFalse(success)
        self.assertTrue(is_combat_active())
        self.assertEqual(quest["failures"], 1)
        self.assertEqual(quest["status"], "combat")

    def test_victory_completes_quest_and_grants_reward(self):
        player, _quest = self._stage_three_player()
        begin_cursed_soldier_combat(player)
        get_active_combat()["enemy"]["hp"] = 1
        outcome, _message = resolve_combat_round(FixedRng(20))
        self.assertEqual(outcome, "victory")
        self.assertFalse(is_combat_active())
        self.assertFalse(player["active_quests"])
        self.assertEqual(player["legend"], 2)
        self.assertEqual(player["completed_quests"][0]["status"], "completed")

    def test_defeat_adds_one_quest_failure_resets_wounds_and_returns_to_start(self):
        player, _quest = self._stage_three_player()
        token = player["_token_ref"]
        original_start = token.start_tile
        begin_cursed_soldier_combat(player)
        player["wounds"] = 3
        outcome, _message = resolve_combat_round(FixedRng(1, 20))
        self.assertEqual(outcome, "defeat")
        self.assertTrue(player["active_quests"])
        self.assertEqual(player["active_quests"][0]["status"], "active")
        self.assertEqual(player["active_quests"][0]["failures"], 1)
        self.assertFalse(player["failed_quests"])
        self.assertEqual(player["wounds"], 0)
        self.assertIs(token.tile, original_start)


if __name__ == "__main__":
    unittest.main()
