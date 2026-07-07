import math
import random
from pathlib import Path

import pygame

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
MIN_SCREEN_WIDTH = 1000
MIN_SCREEN_HEIGHT = 700
FPS = 60

HEX_SIZE = 104
TEXTURE_SIZE = 512
MAX_MAP_TILES = 64
HERO_MOVES_PER_TURN = 4
DRAG_THRESHOLD = 4
ZOOM_STEP = 1.10
MIN_ZOOM = 0.35
MAX_ZOOM = 1.55
DEFAULT_ZOOM = 1.0

ROOT_DIR = Path(__file__).resolve().parent
GRAPHICS_DIR = ROOT_DIR / "Grafiki"

STATE_MENU = "menu"
STATE_MAP_SELECT = "map_select"
STATE_HERO_SELECT = "hero_select"
STATE_GAME = "game"
STATE_MULTIPLAYER = "multiplayer"

TEXT = (235, 235, 235)
MUTED = (180, 185, 190)
BG = (18, 22, 26)
PANEL = (24, 20, 16)
PANEL_DARK = (15, 13, 11)
GOLD = (145, 104, 48)
PINK = (255, 155, 200)
ORANGE = (255, 122, 30)
HOVER = (255, 230, 120)
SELECTED = (120, 210, 255)
MOVE = (120, 210, 255)

TOP_BAR_H = 126
LEFT_PANEL_W = 330
RIGHT_LOG_W = 310
BOTTOM_PANEL_H = 160

MAP_OPTIONS = [
    ("rosette9", "Rozeta 9x9"),
    ("rosette8", "Rozeta 8x8"),
    ("small", "Mala mapa testowa"),
    ("pangea", "Pangea"),
]

HERO_ARCHETYPES = [
    {
        "id": 1,
        "name": "Wojownik",
        "color": (215, 70, 55),
        "stats": {"Walka": 5, "Handel": 2, "Dyplomacja": 2, "Intryga": 1, "Nauka": 1, "Kultura": 1},
        "basic_item": "Prosty miecz",
        "class_item": "Skorzana zbroja",
        "role": "Najlepszy do walki i eskorty.",
    },
    {
        "id": 2,
        "name": "Handlarz",
        "color": (220, 170, 55),
        "stats": {"Handel": 5, "Dyplomacja": 3, "Intryga": 2, "Kultura": 1, "Nauka": 1, "Walka": 0},
        "basic_item": "Sakwa kupca",
        "class_item": "Pierscien kupiecki",
        "role": "Najlepszy do wymiany, kontraktow i towarow.",
    },
    {
        "id": 3,
        "name": "Dyplomata",
        "color": (90, 145, 220),
        "stats": {"Dyplomacja": 5, "Kultura": 3, "Handel": 2, "Nauka": 1, "Intryga": 1, "Walka": 0},
        "basic_item": "Elegancki stroj",
        "class_item": "Pieczec rodu / glejt",
        "role": "Najlepszy do rozmow, lokacji i konfliktow spolecznych.",
    },
    {
        "id": 4,
        "name": "Kulturowiec",
        "color": (170, 95, 210),
        "stats": {"Kultura": 5, "Dyplomacja": 3, "Handel": 1, "Nauka": 1, "Intryga": 1, "Walka": 1},
        "basic_item": "Ozdobny stroj",
        "class_item": "Instrument / kronika",
        "role": "Najlepszy do wydarzen, tlumu i slawy.",
    },
    {
        "id": 5,
        "name": "Intrygant",
        "color": (70, 170, 85),
        "stats": {"Intryga": 5, "Dyplomacja": 2, "Handel": 2, "Walka": 1, "Nauka": 1, "Kultura": 1},
        "basic_item": "Sztylet",
        "class_item": "Kaptur intryganta / pierscien sekretow",
        "role": "Najlepszy do omijania, sabotazu i informacji.",
    },
    {
        "id": 6,
        "name": "Uczony",
        "color": (70, 190, 190),
        "stats": {"Nauka": 5, "Kultura": 2, "Handel": 2, "Dyplomacja": 1, "Intryga": 1, "Walka": 1},
        "basic_item": "Torba badacza",
        "class_item": "Ksiega / mapa ruin",
        "role": "Najlepszy do ruin, mechanizmow i odkrywania slabosci.",
    },
]

