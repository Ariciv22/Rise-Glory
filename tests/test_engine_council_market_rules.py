from rg_engine.council_market import CouncilMarketSession
from rg_engine.council_market_rules import (
    install_council_market_rules,
    mark_public_category_reviewed,
)


def player():
    return {
        "name": "Gracz",
        "player_number": 1,
        "legend": 0,
        "gold": 10,
        "active_quests": [],
        "inventory": [],
        "equipment": {},
        "helpers": [],
        "goods": [],
        "_equipment_migrated": True,
    }


def setup_module():
    install_council_market_rules()


def test_player_must_review_every_public_offer_category_even_when_offering_nothing():
    session = CouncilMarketSession([player()])
    mark_public_category_reviewed(session, 0, "quest")
    ok, message = session.finalize_public_offer(0, no_offer=True)
    assert not ok
    assert "Przedmioty" in message
    assert "Pomocnicy" in message
    assert "Towary" in message

    for category in ("item", "helper", "good"):
        mark_public_category_reviewed(session, 0, category)
    ok, _message = session.finalize_public_offer(0, no_offer=True)
    assert ok
    assert session.public_offer(0).status == "none"
