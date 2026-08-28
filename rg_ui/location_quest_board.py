from __future__ import annotations

from pathlib import Path
from typing import Callable

import pygame

from rg_content.locations import take_quest
from rg_ui import city, city_hub


ROOT_DIR = city.ROOT_DIR
BUTTON_UI_DIR = ROOT_DIR / "Grafiki" / "buttony_panele_lokacji"
QUEST_ICON_FILE = BUTTON_UI_DIR / "quest.png"
BOARD_ART_CANDIDATES = (
    ROOT_DIR / "Grafiki" / "RISE&GLORY" / "Ekrany_miast_wsi_zamkow" / "tablica ogłoszeń wieś.png",
    ROOT_DIR / "Grafiki" / "RISE&GLORY" / "Ekrany_miast_wsi_zamkow" / "tablica ogloszen wies.png",
)

_GOLD = (196, 151, 78)
_GOLD_HOVER = (231, 184, 94)
_TEXT = (236, 224, 199)
_MUTED = (173, 160, 136)
_DARK = (12, 11, 10)
_DARK_SOFT = (20, 18, 15)

_INSTALLED = False
_OPEN_QUEST_LOCATION_KEY: str | None = None
_OPEN_QUEST_INDEX: int | None = None


class _HitboxButton(city.Button):
    """Niewidzialny przycisk. Wyglad rysuje panel, a ten obiekt obsluguje klik."""

    def __init__(self, action, rect, callback: Callable[[], None] | None = None):
        super().__init__("", action, rect)
        self.callback = callback

    def draw(self, screen, font, mouse_pos, active=False):
        _ = (screen, font, mouse_pos, active)

    def clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        if self.callback is not None:
            self.callback()
        return True


class _QuestModalButton(city.Button):
    def __init__(self, text, rect, callback: Callable[[], None]):
        # Zostawiamy action=location_board, aby glowna petla po kliknieciu
        # pozostala w zakladce Tablicy Ogloszen zamiast przelaczac ekran.
        super().__init__(text, "location_board", rect)
        self.callback = callback

    def clicked(self, pos):
        if not super().clicked(pos):
            return False
        self.callback()
        return True


def _location_key(location) -> str:
    return "|".join(
        (
            str(location.get("kind", "")),
            str(location.get("name", "")),
            str(location.get("number", "")),
        )
    )


def _board_art_file() -> Path | None:
    for path in BOARD_ART_CANDIDATES:
        if path.exists():
            return path
    return None


def _open_quest(location, index: int) -> None:
    global _OPEN_QUEST_LOCATION_KEY, _OPEN_QUEST_INDEX
    _OPEN_QUEST_LOCATION_KEY = _location_key(location)
    _OPEN_QUEST_INDEX = int(index)


def _close_quest() -> None:
    global _OPEN_QUEST_LOCATION_KEY, _OPEN_QUEST_INDEX
    _OPEN_QUEST_LOCATION_KEY = None
    _OPEN_QUEST_INDEX = None


def _modal_is_open_for(location) -> bool:
    return (
        _OPEN_QUEST_INDEX is not None
        and _OPEN_QUEST_LOCATION_KEY == _location_key(location)
    )


def _current_modal_offer(location):
    if not _modal_is_open_for(location):
        return None
    offers = location.get("quest_offers", []) or []
    index = int(_OPEN_QUEST_INDEX)
    if index < 0 or index >= len(offers):
        _close_quest()
        return None
    return offers[index]


def _right_content_rects(right_rect):
    """Dopasowuje zawartosc do gotowych ramek zapisanych w prawy_ui.png."""
    # Proporcje sa liczone wzgledem przeskalowanego panelu. Odpowiadaja kolejno:
    # kolku w naglowku, duzemu kwadratowi i trzem dolnym wierszom.
    circle_size = max(
        1,
        min(
            int(round(right_rect.width * 0.38)),
            int(round(right_rect.height * 0.16)),
        ),
    )
    portrait = pygame.Rect(
        right_rect.x + int(round(right_rect.width * 0.055)),
        right_rect.y + int(round(right_rect.height * 0.030)),
        circle_size,
        circle_size,
    )

    description = pygame.Rect(
        right_rect.x + int(round(right_rect.width * 0.055)),
        right_rect.y + int(round(right_rect.height * 0.195)),
        int(round(right_rect.width * 0.89)),
        int(round(right_rect.height * 0.335)),
    )

    slot_x = right_rect.x + int(round(right_rect.width * 0.055))
    slot_w = int(round(right_rect.width * 0.89))
    slot_h = int(round(right_rect.height * 0.120))
    slot_gap = int(round(right_rect.height * 0.012))
    first_y = right_rect.y + int(round(right_rect.height * 0.550))
    slots = [
        pygame.Rect(slot_x, first_y + index * (slot_h + slot_gap), slot_w, slot_h)
        for index in range(3)
    ]
    return {
        "portrait": portrait,
        "description": description,
        "slots": slots,
    }


