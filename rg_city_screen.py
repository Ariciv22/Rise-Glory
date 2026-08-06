from pathlib import Path

import pygame

from rg_combat import draw_combat_screen, is_combat_active
from rg_data import GOLD, MUTED, PANEL_DARK, TEXT
from rg_engine.heroes import training_cost
from rg_engine.items import EQUIPMENT_SLOTS, ensure_equipment_state, item_display_name
from rg_engine.locations import training_stats_for
from rg_location_data import helper_effect_text, initialize_location
from rg_quest_ui import draw_quest_panel, location_quest_tabs, parse_quest_action, quest_action
from rg_ui import Button, draw_lines, draw_panel, wrap

ROOT_DIR = Path(__file__).resolve().parent
CITY_GRAPHICS_DIRS = [ROOT_DIR / "Grafiki" / "grafiki_miast", ROOT_DIR / "grafiki_miast"]

LOCATION_PLACES = [
    ("Sklep", "location_shop"),
    ("Karczma", "location_tavern"),
    ("Tablica ogloszen", "location_board"),
    ("Trening", "location_training"),
    ("Leczenie", "location_healing"),
    ("Ekwipunek", "location_equipment"),
]

SLOT_LABELS = {
    "weapon": "Bron",
    "armor": "Zbroja",
    "helmet": "Helm",
    "boots": "Buty",
    "gloves": "Rekawice",
    "amulet": "Amulet",
    "ring_1": "Pierscien 1",
    "ring_2": "Pierscien 2",
}


def _location_places(location, player):
    places = list(LOCATION_PLACES)
    for quest in location_quest_tabs(player, location.get("name", "")):
        places.append((f"Quest: {quest.get('name', 'Quest')}", quest_action(quest.get("id"))))
    return places


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


def _draw_training(screen, font, small_font, mouse_pos, content, location, player, start_y):
    buttons = []
    stats = training_stats_for(location.get("kind", ""))
    screen.blit(font.render("Trening statystyk", True, TEXT), (content.x + 22, start_y))
    draw_lines(screen, small_font, ["Kazdy trening kosztuje 1 akcje oraz liczbe monet wynikajaca z obecnej wartosci statystyki."], content.x + 22, start_y + 38, MUTED, max_width=content.width - 44)
    y = start_y + 92
    for stat in stats:
        current = int(player.get("stats", {}).get(stat, 0) or 0)
        cost = training_cost(current)
        rect = pygame.Rect(content.x + 22, y, content.width - 44, 64)
        pygame.draw.rect(screen, PANEL_DARK, rect, border_radius=10)
        pygame.draw.rect(screen, GOLD, rect, 1, border_radius=10)
        screen.blit(font.render(f"{stat}: {current}/6", True, TEXT), (rect.x + 16, rect.y + 9))
        cost_text = "maksimum" if cost is None else f"koszt {cost} monet + 1 akcja"
        screen.blit(small_font.render(cost_text, True, MUTED), (rect.x + 16, rect.y + 37))
        button = Button("Trenuj", f"train:{stat}", (rect.right - 138, rect.y + 10, 120, 44))
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)
        y += 76
    return buttons


def _draw_healing(screen, font, small_font, mouse_pos, content, player, start_y):
    wounds = int(player.get("wounds", 0) or 0)
    screen.blit(font.render("Leczenie Ran", True, TEXT), (content.x + 22, start_y))
    lines = [
        f"Aktualne Rany: {wounds}/4",
        "Leczenie wszystkich mozliwych Ran kosztuje 1 akcje i 2 monety za kazda Rane.",
        "Medyk polowy zmniejsza koszt kazdej leczonej Rany o 1 monete.",
    ]
    draw_lines(screen, small_font, lines, content.x + 22, start_y + 48, MUTED, line_h=30, max_width=content.width - 44)
    button = Button("Wylecz Rany", "heal:all", (content.x + 22, start_y + 168, 260, 52))
    button.draw(screen, font, mouse_pos)
    return [button]


