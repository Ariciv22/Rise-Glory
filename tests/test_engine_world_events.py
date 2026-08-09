import random

from rg_content.world_events import WORLD_EVENTS, register_all_world_events
from rg_engine.world_events import (
    DURATION_UNTIL_NEXT_COUNCIL,
    activate_world_event,
    active_world_events,
    draw_next_world_event,
    expire_until_next_council,
    healing_cost_with_world_event,
    movement_cost_with_world_event,
    price_with_world_event,
    register_world_event,
    registered_world_events,
    reset_world_event_deck,
    world_event_history,
)


def setup_function():
    register_all_world_events()
    reset_world_event_deck()


def test_registered_world_event_deck_has_five_level_one_cards():
    assert len(WORLD_EVENTS) == 5
    assert len(registered_world_events(1)) >= 5


def test_first_five_draws_do_not_repeat():
    players = [{"gold": 10, "food": []}]
    rng = random.Random(12345)
    drawn = [draw_next_world_event(players, rng, world_level=1)[0]["id"] for _ in range(5)]
    assert len(set(drawn)) == 5


def test_draw_uses_only_requested_world_level():
    register_world_event(
        {
            "id": "test_poziom_2",
            "name": "Test poziomu 2",
            "world_level": 2,
            "duration": "instant",
        }
    )
    rng = random.Random(2)
    event, _message = draw_next_world_event([], rng, world_level=2)
    assert event["id"] == "test_poziom_2"
    assert event["world_level"] == 2


def test_abundant_harvest_adds_two_food_to_every_player():
    players = [{"food": []}, {"food": ["Ser"]}]
    activate_world_event("obfite_zbiory", players)
    assert players[0]["food"] == ["Bochenek chleba", "Bochenek chleba"]
    assert players[1]["food"][-2:] == ["Bochenek chleba", "Bochenek chleba"]


def test_royal_tax_never_creates_negative_gold():
    players = [{"gold": 1}, {"gold": 5}]
    activate_world_event("krolewski_podatek", players)
    assert players[0]["gold"] == 0
    assert players[1]["gold"] == 3


def test_great_fair_reduces_market_price_by_one_with_minimum_one():
    activate_world_event("wielki_jarmark", [])
    assert price_with_world_event(6) == 5
    assert price_with_world_event(1) == 1
    assert price_with_world_event(0) == 0


def test_dangerous_routes_increase_only_difficult_terrain_cost():
    activate_world_event("niebezpieczne_szlaki", [])
    assert movement_cost_with_world_event(1) == 1
    assert movement_cost_with_world_event(2) == 3


def test_healers_day_reduces_healing_cost_with_minimum_one():
    activate_world_event("dzien_uzdrowicieli", [])
    assert healing_cost_with_world_event(2) == 1
    assert healing_cost_with_world_event(1) == 1


def test_multiple_active_events_stack_their_modifiers():
    activate_world_event("wielki_jarmark", [])
    register_world_event(
        {
            "id": "drugi_jarmark_testowy",
            "name": "Drugi jarmark",
            "world_level": 1,
            "duration": DURATION_UNTIL_NEXT_COUNCIL,
            "modifiers": {"market_price_modifier": -1},
        }
    )
    activate_world_event("drugi_jarmark_testowy", [])
    assert price_with_world_event(6) == 4
    assert len(active_world_events()) == 2


def test_until_next_council_events_expire_and_enter_history():
    activate_world_event("wielki_jarmark", [])
    assert active_world_events(DURATION_UNTIL_NEXT_COUNCIL)
    expire_until_next_council()
    assert not active_world_events(DURATION_UNTIL_NEXT_COUNCIL)
    history = world_event_history()
    assert history[-1]["id"] == "wielki_jarmark"
    assert history[-1]["history_status"] == "expired"
