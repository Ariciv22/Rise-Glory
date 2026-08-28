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


def test_production_marker_fonts_are_cached():
    source = (ROOT / "rg_world" / "production_visuals.py").read_text(encoding="utf-8")

    assert "_FONT_CACHE" in source
    assert "def _marker_font" in source
