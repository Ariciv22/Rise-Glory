from __future__ import annotations

import pygame

from rg_engine.production import (
    available_right_tiles,
    buy_extraction_right,
    buy_location_site,
    location_sites,
    player_has_right,
    potential_summary,
    right_price,
    site_owner_label,
)
from rg_ui import city_hub


_INSTALLED = False
_ORIGINAL_RIGHT_CONTENT = city_hub._draw_right_content


class IndustryActionButton(city_hub.city.Button):
    def __init__(self, text, rect, callback, player):
        super().__init__(text, "location_industry", rect)
        self.callback = callback
        self.player = player

    def clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        success, message = self.callback()
        self.player["_location_message"] = message
        self.last_success = success
        self.last_message = message
        return True


def _fit(font, value, width):
    text = str(value)
    if font.size(text)[0] <= width:
        return text
    suffix = "..."
    while text and font.size(text + suffix)[0] > width:
        text = text[:-1]
    return text.rstrip() + suffix


def _menu_button_rects_with_industry(left_rect):
    """Starszy fallback geometrii; docelowe 6 hitboxow ustawia osobny modul."""
    button_x = left_rect.x + int(left_rect.width * 0.10)
    button_w = int(left_rect.width * 0.82)
    top = left_rect.y + int(left_rect.height * 0.055)
    back_h = max(28, int(left_rect.height * 0.085))
    back_y = left_rect.bottom - int(left_rect.height * 0.055) - back_h
    count = max(1, len(city_hub.LOCATION_MENU))
    available = max(1, back_y - top - int(left_rect.height * 0.04))
    step = max(34, available // count)
    button_h = max(28, min(int(left_rect.height * 0.085), step - 6))

    rows = []
    for index, (label, action) in enumerate(city_hub.LOCATION_MENU):
        rows.append(
            (
                label,
                action,
                pygame.Rect(button_x, top + index * step, button_w, button_h),
            )
        )
    back = pygame.Rect(button_x, back_y, button_w, back_h)
    return rows, back


def _draw_site_row(screen, small_font, mouse, buttons, location, player, site, rect):
    pygame.draw.rect(screen, (20, 19, 17), rect, border_radius=7)
    pygame.draw.rect(screen, (112, 77, 37), rect, 1, border_radius=7)

    title = _fit(small_font, site.get("name", "Zakład"), rect.width - 16)
    screen.blit(small_font.render(title, True, city_hub._GOLD_TEXT), (rect.x + 8, rect.y + 7))

    meta = f"H{site.get('tile_id')} | {site.get('potential_level')} k{site.get('die')} | {site.get('material')}"
    screen.blit(small_font.render(_fit(small_font, meta, rect.width - 16), True, city_hub.city.MUTED), (rect.x + 8, rect.y + 28))

    owner = site_owner_label(site)
    screen.blit(small_font.render(_fit(small_font, owner, rect.width - 96), True, city_hub.city.TEXT), (rect.x + 8, rect.y + 49))

    player_number = int(player.get("player_number", 0) or 0)
    if site.get("owner_type") == "location":
        price = int(site.get("purchase_price", 0) or 0)
        button = IndustryActionButton(
            f"Kup {price}",
            (rect.right - 84, rect.y + 43, 76, 28),
            lambda site_id=site.get("id"): buy_location_site(location, player, site_id),
            player,
        )
        button.draw(screen, small_font, mouse)
        buttons.append(button)
    elif site.get("owner_type") == "player" and int(site.get("owner_player_number", 0) or 0) == player_number:
        label = small_font.render("TWÓJ", True, (144, 205, 133))
        screen.blit(label, label.get_rect(midright=(rect.right - 9, rect.y + 57)))


def _draw_right_row(screen, small_font, mouse, buttons, location, player, tile, rect):
    pygame.draw.rect(screen, (19, 20, 19), rect, border_radius=7)
    pygame.draw.rect(screen, (80, 78, 68), rect, 1, border_radius=7)
    text = f"H{tile.id} | {potential_summary(tile)}"
    screen.blit(small_font.render(_fit(small_font, text, rect.width - 92), True, city_hub.city.TEXT), (rect.x + 8, rect.y + 8))

    owner_name = getattr(tile, "extraction_right_owner_name", None)
    if owner_name:
        owned = player_has_right(player, tile)
        status = "Masz prawo" if owned else f"Prawo: {owner_name}"
        color = (144, 205, 133) if owned else city_hub.city.MUTED
        screen.blit(small_font.render(_fit(small_font, status, rect.width - 16), True, color), (rect.x + 8, rect.y + 31))
        return

    price = right_price(tile)
    button = IndustryActionButton(
        f"Prawo {price}",
        (rect.right - 84, rect.y + 16, 76, 30),
        lambda tile_id=tile.id: buy_extraction_right(location, player, tile_id),
        player,
    )
    button.draw(screen, small_font, mouse)
    buttons.append(button)


def _draw_industry(screen, font, small_font, mouse, location, player, right_rect):
    content = city_hub.right_content_rect(right_rect)
    buttons = []
    x = content.x
    width = content.width
    y = content.y

    title = font.render("Gildia", True, city_hub._GOLD_TEXT)
    screen.blit(title, (x, y))
    y += title.get_height() + 8

    sites = location_sites(location)
    if not sites:
        screen.blit(small_font.render("Brak zakładów lokacji.", True, city_hub.city.MUTED), (x, y))
        y += 30
    else:
        for site in sites[:3]:
            row = pygame.Rect(x, y, width, 78)
            _draw_site_row(screen, small_font, mouse, buttons, location, player, site, row)
            y += 84

    y += 4
    header = small_font.render("Prawa do eksploatacji", True, city_hub._GOLD_TEXT)
    screen.blit(header, (x, y))
    y += header.get_height() + 7

    rights = available_right_tiles(location)
    available_height = max(0, content.bottom - y)
    row_h = 56
    max_rows = max(0, available_height // (row_h + 5))
    visible = rights[:max_rows]
    if not visible:
        screen.blit(small_font.render("Brak wolnych heksów z potencjałem.", True, city_hub.city.MUTED), (x, y))
    else:
        for tile in visible:
            row = pygame.Rect(x, y, width, row_h)
            _draw_right_row(screen, small_font, mouse, buttons, location, player, tile, row)
            y += row_h + 5
        if len(rights) > len(visible):
            more = small_font.render(f"+{len(rights) - len(visible)} kolejnych heksów", True, city_hub.city.MUTED)
            screen.blit(more, (x, min(y, content.bottom - more.get_height())))
    return buttons


def _draw_right_content_with_industry(
    screen,
    font,
    small_font,
    mouse_pos,
    location,
    player,
    selected_place,
    rect,
):
    if selected_place == "location_industry":
        return _draw_industry(screen, font, small_font, mouse_pos, location, player, rect)
    return _ORIGINAL_RIGHT_CONTENT(
        screen,
        font,
        small_font,
        mouse_pos,
        location,
        player,
        selected_place,
        rect,
    )


def install_production_location_hub():
    global _INSTALLED
    if _INSTALLED:
        return
    if not any(action == "location_industry" for _label, action in city_hub.LOCATION_MENU):
        city_hub.LOCATION_MENU.append(("Gildia", "location_industry"))
    city_hub._menu_button_rects = _menu_button_rects_with_industry
    city_hub._draw_right_content = _draw_right_content_with_industry
    _INSTALLED = True
