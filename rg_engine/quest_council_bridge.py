from __future__ import annotations

from rg_engine.quests import abandon_quest as abandon_runtime_quest
from rg_engine.quests import can_trade_quest

_INSTALLED = False


def install_quest_council_bridge() -> None:
    """Spina Radę Bohaterów z zasadami własności Questów V2.

    Stary moduł Rady traktował każdy element `active_quests` jako handlowalny i
    posiadał własną, starszą wersję porzucania Questa. Most zachowuje publiczne
    API Rady, ale filtruje rozpoczęte Questy i deleguje porzucenie do wspólnego
    silnika Questów.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_engine.council as council
    import rg_engine.council_market as council_market
    import rg_ui.council as council_ui
    import rg_ui.council_market as council_market_ui

    original_available_assets = council.available_assets
    original_validate_assets = council._validate_assets

    def available_assets_v2(player: dict, category: str):
        assets = original_available_assets(player, category)
        if category != "quest":
            return assets
        result = []
        for entry in assets:
            asset = entry[0]
            quest = council.resolve_asset(player, asset)
            allowed, _reason = can_trade_quest(quest or {})
            if allowed:
                result.append(entry)
        return result

    def validate_assets_v2(side, player):
        valid, message = original_validate_assets(side, player)
        if not valid:
            return valid, message
        for asset in side.assets:
            if asset.category != "quest":
                continue
            quest = council.resolve_asset(player, asset)
            allowed, reason = can_trade_quest(quest or {})
            if not allowed:
                return False, reason
        return True, message

    def abandon_quest_v2(player: dict, quest_index: int):
        active = player.setdefault("active_quests", [])
        if not 0 <= int(quest_index) < len(active):
            return False, "Nie znaleziono Questa."
        quest = active[int(quest_index)]
        success, message = abandon_runtime_quest(player, quest)
        return success, message

    council.available_assets = available_assets_v2
    council._validate_assets = validate_assets_v2
    council.abandon_quest = abandon_quest_v2

    # Moduły te importują funkcje Rady przez `from ... import`, dlatego ich
    # lokalne referencje również trzeba przepiąć.
    council_market._validate_assets = validate_assets_v2
    council_ui.available_assets = available_assets_v2
    council_ui.abandon_quest = abandon_quest_v2
    council_market_ui.available_assets = available_assets_v2

    _INSTALLED = True
