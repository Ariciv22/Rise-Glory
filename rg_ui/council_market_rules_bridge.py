from __future__ import annotations

from rg_engine.council_market_rules import install_council_market_rules, mark_public_category_reviewed
from rg_ui import council_market as market_ui
from rg_ui.council_market_presenter import draw_council as _draw_presented_council

install_council_market_rules()

_ORIGINAL_SET_PREP_CATEGORY = market_ui._set_prep_category
_ORIGINAL_CONFIRM_DEPARTURE = market_ui._confirm_departure


def _tracked_set_prep_category(category):
    session = market_ui._SESSION
    if session is not None and session.stage == "preparation":
        player_index = market_ui._current_preparation_player(session)
        if player_index is not None:
            mark_public_category_reviewed(session, player_index, category)
    _ORIGINAL_SET_PREP_CATEGORY(category)


def _confirm_departure_and_reset(session, player_index):
    result = _ORIGINAL_CONFIRM_DEPARTURE(session, player_index)
    if result == "close_council":
        from rg_ui import council as legacy_council
        from rg_ui import council_flow

        legacy_council._SESSION = None
        council_flow.reset_council_intro_flow()
    return result


market_ui._set_prep_category = _tracked_set_prep_category
market_ui._confirm_departure = _confirm_departure_and_reset


def draw_council(screen, title_font, font, small_font, mouse, round_number):
    session = market_ui._session(round_number)
    if session.stage == "preparation":
        player_index = market_ui._current_preparation_player(session)
        if player_index is not None:
            mark_public_category_reviewed(session, player_index, market_ui._PREP_CATEGORY)
    return _draw_presented_council(screen, title_font, font, small_font, mouse, round_number)
