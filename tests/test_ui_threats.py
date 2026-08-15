from rg_engine.problem_knowledge import investigate_problem
from rg_engine.world_events import (
    DURATION_UNTIL_RESOLVED,
    activate_world_event,
    register_world_event,
    reset_world_event_deck,
)
from rg_ui.threats import threat_hex_action_state


class Token:
    def __init__(self, actions=4):
        self.actions = actions


def hero(actions=4):
    token = Token(actions)
    player = {
        "name": "Bohater",
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
        "_token_ref": token,
    }
    return player, token


def threat(event_id="ui_threat"):
    return {
        "id": event_id,
        "name": "Problem testowy",
        "world_level": 1,
        "duration": DURATION_UNTIL_RESOLVED,
        "effect_text": "Problem działa.",
        "problem": {
            "action_label": "Usuń problem",
            "methods": [
                {"id": "a", "label": "A", "stat": "Intryga", "difficulty": 10},
                {"id": "b", "label": "B", "stat": "Handel", "difficulty": 10},
            ],
        },
    }


def setup_function():
    reset_world_event_deck()


def activate(event_id="ui_threat"):
    definition = threat(event_id)
    register_world_event(definition)
    event, _ = activate_world_event(event_id, [])
    return event


def test_hex_action_is_investigate_before_hero_knows_problem():
    event = activate()
    player, token = hero(actions=2)

    state = threat_hex_action_state(player, token, event["id"])

    assert state["investigated"] is False
    assert state["label"] == "Zbadaj problem"
    assert state["enabled"] is True


def test_hex_action_changes_to_problem_action_after_investigation():
    event = activate()
    player, token = hero(actions=2)
    investigate_problem(player, event)

    state = threat_hex_action_state(player, token, event["id"])

    assert state["investigated"] is True
    assert state["label"] == "Usuń problem"
    assert state["enabled"] is True


def test_no_action_message_depends_on_investigation_state():
    event = activate()
    player, token = hero(actions=0)

    before = threat_hex_action_state(player, token, event["id"])
    assert before["enabled"] is False
    assert before["reason"] == "Potrzebujesz 1 akcji, aby zbadać problem."

    player["_investigated_problems"] = {event["id"]}
    after = threat_hex_action_state(player, token, event["id"])
    assert after["enabled"] is False
    assert after["reason"] == "Potrzebujesz 1 akcji, aby podjąć próbę."
