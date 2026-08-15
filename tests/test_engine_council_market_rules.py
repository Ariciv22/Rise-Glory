from rg_engine.council import AssetRef
import rg_engine.council_market as market
from rg_engine.council_market import CouncilMarketSession
from rg_engine.council_market_rules import (
    install_council_market_rules,
    mark_public_category_reviewed,
)
from rg_engine.items import ensure_equipment_state


def player():
    value = {
        "name": "Gracz",
        "player_number": 1,
        "legend": 0,
        "gold": 10,
        "active_quests": [],
        "inventory": [],
        "equipment": {},
        "helpers": [],
        "goods": [],
        "backpack_limit": 10,
        "_equipment_migrated": True,
    }
    ensure_equipment_state(value)
    return value


def setup_module():
    install_council_market_rules()


def review_all(session, player_index):
    for category in ("quest", "item", "helper", "good"):
        mark_public_category_reviewed(session, player_index, category)


def test_player_can_skip_public_offer_without_reviewing_categories():
    session = CouncilMarketSession([player()])

    ok, message = session.finalize_public_offer(0, no_offer=True)

    assert ok
    assert "nie wystawia" in message.lower()
    assert session.public_offer(0).status == "none"
    assert session.stage == "turns"


def test_player_with_real_offer_still_reviews_every_public_category():
    hero = player()
    hero["goods"] = ["Lina"]
    session = CouncilMarketSession([hero])
    session.set_public_good_quantity(0, "Lina", 1)

    ok, message = session.finalize_public_offer(0)

    assert not ok
    assert "Najpierw przejrzyj wszystkie kategorie" in message

    review_all(session, 0)
    ok, _message = session.finalize_public_offer(0)
    assert ok
    assert session.public_offer(0).status == "revealed"


def test_item_given_away_in_same_loose_trade_frees_backpack_space_first():
    first = player()
    second = player()
    first["name"] = "A"
    second["name"] = "B"
    second["player_number"] = 2
    first["legend"] = 10
    first["inventory"] = [{"name": f"A{i}", "category": "misc"} for i in range(10)]
    second["inventory"] = [{"name": f"B{i}", "category": "misc"} for i in range(10)]
    ensure_equipment_state(first)
    ensure_equipment_state(second)

    session = CouncilMarketSession([first, second])
    session.finalize_public_offer(0, no_offer=True)
    session.finalize_public_offer(1, no_offer=True)
    session.skip_public_purchase(0)
    session.invite_to_negotiation(1)
    session.respond_to_invitation(1, True)
    session.toggle_negotiation_asset(0, AssetRef("item", "inventory", 0))
    session.toggle_negotiation_asset(1, AssetRef("item", "inventory", 0))

    assert session.negotiation_overflow(0) == {}
    assert session.negotiation_overflow(1) == {}


def test_discarding_equipped_item_does_not_fake_free_backpack_slot():
    hero = player()
    hero["inventory"] = [{"name": f"Rzecz {i}", "category": "misc"} for i in range(10)]
    hero["equipment"]["weapon"] = {"name": "Miecz", "category": "weapon", "slot": "weapon"}
    ensure_equipment_state(hero)

    ok, message = market._validate_discard_plan(
        hero,
        {"item": 1},
        [AssetRef("item", "equipment", "weapon")],
    )
    assert not ok
    assert "item" in message
