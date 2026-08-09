import unittest

from rg_engine.council import AssetRef
from rg_engine.council_market import (
    CouncilMarketSession,
    MAX_LOOSE_NEGOTIATIONS,
    council_turn_order,
)
from rg_engine.items import ensure_equipment_state


def hero(name, number, legend=0, gold=20):
    value = {
        "name": name,
        "player_number": number,
        "legend": legend,
        "gold": gold,
        "active_quests": [],
        "completed_quests": [],
        "failed_quests": [],
        "inventory": [],
        "equipment": {},
        "helpers": [],
        "goods": [],
        "backpack_limit": 10,
        "_equipment_migrated": True,
    }
    ensure_equipment_state(value)
    return value


def finish_preparation(session, no_offer_players=()):
    for index in range(len(session.players)):
        session.finalize_public_offer(index, no_offer=index in no_offer_players)


class CouncilMarketTests(unittest.TestCase):
    def test_leader_starts_then_remaining_players_follow_player_number(self):
        players = [
            hero("Gracz 1", 1, legend=4),
            hero("Gracz 2", 2, legend=12),
            hero("Gracz 3", 3, legend=12),
            hero("Gracz 4", 4, legend=2),
        ]
        self.assertEqual(council_turn_order(players), [1, 0, 2, 3])

    def test_tie_between_everyone_starts_with_player_one(self):
        players = [hero(f"Gracz {number}", number, legend=10) for number in range(1, 5)]
        self.assertEqual(council_turn_order(players), [0, 1, 2, 3])

    def test_public_offers_stay_hidden_until_every_player_is_ready(self):
        players = [hero("A", 1), hero("B", 2)]
        players[0]["inventory"].append({"name": "Miecz", "category": "weapon"})
        session = CouncilMarketSession(players)
        session.toggle_public_asset(0, AssetRef("item", "inventory", 0))
        session.set_public_price(0, 5)
        ok, _ = session.finalize_public_offer(0)
        self.assertTrue(ok)
        self.assertEqual(session.public_offer(0).status, "ready")
        self.assertEqual(session.stage, "preparation")
        session.finalize_public_offer(1, no_offer=True)
        self.assertEqual(session.public_offer(0).status, "revealed")
        self.assertEqual(session.stage, "turns")

    def test_public_offer_can_contain_equipped_item_and_unsold_item_returns_to_backpack(self):
        players = [hero("A", 1), hero("B", 2)]
        players[0]["equipment"]["weapon"] = {"name": "Miecz", "category": "weapon", "slot": "weapon"}
        session = CouncilMarketSession(players)
        session.toggle_public_asset(0, AssetRef("item", "equipment", "weapon"))
        session.set_public_price(0, 5)
        session.finalize_public_offer(0)
        self.assertIsNone(players[0]["equipment"]["weapon"])
        session.finalize_public_offer(1, no_offer=True)
        session.skip_public_purchase(session.active_player_index)
        session.end_active_turn(confirm_unused=True)
        session.skip_public_purchase(session.active_player_index)
        session.end_active_turn(confirm_unused=True)
        self.assertEqual(session.stage, "summary")
        self.assertIsNone(players[0]["equipment"]["weapon"])
        self.assertEqual(players[0]["inventory"][0]["name"], "Miecz")

    def test_active_player_can_buy_only_one_public_offer(self):
        players = [hero("A", 1, legend=10), hero("B", 2), hero("C", 3)]
        for seller in (1, 2):
            players[seller]["goods"] = [f"Towar {seller}"]
        session = CouncilMarketSession(players)
        session.finalize_public_offer(0, no_offer=True)
        session.set_public_good_quantity(1, "Towar 1", 1)
        session.set_public_price(1, 3)
        session.finalize_public_offer(1)
        session.set_public_good_quantity(2, "Towar 2", 1)
        session.set_public_price(2, 4)
        session.finalize_public_offer(2)

        self.assertEqual(session.active_player_index, 0)
        ok, _ = session.buy_public_offer(0, 1)
        self.assertTrue(ok)
        self.assertEqual(players[0]["gold"], 17)
        self.assertIn("Towar 1", players[0]["goods"])
        self.assertEqual(session.turn_phase, "loose")

        session.turn_phase = "public"
        ok, message = session.buy_public_offer(0, 2)
        self.assertFalse(ok)
        self.assertIn("maksymalnie jedną", message)

    def test_rejected_invitation_does_not_use_attempt(self):
        players = [hero("A", 1, legend=10), hero("B", 2)]
        session = CouncilMarketSession(players)
        finish_preparation(session, no_offer_players={0, 1})
        session.skip_public_purchase(0)
        session.invite_to_negotiation(1)
        ok, _ = session.respond_to_invitation(1, False)
        self.assertTrue(ok)
        self.assertEqual(session.loose_attempts_used[0], 0)
        self.assertEqual(session.remaining_negotiations(0), MAX_LOOSE_NEGOTIATIONS)

    def test_accepted_invitation_uses_only_initiators_attempt(self):
        players = [hero("A", 1, legend=10), hero("B", 2)]
        session = CouncilMarketSession(players)
        finish_preparation(session, no_offer_players={0, 1})
        session.skip_public_purchase(0)
        session.invite_to_negotiation(1)
        ok, _ = session.respond_to_invitation(1, True)
        self.assertTrue(ok)
        self.assertEqual(session.loose_attempts_used[0], 1)
        self.assertEqual(session.loose_attempts_used[1], 0)

    def test_loose_trade_requires_two_preliminary_and_two_final_acceptances(self):
        players = [hero("A", 1, legend=10), hero("B", 2)]
        players[0]["goods"] = ["Drewno"]
        players[1]["goods"] = ["Żelazo"]
        session = CouncilMarketSession(players)
        finish_preparation(session, no_offer_players={0, 1})
        session.skip_public_purchase(0)
        session.invite_to_negotiation(1)
        session.respond_to_invitation(1, True)
        session.set_negotiation_good_quantity(0, "Drewno", 1)
        session.set_negotiation_good_quantity(1, "Żelazo", 1)

        ok, _ = session.preliminarily_accept(0)
        self.assertTrue(ok)
        self.assertEqual(session.negotiation.state, "open")
        ok, _ = session.preliminarily_accept(1)
        self.assertTrue(ok)
        self.assertEqual(session.negotiation.state, "locked")

        ok, _ = session.definitively_accept(0)
        self.assertTrue(ok)
        self.assertEqual(session.negotiation.state, "locked")
        ok, _ = session.definitively_accept(1)
        self.assertTrue(ok)
        self.assertEqual(session.negotiation.state, "completed")
        self.assertEqual(players[0]["goods"], ["Żelazo"])
        self.assertEqual(players[1]["goods"], ["Drewno"])

    def test_rollback_cancels_all_acceptances_and_reopens_editing(self):
        players = [hero("A", 1, legend=10), hero("B", 2)]
        players[0]["goods"] = ["Drewno"]
        players[1]["goods"] = ["Żelazo"]
        session = CouncilMarketSession(players)
        finish_preparation(session, no_offer_players={0, 1})
        session.skip_public_purchase(0)
        session.invite_to_negotiation(1)
        session.respond_to_invitation(1, True)
        session.set_negotiation_good_quantity(0, "Drewno", 1)
        session.set_negotiation_good_quantity(1, "Żelazo", 1)
        session.preliminarily_accept(0)
        session.preliminarily_accept(1)
        session.definitively_accept(0)
        ok, _ = session.rollback_to_negotiation(1)
        self.assertTrue(ok)
        self.assertEqual(session.negotiation.state, "open")
        self.assertFalse(session.negotiation.preliminary_acceptance)
        self.assertFalse(session.negotiation.final_acceptance)

    def test_open_negotiation_blocks_end_turn(self):
        players = [hero("A", 1, legend=10), hero("B", 2)]
        session = CouncilMarketSession(players)
        finish_preparation(session, no_offer_players={0, 1})
        session.skip_public_purchase(0)
        session.invite_to_negotiation(1)
        session.respond_to_invitation(1, True)
        ok, message = session.end_active_turn(confirm_unused=True)
        self.assertFalse(ok)
        self.assertIn("negocjację", message)

    def test_unused_negotiations_require_explicit_end_turn_confirmation(self):
        players = [hero("A", 1, legend=10), hero("B", 2)]
        session = CouncilMarketSession(players)
        finish_preparation(session, no_offer_players={0, 1})
        session.skip_public_purchase(0)
        ok, message = session.end_active_turn()
        self.assertFalse(ok)
        self.assertIn("Potwierdź", message)
        ok, _ = session.end_active_turn(confirm_unused=True)
        self.assertTrue(ok)
        self.assertEqual(session.active_player_index, 1)

    def test_departure_readiness_is_irreversible_and_closes_after_everyone(self):
        players = [hero("A", 1, legend=10), hero("B", 2)]
        session = CouncilMarketSession(players)
        finish_preparation(session, no_offer_players={0, 1})
        session.skip_public_purchase(0)
        session.end_active_turn(confirm_unused=True)
        session.skip_public_purchase(1)
        session.end_active_turn(confirm_unused=True)
        session.continue_from_summary()
        ok, _ = session.confirm_departure(0)
        self.assertTrue(ok)
        ok, _ = session.confirm_departure(0)
        self.assertFalse(ok)
        ok, action = session.confirm_departure(1)
        self.assertTrue(ok)
        self.assertEqual(action, "close_council")
        self.assertEqual(session.stage, "closed")


if __name__ == "__main__":
    unittest.main()
