import random
import unittest

from rg_dice_animation import (
    DICE_ROLL_DURATION_MS,
    DiceRollAnimation,
    visible_face_numbers,
)


class DiceRollAnimationTests(unittest.TestCase):
    def test_visible_face_numbers_are_unique(self):
        for result in range(1, 21):
            values = visible_face_numbers(result)
            self.assertEqual(values[0], result)
            self.assertEqual(len(values), len(set(values)))
            self.assertTrue(all(1 <= value <= 20 for value in values))

    def test_roll_does_not_finish_before_duration(self):
        animation = DiceRollAnimation()
        self.assertTrue(animation.start(result=13, now_ms=1000, rng=random.Random(7)))

        self.assertIsNone(animation.update(1000 + DICE_ROLL_DURATION_MS - 1))
        self.assertTrue(animation.rolling)
        self.assertEqual(animation.target, 13)

    def test_roll_finishes_once_with_target_result(self):
        animation = DiceRollAnimation()
        animation.start(result=20, now_ms=200, rng=random.Random(9))

        self.assertEqual(animation.update(200 + DICE_ROLL_DURATION_MS), 20)
        self.assertFalse(animation.rolling)
        self.assertIsNone(animation.update(200 + DICE_ROLL_DURATION_MS + 100))
        self.assertEqual(animation.display_value(9999), 20)

    def test_second_start_cannot_replace_active_result(self):
        animation = DiceRollAnimation()
        self.assertTrue(animation.start(result=4, now_ms=0, rng=random.Random(1)))
        self.assertFalse(animation.start(result=18, now_ms=10, rng=random.Random(2)))
        self.assertEqual(animation.target, 4)


if __name__ == "__main__":
    unittest.main()
