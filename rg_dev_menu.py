from __future__ import annotations

import pygame

from rg_content import register_all_world_events
from rg_data import ACTIONS_PER_TURN, GOLD, MUTED, PANEL_DARK, TEXT
from rg_engine.devtools import (
    DEV_FLAGS,
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
from rg_engine.world_events import active_world_event, draw_next_world_event
from rg_ui import Button, draw_lines, draw_panel, wrap

register_all_world_events()

FLAG_LABELS = {
    "infinite_actions": "Nieskończone akcje",
    "infinite_gold": "Nieskończone złoto",
    "no_wounds": "Brak Ran",
    "council_every_round": "Rada po każdej rundzie",
}


def _button(screen, font, mouse, buttons, text, action, rect, active=False):
    button = Button(text, action, rect)
    button.draw(screen, font, mouse, active=active)
    buttons.append(button)
    return button


def _section_title(screen, font, text, x, y):
    screen.blit(font.render(text, True, GOLD), (x, y))


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

    if action == "dev_open_council":
        result["open_council"] = True
        result["close"] = True
        result["message"] = "Otwieranie Rady Bohaterów."
        return result

    result["message"] = f"Nieznana akcja programisty: {action}"
    return result


def draw_dev_menu(screen, title_font, font, small_font, mouse, hero, token, players, round_number, message=""):
    sw, sh = screen.get_size()
    shade = pygame.Surface((sw, sh), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 205))
    screen.blit(shade, (0, 0))

    width = min(1040, sw - 70)
    height = min(760, sh - 70)
    panel = pygame.Rect((sw - width) // 2, (sh - height) // 2, width, height)
    draw_panel(screen, panel, GOLD)

    buttons = []
    screen.blit(title_font.render("Menu programisty", True, TEXT), (panel.x + 28, panel.y + 20))
    screen.blit(small_font.render("F8 — otwórz / zamknij. Narzędzia działają tylko w bieżącej sesji.", True, MUTED), (panel.x + 30, panel.y + 70))

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
    right_x = panel.centerx + 10
    col_w = panel.width // 2 - 50
    y = panel.y + 176

    _section_title(screen, font, "Poziom świata", left_x, y)
    y += 36
    button_w = (col_w - 20) // 5
    world_buttons = [("AUTO", "auto"), ("I", "1"), ("II", "2"), ("III", "3"), ("IV", "4")]
    for index, (label, value) in enumerate(world_buttons):
        active = (forced is None and value == "auto") or (forced is not None and str(forced) == value)
        _button(screen, small_font, mouse, buttons, label, f"dev_world:{value}", (left_x + index * (button_w + 5), y, button_w, 38), active=active)

    y += 56
    _section_title(screen, font, "Legenda aktywnego bohatera", left_x, y)
    y += 36
    _button(screen, small_font, mouse, buttons, "-10 LP", "dev_legend_minus_10", (left_x, y, 100, 38))
    _button(screen, small_font, mouse, buttons, "+10 LP", "dev_legend_plus_10", (left_x + 108, y, 100, 38))
    set_x = left_x + 222
    for index, value in enumerate((0, 10, 20, 30)):
        _button(screen, small_font, mouse, buttons, str(value), f"dev_legend_set:{value}", (set_x + index * 58, y, 52, 38))

    y += 66
    _section_title(screen, font, "Szybkie akcje testowe", left_x, y)
    y += 36
    _button(screen, small_font, mouse, buttons, "+50 złota", "dev_gold_plus_50", (left_x, y, 130, 40))
    _button(screen, small_font, mouse, buttons, "Wylecz wszystko", "dev_heal_all", (left_x + 138, y, 150, 40))
    _button(screen, small_font, mouse, buttons, "Odnów akcje", "dev_refill_actions", (left_x + 296, y, 140, 40))
    y += 50
    _button(screen, small_font, mouse, buttons, "Następne Wydarzenie Świata", "dev_next_event", (left_x, y, 252, 42))
    _button(screen, small_font, mouse, buttons, "Otwórz Radę teraz", "dev_open_council", (left_x + 262, y, 174, 42))

    y2 = panel.y + 176
    _section_title(screen, font, "Przełączniki", right_x, y2)
    y2 += 40
    for flag in ("infinite_actions", "infinite_gold", "no_wounds", "council_every_round"):
        enabled = dev_flag(flag)
        label = f"{FLAG_LABELS[flag]}: {'WŁ.' if enabled else 'WYŁ.'}"
        _button(screen, small_font, mouse, buttons, label, f"dev_toggle:{flag}", (right_x, y2, col_w, 44), active=enabled)
        y2 += 54

    y2 += 10
    _section_title(screen, font, "Aktywne Wydarzenie Świata", right_x, y2)
    y2 += 34
    active_event = active_world_event()
    event_rect = pygame.Rect(right_x, y2, col_w, 100)
    pygame.draw.rect(screen, PANEL_DARK, event_rect, border_radius=10)
    pygame.draw.rect(screen, GOLD, event_rect, 1, border_radius=10)
    if active_event:
        lines = [active_event.get("name", "Wydarzenie"), active_event.get("effect_text", "")]
    else:
        lines = ["Brak aktywnego wydarzenia."]
    draw_lines(screen, small_font, wrap(small_font, " — ".join(lines), event_rect.width - 20)[:4], event_rect.x + 10, event_rect.y + 10, TEXT, line_h=20)

    message_rect = pygame.Rect(panel.x + 28, panel.bottom - 104, panel.width - 56, 50)
    pygame.draw.rect(screen, PANEL_DARK, message_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 110, 116), message_rect, 1, border_radius=10)
    if message:
        draw_lines(screen, small_font, wrap(small_font, message, message_rect.width - 20)[:2], message_rect.x + 10, message_rect.y + 7, TEXT, line_h=19)
    else:
        screen.blit(small_font.render("Opcje testowe nie są zapisywane jako normalne zasady gry.", True, MUTED), (message_rect.x + 10, message_rect.y + 15))

    _button(screen, small_font, mouse, buttons, "WYŁĄCZ WSZYSTKIE OPCJE", "dev_reset", (panel.x + 28, panel.bottom - 44, 250, 34))
    _button(screen, small_font, mouse, buttons, "ZAMKNIJ [F8]", "dev_close", (panel.right - 190, panel.bottom - 44, 162, 34))
    return buttons
