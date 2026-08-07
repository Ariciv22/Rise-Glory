"""Warstwa zgodnosci dla pierwszego questa po migracji do wspolnego silnika."""

from rg_content.quests import SATANIC_FORCES_ID, register_all_quests
from rg_engine.items import normalise_item
from rg_engine.quests import (
    activate_quest as engine_activate_quest,
    complete_quest,
    create_offer,
    current_stage,
    fail_quest,
    find_player_quest as engine_find_player_quest,
    quest_definition,
    resolve_option,
)
from rg_engine.world import current_world_level, register_players
from rg_ui.quest import QuestActionButton, _draw_image, _draw_result_box, _failure_text, draw_quest_panel as generic_draw_quest_panel

register_all_quests()

QUEST_ID = SATANIC_FORCES_ID
QUEST_NAME = "Szatańskie siły"
QUEST_PLACE_ACTION = f"location_quest:{QUEST_ID}"
ARTIUM_NAME = "Artium"
QUEST_TEMPLATE = create_offer(QUEST_ID)
SHORT_SWORD = normalise_item("Krótki miecz")

_definition = quest_definition(QUEST_ID)
STAGES = {
    int(stage["number"]): {
        "title": stage["title"],
        "text": stage["text"],
        "options": list(stage.get("options", [])),
    }
    for stage in _definition.get("stages", [])
}


def create_quest_offer():
    return create_offer(QUEST_ID)


def activate_quest(card=None):
    return engine_activate_quest(card or QUEST_ID)


def is_satanic_forces(quest):
    return isinstance(quest, dict) and quest.get("id") == QUEST_ID


def find_player_quest(player, include_history=True):
    return engine_find_player_quest(player, QUEST_ID, include_history=include_history)


def has_active_quest(player):
    quest = find_player_quest(player, include_history=False)
    return bool(quest and quest.get("status") in {"active", "combat_pending", "combat"})


def _token(player):
    return player.get("_token_ref")


def _complete_quest(player, quest, note=""):
    return complete_quest(player, quest, note)


def _fail_quest(player, quest, note):
    return fail_quest(player, quest, note)


def resolve_test(player, option_index, rng=None):
    quest = find_player_quest(player, include_history=False)
    if not quest:
        return False, "Nie masz aktywnego etapu tego questa."
    return resolve_option(player, quest, option_index, rng=rng)


def resolve_combat_round(player, rng=None):
    from rg_ui.combat import resolve_combat_round as resolve_active_combat

    return resolve_active_combat(rng=rng)


def _draw_cover_image(screen, rect):
    stage = current_stage({"id": QUEST_ID, "stage_number": 1}) or {}
    _draw_image(screen, rect, stage.get("image") or _definition.get("image", ""))


def draw_quest_panel(screen, font, small_font, mouse_pos, content, player):
    return generic_draw_quest_panel(screen, font, small_font, mouse_pos, content, player, QUEST_ID)
