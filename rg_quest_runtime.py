from __future__ import annotations

import pygame

from rg_combat import is_combat_active, start_combat
from rg_content import create_enemy, register_all_quests
from rg_engine.heroes import defeat_hero
from rg_engine.quests import complete_quest, fail_quest, resolve_option
from rg_engine.world import current_world_level

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


def start_pending_quest_combat(player, quest):
    pending = dict(quest.get("pending_combat") or {})
    enemy_id = pending.get("enemy_id")
    if not enemy_id:
        return False, "Quest nie posiada oczekujacej walki."
    if is_combat_active():
        return False, "Inna walka jest juz aktywna."

    enemy = create_enemy(enemy_id, current_world_level())
    enemy["return_action"] = f"location_quest:{quest.get('id')}"
    token = player.get("_token_ref")

    def on_victory(combat_log):
        _allow_keyboard_events()
        quest["pending_combat"] = None
        complete_quest(player, quest, f"{combat_log} Klątwa zostaje złamana.")

    def on_defeat(combat_log):
        _allow_keyboard_events()
        result = defeat_hero(player, token, current_world_level(), lose_gold=True)
        quest["pending_combat"] = None
        fail_quest(player, quest, f"{combat_log} {result['message']} Quest przegrany.")

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
        intro_text=quest.get("last_result", "Rozpoczyna sie walka."),
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
    success, message = resolve_option(player, quest, option_index, rng=rng)
    if quest.get("status") == "combat_pending":
        started, combat_message = start_pending_quest_combat(player, quest)
        return False, combat_message if started else message
    return success, message
