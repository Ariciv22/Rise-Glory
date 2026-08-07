import unittest

from rg_engine.devtools import (
    add_gold,
    apply_runtime_dev_flags,
    change_legend,
    dev_flag,
    reset_devtools,
    set_legend,
    toggle_dev_flag,
)
from rg_engine.heroes import apply_wounds
from rg_engine.world import (
    clear_forced_world_level,
    current_world_level,
    set_forced_world_level,
)


class DummyToken:
    def __init__(self, actions=0):
        self.actions = actions


class DeveloperToolsTests(unittest.TestCase):
    def setUp(self):
        reset_devtools()
        clear_forced_world_level()

    def tearDown(self):
        reset_devtools()
        clear_forced_world_level()

    def test_legend_controls_follow_normal_world_thresholds(self):
        hero = {"legend": 0}
        players = [hero]
        self.assertEqual(current_world_level(players), 1)
        change_legend(hero, 10)
        self.assertEqual(hero["legend"], 10)
        self.assertEqual(current_world_level(players), 2)
        set_legend(hero, 30)
        self.assertEqual(current_world_level(players), 4)
        change_legend(hero, -100)
        self.assertEqual(hero["legend"], 0)

    def test_forced_world_level_can_be_enabled_and_disabled(self):
        players = [{"legend": 0}]
        self.assertEqual(current_world_level(players), 1)
        set_forced_world_level(3)
        self.assertEqual(current_world_level(players), 3)
        clear_forced_world_level()
        self.assertEqual(current_world_level(players), 1)

    def test_runtime_flags_restore_testing_resources(self):
        hero = {"gold": 2, "wounds": 3}
        token = DummyToken(actions=0)
        toggle_dev_flag("infinite_actions")
        toggle_dev_flag("infinite_gold")
        toggle_dev_flag("no_wounds")
        apply_runtime_dev_flags(hero, token, 3)
        self.assertEqual(token.actions, 3)
        self.assertGreaterEqual(hero["gold"], 999)
        self.assertEqual(hero["wounds"], 0)

    def test_no_wounds_blocks_combat_wounds(self):
        hero = {"wounds": 0}
        toggle_dev_flag("no_wounds")
        added, defeated = apply_wounds(hero, 4)
        self.assertEqual(added, 0)
        self.assertFalse(defeated)
        self.assertEqual(hero["wounds"], 0)

    def test_reset_disables_every_toggle(self):
        for name in ("infinite_actions", "infinite_gold", "no_wounds", "council_every_round"):
            toggle_dev_flag(name)
            self.assertTrue(dev_flag(name))
        reset_devtools()
        for name in ("infinite_actions", "infinite_gold", "no_wounds", "council_every_round"):
            self.assertFalse(dev_flag(name))

    def test_add_gold_never_goes_below_zero(self):
        hero = {"gold": 5}
        add_gold(hero, -20)
        self.assertEqual(hero["gold"], 0)


if __name__ == "__main__":
    unittest.main()
