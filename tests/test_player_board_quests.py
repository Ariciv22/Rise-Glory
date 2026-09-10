import unittest
from pathlib import Path

import pygame

from rg_ui.player_board import (
    _quest_row_rects,
    close_player_board,
    close_quest_details,
    get_open_quest_index,
    open_player_board,
    open_quest_details,
    player_board_layout,
)


ROOT = Path(__file__).resolve().parents[1]


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

    def test_layout_exposes_all_future_asset_slots_and_hitbox_regions(self):
        board = pygame.Rect(0, 0, 1600, 941)
        layout = player_board_layout(board)

        self.assertEqual(len(layout["equipment_slots"]), 8)
        self.assertEqual(len(layout["helper_slots"]), 5)
        self.assertEqual(len(layout["backpack_slots"]), 15)
        self.assertEqual(len(layout["legend_cells"]), 35)
        self.assertEqual(len(layout["quest_rows"]), 3)
        self.assertEqual(set(layout["quest_tabs"]), {"active", "history"})
        self.assertEqual(set(layout["quest_pagination"]), {"prev", "page", "next"})

        rects = [
            layout["close"],
            layout["identity"],
            layout["attributes"],
            layout["wounds"],
            layout["gold"],
            layout["legend"],
            layout["portrait"],
            layout["equipment"],
            layout["helpers"],
            layout["backpack"],
            layout["materials"],
            layout["food"],
            layout["quest_area"],
            *layout["equipment_slots"],
            *layout["helper_slots"],
            *layout["backpack_slots"],
            *layout["quest_rows"],
            *layout["quest_tabs"].values(),
            *layout["quest_pagination"].values(),
        ]
        self.assertTrue(all(board.contains(rect) for rect in rects))

    def test_active_quest_hitboxes_come_from_shared_layout(self):
        board = pygame.Rect(0, 0, 1600, 941)
        hero = {"active_quests": [{"name": "A"}, {"name": "B"}]}
        self.assertEqual(_quest_row_rects(board, hero), player_board_layout(board)["quest_rows"][:2])

    def test_related_board_layers_use_shared_layout_contract(self):
        history_source = (ROOT / "rg_ui" / "quest_history.py").read_text(encoding="utf-8")
        figure_source = (ROOT / "rg_ui" / "hero_figure_system.py").read_text(encoding="utf-8")

        self.assertIn('layout = player_board.player_board_layout(board)', history_source)
        self.assertIn('target = player_board.player_board_layout(board)["portrait"]', figure_source)


if __name__ == "__main__":
    unittest.main()
