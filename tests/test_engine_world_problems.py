from rg_engine.problem_knowledge import investigate_problem
from rg_engine.threats import failure_revealed, method_state
from rg_engine.world import register_players, reset_world_progression
from rg_engine.world_events import (
    DURATION_UNTIL_RESOLVED,
    activate_world_event,
    active_world_events,
    register_world_event,
    reset_world_event_deck,
    world_event_history,
)
from rg_engine.world_problems import (
    begin_problem_attempt,
    clear_problem_retry_blocks,
    problem_retry_blocked,
    resolve_problem_method,
)


class FixedRng:
    def __init__(self, value):
        self.value = value

    def randint(self, _minimum, _maximum):
        return self.value


class Token:
    def __init__(self, actions=4):
        self.actions = actions


def hero(name="Bohater", stat=0, actions=4):
    return {
        "name": name,
        "player_number": 1 if name == "Bohater" else None,
        "stats": {"Walka": stat, "Handel": stat, "Intryga": stat, "Dyplomacja": stat, "Kultura": stat, "Nauka": stat},
        "gold": 5,
        "legend": 0,
        "wounds": 0,
        "food": [],
        "goods": [],
        "materials": {},
        "helpers": [],
        "inventory": [],
        "equipment": {},
        "_token_ref": Token(actions),
    }


def problem_event(event_id="test_problem"):
    return {
        "id": event_id,
        "name": "Rozbójnicy testowi",
        "world_level": 1,
        "duration": DURATION_UNTIL_RESOLVED,
        "effect_text": "Szlak pozostaje niebezpieczny.",
        "problem": {
            "description": "Na trakcie działa grupa rozbójników.",
            "condition": "Pokonaj lub przechytrz rozbójników.",
            "effects": [{"type": "modifier", "name": "market_price_modifier", "amount": 1}],
            "reward": {"gold": 3, "legend": 1},
            "methods": [
                {"id": "fight", "label": "Zaatakuj obóz", "stat": "Walka", "difficulty": 12, "failure": {"wounds": 1}},
                {"id": "trick", "label": "Przechytrz straż", "stat": "Intryga", "difficulty": 10, "failure": {"gold": 2}},
            ],
        },
    }


def setup_function():
    reset_world_event_deck()
    reset_world_progression(1)


def activate(event_id="test_problem", players=None):
    event = problem_event(event_id)
    register_world_event(event)
    activate_world_event(event_id, players or [])
    return active_world_events(DURATION_UNTIL_RESOLVED)[-1]


def test_cannot_start_problem_attempt_before_investigation():
    player = hero(actions=4)
    register_players([player])
    event = activate(players=[player])
    session, message = begin_problem_attempt(player, event)
    assert session is None
    assert player["_token_ref"].actions == 4
    assert message == "Najpierw zbadaj problem."


def test_investigation_costs_action_but_opening_methods_is_free():
    player = hero(actions=4)
    register_players([player])
    event = activate(players=[player])
    investigated, _ = investigate_problem(player, event)
    session, message = begin_problem_attempt(player, event)
    assert investigated and session is not None
    assert player["_token_ref"].actions == 3
    assert "Podgląd metod jest darmowy" in message
    resolve_problem_method(session, 1, FixedRng(20))
    assert player["_token_ref"].actions == 2


def test_zero_actions_after_investigation_can_view_but_not_execute_method():
    player = hero(actions=1)
    register_players([player])
    event = activate(players=[player])
    investigate_problem(player, event)
    session, _ = begin_problem_attempt(player, event)
    assert session is not None
    state = method_state(player, event, session.methods[0])
    assert state["available"] is False
    assert "Brak 1 Akcji" in state["missing"]
    success, message = resolve_problem_method(session, 0, FixedRng(20))
    assert success is False
    assert "Brak 1 Akcji" in message


def test_failure_blocks_only_that_hero_until_next_turn_and_reveals_consequence():
    first = hero("Pierwszy", stat=0)
    first["player_number"] = 1
    second = hero("Drugi", stat=8)
    second["player_number"] = 2
    register_players([first, second])
    event = activate(players=[first, second])
    investigate_problem(first, event)
    investigate_problem(second, event)
    session, _ = begin_problem_attempt(first, event)
    success, _ = resolve_problem_method(session, 0, FixedRng(2))
    assert not success
    assert problem_retry_blocked(first, event["id"])
    assert not problem_retry_blocked(second, event["id"])
    assert failure_revealed(event, "fight")
    clear_problem_retry_blocks(first)
    assert not problem_retry_blocked(first, event["id"])


def test_success_resolves_problem_and_records_resolution_details():
    player = hero(stat=10)
    register_players([player])
    event = activate(players=[player])
    investigate_problem(player, event)
    session, _ = begin_problem_attempt(player, event)
    success, message = resolve_problem_method(session, 1, FixedRng(10))
    assert success
    assert player["gold"] == 8
    assert player["legend"] == 1
    assert not active_world_events(DURATION_UNTIL_RESOLVED)
    history = world_event_history()[-1]
    assert history["history_status"] == "resolved"
    assert history["resolution"]["hero"] == player["name"]
    assert history["resolution"]["method_id"] == "trick"
    assert "Nagroda" in message


def test_failed_method_applies_own_consequence_and_keeps_problem_active():
    player = hero(stat=0)
    register_players([player])
    event = activate(players=[player])
    investigate_problem(player, event)
    session, _ = begin_problem_attempt(player, event)
    success, message = resolve_problem_method(session, 1, FixedRng(1))
    assert not success
    assert player["gold"] == 3
    assert active_world_events(DURATION_UNTIL_RESOLVED)
    assert "-2 Złota" in message


def test_problem_wounds_use_normal_hero_cap():
    player = hero(stat=0)
    player["wounds"] = 3
    register_players([player])
    definition = problem_event("problem_rany_limit")
    definition["problem"]["methods"][0]["failure"] = {"wounds": 3}
    register_world_event(definition)
    activate_world_event(definition["id"], [player])
    event = active_world_events(DURATION_UNTIL_RESOLVED)[-1]
    investigate_problem(player, event)
    session, _ = begin_problem_attempt(player, event)
    success, message = resolve_problem_method(session, 0, FixedRng(1))
    assert not success
    assert player["wounds"] == 4
    assert "+1 Ran" in message
