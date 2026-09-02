from rg_engine.world import (
    current_world_level,
    quest_difficulty_from_legend_gap,
    register_players,
    register_world_level_change_hook,
    required_ready_players,
    reset_world_progression,
    unregister_world_level_change_hook,
    update_world_level,
)


def setup_function():
    register_players([])
    reset_world_progression(1)


def test_required_ready_players_is_half_rounded_up():
    assert [required_ready_players(value) for value in range(1, 7)] == [1, 1, 2, 2, 3, 3]


def test_leader_alone_can_open_world_level_two():
    players = [
        {"legend": 10},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
    ]
    register_players(players)
    assert update_world_level() == 2


def test_world_level_hook_runs_immediately_on_successful_advance():
    players = [{"legend": 10}, {"legend": 0}]
    register_players(players)
    calls = []

    def on_change(previous, current):
        calls.append((previous, current))

    register_world_level_change_hook(on_change)
    try:
        assert update_world_level() == 2
        assert calls == [(1, 2)]
    finally:
        unregister_world_level_change_hook(on_change)


def test_world_cannot_reach_level_three_without_half_of_group_on_level_two():
    players = [
        {"legend": 20},
        {"legend": 9},
        {"legend": 9},
        {"legend": 9},
        {"legend": 9},
        {"legend": 9},
    ]
    register_players(players)
    assert update_world_level() == 2
    assert update_world_level() == 2


def test_world_reaches_level_three_after_later_legend_change_makes_half_ready():
    players = [
        {"legend": 10},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
    ]
    register_players(players)
    assert update_world_level() == 2

    players[0]["legend"] = 20
    players[1]["legend"] = 10
    players[2]["legend"] = 10
    assert update_world_level() == 3


def test_world_reaches_level_four_only_after_half_group_reaches_level_three():
    players = [
        {"legend": 20},
        {"legend": 10},
        {"legend": 10},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
    ]
    register_players(players)
    assert update_world_level() == 2
    assert update_world_level() == 3

    players[0]["legend"] = 30
    players[1]["legend"] = 20
    players[2]["legend"] = 20
    assert update_world_level() == 4


def test_single_update_never_skips_a_world_level_even_if_later_requirements_are_already_met():
    players = [
        {"legend": 30},
        {"legend": 20},
        {"legend": 20},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
    ]
    register_players(players)
    assert update_world_level() == 2


def test_quest_difficulty_adds_two_for_each_level_ahead():
    players = [{"legend": 0}, {"legend": 0}]
    register_players(players)
    assert current_world_level() == 1
    assert quest_difficulty_from_legend_gap({"legend": 0}, 1) == 0
    assert quest_difficulty_from_legend_gap({"legend": 10}, 1) == 2
    assert quest_difficulty_from_legend_gap({"legend": 20}, 1) == 4
    assert quest_difficulty_from_legend_gap({"legend": 30}, 1) == 6
