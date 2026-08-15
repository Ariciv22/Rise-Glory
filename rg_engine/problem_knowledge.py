from __future__ import annotations

import copy
from typing import Any

from rg_engine.world_events import DURATION_UNTIL_RESOLVED, active_world_events

PROBLEM_INVESTIGATION_ACTION_COST = 1


def _event_id(event_or_id: dict[str, Any] | str) -> str:
    if isinstance(event_or_id, dict):
        return str(event_or_id.get("id") or "")
    return str(event_or_id or "")


def _active_problem(event_or_id: dict[str, Any] | str) -> dict[str, Any] | None:
    event_id = _event_id(event_or_id)
    if not event_id:
        return None
    for event in active_world_events(DURATION_UNTIL_RESOLVED):
        if _event_id(event) == event_id:
            return event
    return None


def _investigated_problem_ids(player: dict[str, Any]) -> set[str]:
    raw = player.setdefault("_investigated_problems", set())
    if isinstance(raw, set):
        return raw
    normalised = {str(value) for value in (raw or []) if str(value)}
    player["_investigated_problems"] = normalised
    return normalised


def problem_investigated(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> bool:
    """Zwraca stan wiedzy konkretnego bohatera o aktywnym Zagrożeniu."""
    event_id = _event_id(event_or_id)
    if not event_id or _active_problem(event_id) is None:
        return False
    return event_id in _investigated_problem_ids(player)


def can_investigate_problem(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> tuple[bool, str]:
    """Sprawdza, czy bohater może użyć akcji „Zbadaj problem”."""
    event = _active_problem(event_or_id)
    if event is None:
        return False, "Ten problem nie jest już aktywny."

    event_id = _event_id(event)
    if event_id in _investigated_problem_ids(player):
        return True, "Problem został już zbadany przez tego bohatera."

    token = player.get("_token_ref")
    actions = int(getattr(token, "actions", 0) or 0) if token is not None else 0
    if actions < PROBLEM_INVESTIGATION_ACTION_COST:
        return False, "Potrzebujesz 1 akcji, aby zbadać problem."

    return True, ""


def investigate_problem(player: dict[str, Any], event_or_id: dict[str, Any] | str) -> tuple[bool, str]:
    """Automatycznie bada Zagrożenie i zapisuje wiedzę wyłącznie temu bohaterowi.

    Pierwsze badanie kosztuje 1 Akcję i zawsze kończy się powodzeniem. Ponowne
    otwarcie już zbadanego problemu nie kosztuje Akcji.
    """
    event = _active_problem(event_or_id)
    if event is None:
        return False, "Ten problem nie jest już aktywny."

    event_id = _event_id(event)
    investigated = _investigated_problem_ids(player)
    if event_id in investigated:
        return True, "Problem został już zbadany przez tego bohatera."

    allowed, message = can_investigate_problem(player, event)
    if not allowed:
        return False, message

    token = player.get("_token_ref")
    token.actions = max(0, int(token.actions) - PROBLEM_INVESTIGATION_ACTION_COST)
    investigated.add(event_id)
    return True, "Problem zbadany. Odkryto dostępne sposoby rozwiązania."


def problem_methods_for_player(
    player: dict[str, Any],
    event_or_id: dict[str, Any] | str,
) -> list[dict[str, Any]]:
    """Udostępnia metody tylko bohaterowi, który sam zbadał Zagrożenie."""
    event = _active_problem(event_or_id)
    if event is None or not problem_investigated(player, event):
        return []

    problem = event.get("problem") or {}
    if not isinstance(problem, dict):
        return []
    methods = problem.get("methods") or []
    return [copy.deepcopy(method) for method in methods if isinstance(method, dict)]


def problem_knowledge_view(
    player: dict[str, Any],
    event_or_id: dict[str, Any] | str,
) -> dict[str, Any] | None:
    """Buduje bezpieczny widok Zagrożenia z perspektywy jednego bohatera.

    Publiczne dane są dostępne każdemu. Metody, DC i wymagania pojawiają się
    dopiero po osobistym zbadaniu problemu przez tego bohatera. Nagroda pozostaje
    ukryta na tym etapie zgodnie z zasadami modułu 01.
    """
    event = _active_problem(event_or_id)
    if event is None:
        return None

    problem = event.get("problem") or {}
    if not isinstance(problem, dict):
        problem = {}
    investigated = problem_investigated(player, event)

    return {
        "id": _event_id(event),
        "name": str(event.get("name") or "Problem"),
        "description": str(problem.get("description") or event.get("description") or ""),
        "effect": str(event.get("effect_text") or ""),
        "condition": str(problem.get("condition") or "Rozwiąż problem na wskazanym heksie."),
        "investigated": investigated,
        "methods": problem_methods_for_player(player, event) if investigated else [],
        "reward_revealed": False,
    }


def clear_problem_knowledge(player: dict[str, Any], event_or_id: dict[str, Any] | str | None = None) -> None:
    """Czyści wiedzę bohatera o jednym Zagrożeniu albo o wszystkich Zagrożeniach."""
    if event_or_id is None:
        player["_investigated_problems"] = set()
        return
    event_id = _event_id(event_or_id)
    _investigated_problem_ids(player).discard(event_id)
