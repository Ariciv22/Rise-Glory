from __future__ import annotations

_INSTALLED = False


def install_quest_world_bridge() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_world
    from rg_engine.quests import reset_quest_deck

    original_generate_world = rg_world.generate_world

    def generate_world_with_fresh_quest_deck(map_key="rosette9"):
        # Oferty są rozkładane podczas generowania lokacji, więc reset musi
        # nastąpić PRZED generowaniem, a nie dopiero przy tworzeniu pionków.
        reset_quest_deck()
        return original_generate_world(map_key)

    rg_world.generate_world = generate_world_with_fresh_quest_deck
    _INSTALLED = True
