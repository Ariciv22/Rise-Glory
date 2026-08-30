from __future__ import annotations

from pathlib import Path

import pygame

from rg_ui import city_hub


_INSTALLED = False

BUTTON_UI_DIR = city_hub.city.ROOT_DIR / "Grafiki" / "buttony_panele_lokacji"

# Jedno zrodlo prawdy dla naglowka prawego UI. Akcja pozostaje techniczna,
# natomiast nazwa, ikona i duza grafika sa w pelni prezentacyjne.
PLACE_PRESENTATION = {
    "location_shop": {
        "name": "Sklep",
        "icon": BUTTON_UI_DIR / "mieszek.png",
        "art": BUTTON_UI_DIR / "prawe_ui_sklep.png",
    },
    "location_tavern": {
        "name": "Karczma",
        "icon": BUTTON_UI_DIR / "kufel.png",
        "art": BUTTON_UI_DIR / "prawe_ui_karczma.png",
    },
    "location_board": {
        "name": "Tablica ogłoszeń",
        "icon": BUTTON_UI_DIR / "quest.png",
        "art": BUTTON_UI_DIR / "prawe_ui_tablica_ogloszen.png",
    },
    "location_training": {
        "name": "Trening",
        "icon": BUTTON_UI_DIR / "walka.png",
        "art": BUTTON_UI_DIR / "prawe_ui_trening.png",
    },
    "location_healing": {
        "name": "Leczenie",
        "icon": BUTTON_UI_DIR / "leczenie.png",
        "art": BUTTON_UI_DIR / "prawe_ui_leczenie.png",
    },
    "location_industry": {
        "name": "Gildia",
        "icon": BUTTON_UI_DIR / "skrzynia.png",
        "art": BUTTON_UI_DIR / "prawe_ui_gildia.png",
    },
    # Zgodnosc ze starsza nazwa techniczna. Widoczny szosty kafel jest Gildia.
    "location_equipment": {
        "name": "Gildia",
        "icon": BUTTON_UI_DIR / "skrzynia.png",
        "art": BUTTON_UI_DIR / "prawe_ui_gildia.png",
    },
}

_TITLE_FONT_CACHE = {}


def _right_panel_geometry(right_rect: pygame.Rect):
    """Trafia w gotowe ramki zapisane w prawy_ui.png.

    Proporcje sa takie same jak te uzywane przez Tablice Ogloszen: kolko u gory,
    duzy prostokat pod naglowkiem oraz dolna strefa na interaktywna zawartosc.
    """
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

    title = pygame.Rect(
        portrait.right + int(round(right_rect.width * 0.045)),
        right_rect.y + int(round(right_rect.height * 0.045)),
        max(1, right_rect.right - portrait.right - int(round(right_rect.width * 0.095))),
        max(1, int(round(right_rect.height * 0.095))),
    )

    preview = pygame.Rect(
        right_rect.x + int(round(right_rect.width * 0.055)),
        right_rect.y + int(round(right_rect.height * 0.195)),
        int(round(right_rect.width * 0.89)),
        int(round(right_rect.height * 0.335)),
    )

    # Dolna czesc pozostaje wolna dla sklepu, questow, Gildii itd. Konczymy
    # przed stopka ze strzalkami.
    body_top = right_rect.y + int(round(right_rect.height * 0.545))
    body_bottom = right_rect.bottom - int(round(right_rect.height * 0.055))
    body = pygame.Rect(
        right_rect.x + int(round(right_rect.width * 0.055)),
        body_top,
        int(round(right_rect.width * 0.89)),
        max(1, body_bottom - body_top),
    )
    return {"portrait": portrait, "title": title, "preview": preview, "body": body}


def right_panel_body_rect(right_rect: pygame.Rect) -> pygame.Rect:
    """Publiczny obszar na funkcjonalna zawartosc ponizej grafiki budynku."""
    return _right_panel_geometry(right_rect)["body"]


