import unittest

from rg_engine.combat import attempt_bribe, create_session, defend, resolve_round, use_item
from rg_engine.heroes import ensure_hero_state


class FixedRng:
    def __init__(self, *rolls):
        self.rolls = list(rolls)

    def randint(self, _minimum, _maximum):
        return self.rolls.pop(0)


def make_player():
    player = {
        "stats": {"Walka": 1, "Intryga": 2},
        "helpers": [],
        "inventory": [],
        "equipment": {},
    }
    ensure_hero_state(player)
    return player


class CombatEngineTests(unittest.TestCase):
    def test_short_sword_increases_hit_and_damage(self):
        player = make_player()
        player["equipment"]["weapon"] = {
            "name": "Krótki miecz",
            "category": "weapon",
            "slot": "weapon",
            "hit_bonus": 1,
            "damage_bonus": 1,
        }
        enemy = {"name": "Cel", "max_hp": 2, "armor_class": 12, "attack_bonus": 0, "damage": 1}
        result = resolve_round(create_session(player, enemy), FixedRng(10))
        self.assertEqual(result["outcome"], "victory")
        self.assertEqual(result["hero_attack"]["damage"], 2)

    def test_enemy_deals_hp_damage_not_wounds(self):
        player = make_player()
        enemy = {"name": "Cel", "max_hp": 10, "armor_class": 99, "attack_bonus": 0, "damage": 2}
        result = resolve_round(create_session(player, enemy), FixedRng(1, 20))
        self.assertEqual(result["outcome"], "ongoing")
        self.assertEqual(player["hp"], 6)
        self.assertEqual(player["wounds"], 0)

    def test_defense_adds_two_kp_for_next_enemy_attack(self):
        player = make_player()
        enemy = {"name": "Cel", "max_hp": 10, "armor_class": 99, "attack_bonus": 0, "damage": 2}
        result = defend(create_session(player, enemy), FixedRng(11))
        self.assertEqual(result["outcome"], "ongoing")
        self.assertEqual(player["hp"], 10)

    def test_nat20_ignores_defense_and_hits_twice(self):
        player = make_player()
        enemy = {"name": "Cel", "max_hp": 10, "armor_class": 99, "attack_bonus": 0, "damage": 2}
        defend(create_session(player, enemy), FixedRng(20))
        self.assertEqual(player["hp"], 6)

    def test_offensive_item_auto_hits_and_goes_to_discard(self):
        player = make_player()
        player["inventory"] = [{
            "name": "Bomba",
            "category": "misc",
            "combat_usable": True,
            "effects": {"damage": 3},
        }]
        enemy = {"name": "Cel", "max_hp": 5, "armor_class": 99, "attack_bonus": 0, "damage": 1}
        session = create_session(player, enemy)
        result = use_item(session, 0, FixedRng(1))
        self.assertEqual(session.enemy["hp"], 2)
        self.assertEqual(result["outcome"], "ongoing")
        self.assertFalse(player["inventory"])
        self.assertEqual(player["discarded_items"][0]["name"], "Bomba")

    def test_bribe_is_separate_escape_action(self):
        player = make_player()
        player["gold"] = 8
        enemy = {"name": "Cel", "max_hp": 5, "armor_class": 10, "escape": {"gold": 5}}
        result = attempt_bribe(create_session(player, enemy), FixedRng())
        self.assertEqual(result["outcome"], "escaped")
        self.assertEqual(player["gold"], 3)


if __name__ == "__main__":
    unittest.main()