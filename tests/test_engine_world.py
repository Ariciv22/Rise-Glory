from rg_engine.world import (
    current_world_level,
    quest_difficulty_from_legend_gap,
    register_players,
    required_ready_players,
    reset_world_progression,
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


def test_world_can_reach_level_three_when_half_of_group_are_level_two():
    players = [
        {"legend": 20},
        {"legend": 10},
        {"legend": 10},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
    ]
    register_players(players)
    assert update_world_level() == 3


def test_world_cannot_reach_level_four_without_half_of_group_on_level_three():
    players = [
        {"legend": 30},
        {"legend": 10},
        {"legend": 10},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
    ]
    register_players(players)
    assert update_world_level() == 3


def test_world_can_continue_immediately_when_each_step_is_ready():
    players = [
        {"legend": 30},
        {"legend": 20},
        {"legend": 20},
        {"legend": 0},
        {"legend": 0},
        {"legend": 0},
    ]
    register_players(players)
    assert update_world_level() == 4


def test_quest_difficulty_adds_two_for_each_level_ahead():
    players = [{"legend": 0}, {"legend": 0}]
    register_players(players)
    assert current_world_level() == 1
    assert quest_difficulty_from_legend_gap({"legend": 0}, 1) == 0
    assert quest_difficulty_from_legend_gap({"legend": 10}, 1) == 2
    assert quest_difficulty_from_legend_gap({"legend": 20}, 1) == 4
    assert quest_difficulty_from_legend_gap({"legend": 30}, 1) == 6
