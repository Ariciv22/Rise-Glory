from __future__ import annotations

_INSTALLED = False


def install_quest_effect_bridge() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_engine.quests as quest_engine

    original_apply_effect = quest_engine._apply_effect
    original_check_requirements = quest_engine._check_requirements

    def check_requirements_v2(player, quest, option):
        option = option or {}

        # Wymagana lokacja jest regułą silnika, nie tylko filtrem UI.
        # Bez tego dało się otworzyć Quest z planszetki bohatera i wykonać
        # etap przeznaczony np. dla Artium stojąc na pustkowiu.
        stage = quest_engine.current_stage(quest) or {}
        definition = quest_engine.quest_definition(str(quest.get("id") or "")) or {}
        required_location = stage.get("required_location") or definition.get("required_location")
        if required_location:
            token = player.get("_token_ref")
            tile = getattr(token, "tile", None)
            location = getattr(tile, "location", None)
            current_location = location.get("name") if isinstance(location, dict) else None
            if quest_engine._normalize(required_location) != quest_engine._normalize(current_location):
                return False, f"Ten etap Questa można wykonać tylko w lokacji: {required_location}."

        requires = option.get("requires") or {}
        effects = [*(option.get("success_effects") or []), *(option.get("failure_effects") or [])]
        needs_marker = bool(requires.get("quest_marker") or requires.get("current_marker")) or any(
            str((effect or {}).get("type") or "") == "resolve_marker" for effect in effects
        )
        if needs_marker:
            marker_id = str(quest.get("current_marker_id") or "")
            if not marker_id:
                return False, "Tę opcję można wykonać tylko na właściwym Znaczniku Questa."
            try:
                from rg_world.quest_markers import marker_tile

                target_tile = marker_tile(marker_id)
            except (ImportError, AttributeError):
                target_tile = None
            token = player.get("_token_ref")
            current_tile = getattr(token, "tile", None)
            if target_tile is None or current_tile is None:
                return False, "Nie odnaleziono aktywnego Znacznika Questa na mapie."
            if int(getattr(target_tile, "id", -1)) != int(getattr(current_tile, "id", -2)):
                return False, "Musisz znajdować się na heksie właściwego Znacznika Questa."
        return original_check_requirements(player, quest, option)

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

    quest_engine._check_requirements = check_requirements_v2
    quest_engine._apply_effect = apply_effect_v2
    _INSTALLED = True