TERRAINS = {
    "plains": {"name": "Rowniny", "image": "rowniny.png", "fallback": (112, 156, 76), "weight": 30, "passable": True, "move": 1},
    "forest": {"name": "Las", "image": "las.png", "fallback": (49, 107, 62), "weight": 22, "passable": True, "move": 2},
    "hills": {"name": "Wzgorza", "image": "wzgorza.png", "fallback": (139, 116, 73), "weight": 18, "passable": True, "move": 2},
    "mountain": {"name": "Gory", "image": "gory.png", "fallback": (116, 116, 112), "weight": 12, "passable": False, "move": 99},
    "desert": {"name": "Pustynia", "image": "pustynia.png", "fallback": (194, 165, 92), "weight": 10, "passable": True, "move": 1},
    "tundra": {"name": "Tundra", "image": "tundra.png", "fallback": (145, 170, 154), "weight": 8, "passable": True, "move": 1},
}


def clone_hero(template):
    hero = dict(template)
    hero["stats"] = dict(template["stats"])
    hero["gold"] = 3
    hero["wounds"] = 0
    hero["legend"] = 0
    return hero


class Button:
    def __init__(self, text, action, rect):
        self.text = text
        self.action = action
        self.rect = pygame.Rect(rect)

    def draw(self, screen, font, mouse_pos, active=False):
        hovered = self.rect.collidepoint(mouse_pos)
        bg = (74, 92, 72) if active else ((62, 74, 84) if hovered else (42, 50, 58))
        pygame.draw.rect(screen, bg, self.rect, border_radius=12)
        pygame.draw.rect(screen, (120, 140, 150), self.rect, 2, border_radius=12)
        if self.text:
            label = font.render(self.text, True, TEXT)
            screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class Camera:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.zoom = DEFAULT_ZOOM

    def apply(self, x, y):
        return x * self.zoom + self.x, y * self.zoom + self.y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def zoom_at(self, mouse_pos, factor):
        old_zoom = self.zoom
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom * factor))
        if new_zoom == old_zoom:
            return
        mx, my = mouse_pos
        wx = (mx - self.x) / old_zoom
        wy = (my - self.y) / old_zoom
        self.zoom = new_zoom
        self.x = mx - wx * self.zoom
        self.y = my - wy * self.zoom

    def center_on_tiles(self, tiles):
        if not tiles:
            return
        min_x = min(tile.x for tile in tiles) - HEX_SIZE
        max_x = max(tile.x for tile in tiles) + HEX_SIZE
        min_y = min(tile.y for tile in tiles) - HEX_SIZE
        max_y = max(tile.y for tile in tiles) + HEX_SIZE
        self.zoom = DEFAULT_ZOOM
        self.x = SCREEN_WIDTH / 2 - ((min_x + max_x) / 2) * self.zoom
        self.y = TOP_BAR_H + (SCREEN_HEIGHT - TOP_BAR_H - BOTTOM_PANEL_H) / 2 - ((min_y + max_y) / 2) * self.zoom


class Tile:
    def __init__(self, tile_id, q, r, x, y, terrain_key):
        self.id = tile_id
        self.q = q
        self.r = r
        self.x = x
        self.y = y
        self.terrain_key = terrain_key
        self.terrain = TERRAINS[terrain_key]
        self.points = hex_corners(x, y, HEX_SIZE)

    def screen_points(self, camera):
        return [camera.apply(x, y) for x, y in self.points]

    def center(self, camera):
        return camera.apply(self.x, self.y)

    def contains(self, pos, camera):
        return point_in_polygon(pos, self.screen_points(camera))

    def draw(self, screen, textures, camera, hovered=False, selected=False, valid_move=False):
        sx, sy = self.center(camera)
        size = max(1, int(HEX_SIZE * 2 * camera.zoom))
        texture = pygame.transform.smoothscale(textures[self.terrain_key], (size, size))
        screen.blit(texture, (sx - size / 2, sy - size / 2))
        pts = self.screen_points(camera)
        pygame.draw.polygon(screen, (24, 24, 24), pts, max(1, int(2 * camera.zoom)))
        if valid_move:
            pygame.draw.polygon(screen, MOVE, pts, max(2, int(4 * camera.zoom)))
        if hovered:
            pygame.draw.polygon(screen, HOVER, pts, max(2, int(5 * camera.zoom)))
        if selected:
            pygame.draw.polygon(screen, SELECTED, pts, max(2, int(5 * camera.zoom)))


