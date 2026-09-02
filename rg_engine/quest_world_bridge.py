from __future__ import annotations

_INSTALLED = False


def install_quest_world_bridge() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_world
    import rg_world.generation as generation
    from rg_engine.quests import reset_quest_deck

    original_generate_world = rg_world.generate_world
    original_try_generate_world = generation._try_generate_world

    def try_generate_world_with_fresh_quest_deck(map_key, rng):
        # Generator moze odrzucic kilka map zanim znajdzie poprawny uklad
        # jurysdykcji i Zakladow. Kazda taka proba tworzy 9 lokacji i rezerwuje
        # Questy na ich Tablicach, dlatego talia musi byc czyszczona PRZED
        # KAZDA proba, a nie tylko raz przed calym generate_world().
        reset_quest_deck()
        return original_try_generate_world(map_key, rng)

    generation._try_generate_world = try_generate_world_with_fresh_quest_deck

    def generate_world_with_fresh_quest_deck(map_key="rosette9"):
        # Pierwszy reset usuwa stan poprzedniej rozgrywki. Kolejne resety sa
        # wykonywane przez wrapper _try_generate_world przy kazdej probie mapy.
        reset_quest_deck()
        return original_generate_world(map_key)

    rg_world.generate_world = generate_world_with_fresh_quest_deck
    _INSTALLED = True
