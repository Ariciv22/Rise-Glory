from pathlib import Path
import pygame

PLAYER_TOPBAR_HEIGHT = 142
LEFT_SCORE_WIDTH = 280
LEFT_SCORE_HEIGHT = 340
LEFT_CARDS_WIDTH = 300
LEFT_CARDS_HEIGHT = 260
RIGHT_LOG_WIDTH = 300
BOTTOM_CITY_HEIGHT = 160
PANEL_HANDLE = 34
PANEL_GAP = 12
EVENT_CARD_W = 250
EVENT_CARD_H = 270

BUTTON_COLOR = (42, 50, 58)
BUTTON_HOVER_COLOR = (62, 74, 84)
BUTTON_ACTIVE_COLOR = (74, 92, 72)
BUTTON_BORDER_COLOR = (120, 140, 150)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT_COLOR = (180, 185, 190)
BACKGROUND_COLOR = (18, 22, 26)
UI_PINK = (255, 155, 200)
UI_ORANGE = (255, 122, 30)
GOLD_BORDER = (145, 104, 48)

ROOT_DIR = Path(__file__).resolve().parent
UI_GRAPHICS_DIR = ROOT_DIR / "Grafiki" / "grafiki UI"


class Button:
    def __init__(self, text, action, rect):
        self.text = text
        self.action = action
        self.rect = pygame.Rect(rect)

    def draw(self, screen, font, mouse_pos, active=False):
        hovered = self.rect.collidepoint(mouse_pos)
        color = BUTTON_ACTIVE_COLOR if active else (BUTTON_HOVER_COLOR if hovered else BUTTON_COLOR)
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, self.rect, 2, border_radius=12)
        if self.text:
            label = font.render(self.text, True, TEXT_COLOR)
            screen.blit(label, label.get_rect(center=self.rect.center))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class GameUIState:
    def __init__(self):
        self.score_open = True
        self.cards_open = True
        self.log_open = True
        self.city_open = True
        self.show_event_card = True
        self.selected_player_id = 1
        self.logs = [
            "Start gry. Wybierz osadnika i odkrywaj mape.",
            "Panele chowasz roznymi strzalkami.",
        ]

    def toggle(self, name):
        if name == "score":
            self.score_open = not self.score_open
        elif name == "cards":
            self.cards_open = not self.cards_open
        elif name == "log":
            self.log_open = not self.log_open
        elif name == "city":
            self.city_open = not self.city_open
        elif name == "event":
            self.show_event_card = not self.show_event_card

    def select_player(self, player_id):
        self.selected_player_id = player_id

    def add_log(self, message):
        self.logs.append(message)
        self.logs = self.logs[-12:]


def draw_background(screen):
    screen.fill(BACKGROUND_COLOR)


def find_ui_image(*names):
    for name in names:
        for ext in ["", ".png", ".jpg", ".jpeg", ".webp"]:
            path = UI_GRAPHICS_DIR / f"{name}{ext}"
            if path.exists():
                return path
    return None


def remove_checker_background(surface):
    cleaned = surface.copy().convert_alpha()
    width, height = cleaned.get_size()
    for y in range(height):
        for x in range(width):
            r, g, b, a = cleaned.get_at((x, y))
            near_gray = abs(r - g) <= 10 and abs(g - b) <= 10 and abs(r - b) <= 10
            if a > 0 and near_gray and r >= 185 and g >= 185 and b >= 185:
                cleaned.set_at((x, y), (r, g, b, 0))
    return cleaned


def crop_to_visible(surface, alpha_threshold=8):
    rect = surface.get_bounding_rect(min_alpha=alpha_threshold)
    if rect.width <= 0 or rect.height <= 0:
        return surface
    cropped = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    cropped.blit(surface, (0, 0), rect)
    return cropped


def load_ui_panel_graphics():
    mapping = {
        "panel1": ("panel1", "panel 1"),
        "panel2": ("panel", "panel2", "panel 2"),
        "panel3": ("panel 3", "panel3"),
        "panel4": ("panel 4", "panel4"),
    }
    loaded = {}
    for key, variants in mapping.items():
        path = find_ui_image(*variants)
        if path:
            image = pygame.image.load(str(path)).convert_alpha()
            loaded[key] = crop_to_visible(remove_checker_background(image))
        else:
            loaded[key] = None
    return loaded


