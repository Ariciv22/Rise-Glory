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
)
from rg_ui import hud, world_state
from rg_ui.combat import is_combat_active
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


def _world_state_slot(rect):
    """Dokladnie ten sam obszar, ktory wykorzystuje Wydarzenia Swiata."""
    width = min(230, max(190, rect.width // 4))
    return pygame.Rect(
        rect.right - width - 16,
        rect.y + max(4, (rect.height - 34) // 2),
        width,
        34,
    )


def _draw_tile_economy(screen, font, small_font, hero, token, selected_tile, mouse):
    _ = font
    rect = game_layout_rects(screen)["bottom"]
    if rect.width <= 300 or rect.height <= 0:
        return []

    # Moduly Wydarzen Swiata rysuja ten sam dolny panel przed nami. Gospodarka
    # moze odswiezyc jego tlo, ale prawa czesc jest na stale zarezerwowana dla
    # przycisku Wydarzen i na koncu rysujemy go ponownie ponad naszym panelem.
    draw_image_panel(screen, rect, 2)
    pad = 18
    state_rect = _world_state_slot(rect)

    if selected_tile is None:
        text_w = max(80, state_rect.x - pad - (rect.x + pad))
        line1 = "POTENCJAŁ HEKSA: wybierz heks na mapie."
        line2 = str(hero.get("_map_message", ""))
        screen.blit(
            small_font.render(_shorten(small_font, line1, text_w), True, TEXT),
            (rect.x + pad, rect.y + 12),
        )
        if line2:
            screen.blit(
                small_font.render(_shorten(small_font, line2, text_w), True, MUTED),
                (rect.x + pad, rect.y + 36),
            )
        world_state._draw_state_button(screen, small_font, rect)
        return []

    value = potential(selected_tile)
    site = getattr(selected_tile, "production_site", None)
    on_tile = token is not None and getattr(token, "tile", None) is selected_tile
    can_build = (
        on_tile
        and site is None
        and value.get("material")
        and player_has_right(hero, selected_tile)
    )

    button_w = min(220, max(165, int(rect.width * 0.18)))
    action_rect = None
    if can_build:
        action_rect = pygame.Rect(
            state_rect.x - pad - button_w,
            rect.y + max(6, (rect.height - 38) // 2),
            button_w,
            38,
        )
        text_right = action_rect.x - pad
    else:
        text_right = state_rect.x - pad
    text_w = max(80, text_right - (rect.x + pad))

    line1 = (
        f"Heks {selected_tile.id}: {selected_tile.terrain['name']} | "
        f"POTENCJAŁ: {potential_summary(selected_tile)} | "
        f"Jurysdykcja: {getattr(selected_tile, 'jurisdiction_name', None) or 'brak'}"
    )
    if site:
        status = "aktywny" if site.get("status") == "active" else "w budowie"
        line2 = f"{site.get('name', 'Zakład')} ({status}) | Właściciel: {site_owner_label(site)}"
    else:
        right_name = getattr(selected_tile, "extraction_right_owner_name", None) or "wolne"
        line2 = f"Zakład: brak | Prawo eksploatacji: {right_name}"

    if can_build:
        line2 = f"{line2} | {build_cost_text(hero, selected_tile)}"

    message = str(hero.get("_map_message", ""))
    if message:
        line2 = f"{line2} | {message}"

    y1 = rect.y + max(8, (rect.height - 44) // 2)
    screen.blit(
        small_font.render(_shorten(small_font, line1, text_w), True, TEXT),
        (rect.x + pad, y1),
    )
    screen.blit(
        small_font.render(_shorten(small_font, line2, text_w), True, MUTED),
        (rect.x + pad, y1 + 24),
    )

    buttons = []
    if can_build and action_rect is not None:
        button = ProductionActionButton(
            "Buduj zakład",
            f"production_build:{selected_tile.id}",
            action_rect,
            lambda: start_site_construction(hero, token, selected_tile),
            hero,
        )
        button.draw(screen, small_font, mouse)
        buttons.append(button)

    # Nie rysujemy juz placeholdera "Przejmij (ALFA)". Lezal dokladnie na
    # hitboxie Wydarzen Swiata, a sama funkcja przejecia i tak byla atrapą.
    # Prawa czesc dolnego HUD-u nalezy wylacznie do Wydarzen Swiata.
    world_state._draw_state_button(screen, small_font, rect)
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

    # Pelnoekranowe nakladki musza pozostac ostatnia warstwa. Nie rysujemy na
    # nich dolnego HUD-u gospodarki ani jego niewidocznych hitboxow.
    if hud.is_player_board_open() or world_state.is_world_state_open() or is_combat_active():
        return buttons

    buttons.extend(
        _draw_tile_economy(
            screen,
            font,
            small_font,
            hero,
            token,
            selected_tile,
            pygame.mouse.get_pos(),
        )
    )
    return buttons


def install_production_hud(app_module=None):
    global _INSTALLED
    if _INSTALLED:
        return
    hud.draw_game_ui = draw_game_ui_with_production
    if app_module is not None:
        app_module.draw_game_ui = draw_game_ui_with_production

    # Ta poprawka jest instalowana tutaj, bo production_hud jest pierwszym
    # pozniejszym modulem mapy uruchamianym po kompletnym lancuchu setupu
    # (Wydarzenia Swiata, Zagrozenia i Questy sa juz wtedy opakowane).
    from rg_ui.map_ui_regression_fixes import install_map_ui_regression_fixes

    install_map_ui_regression_fixes(app_module)
    _INSTALLED = True
