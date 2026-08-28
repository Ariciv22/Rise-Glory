from __future__ import annotations

import pygame

from rg_content import register_all_world_events
from rg_core.data import ACTIONS_PER_TURN, GOLD, MUTED, PANEL_DARK, TEXT
from rg_engine.dev_quest_tools import (
    add_quest_for_testing,
    clear_active_quests_for_testing,
    developer_quest_rows,
)
from rg_engine.devtools import (
    add_gold,
    change_legend,
    dev_flag,
    heal_all,
    refill_actions,
    reset_devtools,
    set_legend,
    toggle_dev_flag,
)
from rg_engine.world import (
    clear_forced_world_level,
    current_world_level,
    forced_world_level,
    set_forced_world_level,
)
from rg_engine.world_events import (
    DURATION_UNTIL_RESOLVED,
    activate_world_event,
    active_world_event,
    active_world_events,
    draw_next_world_event,
    register_world_event,
)
from rg_ui.common import Button, draw_lines, draw_panel, wrap

register_all_world_events()

FLAG_LABELS = {
    "infinite_actions": "Nieskończone akcje",
    "infinite_gold": "Nieskończone złoto",
    "no_wounds": "Brak Ran",
    "council_every_round": "Rada po każdej rundzie",
}

DEV_PROBLEM_ID = "dev_rozbojnicy_na_trakcie"
_QUEST_ROWS = developer_quest_rows()
_QUEST_SCROLL = 0
_QUEST_VISIBLE_ROWS = 8
_LAST_DRAW_TICKS = -10000


def dev_menu_recently_visible(max_age_ms=180):
    return pygame.time.get_ticks() - int(_LAST_DRAW_TICKS) <= int(max_age_ms)


def scroll_dev_quests(wheel_y):
    """Przewija liste Questow. Dodatnie wheel_y oznacza ruch w gore."""
    global _QUEST_SCROLL
    maximum = max(0, len(_QUEST_ROWS) - int(_QUEST_VISIBLE_ROWS))
    _QUEST_SCROLL = max(0, min(maximum, int(_QUEST_SCROLL) - int(wheel_y)))
    return _QUEST_SCROLL


def _shift_quest_scroll(step):
    global _QUEST_SCROLL
    maximum = max(0, len(_QUEST_ROWS) - int(_QUEST_VISIBLE_ROWS))
    _QUEST_SCROLL = max(0, min(maximum, int(_QUEST_SCROLL) + int(step)))
    return _QUEST_SCROLL


def _button(screen, font, mouse, buttons, text, action, rect, active=False):
    button = Button(text, action, rect)
    button.draw(screen, font, mouse, active=active)
    buttons.append(button)
    return button


def _section_title(screen, font, text, x, y):
    screen.blit(font.render(text, True, GOLD), (x, y))


def _spawn_dev_problem(players):
    existing = next((event for event in active_world_events(DURATION_UNTIL_RESOLVED) if event.get("id") == DEV_PROBLEM_ID), None)
    if existing:
        return existing, "Testowy Problem jest już aktywny na mapie."

    event = {
        "id": DEV_PROBLEM_ID,
        "name": "[DEV] Rozbójnicy na trakcie",
        "description": "Testowy Problem do sprawdzania znacznika, interakcji i panelu stanu świata.",
        "effect_text": "[DEV] Na mapie pojawia się aktywny Problem wymagający interwencji bohatera.",
        "world_level": current_world_level(players),
        "duration": DURATION_UNTIL_RESOLVED,
        "problem": {
            "description": "Rozbójnicy rozbili obóz przy trakcie i zatrzymują podróżnych.",
            "condition": "Dotrzyj do znacznika i zalicz jeden z dostępnych testów.",
            "action_label": "Zajmij się rozbójnikami",
            "reward_hint": "Wdzięczność kupców — dokładna nagroda pozostaje ukryta.",
            "placement": {"type": "random_passable"},
            "fallback": {"type": "random_passable"},
            "reward": {"gold": 3, "legend": 1},
            "methods": [
                {
                    "id": "atak",
                    "label": "Zaatakuj obóz rozbójników",
                    "stat": "Walka",
                    "difficulty": 12,
                    "success_text": "Obóz zostaje rozbity, a trakt ponownie jest bezpieczny.",
                    "failure_text": "Rozbójnicy odpierają atak i zmuszają cię do odwrotu.",
                    "failure": {"wounds": 1},
                },
                {
                    "id": "podstep",
                    "label": "Wkradnij się do obozu podstępem",
                    "stat": "Intryga",
                    "difficulty": 11,
                    "success_text": "Podstęp rozbija bandę bez otwartej walki.",
                    "failure_text": "Plan zostaje odkryty, a za ucieczkę trzeba słono zapłacić.",
                    "failure": {"gold": 2},
                },
            ],
        },
    }
    register_world_event(event)
    activated, message = activate_world_event(DEV_PROBLEM_ID, players)
    return activated, message or "Testowy Problem został aktywowany."


