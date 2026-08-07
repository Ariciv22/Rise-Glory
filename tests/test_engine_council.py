import unittest

from rg_engine.council import (
    AssetRef,
    CouncilUsage,
    TradeOffer,
    abandon_quest,
    execute_trade,
    validate_trade,
)
from rg_engine.items import ensure_equipment_state


def player(name, gold=20):
    hero = {
        "name": name,
        "gold": gold,
        "active_quests": [],
        "completed_quests": [],
        "failed_quests": [],
        "inventory": [],
        "equipment": {},
        "helpers": [],
        "goods": [],
        "_equipment_migrated": True,
    }
    ensure_equipment_state(hero)
    return hero


def accepted(offer):
    offer.accepted_left = True
    offer.accepted_right = True
    return offer


class CouncilTradeTests(unittest.TestCase):
    def test_quest_sale_uses_fixed_world_price(self):
        players = [player("A"), player("B")]
        players[0]["active_quests"].append({"name": "Wilki", "status": "active"})
        usage = CouncilUsage.for_players(players)
        offer = TradeOffer(0, 1)
        offer.left.assets.append(AssetRef("quest", "active_quests", 0))
        offer.right.gold = 4

        ok, _ = validate_trade(offer, players, usage, world_level=2)
        self.assertTrue(ok)
        success, _ = execute_trade(accepted(offer), players, usage, world_level=2)
        self.assertTrue(success)
        self.assertEqual(players[0]["gold"], 24)
        self.assertEqual(players[1]["gold"], 16)
        self.assertEqual(players[1]["active_quests"][0]["name"], "Wilki")

    def test_wrong_quest_price_is_rejected(self):
        players = [player("A"), player("B")]
        players[0]["active_quests"].append({"name": "Wilki", "status": "active"})
        offer = TradeOffer(0, 1)
        offer.left.assets.append(AssetRef("quest", "active_quests", 0))
        offer.right.gold = 3

        ok, message = validate_trade(offer, players, CouncilUsage.for_players(players), world_level=2)
        self.assertFalse(ok)
        self.assertIn("4", message)

    def test_quest_for_quest_needs_no_gold(self):
        players = [player("A"), player("B")]
        players[0]["active_quests"].append({"name": "Wilki", "status": "active"})
        players[1]["active_quests"].append({"name": "Kronika", "status": "active"})
        offer = TradeOffer(0, 1)
        offer.left.assets.append(AssetRef("quest", "active_quests", 0))
        offer.right.assets.append(AssetRef("quest", "active_quests", 0))
        success, _ = execute_trade(accepted(offer), players, CouncilUsage.for_players(players), world_level=1)
        self.assertTrue(success)
        self.assertEqual(players[0]["active_quests"][0]["name"], "Kronika")
        self.assertEqual(players[1]["active_quests"][0]["name"], "Wilki")

    def test_two_quest_limit_applies_to_both_participants(self):
        players = [player("A"), player("B")]
        players[0]["active_quests"] = [
            {"name": "Q1", "status": "active"},
            {"name": "Q2", "status": "active"},
        ]
        usage = CouncilUsage.for_players(players)
        offer = TradeOffer(0, 1)
        offer.left.assets.extend([
            AssetRef("quest", "active_quests", 0),
            AssetRef("quest", "active_quests", 1),
        ])
        offer.right.gold = 4
        success, _ = execute_trade(accepted(offer), players, usage, world_level=1)
        self.assertTrue(success)
        self.assertEqual(usage.used(0, "quest"), 2)
        self.assertEqual(usage.used(1, "quest"), 2)

        players[0]["active_quests"].append({"name": "Q3", "status": "active"})
        second = TradeOffer(0, 1)
        second.left.assets.append(AssetRef("quest", "active_quests", 0))
        second.right.gold = 2
        ok, _ = validate_trade(second, players, usage, world_level=1)
        self.assertFalse(ok)

    def test_goods_allow_any_quantity_but_only_two_goods_transactions(self):
        players = [player("A"), player("B")]
        players[0]["goods"] = ["Jedwab"] * 9
        usage = CouncilUsage.for_players(players)

        for quantity in (5, 3):
            offer = TradeOffer(0, 1)
            offer.left.assets.append(AssetRef("good", "goods", "Jedwab", quantity))
            offer.right.gold = 1
            success, _ = execute_trade(accepted(offer), players, usage, world_level=1)
            self.assertTrue(success)

        self.assertEqual(usage.used(0, "good"), 2)
        self.assertEqual(usage.used(1, "good"), 2)
        self.assertEqual(players[1]["goods"].count("Jedwab"), 8)

        third = TradeOffer(0, 1)
        third.left.assets.append(AssetRef("good", "goods", "Jedwab", 1))
        third.right.gold = 1
        ok, _ = validate_trade(third, players, usage, world_level=1)
        self.assertFalse(ok)

    def test_equipped_item_can_be_traded_and_goes_to_backpack(self):
        players = [player("A"), player("B")]
        players[0]["equipment"]["weapon"] = {
            "id": "miecz",
            "name": "Miecz",
            "category": "weapon",
            "slot": "weapon",
            "price": 6,
        }
        usage = CouncilUsage.for_players(players)
        offer = TradeOffer(0, 1)
        offer.left.assets.append(AssetRef("item", "equipment", "weapon"))
        offer.right.gold = 3
        success, _ = execute_trade(accepted(offer), players, usage, world_level=1)
        self.assertTrue(success)
        self.assertIsNone(players[0]["equipment"]["weapon"])
        self.assertEqual(players[1]["inventory"][0]["name"], "Miecz")

    def test_full_backpack_blocks_incoming_item(self):
        players = [player("A"), player("B")]
        players[0]["inventory"].append({"name": "Miecz", "category": "weapon"})
        players[1]["inventory"] = [{"name": f"Rzecz {i}", "category": "misc"} for i in range(10)]
        offer = TradeOffer(0, 1)
        offer.left.assets.append(AssetRef("item", "inventory", 0))
        offer.right.gold = 2
        ok, message = validate_trade(offer, players, CouncilUsage.for_players(players), world_level=1)
        self.assertFalse(ok)
        self.assertIn("plecaku", message)

    def test_abandon_moves_quest_to_failed_history(self):
        hero = player("A")
        hero["active_quests"].append({"name": "Stary quest", "status": "active"})
        success, _ = abandon_quest(hero, 0)
        self.assertTrue(success)
        self.assertFalse(hero["active_quests"])
        self.assertEqual(hero["failed_quests"][0]["status"], "failed")
        self.assertEqual(hero["failed_quests"][0]["stage"], "Porzucony")


if __name__ == "__main__":
    unittest.main()
