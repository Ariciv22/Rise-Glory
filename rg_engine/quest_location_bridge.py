from __future__ import annotations

import random
import sys

_INSTALLED = False


def install_quest_location_bridge() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_content.locations as locations
    from rg_engine.quests import create_offer, draw_quest_id, return_quest_id_to_deck
    from rg_engine.world import current_world_level

    original_initialize = locations.initialize_location

    def _draw_offer(visible, rng):
        blocked = [str(card.get("id")) for card in visible if isinstance(card, dict) and card.get("id")]
        quest_id = draw_quest_id(current_world_level(), unavailable_ids=blocked, rng=rng)
        return create_offer(quest_id) if quest_id else None

    def _release_visible_offers(location, rng):
        for card in list(location.get("quest_offers", []) or []):
            if isinstance(card, dict) and card.get("id"):
                return_quest_id_to_deck(str(card["id"]), rng=rng)
        location["quest_offers"] = []

    def initialize_location_v2(location, rng=None):
        rng = rng or random
        # Stary initializer nadal odpowiada za sklep i Pomocników. Jego stare
        # Questy-kategorie są tylko tymczasowo tworzone i zaraz zastępowane;
        # nie podmieniamy jego prywatnego _draw_quest, żeby nie rezerwować kart
        # nowej talii dwa razy.
        original_initialize(location, rng)
        level = int(current_world_level() or 1)

        if location.get("quest_v2_ready") and int(location.get("quest_offer_world_level", level) or level) == level:
            return location

        if location.get("quest_v2_ready"):
            # Niewzięte karty starego poziomu wracają do właściwej talii. Już
            # posiadane Questy pozostają u bohaterów zgodnie z zasadami.
            _release_visible_offers(location, rng)

        offers = []
        for _ in range(3):
            offer = _draw_offer(offers, rng)
            if offer is None:
                break
            offers.append(offer)
        location["quest_offers"] = offers
        location["quest_v2_ready"] = True
        location["quest_offer_world_level"] = level
        return location

    def take_quest_v2(location, player, slot_index, rng=None):
        rng = rng or random
        initialize_location_v2(location, rng)
        offers = location.setdefault("quest_offers", [])
        if slot_index < 0 or slot_index >= len(offers):
            return False, "Nieprawidłowy slot Questa."

        quest = offers[slot_index]
        success, message = locations.accept_quest_card(player, quest)
        if not success:
            return False, message

        visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
        replacement = _draw_offer(visible_without_slot, rng)
        if replacement is None:
            offers.pop(slot_index)
        else:
            offers[slot_index] = replacement
        return True, message

    locations.initialize_location = initialize_location_v2
    locations.take_quest = take_quest_v2

    # Te moduły wcześniej zaimportowały funkcje przez `from ... import`.
    try:
        import rg_world.generation as generation
        generation.initialize_location = initialize_location_v2
    except (ImportError, AttributeError):
        pass

    try:
        import rg_ui.city as city
        city.initialize_location = initialize_location_v2
    except (ImportError, AttributeError):
        pass

    app = sys.modules.get("rg_core.app")
    if app is not None:
        app.take_quest = take_quest_v2

    legacy_app = sys.modules.get("rg_location_data")
    if legacy_app is not None:
        legacy_app.initialize_location = initialize_location_v2
        legacy_app.take_quest = take_quest_v2

    _INSTALLED = True