def handle_dev_action(action, hero, token, players):
    action = str(action)
    result = {"message": "", "close": False, "open_council": False}

    if action == "dev_close":
        result["close"] = True
        return result

    if action == "dev_reset":
        reset_devtools()
        clear_forced_world_level()
        result["message"] = "Wyłączono wszystkie opcje programisty i przywrócono automatyczny poziom świata."
        return result

    if action.startswith("dev_add_quest:"):
        number = int(action.split(":", 1)[1])
        _success, message = add_quest_for_testing(hero, number)
        result["message"] = message
        return result

    if action == "dev_clear_active_quests":
        _count, message = clear_active_quests_for_testing(hero)
        result["message"] = message
        return result

    if action.startswith("dev_quest_scroll:"):
        step = int(action.split(":", 1)[1])
        _shift_quest_scroll(step)
        return result

    if action.startswith("dev_toggle:"):
        flag = action.split(":", 1)[1]
        enabled = toggle_dev_flag(flag)
        result["message"] = f"{FLAG_LABELS.get(flag, flag)}: {'WŁ.' if enabled else 'WYŁ.'}"
        return result

    if action.startswith("dev_world:"):
        value = action.split(":", 1)[1]
        if value == "auto":
            clear_forced_world_level()
            result["message"] = f"Poziom świata wrócił do automatycznego wyliczania. Aktualnie: {current_world_level(players)}."
        else:
            level = set_forced_world_level(int(value))
            result["message"] = f"Wymuszono poziom świata {level}."
        return result

    if action == "dev_legend_plus_10":
        value = change_legend(hero, 10)
        result["message"] = f"Legenda aktywnego bohatera: {value}. Poziom świata: {current_world_level(players)}."
        return result

    if action == "dev_legend_minus_10":
        value = change_legend(hero, -10)
        result["message"] = f"Legenda aktywnego bohatera: {value}. Poziom świata: {current_world_level(players)}."
        return result

    if action.startswith("dev_legend_set:"):
        value = set_legend(hero, int(action.split(":", 1)[1]))
        result["message"] = f"Ustawiono Legendę aktywnego bohatera na {value}. Poziom świata: {current_world_level(players)}."
        return result

    if action == "dev_gold_plus_50":
        value = add_gold(hero, 50)
        result["message"] = f"Dodano 50 złota. Stan: {value}."
        return result

    if action == "dev_heal_all":
        healed = heal_all(hero)
        result["message"] = f"Usunięto {healed} Ran."
        return result

    if action == "dev_refill_actions":
        value = refill_actions(token, ACTIONS_PER_TURN)
        result["message"] = f"Akcje odnowione do {value}."
        return result

    if action == "dev_next_event":
        event, message = draw_next_world_event(players)
        if event:
            result["message"] = f"Wydarzenie: {event.get('name', 'Wydarzenie')} — {message or event.get('effect_text', '')}"
        else:
            result["message"] = message
        return result

    if action == "dev_spawn_problem":
        event, message = _spawn_dev_problem(players)
        result["message"] = f"{event.get('name', '[DEV] Problem')} — {message}"
        result["close"] = True
        return result

    if action == "dev_open_council":
        result["open_council"] = True
        result["close"] = True
        result["message"] = "Otwieranie Rady Bohaterów."
        return result

    result["message"] = f"Nieznana akcja programisty: {action}"
    return result


