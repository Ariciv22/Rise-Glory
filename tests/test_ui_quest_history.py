import unittest

from rg_ui.quest_history import _history_quests


class QuestHistoryUiTests(unittest.TestCase):
    def test_history_contains_resolved_quests_but_not_active_slots(self):
        hero = {
            "active_quests": [{"id": "active", "name": "Aktywny"}],
            "completed_quests": [{"id": "done", "name": "Ukonczony", "status": "completed"}],
            "failed_quests": [{"id": "failed", "name": "Przegrany", "status": "failed"}],
            "abandoned_quests": [{"id": "left", "name": "Porzucony", "status": "abandoned"}],
        }

        history = _history_quests(hero)

        self.assertEqual([quest["id"] for quest in history], ["done", "failed", "left"])
        self.assertNotIn("active", [quest["id"] for quest in history])
        self.assertEqual(history[0]["_history_status"], "completed")
        self.assertEqual(history[1]["_history_status"], "failed")
        self.assertEqual(history[2]["_history_status"], "abandoned")

    def test_history_keeps_latest_item_first_inside_each_status(self):
        hero = {
            "completed_quests": [
                {"id": "first", "status": "completed"},
                {"id": "second", "status": "completed"},
            ]
        }

        history = _history_quests(hero)

        self.assertEqual([quest["id"] for quest in history], ["second", "first"])


if __name__ == "__main__":
    unittest.main()
