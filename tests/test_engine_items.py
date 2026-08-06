import unittest

from rg_engine.items import armor_class, equip_inventory_item, ensure_equipment_state, normalise_item, weapon_bonuses


class ItemEngineTests(unittest.TestCase):
    def test_starting_equipment_is_migrated_once(self):
        hero = {
            "basic_item": "Prosty miecz",
            "class_item": "Skorzana zbroja",
            "inventory": [],
        }
        ensure_equipment_state(hero)
        ensure_equipment_state(hero)
        self.assertEqual(hero["equipment"]["weapon"]["name"], "Prosty miecz")
        self.assertEqual(hero["equipment"]["armor"]["name"], "Skorzana zbroja")
        self.assertEqual(hero["inventory"], [])
        self.assertEqual(armor_class(hero), 12)

    def test_short_sword_can_be_equipped_and_grants_bonuses(self):
        hero = {"inventory": [normalise_item("Krótki miecz")], "equipment": {}}
        success, _message = equip_inventory_item(hero, 0)
        self.assertTrue(success)
        self.assertEqual(weapon_bonuses(hero), (1, 1))


if __name__ == "__main__":
    unittest.main()
