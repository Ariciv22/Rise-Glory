from __future__ import annotations

import pygame

from rg_core.data import GOLD, MUTED, PANEL_DARK, TEXT
from rg_engine.production import potential, potential_summary, site_owner_label, world_tile
from rg_engine.world_events import movement_cost_with_world_event
from rg_ui.common import Button, draw_image_panel, game_layout_rects, wrap
from rg_ui.player_board import is_player_board_open
from rg_world.quest_places import quest_places_on_tile


_KIND_LABELS = {
    "city": "Miasto",
    "village": "Wieś",
    "castle": "Zamek",
}

_PLACE_CACHE: dict[int, list[dict]] = {}
_PLACE_SIGNATURE: tuple[str, ...] | None = None


class HexInfoButton(Button):
    """Przycisk panelu heksa z wariantem nieaktywnym."""

    def __init__(self, text, action, rect, enabled=True):
        super().__init__(text, action, rect)
        self.enabled = bool(enabled)

    def draw(self, screen, font, mouse_pos, active=False):
        draw_image_panel(screen, self.rect, 2)
        hovered = self.enabled and self.rect.collidepoint(mouse_pos)

        if hovered or active:
            glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            glow.fill((255, 218, 132, 24 if hovered else 14))
            screen.blit(glow, self.rect.topleft)

        if not self.enabled:
            shade = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            shade.fill((0, 0, 0, 118))
            screen.blit(shade, self.rect.topleft)

        color = TEXT if self.enabled else MUTED
        label = font.render(self.text, True, color)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.enabled and super().clicked(pos)


def hex_info_panel_rect(screen):
    """Panel siedzi po prawej stronie pola mapy, przed stałą tabelą graczy."""
    layout = game_layout_rects(screen)
    center = layout["center"]
    bottom = layout["bottom"]

    width = min(370, max(286, int(center.width * 0.34)))
    available_h = max(360, center.height - bottom.height - 48)
    height = min(530, available_h)
    return pygame.Rect(
        center.right - width - 18,
        center.y + 22,
        width,
        height,
    )


def _draw_wrapped(screen, font, text, x, y, width, color, bottom, line_gap=3):
    line_h = font.get_height() + line_gap
    for line in wrap(font, text, width):
        if y + font.get_height() > bottom:
            return y, False
        screen.blit(font.render(line, True, color), (x, y))
        y += line_h
    return y, True


def _draw_section_title(screen, font, text, x, y, width, bottom):
    if y + font.get_height() + 7 > bottom:
        return y, False
    screen.blit(font.render(text, True, GOLD), (x, y))
    y += font.get_height() + 4
    pygame.draw.line(screen, GOLD, (x, y), (x + width, y), 1)
    return y + 7, True


def _jurisdiction_tiles(location):
    result = []
    for tile_id in location.get("jurisdiction_tile_ids", []):
        tile = world_tile(tile_id)
        if tile is not None:
            result.append(tile)
    return result


def _jurisdiction_economy(location):
    tiles = _jurisdiction_tiles(location)
    sites = []
    free_rights = 0
    owned_rights = 0

    for tile in tiles:
        site = getattr(tile, "production_site", None)
        if site:
            sites.append(site)
            continue
        if getattr(tile, "location", None):
            continue
        if not potential(tile).get("material"):
            continue
        if getattr(tile, "extraction_right_owner", None) is None:
            free_rights += 1
        else:
            owned_rights += 1

    mines = [site for site in sites if str(site.get("name", "")).casefold().startswith("kopalnia")]
    return {
        "tile_count": len(tiles),
        "sites": sites,
        "mine_count": len(mines),
        "free_rights": free_rights,
        "owned_rights": owned_rights,
    }


def _places_signature():
    try:
        from rg_content.quest_runtime_ext import quest_created_places

        return tuple(sorted(str(place.get("id") or "") for place in quest_created_places()))
    except (ImportError, AttributeError, TypeError):
        return ()


def _places_on_tile(tile):
    global _PLACE_SIGNATURE
    signature = _places_signature()
    if signature != _PLACE_SIGNATURE:
        _PLACE_SIGNATURE = signature
        _PLACE_CACHE.clear()

    tile_id = int(getattr(tile, "id", -1))
    if tile_id not in _PLACE_CACHE:
        _PLACE_CACHE[tile_id] = list(quest_places_on_tile(tile))
    return list(_PLACE_CACHE[tile_id])


def _movement_cost(tile):
    base = int(tile.terrain.get("move", 1) or 1)
    actual = int(movement_cost_with_world_event(base))
    if actual == base:
        return str(actual)
    return f"{actual} (bazowo {base})"


