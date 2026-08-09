from __future__ import annotations

from rg_engine.council_market import CouncilMarketSession, PUBLIC_CATEGORIES

_INSTALLED = False
_ORIGINAL_FINALIZE = CouncilMarketSession.finalize_public_offer


def reviewed_public_categories(session: CouncilMarketSession, player_index: int) -> set[str]:
    state = getattr(session, "_reviewed_public_categories", None)
    if not isinstance(state, dict):
        state = {}
        session._reviewed_public_categories = state
    reviewed = state.setdefault(int(player_index), set())
    return reviewed


def mark_public_category_reviewed(session: CouncilMarketSession, player_index: int, category: str) -> None:
    category = str(category)
    if category in PUBLIC_CATEGORIES:
        reviewed_public_categories(session, player_index).add(category)


def missing_public_categories(session: CouncilMarketSession, player_index: int) -> list[str]:
    reviewed = reviewed_public_categories(session, player_index)
    return [category for category in PUBLIC_CATEGORIES if category not in reviewed]


def _finalize_with_required_review(self, player_index: int, no_offer: bool = False):
    missing = missing_public_categories(self, player_index)
    if missing:
        labels = {
            "quest": "Questy",
            "item": "Przedmioty",
            "helper": "Pomocnicy",
            "good": "Towary",
        }
        names = ", ".join(labels.get(category, category) for category in missing)
        return False, f"Najpierw przejrzyj wszystkie kategorie. Pozostało: {names}."
    return _ORIGINAL_FINALIZE(self, player_index, no_offer=no_offer)


def install_council_market_rules() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    CouncilMarketSession.finalize_public_offer = _finalize_with_required_review
    _INSTALLED = True
