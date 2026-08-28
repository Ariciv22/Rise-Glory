from __future__ import annotations

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_engine.production import (
    build_cost_text,
    player_has_right,
    potential,
    potential_summary,
    site_owner_label,
    start_site_construction,
    takeover_placeholder,
)
from rg_ui import hud
from rg_ui.common import Button, draw_image_panel, game_layout_rects


_INSTALLED = False
_ORIGINAL_DRAW_GAME_UI = hud.draw_game_ui


class ProductionActionButton(Button):
    def __init__(self, text, action, rect, callback, hero):
        super().__init__(text, action, rect)
        self.callback = callback
        self.hero = hero

    def clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        success, message = self.callback()
        self.hero["_map_message"] = message
        self.last_success = success
        self.last_message = message
        return True


def _shorten(font, text, max_width):
    value = str(text)
    if font.size(value)[0] <= max_width:
        return value
    suffix = "..."
    while value and font.size(value + suffix)[0] > max_width:
        value = value[:-1]
    return value.rstrip() + suffix


def _draw_tile_economy(screen, font, small_font, hero, token, selected_tile, mouse):
    rect = game_layout_rects(screen)["bottom"]
    if rect.width <= 300 or rect.height <= 0:
        return []

    draw_image_panel(screen, rect, 2)
    pad = 18
    button_w = min(230, max(170, int(rect.width * 0.22)))
    text_w = rect.width - button_w - pad * 3

    if selected_tile is None:
        line1 = "POTENCJAŁ HEKSA: wybierz heks na mapie."
        line2 = str(hero.get("_map_message", ""))
        screen.blit(small_font.render(_shorten(small_font, line1, text_w), True, TEXT), (rect.x + pad, rect.y + 12))
        if line2:
            screen.blit(small_font.render(_shorten(small_font, line2, text_w), True, MUTED), (rect.x + pad, rect.y + 36))
        return []

    value = potential(selected_tile)
    line1 = (
        f"Heks {selected_tile.id}: {selected_tile.terrain['name']} | "
        f"POTENCJAŁ: {potential_summary(selected_tile)} | "
        f"Jurysdykcja: {getattr(selected_tile, 'jurisdiction_name', None) or 'brak'}"
    )
    site = getattr(selected_tile, "production_site", None)
    if site:
        status = "aktywny" if site.get("status") == "active" else "w budowie"
        line2 = f"{site.get('name', 'Zakład')} ({status}) | Właściciel: {site_owner_label(site)}"
    else:
        right_name = getattr(selected_tile, "extraction_right_owner_name", None) or "wolne"
        line2 = f"Zakład: brak | Prawo eksploatacji: {right_name}"

    message = str(hero.get("_map_message", ""))
    if message:
        line2 = f"{line2} | {message}"

    y1 = rect.y + max(8, (rect.height - 44) // 2)
    screen.blit(small_font.render(_shorten(small_font, line1, text_w), True, TEXT), (rect.x + pad, y1))
    screen.blit(small_font.render(_shorten(small_font, line2, text_w), True, MUTED), (rect.x + pad, y1 + 24))

    buttons = []
    on_tile = token is not None and getattr(token, "tile", None) is selected_tile
    action_rect = pygame.Rect(rect.right - button_w - pad, rect.y + max(5, (rect.height - 42) // 2), button_w, 42)

    if (
        on_tile
        and site is None
        and value.get("material")
        and player_has_right(hero, selected_tile)
    ):
        button = ProductionActionButton(
            "Buduj zakład",
            f"production_build:{selected_tile.id}",
            action_rect,
            lambda: start_site_construction(hero, token, selected_tile),
            hero,
        )
        button.draw(screen, small_font, mouse)
        buttons.append(button)
        cost = build_cost_text(hero, selected_tile)
        hint = small_font.render(_shorten(small_font, cost, button_w), True, GOLD)
        screen.blit(hint, hint.get_rect(midbottom=(action_rect.centerx, action_rect.y - 2)))
    elif on_tile and site is not None:
        own = site.get("owner_type") == "player" and int(site.get("owner_player_number", 0) or 0) == int(hero.get("player_number", 0) or 0)
        if not own:
            button = ProductionActionButton(
                "Przejmij (ALFA)",
                f"production_takeover:{selected_tile.id}",
                action_rect,
                lambda: takeover_placeholder(hero, token, selected_tile),
                hero,
            )
            button.draw(screen, small_font, mouse)
            buttons.append(button)

    return buttons


def draw_game_ui_with_production(
    screen,
    font,
    small_font,
    hero,
    token,
    selected_tile,
    current_map,
    active_player_index,
    players,
    tokens,
    round_number,
    council_cycle,
):
    buttons = _ORIGINAL_DRAW_GAME_UI(
        screen,
        font,
        small_font,
        hero,
        token,
        selected_tile,
        current_map,
        active_player_index,
        players,
        tokens,
        round_number,
        council_cycle,
    )
    buttons = list(buttons or [])

    # Planszetka bohatera jest pełnoekranową nakładką. Nie dokładamy na nią
    # dolnego panelu gospodarki ani niewidocznych przycisków z mapy.
    if hud.is_player_board_open():
        return buttons

    buttons.extend(_draw_tile_economy(screen, font, small_font, hero, token, selected_tile, pygame.mouse.get_pos()))
    return buttons


def install_production_hud(app_module=None):
    global _INSTALLED
    if _INSTALLED:
        return
    hud.draw_game_ui = draw_game_ui_with_production
    if app_module is not None:
        app_module.draw_game_ui = draw_game_ui_with_production
    _INSTALLED = True