def _fit_title(text: str, rect: pygame.Rect):
    size = max(16, int(round(rect.height * 0.45)))
    while size >= 14:
        try:
            font = pygame.font.SysFont("georgia", size, bold=True)
        except pygame.error:
            font = pygame.font.Font(None, size)
        if font.size(text)[0] <= rect.width:
            return font
        size -= 1
    return pygame.font.Font(None, 14)


def _draw_cover(screen, path: Path, rect: pygame.Rect) -> bool:
    source = city_hub._load_asset(path)
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

    src = pygame.Rect(
        max(0, (image.get_width() - rect.width) // 2),
        max(0, (image.get_height() - rect.height) // 2),
        rect.width,
        rect.height,
    )
    old_clip = screen.get_clip()
    screen.set_clip(rect)
    screen.blit(image, rect.topleft, src)
    screen.set_clip(old_clip)
    return True


def _draw_place_presentation(screen, right_rect: pygame.Rect, selected_place):
    action = selected_place or "location_shop"
    meta = PLACE_PRESENTATION.get(action)
    if meta is None:
        return

    geometry = _right_panel_geometry(right_rect)

    # Ikona z lewego UI trafia do gotowego okraglego pola w prawym panelu.
    portrait = geometry["portrait"]
    icon_pad = max(8, int(round(min(portrait.width, portrait.height) * 0.18)))
    city_hub._draw_asset_contained(
        screen,
        meta["icon"],
        portrait.inflate(-icon_pad * 2, -icon_pad * 2),
    )

    # Nazwa budynku po prawej stronie kolka.
    title_rect = geometry["title"]
    title_font = _fit_title(meta["name"], title_rect)
    shadow = title_font.render(meta["name"], True, (43, 28, 14))
    label = title_font.render(meta["name"], True, city_hub._GOLD_TEXT)
    y = title_rect.centery - label.get_height() // 2
    screen.blit(shadow, (title_rect.x + 2, y + 2))
    screen.blit(label, (title_rect.x, y))

    # Duzy asset budynku wypelnia istniejaca ramke bez deformowania proporcji.
    preview = geometry["preview"]
    inset_x = max(5, int(round(right_rect.width * 0.018)))
    inset_y = max(5, int(round(right_rect.height * 0.010)))
    inner = preview.inflate(-inset_x * 2, -inset_y * 2)
    _draw_cover(screen, meta["art"], inner)


def install_location_right_panel_content() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    # Instalujemy ten wrapper po Gildii oraz Tablicy Ogloszen, dlatego
    # original_right_content zawiera juz ich logike i przyciski.
    original_right_content = city_hub._draw_right_content
    original_content_rect = city_hub.right_content_rect

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
        action = selected_place or "location_shop"

        # Gildia ma rozbudowana liste Zakladow i praw. Przesuwamy jej istniejacy
        # renderer do dolnej strefy, aby nie wszedl pod grafike prawe_ui_gildia.
        if action == "location_industry":
            _draw_place_presentation(screen, rect, action)

            def body_content_rect(_right_rect):
                return right_panel_body_rect(_right_rect)

            city_hub.right_content_rect = body_content_rect
            try:
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
            finally:
                city_hub.right_content_rect = original_content_rect

        # Pozostale moduly (szczegolnie Tablica Ogloszen) najpierw rysuja swoja
        # funkcjonalna zawartosc. Na koncu ujednolicamy tylko trzy stale pola:
        # ikone, nazwe i glowna grafike budynku. Dolnych slotow nie dotykamy.
        buttons = original_right_content(
            screen,
            font,
            small_font,
            mouse_pos,
            location,
            player,
            selected_place,
            rect,
        )
        _draw_place_presentation(screen, rect, action)
        return buttons

    city_hub._draw_right_content = draw_right_content
    city_hub.right_panel_body_rect = right_panel_body_rect
    city_hub._rise_glory_location_right_panel_content_installed = True
    _INSTALLED = True
