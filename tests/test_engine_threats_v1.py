from rg_engine.problem_knowledge import investigate_problem, problem_knowledge_view
from rg_engine.threats import (
    finish_problem_combat,
    is_interaction_blocked,
    is_tile_entry_blocked,
    method_state,
    set_problem_combat_launcher,
    threat_display_number,
    threat_modifier,
)
from rg_engine.world import register_players, reset_world_progression
from rg_engine.world_chronicle import world_chronicle_entries
from rg_engine.world_events import (
    DURATION_UNTIL_RESOLVED,
    activate_world_event,
    active_world_events,
    price_with_world_event,
    register_world_event,
    reset_world_event_deck,
)
from rg_engine.world_problems import begin_problem_attempt, resolve_problem_method
from rg_world.world_event_markers import (
    bind_world_tiles,
    can_place_problem_markers,
    marker_event_ids_on_tile,
    sync_problem_markers,
)


class FixedRng:
    def __init__(self, value):
        self.value = value

    def randint(self, _minimum, _maximum):
        return self.value

    def shuffle(self, values):
        return None

    def choice(self, values):
        return values[0]


class Token:
    def __init__(self, actions=4):
        self.actions = actions


class Tile:
    def __init__(self, tile_id, terrain_key="plains", passable=True):
        self.id = tile_id
        self.terrain_key = terrain_key
        self.terrain = {"passable": passable, "move": 1}
        self.location = None
        self.world_event_markers = []


