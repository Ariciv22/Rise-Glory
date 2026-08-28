from __future__ import annotations

import random

from rg_content.quest_pack_common import LEKKOMYSLNY_ZNACHOR, MINIATUROWY_WEDROWNY_DOM
from rg_content.quest_runtime_ext import miniature_house_available, quest_created_places
from rg_content.quests_final import QUESTS, register_all_quests
from rg_engine.heroes import ensure_hero_state, healing_cost_per_wound
from rg_engine.items import add_item
from rg_engine.quests import (
    activate_quest,
    complete_quest,
    create_offer,
    draw_quest_id,
    quest_definition,
    reset_quest_deck,
)


def setup_module(_module):
    register_all_quests()


def test_all_23_final_quests_are_registered_with_stable_numbers():
    assert len(QUESTS) == 23
    for number in range(1, 24):
        matches = [quest for quest in QUESTS if int(quest.get("quest_number", 0)) == number]
        assert len(matches) == 1
        definition = quest_definition(matches[0]["id"])
        assert definition is not None
        assert definition["quest_number"] == number
        assert definition.get("board_location")
        assert definition.get("board_text")
        assert definition.get("issuer")
        assert definition.get("ending_rewards")


def test_elarin_board_draws_only_elarin_quests():
    reset_quest_deck()
    rng = random.Random(1701)
    drawn = []
    for _ in range(3):
        quest_id = draw_quest_id(1, rng=rng, location_name="Elarin")
        assert quest_id is not None
        drawn.append(quest_id)
        definition = quest_definition(quest_id)
        assert definition["board_location"] == "Elarin"
    assert set(drawn) == {"dzwon_miedzy_nami", "ostatnia_woda", "miod_wiedzmy"}


def test_q21_offer_contains_issuer_and_immediate_teren_scene():
    offer = create_offer("kruk_z_pierscieniem")
    assert offer["issuer"] == "Jubiler Teren"
    assert "kruk" in offer["accept_text"].lower()
    assert "blyskot" in offer["accept_text"].lower()


def test_q09_three_channels_reward_sets_result_and_creates_farm_place():
    player = ensure_hero_state({"gold": 0, "legend": 0})
    quest = activate_quest("ostatnia_woda")
    player["active_quests"].append(quest)

    complete_quest(player, quest, ending_id="trzy_kanaly")

    assert player["gold"] == 7
    assert player["legend"] == 2
    assert player["story_flags"]["q09_result"] == "trzy_kanaly"
    places = quest_created_places([player])
    assert any(place["id"] == "folwark_elarin" for place in places)


def test_reckless_healer_reduces_healing_cost_by_two_with_floor_one():
    player = ensure_hero_state({"helpers": [LEKKOMYSLNY_ZNACHOR]})
    assert healing_cost_per_wound(player, world_level=1) == 1


def test_q23_miniature_house_is_unique_reward_and_once_per_round_capability():
    player = ensure_hero_state({})
    add_item(player, MINIATUROWY_WEDROWNY_DOM)
    assert miniature_house_available(player, round_number=4) is True

    quest = activate_quest("wedrowny_dom")
    player["active_quests"].append(quest)
    complete_quest(player, quest, ending_id="dom_przeprogramowany")

    assert player["gold"] == 18
    assert player["legend"] == 2
    assert player["story_flags"]["q23_result"] == "dom_przeprogramowany"
