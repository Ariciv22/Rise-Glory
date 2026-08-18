from pathlib import Path

import pygame

from rg_ui import city


VILLAGE_SCENE_DIR = city.ROOT_DIR / "Grafiki" / "RISE&GLORY" / "Ekrany_miast_wsi_zamkow"
VILLAGE_SCENE_FILE = VILLAGE_SCENE_DIR / "wies3.png"

# Hotspoty sa zapisane wzgledem samej ilustracji wsi (x, y, szerokosc, wysokosc).
# Dzieki temu pozostaja we wlasciwych miejscach po zmianie rozdzielczosci okna.
VILLAGE_HOTSPOTS = [
    ("Sklep", "location_shop", (0.06, 0.24, 0.35, 0.29)),
    ("Karczma", "location_tavern", (0.46, 0.06, 0.35, 0.31)),
    ("Tablica", "location_board", (0.79, 0.20, 0.18, 0.24)),
    ("Trening", "location_training", (0.62, 0.38, 0.35, 0.30)),
    ("Leczenie", "location_healing", (0.03, 0.57, 0.39, 0.39)),
    ("Ekwipunek", "location_equipment", (0.58, 0.65, 0.39, 0.33)),
]

_SCENE_SOURCE = None
_SCENE_SCALED = {}


class VillageHotspotButton(city.Button):
    """Niewidzialna strefa klikniecia z mala etykieta i podswietleniem hover."""

    def __init__(self, text, action, rect, label_pos):
        super().__init__(text, action, rect)
        self.label_pos = label_pos

    def draw_hotspot(self, screen, font, mouse_pos, active=False):
        hovered = self.rect.collidepoint(mouse_pos)
        if hovered or active:
            glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            glow.fill((255, 190, 65, 28 if hovered else 20))
            screen.blit(glow, self.rect.topleft)
            pygame.draw.rect(screen, (226, 170, 72), self.rect, 2, border_radius=12)

        label = font.render(self.text, True, city.TEXT)
        pad_x, pad_y = 12, 7
        label_rect = pygame.Rect(
            0,
            0,
            label.get_width() + pad_x * 2,
            label.get_height() + pad_y * 2,
        )
        label_rect.center = self.label_pos
        panel = pygame.Surface(label_rect.size, pygame.SRCALPHA)
        panel.fill((18, 14, 10, 220 if hovered or active else 185))
        screen.blit(panel, label_rect.topleft)
        pygame.draw.rect(
            screen,
            (232, 177, 75) if hovered or active else (126, 91, 43),
            label_rect,
            2 if hovered or active else 1,
            border_radius=10,
        )
        screen.blit(label, label.get_rect(center=label_rect.center))


def _load_scene_source():
    global _SCENE_SOURCE
    if _SCENE_SOURCE is not None:
        return _SCENE_SOURCE
    if not VILLAGE_SCENE_FILE.exists():
        return None
    try:
        _SCENE_SOURCE = pygame.image.load(str(VILLAGE_SCENE_FILE)).convert_alpha()
    except pygame.error:
        return None
    return _SCENE_SOURCE


def _fit_scene(rect):
    source = _load_scene_source()
    if source is None:
        return None, None
    iw, ih = source.get_size()
    scale = min(rect.width / iw, rect.height / ih)
    width = max(1, int(iw * scale))
    height = max(1, int(ih * scale))
    key = (width, height)
    scaled = _SCENE_SCALED.get(key)
    if scaled is None:
        scaled = pygame.transform.smoothscale(source, key)
        _SCENE_SCALED[key] = scaled
    image_rect = scaled.get_rect(center=rect.center)
    return scaled, image_rect


def _hotspot_rect(image_rect, normalized):
    x, y, w, h = normalized
    return pygame.Rect(
        image_rect.x + int(image_rect.width * x),
        image_rect.y + int(image_rect.height * y),
        max(12, int(image_rect.width * w)),
        max(12, int(image_rect.height * h)),
    )


def _draw_header(screen, title_font, small_font, location, player, rect):
    city.draw_panel(screen, rect, city.GOLD)
    title = f"{location.get('type_name', 'Wies')}: {location.get('name', 'Wies')}"
    screen.blit(title_font.render(title, True, city.TEXT), (rect.x + 24, rect.y + 12))
    token = player.get("_token_ref")
    actions = int(getattr(token, "actions", 0) or 0) if token is not None else 0
    status = (
        f"{player['name']} | Zloto: {player.get('gold', 0)} | Akcje: {actions} | "
        f"Questy: {len(player.get('active_quests', []))}/3 | "
        f"Pomocnicy: {len(player.get('helpers', []))}/5"
    )
    screen.blit(small_font.render(status, True, city.MUTED), (rect.x + 26, rect.bottom - 30))


