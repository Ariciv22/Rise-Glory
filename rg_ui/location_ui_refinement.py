from __future__ import annotations

import pygame

from rg_ui import city_hub
from rg_ui import location_right_panel_content


_INSTALLED = False
_ACTIVE_CONTEXT = None
_FONT_CACHE = {}

_MENU_LABELS = {
    "location_shop": "Sklep",
    "location_tavern": "Karczma",
    "location_board": "Tablica ogłoszeń",
    "location_training": "Trening",
    "location_healing": "Leczenie",
    "location_industry": "Gildia",
    "location_equipment": "Gildia",
    "back_to_map": "Powrót na mapę",
}


def _font(size: int, bold: bool = False):
    size = max(14, int(size))
    key = (size, bool(bold))
    cached = _FONT_CACHE.get(key)
    if cached is not None:
        return cached
    try:
        cached = pygame.font.SysFont("georgia", size, bold=bold)
    except pygame.error:
        cached = pygame.font.Font(None, size)
        cached.set_bold(bool(bold))
    _FONT_CACHE[key] = cached
    return cached


def _fit_font(text: str, max_size: int, min_size: int, max_width: int, bold: bool = False):
    size = max(min_size, int(max_size))
    while size > min_size:
        candidate = _font(size, bold=bold)
        if candidate.size(text)[0] <= max_width:
            return candidate
        size -= 1
    return _font(min_size, bold=bold)


def _draw_menu_label(screen, button, mouse_pos, selected_place):
    action = str(getattr(button, "action", ""))
    text = _MENU_LABELS.get(action)
    if not text:
        return

    rect = pygame.Rect(button.rect)
    # Ikona zajmuje lewa czesc kafla. Przykrywamy tylko stary napis zapisany
    # w lewy_ui.png, bez dotykania ikony i zlotej ramki.
    cover_left = rect.x + int(round(rect.width * 0.275))
    cover_right = rect.right - int(round(rect.width * 0.055))
    cover_top = rect.y + int(round(rect.height * 0.14))
    cover_bottom = rect.bottom - int(round(rect.height * 0.14))
    cover = pygame.Rect(
        cover_left,
        cover_top,
        max(1, cover_right - cover_left),
        max(1, cover_bottom - cover_top),
    )

    shade = pygame.Surface(cover.size, pygame.SRCALPHA)
    shade.fill((10, 10, 9, 238))
    screen.blit(shade, cover.topleft)

    max_size = max(20, int(round(rect.height * 0.42)))
    min_size = max(17, int(round(rect.height * 0.24)))
    label_font = _fit_font(
        text,
        max_size=max_size,
        min_size=min_size,
        max_width=max(1, cover.width - 10),
        bold=False,
    )

    active_action = selected_place or "location_shop"
    highlighted = rect.collidepoint(mouse_pos) or action == active_action
    color = city_hub._GOLD_HOVER if highlighted else city_hub._GOLD_TEXT
    shadow = label_font.render(text, True, (34, 24, 14))
    label = label_font.render(text, True, color)
    target = label.get_rect(midleft=(cover.x + 5, rect.centery))
    screen.blit(shadow, (target.x + 1, target.y + 2))
    screen.blit(label, target)


def _draw_art_contained(screen, path, rect: pygame.Rect) -> bool:
    """Pokazuje caly asset w zlotej ramce prawego UI bez cropowania."""
    source = city_hub._load_asset(path)
    rect = pygame.Rect(rect)
    if source is None or rect.width <= 0 or rect.height <= 0:
        return False

    iw, ih = source.get_size()
    if iw <= 0 or ih <= 0:
        return False

    scale = min(rect.width / iw, rect.height / ih)
    size = (
        max(1, int(round(iw * scale))),
        max(1, int(round(ih * scale))),
    )
    image = (
        source
        if source.get_size() == size
        else pygame.transform.smoothscale(source, size)
    )

    target = image.get_rect(center=rect.center)
    old_clip = screen.get_clip()
    screen.set_clip(rect)
    screen.blit(image, target)
    screen.set_clip(old_clip)
    return True


