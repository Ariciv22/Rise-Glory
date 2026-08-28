from rg_engine.dev_quest_tools import (
    add_quest_for_testing,
    clear_active_quests_for_testing,
    developer_quest_rows,
)
from rg_engine.heroes import ensure_hero_state


def test_developer_picker_exposes_exactly_quests_1_to_30():
    rows = developer_quest_rows()
    assert len(rows) == 30
    assert [row["number"] for row in rows] == list(range(1, 31))
    assert all(row["id"] and row["name"] and row["board_location"] for row in rows)


def test_developer_picker_adds_selected_quest_directly():
    hero = ensure_hero_state({})
    success, message = add_quest_for_testing(hero, 29)

    assert success is True
    assert "#29" in message
    assert len(hero["active_quests"]) == 1
    assert hero["active_quests"][0]["quest_number"] == 29
    assert hero["active_quests"][0]["id"] == "wilk_przy_palenisku"

    clear_active_quests_for_testing(hero)


def test_developer_picker_rejects_duplicate_active_quest():
    hero = ensure_hero_state({})
    success, _message = add_quest_for_testing(hero, 7)
    assert success is True

    success, message = add_quest_for_testing(hero, 7)
    assert success is False
    assert "juz aktywny" in message

    clear_active_quests_for_testing(hero)


def test_developer_picker_clear_removes_all_active_quests():
    hero = ensure_hero_state({})
    assert add_quest_for_testing(hero, 24)[0] is True
    assert add_quest_for_testing(hero, 25)[0] is True
    assert add_quest_for_testing(hero, 26)[0] is True
    assert len(hero["active_quests"]) == 3

    count, message = clear_active_quests_for_testing(hero)
    assert count == 3
    assert hero["active_quests"] == []
    assert "3" in message