class HeroToken:
    def __init__(self, hero, tile):
        self.hero = hero
        self.tile = tile
        self.moves = HERO_MOVES_PER_TURN

    @property
    def name(self):
        return "Bohater"

    def reset_moves(self):
        self.moves = HERO_MOVES_PER_TURN

    def can_move_to(self, target):
        if not target or not target.terrain["passable"]:
            return False
        if not are_adjacent(self.tile, target):
            return False
        return self.moves >= target.terrain["move"]

    def move_to(self, target):
        if not self.can_move_to(target):
            return False
        self.moves -= target.terrain["move"]
        self.tile = target
        return True

    def draw(self, screen, camera, font, selected=False):
        sx, sy = self.tile.center(camera)
        center = (int(sx), int(sy - 30 * camera.zoom))
        radius = max(11, int(18 * camera.zoom))
        pygame.draw.circle(screen, self.hero["color"], center, radius + 5)
        pygame.draw.circle(screen, (238, 238, 220), center, radius)
        pygame.draw.circle(screen, (25, 25, 25), center, radius, max(2, int(3 * camera.zoom)))
        label = font.render("B", True, (20, 20, 20))
        screen.blit(label, label.get_rect(center=center))
        if selected:
            pygame.draw.circle(screen, SELECTED, center, radius + 10, max(2, int(4 * camera.zoom)))


class Log:
    def __init__(self):
        self.lines = ["Start prototypu v0.1.", "Wybierz bohatera i ruszaj po Punkty Legendy."]

    def add(self, text):
        self.lines.append(text)
        self.lines = self.lines[-12:]


def hex_corners(cx, cy, size):
    return [(cx + size * math.cos(math.radians(60 * i - 30)), cy + size * math.sin(math.radians(60 * i - 30))) for i in range(6)]


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) + 0.00001) + xi):
            inside = not inside
        j = i
    return inside


def axial_to_pixel(q, r):
    return HEX_SIZE * math.sqrt(3) * (q + r / 2), HEX_SIZE * 1.5 * r


def are_adjacent(a, b):
    return math.hypot(a.x - b.x, a.y - b.y) <= HEX_SIZE * 1.85


def create_fallback_texture(color):
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(surface, color, hex_corners(TEXTURE_SIZE / 2, TEXTURE_SIZE / 2, TEXTURE_SIZE / 2 - 2))
    return surface


def create_hex_texture(image):
    target = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    target.blit(pygame.transform.smoothscale(image, (TEXTURE_SIZE, TEXTURE_SIZE)), (0, 0))
    mask = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    points = [(int(x), int(y)) for x, y in hex_corners(TEXTURE_SIZE / 2, TEXTURE_SIZE / 2, TEXTURE_SIZE / 2 - 2)]
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    target.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return target


def load_textures():
    textures = {}
    for key, terrain in TERRAINS.items():
        path = GRAPHICS_DIR / terrain["image"]
        if path.exists():
            textures[key] = create_hex_texture(pygame.image.load(str(path)).convert_alpha())
        else:
            textures[key] = create_fallback_texture(terrain["fallback"])
    return textures


def generate_rosette_rows(row_lengths):
    raw = []
    h = HEX_SIZE * math.sqrt(3)
    v = HEX_SIZE * 1.5
    center_row = (len(row_lengths) - 1) / 2
    for row, length in enumerate(row_lengths):
        row_width = (length - 1) * h
        y = (row - center_row) * v
        for col in range(length):
            x = col * h - row_width / 2
            raw.append((col, row, x, y))
    return raw


def make_spiral(count, seed):
    rng = random.Random(seed)
    coords = [(0, 0)]
    used = {(0, 0)}
    q = r = 0
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    direction = rng.randrange(6)
    while len(coords) < count:
        moved = False
        for turn in [0, 1, -1, 2, -2, 3]:
            dq, dr = dirs[(direction + turn) % 6]
            nxt = (q + dq, r + dr)
            if nxt not in used:
                q, r = nxt
                direction = (direction + turn) % 6
                used.add(nxt)
                coords.append(nxt)
                moved = True
                break
        if not moved:
            q, r = rng.choice(coords)
    raw = []
    for q, r in coords:
        x, y = axial_to_pixel(q, r)
        raw.append((q, r, x, y))
    return raw