def blit_nine_slice(screen, image, rect, border=38):
    iw, ih = image.get_size()
    if iw <= 0 or ih <= 0 or rect.width <= 0 or rect.height <= 0:
        return
    b = max(8, min(border, iw // 3, ih // 3, rect.width // 3, rect.height // 3))
    src = {
        "tl": pygame.Rect(0, 0, b, b),
        "t": pygame.Rect(b, 0, iw - 2 * b, b),
        "tr": pygame.Rect(iw - b, 0, b, b),
        "l": pygame.Rect(0, b, b, ih - 2 * b),
        "c": pygame.Rect(b, b, iw - 2 * b, ih - 2 * b),
        "r": pygame.Rect(iw - b, b, b, ih - 2 * b),
        "bl": pygame.Rect(0, ih - b, b, b),
        "bt": pygame.Rect(b, ih - b, iw - 2 * b, b),
        "br": pygame.Rect(iw - b, ih - b, b, b),
    }
    dst = {
        "tl": pygame.Rect(rect.x, rect.y, b, b),
        "t": pygame.Rect(rect.x + b, rect.y, rect.width - 2 * b, b),
        "tr": pygame.Rect(rect.right - b, rect.y, b, b),
        "l": pygame.Rect(rect.x, rect.y + b, b, rect.height - 2 * b),
        "c": pygame.Rect(rect.x + b, rect.y + b, rect.width - 2 * b, rect.height - 2 * b),
        "r": pygame.Rect(rect.right - b, rect.y + b, b, rect.height - 2 * b),
        "bl": pygame.Rect(rect.x, rect.bottom - b, b, b),
        "bt": pygame.Rect(rect.x + b, rect.bottom - b, rect.width - 2 * b, b),
        "br": pygame.Rect(rect.right - b, rect.bottom - b, b, b),
    }
    for key in src:
        if src[key].width > 0 and src[key].height > 0 and dst[key].width > 0 and dst[key].height > 0:
            part = image.subsurface(src[key])
            scaled = pygame.transform.smoothscale(part, (dst[key].width, dst[key].height))
            screen.blit(scaled, dst[key].topleft)


def draw_image_panel(screen, rect, image, fallback_border=None, fill_alpha=35):
    dark_back = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    dark_back.fill((0, 0, 0, 125))
    screen.blit(dark_back, rect.topleft)
    if image:
        blit_nine_slice(screen, image, rect)
        if fill_alpha:
            shade = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            shade.fill((0, 0, 0, fill_alpha))
            screen.blit(shade, rect.topleft)
    elif fallback_border:
        pygame.draw.rect(screen, fallback_border, rect, 3, border_radius=8)


def map_display_name(map_key, map_options):
    for key, name in map_options:
        if key == map_key:
            return name
    return "Mapa"


def draw_text_lines(screen, font, lines, x, y, color=MUTED_TEXT_COLOR, line_height=22, max_width=None):
    for line in lines:
        text = str(line)
        if max_width:
            while font.size(text)[0] > max_width and len(text) > 3:
                text = text[:-4] + "..."
        screen.blit(font.render(text, True, color), (x, y))
        y += line_height
    return y


def draw_arrow_handle(screen, rect, direction, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)
    bg = (64, 45, 58) if hovered else (42, 34, 44)
    pygame.draw.rect(screen, bg, rect, border_radius=8)
    pygame.draw.rect(screen, UI_PINK, rect, 3, border_radius=8)
    cx, cy = rect.center
    if direction == "left":
        points = [(cx - 9, cy), (cx + 7, cy - 10), (cx + 7, cy + 10)]
    elif direction == "right":
        points = [(cx + 9, cy), (cx - 7, cy - 10), (cx - 7, cy + 10)]
    elif direction == "down":
        points = [(cx, cy + 9), (cx - 10, cy - 7), (cx + 10, cy - 7)]
    else:
        points = [(cx, cy - 9), (cx - 10, cy + 7), (cx + 10, cy + 7)]
    pygame.draw.polygon(screen, UI_PINK, points)


def calculate_player_stats(player, cities, units):
    city_count = len([city for city in cities if city["player"]["id"] == player["id"]])
    unit_count = len([unit for unit in units if unit.player["id"] == player["id"]])
    return {
        "score": city_count * 3 + unit_count,
        "cities": city_count,
        "units": unit_count,
        "food": city_count * 2,
        "production": city_count + 1,
        "gold": 3,
        "science": 0,
        "culture": 0,
    }


def draw_top_resource_bar(screen, font, small_font, current_player, tile_count, current_map_key, city_count, unit_count, ui_graphics, map_options, max_map_tiles):
    sw, _ = screen.get_size()
    rect = pygame.Rect(0, 0, sw, PLAYER_TOPBAR_HEIGHT)
    draw_image_panel(screen, rect, ui_graphics.get("panel4"), UI_ORANGE, fill_alpha=25)
    pygame.draw.line(screen, UI_ORANGE, (0, PLAYER_TOPBAR_HEIGHT - 2), (sw, PLAYER_TOPBAR_HEIGHT - 2), 2)

    old_clip = screen.get_clip()
    screen.set_clip(rect.inflate(-72, -32))

    title_box = pygame.Rect(58, 24, min(420, sw - 132), 34)
    pygame.draw.rect(screen, (18, 15, 12), title_box, border_radius=10)
    pygame.draw.rect(screen, GOLD_BORDER, title_box, 1, border_radius=10)
    title = font.render(f"Rise & Glory - {map_display_name(current_map_key, map_options)}", True, TEXT_COLOR)
    screen.blit(title, (title_box.x + 14, title_box.y + 6))

    resources = [
        ("Zywnosc", city_count * 2, 132),
        ("Produkcja", city_count + 1, 138),
        ("Zloto", 3, 100),
        ("Nauka", 0, 104),
        ("Kultura", 0, 112),
        ("Kafle", f"{tile_count}/{max_map_tiles}", 118),
        ("Jedn.", unit_count, 100),
    ]

    y = 86
    x = 34
    box_h = 30
    player_box = pygame.Rect(x, y, 118, box_h)
    pygame.draw.rect(screen, (18, 15, 12), player_box, border_radius=9)
    pygame.draw.rect(screen, GOLD_BORDER, player_box, 1, border_radius=9)
    pygame.draw.circle(screen, current_player["color"], (player_box.x + 16, player_box.centery), 9)
    screen.blit(small_font.render(current_player["name"], True, TEXT_COLOR), (player_box.x + 34, player_box.y + 5))
    x = player_box.right + 12

    for label, value, width in resources:
        if x + width > sw - 56:
            break
        box = pygame.Rect(x, y, width, box_h)
        pygame.draw.rect(screen, (18, 15, 12), box, border_radius=9)
        pygame.draw.rect(screen, GOLD_BORDER, box, 1, border_radius=9)
        text = f"{label}: {value}"
        while small_font.size(text)[0] > box.width - 18 and len(text) > 4:
            text = text[:-4] + "..."
        screen.blit(small_font.render(text, True, TEXT_COLOR), (box.x + 9, box.y + 5))
        x = box.right + 10
    screen.set_clip(old_clip)


def draw_score_panel(screen, font, small_font, mouse_pos, ui_state, cities, units, ui_graphics, players):
    buttons = []
    x = 0 if ui_state.score_open else -LEFT_SCORE_WIDTH + PANEL_HANDLE
    y = PLAYER_TOPBAR_HEIGHT + PANEL_GAP
    panel = pygame.Rect(x, y, LEFT_SCORE_WIDTH, LEFT_SCORE_HEIGHT)
    draw_image_panel(screen, panel, ui_graphics.get("panel1"), fill_alpha=25)
    handle = pygame.Rect(x + LEFT_SCORE_WIDTH - PANEL_HANDLE, y + 14, PANEL_HANDLE, 54)
    draw_arrow_handle(screen, handle, "left" if ui_state.score_open else "right", mouse_pos)
    buttons.append(Button("", "toggle_score", handle))

    if ui_state.score_open:
        old_clip = screen.get_clip()
        screen.set_clip(panel.inflate(-46, -34))
        screen.blit(font.render("Tabela wynikow", True, TEXT_COLOR), (x + 52, y + 28))
        py = y + 75
        selected_player = players[0]
        for player in players:
            stats = calculate_player_stats(player, cities, units)
            row = pygame.Rect(x + 24, py - 5, LEFT_SCORE_WIDTH - 62, 30)
            if player["id"] == ui_state.selected_player_id:
                selected_player = player
                pygame.draw.rect(screen, (34, 28, 22), row, border_radius=7)
                pygame.draw.rect(screen, GOLD_BORDER, row, 1, border_radius=7)
            pygame.draw.circle(screen, player["color"], (x + 34, py + 10), 8)
            screen.blit(small_font.render(f"{player['name']}  {stats['score']} pkt", True, TEXT_COLOR), (x + 56, py))
            buttons.append(Button("", f"select_player:{player['id']}", row))
            py += 30

        stats = calculate_player_stats(selected_player, cities, units)
        pygame.draw.line(screen, GOLD_BORDER, (x + 30, py + 6), (x + LEFT_SCORE_WIDTH - 38, py + 6), 1)
        py += 18
        screen.blit(small_font.render(f"Statystyki: {selected_player['name']}", True, TEXT_COLOR), (x + 34, py))
        py += 27
        stat_lines = [
            f"Zywnosc: {stats['food']}",
            f"Produkcja: {stats['production']}",
            f"Zloto: {stats['gold']}",
            f"Nauka: {stats['science']}",
            f"Kultura: {stats['culture']}",
            f"Miasta: {stats['cities']}   Jedn.: {stats['units']}",
        ]
        draw_text_lines(screen, small_font, stat_lines, x + 34, py, MUTED_TEXT_COLOR, line_height=21, max_width=LEFT_SCORE_WIDTH - 70)
        screen.set_clip(old_clip)
    return buttons, [panel]


def draw_cards_panel(screen, font, small_font, mouse_pos, ui_state, ui_graphics):
    buttons = []
    x = 0 if ui_state.cards_open else -LEFT_CARDS_WIDTH + PANEL_HANDLE
    y = PLAYER_TOPBAR_HEIGHT + LEFT_SCORE_HEIGHT + PANEL_GAP * 2 + 24
    panel = pygame.Rect(x, y, LEFT_CARDS_WIDTH, LEFT_CARDS_HEIGHT)
    draw_image_panel(screen, panel, ui_graphics.get("panel1"), fill_alpha=25)
    handle = pygame.Rect(x + LEFT_CARDS_WIDTH - PANEL_HANDLE, y + 14, PANEL_HANDLE, 54)
    draw_arrow_handle(screen, handle, "left" if ui_state.cards_open else "right", mouse_pos)
    buttons.append(Button("", "toggle_cards", handle))
    if ui_state.cards_open:
        old_clip = screen.get_clip()
        screen.set_clip(panel.inflate(-48, -38))
        screen.blit(font.render("Talie kart", True, TEXT_COLOR), (x + 52, y + 30))
        lines = ["Przygody: 50", "Technologie: 0 / do dodania", "Polityki: 0 / do dodania", "Cuda: 0 / do dodania", "Liderzy: 0 / do dodania", "Klik w zeton odkrycia -> karta"]
        draw_text_lines(screen, small_font, lines, x + 32, y + 86, max_width=LEFT_CARDS_WIDTH - 76, line_height=21)
        screen.set_clip(old_clip)
    return buttons, [panel]


def draw_log_panel(screen, font, small_font, mouse_pos, ui_state, ui_graphics):
    sw, sh = screen.get_size()
    buttons = []
    x = sw - RIGHT_LOG_WIDTH if ui_state.log_open else sw - PANEL_HANDLE
    y = PLAYER_TOPBAR_HEIGHT
    h = sh - PLAYER_TOPBAR_HEIGHT - (BOTTOM_CITY_HEIGHT if ui_state.city_open else 0)
    panel = pygame.Rect(x, y, RIGHT_LOG_WIDTH, h)
    draw_image_panel(screen, panel, ui_graphics.get("panel3"), fill_alpha=25)
    handle = pygame.Rect(x, y + 18, PANEL_HANDLE, 54)
    draw_arrow_handle(screen, handle, "right" if ui_state.log_open else "left", mouse_pos)
    buttons.append(Button("", "toggle_log", handle))
    if ui_state.log_open:
        old_clip = screen.get_clip()
        screen.set_clip(panel.inflate(-54, -44))
        screen.blit(font.render("Chat i logi gry", True, TEXT_COLOR), (x + 62, y + 30))
        screen.blit(small_font.render("Co sie dzieje na planszy", True, MUTED_TEXT_COLOR), (x + 62, y + 62))
        py = y + 102
        for line in ui_state.logs[-10:]:
            row = pygame.Rect(x + 34, py - 4, RIGHT_LOG_WIDTH - 68, 34)
            pygame.draw.rect(screen, (20, 18, 15), row, border_radius=8)
            pygame.draw.rect(screen, (125, 92, 52), row, 1, border_radius=8)
            draw_text_lines(screen, small_font, [line], x + 44, py + 4, TEXT_COLOR, max_width=RIGHT_LOG_WIDTH - 88)
            py += 40
        screen.set_clip(old_clip)
    return buttons, [panel]


def draw_event_card(screen, font, small_font, mouse_pos, ui_state, selected_tile):
    sw, _ = screen.get_size()
    if not ui_state.show_event_card:
        handle = pygame.Rect(sw // 2 - 45, PLAYER_TOPBAR_HEIGHT + 12, 90, 34)
        draw_arrow_handle(screen, handle, "down", mouse_pos)
        return [Button("", "toggle_event", handle)], [handle]
    card_x = sw / 2 - EVENT_CARD_W / 2
    card_y = PLAYER_TOPBAR_HEIGHT + 250
    card = pygame.Rect(card_x, card_y, EVENT_CARD_W, EVENT_CARD_H)
    pygame.draw.rect(screen, (20, 18, 15), card, border_radius=10)
    pygame.draw.rect(screen, (160, 108, 55), card, 4, border_radius=10)
    title = "Karta odkrycia"
    desc = "Tu pojawi sie karta, ktora gracz odkrywa i pokazuje wszystkim."
    if selected_tile:
        title = selected_tile.terrain["name"]
        desc = f"Wybrany heks #{selected_tile.tile_id}. Tutaj pozniej podepniemy przygody i zeton odkrycia."
    screen.blit(font.render(title, True, TEXT_COLOR), (card.x + 22, card.y + 24))
    draw_text_lines(screen, small_font, [desc], card.x + 18, card.y + 72, MUTED_TEXT_COLOR, max_width=EVENT_CARD_W - 36)
    hint = small_font.render("Kliknij karte, aby schowac", True, UI_PINK)
    screen.blit(hint, (card.x + 18, card.bottom - 38))
    return [Button("", "toggle_event", card)], [card]


def draw_city_panel(screen, font, small_font, mouse_pos, ui_state, current_player, selected_tile, selected_unit, placement_mode, cities, units, ui_graphics):
    sw, sh = screen.get_size()
    buttons = []
    y = sh - BOTTOM_CITY_HEIGHT if ui_state.city_open else sh - PANEL_HANDLE
    h = BOTTOM_CITY_HEIGHT if ui_state.city_open else PANEL_HANDLE
    panel = pygame.Rect(LEFT_CARDS_WIDTH + PANEL_GAP, y, sw - LEFT_CARDS_WIDTH - RIGHT_LOG_WIDTH - PANEL_GAP * 2, h)
    if not ui_state.log_open:
        panel.width += RIGHT_LOG_WIDTH - PANEL_HANDLE
    draw_image_panel(screen, panel, ui_graphics.get("panel2"), fill_alpha=25)
    handle = pygame.Rect(panel.right - 70, y + 8, 54, PANEL_HANDLE)
    draw_arrow_handle(screen, handle, "down" if ui_state.city_open else "up", mouse_pos)
    buttons.append(Button("", "toggle_city", handle))
    if ui_state.city_open:
        old_clip = screen.get_clip()
        screen.set_clip(panel.inflate(-44, -30))
        screen.blit(font.render("Miasta gracza i ich rozwoj", True, TEXT_COLOR), (panel.x + 34, panel.y + 28))
        player_cities = [city for city in cities if city["player"]["id"] == current_player["id"]]
        city_text = ", ".join(city["name"] for city in player_cities) if player_cities else "Brak miast - zaloz pierwsze miasto osadnikiem."
        draw_text_lines(screen, small_font, [city_text], panel.x + 34, panel.y + 62, MUTED_TEXT_COLOR, max_width=panel.width - 68)
        bx = panel.x + 34
        by = panel.y + 98
        action_buttons = [
            Button("Zaloz miasto", "place_city", (bx, by, 160, 42)),
            Button("Nastepny gracz", "next_player", (bx + 172, by, 170, 42)),
            Button("Nowa tura ruchu", "reset_moves", (bx + 354, by, 180, 42)),
            Button("Anuluj akcje", "cancel_action", (bx + 546, by, 150, 42)),
        ]
        for button in action_buttons:
            button.draw(screen, small_font, mouse_pos, active=(placement_mode and button.action == "place_city"))
        buttons.extend(action_buttons)
        info_x = bx + 740
        selected_tile_name = selected_tile.terrain["name"] if selected_tile else "brak"
        selected_unit_name = selected_unit.name if selected_unit else "brak"
        lines = [f"Kafel: {selected_tile_name}", f"Jednostka: {selected_unit_name}", f"Ruchy: {selected_unit.moves_left}/{2}" if selected_unit else "Ruchy: -"]
        draw_text_lines(screen, small_font, lines, info_x, panel.y + 56, TEXT_COLOR, max_width=max(120, panel.right - info_x - 30))
        screen.set_clip(old_clip)
    return buttons, [panel]


def draw_player_ui(screen, title_font, font, small_font, mouse_pos, ui_state, hovered_tile, camera, current_map_key, tile_count, current_player, placement_mode, selected_tile, selected_unit, cities, units, ui_graphics, players, map_options, max_map_tiles):
    sw, _ = screen.get_size()
    draw_top_resource_bar(screen, font, small_font, current_player, tile_count, current_map_key, len(cities), len(units), ui_graphics, map_options, max_map_tiles)
    buttons = []
    blocking_rects = [pygame.Rect(0, 0, sw, PLAYER_TOPBAR_HEIGHT)]
    score_buttons, score_rects = draw_score_panel(screen, font, small_font, mouse_pos, ui_state, cities, units, ui_graphics, players)
    card_buttons, card_rects = draw_cards_panel(screen, font, small_font, mouse_pos, ui_state, ui_graphics)
    buttons.extend(score_buttons + card_buttons)
    blocking_rects.extend(score_rects + card_rects)
    event_buttons, event_rects = draw_event_card(screen, font, small_font, mouse_pos, ui_state, selected_tile)
    buttons.extend(event_buttons)
    blocking_rects.extend(event_rects)
    city_buttons, city_rects = draw_city_panel(screen, font, small_font, mouse_pos, ui_state, current_player, selected_tile, selected_unit, placement_mode, cities, units, ui_graphics)
    buttons.extend(city_buttons)
    blocking_rects.extend(city_rects)
    log_buttons, log_rects = draw_log_panel(screen, font, small_font, mouse_pos, ui_state, ui_graphics)
    buttons.extend(log_buttons)
    blocking_rects.extend(log_rects)
    return buttons, blocking_rects


def is_over_ui(mouse_pos, rects):
    return any(rect.collidepoint(mouse_pos) for rect in rects)