def _draw_cover(screen, path: Path | None, rect: pygame.Rect) -> bool:
    source = city_hub._load_asset(path) if path is not None else None
    if source is None or rect.width <= 0 or rect.height <= 0:
        return False
    iw, ih = source.get_size()
    if iw <= 0 or ih <= 0:
        return False
    scale = max(rect.width / iw, rect.height / ih)
    size = (
        max(1, int(round(iw * scale))),
        max(1, int(round(ih * scale))),
    )
    image = (
        source
        if source.get_size() == size
        else pygame.transform.smoothscale(source, size)
    )
    source_rect = pygame.Rect(
        max(0, (image.get_width() - rect.width) // 2),
        max(0, (image.get_height() - rect.height) // 2),
        rect.width,
        rect.height,
    )
    old_clip = screen.get_clip()
    screen.set_clip(rect)
    screen.blit(image, rect.topleft, source_rect)
    screen.set_clip(old_clip)
    return True


def _fit_line(font, text, max_width):
    text = str(text or "")
    if font.size(text)[0] <= max_width:
        return text
    suffix = "..."
    while text and font.size(text + suffix)[0] > max_width:
        text = text[:-1]
    return text.rstrip() + suffix


def _quest_title(offer) -> str:
    number = int(offer.get("quest_number", 0) or 0)
    prefix = f"Q{number:02d} — " if number > 0 else ""
    return f"{prefix}{offer.get('name', 'Quest')}"


def _draw_board_header_icon(screen, rect):
    inner = rect.inflate(-max(8, rect.width // 5), -max(8, rect.height // 5))
    if not city_hub._draw_asset_contained(screen, QUEST_ICON_FILE, inner):
        pygame.draw.circle(screen, _GOLD, rect.center, max(4, min(rect.width, rect.height) // 4), 2)


def _draw_board_art(screen, rect):
    inner = rect.inflate(-10, -10)
    pygame.draw.rect(screen, _DARK, inner)
    if not _draw_cover(screen, _board_art_file(), inner):
        city_hub._draw_asset_contained(screen, QUEST_ICON_FILE, inner.inflate(-30, -30))
    veil = pygame.Surface(inner.size, pygame.SRCALPHA)
    veil.fill((0, 0, 0, 20))
    screen.blit(veil, inner.topleft)


def _draw_offer_slot(screen, small_font, mouse_pos, slot, offer, index):
    inner = slot.inflate(-7, -7)
    hovered = slot.collidepoint(mouse_pos)

    if hovered:
        hover = pygame.Surface(inner.size, pygame.SRCALPHA)
        hover.fill((218, 157, 53, 26))
        screen.blit(hover, inner.topleft)
        pygame.draw.rect(screen, _GOLD_HOVER, inner, 2, border_radius=5)

    if offer is None:
        empty = small_font.render("Brak nowego zlecenia", True, _MUTED)
        screen.blit(empty, empty.get_rect(center=inner.center))
        return None

    thumb_size = max(24, min(inner.height - 8, int(inner.width * 0.22)))
    thumb = pygame.Rect(inner.x + 5, inner.centery - thumb_size // 2, thumb_size, thumb_size)
    pygame.draw.rect(screen, (18, 16, 13), thumb, border_radius=5)
    city_hub._draw_asset_contained(screen, QUEST_ICON_FILE, thumb.inflate(-8, -8))
    pygame.draw.line(
        screen,
        (103, 71, 34),
        (thumb.right + 7, inner.y + 5),
        (thumb.right + 7, inner.bottom - 5),
        1,
    )

    text_x = thumb.right + 15
    text_w = max(20, inner.right - text_x - 7)
    title_font = pygame.font.SysFont("arial", max(11, int(inner.height * 0.18)), bold=True)
    body_font = pygame.font.SysFont("arial", max(10, int(inner.height * 0.145)))
    title = _fit_line(title_font, _quest_title(offer), text_w)
    screen.blit(title_font.render(title, True, _TEXT), (text_x, inner.y + 7))

    story = str(offer.get("description") or offer.get("objective") or "")
    lines = city.wrap(body_font, story, text_w)[:2]
    y = inner.y + 29
    for line in lines:
        screen.blit(body_font.render(line, True, _MUTED), (text_x, y))
        y += body_font.get_height() + 1

    return _HitboxButton(
        "location_board",
        slot,
        callback=lambda selected=index: _open_quest(offer.get("_location_ref", {}), selected),
    )


def _draw_board_right_content(
    screen,
    font,
    small_font,
    mouse_pos,
    location,
    player,
    selected_place,
    rect,
):
    _ = (font, player)
    if selected_place != "location_board":
        _close_quest()
        return []

    city.initialize_location(location)
    geometry = _right_content_rects(rect)
    _draw_board_header_icon(screen, geometry["portrait"])
    _draw_board_art(screen, geometry["description"])

    offers = list(location.get("quest_offers", []) or [])
    buttons = []
    for index, slot in enumerate(geometry["slots"]):
        offer = offers[index] if index < len(offers) else None
        if offer is None:
            _draw_offer_slot(screen, small_font, mouse_pos, slot, None, index)
            continue

        # Nie dopisujemy danych runtime do samej karty Questa. Hitbox dostaje
        # zamkniecie z referencja do lokacji, aby po kliknieciu otworzyc modal.
        inner = slot.inflate(-7, -7)
        hovered = slot.collidepoint(mouse_pos)
        if hovered:
            hover = pygame.Surface(inner.size, pygame.SRCALPHA)
            hover.fill((218, 157, 53, 26))
            screen.blit(hover, inner.topleft)
            pygame.draw.rect(screen, _GOLD_HOVER, inner, 2, border_radius=5)

        thumb_size = max(24, min(inner.height - 8, int(inner.width * 0.22)))
        thumb = pygame.Rect(inner.x + 5, inner.centery - thumb_size // 2, thumb_size, thumb_size)
        pygame.draw.rect(screen, (18, 16, 13), thumb, border_radius=5)
        city_hub._draw_asset_contained(screen, QUEST_ICON_FILE, thumb.inflate(-8, -8))
        pygame.draw.line(
            screen,
            (103, 71, 34),
            (thumb.right + 7, inner.y + 5),
            (thumb.right + 7, inner.bottom - 5),
            1,
        )

        text_x = thumb.right + 15
        text_w = max(20, inner.right - text_x - 7)
        title_font = pygame.font.SysFont("arial", max(11, int(inner.height * 0.18)), bold=True)
        body_font = pygame.font.SysFont("arial", max(10, int(inner.height * 0.145)))
        title = _fit_line(title_font, _quest_title(offer), text_w)
        screen.blit(title_font.render(title, True, _TEXT), (text_x, inner.y + 7))
        story = str(offer.get("description") or offer.get("objective") or "")
        lines = city.wrap(body_font, story, text_w)[:2]
        y = inner.y + 29
        for line in lines:
            screen.blit(body_font.render(line, True, _MUTED), (text_x, y))
            y += body_font.get_height() + 1

        buttons.append(
            _HitboxButton(
                "location_board",
                slot,
                callback=lambda selected=index, current=location: _open_quest(current, selected),
            )
        )
    return buttons


def _draw_quest_card_modal(screen, title_font, font, small_font, location, player, offer, index):
    sw, sh = screen.get_size()
    shade = pygame.Surface((sw, sh), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 195))
    screen.blit(shade, (0, 0))

    card_w = min(1120, max(760, int(round(sw * 0.70))))
    card_h = min(530, max(420, int(round(sh * 0.60))))
    card = pygame.Rect((sw - card_w) // 2, (sh - card_h) // 2, card_w, card_h)

    pygame.draw.rect(screen, _DARK, card, border_radius=14)
    pygame.draw.rect(screen, (58, 42, 24), card.inflate(-8, -8), border_radius=12)
    pygame.draw.rect(screen, _GOLD, card, 3, border_radius=14)
    pygame.draw.rect(screen, (105, 72, 34), card.inflate(-12, -12), 1, border_radius=10)

    number = int(offer.get("quest_number", 0) or 0)
    meta = f"QUEST {number:02d}" if number > 0 else "QUEST"
    screen.blit(small_font.render(meta, True, _GOLD), (card.x + 30, card.y + 22))

    title = str(offer.get("name") or "Quest")
    title_surface = title_font.render(title, True, _TEXT)
    max_title_w = card.width - 60
    if title_surface.get_width() > max_title_w:
        fitted = _fit_line(font, title, max_title_w)
        title_surface = font.render(fitted, True, _TEXT)
    screen.blit(title_surface, (card.x + 30, card.y + 50))

    divider_y = card.y + 105
    pygame.draw.line(screen, (118, 80, 36), (card.x + 28, divider_y), (card.right - 28, divider_y), 2)

    body_top = divider_y + 18
    button_h = 46
    footer_y = card.bottom - 28 - button_h
    image_w = int(round(card.width * 0.36))
    image_rect = pygame.Rect(card.x + 30, body_top, image_w, footer_y - body_top - 18)
    pygame.draw.rect(screen, _DARK_SOFT, image_rect, border_radius=8)
    pygame.draw.rect(screen, (111, 76, 35), image_rect, 2, border_radius=8)
    art_inner = image_rect.inflate(-10, -10)
    if not _draw_cover(screen, _board_art_file(), art_inner):
        city_hub._draw_asset_contained(screen, QUEST_ICON_FILE, art_inner.inflate(-50, -50))

    text_x = image_rect.right + 26
    text_w = card.right - 30 - text_x
    y = body_top + 2

    issuer = str(offer.get("issuer") or "Nieznany wystawca")
    screen.blit(font.render(f"Wystawca: {issuer}", True, _GOLD), (text_x, y))
    y += font.get_height() + 12

    length = str(offer.get("length") or "-")
    world_level = int(offer.get("world_level", offer.get("world_level_min", 1)) or 1)
    level_names = {1: "I", 2: "II", 3: "III", 4: "IV"}
    info = f"Poziom świata: {level_names.get(world_level, world_level)}   |   Długość: {length}"
    screen.blit(small_font.render(info, True, _MUTED), (text_x, y))
    y += small_font.get_height() + 18

    screen.blit(font.render("Treść ogłoszenia", True, _TEXT), (text_x, y))
    y += font.get_height() + 8

    # Uzywamy description z oferty, czyli board_text. Nie wyswietlamy
    # wewnetrznego description definicji Questa, bo moze zdradzac prawde/final.
    story = str(offer.get("description") or offer.get("objective") or "Brak opisu.")
    story_lines = city.wrap(small_font, story, text_w)
    max_story_bottom = footer_y - 68
    for line in story_lines:
        if y + small_font.get_height() > max_story_bottom:
            break
        screen.blit(small_font.render(line, True, _TEXT), (text_x, y))
        y += small_font.get_height() + 4

    hint = str(offer.get("reward_hint") or "Nagroda zależy od zakończenia Questa.")
    hint_label = _fit_line(small_font, f"Możliwa nagroda: {hint}", text_w)
    screen.blit(small_font.render(hint_label, True, _GOLD), (text_x, footer_y - 48))

    button_gap = 14
    close_w = 150
    accept_w = 210
    close_rect = pygame.Rect(card.right - 30 - close_w, footer_y, close_w, button_h)
    accept_rect = pygame.Rect(close_rect.x - button_gap - accept_w, footer_y, accept_w, button_h)

    message_rect = pygame.Rect(card.x + 30, footer_y, max(100, accept_rect.x - card.x - 48), button_h)
    location_message = str(player.get("_location_message") or "")
    if location_message:
        compact = _fit_line(small_font, location_message, message_rect.width)
        screen.blit(small_font.render(compact, True, _MUTED), (message_rect.x, message_rect.centery - small_font.get_height() // 2))

    def accept_selected():
        success, message = take_quest(location, player, index)
        player["_location_message"] = message
        if success:
            _close_quest()

    accept_button = _QuestModalButton("POBIERZ QUEST", accept_rect, accept_selected)
    close_button = _QuestModalButton("ZAMKNIJ", close_rect, _close_quest)
    accept_button.draw(screen, font, pygame.mouse.get_pos())
    close_button.draw(screen, font, pygame.mouse.get_pos())

    # Bloker przechwytuje klik poza karta. Jest ostatni na liscie, wiec guziki
    # modala maja pierwszenstwo w glownej petli aplikacji.
    blocker = _HitboxButton("location_board", screen.get_rect())
    return [accept_button, close_button, blocker]


def install_location_quest_board() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    original_right_content = city_hub._draw_right_content
    original_draw_screen = city_hub.draw_location_hub_screen

    def draw_right_content(
        screen,
        font,
        small_font,
        mouse_pos,
        location,
        player,
        selected_place,
        rect,
    ):
        if selected_place == "location_board":
            return _draw_board_right_content(
                screen,
                font,
                small_font,
                mouse_pos,
                location,
                player,
                selected_place,
                rect,
            )
        _close_quest()
        return original_right_content(
            screen,
            font,
            small_font,
            mouse_pos,
            location,
            player,
            selected_place,
            rect,
        )

    def draw_screen(
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
        buttons = original_draw_screen(
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
        if buttons is None:
            return None
        if selected_place != "location_board":
            _close_quest()
            return buttons

        offer = _current_modal_offer(location)
        if offer is None:
            return buttons

        return _draw_quest_card_modal(
            screen,
            title_font,
            font,
            small_font,
            location,
            player,
            offer,
            int(_OPEN_QUEST_INDEX),
        )

    city_hub._draw_right_content = draw_right_content
    city_hub.draw_location_hub_screen = draw_screen
    city_hub._rise_glory_location_quest_board_installed = True
    _INSTALLED = True