def generate_positions(map_key):
    if map_key == "rosette9":
        return generate_rosette_rows([5, 6, 7, 8, 9, 8, 7, 6, 5])
    if map_key == "rosette8":
        return generate_rosette_rows([4, 5, 6, 7, 8, 7, 6, 5, 4])
    if map_key == "small":
        return generate_rosette_rows([3, 4, 5, 4, 3])
    return make_spiral(48, 44)


def generate_map(map_key):
    keys = list(TERRAINS.keys())
    weights = [TERRAINS[key]["weight"] for key in keys]
    random.seed(42)
    tiles = []
    for idx, (q, r, x, y) in enumerate(generate_positions(map_key)[:MAX_MAP_TILES], start=1):
        terrain = random.choices(keys, weights=weights, k=1)[0]
        tiles.append(Tile(idx, q, r, x, y, terrain))
    return tiles


def find_start_tile(tiles):
    for tile in tiles:
        if tile.terrain["passable"]:
            return tile
    return tiles[0]


def map_name(key):
    return next((name for item_key, name in MAP_OPTIONS if item_key == key), "Mapa")


def wrap(font, text, width):
    words = str(text).split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(screen, font, lines, x, y, color=MUTED, line_h=22, max_width=None):
    for line in lines:
        text = str(line)
        if max_width:
            while font.size(text)[0] > max_width and len(text) > 4:
                text = text[:-4] + "..."
        screen.blit(font.render(text, True, color), (x, y))
        y += line_h
    return y


def draw_title(screen, title_font, font, title, subtitle):
    screen.blit(title_font.render(title, True, TEXT), title_font.render(title, True, TEXT).get_rect(center=(SCREEN_WIDTH / 2, 130)))
    screen.blit(font.render(subtitle, True, MUTED), font.render(subtitle, True, MUTED).get_rect(center=(SCREEN_WIDTH / 2, 178)))


def vertical_buttons(items, start_y, width=420, height=60, gap=16):
    buttons = []
    x = SCREEN_WIDTH / 2 - width / 2
    for idx, (text, action) in enumerate(items):
        buttons.append(Button(text, action, (x, start_y + idx * (height + gap), width, height)))
    return buttons


