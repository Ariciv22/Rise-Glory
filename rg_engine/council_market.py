from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from rg_engine.council import (
    AssetRef,
    MAX_ACTIVE_QUESTS,
    MAX_HELPERS,
    TradeOffer,
    TradeSide,
    _asset_name,
    _validate_assets,
    resolve_asset,
)
from rg_engine.items import BACKPACK_LIMIT, ensure_equipment_state, normalise_item

PUBLIC_MIN_PRICE = 1
MAX_LOOSE_NEGOTIATIONS = 2
PUBLIC_CATEGORIES = ("quest", "item", "helper", "good")


def _empty_assets() -> dict[str, list[Any]]:
    return {"quest": [], "item": [], "helper": [], "good": []}


def _player_number(player: dict, index: int) -> int:
    try:
        return int(player.get("player_number", index + 1) or index + 1)
    except (TypeError, ValueError):
        return index + 1


def council_turn_order(players: list[dict]) -> list[int]:
    """Lider zaczyna, potem pozostali według numerów graczy."""
    if not players:
        return []
    indices = list(range(len(players)))
    leader = min(
        indices,
        key=lambda index: (
            -int(players[index].get("legend", 0) or 0),
            _player_number(players[index], index),
        ),
    )
    remaining = sorted(
        (index for index in indices if index != leader),
        key=lambda index: _player_number(players[index], index),
    )
    return [leader, *remaining]


def _side_counts(side: TradeSide) -> dict[str, int]:
    counts = {category: 0 for category in PUBLIC_CATEGORIES}
    for asset in side.assets:
        if asset.category not in counts:
            continue
        if asset.category == "good":
            counts["good"] += max(0, int(asset.quantity or 0))
        else:
            counts[asset.category] += 1
    return counts


def _asset_identity(asset: AssetRef) -> tuple[str, str, str]:
    return asset.category, asset.source, str(asset.key)


def _copy_extract_assets(player: dict, side: TradeSide) -> dict[str, list[Any]]:
    """Przenosi wskazane elementy z gracza do escrow/transakcji."""
    result = _empty_assets()

    quest_indices = sorted(
        {int(asset.key) for asset in side.assets if asset.category == "quest" and asset.source == "active_quests"},
        reverse=True,
    )
    for index in quest_indices:
        if 0 <= index < len(player.get("active_quests", []) or []):
            result["quest"].append(copy.deepcopy(player["active_quests"].pop(index)))

    helper_indices = sorted(
        {int(asset.key) for asset in side.assets if asset.category == "helper" and asset.source == "helpers"},
        reverse=True,
    )
    for index in helper_indices:
        if 0 <= index < len(player.get("helpers", []) or []):
            result["helper"].append(copy.deepcopy(player["helpers"].pop(index)))

    ensure_equipment_state(player)
    inventory_indices = sorted(
        {int(asset.key) for asset in side.assets if asset.category == "item" and asset.source == "inventory"},
        reverse=True,
    )
    for index in inventory_indices:
        if 0 <= index < len(player.get("inventory", []) or []):
            result["item"].append(copy.deepcopy(player["inventory"].pop(index)))

    for asset in side.assets:
        if asset.category != "item" or asset.source != "equipment":
            continue
        slot = str(asset.key)
        item = player.get("equipment", {}).get(slot)
        if item:
            result["item"].append(copy.deepcopy(item))
            player["equipment"][slot] = None

    requested_goods: dict[str, int] = {}
    for asset in side.assets:
        if asset.category == "good" and asset.source == "goods":
            name = str(asset.key)
            requested_goods[name] = requested_goods.get(name, 0) + max(0, int(asset.quantity or 0))
    goods = player.setdefault("goods", [])
    for name, amount in requested_goods.items():
        removed = 0
        for index in range(len(goods) - 1, -1, -1):
            if removed >= amount:
                break
            if str(goods[index]) == name:
                goods.pop(index)
                removed += 1
        result["good"].extend([name] * removed)

    return result


def _receive_assets(player: dict, assets: dict[str, list[Any]]) -> None:
    player.setdefault("active_quests", []).extend(copy.deepcopy(assets.get("quest", [])))
    ensure_equipment_state(player)
    player.setdefault("inventory", []).extend(normalise_item(item) for item in assets.get("item", []))
    player.setdefault("helpers", []).extend(copy.deepcopy(assets.get("helper", [])))
    player.setdefault("goods", []).extend(list(assets.get("good", [])))