def _selected_section_name(selected_place) -> str:
    action = str(selected_place or "location_shop")
    return _MENU_LABELS.get(action, "Sklep")


def _top_bar_text(location, selected_place) -> str:
    location_name = str((location or {}).get("name") or "Lokacja").upper()
    section = _selected_section_name(selected_place).upper()
    return f"{location_name}  •  {section}"


def _bottom_bar_text(player) -> str:
    player = player or {}
    gold = int(player.get("gold", 0) or 0)
    legend = int(player.get("legend", 0) or 0)
    hp = int(player.get("hp", 0) or 0)
    max_hp = int(player.get("max_hp", 10) or 10)
    wounds = int(player.get("wounds", 0) or 0)
    return f"Złoto: {gold}  •  Legenda: {legend}  •  HP: {hp}/{max_hp}  •  Rany: {wounds}/4"


def _draw_centered_bar_text(screen, rect, text, top_bar: bool):
    if not text:
        return

    rect = pygame.Rect(rect)
    max_size = min(27 if top_bar else 21, max(16, int(round(rect.height * (0.27 if top_bar else 0.34)))))
    min_size = 16 if top_bar else 14
    side_pad = max(38, int(round(rect.width * 0.14)))
    bar_font = _fit_font(
        str(text),
        max_size=max_size,
        min_size=min_size,
        max_width=max(1, rect.width - side_pad * 2),
        bold=top_bar,
    )

    color = city_hub._GOLD_TEXT if top_bar else city_hub.city.MUTED
    shadow = bar_font.render(str(text), True, (26, 18, 10))
    label = bar_font.render(str(text), True, color)
    target = label.get_rect(center=rect.center)
    screen.blit(shadow, (target.x + 2, target.y + 2))
    screen.blit(label, target)


def install_location_ui_refinement() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    original_draw_left_menu = city_hub._draw_left_menu
    original_edge_bar = city_hub._draw_edge_bar
    original_draw_location_hub_screen = city_hub.draw_location_hub_screen

    def draw_left_menu(screen, font, mouse_pos, selected_place, rect):
        buttons = original_draw_left_menu(
            screen,
            font,
            mouse_pos,
            selected_place,
            rect,
        )
        for button in buttons:
            _draw_menu_label(screen, button, mouse_pos, selected_place)
        return buttons

    def draw_edge_bar(screen, rect, message=""):
        # Najpierw zostawiamy caly istniejacy ornament/panel2.png.
        original_edge_bar(screen, rect, "")

        context = _ACTIVE_CONTEXT
        top_bar = pygame.Rect(rect).centery < screen.get_height() // 2
        text = str(message or "").strip()
        if not text and context:
            location, player, selected_place = context
            text = (
                _top_bar_text(location, selected_place)
                if top_bar
                else _bottom_bar_text(player)
            )
        _draw_centered_bar_text(screen, rect, text, top_bar=top_bar)

    def draw_location_hub_screen(
        screen,
        title_font,
        font,
        small_font,
        mouse_pos,
        location,
        player,
        selected_place=None,
        message="",
    ):
        global _ACTIVE_CONTEXT
        previous = _ACTIVE_CONTEXT
        _ACTIVE_CONTEXT = (location, player, selected_place)
        try:
            return original_draw_location_hub_screen(
                screen,
                title_font,
                font,
                small_font,
                mouse_pos,
                location,
                player,
                selected_place,
                message,
            )
        finally:
            _ACTIVE_CONTEXT = previous

    city_hub._draw_left_menu = draw_left_menu
    city_hub._draw_edge_bar = draw_edge_bar
    city_hub._draw_bottom_bar = draw_edge_bar
    city_hub.draw_location_hub_screen = draw_location_hub_screen

    # location_right_panel_content wywoluje swoja funkcje globalnie przy kazdej
    # klatce, wiec podmiana tutaj automatycznie dotyczy Sklepu, Karczmy,
    # Tablicy, Treningu, Leczenia i Gildii.
    location_right_panel_content._draw_cover = _draw_art_contained

    city_hub._rise_glory_location_ui_refinement_installed = True
    _INSTALLED = True
