from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

TRADE_CATEGORIES = ("quest", "item", "helper", "good")


@dataclass
class TradeOffer:
    seller_index: int
    buyer_index: int
    category: str
    offered: Any
    requested_gold: int = 0
    requested: Any = None
    accepted_by_seller: bool = False
    accepted_by_buyer: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def accepted(self) -> bool:
        return self.accepted_by_seller and self.accepted_by_buyer


def validate_trade(offer: TradeOffer, players: list[dict], used_categories: dict[int, set[str]] | None = None) -> tuple[bool, str]:
    if offer.category not in TRADE_CATEGORIES:
        return False, "Nieprawidlowa kategoria transakcji."
    if offer.seller_index == offer.buyer_index:
        return False, "Nie mozna handlowac z samym soba."
    if not 0 <= offer.seller_index < len(players) or not 0 <= offer.buyer_index < len(players):
        return False, "Nieprawidlowy uczestnik transakcji."
    if int(offer.requested_gold or 0) < 0:
        return False, "Cena nie moze byc ujemna."
    if not offer.requested_gold and offer.requested is None:
        return False, "Transakcja nie moze byc darmowym przekazaniem."
    if used_categories and offer.category in used_categories.get(offer.seller_index, set()):
        return False, "Sprzedajacy wykorzystal juz ten limit kategorii podczas Rady."
    return True, "Transakcja jest poprawna."


def _collection_for(player: dict, category: str):
    return {
        "quest": player.setdefault("active_quests", []),
        "item": player.setdefault("inventory", []),
        "helper": player.setdefault("helpers", []),
        "good": player.setdefault("goods", []),
    }[category]


def execute_trade(offer: TradeOffer, players: list[dict], used_categories: dict[int, set[str]] | None = None) -> tuple[bool, str]:
    valid, message = validate_trade(offer, players, used_categories)
    if not valid:
        return False, message
    if not offer.accepted:
        return False, "Obie strony musza zaakceptowac transakcje."
    seller = players[offer.seller_index]
    buyer = players[offer.buyer_index]
    seller_collection = _collection_for(seller, offer.category)
    if offer.offered not in seller_collection:
        return False, "Sprzedajacy nie posiada oferowanego elementu."
    price = int(offer.requested_gold or 0)
    if int(buyer.get("gold", 0) or 0) < price:
        return False, "Kupujacy nie ma wystarczajacej liczby monet."

    seller_collection.remove(offer.offered)
    _collection_for(buyer, offer.category).append(copy.deepcopy(offer.offered))
    buyer["gold"] = int(buyer.get("gold", 0) or 0) - price
    seller["gold"] = int(seller.get("gold", 0) or 0) + price
    if used_categories is not None:
        used_categories.setdefault(offer.seller_index, set()).add(offer.category)
        used_categories.setdefault(offer.buyer_index, set()).add(offer.category)
    return True, "Transakcja zostala zakonczona."