def _draw_quest_picker(screen, small_font, mouse, buttons, hero, panel, right_x, col_w, message_top):
    global _QUEST_VISIBLE_ROWS, _QUEST_SCROLL

    title_y = panel.y + 176
    _section_title(screen, small_font, "QUESTY 1–30 — DODAJ DO TESTU", right_x, title_y)
    active_count = len(hero.get("active_quests", []) or [])
    status = f"Aktywne: {active_count}/3 | kółko myszy przewija listę"
    screen.blit(small_font.render(status, True, MUTED), (right_x, title_y + 27))

    controls_y = title_y + 52
    _button(screen, small_font, mouse, buttons, "▲", "dev_quest_scroll:-1", (right_x, controls_y, 42, 34))
    _button(screen, small_font, mouse, buttons, "▼", "dev_quest_scroll:1", (right_x + 48, controls_y, 42, 34))
    _button(screen, small_font, mouse, buttons, "WYCZYŚĆ AKTYWNE", "dev_clear_active_quests", (right_x + 102, controls_y, col_w - 102, 34))

    list_top = controls_y + 46
    list_bottom = message_top - 12
    list_rect = pygame.Rect(right_x, list_top, col_w, max(120, list_bottom - list_top))
    pygame.draw.rect(screen, PANEL_DARK, list_rect, border_radius=10)
    pygame.draw.rect(screen, GOLD, list_rect, 1, border_radius=10)

    row_h = 39
    gap = 5
    _QUEST_VISIBLE_ROWS = max(3, min(9, (list_rect.height - 12) // (row_h + gap)))
    maximum = max(0, len(_QUEST_ROWS) - _QUEST_VISIBLE_ROWS)
    _QUEST_SCROLL = max(0, min(maximum, _QUEST_SCROLL))

    active_ids = {
        str(quest.get("id") or "")
        for quest in hero.get("active_quests", []) or []
        if isinstance(quest, dict)
    }
    visible = _QUEST_ROWS[_QUEST_SCROLL : _QUEST_SCROLL + _QUEST_VISIBLE_ROWS]
    for row_index, quest in enumerate(visible):
        y = list_rect.y + 7 + row_index * (row_h + gap)
        label = f"Q{quest['number']:02d}  {quest['name']}  [{quest['board_location']}]"
        active = quest["id"] in active_ids
        _button(
            screen,
            small_font,
            mouse,
            buttons,
            label,
            f"dev_add_quest:{quest['number']}",
            (list_rect.x + 8, y, list_rect.width - 28, row_h),
            active=active,
        )

    track = pygame.Rect(list_rect.right - 14, list_rect.y + 8, 6, list_rect.height - 16)
    pygame.draw.rect(screen, (55, 50, 43), track, border_radius=3)
    if len(_QUEST_ROWS) > _QUEST_VISIBLE_ROWS:
        thumb_h = max(28, int(track.height * (_QUEST_VISIBLE_ROWS / len(_QUEST_ROWS))))
        travel = max(1, track.height - thumb_h)
        thumb_y = track.y + int(travel * (_QUEST_SCROLL / maximum)) if maximum else track.y
        pygame.draw.rect(screen, GOLD, (track.x, thumb_y, track.width, thumb_h), border_radius=3)
    else:
        pygame.draw.rect(screen, GOLD, track, border_radius=3)


def draw_dev_menu(screen, title_font, font, small_font, mouse, hero, token, players, round_number, message=""):
    global _LAST_DRAW_TICKS
    _LAST_DRAW_TICKS = pygame.time.get_ticks()

    sw, sh = screen.get_size()
    shade = pygame.Surface((sw, sh), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 205))
    screen.blit(shade, (0, 0))

    width = min(1120, sw - 70)
    height = min(760, sh - 70)
    panel = pygame.Rect((sw - width) // 2, (sh - height) // 2, width, height)
    draw_panel(screen, panel, GOLD)

    buttons = []
    screen.blit(title_font.render("Menu programisty", True, TEXT), (panel.x + 28, panel.y + 20))
    screen.blit(small_font.render("F8 — otwórz / zamknij. Lista Questów jest przewijalna kółkiem myszy.", True, MUTED), (panel.x + 30, panel.y + 70))

    forced = forced_world_level()
    world_mode = f"WYMUSZONY {forced}" if forced is not None else "AUTO"
    actions = int(getattr(token, "actions", 0) or 0) if token is not None else 0
    status = (
        f"Bohater: {hero.get('name', 'Gracz')}   |   Legenda: {hero.get('legend', 0)}   |   "
        f"Poziom świata: {current_world_level(players)} ({world_mode})   |   Złoto: {hero.get('gold', 0)}   |   "
        f"Rany: {hero.get('wounds', 0)}   |   Akcje: {actions}   |   Runda: {round_number}"
    )
    status_rect = pygame.Rect(panel.x + 28, panel.y + 100, panel.width - 56, 54)
    pygame.draw.rect(screen, PANEL_DARK, status_rect, border_radius=10)
    draw_lines(screen, small_font, wrap(small_font, status, status_rect.width - 24)[:2], status_rect.x + 12, status_rect.y + 9, TEXT, line_h=20)

    left_x = panel.x + 30
    right_x = panel.centerx + 18
    col_w = panel.width // 2 - 56

    y = panel.y + 176
    _section_title(screen, font, "Poziom świata", left_x, y)
    y += 32
    button_w = (col_w - 20) // 5
    world_buttons = [("AUTO", "auto"), ("I", "1"), ("II", "2"), ("III", "3"), ("IV", "4")]
    for index, (label, value) in enumerate(world_buttons):
        active = (forced is None and value == "auto") or (forced is not None and str(forced) == value)
        _button(screen, small_font, mouse, buttons, label, f"dev_world:{value}", (left_x + index * (button_w + 5), y, button_w, 38), active=active)

    y = panel.y + 256
    _section_title(screen, font, "Legenda aktywnego bohatera", left_x, y)
    y += 32
    _button(screen, small_font, mouse, buttons, "-10 LP", "dev_legend_minus_10", (left_x, y, 100, 38))
    _button(screen, small_font, mouse, buttons, "+10 LP", "dev_legend_plus_10", (left_x + 108, y, 100, 38))
    set_x = left_x + 218
    for index, value in enumerate((0, 10, 20, 30)):
        _button(screen, small_font, mouse, buttons, str(value), f"dev_legend_set:{value}", (set_x + index * 56, y, 50, 38))

    y = panel.y + 340
    _section_title(screen, font, "Szybkie akcje testowe", left_x, y)
    y += 32
    _button(screen, small_font, mouse, buttons, "+50 złota", "dev_gold_plus_50", (left_x, y, 124, 38))
    _button(screen, small_font, mouse, buttons, "Wylecz wszystko", "dev_heal_all", (left_x + 132, y, 142, 38))
    _button(screen, small_font, mouse, buttons, "Odnów akcje", "dev_refill_actions", (left_x + 282, y, 134, 38))
    y += 46
    _button(screen, small_font, mouse, buttons, "Następne Wydarzenie", "dev_next_event", (left_x, y, 198, 38))
    _button(screen, small_font, mouse, buttons, "Otwórz Radę", "dev_open_council", (left_x + 206, y, 150, 38))
    y += 46
    _button(screen, small_font, mouse, buttons, "[DEV] Dodaj Problem na mapę", "dev_spawn_problem", (left_x, y, 250, 38))

    y = panel.y + 512
    _section_title(screen, font, "Przełączniki", left_x, y)
    y += 32
    flags = ("infinite_actions", "infinite_gold", "no_wounds", "council_every_round")
    flag_w = (col_w - 8) // 2
    for index, flag in enumerate(flags):
        row = index // 2
        col = index % 2
        enabled = dev_flag(flag)
        label = f"{FLAG_LABELS[flag]}: {'WŁ.' if enabled else 'WYŁ.'}"
        _button(
            screen,
            small_font,
            mouse,
            buttons,
            label,
            f"dev_toggle:{flag}",
            (left_x + col * (flag_w + 8), y + row * 48, flag_w, 40),
            active=enabled,
        )

    message_rect = pygame.Rect(panel.x + 28, panel.bottom - 104, panel.width - 56, 50)
    _draw_quest_picker(screen, small_font, mouse, buttons, hero, panel, right_x, col_w, message_rect.y)

    pygame.draw.rect(screen, PANEL_DARK, message_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 110, 116), message_rect, 1, border_radius=10)
    if message:
        draw_lines(screen, small_font, wrap(small_font, message, message_rect.width - 20)[:2], message_rect.x + 10, message_rect.y + 7, TEXT, line_h=19)
    else:
        active_event = active_world_event()
        event_name = active_event.get("name", "brak") if active_event else "brak"
        info = f"Opcje testowe są tymczasowe. Aktywne Wydarzenie Świata: {event_name}."
        screen.blit(small_font.render(info, True, MUTED), (message_rect.x + 10, message_rect.y + 15))

    _button(screen, small_font, mouse, buttons, "WYŁĄCZ WSZYSTKIE OPCJE", "dev_reset", (panel.x + 28, panel.bottom - 44, 250, 34))
    _button(screen, small_font, mouse, buttons, "ZAMKNIJ [F8]", "dev_close", (panel.right - 190, panel.bottom - 44, 162, 34))
    return buttons
