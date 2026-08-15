from __future__ import annotations

_INSTALLED = False


def _reset_council_ui_sessions() -> None:
    """Czyści wyłącznie UI/sesję bieżącej Rady, bez resetowania talii Wydarzeń."""
    from rg_ui import council as legacy_council
    from rg_ui import council_flow
    from rg_ui import council_market

    legacy_council._SESSION = None
    council_flow.reset_council_intro_flow()
    council_market.reset_council_market()


def install_dev_council_reset(app_module) -> None:
    """Każde DEV `Otwórz Radę teraz` zaczyna świeżą sesję Rady.

    Jest to wyłącznie ułatwienie testowe. Normalne wejścia do Rady zachowują
    standardowy cykl i nie są przez ten wrapper resetowane.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    original = app_module.handle_dev_action

    def handle_dev_action_with_fresh_council(action, hero, token, players):
        result = original(action, hero, token, players)
        if str(action) == "dev_open_council" and result.get("open_council"):
            _reset_council_ui_sessions()
        return result

    app_module.handle_dev_action = handle_dev_action_with_fresh_council
    _INSTALLED = True
