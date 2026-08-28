from __future__ import annotations

import pygame

from rg_ui import city_hub
from rg_ui import location_menu_hitbox_fix


_INSTALLED = False
_ORIGINAL_DRAW_LEFT_MENU = city_hub._draw_left_menu
_FONT_CACHE = {}


def _guild_font(size):
    size = max(14, int(size))
    cached = _FONT_CACHE.get(size)
    if cached is not None:
        return cached
    try:
        font = pygame.font.SysFont("georgia", size)
    except pygame.error:
        font = pygame.font.Font(None, size)
    _FONT_CACHE[size] = font
    return font


def _draw_guild_label(screen, button_rect):
    """Przykrywa napis Ekwipunek zapisany w assetcie i rysuje Gildia.

    Nie ruszamy ramki ani ikony szostego kafelka. Po przygotowaniu osobnego
    assetu Gildii ta nakladka moze zostac usunieta bez zmian w logice menu.
    """
    text_left = button_rect.x + int(button_rect.width * 0.30)
    text_right = button_rect.right - int(button_rect.width * 0.08)
    text_top = button_rect.y + int(button_rect.height * 0.20)
    text_bottom = button_rect.bottom - int(button_rect.height * 0.18)
    cover = pygame.Rect(
        text_left,
        text_top,
        max(1, text_right - text_left),
        max(1, text_bottom - text_top),
    )

    # Wnetrze kafelka jest prawie czarne. Opaque fill calkowicie usuwa stary
    # napis z PNG, a niewielki gradient/tekstura panelu pozostaje widoczna
    # dookola bez naruszania zlotej ramki.
    pygame.draw.rect(screen, (12, 12, 11), cover)

    font = _guild_font(button_rect.height * 0.31)
    label = font.render("Gildia", True, city_hub._GOLD_TEXT)
    label_rect = label.get_rect(
        midleft=(
            text_left + int(button_rect.width * 0.015),
            button_rect.centery,
        )
    )
    screen.blit(label, label_rect)


def _draw_left_menu_with_guild(screen, font, mouse_pos, selected_place, rect):
    buttons = _ORIGINAL_DRAW_LEFT_MENU(
        screen,
        font,
        mouse_pos,
        selected_place,
        rect,
    )

    for button in buttons:
        if getattr(button, "action", None) == "location_industry":
            _draw_guild_label(screen, button.rect)
            break
    return buttons


def install_location_guild_menu():
    global _INSTALLED
    if _INSTALLED:
        return

    # Szosty widoczny kafelek nie jest juz Ekwipunkiem. Otwiera istniejacy
    # ekran gospodarczy z zakladami oraz prawami do eksploatacji heksow.
    menu = []
    guild_added = False
    for label, action in city_hub.LOCATION_MENU:
        if action == "location_equipment":
            if not guild_added:
                menu.append(("Gildia", "location_industry"))
                guild_added = True
            continue
        if action == "location_industry":
            if not guild_added:
                menu.append(("Gildia", "location_industry"))
                guild_added = True
            continue
        menu.append((label, action))

    if not guild_added:
        # Aktualny layout ma szesc kafelkow. Gdyby starsza konfiguracja nie
        # miala Ekwipunku, Gildia zajmuje ostatni wolny slot.
        menu = menu[:5] + [("Gildia", "location_industry")]

    city_hub.LOCATION_MENU[:] = menu[:6]

    # Precyzyjny system hitboxow korzysta z tej listy przy kazdym renderze,
    # wiec szosty hitbox zachowuje geometrie dawnego Ekwipunku, ale prowadzi
    # juz do Gildii.
    location_menu_hitbox_fix._VISIBLE_ACTIONS = (
        "location_shop",
        "location_tavern",
        "location_board",
        "location_training",
        "location_healing",
        "location_industry",
    )

    city_hub._draw_left_menu = _draw_left_menu_with_guild
    _INSTALLED = True
