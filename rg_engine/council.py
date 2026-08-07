from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from rg_engine.items import BACKPACK_LIMIT, ensure_equipment_state, normalise_item

TRADE_CATEGORIES = ("quest", "item", "helper", "good")
COUNCIL_LIMITS = {"quest": 2, "item": 2, "helper": 1, "good": 2}
QUEST_PRICES = {1: 2, 2: 4, 3: 6, 4: 8}
MAX_ACTIVE_QUESTS = 3
MAX_HELPERS = 5


@dataclass(frozen=True)
class AssetRef:
    category: str
    source: str
    key: Any
    quantity: int = 1


@dataclass
class TradeSide:
    assets: list[AssetRef] = field(default_factory=list)
    gold: int = 0


@dataclass
class TradeOffer:
    left_index: int
    right_index: int
    left: TradeSide = field(default_factory=TradeSide)
    right: TradeSide = field(default_factory=TradeSide)
    accepted_left: bool = False
    accepted_right: bool = False

    @property
    def accepted(self) -> bool:
        return self.accepted_left and self.accepted_right

    def reset_acceptance(self) -> None:
        self.accepted_left = False
        self.accepted_right = False


@dataclass
class CouncilUsage:
    counts: dict[int, dict[str, int]] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)

    @classmethod
    def for_players(cls, players: list[dict]) -> "CouncilUsage":
        return cls({index: {category: 0 for category in TRADE_CATEGORIES} for index in range(len(players))})

    def used(self, player_index: int, category: str) -> int:
        return int(self.counts.get(player_index, {}).get(category, 0) or 0)

    def remaining(self, player_index: int, category: str) -> int:
        return max(0, COUNCIL_LIMITS[category] - self.used(player_index, category))

    def add(self, player_index: int, category: str, amount: int) -> None:
        self.counts.setdefault(player_index, {key: 0 for key in TRADE_CATEGORIES})
        self.counts[player_index][category] = self.used(player_index, category) + max(0, int(amount))


def quest_sale_price(world_level: int) -> int:
    return QUEST_PRICES[max(1, min(4, int(world_level or 1)))]


def _quest_name(quest: Any) -> str:
    return str(quest.get("name", "Quest")) if isinstance(quest, dict) else str(quest)


def _item_name(item: Any) -> str:
    return str(normalise_item(item).get("name", "Przedmiot"))


def _helper_name(helper: Any) -> str:
    return str(helper.get("name", "Pomocnik")) if isinstance(helper, dict) else str(helper)


def _asset_name(asset: AssetRef, player: dict) -> str:
    value = resolve_asset(player, asset)
    if asset.category == "quest":
        return _quest_name(value)
    if asset.category == "item":
        return _item_name(value)
    if asset.category == "helper":
        return _helper_name(value)
    return str(asset.key)


def available_assets(player: dict, category: str) -> list[tuple[AssetRef, str, str]]:
    if category == "quest":
        result = []
        for index, quest in enumerate(player.get("active_quests", []) or []):
            result.append((AssetRef("quest", "active_quests", index), _quest_name(quest), str(quest.get("stage", ""))))
        return result
    if category == "item":
        ensure_equipment_state(player)
        result = []
        for index, item in enumerate(player.get("inventory", []) or []):
            result.append((AssetRef("item", "inventory", index), _item_name(item), "Plecak"))
        for slot, item in (player.get("equipment", {}) or {}).items():
            if item:
                result.append((AssetRef("item", "equipment", slot), _item_name(item), f"Założone: {slot}"))
        return result
    if category == "helper":
        return [
            (AssetRef("helper", "helpers", index), _helper_name(helper), str(helper.get("effect_text", "")))
            for index, helper in enumerate(player.get("helpers", []) or [])
        ]
    if category == "good":
        counts: dict[str, int] = {}
        for good in player.get("goods", []) or []:
            name = str(good)
            counts[name] = counts.get(name, 0) + 1
        return [(AssetRef("good", "goods", name, amount), name, f"Posiadasz: {amount}") for name, amount in sorted(counts.items())]
    return []


