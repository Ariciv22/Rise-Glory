from rg_engine.problem_knowledge import (
    investigate_problem,
    problem_investigated,
    problem_knowledge_view,
    problem_methods_for_player,
)
from rg_engine.world_events import (
    DURATION_UNTIL_RESOLVED,
    activate_world_event,
    register_world_event,
    reset_world_event_deck,
)


class Token:
    def __init__(self, actions=4):
        self.actions = actions


def hero(name="Bohater", actions=4):
    return {
        "name": name,
        "stats": {},
        "gold": 0,
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


def threat(event_id="test_threat"):
    return {
        "id": event_id,
        "name": "Zagrożenie testowe",
        "world_level": 1,
        "duration": DURATION_UNTIL_RESOLVED,
        "effect_text": "Droga pozostaje zablokowana.",
        "problem": {
            "description": "Na trakcie pojawił się problem.",
            "condition": "Usuń zagrożenie.",
            "reward": {"gold": 3},
            "methods": [
                {"id": "method_a", "label": "Metoda A", "stat": "Intryga", "difficulty": 11},
                {"id": "method_b", "label": "Metoda B", "stat": "Handel", "difficulty": 13},
            ],
        },
    }


def setup_function():
    reset_world_event_deck()


def activate(event_id="test_threat"):
    definition = threat(event_id)
    register_world_event(definition)
    event, _ = activate_world_event(event_id, [])
    return event


def test_problem_starts_uninvestigated_for_each_hero():
    event = activate()
    first = hero("Pierwszy")
    second = hero("Drugi")

    assert not problem_investigated(first, event)
    assert not problem_investigated(second, event)
    assert problem_methods_for_player(first, event) == []
    assert problem_methods_for_player(second, event) == []


def test_investigation_costs_one_action_and_reveals_methods_only_to_that_hero():
    event = activate()
    first = hero("Pierwszy", actions=4)
    second = hero("Drugi", actions=4)

    success, message = investigate_problem(first, event)

    assert success
    assert "Odkryto" in message
    assert first["_token_ref"].actions == 3
    assert second["_token_ref"].actions == 4
    assert problem_investigated(first, event)
    assert not problem_investigated(second, event)
    assert len(problem_methods_for_player(first, event)) == 2
    assert problem_methods_for_player(second, event) == []


def test_last_action_can_be_spent_on_investigation():
    event = activate()
    player = hero(actions=1)

    success, _ = investigate_problem(player, event)

    assert success
    assert player["_token_ref"].actions == 0
    assert problem_investigated(player, event)


def test_reopening_investigated_problem_is_free():
    event = activate()
    player = hero(actions=3)

    first_success, _ = investigate_problem(player, event)
    actions_after_first = player["_token_ref"].actions
    second_success, message = investigate_problem(player, event)

    assert first_success and second_success
    assert actions_after_first == 2
    assert player["_token_ref"].actions == 2
    assert "już zbadany" in message


def test_hero_without_action_cannot_investigate():
    event = activate()
    player = hero(actions=0)

    success, message = investigate_problem(player, event)

    assert not success
    assert message == "Potrzebujesz 1 akcji, aby zbadać problem."
    assert not problem_investigated(player, event)


def test_knowledge_view_hides_methods_and_reward_before_investigation():
    event = activate()
    player = hero()

    before = problem_knowledge_view(player, event)
    assert before is not None
    assert before["investigated"] is False
    assert before["methods"] == []
    assert before["reward_revealed"] is False

    investigate_problem(player, event)
    after = problem_knowledge_view(player, event)
    assert after is not None
    assert after["investigated"] is True
    assert len(after["methods"]) == 2
    assert after["reward_revealed"] is False
