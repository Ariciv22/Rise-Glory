from pathlib import Path

import pygame

from rg_data import GOLD, MUTED, PANEL_DARK, SCREEN_WIDTH, TEXT
from rg_location_data import initialize_location
from rg_ui import Button, draw_lines, draw_panel, wrap

ROOT_DIR = Path(__file__).resolve().parent
CITY_GRAPHICS_DIRS = [ROOT_DIR / "Grafiki" / "grafiki_miast", ROOT_DIR / "grafiki_miast"]

LOCATION_PLACES = [
    ("Sklep", "location_shop"),
    ("Karczma", "location_tavern"),
    ("Tablica ogloszen", "location_board"),
    ("Trening", "location_training"),
    ("Leczenie", "location_healing"),
]


def find_city_background(location):
    background = location.get("background") or ""
    names = [background] if background else []
    if location.get("name") == "Lirion":
        names.append("lirion_miasto")
    for directory in CITY_GRAPHICS_DIRS:
        for name in names:
            for ext in ["", ".png", ".jpg", ".jpeg", ".webp"]:
                path = directory / f"{name}{ext}"
                if path.exists():
                    return path
    return None


def load_city_background(location, size):
    path = find_city_background(location)
    if not path:
        return None
    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None
    iw, ih = image.get_size()
    sw, sh = size
    scale = max(sw / iw, sh / ih)
    scaled = pygame.transform.smoothscale(image, (int(iw * scale), int(ih * scale)))
    result = pygame.Surface(size, pygame.SRCALPHA)
    result.blit(scaled, ((sw - scaled.get_width()) // 2, (sh - scaled.get_height()) // 2))
    return result


def draw_fallback_background(screen):
    screen.fill((19, 15, 12))
    sw, sh = screen.get_size()
    for i in range(18):
        shade = 22 + i * 4
        rect = pygame.Rect(i * 35, i * 24, sw - i * 70, sh - i * 48)
        if rect.width > 0 and rect.height > 0:
            pygame.draw.rect(screen, (shade, 25, 16), rect, 1)


def _draw_offer_cards(screen, font, small_font, mouse_pos, cards, prefix, x, y, width, button_text):
    buttons = []
    card_h = 104
    for index, card in enumerate(cards):
        rect = pygame.Rect(x, y + index * (card_h + 10), width, card_h)
        pygame.draw.rect(screen, PANEL_DARK, rect, border_radius=10)
        pygame.draw.rect(screen, GOLD, rect, 1, border_radius=10)
        screen.blit(font.render(card["name"], True, TEXT), (rect.x + 14, rect.y + 10))
        price = card.get("price")
        meta = f"{price} monet" if price is not None else f"Talia: {card.get('deck', '-')}"
        screen.blit(small_font.render(meta, True, MUTED), (rect.x + 14, rect.y + 38))
        lines = wrap(small_font, card.get("description", ""), width - 170)[:2]
        draw_lines(screen, small_font, lines, rect.x + 14, rect.y + 62, MUTED, line_h=18, max_width=width - 170)
        button = Button(button_text, f"{prefix}:{index}", (rect.right - 140, rect.y + 29, 122, 44))
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)
    return buttons


def draw_city_screen(screen, title_font, font, small_font, mouse_pos, location, player, selected_place=None, message=""):
    initialize_location(location)
    bg = load_city_background(location, screen.get_size())
    if bg:
        screen.blit(bg, (0, 0))
    else:
        draw_fallback_background(screen)

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 110))
    screen.blit(overlay, (0, 0))

    sw, sh = screen.get_size()
    header = pygame.Rect(40, 28, sw - 80, 112)
    draw_panel(screen, header, GOLD)
    title = f"{location.get('type_name', 'Lokacja')}: {location.get('name', 'Lokacja')}"
    screen.blit(title_font.render(title, True, TEXT), (header.x + 28, header.y + 18))
    status = f"{player['name']} | Zloto: {player.get('gold', 0)} | Questy: {len(player.get('active_quests', []))}/3 | Pomocnicy: {len(player.get('helpers', []))}/5"
    screen.blit(small_font.render(status, True, MUTED), (header.x + 30, header.y + 78))

    left = pygame.Rect(42, 164, 300, sh - 206)
    draw_panel(screen, left, GOLD)
    screen.blit(font.render("Miejsca", True, TEXT), (left.x + 22, left.y + 20))
    buttons = []
    y = left.y + 64
    for label, action in LOCATION_PLACES:
        button = Button(label, action, (left.x + 20, y, left.width - 40, 48))
        button.draw(screen, font, mouse_pos, active=(selected_place == action))
        buttons.append(button)
        y += 60
    back = Button("Powrot na mape", "back_to_map", (left.x + 20, left.bottom - 64, left.width - 40, 46))
    back.draw(screen, font, mouse_pos)
    buttons.append(back)

    content = pygame.Rect(360, 164, sw - 402, sh - 206)
    draw_panel(screen, content, GOLD)
    if message:
        message_box = pygame.Rect(content.x + 18, content.y + 14, content.width - 36, 42)
        pygame.draw.rect(screen, (45, 55, 48), message_box, border_radius=8)
        screen.blit(small_font.render(message, True, TEXT), (message_box.x + 12, message_box.y + 11))

    start_y = content.y + 70
    if selected_place == "location_shop":
        screen.blit(font.render("Sklep - 5 dostepnych kart", True, TEXT), (content.x + 22, start_y))
        buttons += _draw_offer_cards(screen, font, small_font, mouse_pos, location["shop_offers"], "buy", content.x + 22, start_y + 42, content.width - 44, "Kup")
    elif selected_place == "location_tavern":
        screen.blit(font.render("Karczma - 3 pomocnikow", True, TEXT), (content.x + 22, start_y))
        buttons += _draw_offer_cards(screen, font, small_font, mouse_pos, location["helper_offers"], "hire", content.x + 22, start_y + 42, content.width - 44, "Zatrudnij")
    elif selected_place == "location_board":
        screen.blit(font.render("Tablica ogloszen - 3 questy", True, TEXT), (content.x + 22, start_y))
        buttons += _draw_offer_cards(screen, font, small_font, mouse_pos, location["quest_offers"], "quest", content.x + 22, start_y + 42, content.width - 44, "Pobierz")
    elif selected_place == "location_training":
        screen.blit(font.render("Trening", True, TEXT), (content.x + 22, start_y))
        draw_lines(screen, font, ["Pelny system treningu zostanie podpiety w kolejnym etapie."], content.x + 22, start_y + 50, MUTED)
    elif selected_place == "location_healing":
        screen.blit(font.render("Leczenie", True, TEXT), (content.x + 22, start_y))
        draw_lines(screen, font, ["Leczenie kosztuje 2 monety za Rane i 1 akcje.", "Interakcja zostanie podpieta razem z pelnym systemem Ran."], content.x + 22, start_y + 50, MUTED, line_h=34)
    else:
        screen.blit(font.render("Wybierz miejsce w lokacji", True, TEXT), (content.x + 22, start_y))
        draw_lines(screen, font, ["Sklep, karczma i tablica posiadaja osobne, trwale oferty.", "Kupiona lub pobrana karta jest natychmiast zastepowana nowa."], content.x + 22, start_y + 50, MUTED, line_h=32)
    return buttons
