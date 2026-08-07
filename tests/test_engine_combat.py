import unittest

from rg_engine.combat import create_session, resolve_round


class FixedRng:
    def __init__(self, *rolls):
        self.rolls = list(rolls)

    def randint(self, _minimum, _maximum):
        return self.rolls.pop(0)


class CombatEngineTests(unittest.TestCase):
    def test_short_sword_increases_hit_and_damage(self):
        player = {
            "stats": {"Walka": 1},
            "wounds": 0,
            "helpers": [],
            "inventory": [],
            "equipment": {"weapon": {"name": "Krótki miecz", "category": "weapon", "hit_bonus": 1, "damage_bonus": 1}},
        }
        enemy = {"name": "Cel", "max_hp": 2, "armor_class": 12, "attack_bonus": 0, "wounds": 1}
        session = create_session(player, enemy)
        result = resolve_round(session, FixedRng(10))
        self.assertEqual(result["outcome"], "victory")
        self.assertEqual(result["hero_attack"]["damage"], 2)


if __name__ == "__main__":
    unittest.main()
