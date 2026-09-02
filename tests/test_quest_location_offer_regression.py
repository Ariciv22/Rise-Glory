import random

import rg_content.locations as locations
import rg_engine.quests as quests
from rg_content.quests_final import register_all_quests
from rg_engine.quest_location_bridge import (
    clear_tracked_quest_locations,
    install_quest_location_bridge,
)
from rg_engine.world import register_players, reset_world_progression, update_world_level


def _reset_runtime():
    register_all_quests()
    install_quest_location_bridge()
    quests.reset_quest_deck()
    clear_tracked_quest_locations()
    reset_world_progression(1)
    register_players([])


def test_location_initialization_reserves_only_visible_local_quest_offers():
    _reset_runtime()

    location = {"name": "Elarin", "kind": "village", "number": 1}
    locations.initialize_location(location, random.Random(101))

    offers = list(location.get("quest_offers", []) or [])
    assert offers, "Elarin should receive visible Quest offers on a fresh WL I deck."
    assert len(offers) <= 3

    visible_ids = {str(offer["id"]) for offer in offers}
    assert quests._RESERVED_OFFERS == visible_ids

    for offer in offers:
        definition = quests.quest_definition(str(offer["id"])) or {}
        assert definition.get("board_location") == "Elarin"

    assert location.get("quest_v2_ready") is True
    assert int(location.get("quest_offer_world_level", 0) or 0) == 1


def test_world_advance_immediately_replaces_board_but_keeps_accepted_quests():
    _reset_runtime()

    synthetic_id = "test_wl2_elarin_board_refresh"
    if quests.quest_definition(synthetic_id) is None:
        quests.register_quest(
            {
                "id": synthetic_id,
                "name": "Test WL II",
                "world_level": 2,
                "world_level_min": 2,
                "board_location": "Elarin",
                "required_location": "",
                "unique": False,
                "quest_number": 0,
                "stages": [
                    {
                        "number": 1,
                        "title": "Test",
                        "text": "Test",
                        "options": [],
                    }
                ],
            }
        )

    player = {
        "name": "Lider",
        "legend": 0,
        "active_quests": [
            {"id": "accepted_before_world_change", "status": "active", "started": False}
        ],
    }
    register_players([player, {"name": "Drugi", "legend": 0}])

    location = {"name": "Elarin", "kind": "village", "number": 1}
    locations.initialize_location(location, random.Random(202))
    assert int(location.get("quest_offer_world_level", 0) or 0) == 1
    active_before = list(player["active_quests"])

    player["legend"] = 10
    assert update_world_level() == 2

    assert int(location.get("quest_offer_world_level", 0) or 0) == 2
    assert player["active_quests"] == active_before
    offers = list(location.get("quest_offers", []) or [])
    assert offers
    assert all((quests.quest_definition(str(offer["id"])) or {}).get("world_level") == 2 for offer in offers)
    assert all((quests.quest_definition(str(offer["id"])) or {}).get("board_location") == "Elarin" for offer in offers)
