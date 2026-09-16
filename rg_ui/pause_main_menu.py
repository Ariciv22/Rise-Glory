from __future__ import annotations

import pygame


_INSTALLED = False
_ORIGINAL_APP_MAIN = None
_ORIGINAL_PAUSE_LAYOUT = None
_ORIGINAL_DRAW_PAUSE_OVERLAY = None
_ORIGINAL_HANDLE_PAUSE_EVENT = None


class ReturnToMainMenu(RuntimeError):
    """Sterowany powrot z aktywnej rozgrywki do glownego menu."""


def _cleanup_runtime_state(base) -> None:
    """Czyści nakładki sesji zanim uruchomimy świeże menu główne."""
    try:
        base.stop_map_music_queue()
    except Exception:
        pass

    try:
        from rg_ui import player_board

        player_board.close_player_board()
    except Exception:
        pass

    try:
        from rg_ui import player_board_items

        player_board_items.close_item_details()
    except Exception:
        pass

    try:
        pygame.key.stop_text_input()
    except pygame.error:
        pass


def _pause_layout_with_main_menu(base):
    if base._PAUSE_OPTIONS_OPEN:
        return _ORIGINAL_PAUSE_LAYOUT()

    screen = pygame.display.get_surface()
    if screen is None:
        return {}

    sw, sh = screen.get_size()
    panel_w = min(520, max(390, sw - 80))
    panel_h = min(460, max(410, sh - 80))
    panel = pygame.Rect((sw - panel_w) // 2, (sh - panel_h) // 2, panel_w, panel_h)
    button_w = min(340, panel_w - 80)
    button_h = 58
    button_x = panel.centerx - button_w // 2

    return {
        "panel": panel,
        "resume": pygame.Rect(button_x, panel.y + 145, button_w, button_h),
        "options": pygame.Rect(button_x, panel.y + 215, button_w, button_h),
        "main_menu": pygame.Rect(button_x, panel.y + 285, button_w, button_h),
    }


def _draw_pause_overlay_with_main_menu(base):
    _ORIGINAL_DRAW_PAUSE_OVERLAY()

    if not base._PAUSE_MENU_OPEN or base._PAUSE_OPTIONS_OPEN:
        return

    screen = pygame.display.get_surface()
    if screen is None:
        return

    layout = base._pause_layout()
    main_menu = layout.get("main_menu")
    if main_menu is None:
        return

    base._draw_pause_button(
        screen,
        main_menu,
        "MENU GŁÓWNE",
        pygame.mouse.get_pos(),
    )


def _handle_pause_event_with_main_menu(base, event):
    if (
        not base._PAUSE_OPTIONS_OPEN
        and event.type == pygame.MOUSEBUTTONUP
        and event.button == 1
    ):
        layout = base._pause_layout()
        main_menu = layout.get("main_menu")
        if main_menu is not None and main_menu.collidepoint(event.pos):
            _cleanup_runtime_state(base)
            raise ReturnToMainMenu()

    return _ORIGINAL_HANDLE_PAUSE_EVENT(event)


def _wrap_app_main(app_module, base) -> None:
    global _ORIGINAL_APP_MAIN

    if getattr(app_module.main, "_rise_glory_pause_main_menu_wrapper", False):
        return

    _ORIGINAL_APP_MAIN = app_module.main

    def main_with_return_to_menu():
        skip_start_intro = False

        while True:
            original_start_intro_count = app_module.start_intro_count
            if skip_start_intro:
                app_module.start_intro_count = lambda: 0

            try:
                return _ORIGINAL_APP_MAIN()
            except ReturnToMainMenu:
                _cleanup_runtime_state(base)
                skip_start_intro = True
                try:
                    pygame.event.clear()
                except pygame.error:
                    pass
                continue
            finally:
                app_module.start_intro_count = original_start_intro_count

    main_with_return_to_menu._rise_glory_pause_main_menu_wrapper = True
    app_module.main = main_with_return_to_menu


def install_pause_main_menu(app_module) -> None:
    global _INSTALLED
    global _ORIGINAL_PAUSE_LAYOUT, _ORIGINAL_DRAW_PAUSE_OVERLAY, _ORIGINAL_HANDLE_PAUSE_EVENT

    if _INSTALLED:
        return

    from rg_ui import start_intro_base as base

    _ORIGINAL_PAUSE_LAYOUT = base._pause_layout
    _ORIGINAL_DRAW_PAUSE_OVERLAY = base._draw_pause_overlay
    _ORIGINAL_HANDLE_PAUSE_EVENT = base._handle_pause_event

    base._pause_layout = lambda: _pause_layout_with_main_menu(base)
    base._draw_pause_overlay = lambda: _draw_pause_overlay_with_main_menu(base)
    base._handle_pause_event = lambda event: _handle_pause_event_with_main_menu(base, event)

    _wrap_app_main(app_module, base)
    _INSTALLED = True
