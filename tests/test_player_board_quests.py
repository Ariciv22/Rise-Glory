import unittest

import pygame

from rg_player_board import (
    _quest_row_rects,
    close_player_board,
    close_quest_details,
    get_open_quest_index,
    open_player_board,
    open_quest_details,
)


class PlayerBoardQuestInteractionTests(unittest.TestCase):
    def tearDown(self):
        close_quest_details()
        close_player_board()

    def test_quest_details_state_can_be_opened_and_closed(self):
        open_player_board()
        self.assertTrue(open_quest_details(1))
        self.assertEqual(get_open_quest_index(), 1)
        self.assertTrue(close_quest_details())
        self.assertIsNone(get_open_quest_index())

    def test_closing_board_also_closes_quest_details(self):
        open_player_board()
        open_quest_details(0)
        close_player_board()
        self.assertIsNone(get_open_quest_index())

    def test_invalid_quest_index_is_rejected(self):
        self.assertFalse(open_quest_details(-1))
        self.assertFalse(open_quest_details("bad"))
        self.assertIsNone(get_open_quest_index())

    def test_rows_cover_each_active_quest_without_overlap(self):
        board = pygame.Rect(0, 0, 1600, 941)
        hero = {"active_quests": [{"name": "A"}, {"name": "B"}, {"name": "C"}]}
        rows = _quest_row_rects(board, hero)

        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row.width > 100 and row.height > 20 for row in rows))
        self.assertLessEqual(rows[0].bottom, rows[1].top)
        self.assertLessEqual(rows[1].bottom, rows[2].top)


if __name__ == "__main__":
    unittest.main()