def draw_menu(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Rise & Glory", "Prototyp v0.1 - bohater, mapa i pierwsze testy")
    buttons = vertical_buttons([("Nowa gra", "new"), ("Multiplayer", "multi"), ("Wyjscie", "exit")], 310)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons


def draw_map_select(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Nowa gra", "Wybierz mape testowa")
    items = [(name, key) for key, name in MAP_OPTIONS] + [("Powrot", "back")]
    buttons = vertical_buttons(items, 280, width=430, height=58, gap=14)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons


def draw_hero_select(screen, title_font, font, small_font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Wybierz bohatera", "Start: 3 zlota, 0 ran, 0 Punktow Legendy, item podstawowy i klasowy")
    buttons = []
    card_w, card_h = 430, 188
    gap_x, gap_y = 28, 24
    start_x = SCREEN_WIDTH / 2 - (card_w * 2 + gap_x) / 2
    start_y = 230
    for idx, hero in enumerate(HERO_ARCHETYPES):
        col = idx % 2
        row = idx // 2
        rect = pygame.Rect(start_x + col * (card_w + gap_x), start_y + row * (card_h + gap_y), card_w, card_h)
        hovered = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (38, 34, 28) if hovered else PANEL, rect, border_radius=14)
        pygame.draw.rect(screen, hero["color"] if hovered else GOLD, rect, 3, border_radius=14)
        pygame.draw.circle(screen, hero["color"], (rect.x + 28, rect.y + 30), 12)
        screen.blit(font.render(hero["name"], True, TEXT), (rect.x + 52, rect.y + 18))
        stat_line = "  ".join(f"{name[:3]} {value}" for name, value in hero["stats"].items())
        screen.blit(small_font.render(stat_line, True, MUTED), (rect.x + 24, rect.y + 58))
        y = rect.y + 88
        for line in wrap(small_font, hero["role"], card_w - 48)[:2]:
            screen.blit(small_font.render(line, True, TEXT), (rect.x + 24, y))
            y += 22
        eq = f"Start: {hero['basic_item']} + {hero['class_item']}"
        for line in wrap(small_font, eq, card_w - 48)[:2]:
            screen.blit(small_font.render(line, True, MUTED), (rect.x + 24, y))
            y += 21
        buttons.append(Button("", hero["id"], rect))
    back = Button("Powrot", "back", (SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT - 84, 240, 52))
    back.draw(screen, font, mouse)
    buttons.append(back)
    return buttons


def draw_multiplayer(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Multiplayer", "Tryb do dodania pozniej")
    buttons = vertical_buttons([("Powrot", "back")], 390)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons


def draw_panel(screen, rect, border=GOLD):
    pygame.draw.rect(screen, PANEL, rect, border_radius=12)
    pygame.draw.rect(screen, border, rect, 2, border_radius=12)


def draw_game_ui(screen, font, small_font, hero, token, selected_tile, logs, current_map):
    sw, sh = screen.get_size()
    top = pygame.Rect(0, 0, sw, TOP_BAR_H)
    draw_panel(screen, top, ORANGE)
    title = f"Rise & Glory - {map_name(current_map)}"
    screen.blit(font.render(title, True, TEXT), (36, 26))
    top_stats = [
        f"Bohater: {hero['name']}",
        f"Legenda: {hero['legend']}",
        f"Zloto: {hero['gold']}",
        f"Rany: {hero['wounds']}/5",
        f"Ruch: {token.moves}/{HERO_MOVES_PER_TURN}",
    ]
    x = 36
    for item in top_stats:
        box = pygame.Rect(x, 78, 150, 30)
        draw_panel(screen, box)
        screen.blit(small_font.render(item, True, TEXT), (box.x + 9, box.y + 6))
        x += box.width + 10

    left = pygame.Rect(12, TOP_BAR_H + 12, LEFT_PANEL_W, sh - TOP_BAR_H - BOTTOM_PANEL_H - 28)
    draw_panel(screen, left)
    screen.blit(font.render("Bohater", True, TEXT), (left.x + 28, left.y + 24))
    pygame.draw.circle(screen, hero["color"], (left.x + 34, left.y + 74), 12)
    screen.blit(font.render(hero["name"], True, TEXT), (left.x + 58, left.y + 62))
    y = left.y + 104
    y = draw_lines(screen, small_font, wrap(small_font, hero["role"], left.width - 56), left.x + 28, y, MUTED, max_width=left.width - 56)
    y += 16
    screen.blit(small_font.render("Zdolnosci", True, TEXT), (left.x + 28, y))
    y += 26
    for stat, value in hero["stats"].items():
        row = pygame.Rect(left.x + 24, y - 4, left.width - 48, 25)
        pygame.draw.rect(screen, PANEL_DARK, row, border_radius=8)
        pygame.draw.rect(screen, GOLD, row, 1, border_radius=8)
        screen.blit(small_font.render(stat, True, TEXT), (row.x + 10, row.y + 4))
        screen.blit(small_font.render(str(value), True, TEXT), (row.right - 30, row.y + 4))
        y += 29
    y += 10
    equip = [f"Item: {hero['basic_item']}", f"Klasowy: {hero['class_item']}"]
    draw_lines(screen, small_font, equip, left.x + 28, y, MUTED, max_width=left.width - 56)

    right = pygame.Rect(sw - RIGHT_LOG_W - 12, TOP_BAR_H + 12, RIGHT_LOG_W, sh - TOP_BAR_H - BOTTOM_PANEL_H - 28)
    draw_panel(screen, right)
    screen.blit(font.render("Dziennik wyprawy", True, TEXT), (right.x + 26, right.y + 24))
    y = right.y + 70
    for line in logs.lines[-9:]:
        row = pygame.Rect(right.x + 18, y - 4, right.width - 36, 34)
        pygame.draw.rect(screen, PANEL_DARK, row, border_radius=8)
        draw_lines(screen, small_font, [line], row.x + 8, row.y + 7, TEXT, max_width=row.width - 16)
        y += 40

    bottom = pygame.Rect(LEFT_PANEL_W + 26, sh - BOTTOM_PANEL_H - 12, sw - LEFT_PANEL_W - RIGHT_LOG_W - 52, BOTTOM_PANEL_H)
    draw_panel(screen, bottom)
    screen.blit(font.render("Akcje bohatera", True, TEXT), (bottom.x + 28, bottom.y + 24))
    desc = "Stare akcje cywilizacyjne usuniete: nie ma osadnika, zakladania miast, zywnosci ani produkcji."
    draw_lines(screen, small_font, [desc], bottom.x + 28, bottom.y + 58, MUTED, max_width=bottom.width - 56)
    buttons = [
        Button("Koniec tury", "end_turn", (bottom.x + 28, bottom.y + 102, 150, 42)),
        Button("Odpocznij", "rest", (bottom.x + 190, bottom.y + 102, 130, 42)),
        Button("Odnow ruch", "reset_moves", (bottom.x + 332, bottom.y + 102, 150, 42)),
    ]
    for button in buttons:
        button.draw(screen, small_font, pygame.mouse.get_pos())

    info_x = bottom.x + 520
    tile_name = selected_tile.terrain["name"] if selected_tile else "brak"
    tile_move = selected_tile.terrain["move"] if selected_tile else "-"
    draw_lines(screen, small_font, [f"Wybrany heks: {tile_name}", f"Koszt ruchu: {tile_move}", "Questy podepniemy w nastepnym kroku."], info_x, bottom.y + 58, TEXT, max_width=bottom.right - info_x - 24)
    return buttons


def ui_rects(screen):
    sw, sh = screen.get_size()
    return [
        pygame.Rect(0, 0, sw, TOP_BAR_H),
        pygame.Rect(12, TOP_BAR_H + 12, LEFT_PANEL_W, sh - TOP_BAR_H - BOTTOM_PANEL_H - 28),
        pygame.Rect(sw - RIGHT_LOG_W - 12, TOP_BAR_H + 12, RIGHT_LOG_W, sh - TOP_BAR_H - BOTTOM_PANEL_H - 28),
        pygame.Rect(LEFT_PANEL_W + 26, sh - BOTTOM_PANEL_H - 12, sw - LEFT_PANEL_W - RIGHT_LOG_W - 52, BOTTOM_PANEL_H),
    ]


def over_ui(pos, rects):
    return any(rect.collidepoint(pos) for rect in rects)


def create_window(fullscreen=False):
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)


def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    screen = create_window(False)
    pygame.display.set_caption("Rise & Glory")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20, bold=True)
    small_font = pygame.font.SysFont("arial", 17, bold=True)
    token_font = pygame.font.SysFont("arial", 17, bold=True)
    title_font = pygame.font.SysFont("arial", 42, bold=True)

    textures = load_textures()
    camera = Camera()
    state = STATE_MENU
    current_map = "rosette9"
    hero = clone_hero(HERO_ARCHETYPES[0])
    tiles = generate_map(current_map)
    camera.center_on_tiles(tiles)
    token = HeroToken(hero, find_start_tile(tiles))
    selected_tile = None
    selected_token = token
    logs = Log()
    buttons = []
    game_buttons = []
    dragging = False
    drag_moved = False
    drag_start = (0, 0)
    last_mouse = (0, 0)
    fullscreen = False
    running = True

    while running:
        mouse = pygame.mouse.get_pos()
        hovered = None
        rects = ui_rects(screen) if state == STATE_GAME else []
        if state == STATE_GAME and not dragging and not over_ui(mouse, rects):
            for tile in tiles:
                if tile.contains(mouse, camera):
                    hovered = tile
                    break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE and not fullscreen:
                SCREEN_WIDTH = max(MIN_SCREEN_WIDTH, event.w)
                SCREEN_HEIGHT = max(MIN_SCREEN_HEIGHT, event.h)
                screen = create_window(False)
                if state == STATE_GAME:
                    camera.center_on_tiles(tiles)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = STATE_MENU if state == STATE_GAME else STATE_MENU if state != STATE_MENU else STATE_MENU
                elif event.key == pygame.K_SPACE and state == STATE_GAME:
                    camera.center_on_tiles(tiles)
                elif event.key in [pygame.K_TAB, pygame.K_n] and state == STATE_GAME:
                    token.reset_moves()
                    logs.add(f"Nowa tura: {hero['name']}. Ruch odnowiony.")
                elif event.key == pygame.K_r and state == STATE_GAME:
                    tiles = generate_map(current_map)
                    camera.center_on_tiles(tiles)
                    token = HeroToken(hero, find_start_tile(tiles))
                    selected_token = token
                    selected_tile = None
                    logs.add("Mapa zresetowana.")
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = create_window(True)
                        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
                    else:
                        SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1000
                        screen = create_window(False)
                    if state == STATE_GAME:
                        camera.center_on_tiles(tiles)
            elif event.type == pygame.MOUSEWHEEL and state == STATE_GAME and not over_ui(mouse, rects):
                camera.zoom_at(mouse, ZOOM_STEP if event.y > 0 else 1 / ZOOM_STEP)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and state == STATE_GAME and not over_ui(event.pos, rects):
                dragging = True
                drag_moved = False
                drag_start = event.pos
                last_mouse = event.pos
            elif event.type == pygame.MOUSEMOTION and dragging and state == STATE_GAME:
                dx = event.pos[0] - last_mouse[0]
                dy = event.pos[1] - last_mouse[1]
                if abs(event.pos[0] - drag_start[0]) > DRAG_THRESHOLD or abs(event.pos[1] - drag_start[1]) > DRAG_THRESHOLD:
                    drag_moved = True
                camera.move(dx, dy)
                last_mouse = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if state in [STATE_MENU, STATE_MAP_SELECT, STATE_HERO_SELECT, STATE_MULTIPLAYER]:
                    for button in buttons:
                        if button.clicked(event.pos):
                            if state == STATE_MENU:
                                if button.action == "new":
                                    state = STATE_MAP_SELECT
                                elif button.action == "multi":
                                    state = STATE_MULTIPLAYER
                                elif button.action == "exit":
                                    running = False
                            elif state == STATE_MAP_SELECT:
                                if button.action == "back":
                                    state = STATE_MENU
                                else:
                                    current_map = button.action
                                    state = STATE_HERO_SELECT
                            elif state == STATE_HERO_SELECT:
                                if button.action == "back":
                                    state = STATE_MAP_SELECT
                                else:
                                    template = next(item for item in HERO_ARCHETYPES if item["id"] == int(button.action))
                                    hero = clone_hero(template)
                                    tiles = generate_map(current_map)
                                    camera.center_on_tiles(tiles)
                                    token = HeroToken(hero, find_start_tile(tiles))
                                    selected_token = token
                                    selected_tile = None
                                    logs = Log()
                                    logs.add(f"Wybrano bohatera: {hero['name']}.")
                                    logs.add(f"Mapa: {map_name(current_map)}.")
                                    state = STATE_GAME
                            elif state == STATE_MULTIPLAYER:
                                state = STATE_MENU
                            break
                elif state == STATE_GAME:
                    dragging = False
                    clicked_button = False
                    for button in game_buttons:
                        if button.clicked(event.pos):
                            clicked_button = True
                            if button.action in ["end_turn", "reset_moves"]:
                                token.reset_moves()
                                logs.add(f"Nowa tura: {hero['name']}. Ruch odnowiony.")
                            elif button.action == "rest":
                                if hero["wounds"] > 0:
                                    hero["wounds"] -= 1
                                    logs.add(f"{hero['name']} odpoczywa i leczy 1 rane.")
                                else:
                                    logs.add("Bohater nie ma ran do leczenia.")
                            break
                    if not clicked_button and not drag_moved and not over_ui(event.pos, rects):
                        for tile in tiles:
                            if tile.contains(event.pos, camera):
                                selected_tile = tile
                                if selected_token and selected_token.can_move_to(tile):
                                    selected_token.move_to(tile)
                                    logs.add(f"{hero['name']} rusza na heks {tile.id}. Koszt: {tile.terrain['move']}.")
                                elif tile == token.tile:
                                    selected_token = token
                                    logs.add("Wybrano bohatera.")
                                else:
                                    selected_token = None
                                break

        if state == STATE_MENU:
            buttons = draw_menu(screen, title_font, font, mouse)
            game_buttons = []
        elif state == STATE_MAP_SELECT:
            buttons = draw_map_select(screen, title_font, font, mouse)
            game_buttons = []
        elif state == STATE_HERO_SELECT:
            buttons = draw_hero_select(screen, title_font, font, small_font, mouse)
            game_buttons = []
        elif state == STATE_MULTIPLAYER:
            buttons = draw_multiplayer(screen, title_font, font, mouse)
            game_buttons = []
        elif state == STATE_GAME:
            screen.fill(BG)
            for tile in tiles:
                valid = selected_token.can_move_to(tile) if selected_token else False
                tile.draw(screen, textures, camera, hovered=(tile == hovered), selected=(tile == selected_tile), valid_move=valid)
            token.draw(screen, camera, token_font, selected=(selected_token == token))
            game_buttons = draw_game_ui(screen, font, small_font, hero, token, selected_tile, logs, current_map)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
