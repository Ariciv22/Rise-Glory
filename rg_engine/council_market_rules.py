from __future__ import annotations

import rg_engine.council_market as market
from rg_engine.council import TradeSide
from rg_engine.council_market import CouncilMarketSession, PUBLIC_CATEGORIES
from rg_engine.items import BACKPACK_LIMIT, ensure_equipment_state

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
    # Gracz, który świadomie rezygnuje z publicznej oferty, nie musi otwierać
    # żadnej kategorii. Wymóg przejrzenia kategorii dotyczy wyłącznie gracza,
    # który faktycznie chce zatwierdzić przygotowaną ofertę.
    if no_offer:
        return _ORIGINAL_FINALIZE(self, player_index, no_offer=True)

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
    return _ORIGINAL_FINALIZE(self, player_index, no_offer=False)


def _correct_negotiation_overflow(self: CouncilMarketSession, player_index: int) -> dict[str, int]:
    negotiation = self.negotiation
    if negotiation is None or player_index not in negotiation.participants:
        return {}

    if player_index == negotiation.offer.left_index:
        own_side = negotiation.offer.left
        incoming_side = negotiation.offer.right
        incoming_owner = self.players[negotiation.offer.right_index]
    else:
        own_side = negotiation.offer.right
        incoming_side = negotiation.offer.left
        incoming_owner = self.players[negotiation.offer.left_index]

    incoming = self._preview_side_assets(incoming_side, incoming_owner)
    incoming_counts = market._asset_bundle_counts(incoming)
    reserved = self.reserved_counts(player_index)
    player = self.players[player_index]

    outgoing_quests = sum(1 for asset in own_side.assets if asset.category == "quest")
    outgoing_helpers = sum(1 for asset in own_side.assets if asset.category == "helper")
    outgoing_goods = sum(max(0, int(asset.quantity or 0)) for asset in own_side.assets if asset.category == "good")
    outgoing_inventory_items = sum(
        1 for asset in own_side.assets
        if asset.category == "item" and asset.source == "inventory"
    )

    overflow: dict[str, int] = {}
    quest_final = len(player.get("active_quests", []) or []) - outgoing_quests + reserved.get("quest", 0) + incoming_counts["quest"]
    if quest_final > market.MAX_ACTIVE_QUESTS:
        overflow["quest"] = quest_final - market.MAX_ACTIVE_QUESTS

    helper_final = len(player.get("helpers", []) or []) - outgoing_helpers + reserved.get("helper", 0) + incoming_counts["helper"]
    if helper_final > market.MAX_HELPERS:
        overflow["helper"] = helper_final - market.MAX_HELPERS

    ensure_equipment_state(player)
    item_limit = int(player.get("backpack_limit", BACKPACK_LIMIT) or BACKPACK_LIMIT)
    item_final = len(player.get("inventory", []) or []) - outgoing_inventory_items + reserved.get("item", 0) + incoming_counts["item"]
    if item_final > item_limit:
        overflow["item"] = item_final - item_limit

    raw_goods_limit = player.get("goods_limit")
    if raw_goods_limit not in (None, ""):
        goods_limit = max(0, int(raw_goods_limit or 0))
        goods_final = len(player.get("goods", []) or []) - outgoing_goods + reserved.get("good", 0) + incoming_counts["good"]
        if goods_final > goods_limit:
            overflow["good"] = goods_final - goods_limit
    return overflow


def _correct_validate_discard_plan(player: dict, required: dict[str, int], discard_assets):
    if not required:
        return True, "Brak odrzutów."
    side = TradeSide(list(discard_assets), 0)
    valid, message = market._validate_assets(side, player)
    if not valid:
        return False, message

    counts = {category: 0 for category in PUBLIC_CATEGORIES}
    for asset in discard_assets:
        if asset.category not in counts:
            continue
        if asset.category == "good":
            counts["good"] += max(0, int(asset.quantity or 0))
        elif asset.category == "item":
            # Odrzucenie wyposażonego przedmiotu nie zwalnia miejsca w plecaku.
            if asset.source == "inventory":
                counts["item"] += 1
        else:
            counts[asset.category] += 1

    for category, amount in required.items():
        missing = int(amount) - counts.get(category, 0)
        if missing > 0:
            return False, f"Musisz odrzucić jeszcze {missing} elementów kategorii {category}."
    return True, "Plan odrzutu poprawny."


def install_council_market_rules() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    CouncilMarketSession.finalize_public_offer = _finalize_with_required_review
    CouncilMarketSession.negotiation_overflow = _correct_negotiation_overflow
    market._validate_discard_plan = _correct_validate_discard_plan
    _INSTALLED = True
