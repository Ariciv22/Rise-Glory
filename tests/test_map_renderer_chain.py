from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_fast_map_renderer_is_installed_before_legacy_setup_imports():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    fast_renderer = source.index("install_locked_map_camera()")
    legacy_setup = source.index("install_legacy_module_aliases()")
    background = source.rindex("install_map_background()")
    production = source.rindex("install_production_visuals()")

    assert fast_renderer < legacy_setup < background < production


def test_production_visuals_wrap_current_tile_draw_at_install_time():
    source = (ROOT / "rg_world" / "production_visuals.py").read_text(encoding="utf-8")

    assert "current_tile_draw = world_map.Tile.draw" in source
    assert "_ORIGINAL_TILE_DRAW = world_map.Tile.draw" not in source
    assert "world_map.Tile.draw = tile_draw_with_production" in source


def test_temporary_letter_production_markers_are_removed():
    source = (ROOT / "rg_world" / "production_visuals.py").read_text(encoding="utf-8")

    assert "_MATERIAL_SHORT" not in source
    assert "pygame.draw.circle" not in source
    assert '"Dr"' not in source
    assert '"Sk"' not in source
    assert '"Ag"' not in source


def test_clicking_current_hero_tile_is_rejected_before_movement_cost():
    source = (ROOT / "rg_ui" / "map_ui_regression_fixes.py").read_text(encoding="utf-8")

    assert "if target is self.tile:" in source
    assert "world_map.HeroToken.can_move_to = _can_move_without_spending_action_on_current_tile" in source


def test_scoreboard_text_is_redrawn_inside_dedicated_ui_panels():
    source = (ROOT / "rg_ui" / "map_ui_regression_fixes.py").read_text(encoding="utf-8")

    assert 'font.render("Tabela graczy"' in source
    assert "draw_image_panel(screen, header, 2)" in source
    assert "draw_image_panel(screen, row, 2)" in source
    assert "world_state._draw_hex_actions(" in source


def test_production_hud_reserves_world_event_slot_and_removes_alpha_takeover():
    source = (ROOT / "rg_ui" / "production_hud.py").read_text(encoding="utf-8")

    assert "production_takeover:" not in source
    assert "takeover_placeholder" not in source
    assert "state_rect = _world_state_slot(rect)" in source
    assert "world_state._draw_state_button(screen, small_font, rect)" in source
    assert "action_rect = pygame.Rect(" in source
    assert "state_rect.x - pad - button_w" in source


def test_location_hex_info_gets_quest_button_without_seventh_city_slot():
    source = (ROOT / "rg_ui" / "map_ui_regression_fixes.py").read_text(encoding="utf-8")

    assert "quest_tabs_for_location(hero, location_name)" in source
    assert 'f"QUEST: {quest_name}"' in source
    assert '"enter_selected_location"' in source
    assert "quest_marker_ui._QUEST_PANEL_ID = self.quest_id" in source
    assert "buttons.extend([quest_button, enter_button])" in source


def test_blocked_world_threats_can_be_resolved_from_adjacent_hexes():
    source = (ROOT / "rg_ui" / "threat_adjacent_resolution.py").read_text(encoding="utf-8")
    production = (ROOT / "rg_ui" / "production_hud.py").read_text(encoding="utf-8")

    assert 'str(effect.get("type") or "") != "block_entry"' in source
    assert 'scope in {"marker", "marker_tile", "marker_tiles", "local"}' in source
    assert "tile is origin or not world_map.are_adjacent(origin, tile)" in source
    assert "marker_event_ids_on_tile(tile)" in source
    assert "threat_hex_action_state(player, token, marker_ref)" in source
    assert "world_state._HEX_ACTION_RECTS.append" in source
    assert '"Zablokowany heks obok"' in source
    assert "install_threat_adjacent_resolution()" in production


def test_bottom_hud_tracks_hovered_hex_without_changing_selected_actions():
    source = (ROOT / "rg_ui" / "production_hud.py").read_text(encoding="utf-8")

    assert "def _hovered_map_tile(screen, mouse):" in source
    assert 'map_rect.height = max(0, layout["bottom"].top - map_rect.top)' in source
    assert "tile.contains(mouse, camera)" in source
    assert "display_tile = hovered_tile or selected_tile" in source
    assert "selected_value = potential(selected_tile) if selected_tile is not None else {}" in source
    assert "if can_build and display_tile is selected_tile:" in source
    assert "first_y = rect.y + 16" in source
    assert "second_y = min(" in source
