from pathlib import Path

import pygame

from rg_data import GOLD, MUTED, PANEL_DARK, SCREEN_WIDTH, STAT_NAMES, TEXT
from rg_gameplay import quest_test_preview
from rg_location_data import helper_effect_text, initialize_location
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
        description = helper_effect_text(card) if prefix == "hire" else card.get("description", "")
        lines = wrap(small_font, description, width - 170)[:2]
        draw_lines(screen, small_font, lines, rect.x + 14, rect.y + 62, MUTED, line_h=18, max_width=width - 170)
        button = Button(button_text, f"{prefix}:{index}", (rect.right - 140, rect.y + 29, 122, 44))
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)
    return buttons


def _draw_owned_helpers(screen, font, small_font, player, x, y, width):
    helpers = player.get("helpers", [])
    screen.blit(font.render(f"Twoi pomocnicy: {len(helpers)}/5", True, TEXT), (x, y))
    y += 38
    if not helpers:
        draw_lines(screen, small_font, ["Nie zatrudniono jeszcze zadnego pomocnika."], x, y, MUTED, max_width=width)
        return

    for helper in helpers:
        line = f"{helper['name']} - {helper_effect_text(helper)}"
        for wrapped in wrap(small_font, line, width)[:2]:
            screen.blit(small_font.render(wrapped, True, MUTED), (x, y))
            y += 20
        y += 6


def _draw_active_quests(screen, font, small_font, mouse_pos, player, x, y, width):
    buttons = []
    quests = player.get("active_quests", [])
    screen.blit(font.render(f"Aktywne questy: {len(quests)}/3", True, TEXT), (x, y))
    y += 38
    if not quests:
        draw_lines(screen, small_font, ["Pobierz quest z ofert po lewej stronie."], x, y, MUTED, max_width=width)
        return buttons

    for index, quest in enumerate(quests):
        rect = pygame.Rect(x, y, width, 92)
        pygame.draw.rect(screen, PANEL_DARK, rect, border_radius=10)
        pygame.draw.rect(screen, GOLD, rect, 1, border_radius=10)
        stat, base, bonus, difficulty = quest_test_preview(player, quest)
        screen.blit(small_font.render(quest["name"], True, TEXT), (rect.x + 12, rect.y + 10))
        test_text = f"Test: k6 + {stat} ({base}) + pomocnicy ({bonus}) vs {difficulty}"
        screen.blit(small_font.render(test_text, True, MUTED), (rect.x + 12, rect.y + 36))
        button = Button("Rozwiaz", f"resolve_quest:{index}", (rect.right - 116, rect.y + 23, 100, 44))
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)
        y += 102
    return buttons


def _draw_training(screen, font, small_font, mouse_pos, player, x, y, width):
    buttons = []
    screen.blit(font.render("Trening statystyk", True, TEXT), (x, y))
    draw_lines(screen, small_font, ["Kazdy trening kosztuje 4 zlota. Maksymalna wartosc statystyki: 6."], x, y + 38, MUTED, max_width=width)
    y += 82
    columns = 2
    gap = 14
    button_w = (width - gap) // columns
    for index, stat in enumerate(STAT_NAMES):
        row = index // columns
        col = index % columns
        bx = x + col * (button_w + gap)
        by = y + row * 62
        value = player.get("stats", {}).get(stat, 0)
        button = Button(f"{stat}: {value}  (+1)", f"train:{stat}", (bx, by, button_w, 48))
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
    status = (
        f"{player['name']} | Zloto: {player.get('gold', 0)} | Legenda: {player.get('legend', 0)} "
        f"| Rany: {player.get('wounds', 0)} | Questy: {len(player.get('active_quests', []))}/3 "
        f"| Pomocnicy: {len(player.get('helpers', []))}/5"
    )
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
        message_box = pygame.Rect(content.x + 18, content.y + 14, content.width - 36, 56)
        pygame.draw.rect(screen, (45, 55, 48), message_box, border_radius=8)
        draw_lines(screen, small_font, wrap(small_font, message, message_box.width - 24)[:2], message_box.x + 12, message_box.y + 9, TEXT, line_h=19)

    start_y = content.y + 84
    if selected_place == "location_shop":
        screen.blit(font.render("Sklep - 5 dostepnych kart", True, TEXT), (content.x + 22, start_y))
        buttons += _draw_offer_cards(screen, font, small_font, mouse_pos, location["shop_offers"], "buy", content.x + 22, start_y + 42, content.width - 44, "Kup")
    elif selected_place == "location_tavern":
        screen.blit(font.render("Karczma - 3 pomocnikow", True, TEXT), (content.x + 22, start_y))
        offer_width = int((content.width - 66) * 0.62)
        buttons += _draw_offer_cards(screen, font, small_font, mouse_pos, location["helper_offers"], "hire", content.x + 22, start_y + 42, offer_width, "Zatrudnij")
        owned_x = content.x + 44 + offer_width
        _draw_owned_helpers(screen, font, small_font, player, owned_x, start_y + 42, content.right - owned_x - 22)
    elif selected_place == "location_board":
        split = int((content.width - 66) * 0.56)
        screen.blit(font.render("Tablica ogloszen", True, TEXT), (content.x + 22, start_y))
        buttons += _draw_offer_cards(screen, font, small_font, mouse_pos, location["quest_offers"], "quest", content.x + 22, start_y + 42, split, "Pobierz")
        active_x = content.x + 44 + split
        buttons += _draw_active_quests(screen, font, small_font, mouse_pos, player, active_x, start_y + 42, content.right - active_x - 22)
    elif selected_place == "location_training":
        buttons += _draw_training(screen, font, small_font, mouse_pos, player, content.x + 22, start_y, content.width - 44)
    elif selected_place == "location_healing":
        screen.blit(font.render("Leczenie", True, TEXT), (content.x + 22, start_y))
        cost = 1 if any(helper.get("name") == "Medyk polowy" for helper in player.get("helpers", [])) else 2
        draw_lines(
            screen,
            font,
            [f"Aktualne Rany: {player.get('wounds', 0)}", f"Wyleczenie jednej Rany kosztuje {cost} zlota."],
            content.x + 22,
            start_y + 52,
            MUTED,
            line_h=34,
        )
        heal = Button("Wylecz 1 Rane", "heal_one", (content.x + 22, start_y + 136, 220, 50))
        heal.draw(screen, font, mouse_pos)
        buttons.append(heal)
    else:
        screen.blit(font.render("Wybierz miejsce w lokacji", True, TEXT), (content.x + 22, start_y))
        draw_lines(
            screen,
            font,
            [
                "Pobieraj i rozwiazuj questy, aby zdobywac zloto i Legende.",
                "Pierwszy bohater, ktory zdobedzie 5 punktow Legendy, wygrywa gre.",
            ],
            content.x + 22,
            start_y + 50,
            MUTED,
            line_h=32,
        )
    return buttons
