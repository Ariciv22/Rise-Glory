from __future__ import annotations

_INSTALLED = False


def _record(player, quest) -> None:
    if not isinstance(quest, dict):
        return
    if quest.get("_chronicle_recorded"):
        return
    if quest.get("status") not in {"completed", "failed", "abandoned"}:
        return
    from rg_engine.world_chronicle import add_quest_resolution

    add_quest_resolution(player, quest)
    quest["_chronicle_recorded"] = True


def install_quest_chronicle_bridge() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_engine.quests as quest_engine

    original_complete = quest_engine.complete_quest
    original_fail = quest_engine.fail_quest
    original_abandon = quest_engine.abandon_quest

    def complete_with_chronicle(player, quest, *args, **kwargs):
        result = original_complete(player, quest, *args, **kwargs)
        _record(player, quest)
        return result

    def fail_with_chronicle(player, quest, *args, **kwargs):
        result = original_fail(player, quest, *args, **kwargs)
        _record(player, quest)
        return result

    def abandon_with_chronicle(player, quest, *args, **kwargs):
        result = original_abandon(player, quest, *args, **kwargs)
        _record(player, quest)
        return result

    quest_engine.complete_quest = complete_with_chronicle
    quest_engine.fail_quest = fail_with_chronicle
    quest_engine.abandon_quest = abandon_with_chronicle

    # Rada importuje funkcję porzucania jako lokalną referencję.
    try:
        import rg_engine.quest_council_bridge as council_bridge
        council_bridge.abandon_runtime_quest = abandon_with_chronicle
    except (ImportError, AttributeError):
        pass

    _INSTALLED = True
