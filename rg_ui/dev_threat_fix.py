from __future__ import annotations

from rg_content.threats import ROZBOJNICY_ID, register_all_threats
from rg_engine.world_events import DURATION_UNTIL_RESOLVED, activate_world_event, active_world_events


def _spawn_real_robbers(players):
    existing = next(
        (event for event in active_world_events(DURATION_UNTIL_RESOLVED) if event.get("id") == ROZBOJNICY_ID),
        None,
    )
    if existing:
        return existing, "Rozbójnicy na trakcie są już aktywni na mapie."
    register_all_threats()
    activated, message = activate_world_event(ROZBOJNICY_ID, players)
    return activated, message or "Rozbójnicy na trakcie zostali aktywowani."


def install_dev_threat_fix() -> None:
    """DEV przycisk używa prawdziwej karty zamiast osobnego duplikatu Zagrożenia."""
    from rg_ui import dev_menu

    dev_menu.DEV_PROBLEM_ID = ROZBOJNICY_ID
    dev_menu._spawn_dev_problem = _spawn_real_robbers
