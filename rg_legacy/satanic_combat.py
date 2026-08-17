"""Zgodnosc starego API walki questa z nowym silnikiem danych."""

from rg_content.quests import SATANIC_FORCES_ID
from rg_engine.quests import find_player_quest as engine_find_player_quest
from rg_core.quest_runtime import resolve_quest_option, start_pending_quest_combat
from rg_ui.quest import draw_quest_panel as generic_draw_quest_panel

QUEST_ID = SATANIC_FORCES_ID
QUEST_NAME = "Szatańskie siły"
QUEST_PLACE_ACTION = f"location_quest:{QUEST_ID}"


def _quest(player, include_history=True):
    return engine_find_player_quest(player, QUEST_ID, include_history=include_history)


def find_player_quest(player, include_history=True):
    return _quest(player, include_history)


def has_active_quest(player):
    quest = _quest(player, include_history=False)
    return bool(quest and quest.get("status") in {"active", "combat_pending", "combat"})


def begin_cursed_soldier_combat(player, action_already_paid=False, reason=""):
    quest = _quest(player, include_history=False)
    if not quest or int(quest.get("stage_number", 0) or 0) != 3:
        return False, "Walke mozna rozpoczac wylacznie w trzecim etapie questa."
    if reason:
        quest["last_result"] = reason
    if quest.get("status") == "combat_pending":
        return start_pending_quest_combat(player, quest)
    if action_already_paid:
        quest["status"] = "combat_pending"
        quest["pending_combat"] = {"enemy_id": "przeklety_zolnierz", "action_paid": True}
        return start_pending_quest_combat(player, quest)
    success, message = resolve_quest_option(player, quest, 2)
    if quest.get("status") == "combat":
        return True, message
    return success, message


def resolve_final_option(player, option_index, rng=None):
    quest = _quest(player, include_history=False)
    if not quest:
        return False, "Nie masz aktywnego questa."
    return resolve_quest_option(player, quest, option_index, rng=rng)


def draw_quest_panel(screen, font, small_font, mouse_pos, content, player):
    return generic_draw_quest_panel(screen, font, small_font, mouse_pos, content, player, QUEST_ID)
