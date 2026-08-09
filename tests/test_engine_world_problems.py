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
        "stats": {"Walka": stat, "Intryga": stat},
        "gold": 5,
        "legend": 0,
        "wounds": 0,
        "food": [],
        "goods": [],
        "materials": {},
        "helpers": [],
        "inventory": [],
        "equipment": {},
        "active_quests": [],
        "completed_quests": [],
        "failed_quests": [],
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
            "reward": {"gold": 3, "legend": 1},
            "methods": [
                {
                    "id": "fight",
                    "label": "Zaatakuj obóz",
                    "stat": "Walka",
                    "difficulty": 12,
                    "failure": {"wounds": 1},
                },
                {
                    "id": "trick",
                    "label": "Przechytrz straż",
                    "stat": "Intryga",
                    "difficulty": 10,
                    "failure": {"gold": 2},
                },
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


def test_starting_problem_attempt_immediately_costs_one_action():
    player = hero(actions=4)
    register_players([player])
    event = activate(players=[player])
    session, message = begin_problem_attempt(player, event)
    assert session is not None
    assert player["_token_ref"].actions == 3
    assert "Akcja została zużyta" in message


def test_player_with_no_action_cannot_start_problem():
    player = hero(actions=0)
    register_players([player])
    event = activate(players=[player])
    session, message = begin_problem_attempt(player, event)
    assert session is None
    assert message == "Potrzebujesz 1 akcji, aby podjąć próbę."


def test_failure_blocks_only_that_hero_until_next_turn():
    first = hero("Pierwszy", stat=0)
    second = hero("Drugi", stat=8)
    register_players([first, second])
    event = activate(players=[first, second])

    session, _ = begin_problem_attempt(first, event)
    success, _ = resolve_problem_method(session, 0, FixedRng(2))
    assert not success
    assert problem_retry_blocked(first, event["id"])
    assert not problem_retry_blocked(second, event["id"])

    second_session, _ = begin_problem_attempt(second, event)
    assert second_session is not None

    clear_problem_retry_blocks(first)
    assert not problem_retry_blocked(first, event["id"])


def test_success_resolves_problem_globally_and_grants_same_problem_reward():
    player = hero(stat=10)
    register_players([player])
    event = activate(players=[player])
    session, _ = begin_problem_attempt(player, event)
    success, message = resolve_problem_method(session, 1, FixedRng(10))
    assert success
    assert player["gold"] == 8
    assert player["legend"] == 1
    assert not active_world_events(DURATION_UNTIL_RESOLVED)
    assert world_event_history()[-1]["history_status"] == "resolved"
    assert "Nagroda" in message


def test_failed_method_reveals_and_applies_its_own_consequence():
    player = hero(stat=0)
    register_players([player])
    event = activate(players=[player])
    session, _ = begin_problem_attempt(player, event)
    success, message = resolve_problem_method(session, 1, FixedRng(1))
    assert not success
    assert player["gold"] == 3
    assert "-2 Złota" in message