def resolve_asset(player: dict, asset: AssetRef) -> Any:
    if asset.category == "quest" and asset.source == "active_quests":
        collection = player.get("active_quests", []) or []
        return collection[int(asset.key)] if 0 <= int(asset.key) < len(collection) else None
    if asset.category == "helper" and asset.source == "helpers":
        collection = player.get("helpers", []) or []
        return collection[int(asset.key)] if 0 <= int(asset.key) < len(collection) else None
    if asset.category == "item":
        ensure_equipment_state(player)
        if asset.source == "inventory":
            collection = player.get("inventory", []) or []
            return collection[int(asset.key)] if 0 <= int(asset.key) < len(collection) else None
        if asset.source == "equipment":
            return (player.get("equipment", {}) or {}).get(str(asset.key))
    if asset.category == "good" and asset.source == "goods":
        return str(asset.key)
    return None


def _side_category_counts(side: TradeSide) -> dict[str, int]:
    counts = {category: 0 for category in TRADE_CATEGORIES}
    for asset in side.assets:
        if asset.category == "good":
            counts["good"] = 1
        elif asset.category in counts:
            counts[asset.category] += max(1, int(asset.quantity or 1))
    return counts


def participation_costs(offer: TradeOffer) -> dict[str, int]:
    left_counts = _side_category_counts(offer.left)
    right_counts = _side_category_counts(offer.right)
    return {category: max(left_counts[category], right_counts[category]) for category in TRADE_CATEGORIES}


def _selected_good_quantity(side: TradeSide, name: str) -> int:
    return sum(max(0, int(asset.quantity or 0)) for asset in side.assets if asset.category == "good" and str(asset.key) == name)


def _validate_assets(side: TradeSide, player: dict) -> tuple[bool, str]:
    seen = set()
    goods_available: dict[str, int] = {}
    for good in player.get("goods", []) or []:
        goods_available[str(good)] = goods_available.get(str(good), 0) + 1

    for asset in side.assets:
        identity = (asset.category, asset.source, str(asset.key))
        if identity in seen and asset.category != "good":
            return False, "Ten sam element został dodany do oferty więcej niż raz."
        seen.add(identity)
        if asset.category not in TRADE_CATEGORIES:
            return False, "Oferta zawiera nieprawidłową kategorię."
        if asset.category == "good":
            amount = _selected_good_quantity(side, str(asset.key))
            if amount <= 0 or amount > goods_available.get(str(asset.key), 0):
                return False, f"Brak odpowiedniej liczby towaru: {asset.key}."
            continue
        value = resolve_asset(player, asset)
        if value is None:
            return False, "Jeden z oferowanych elementów nie jest już dostępny."
        if asset.category == "quest" and isinstance(value, dict):
            if value.get("legendary") or value.get("tradeable") is False:
                return False, f"Questa „{_quest_name(value)}” nie można wymieniać."
    return True, "Oferta poprawna."


def _final_capacity_valid(offer: TradeOffer, players: list[dict]) -> tuple[bool, str]:
    left_player = players[offer.left_index]
    right_player = players[offer.right_index]
    left_counts = _side_category_counts(offer.left)
    right_counts = _side_category_counts(offer.right)

    for player, outgoing, incoming, side in (
        (left_player, left_counts, right_counts, offer.left),
        (right_player, right_counts, left_counts, offer.right),
    ):
        quest_final = len(player.get("active_quests", []) or []) - outgoing["quest"] + incoming["quest"]
        if quest_final > MAX_ACTIVE_QUESTS:
            return False, f"{player.get('name', 'Gracz')} nie ma miejsca na kolejne questy."
        helper_final = len(player.get("helpers", []) or []) - outgoing["helper"] + incoming["helper"]
        if helper_final > MAX_HELPERS:
            return False, f"{player.get('name', 'Gracz')} nie ma miejsca na kolejnego pomocnika."

        ensure_equipment_state(player)
        outgoing_inventory = sum(1 for asset in side.assets if asset.category == "item" and asset.source == "inventory")
        incoming_items = incoming["item"]
        inventory_final = len(player.get("inventory", []) or []) - outgoing_inventory + incoming_items
        limit = int(player.get("backpack_limit", BACKPACK_LIMIT) or BACKPACK_LIMIT)
        if inventory_final > limit:
            return False, f"{player.get('name', 'Gracz')} nie ma miejsca w plecaku."
    return True, "Pojemność poprawna."


