from __future__ import annotations

_INSTALLED = False


def install_quest_effect_bridge() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_engine.quests as quest_engine

    original_apply_effect = quest_engine._apply_effect

    def apply_effect_v2(player, quest, effect):
        effect_type = str((effect or {}).get("type") or "")
        if effect_type == "resolve_marker":
            marker_id = str((effect or {}).get("marker_id") or quest.get("current_marker_id") or "")
            if not marker_id:
                return "Brak wskazanego Znacznika Questa."
            if quest_engine.resolve_quest_marker(quest, marker_id):
                if str(quest.get("current_marker_id") or "") == marker_id:
                    quest["current_marker_id"] = None
                return f"Rozwiązano Znacznik Questa {marker_id}."
            return f"Nie znaleziono aktywnego Znacznika Questa {marker_id}."
        return original_apply_effect(player, quest, effect)

    quest_engine._apply_effect = apply_effect_v2
    _INSTALLED = True