def _draw_equipment(screen, font, small_font, mouse_pos, content, player, start_y):
    ensure_equipment_state(player)
    buttons = []
    left_width = int((content.width - 66) * 0.44)
    left_x = content.x + 22
    right_x = left_x + left_width + 22
    right_width = content.right - right_x - 22

    screen.blit(font.render("Zalozony ekwipunek", True, TEXT), (left_x, start_y))
    y = start_y + 42
    for slot in EQUIPMENT_SLOTS:
        item = player["equipment"].get(slot)
        rect = pygame.Rect(left_x, y, left_width, 48)
        pygame.draw.rect(screen, PANEL_DARK, rect, border_radius=8)
        pygame.draw.rect(screen, GOLD, rect, 1, border_radius=8)
        label = f"{SLOT_LABELS.get(slot, slot)}: {item_display_name(item) if item else '-'}"
        screen.blit(small_font.render(label, True, TEXT if item else MUTED), (rect.x + 10, rect.y + 14))
        if item:
            button = Button("Zdejmij", f"unequip:{slot}", (rect.right - 102, rect.y + 6, 90, 36))
            button.draw(screen, small_font, mouse_pos)
            buttons.append(button)
        y += 56

    inventory = list(player.get("inventory", []))
    screen.blit(font.render(f"Plecak: {len(inventory)}/{player.get('backpack_limit', 10)}", True, TEXT), (right_x, start_y))
    y = start_y + 42
    if not inventory:
        screen.blit(small_font.render("Plecak jest pusty.", True, MUTED), (right_x, y))
    for index, item in enumerate(inventory[:8]):
        rect = pygame.Rect(right_x, y, right_width, 58)
        pygame.draw.rect(screen, PANEL_DARK, rect, border_radius=8)
        pygame.draw.rect(screen, GOLD, rect, 1, border_radius=8)
        screen.blit(small_font.render(item_display_name(item), True, TEXT), (rect.x + 10, rect.y + 8))
        description = str(item.get("description", "")) if isinstance(item, dict) else ""
        screen.blit(small_font.render(description[:52], True, MUTED), (rect.x + 10, rect.y + 31))
        equip = Button("Zaloz", f"equip:{index}", (rect.right - 196, rect.y + 10, 82, 38))
        sell = Button("Sprzedaj", f"sell:{index}", (rect.right - 106, rect.y + 10, 94, 38))
        equip.draw(screen, small_font, mouse_pos)
        sell.draw(screen, small_font, mouse_pos)
        buttons.extend([equip, sell])
        y += 66
    return buttons


def draw_city_screen(screen, title_font, font, small_font, mouse_pos, location, player, selected_place=None, message=""):
    if is_combat_active():
        return draw_combat_screen(screen, title_font, font, small_font, mouse_pos)

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
    token = player.get("_token_ref")
    actions = int(getattr(token, "actions", 0) or 0) if token is not None else 0
    status = (
        f"{player['name']} | Zloto: {player.get('gold', 0)} | Akcje: {actions} | "
        f"Questy: {len(player.get('active_quests', []))}/3 | Pomocnicy: {len(player.get('helpers', []))}/5"
    )
    screen.blit(small_font.render(status, True, MUTED), (header.x + 30, header.y + 78))

    left = pygame.Rect(42, 164, 300, sh - 206)
    draw_panel(screen, left, GOLD)
    screen.blit(font.render("Miejsca", True, TEXT), (left.x + 22, left.y + 20))
    buttons = []
    y = left.y + 64
    place_buttons = _location_places(location, player)
    max_button_y = left.bottom - 126
    for label, action in place_buttons:
        if y > max_button_y:
            break
        button = Button(label, action, (left.x + 20, y, left.width - 40, 48))
        button.draw(screen, font, mouse_pos, active=(selected_place == action))
        buttons.append(button)
        y += 58
    back = Button("Powrot na mape", "back_to_map", (left.x + 20, left.bottom - 64, left.width - 40, 46))
    back.draw(screen, font, mouse_pos)
    buttons.append(back)

    content = pygame.Rect(360, 164, sw - 402, sh - 206)
    draw_panel(screen, content, GOLD)
    if message:
        message_box = pygame.Rect(content.x + 18, content.y + 14, content.width - 36, 42)
        pygame.draw.rect(screen, (45, 55, 48), message_box, border_radius=8)
        screen.blit(small_font.render(message[:120], True, TEXT), (message_box.x + 12, message_box.y + 11))

    start_y = content.y + 70
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
        screen.blit(font.render("Tablica ogloszen - 3 questy", True, TEXT), (content.x + 22, start_y))
        buttons += _draw_offer_cards(screen, font, small_font, mouse_pos, location["quest_offers"], "quest", content.x + 22, start_y + 42, content.width - 44, "Pobierz")
    elif parse_quest_action(selected_place):
        buttons += draw_quest_panel(screen, font, small_font, mouse_pos, content, player, parse_quest_action(selected_place))
    elif selected_place == "location_training":
        buttons += _draw_training(screen, font, small_font, mouse_pos, content, location, player, start_y)
    elif selected_place == "location_healing":
        buttons += _draw_healing(screen, font, small_font, mouse_pos, content, player, start_y)
    elif selected_place == "location_equipment":
        buttons += _draw_equipment(screen, font, small_font, mouse_pos, content, player, start_y)
    else:
        screen.blit(font.render("Wybierz miejsce w lokacji", True, TEXT), (content.x + 22, start_y))
        draw_lines(screen, font, ["Sklep, karczma i tablica posiadaja osobne, trwale oferty.", "Questy wymagajace tej lokacji pojawiaja sie jako dodatkowe zakladki."], content.x + 22, start_y + 50, MUTED, line_h=32)
    return buttons