def _quest_price_valid(offer: TradeOffer, world_level: int) -> tuple[bool, str]:
    left_quests = _side_category_counts(offer.left)["quest"]
    right_quests = _side_category_counts(offer.right)["quest"]
    if left_quests == right_quests:
        return True, "Questy są wymieniane quest za quest."

    price = quest_sale_price(world_level)
    difference = abs(left_quests - right_quests)
    expected = price * difference
    if left_quests > right_quests:
        net_gold = int(offer.right.gold or 0) - int(offer.left.gold or 0)
        payer = "prawa strona"
    else:
        net_gold = int(offer.left.gold or 0) - int(offer.right.gold or 0)
        payer = "lewa strona"
    if net_gold != expected:
        return False, f"Netto sprzedany quest kosztuje dokładnie {price} złota. {payer} musi zapłacić {expected} złota netto."
    return True, "Cena questów jest poprawna."


def validate_trade(offer: TradeOffer, players: list[dict], usage: CouncilUsage | None = None, world_level: int = 1) -> tuple[bool, str]:
    if not 0 <= offer.left_index < len(players) or not 0 <= offer.right_index < len(players):
        return False, "Nieprawidłowy uczestnik transakcji."
    if offer.left_index == offer.right_index:
        return False, "Nie można handlować z samym sobą."
    if int(offer.left.gold or 0) < 0 or int(offer.right.gold or 0) < 0:
        return False, "Ilość złota nie może być ujemna."
    if int(players[offer.left_index].get("gold", 0) or 0) < int(offer.left.gold or 0):
        return False, "Lewa strona nie ma wystarczającej liczby monet."
    if int(players[offer.right_index].get("gold", 0) or 0) < int(offer.right.gold or 0):
        return False, "Prawa strona nie ma wystarczającej liczby monet."

    left_has_value = bool(offer.left.assets or offer.left.gold)
    right_has_value = bool(offer.right.assets or offer.right.gold)
    if not left_has_value or not right_has_value:
        return False, "Transakcja nie może być darmowym przekazaniem. Obie strony muszą coś zaoferować."

    valid, message = _validate_assets(offer.left, players[offer.left_index])
    if not valid:
        return False, message
    valid, message = _validate_assets(offer.right, players[offer.right_index])
    if not valid:
        return False, message

    costs = participation_costs(offer)
    if usage is not None:
        for category, cost in costs.items():
            if cost <= 0:
                continue
            for player_index in (offer.left_index, offer.right_index):
                if usage.used(player_index, category) + cost > COUNCIL_LIMITS[category]:
                    return False, f"{players[player_index].get('name', 'Gracz')} przekroczył limit kategorii: {category}."

    valid, message = _quest_price_valid(offer, world_level)
    if not valid:
        return False, message
    valid, message = _final_capacity_valid(offer, players)
    if not valid:
        return False, message
    return True, "Transakcja jest poprawna."


