import pygame

from rg_ui import map_step1_layout as layout


def setup_function():
    layout.set_scoreboard_open(False)


def test_scoreboard_toggle_is_explicit_and_reversible():
    assert layout.is_scoreboard_open() is False
    assert layout.toggle_scoreboard() is True
    assert layout.is_scoreboard_open() is True
    assert layout.toggle_scoreboard() is False
    assert layout.is_scoreboard_open() is False


def test_right_content_rect_stays_inside_right_hud():
    screen = pygame.Surface((1600, 900))
    right = layout.game_layout_rects(screen)["right"]
    content = layout._right_content_rect(screen)
    assert right.contains(content)
    assert content.width < right.width
    assert content.bottom < right.bottom


def test_world_state_overlay_temporarily_disables_only_background_shade(monkeypatch):
    calls = []

    def shade(_screen):
        calls.append("shade")

    def overlay(screen, font, small_font):
        layout.world_state._draw_modal_shade(screen)
        return "ok"

    monkeypatch.setattr(layout.world_state, "_draw_modal_shade", shade)
    monkeypatch.setattr(layout, "_ORIGINAL_WORLD_STATE_OVERLAY", overlay)

    assert layout.draw_world_state_without_map_shade(None, None, None) == "ok"
    assert calls == []
    layout.world_state._draw_modal_shade(None)
    assert calls == ["shade"]