def draw_hex_info_panel(screen, font, small_font, hero, token, selected_tile, mouse_pos):
    """Rysuje stały panel szczegółów wybranego heksa i zwraca jego przyciski."""
    if selected_tile is None or is_player_board_open():
        return []

    rect = hex_info_panel_rect(screen)
    draw_image_panel(screen, rect, 5)

    inner = rect.inflate(-22, -22)
    pygame.draw.rect(screen, PANEL_DARK, inner, border_radius=9)
    pygame.draw.rect(screen, GOLD, inner, 1, border_radius=9)

    location = getattr(selected_tile, "location", None)
    places = _places_on_tile(selected_tile)
    title = str(location.get("name")) if location else f"Heks {selected_tile.id}"
    subtitle_parts = [f"Heks {selected_tile.id}", str(selected_tile.terrain.get("name", "Teren"))]
    if location:
        subtitle_parts.insert(1, _KIND_LABELS.get(str(location.get("kind")), str(location.get("type_name") or "Lokacja")))

    header = pygame.Rect(inner.x + 8, inner.y + 8, inner.width - 16, 62)
    draw_image_panel(screen, header, 2)
    title_surface = font.render(title, True, TEXT)
    if title_surface.get_width() > header.width - 66:
        title_surface = small_font.render(title, True, TEXT)
    screen.blit(title_surface, (header.x + 16, header.y + 10))
    subtitle = " • ".join(subtitle_parts)
    subtitle_surface = small_font.render(subtitle, True, MUTED)
    if subtitle_surface.get_width() > header.width - 32:
        while subtitle and small_font.size(subtitle + "...")[0] > header.width - 32:
            subtitle = subtitle[:-1]
        subtitle_surface = small_font.render(subtitle.rstrip() + "...", True, MUTED)
    screen.blit(subtitle_surface, (header.x + 16, header.y + 36))

    close_button = HexInfoButton(
        "X",
        "close_hex_info",
        (header.right - 36, header.y + 13, 26, 26),
    )
    close_button.draw(screen, small_font, mouse_pos)
    buttons = [close_button]

    on_tile = token is not None and getattr(token, "tile", None) is selected_tile
    action_h = 44 if location else 0
    action_gap = 12 if location else 0
    content_bottom = inner.bottom - 12 - action_h - action_gap
    content_x = inner.x + 18
    content_w = inner.width - 36
    y = header.bottom + 16

    rows = [
        f"Teren: {selected_tile.terrain.get('name', '-')}",
        f"Koszt ruchu: {_movement_cost(selected_tile)}",
        f"Potencjał: {potential_summary(selected_tile)}",
        f"Jurysdykcja: {getattr(selected_tile, 'jurisdiction_name', None) or 'brak'}",
    ]
    for row in rows:
        y, ok = _draw_wrapped(screen, small_font, row, content_x, y, content_w, TEXT, content_bottom)
        if not ok:
            break

    y += 5
    y, ok = _draw_section_title(screen, small_font, "GOSPODARKA HEKSA", content_x, y, content_w, content_bottom)
    if ok:
        site = getattr(selected_tile, "production_site", None)
        if site:
            status = "aktywny" if site.get("status") == "active" else "w budowie"
            economy_rows = [
                f"Zakład: {site.get('name', 'Zakład')} ({status})",
                f"Właściciel: {site_owner_label(site)}",
            ]
        else:
            right_owner = getattr(selected_tile, "extraction_right_owner_name", None) or "wolne"
            economy_rows = ["Zakład na heksie: brak", f"Prawo eksploatacji: {right_owner}"]

        for row in economy_rows:
            y, row_ok = _draw_wrapped(screen, small_font, row, content_x, y, content_w, MUTED, content_bottom)
            if not row_ok:
                ok = False
                break

    if ok and location:
        y += 5
        y, ok = _draw_section_title(screen, small_font, "JURYSDYKCJA LOKACJI", content_x, y, content_w, content_bottom)
        if ok:
            economy = _jurisdiction_economy(location)
            summary = (
                f"Heksy: {economy['tile_count']} | Zakłady: {len(economy['sites'])} | "
                f"Kopalnie: {economy['mine_count']}"
            )
            y, ok = _draw_wrapped(screen, small_font, summary, content_x, y, content_w, TEXT, content_bottom)
            if ok:
                rights = f"Wolne prawa: {economy['free_rights']} | Zajęte prawa: {economy['owned_rights']}"
                y, ok = _draw_wrapped(screen, small_font, rights, content_x, y, content_w, MUTED, content_bottom)
            if ok:
                for site in economy["sites"][:3]:
                    y, site_ok = _draw_wrapped(
                        screen,
                        small_font,
                        f"• {site.get('name', 'Zakład')}",
                        content_x + 6,
                        y,
                        content_w - 6,
                        MUTED,
                        content_bottom,
                    )
                    if not site_ok:
                        ok = False
                        break
                remaining = len(economy["sites"]) - 3
                if ok and remaining > 0:
                    y, ok = _draw_wrapped(
                        screen,
                        small_font,
                        f"• +{remaining} kolejnych zakładów",
                        content_x + 6,
                        y,
                        content_w - 6,
                        MUTED,
                        content_bottom,
                    )

    if ok and (location or places):
        y += 5
        y, ok = _draw_section_title(screen, small_font, "OBIEKTY NA HEKSIE", content_x, y, content_w, content_bottom)
        if ok and location:
            kind = _KIND_LABELS.get(str(location.get("kind")), str(location.get("type_name") or "Lokacja"))
            y, ok = _draw_wrapped(
                screen,
                small_font,
                f"• {kind}: {location.get('name', 'Lokacja')}",
                content_x + 6,
                y,
                content_w - 6,
                TEXT,
                content_bottom,
            )
        if ok:
            for place in places:
                y, place_ok = _draw_wrapped(
                    screen,
                    small_font,
                    f"• Miejsce: {place.get('name', 'Miejsce')}",
                    content_x + 6,
                    y,
                    content_w - 6,
                    MUTED,
                    content_bottom,
                )
                if not place_ok:
                    break

    if location:
        action_rect = pygame.Rect(inner.x + 18, inner.bottom - 56, inner.width - 36, 42)
        location_name = str(location.get("name") or "lokacji")
        if on_tile:
            text = f"Wejdź: {location_name}"
        else:
            text = "Podejdź na heks, aby wejść"
        enter_button = HexInfoButton(
            text,
            "enter_selected_location",
            action_rect,
            enabled=on_tile,
        )
        enter_button.draw(screen, small_font, mouse_pos)
        buttons.append(enter_button)

    return buttons