def hero(name, number, actions=4):
    return {
        "name": name,
        "player_number": number,
        "stats": {"Walka": 4, "Handel": 4, "Intryga": 4, "Dyplomacja": 4, "Kultura": 4, "Nauka": 4},
        "gold": 10,
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


def base_threat(event_id, methods, *, marker_count=1, effects=None, reward=None, placement=None, fallback=None):
    return {
        "id": event_id,
        "name": event_id,
        "world_level": 1,
        "duration": DURATION_UNTIL_RESOLVED,
        "effect_text": "Aktywny negatywny efekt.",
        "problem": {
            "description": "Problem testowy.",
            "condition": "Rozwiąż problem.",
            "marker_count": marker_count,
            "placement": placement or {"type": "random_passable"},
            "fallback": fallback,
            "effects": effects or [{"type": "modifier", "name": "test_modifier", "amount": -1}],
            "reward": reward or {},
            "methods": methods,
        },
    }


def activate(definition, players):
    register_world_event(definition)
    activate_world_event(definition["id"], players)
    return active_world_events(DURATION_UNTIL_RESOLVED)[-1]


def setup_function():
    reset_world_event_deck()
    reset_world_progression(1)
    register_players([])
    bind_world_tiles([])
    set_problem_combat_launcher(None)


def test_missing_requirement_is_visible_but_method_cannot_spend_action():
    player = hero("A", 1)
    register_players([player])
    event = activate(
        base_threat(
            "req",
            [
                {"id": "rope", "label": "Lina", "stat": "Intryga", "difficulty": 10, "requirements": {"goods": "Lina"}},
                {"id": "other", "label": "Inna", "stat": "Handel", "difficulty": 10},
            ],
        ),
        [player],
    )
    investigate_problem(player, event)
    session, _ = begin_problem_attempt(player, event)
    before = player["_token_ref"].actions
    state = method_state(player, event, session.methods[0])
    assert not state["available"]
    assert any("Lina" in missing for missing in state["missing"])
    success, _ = resolve_problem_method(session, 0, FixedRng(20))
    assert not success
    assert player["_token_ref"].actions == before


def test_consumed_costs_are_paid_at_attempt_start_even_on_failure():
    player = hero("A", 1)
    register_players([player])
    event = activate(
        base_threat(
            "cost",
            [
                {"id": "bribe", "label": "Przekup", "stat": "Handel", "difficulty": 99, "costs": {"gold": 3}},
                {"id": "other", "label": "Inna", "stat": "Nauka", "difficulty": 99},
            ],
        ),
        [player],
    )
    investigate_problem(player, event)
    session, _ = begin_problem_attempt(player, event)
    success, _ = resolve_problem_method(session, 0, FixedRng(1))
    assert not success
    assert player["gold"] == 7
    assert player["_token_ref"].actions == 2


def test_automatic_method_spends_resources_and_succeeds_without_roll():
    player = hero("A", 1)
    player["materials"] = {"Drewno": 2, "Żelazo": 1}
    register_players([player])
    event = activate(
        base_threat(
            "automatic",
            [
                {
                    "id": "repair",
                    "label": "Napraw",
                    "mode": "automatic",
                    "requirements": {"materials": {"Drewno": 2, "Żelazo": 1}},
                    "costs": {"materials": {"Drewno": 2, "Żelazo": 1}},
                },
                {"id": "other", "label": "Inna", "stat": "Nauka", "difficulty": 20},
            ],
        ),
        [player],
    )
    investigate_problem(player, event)
    session, _ = begin_problem_attempt(player, event)
    success, _ = resolve_problem_method(session, 0)
    assert success
    assert session.roll is None
    assert player["materials"].get("Drewno", 0) == 0
    assert player["materials"].get("Żelazo", 0) == 0


def test_all_six_stats_are_legal_for_threat_tests():
    player = hero("A", 1)
    register_players([player])
    stats = ["Walka", "Handel", "Intryga", "Dyplomacja", "Kultura", "Nauka"]
    methods = [{"id": stat, "label": stat, "stat": stat, "difficulty": 10} for stat in stats]
    event = activate(base_threat("six_stats", methods), [player])
    investigate_problem(player, event)
    view = problem_knowledge_view(player, event)
    assert [method["availability"]["stat"] for method in view["methods"]] == stats
    assert all(method["availability"]["available"] for method in view["methods"])


def test_failure_is_revealed_to_other_hero_only_after_they_investigate():
    first = hero("A", 1)
    second = hero("B", 2)
    register_players([first, second])
    event = activate(
        base_threat(
            "failure_knowledge",
            [
                {"id": "risky", "label": "Ryzyko", "stat": "Intryga", "difficulty": 99, "failure": {"gold": 1}, "failure_text": "Tracisz złoto."},
                {"id": "other", "label": "Inna", "stat": "Nauka", "difficulty": 99},
            ],
        ),
        [first, second],
    )
    investigate_problem(first, event)
    session, _ = begin_problem_attempt(first, event)
    resolve_problem_method(session, 0, FixedRng(1))
    assert problem_knowledge_view(second, event)["methods"] == []
    investigate_problem(second, event)
    state = problem_knowledge_view(second, event)["methods"][0]["availability"]
    assert state["failure_revealed"] is True
    assert state["failure"]["gold"] == 1


def test_combat_method_uses_launcher_and_one_action_for_whole_combat():
    player = hero("A", 1)
    register_players([player])
    event = activate(
        base_threat(
            "combat_threat",
            [
                {"id": "fight", "label": "Walcz", "mode": "combat", "enemy": {"name": "Wróg"}},
                {"id": "other", "label": "Inna", "stat": "Nauka", "difficulty": 20},
            ],
        ),
        [player],
    )
    investigate_problem(player, event)
    session, _ = begin_problem_attempt(player, event)
    calls = []

    def launcher(pending_session, index, method):
        calls.append((pending_session, index, method["id"]))
        return True, "Walka rozpoczęta."

    set_problem_combat_launcher(launcher)
    success, message = resolve_problem_method(session, 0)
    assert not success
    assert session.combat_pending
    assert player["_token_ref"].actions == 2
    assert calls and "Walka" in message
    success, _ = finish_problem_combat(session, True, "Wróg pokonany.")
    assert success
    assert not active_world_events(DURATION_UNTIL_RESOLVED)


def test_multi_marker_threat_resolves_locally_and_rewards_all_contributors():
    first = hero("A", 1)
    second = hero("B", 2)
    first["gold"] = second["gold"] = 0
    register_players([first, second])
    tiles = [Tile(1), Tile(2), Tile(3)]
    bind_world_tiles(tiles)
    event = activate(
        base_threat(
            "multi",
            [
                {"id": "auto", "label": "Usuń", "mode": "automatic"},
                {"id": "test", "label": "Test", "stat": "Nauka", "difficulty": 10},
            ],
            marker_count=2,
            effects=[{"type": "block_entry", "scope": "marker_tiles"}],
            reward={"gold": 2},
        ),
        [first, second],
    )
    placed = sync_problem_markers(FixedRng(1))
    assert len(placed) == 2
    refs = sorted(ref for ref, _tile_id in placed)
    tile_by_ref = {ref: tile_id for ref, tile_id in placed}
    assert tile_by_ref[refs[0]] != tile_by_ref[refs[1]]
    assert threat_display_number(event) > 0

    investigate_problem(first, event)
    session, _ = begin_problem_attempt(first, refs[0])
    success, _ = resolve_problem_method(session, 0)
    assert success
    assert active_world_events(DURATION_UNTIL_RESOLVED)
    assert is_tile_entry_blocked(tile_by_ref[refs[0]])[0] is False
    assert is_tile_entry_blocked(tile_by_ref[refs[1]])[0] is True

    investigate_problem(second, event)
    session, _ = begin_problem_attempt(second, refs[1])
    success, _ = resolve_problem_method(session, 0)
    assert success
    assert not active_world_events(DURATION_UNTIL_RESOLVED)
    assert first["gold"] == 2
    assert second["gold"] == 2
    chronicle = world_chronicle_entries()
    assert chronicle and chronicle[-1]["event_id"] == "multi"


def test_marker_placement_uses_fallback_for_whole_multi_marker_group():
    tiles = [Tile(1, "plains"), Tile(2, "plains"), Tile(3, "plains")]
    bind_world_tiles(tiles)
    definition = base_threat(
        "fallback_multi",
        [
            {"id": "a", "label": "A", "mode": "automatic"},
            {"id": "b", "label": "B", "mode": "automatic"},
        ],
        marker_count=2,
        placement={"type": "terrain", "terrain": "mountain"},
        fallback={"type": "terrain", "terrain": "plains"},
    )
    assert can_place_problem_markers(definition)
    player = hero("A", 1)
    register_players([player])
    activate(definition, [player])
    placed = sync_problem_markers(FixedRng(1))
    assert len(placed) == 2
    assert len({tile_id for _ref, tile_id in placed}) == 2
    assert sum(len(marker_event_ids_on_tile(tile)) for tile in tiles) == 2


def test_local_interaction_block_disappears_after_its_marker_is_resolved():
    player = hero("A", 1)
    register_players([player])
    tile = Tile(7, "forest")
    bind_world_tiles([tile])
    event = activate(
        base_threat(
            "wood_block",
            [
                {"id": "auto", "label": "Usuń", "mode": "automatic"},
                {"id": "test", "label": "Test", "stat": "Nauka", "difficulty": 10},
            ],
            effects=[{"type": "block_interaction", "interaction": "wood_production", "scope": "marker_tiles"}],
            placement={"type": "terrain", "terrain": "forest"},
        ),
        [player],
    )
    placed = sync_problem_markers(FixedRng(1))
    ref, tile_id = placed[0]
    assert is_interaction_blocked("wood_production", tile_id)[0]
    investigate_problem(player, event)
    session, _ = begin_problem_attempt(player, ref)
    resolve_problem_method(session, 0)
    assert not is_interaction_blocked("wood_production", tile_id)[0]


def test_threat_modifiers_stack_and_can_reduce_price_to_zero():
    methods = [
        {"id": "a", "label": "A", "mode": "automatic"},
        {"id": "b", "label": "B", "mode": "automatic"},
    ]
    first = base_threat("discount_1", methods, effects=[{"type": "modifier", "name": "market_price_modifier", "amount": -1, "scope": "global"}])
    second = base_threat("discount_2", methods, effects=[{"type": "modifier", "name": "market_price_modifier", "amount": -2, "scope": "global"}])
    activate(first, [])
    activate(second, [])
    assert threat_modifier("market_price_modifier") == -3
    assert price_with_world_event(2) == 0