def _asset_bundle_counts(assets: dict[str, list[Any]]) -> dict[str, int]:
    return {category: len(assets.get(category, []) or []) for category in PUBLIC_CATEGORIES}


def _bundle_summary(assets: dict[str, list[Any]]) -> str:
    parts: list[str] = []
    for quest in assets.get("quest", []) or []:
        parts.append(str(quest.get("name", "Quest")) if isinstance(quest, dict) else str(quest))
    for item in assets.get("item", []) or []:
        parts.append(str(normalise_item(item).get("name", "Przedmiot")))
    for helper in assets.get("helper", []) or []:
        parts.append(str(helper.get("name", "Pomocnik")) if isinstance(helper, dict) else str(helper))
    goods: dict[str, int] = {}
    for good in assets.get("good", []) or []:
        name = str(good)
        goods[name] = goods.get(name, 0) + 1
    parts.extend(f"{amount}x {name}" for name, amount in sorted(goods.items()))
    return ", ".join(parts) if parts else "—"


def _draft_summary(side: TradeSide, player: dict) -> str:
    parts = []
    for asset in side.assets:
        if asset.category == "good":
            parts.append(f"{max(0, int(asset.quantity or 0))}x {asset.key}")
        else:
            parts.append(_asset_name(asset, player))
    if side.gold:
        parts.append(f"{side.gold} Złota")
    return ", ".join(parts) if parts else "—"


def _reserved_counts_for_player(public_offer: "PublicOffer" | None) -> dict[str, int]:
    if public_offer is None or public_offer.status not in {"ready", "revealed"}:
        return {category: 0 for category in PUBLIC_CATEGORIES}
    return _asset_bundle_counts(public_offer.escrow)


def capacity_overflow(
    player: dict,
    incoming: dict[str, list[Any]],
    reserved: dict[str, int] | None = None,
) -> dict[str, int]:
    """Zwraca liczbę własnych elementów, które trzeba odrzucić przed finalizacją."""
    reserved = reserved or {category: 0 for category in PUBLIC_CATEGORIES}
    incoming_counts = _asset_bundle_counts(incoming)
    overflow: dict[str, int] = {}

    quest_final = len(player.get("active_quests", []) or []) + reserved.get("quest", 0) + incoming_counts["quest"]
    if quest_final > MAX_ACTIVE_QUESTS:
        overflow["quest"] = quest_final - MAX_ACTIVE_QUESTS

    helper_final = len(player.get("helpers", []) or []) + reserved.get("helper", 0) + incoming_counts["helper"]
    if helper_final > MAX_HELPERS:
        overflow["helper"] = helper_final - MAX_HELPERS

    ensure_equipment_state(player)
    item_limit = int(player.get("backpack_limit", BACKPACK_LIMIT) or BACKPACK_LIMIT)
    item_final = len(player.get("inventory", []) or []) + reserved.get("item", 0) + incoming_counts["item"]
    if item_final > item_limit:
        overflow["item"] = item_final - item_limit

    raw_goods_limit = player.get("goods_limit")
    if raw_goods_limit not in (None, ""):
        goods_limit = max(0, int(raw_goods_limit or 0))
        goods_final = len(player.get("goods", []) or []) + reserved.get("good", 0) + incoming_counts["good"]
        if goods_final > goods_limit:
            overflow["good"] = goods_final - goods_limit

    return overflow


def _discard_plan_counts(discard_assets: list[AssetRef]) -> dict[str, int]:
    side = TradeSide(list(discard_assets), 0)
    return _side_counts(side)


def _validate_discard_plan(player: dict, required: dict[str, int], discard_assets: list[AssetRef]) -> tuple[bool, str]:
    if not required:
        return True, "Brak odrzutów."
    side = TradeSide(list(discard_assets), 0)
    valid, message = _validate_assets(side, player)
    if not valid:
        return False, message
    counts = _discard_plan_counts(discard_assets)
    for category, amount in required.items():
        if counts.get(category, 0) < int(amount):
            return False, f"Musisz odrzucić jeszcze {int(amount) - counts.get(category, 0)} elementów kategorii {category}."
    return True, "Plan odrzutu poprawny."


def _discard_selected(player: dict, discard_assets: list[AssetRef]) -> dict[str, list[Any]]:
    discarded = _copy_extract_assets(player, TradeSide(list(discard_assets), 0))
    player.setdefault("discarded_trade_assets", []).append(copy.deepcopy(discarded))
    return discarded


