from __future__ import annotations

import math

import pygame

from rg_ui import city_hub


_INSTALLED = False

# Lewy panel jest gotowa grafika z SZESCIOMA widocznymi kafelkami. Ich srodki
# sa wyznaczone przez srodki ikon zapisanych w grafice panelu. Wczesniejszy
# kod dzielil obszar matematycznie (a modul Zakladow dodatkowo dopisywal
# niewidoczny 7. wpis), przez co hitboxy ladowaly pomiedzy prawdziwymi ramkami.
_VISIBLE_ACTIONS = (
    "location_shop",
    "location_tavern",
    "location_board",
    "location_training",
    "location_healing",
    "location_equipment",
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


def install_location_menu_hitbox_fix():
    global _INSTALLED
    if _INSTALLED:
        return

    # Grafika lewego panelu ma tylko 6 przyciskow. Usuwamy niewidoczny wpis
    # location_industry dodawany przez starszy modul produkcji, bo zmienial on
    # geometrie wszystkich pozostalych hitboxow. Sam system Zakladow zostaje w
    # kodzie i moze dostac osobne, widoczne wejscie w UI bez psucia tego panelu.
    city_hub.LOCATION_MENU[:] = [
        (label, action)
        for label, action in city_hub.LOCATION_MENU
        if action != "location_industry"
    ]

    city_hub._menu_button_rects = _menu_button_rects_from_icons
    _INSTALLED = True
