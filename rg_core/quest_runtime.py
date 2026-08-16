from __future__ import annotations

import pygame

from rg_ui.combat import is_combat_active, start_combat
from rg_content import create_enemy, register_all_quests
from rg_engine.heroes import defeat_hero
from rg_engine.quests import (
    resolve_option,
    resolve_pending_combat_defeat,
    resolve_pending_combat_victory,
)
from rg_engine.world import current_world_level, quest_difficulty_from_legend_gap, update_world_level

register_all_quests()


def _allow_keyboard_events():
    try:
        pygame.event.set_allowed(pygame.KEYDOWN)
    except (AttributeError, pygame.error):
        pass


def _block_keyboard_events():
    try:
        pygame.event.set_blocked(pygame.KEYDOWN)
    except (AttributeError, pygame.error):
        pass


def _update_world_after_legend_change(player, previous_legend):
    if int(player.get("legend", 0) or 0) != int(previous_legend or 0):
        update_world_level()


def start_pending_quest_combat(player, quest):
    pending = dict(quest.get("pending_combat") or {})
    enemy_id = pending.get("enemy_id")
    if not enemy_id:
        return False, "Quest nie posiada oczekującej walki."
    if is_combat_active():
        return False, "Inna walka jest już aktywna."

    enemy = create_enemy(enemy_id, current_world_level())
    enemy["return_action"] = f"location_quest:{quest.get('id')}"
    token = player.get("_token_ref")

    def on_victory(combat_log):
        _allow_keyboard_events()
        previous_legend = int(player.get("legend", 0) or 0)
        quest["last_result"] = resolve_pending_combat_victory(player, quest, combat_log)
        _update_world_after_legend_change(player, previous_legend)

    def on_defeat(combat_log):
        _allow_keyboard_events()
        result = defeat_hero(player, token, current_world_level(), lose_gold=True)
        details = " ".join(part for part in [combat_log, result.get("message", "")] if part).strip()
        quest["last_result"] = resolve_pending_combat_defeat(player, quest, details)

    def on_escape(combat_log):
        _allow_keyboard_events()
        quest["status"] = "active"
        quest["pending_combat"] = None
        quest["last_result"] = combat_log

    started, message = start_combat(
        player,
        enemy,
        on_victory=on_victory,
        on_defeat=on_defeat,
        on_escape=on_escape,
        intro_text=quest.get("last_result", "Rozpoczyna się walka."),
        metadata={"context_label": f"Quest: {quest.get('name', 'Quest')}"},
    )
    if not started:
        quest["status"] = "active"
        return False, message
    quest["status"] = "combat"
    quest["last_result"] = message
    _block_keyboard_events()
    return True, message


def resolve_quest_option(player, quest, option_index, rng=None):
    """Rozstrzyga opcję Questa razem z anty-farmingowym skalowaniem Legendy.

    Do normalnego progu testu dokładamy +2 za każdy poziom, o który osobista
    Ranga Legendy bohatera przewyższa aktualny Poziom Świata. Modyfikator nie
    zwiększa nagrody i działa tylko na bieżący test; kara kolejnego testu
    zapisana w `difficulty_modifier` pozostaje niezależna.
    """
    previous_legend = int(player.get("legend", 0) or 0)
    persistent_modifier = int(quest.get("difficulty_modifier", 0) or 0)
    legend_modifier = quest_difficulty_from_legend_gap(player)
    quest["difficulty_modifier"] = persistent_modifier + legend_modifier

    success, message = resolve_option(player, quest, option_index, rng=rng)
    _update_world_after_legend_change(player, previous_legend)

    if quest.get("status") == "combat_pending":
        started, combat_message = start_pending_quest_combat(player, quest)
        return False, combat_message if started else message
    return success, message
