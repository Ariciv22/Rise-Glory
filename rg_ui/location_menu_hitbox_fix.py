from __future__ import annotations

import math

import pygame

from rg_ui import city_hub


_INSTALLED = False
_ORIGINAL_DRAW_LEFT_MENU = city_hub._draw_left_menu
_FONT_CACHE = {}

# Lewy panel jest gotowa grafika z SZESCIOMA widocznymi kafelkami. Ich srodki
# sa wyznaczone przez srodki ikon zapisanych w grafice panelu. Szosty kafelek
# jest od teraz Gildia i prowadzi do istniejacego ekranu praw eksploatacji.
_VISIBLE_ACTIONS = (
    "location_shop",
    "location_tavern",
    "location_board",
    "location_training",
    "location_healing",
    "location_industry",
)

# Proporcje sa mierzone wzgledem calego lewego panelu. Kazdy hitbox jest
# centrowany na ikonie danego kafelka i obejmuje cala widoczna ramke, lacznie
# z jej skrajnymi pikselami.
_TILE_CENTER_Y = (0.115, 0.243, 0.370, 0.499, 0.626, 0.754)
_TILE_HALF_HEIGHT = 0.058
_TILE_LEFT = 0.097
_TILE_RIGHT = 0.907

_BACK_CENTER_Y = 0.916
_BACK_HALF_HEIGHT = 0.056
_BACK_LEFT = 0.097
_BACK_RIGHT = 0.907


def _ratio_rect(panel_rect, left_ratio, right_ratio, center_y_ratio, half_height_ratio):
    left = int(math.floor(panel_rect.x + panel_rect.width * left_ratio))
    right = int(math.ceil(panel_rect.x + panel_rect.width * right_ratio))
    center_y = panel_rect.y + panel_rect.height * center_y_ratio
    half_h = panel_rect.height * half_height_ratio
    top = int(math.floor(center_y - half_h))
    bottom = int(math.ceil(center_y + half_h))

    # pygame.Rect ma prawa i dolna krawedz wylaczna. +1 sprawia, ze ostatni
    # piksel widocznej ramki rowniez reaguje na klikniecie.
    return pygame.Rect(
        left,
        top,
        max(1, right - left + 1),
        max(1, bottom - top + 1),
    )


def _visible_menu_entries():
    by_action = {action: (label, action) for label, action in city_hub.LOCATION_MENU}
    return [by_action[action] for action in _VISIBLE_ACTIONS if action in by_action]


def _menu_button_rects_from_icons(left_rect):
    entries = _visible_menu_entries()
    rows = []

    for index, (label, action) in enumerate(entries):
        if index >= len(_TILE_CENTER_Y):
            break
        rows.append(
            (
                label,
                action,
                _ratio_rect(
                    left_rect,
                    _TILE_LEFT,
                    _TILE_RIGHT,
                    _TILE_CENTER_Y[index],
                    _TILE_HALF_HEIGHT,
                ),
            )
        )

    back = _ratio_rect(
        left_rect,
        _BACK_LEFT,
        _BACK_RIGHT,
        _BACK_CENTER_Y,
        _BACK_HALF_HEIGHT,
    )
    return rows, back


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
    """Przykrywa napis Ekwipunek zapisany w PNG i rysuje Gildia."""
    text_left = button_rect.x + int(button_rect.width * 0.30)
    text_right = button_rect.right - int(button_rect.width * 0.08)
    text_top = button_rect.y + int(button_rect.height * 0.19)
    text_bottom = button_rect.bottom - int(button_rect.height * 0.17)
    cover = pygame.Rect(
        text_left,
        text_top,
        max(1, text_right - text_left),
        max(1, text_bottom - text_top),
    )

    # Wnetrze assetu jest niemal czarne. Przykrywamy tylko stary napis,
    # pozostawiajac cala zlota ramke oraz obecna ikone nietkniete.
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


def _replace_equipment_with_guild():
    menu = []
    guild_added = False

    for label, action in city_hub.LOCATION_MENU:
        if action in {"location_equipment", "location_industry"}:
            if not guild_added:
                menu.append(("Gildia", "location_industry"))
                guild_added = True
            continue
        menu.append((label, action))

    if not guild_added:
        # Aktualny panel ma piec pozostalych kategorii + szosty slot Gildii.
        menu = menu[:5] + [("Gildia", "location_industry")]

    city_hub.LOCATION_MENU[:] = menu[:6]


def install_location_menu_hitbox_fix():
    global _INSTALLED
    if _INSTALLED:
        return

    # Modul produkcji moze przed nami dodac techniczny wpis location_industry.
    # Skladamy go z dawnym Ekwipunkiem do jednego, widocznego szostego kafelka.
    _replace_equipment_with_guild()

    city_hub._menu_button_rects = _menu_button_rects_from_icons
    city_hub._draw_left_menu = _draw_left_menu_with_guild
    _INSTALLED = True
