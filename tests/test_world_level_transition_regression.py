from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_world_level_transition_is_installed_as_final_ui_layer():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    transition = source.rindex("install_world_level_transition(_app)")
    location_ui = source.rindex("install_location_ui_refinement()")
    assert transition > location_ui


def test_world_level_transition_is_automatic_and_modal_without_continue_button():
    source = (ROOT / "rg_ui" / "world_level_transition.py").read_text(encoding="utf-8")
    assert "_DURATION_MS = 3200" in source
    assert "Kontynuuj" not in source
    assert "if is_world_level_transition_active():\n            return True" in source
    assert "app_module.TurnManager.end_turn = end_turn_without_transition" in source
    assert "draw_world_level_transition" in source