@dataclass
class PublicOffer:
    owner_index: int
    draft: TradeSide = field(default_factory=TradeSide)
    price: int = PUBLIC_MIN_PRICE
    status: str = "draft"  # draft / ready / revealed / sold / expired / none
    escrow: dict[str, list[Any]] = field(default_factory=_empty_assets)
    buyer_index: int | None = None

    @property
    def has_offer(self) -> bool:
        return any(self.escrow.get(category) for category in PUBLIC_CATEGORIES) or bool(self.draft.assets)

    @property
    def frozen(self) -> bool:
        return self.status in {"ready", "revealed", "sold", "expired", "none"}

    def summary(self) -> str:
        if self.status == "draft":
            return "Oferta w przygotowaniu"
        if self.status == "none":
            return "Brak oferty"
        return _bundle_summary(self.escrow)


@dataclass
class LooseNegotiation:
    initiator_index: int
    partner_index: int
    offer: TradeOffer
    state: str = "invited"  # invited/open/locked/completed/failed/cancelled/rejected/expired
    preliminary_acceptance: set[int] = field(default_factory=set)
    final_acceptance: set[int] = field(default_factory=set)
    discard_plans: dict[int, list[AssetRef]] = field(default_factory=dict)
    last_message: str = ""

    @property
    def participants(self) -> tuple[int, int]:
        return self.initiator_index, self.partner_index

    def side_for(self, player_index: int) -> TradeSide:
        if player_index == self.offer.left_index:
            return self.offer.left
        if player_index == self.offer.right_index:
            return self.offer.right
        raise ValueError("Gracz nie uczestniczy w tej negocjacji.")

    def reset_acceptance(self) -> None:
        self.preliminary_acceptance.clear()
        self.final_acceptance.clear()
        self.discard_plans.clear()
        if self.state not in {"invited", "completed", "failed", "cancelled", "rejected", "expired"}:
            self.state = "open"


@dataclass
class TradeLogEntry:
    kind: str
    left_index: int | None = None
    right_index: int | None = None
    left_summary: str = ""
    right_summary: str = ""
    text: str = ""