def _draw_left_menu(screen, font, mouse_pos, location, player, selected_place, rect):
    city.draw_panel(screen, rect, city.GOLD)
    buttons = []
    y = rect.y + 20
    for label, action in city._location_places(location, player):
        if y + 48 > rect.bottom - 76:
            break
        button = city.Button(label, action, (rect.x + 16, y, rect.width - 32, 48))
        button.draw(screen, font, mouse_pos, active=(selected_place == action))
        buttons.append(button)
        y += 56

    back = city.Button("Powrot na mape", "back_to_map", (rect.x + 16, rect.bottom - 60, rect.width - 32, 44))
    back.draw(screen, font, mouse_pos)
    buttons.append(back)
    return buttons


def _draw_compact_equipment(screen, font, small_font, mouse_pos, rect, player, start_y):
    city.ensure_equipment_state(player)
    buttons = []
    y = start_y
    screen.blit(font.render("Zalozony ekwipunek", True, city.TEXT), (rect.x + 16, y))
    y += 34

    for slot in city.EQUIPMENT_SLOTS:
        item = player["equipment"].get(slot)
        row = pygame.Rect(rect.x + 14, y, rect.width - 28, 34)
        pygame.draw.rect(screen, city.PANEL_DARK, row, border_radius=7)
        pygame.draw.rect(screen, city.GOLD, row, 1, border_radius=7)
        label = f"{city.SLOT_LABELS.get(slot, slot)}: {city.item_display_name(item) if item else '-'}"
        screen.blit(small_font.render(label[:34], True, city.TEXT if item else city.MUTED), (row.x + 8, row.y + 8))
        if item:
            button = city.LocationActionButton(
                "Zdejmij",
                "location_equipment",
                (row.right - 78, row.y + 4, 70, 26),
                city._remember_message(player, lambda selected=slot: city.unequip_equipment_slot(player, selected)),
            )
            button.draw(screen, small_font, mouse_pos)
            buttons.append(button)
        y += 39

    inventory = list(player.get("inventory", []))
    y += 8
    screen.blit(font.render(f"Plecak: {len(inventory)}/{player.get('backpack_limit', 10)}", True, city.TEXT), (rect.x + 16, y))
    y += 34
    if not inventory:
        screen.blit(small_font.render("Plecak jest pusty.", True, city.MUTED), (rect.x + 16, y))
        return buttons

    max_items = max(1, min(5, (rect.bottom - y - 8) // 54))
    for index, item in enumerate(inventory[:max_items]):
        row = pygame.Rect(rect.x + 14, y, rect.width - 28, 48)
        pygame.draw.rect(screen, city.PANEL_DARK, row, border_radius=7)
        pygame.draw.rect(screen, city.GOLD, row, 1, border_radius=7)
        screen.blit(small_font.render(city.item_display_name(item)[:24], True, city.TEXT), (row.x + 8, row.y + 6))
        equip = city.LocationActionButton(
            "Zaloz",
            "location_equipment",
            (row.right - 146, row.y + 20, 64, 24),
            city._remember_message(player, lambda selected=index: city.equip_inventory_item(player, selected)),
        )
        sell = city.LocationActionButton(
            "Sprzedaj",
            "location_equipment",
            (row.right - 76, row.y + 20, 68, 24),
            city._remember_message(player, lambda selected=index: city.sell_inventory_item(player, selected)),
        )
        equip.draw(screen, small_font, mouse_pos)
        sell.draw(screen, small_font, mouse_pos)
        buttons.extend([equip, sell])
        y += 54
    return buttons


def _draw_right_panel(screen, font, small_font, mouse_pos, location, player, selected_place, message, rect):
    city.draw_panel(screen, rect, city.GOLD)
    buttons = []
    y = rect.y + 16
    effective_message = message or player.get("_location_message", "")
    if effective_message:
        box = pygame.Rect(rect.x + 12, y, rect.width - 24, 38)
        pygame.draw.rect(screen, (45, 55, 48), box, border_radius=7)
        screen.blit(small_font.render(effective_message[:58], True, city.TEXT), (box.x + 8, box.y + 9))
        y = box.bottom + 10

    inner_x = rect.x + 14
    inner_w = rect.width - 28

    if selected_place == "location_shop":
        screen.blit(font.render("Sklep", True, city.TEXT), (inner_x, y))
        buttons += city._draw_offer_cards(
            screen, font, small_font, mouse_pos, location["shop_offers"], "buy",
            inner_x, y + 34, inner_w, "Kup",
        )
    elif selected_place == "location_tavern":
        screen.blit(font.render("Karczma", True, city.TEXT), (inner_x, y))
        buttons += city._draw_offer_cards(
            screen, font, small_font, mouse_pos, location["helper_offers"], "hire",
            inner_x, y + 34, inner_w, "Zatrudnij",
        )
    elif selected_place == "location_board":
        screen.blit(font.render("Tablica ogloszen", True, city.TEXT), (inner_x, y))
        buttons += city._draw_offer_cards(
            screen, font, small_font, mouse_pos, location["quest_offers"], "quest",
            inner_x, y + 34, inner_w, "Pobierz",
        )
    elif selected_place == "location_training":
        buttons += city._draw_training(screen, font, small_font, mouse_pos, rect, location, player, y)
    elif selected_place == "location_healing":
        buttons += city._draw_healing(screen, font, small_font, mouse_pos, rect, player, y)
    elif selected_place == "location_equipment":
        buttons += _draw_compact_equipment(screen, font, small_font, mouse_pos, rect, player, y)
    else:
        screen.blit(font.render("Wybierz miejsce", True, city.TEXT), (inner_x, y))
        lines = [
            "Kliknij obiekt na planszetce wsi",
            "albo wybierz miejsce z listy po lewej.",
        ]
        city.draw_lines(screen, small_font, lines, inner_x, y + 42, city.MUTED, line_h=24, max_width=inner_w)
    return buttons


def draw_village_screen(screen, title_font, font, small_font, mouse_pos, location, player, selected_place=None, message=""):
    city.initialize_location(location)
    city.draw_fallback_background(screen)

    sw, sh = screen.get_size()
    header = pygame.Rect(24, 18, sw - 48, 96)
    body_y = header.bottom + 10
    body_bottom = sh - 32
    body_h = body_bottom - body_y

    left_w = 264
    right_w = 392
    gap = 10
    left = pygame.Rect(24, body_y, left_w, body_h)
    right = pygame.Rect(sw - 24 - right_w, body_y, right_w, body_h)
    scene = pygame.Rect(left.right + gap, body_y, right.left - left.right - gap * 2, body_h)

    _draw_header(screen, title_font, small_font, location, player, header)
    buttons = _draw_left_menu(screen, font, mouse_pos, location, player, selected_place, left)

    image, image_rect = _fit_scene(scene)
    if image is None or image_rect is None:
        return city.draw_city_screen(screen, title_font, font, small_font, mouse_pos, location, player, selected_place, message)

    pygame.draw.rect(screen, (8, 7, 5), scene)
    screen.blit(image, image_rect)
    pygame.draw.rect(screen, city.GOLD, image_rect, 1)

    for label, action, normalized in VILLAGE_HOTSPOTS:
        rect = _hotspot_rect(image_rect, normalized)
        label_pos = (rect.centerx, max(image_rect.top + 20, rect.top + 18))
        hotspot = VillageHotspotButton(label, action, rect, label_pos)
        hotspot.draw_hotspot(screen, small_font, mouse_pos, active=(selected_place == action))
        buttons.append(hotspot)

    buttons += _draw_right_panel(
        screen, font, small_font, mouse_pos, location, player, selected_place, message, right
    )
    return buttons


def install_village_hub(app_module):
    """Podmienia ekran tylko dla wsi; miasta i zamki korzystaja ze starego renderera."""
    if getattr(app_module, "_rise_glory_village_hub_installed", False):
        return

    original = app_module.draw_city_screen

    def wrapped(screen, title_font, font, small_font, mouse_pos, location, player, selected_place=None, message=""):
        if (
            location.get("kind") == "village"
            and not city.is_combat_active()
            and screen.get_width() >= 1250
            and screen.get_height() >= 760
            and not city.parse_quest_action(selected_place)
        ):
            return draw_village_screen(
                screen, title_font, font, small_font, mouse_pos,
                location, player, selected_place, message,
            )
        return original(screen, title_font, font, small_font, mouse_pos, location, player, selected_place, message)

    app_module.draw_city_screen = wrapped
    app_module._rise_glory_village_hub_installed = True
