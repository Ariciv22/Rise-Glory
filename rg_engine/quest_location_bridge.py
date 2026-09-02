from __future__ import annotations

import random
import sys

_INSTALLED = False
_TRACKED_LOCATIONS: list[dict] = []


def clear_tracked_quest_locations() -> None:
    """Czyści referencje Tablic z poprzedniej wygenerowanej mapy."""
    _TRACKED_LOCATIONS.clear()


def tracked_quest_locations() -> list[dict]:
    return list(_TRACKED_LOCATIONS)


def _track_location(location: dict) -> None:
    if not isinstance(location, dict):
        return
    if all(existing is not location for existing in _TRACKED_LOCATIONS):
        _TRACKED_LOCATIONS.append(location)


def install_quest_location_bridge() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_content.locations as locations
    from rg_engine.quests import create_offer, draw_quest_id, return_quest_id_to_deck
    from rg_engine.world import current_world_level, register_world_level_change_hook

    original_initialize = locations.initialize_location

    def _draw_offer(visible, rng, location_name=None, world_level=None):
        blocked = [str(card.get("id")) for card in visible if isinstance(card, dict) and card.get("id")]
        quest_id = draw_quest_id(
            int(current_world_level() if world_level is None else world_level),
            unavailable_ids=blocked,
            rng=rng,
            location_name=location_name,
        )
        return create_offer(quest_id) if quest_id else None

    def _release_visible_offers(location, rng):
        for card in list(location.get("quest_offers", []) or []):
            if isinstance(card, dict) and card.get("id"):
                return_quest_id_to_deck(str(card["id"]), rng=rng)
        location["quest_offers"] = []

    def _refresh_board(location, level, rng=None):
        rng = rng or random
        _release_visible_offers(location, rng)
        offers = []
        location_name = location.get("name")
        for _ in range(3):
            offer = _draw_offer(
                offers,
                rng,
                location_name=location_name,
                world_level=level,
            )
            if offer is None:
                break
            offers.append(offer)
        location["quest_offers"] = offers
        location["quest_offer_world_level"] = int(level)
        location["quest_v2_ready"] = True
        return location

    def initialize_location_v2(location, rng=None):
        rng = rng or random
        # Bazowy initializer odpowiada za sklep, Pomocnikow ORAZ pierwsze trzy
        # finalne Questy przypisane do tej konkretnej Tablicy Ogloszen. Nie
        # losujemy ich drugi raz, bo wtedy pierwsza trojka pozostawalaby
        # zarezerwowana w talii mimo ze nie bylaby juz widoczna graczowi.
        original_initialize(location, rng)
        _track_location(location)
        level = int(current_world_level() or 1)

        if not location.get("quest_v2_ready"):
            location["quest_v2_ready"] = True
            location["quest_offer_world_level"] = level
            return location

        if int(location.get("quest_offer_world_level", level) or level) == level:
            return location

        # Bezpiecznik dla zapisow/starszych runtime'ow: jesli lokacja zostanie
        # otwarta juz po awansie, jej Tablica i tak natychmiast dogoni poziom.
        return _refresh_board(location, level, rng)

    def _world_level_changed(_previous, level):
        # Decyzja projektowa ALFY: niewziete oferty znikaja NATYCHMIAST po
        # akcji, ktora awansowala swiat. Przyjete Questy sa w stanie graczy,
        # wiec ta operacja ich nie dotyka. Zagrozenia/Wydarzenia tez pozostaja.
        for location in list(_TRACKED_LOCATIONS):
            if location.get("offers_ready"):
                _refresh_board(location, int(level), random)

    def take_quest_v2(location, player, slot_index, rng=None):
        rng = rng or random
        initialize_location_v2(location, rng)
        offers = location.setdefault("quest_offers", [])
        if slot_index < 0 or slot_index >= len(offers):
            return False, "Nieprawidlowy slot Questa."

        quest = offers[slot_index]
        success, message = locations.accept_quest_card(player, quest)
        if not success:
            return False, message

        visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
        replacement = _draw_offer(
            visible_without_slot,
            rng,
            location_name=location.get("name"),
        )
        if replacement is None:
            offers.pop(slot_index)
        else:
            offers[slot_index] = replacement
        return True, message

    locations.initialize_location = initialize_location_v2
    locations.take_quest = take_quest_v2
    register_world_level_change_hook(_world_level_changed)

    # Te moduly wczesniej zaimportowaly funkcje przez `from ... import`.
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