def _extract_assets(player: dict, side: TradeSide) -> dict[str, list[Any]]:
    result = {"quest": [], "item": [], "helper": [], "good": []}

    quest_indices = sorted((int(asset.key) for asset in side.assets if asset.category == "quest"), reverse=True)
    for index in quest_indices:
        result["quest"].append(copy.deepcopy(player["active_quests"].pop(index)))

    helper_indices = sorted((int(asset.key) for asset in side.assets if asset.category == "helper"), reverse=True)
    for index in helper_indices:
        result["helper"].append(copy.deepcopy(player["helpers"].pop(index)))

    ensure_equipment_state(player)
    inventory_indices = sorted((int(asset.key) for asset in side.assets if asset.category == "item" and asset.source == "inventory"), reverse=True)
    for index in inventory_indices:
        result["item"].append(copy.deepcopy(player["inventory"].pop(index)))
    for asset in side.assets:
        if asset.category == "item" and asset.source == "equipment":
            slot = str(asset.key)
            item = player["equipment"].get(slot)
            if item:
                result["item"].append(copy.deepcopy(item))
                player["equipment"][slot] = None

    for asset in side.assets:
        if asset.category != "good":
            continue
        name = str(asset.key)
        amount = max(0, int(asset.quantity or 0))
        removed = 0
        goods = player.setdefault("goods", [])
        for index in range(len(goods) - 1, -1, -1):
            if str(goods[index]) == name and removed < amount:
                goods.pop(index)
                removed += 1
        result["good"].extend([name] * removed)
    return result


def _receive_assets(player: dict, assets: dict[str, list[Any]]) -> None:
    player.setdefault("active_quests", []).extend(copy.deepcopy(assets["quest"]))
    ensure_equipment_state(player)
    player.setdefault("inventory", []).extend(normalise_item(item) for item in assets["item"])
    player.setdefault("helpers", []).extend(copy.deepcopy(assets["helper"]))
    player.setdefault("goods", []).extend(list(assets["good"]))


def _side_summary(side: TradeSide, player: dict) -> str:
    names = []
    for asset in side.assets:
        if asset.category == "good":
            names.append(f"{asset.quantity}x {asset.key}")
        else:
            names.append(_asset_name(asset, player))
    if side.gold:
        names.append(f"{side.gold} złota")
    return ", ".join(names) if names else "—"


def execute_trade(offer: TradeOffer, players: list[dict], usage: CouncilUsage, world_level: int = 1) -> tuple[bool, str]:
    if not offer.accepted:
        return False, "Obie strony muszą zaakceptować transakcję."
    valid, message = validate_trade(offer, players, usage, world_level)
    if not valid:
        return False, message

    left_player = players[offer.left_index]
    right_player = players[offer.right_index]
    left_summary = _side_summary(offer.left, left_player)
    right_summary = _side_summary(offer.right, right_player)

    left_assets = _extract_assets(left_player, offer.left)
    right_assets = _extract_assets(right_player, offer.right)
    _receive_assets(left_player, right_assets)
    _receive_assets(right_player, left_assets)

    left_gold = int(offer.left.gold or 0)
    right_gold = int(offer.right.gold or 0)
    left_player["gold"] = int(left_player.get("gold", 0) or 0) - left_gold + right_gold
    right_player["gold"] = int(right_player.get("gold", 0) or 0) - right_gold + left_gold

    costs = participation_costs(offer)
    for category, cost in costs.items():
        if cost <= 0:
            continue
        usage.add(offer.left_index, category, cost)
        usage.add(offer.right_index, category, cost)

    entry = f"{left_player.get('name', 'Gracz')} [{left_summary}] ⇄ {right_player.get('name', 'Gracz')} [{right_summary}]"
    usage.history.append(entry)
    return True, entry


def abandon_quest(player: dict, quest_index: int) -> tuple[bool, str]:
    active = player.setdefault("active_quests", [])
    if not 0 <= int(quest_index) < len(active):
        return False, "Nie znaleziono questa."
    quest = active.pop(int(quest_index))
    if isinstance(quest, dict) and quest.get("abandonable") is False:
        active.insert(int(quest_index), quest)
        return False, "Tego questa nie można porzucić."
    if isinstance(quest, dict):
        quest["status"] = "failed"
        quest["stage"] = "Porzucony"
        quest["last_result"] = "Quest porzucony podczas Rady Bohaterów."
    player.setdefault("failed_quests", []).append(quest)
    return True, f"{player.get('name', 'Gracz')} porzuca quest: {_quest_name(quest)}."
