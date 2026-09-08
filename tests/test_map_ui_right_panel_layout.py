from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_final_map_ui_moves_hex_info_to_right_panel_and_hides_scoreboard():
    source = (ROOT / "rg_ui" / "quest_hex_info_visibility.py").read_text(encoding="utf-8")
    main = (ROOT / "main.py").read_text(encoding="utf-8")

    assert 'right = game_layout_rects(screen)["right"]' in source
    assert "hex_info_panel.hex_info_panel_rect = right_hex_info_rect" in source
    assert "app_module.hex_info_panel_rect = right_hex_info_rect" in source
    assert "hud._draw_scoreboard = scoreboard_without_table" in source
    assert "world_state._draw_hex_actions(" in source
    assert "find_action_button(controller, \"end_turn\")" in source
    assert main.index("install_production_hud(_app)") < main.index("install_quest_hex_info_visibility(_app)")


def test_world_state_main_overlay_does_not_dim_map():
    source = (ROOT / "rg_ui" / "quest_hex_info_visibility.py").read_text(encoding="utf-8")

    assert "original_shade = world_state._draw_modal_shade" in source
    assert "world_state._draw_modal_shade = lambda _screen: None" in source
    assert "world_state._draw_modal_shade = original_shade" in source
