from __future__ import annotations

import random
from types import SimpleNamespace

from rg_content.quest_pack_common import LEKKOMYSLNY_ZNACHOR, MINIATUROWY_WEDROWNY_DOM
from rg_content.quest_runtime_ext import miniature_house_available, quest_created_places
from rg_content.quest_special_rewards import miniature_house_targets, teleport_with_miniature_house
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


def test_all_30_final_quests_are_registered_with_stable_numbers():
    assert len(QUESTS) == 30
    for number in range(1, 31):
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
    for _ in range(4):
        quest_id = draw_quest_id(1, rng=rng, location_name="Elarin")
        assert quest_id is not None
        drawn.append(quest_id)
        definition = quest_definition(quest_id)
        assert definition["board_location"] == "Elarin"
    assert set(drawn) == {"dzwon_miedzy_nami", "ostatnia_woda", "miod_wiedzmy", "dom_bez_drzwi"}


def test_new_quests_24_30_cover_seven_different_boards():
    expected = {
        24: "Artium",
        25: "Norven",
        26: "Thalwen",
        27: "Eryndor",
        28: "Lirion",
        29: "Durnhal",
        30: "Elarin",
    }
    for number, location in expected.items():
        definition = next(quest for quest in QUESTS if quest["quest_number"] == number)
        assert definition["board_location"] == location
        assert len(definition["stages"]) >= 3
        assert len(definition["ending_rewards"]) == 3


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


def test_q25_trade_bridge_creates_permanent_place():
    player = ensure_hero_state({"gold": 0, "legend": 0})
    quest = activate_quest("most_bez_wlasciciela")
    player["active_quests"].append(quest)

    complete_quest(player, quest, ending_id="most_handlowy")

    assert player["gold"] == 9
    assert player["legend"] == 3
    assert player["story_flags"]["q25_result"] == "most_handlowy"
    places = quest_created_places([player])
    assert any(place["id"] == "most_handlowy" for place in places)


def test_q29_wolf_can_become_real_companion_reward():
    player = ensure_hero_state({"gold": 0, "legend": 0})
    quest = activate_quest("wilk_przy_palenisku")
    player["active_quests"].append(quest)

    complete_quest(player, quest, ending_id="wilk_towarzysz")

    assert player["gold"] == 7
    assert player["legend"] == 3
    assert player["story_flags"]["q29_result"] == "wilk_towarzysz"
    wolf = next(helper for helper in player["helpers"] if helper.get("id") == "wilk_przy_palenisku")
    assert wolf["stat_bonus"]["Walka"] == 1
    assert wolf["stat_bonus"]["Intryga"] == 1


def test_q30_hidden_warehouse_creates_permanent_place():
    player = ensure_hero_state({"gold": 0, "legend": 0})
    quest = activate_quest("dom_bez_drzwi")
    player["active_quests"].append(quest)

    complete_quest(player, quest, ending_id="ukryty_magazyn")

    assert player["gold"] == 8
    assert player["legend"] == 3
    assert player["story_flags"]["q30_result"] == "ukryty_magazyn"
    places = quest_created_places([player])
    assert any(place["id"] == "ukryty_magazyn" for place in places)


def test_reckless_healer_reduces_healing_cost_by_two_with_floor_one():
    player = ensure_hero_state({"helpers": [LEKKOMYSLNY_ZNACHOR]})
    assert healing_cost_per_wound(player, world_level=1) == 1


def test_q23_miniature_house_is_unique_reward_and_once_per_round_capability():
    player = ensure_hero_state({})
    quest = activate_quest("wedrowny_dom")
    player["active_quests"].append(quest)
    complete_quest(player, quest, ending_id="dom_przeprogramowany")

    assert player["gold"] == 18
    assert player["legend"] == 2
    assert player["story_flags"]["q23_result"] == "dom_przeprogramowany"
    assert miniature_house_available(player, round_number=4) is True


def test_miniature_house_teleports_to_nearest_place_and_requires_choice_on_tie():
    player = ensure_hero_state({})
    add_item(player, MINIATUROWY_WEDROWNY_DOM)

    start = SimpleNamespace(id=1, q=0, r=0, location=None)
    elarin = SimpleNamespace(id=2, q=1, r=0, location={"name": "Elarin", "kind": "village"})
    norven = SimpleNamespace(id=3, q=0, r=1, location={"name": "Norven", "kind": "village"})
    far_city = SimpleNamespace(id=4, q=4, r=0, location={"name": "Lirion", "kind": "city"})
    token = SimpleNamespace(tile=start)
    tiles = [start, elarin, norven, far_city]

    targets = miniature_house_targets(player, token, tiles, round_number=7)
    assert {target["tile_id"] for target in targets} == {2, 3}

    success, message = teleport_with_miniature_house(player, token, tiles, round_number=7)
    assert success is False
    assert "Wybierz cel" in message
    assert token.tile is start

    success, _message = teleport_with_miniature_house(
        player,
        token,
        tiles,
        round_number=7,
        target_tile_id=2,
    )
    assert success is True
    assert token.tile is elarin
    assert miniature_house_available(player, round_number=7) is False
    assert miniature_house_available(player, round_number=8) is True
