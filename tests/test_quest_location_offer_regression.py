import random

import rg_content.locations as locations
import rg_engine.quests as quests
from rg_content.quests_final import register_all_quests
from rg_engine.quest_location_bridge import install_quest_location_bridge


def test_location_initialization_reserves_only_visible_local_quest_offers():
    register_all_quests()
    install_quest_location_bridge()
    quests.reset_quest_deck()

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
