from __future__ import annotations


_INSTALLED = False


def install_quest_hex_info_visibility(app_module=None) -> None:
    """Ukrywa panel informacji o heksie pod modalami Questa.

    Panel heksa jest elementem mapy i nie powinien przebijac sie nad pelnoekranowy
    modal Questa. Po zamknieciu modala zaznaczony heks pozostaje bez zmian, wiec
    panel automatycznie pojawia sie ponownie przy kolejnym renderze.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    from rg_ui import hex_info_panel
    from rg_ui.quest_markers import is_quest_marker_modal_open

    original_draw_hex_info_panel = hex_info_panel.draw_hex_info_panel

    def draw_hex_info_panel_with_quest_visibility(
        screen,
        font,
        small_font,
        hero,
        token,
        selected_tile,
        mouse_pos,
    ):
        if is_quest_marker_modal_open():
            return []
        return original_draw_hex_info_panel(
            screen,
            font,
            small_font,
            hero,
            token,
            selected_tile,
            mouse_pos,
        )

    hex_info_panel.draw_hex_info_panel = draw_hex_info_panel_with_quest_visibility
    if app_module is not None:
        app_module.draw_hex_info_panel = draw_hex_info_panel_with_quest_visibility

    _INSTALLED = True