class CouncilMarketSession:
    """Docelowy, sekwencyjny przebieg Rady Bohaterów."""

    def __init__(self, players: list[dict]):
        self.players = players
        self.turn_order = council_turn_order(players)
        self.stage = "preparation"  # preparation/turns/summary/departure/closed
        self.public_offers = [PublicOffer(index) for index in range(len(players))]
        self.prepared_players: set[int] = set()
        self.turn_position = 0
        self.turn_phase = "public"
        self.public_purchase_used: dict[int, bool] = {index: False for index in range(len(players))}
        self.loose_attempts_used: dict[int, int] = {index: 0 for index in range(len(players))}
        self.negotiation: LooseNegotiation | None = None
        self.trade_logs: list[TradeLogEntry] = []
        self.chat_messages: list[dict[str, Any]] = []
        self.departure_ready: set[int] = set()
        self.message = "Przygotuj publiczną ofertę lub wybierz Brak oferty."

    @property
    def active_player_index(self) -> int | None:
        if self.stage != "turns" or not self.turn_order:
            return None
        return self.turn_order[min(self.turn_position, len(self.turn_order) - 1)]

    @property
    def active_player(self) -> dict | None:
        index = self.active_player_index
        return self.players[index] if index is not None else None

    def public_offer(self, player_index: int) -> PublicOffer:
        return self.public_offers[int(player_index)]

    def toggle_public_asset(self, player_index: int, asset: AssetRef) -> tuple[bool, str]:
        offer = self.public_offer(player_index)
        if offer.status != "draft":
            return False, "Oferta została już zatwierdzona i jest zamrożona."
        player = self.players[player_index]
        if asset.category == "good":
            return False, "Ilość Towaru ustawiaj osobno."
        valid, message = _validate_assets(TradeSide([asset], 0), player)
        if not valid:
            return False, message
        identity = _asset_identity(asset)
        current = next((value for value in offer.draft.assets if _asset_identity(value) == identity), None)
        if current:
            offer.draft.assets.remove(current)
            return True, "Usunięto element z publicznej oferty."
        offer.draft.assets.append(asset)
        return True, "Dodano element do publicznej oferty."

    def set_public_good_quantity(self, player_index: int, name: str, quantity: int) -> tuple[bool, str]:
        offer = self.public_offer(player_index)
        if offer.status != "draft":
            return False, "Oferta została już zatwierdzona i jest zamrożona."
        player = self.players[player_index]
        available = sum(1 for good in player.get("goods", []) or [] if str(good) == str(name))
        quantity = max(0, min(available, int(quantity or 0)))
        offer.draft.assets = [
            asset for asset in offer.draft.assets
            if not (asset.category == "good" and str(asset.key) == str(name))
        ]
        if quantity:
            offer.draft.assets.append(AssetRef("good", "goods", str(name), quantity))
        return True, f"Ustawiono {quantity}/{available} Towaru: {name}."

    def set_public_price(self, player_index: int, price: int) -> tuple[bool, str]:
        offer = self.public_offer(player_index)
        if offer.status != "draft":
            return False, "Oferta została już zatwierdzona i jest zamrożona."
        offer.price = max(PUBLIC_MIN_PRICE, int(price or PUBLIC_MIN_PRICE))
        return True, f"Cena publicznej oferty: {offer.price} Złota."

    def finalize_public_offer(self, player_index: int, no_offer: bool = False) -> tuple[bool, str]:
        offer = self.public_offer(player_index)
        if offer.status != "draft":
            return False, "Decyzja tego gracza została już zatwierdzona."
        player = self.players[player_index]

        if no_offer or not offer.draft.assets:
            offer.draft.assets.clear()
            offer.status = "none"
            self.prepared_players.add(player_index)
            self._reveal_if_ready()
            return True, "Gracz nie wystawia publicznej oferty."

        if offer.price < PUBLIC_MIN_PRICE:
            return False, "Minimalna cena publicznej oferty to 1 Złoto."
        valid, message = _validate_assets(offer.draft, player)
        if not valid:
            return False, message
        offer.escrow = _copy_extract_assets(player, offer.draft)
        offer.status = "ready"
        self.prepared_players.add(player_index)
        self._reveal_if_ready()
        return True, "Publiczna oferta została zatwierdzona i zamrożona."

    def _reveal_if_ready(self) -> None:
        if len(self.prepared_players) < len(self.players):
            self.message = f"Oferty gotowe: {len(self.prepared_players)}/{len(self.players)}"
            return
        for offer in self.public_offers:
            if offer.status == "ready":
                offer.status = "revealed"
        self.stage = "turns"
        self.turn_position = 0
        self.turn_phase = "public"
        active = self.active_player
        self.message = f"Kolej gracza: {active.get('name', 'Gracz') if active else '—'}. Faza publicznych ofert."

    def reserved_counts(self, player_index: int) -> dict[str, int]:
        return _reserved_counts_for_player(self.public_offer(player_index))

    def public_purchase_overflow(self, buyer_index: int, seller_index: int) -> dict[str, int]:
        offer = self.public_offer(seller_index)
        return capacity_overflow(self.players[buyer_index], offer.escrow, self.reserved_counts(buyer_index))

    def buy_public_offer(
        self,
        buyer_index: int,
        seller_index: int,
        discard_assets: list[AssetRef] | None = None,
    ) -> tuple[bool, str]:
        if self.stage != "turns" or self.turn_phase != "public":
            return False, "Publiczne oferty nie są teraz dostępne do zakupu."
        if buyer_index != self.active_player_index:
            return False, "Tylko aktywny gracz może kupić publiczną ofertę."
        if self.public_purchase_used.get(buyer_index):
            return False, "W tej turze kupiono już maksymalnie jedną publiczną ofertę."
        if seller_index == buyer_index:
            return False, "Nie można kupić własnej oferty."

        offer = self.public_offer(seller_index)
        if offer.status != "revealed":
            return False, "Ta publiczna oferta nie jest już dostępna."
        buyer = self.players[buyer_index]
        seller = self.players[seller_index]
        if int(buyer.get("gold", 0) or 0) < int(offer.price):
            return False, "Nie masz wystarczająco Złota na tę ofertę."

        overflow = self.public_purchase_overflow(buyer_index, seller_index)
        discard_assets = list(discard_assets or [])
        valid, message = _validate_discard_plan(buyer, overflow, discard_assets)
        if not valid:
            return False, message
        if overflow:
            _discard_selected(buyer, discard_assets)

        buyer["gold"] = int(buyer.get("gold", 0) or 0) - int(offer.price)
        seller["gold"] = int(seller.get("gold", 0) or 0) + int(offer.price)
        _receive_assets(buyer, offer.escrow)

        summary = _bundle_summary(offer.escrow)
        offer.status = "sold"
        offer.buyer_index = buyer_index
        self.public_purchase_used[buyer_index] = True
        self.trade_logs.append(
            TradeLogEntry(
                kind="public",
                left_index=seller_index,
                right_index=buyer_index,
                left_summary=summary,
                right_summary=f"{offer.price} Złota",
                text=f"{buyer.get('name', 'Gracz')} kupuje ofertę od {seller.get('name', 'Gracz')} za {offer.price} Złota.",
            )
        )
        self.turn_phase = "loose"
        self.message = "Oferta kupiona. Rozpoczyna się faza luźnego handlu. Pozostało: 2 z 2 negocjacji."
        return True, self.trade_logs[-1].text

    def skip_public_purchase(self, player_index: int) -> tuple[bool, str]:
        if self.stage != "turns" or self.turn_phase != "public" or player_index != self.active_player_index:
            return False, "Nie można teraz pominąć publicznych ofert."
        self.turn_phase = "loose"
        remaining = self.remaining_negotiations(player_index)
        self.message = f"Nie kupujesz żadnej oferty. Faza luźnego handlu — pozostało: {remaining} z {MAX_LOOSE_NEGOTIATIONS} negocjacji."
        return True, self.message

    def remaining_negotiations(self, player_index: int | None = None) -> int:
        index = self.active_player_index if player_index is None else int(player_index)
        if index is None:
            return 0
        return max(0, MAX_LOOSE_NEGOTIATIONS - int(self.loose_attempts_used.get(index, 0) or 0))

    def invite_to_negotiation(self, partner_index: int) -> tuple[bool, str]:
        initiator = self.active_player_index
        if self.stage != "turns" or self.turn_phase != "loose" or initiator is None:
            return False, "Luźny handel nie jest teraz aktywny."
        if self.negotiation is not None and self.negotiation.state in {"invited", "open", "locked"}:
            return False, "Możesz mieć tylko jedno oczekujące zaproszenie lub negocjację naraz."
        if self.remaining_negotiations(initiator) <= 0:
            return False, "Wykorzystano już obie luźne negocjacje w tej turze."
        if not 0 <= int(partner_index) < len(self.players) or int(partner_index) == initiator:
            return False, "Wybierz innego gracza."

        partner_index = int(partner_index)
        offer = TradeOffer(initiator, partner_index)
        self.negotiation = LooseNegotiation(initiator, partner_index, offer)
        text = f"{self.players[initiator].get('name', 'Gracz')} zaprasza {self.players[partner_index].get('name', 'Gracz')} do negocjacji."
        self.trade_logs.append(TradeLogEntry(kind="invite", left_index=initiator, right_index=partner_index, text=text))
        self.message = text
        return True, text

    def respond_to_invitation(self, partner_index: int, accept: bool) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None or negotiation.state != "invited":
            return False, "Nie ma oczekującego zaproszenia."
        if int(partner_index) != negotiation.partner_index:
            return False, "Tylko zaproszony gracz może odpowiedzieć."
        if not accept:
            negotiation.state = "rejected"
            text = f"{self.players[partner_index].get('name', 'Gracz')} odrzuca zaproszenie do handlu. Próba nie została zużyta."
            self.trade_logs.append(TradeLogEntry(kind="invite_rejected", left_index=negotiation.initiator_index, right_index=partner_index, text=text))
            self.message = text
            return True, text

        negotiation.state = "open"
        self.loose_attempts_used[negotiation.initiator_index] = int(self.loose_attempts_used.get(negotiation.initiator_index, 0) or 0) + 1
        text = (
            f"{self.players[negotiation.initiator_index].get('name', 'Gracz')} rozpoczyna negocjacje z "
            f"{self.players[partner_index].get('name', 'Gracz')}."
        )
        self.trade_logs.append(TradeLogEntry(kind="negotiation_started", left_index=negotiation.initiator_index, right_index=partner_index, text=text))
        self.message = text
        return True, text

    def clear_finished_negotiation(self) -> None:
        if self.negotiation and self.negotiation.state in {"completed", "failed", "cancelled", "rejected", "expired"}:
            self.negotiation = None

    def negotiation_side(self, player_index: int) -> TradeSide:
        if self.negotiation is None:
            raise ValueError("Brak aktywnej negocjacji.")
        return self.negotiation.side_for(player_index)

    def _can_edit_negotiation(self, player_index: int) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None or negotiation.state != "open":
            return False, "Warunki tej negocjacji są obecnie zablokowane."
        if player_index not in negotiation.participants:
            return False, "Tylko uczestnicy negocjacji mogą zmieniać ofertę."
        return True, ""

    def toggle_negotiation_asset(self, player_index: int, asset: AssetRef) -> tuple[bool, str]:
        allowed, message = self._can_edit_negotiation(player_index)
        if not allowed:
            return False, message
        player = self.players[player_index]
        valid, message = _validate_assets(TradeSide([asset], 0), player)
        if not valid:
            return False, message
        side = self.negotiation.side_for(player_index)
        if asset.category == "good":
            return False, "Ilość Towaru ustawiaj osobno."
        identity = _asset_identity(asset)
        current = next((value for value in side.assets if _asset_identity(value) == identity), None)
        if current:
            side.assets.remove(current)
        else:
            side.assets.append(asset)
        self.negotiation.reset_acceptance()
        self.negotiation.last_message = "Oferta zmieniona — wszystkie akceptacje anulowano."
        return True, self.negotiation.last_message

    def set_negotiation_good_quantity(self, player_index: int, name: str, quantity: int) -> tuple[bool, str]:
        allowed, message = self._can_edit_negotiation(player_index)
        if not allowed:
            return False, message
        player = self.players[player_index]
        available = sum(1 for good in player.get("goods", []) or [] if str(good) == str(name))
        quantity = max(0, min(available, int(quantity or 0)))
        side = self.negotiation.side_for(player_index)
        side.assets = [asset for asset in side.assets if not (asset.category == "good" and str(asset.key) == str(name))]
        if quantity:
            side.assets.append(AssetRef("good", "goods", str(name), quantity))
        self.negotiation.reset_acceptance()
        return True, "Zmieniono ilość Towaru — wszystkie akceptacje anulowano."

    def set_negotiation_gold(self, player_index: int, amount: int) -> tuple[bool, str]:
        allowed, message = self._can_edit_negotiation(player_index)
        if not allowed:
            return False, message
        maximum = max(0, int(self.players[player_index].get("gold", 0) or 0))
        side = self.negotiation.side_for(player_index)
        side.gold = max(0, min(maximum, int(amount or 0)))
        self.negotiation.reset_acceptance()
        return True, "Zmieniono Złoto — wszystkie akceptacje anulowano."

    def _validate_loose_trade(self) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None or negotiation.state not in {"open", "locked"}:
            return False, "Brak aktywnej negocjacji."
        offer = negotiation.offer
        left = self.players[offer.left_index]
        right = self.players[offer.right_index]
        if not (offer.left.assets or offer.left.gold) or not (offer.right.assets or offer.right.gold):
            return False, "Obie strony muszą coś zaoferować."
        if int(left.get("gold", 0) or 0) < int(offer.left.gold or 0):
            return False, f"{left.get('name', 'Gracz')} nie ma wystarczająco Złota."
        if int(right.get("gold", 0) or 0) < int(offer.right.gold or 0):
            return False, f"{right.get('name', 'Gracz')} nie ma wystarczająco Złota."
        valid, message = _validate_assets(offer.left, left)
        if not valid:
            return False, message
        valid, message = _validate_assets(offer.right, right)
        if not valid:
            return False, message
        return True, "Warunki negocjacji są poprawne."

    def preliminarily_accept(self, player_index: int) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None or negotiation.state != "open" or player_index not in negotiation.participants:
            return False, "Nie możesz teraz zaakceptować tej negocjacji."
        valid, message = self._validate_loose_trade()
        if not valid:
            return False, message
        negotiation.preliminary_acceptance.add(player_index)
        if set(negotiation.participants).issubset(negotiation.preliminary_acceptance):
            negotiation.state = "locked"
            negotiation.last_message = "Obie strony wstępnie zaakceptowały. Oferta została zablokowana do edycji."
        else:
            negotiation.last_message = f"{self.players[player_index].get('name', 'Gracz')} wstępnie akceptuje warunki."
        return True, negotiation.last_message

    def rollback_to_negotiation(self, player_index: int) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None or negotiation.state not in {"open", "locked"} or player_index not in negotiation.participants:
            return False, "Nie można wrócić do negocjacji."
        negotiation.preliminary_acceptance.clear()
        negotiation.final_acceptance.clear()
        negotiation.discard_plans.clear()
        negotiation.state = "open"
        negotiation.last_message = "Cofnięto do negocjacji. Wszystkie akceptacje zostały anulowane."
        return True, negotiation.last_message

    def negotiation_overflow(self, player_index: int) -> dict[str, int]:
        negotiation = self.negotiation
        if negotiation is None:
            return {}
        if player_index == negotiation.offer.left_index:
            incoming_side = negotiation.offer.right
        elif player_index == negotiation.offer.right_index:
            incoming_side = negotiation.offer.left
        else:
            return {}
        incoming = self._preview_side_assets(incoming_side, self.players[negotiation.partner_index if player_index == negotiation.initiator_index else negotiation.initiator_index])
        return capacity_overflow(self.players[player_index], incoming, self.reserved_counts(player_index))

    def _preview_side_assets(self, side: TradeSide, owner: dict) -> dict[str, list[Any]]:
        result = _empty_assets()
        for asset in side.assets:
            if asset.category == "good":
                result["good"].extend([str(asset.key)] * max(0, int(asset.quantity or 0)))
                continue
            value = resolve_asset(owner, asset)
            if value is not None:
                result[asset.category].append(copy.deepcopy(value))
        return result

    def set_negotiation_discard_plan(self, player_index: int, discard_assets: list[AssetRef]) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None or negotiation.state != "locked" or player_index not in negotiation.participants:
            return False, "Plan odrzutu można ustawić dopiero po wstępnym zaakceptowaniu warunków."
        required = self.negotiation_overflow(player_index)
        valid, message = _validate_discard_plan(self.players[player_index], required, list(discard_assets))
        if not valid:
            return False, message
        negotiation.discard_plans[player_index] = list(discard_assets)
        return True, "Plan odrzutu zapisany."

    def definitively_accept(self, player_index: int) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None or negotiation.state != "locked" or player_index not in negotiation.participants:
            return False, "Definitywna akceptacja jest dostępna dopiero po dwóch wstępnych akceptacjach."
        required = self.negotiation_overflow(player_index)
        if required:
            plan = negotiation.discard_plans.get(player_index, [])
            valid, message = _validate_discard_plan(self.players[player_index], required, plan)
            if not valid:
                return False, message
        negotiation.final_acceptance.add(player_index)
        if not set(negotiation.participants).issubset(negotiation.final_acceptance):
            negotiation.last_message = f"{self.players[player_index].get('name', 'Gracz')} zaakceptował definitywnie. Oczekiwanie na drugą stronę."
            return True, negotiation.last_message
        return self._execute_negotiation()

    def _execute_negotiation(self) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None:
            return False, "Brak negocjacji."
        valid, message = self._validate_loose_trade()
        if not valid:
            negotiation.final_acceptance.clear()
            return False, message

        offer = negotiation.offer
        left_player = self.players[offer.left_index]
        right_player = self.players[offer.right_index]

        for player_index in negotiation.participants:
            required = self.negotiation_overflow(player_index)
            plan = negotiation.discard_plans.get(player_index, [])
            valid, message = _validate_discard_plan(self.players[player_index], required, plan)
            if not valid:
                negotiation.final_acceptance.clear()
                return False, message
        for player_index, plan in negotiation.discard_plans.items():
            if plan:
                _discard_selected(self.players[player_index], plan)

        left_summary = _draft_summary(offer.left, left_player)
        right_summary = _draft_summary(offer.right, right_player)
        left_assets = _copy_extract_assets(left_player, offer.left)
        right_assets = _copy_extract_assets(right_player, offer.right)
        _receive_assets(left_player, right_assets)
        _receive_assets(right_player, left_assets)

        left_gold = int(offer.left.gold or 0)
        right_gold = int(offer.right.gold or 0)
        left_player["gold"] = int(left_player.get("gold", 0) or 0) - left_gold + right_gold
        right_player["gold"] = int(right_player.get("gold", 0) or 0) - right_gold + left_gold

        negotiation.state = "completed"
        text = f"{left_player.get('name', 'Gracz')} [{left_summary}] ⇄ {right_player.get('name', 'Gracz')} [{right_summary}]"
        negotiation.last_message = text
        self.trade_logs.append(
            TradeLogEntry(
                kind="loose",
                left_index=offer.left_index,
                right_index=offer.right_index,
                left_summary=left_summary,
                right_summary=right_summary,
                text=text,
            )
        )
        self.message = text
        return True, text

    def cancel_negotiation(self, player_index: int) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None or negotiation.state not in {"open", "locked"} or player_index not in negotiation.participants:
            return False, "Nie ma negocjacji do zakończenia."
        negotiation.state = "cancelled"
        text = "Negocjacje zakończono bez transakcji. Wykorzystana próba nie wraca."
        negotiation.last_message = text
        self.trade_logs.append(
            TradeLogEntry(kind="negotiation_cancelled", left_index=negotiation.initiator_index, right_index=negotiation.partner_index, text=text)
        )
        self.message = text
        return True, text

    def expire_invitation(self) -> tuple[bool, str]:
        negotiation = self.negotiation
        if negotiation is None or negotiation.state != "invited":
            return False, "Nie ma oczekującego zaproszenia."
        negotiation.state = "expired"
        text = "Zaproszenie do handlu wygasło. Próba nie została zużyta."
        self.trade_logs.append(
            TradeLogEntry(kind="invite_expired", left_index=negotiation.initiator_index, right_index=negotiation.partner_index, text=text)
        )
        self.message = text
        return True, text

    def can_end_active_turn(self) -> tuple[bool, str]:
        if self.stage != "turns":
            return False, "Rada nie jest w fazie tur graczy."
        if self.turn_phase == "public":
            return False, "Najpierw kup publiczną ofertę albo wybierz Nie kupuję żadnej oferty."
        if self.negotiation is not None and self.negotiation.state in {"invited", "open", "locked"}:
            return False, "Najpierw zakończ oczekujące zaproszenie lub trwającą negocjację."
        return True, ""

    def end_active_turn(self, confirm_unused: bool = False) -> tuple[bool, str]:
        allowed, message = self.can_end_active_turn()
        if not allowed:
            return False, message
        active = self.active_player_index
        if active is None:
            return False, "Brak aktywnego gracza."
        remaining = self.remaining_negotiations(active)
        if remaining > 0 and not confirm_unused:
            return False, f"Pozostało: {remaining} z {MAX_LOOSE_NEGOTIATIONS} negocjacji. Potwierdź, że chcesz zakończyć turę."

        self.clear_finished_negotiation()
        if self.turn_position >= len(self.turn_order) - 1:
            self.stage = "summary"
            self.message = "Wszyscy gracze zakończyli swoje tury w Radzie."
            self._expire_unsold_public_offers()
            return True, self.message

        self.turn_position += 1
        self.turn_phase = "public"
        next_player = self.active_player
        self.message = f"Kolej gracza: {next_player.get('name', 'Gracz')}. Faza publicznych ofert."
        return True, self.message

    def _expire_unsold_public_offers(self) -> None:
        for offer in self.public_offers:
            if offer.status != "revealed":
                continue
            owner = self.players[offer.owner_index]
            _receive_assets(owner, offer.escrow)
            offer.status = "expired"
            self.trade_logs.append(
                TradeLogEntry(
                    kind="public_expired",
                    left_index=offer.owner_index,
                    left_summary=_bundle_summary(offer.escrow),
                    text=f"Niesprzedana oferta gracza {owner.get('name', 'Gracz')} wygasa. Jej zawartość wraca do właściciela.",
                )
            )

    def successful_trade_logs(self) -> list[TradeLogEntry]:
        return [entry for entry in self.trade_logs if entry.kind in {"public", "loose"}]

    def continue_from_summary(self) -> tuple[bool, str]:
        if self.stage != "summary":
            return False, "Podsumowanie Rady nie jest teraz aktywne."
        self.stage = "departure"
        self.message = "Rada zakończona. Każdy gracz musi potwierdzić gotowość do opuszczenia Rady."
        return True, self.message

    def confirm_departure(self, player_index: int) -> tuple[bool, str]:
        if self.stage != "departure" or not 0 <= int(player_index) < len(self.players):
            return False, "Nie można teraz potwierdzić wyjścia z Rady."
        player_index = int(player_index)
        if player_index in self.departure_ready:
            return False, "Ten gracz już potwierdził gotowość i nie może jej cofnąć."
        self.departure_ready.add(player_index)
        if len(self.departure_ready) >= len(self.players):
            self.stage = "closed"
            self.message = "Bohaterowie opuszczają Radę."
            return True, "close_council"
        self.message = f"Gotowi do opuszczenia Rady: {len(self.departure_ready)}/{len(self.players)}"
        return True, self.message

    def add_chat_message(self, player_index: int, text: str) -> tuple[bool, str]:
        value = str(text or "").strip()
        if not value:
            return False, "Wiadomość jest pusta."
        if not 0 <= int(player_index) < len(self.players):
            return False, "Nieprawidłowy gracz."
        entry = {
            "player_index": int(player_index),
            "name": self.players[int(player_index)].get("name", "Gracz"),
            "text": value[:300],
        }
        self.chat_messages.append(entry)
        return True, entry["text"]
