import math
import random
from pathlib import Path

import pygame

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
MIN_SCREEN_WIDTH = 1000
MIN_SCREEN_HEIGHT = 700
FPS = 60

HEX_SIZE = 118
TEXTURE_SIZE = 512
DRAG_THRESHOLD = 5
MAX_MAP_TILES = 64
UNIT_MOVES_PER_TURN = 2

ZOOM_STEP = 1.10
MIN_ZOOM = 0.35
MAX_ZOOM = 1.50
DEFAULT_ZOOM = 1.0

TOP_UI_HEIGHT = 88
BOTTOM_UI_HEIGHT = 70
SIDE_PANEL_WIDTH = 340

BACKGROUND_COLOR = (18, 22, 26)
PANEL_COLOR = (28, 33, 38)
PANEL_DARK_COLOR = (18, 22, 26)
BUTTON_COLOR = (42, 50, 58)
BUTTON_HOVER_COLOR = (62, 74, 84)
BUTTON_ACTIVE_COLOR = (74, 92, 72)
BUTTON_DISABLED_COLOR = (34, 38, 42)
BUTTON_BORDER_COLOR = (120, 140, 150)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT_COLOR = (180, 185, 190)
HEX_BORDER_COLOR = (24, 24, 24)
HEX_HOVER_COLOR = (255, 230, 120)
HEX_SELECTED_COLOR = (120, 210, 255)
CITY_COLOR = (245, 230, 170)
CITY_BORDER_COLOR = (42, 32, 18)
VALID_MOVE_COLOR = (120, 210, 255)
VALID_CITY_COLOR = (125, 240, 150)

ROOT_DIR = Path(__file__).resolve().parent
GRAPHICS_DIR = ROOT_DIR / "Grafiki"

GAME_STATE_MENU = "menu"
GAME_STATE_MAP_SELECT = "map_select"
GAME_STATE_PLAYER_SELECT = "player_select"
GAME_STATE_GAME = "game"
GAME_STATE_MULTIPLAYER = "multiplayer"

MAP_OPTIONS = [
    ("catan", "Rozeta ala Catan"),
    ("rosette8", "Rozeta 8x8"),
    ("archipelago", "Archipelag"),
    ("fractal", "Fraktal"),
    ("pangea", "Pangea"),
]

PLAYERS = [
    {"id": 1, "name": "Gracz 1", "color": (215, 70, 55)},
    {"id": 2, "name": "Gracz 2", "color": (65, 130, 220)},
    {"id": 3, "name": "Gracz 3", "color": (70, 170, 85)},
    {"id": 4, "name": "Gracz 4", "color": (220, 170, 55)},
]

TERRAINS = {
    "plains": {"name": "Rowniny", "image": "rowniny.png", "fallback": (112, 156, 76), "weight": 30, "land": True, "passable": True, "city": True},
    "forest": {"name": "Las", "image": "las.png", "fallback": (49, 107, 62), "weight": 22, "land": True, "passable": True, "city": True},
    "hills": {"name": "Wzgorza", "image": "wzgorza.png", "fallback": (139, 116, 73), "weight": 18, "land": True, "passable": True, "city": True},
    "mountain": {"name": "Gory", "image": "gory.png", "fallback": (116, 116, 112), "weight": 12, "land": True, "passable": False, "city": False},
    "desert": {"name": "Pustynia", "image": "pustynia.png", "fallback": (194, 165, 92), "weight": 10, "land": True, "passable": True, "city": True},
    "tundra": {"name": "Tundra", "image": "tundra.png", "fallback": (145, 170, 154), "weight": 8, "land": True, "passable": True, "city": True},
    "coast": {"name": "Wybrzeze", "image": "wybrzeze.png", "fallback": (56, 128, 164), "weight": 0, "land": False, "passable": False, "city": False},
    "ocean": {"name": "Ocean", "image": "ocean.png", "fallback": (22, 64, 102), "weight": 0, "land": False, "passable": False, "city": False},
}


def hex_corners(center_x, center_y, size):
    return [(center_x + size * math.cos(math.radians(60 * i - 30)), center_y + size * math.sin(math.radians(60 * i - 30))) for i in range(6)]


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


def neighbors(q, r):
    return [(q + 1, r), (q - 1, r), (q, r + 1), (q, r - 1), (q + 1, r - 1), (q - 1, r + 1)]


def are_adjacent_tiles(tile_a, tile_b):
    if not tile_a or not tile_b or tile_a == tile_b:
        return False
    return math.hypot(tile_a.x - tile_b.x, tile_a.y - tile_b.y) <= HEX_SIZE * 1.85


def normalize_pixel_positions(raw_positions):
    min_x = min(pos[2] for pos in raw_positions)
    max_x = max(pos[2] for pos in raw_positions)
    min_y = min(pos[3] for pos in raw_positions)
    max_y = max(pos[3] for pos in raw_positions)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    return [(col, row, x - center_x, y - center_y, terrain) for col, row, x, y, terrain in raw_positions]


def axial_set_to_positions(terrain_by_coord):
    raw = []
    for q, r in sorted(terrain_by_coord.keys(), key=lambda item: (item[1], item[0])):
        x, y = axial_to_pixel(q, r)
        raw.append((q, r, x, y, terrain_by_coord[q, r]))
    return normalize_pixel_positions(raw)


def create_hex_texture(source_image):
    target = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    scaled = pygame.transform.smoothscale(source_image, (TEXTURE_SIZE, TEXTURE_SIZE))
    target.blit(scaled, (0, 0))
    points = [(int(x), int(y)) for x, y in hex_corners(TEXTURE_SIZE / 2, TEXTURE_SIZE / 2, TEXTURE_SIZE / 2 - 2)]
    mask = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    target.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return target


def create_fallback_texture(color):
    fallback = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(fallback, color, hex_corners(TEXTURE_SIZE / 2, TEXTURE_SIZE / 2, TEXTURE_SIZE / 2 - 2))
    pygame.draw.circle(fallback, tuple(min(255, c + 18) for c in color), (TEXTURE_SIZE // 2, TEXTURE_SIZE // 2), TEXTURE_SIZE // 4)
    return fallback


def load_terrain_textures():
    textures = {}
    for terrain_key, terrain in TERRAINS.items():
        image_path = GRAPHICS_DIR / terrain["image"]
        if image_path.exists():
            textures[terrain_key] = create_hex_texture(pygame.image.load(str(image_path)).convert_alpha())
        else:
            textures[terrain_key] = create_fallback_texture(terrain["fallback"])
            print(f"Brak grafiki: {image_path}. Uzywam koloru zastepczego.")
    return textures


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = DEFAULT_ZOOM

    def apply(self, x, y):
        return x * self.zoom + self.x, y * self.zoom + self.y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def zoom_at(self, mouse_pos, zoom_factor):
        old_zoom = self.zoom
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom * zoom_factor))
        if new_zoom == old_zoom:
            return
        mx, my = mouse_pos
        world_x = (mx - self.x) / old_zoom
        world_y = (my - self.y) / old_zoom
        self.zoom = new_zoom
        self.x = mx - world_x * self.zoom
        self.y = my - world_y * self.zoom

    def center_on_tiles(self, tiles):
        if not tiles:
            return
        min_x = min(tile.x for tile in tiles) - HEX_SIZE
        max_x = max(tile.x for tile in tiles) + HEX_SIZE
        min_y = min(tile.y for tile in tiles) - HEX_SIZE
        max_y = max(tile.y for tile in tiles) + HEX_SIZE
        self.zoom = DEFAULT_ZOOM
        self.x = (SCREEN_WIDTH - SIDE_PANEL_WIDTH) / 2 - ((min_x + max_x) / 2) * self.zoom
        self.y = (TOP_UI_HEIGHT + (SCREEN_HEIGHT - BOTTOM_UI_HEIGHT)) / 2 - ((min_y + max_y) / 2) * self.zoom


class Button:
    def __init__(self, text, action, rect):
        self.text = text
        self.action = action
        self.rect = pygame.Rect(rect)

    def draw(self, screen, font, mouse_pos, active=False, disabled=False):
        hovered = self.rect.collidepoint(mouse_pos) and not disabled
        color = BUTTON_DISABLED_COLOR if disabled else (BUTTON_ACTIVE_COLOR if active else (BUTTON_HOVER_COLOR if hovered else BUTTON_COLOR))
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, self.rect, 2, border_radius=12)
        label = font.render(self.text, True, MUTED_TEXT_COLOR if disabled else TEXT_COLOR)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class Unit:
    def __init__(self, unit_id, unit_type, player, tile):
        self.unit_id = unit_id
        self.unit_type = unit_type
        self.player = player
        self.tile = tile
        self.moves_left = UNIT_MOVES_PER_TURN

    @property
    def name(self):
        return "Osadnik" if self.unit_type == "settler" else "Wojownik"

    @property
    def short_label(self):
        return "O" if self.unit_type == "settler" else "W"

    def reset_moves(self):
        self.moves_left = UNIT_MOVES_PER_TURN

    def can_move_to(self, target_tile, units):
        if self.moves_left <= 0 or not target_tile or not target_tile.terrain.get("passable"):
            return False
        if not are_adjacent_tiles(self.tile, target_tile):
            return False
        if any(unit.tile == target_tile for unit in units if unit != self):
            return False
        return True

    def move_to(self, target_tile, units):
        if not self.can_move_to(target_tile, units):
            return False
        self.tile = target_tile
        self.moves_left -= 1
        return True

    def draw(self, screen, camera, font, selected=False, stack_offset=0):
        sx, sy = self.tile.screen_position(camera)
        token_x = sx + stack_offset * 24 * camera.zoom
        token_y = sy - 34 * camera.zoom
        radius = max(12, int(18 * camera.zoom))
        pygame.draw.circle(screen, self.player["color"], (int(token_x), int(token_y)), radius + 5)
        pygame.draw.circle(screen, (238, 238, 220), (int(token_x), int(token_y)), radius)
        pygame.draw.circle(screen, (25, 25, 25), (int(token_x), int(token_y)), radius, max(2, int(3 * camera.zoom)))
        label = font.render(self.short_label, True, (20, 20, 20))
        screen.blit(label, label.get_rect(center=(token_x, token_y)))
        if selected:
            pygame.draw.circle(screen, HEX_SELECTED_COLOR, (int(token_x), int(token_y)), radius + 10, max(2, int(4 * camera.zoom)))


class HexTile:
    def __init__(self, tile_id, board_col, board_row, x, y, terrain_key):
        self.tile_id = tile_id
        self.board_col = board_col
        self.board_row = board_row
        self.x = x
        self.y = y
        self.terrain_key = terrain_key
        self.terrain = TERRAINS[terrain_key]
        self.base_points = hex_corners(x, y, HEX_SIZE)
        self.city = None

    def screen_points(self, camera):
        return [camera.apply(x, y) for x, y in self.base_points]

    def screen_position(self, camera):
        return camera.apply(self.x, self.y)

    def can_found_city_here(self):
        return self.terrain.get("city") and self.city is None

    def draw_city(self, screen, camera):
        if not self.city:
            return
        sx, sy = self.screen_position(camera)
        scale = camera.zoom
        w = max(34, int(46 * scale))
        h = max(22, int(30 * scale))
        roof_h = max(16, int(22 * scale))
        x = int(sx - w / 2)
        y = int(sy - h / 2)
        owner = self.city["player"]
        pygame.draw.circle(screen, owner["color"], (int(sx), int(sy)), max(28, int(35 * scale)))
        pygame.draw.rect(screen, CITY_COLOR, (x, y, w, h), border_radius=max(3, int(5 * scale)))
        roof = [(sx - w / 2 - 5 * scale, y), (sx, y - roof_h), (sx + w / 2 + 5 * scale, y)]
        pygame.draw.polygon(screen, owner["color"], roof)
        pygame.draw.polygon(screen, CITY_BORDER_COLOR, roof, max(2, int(3 * scale)))
        pygame.draw.rect(screen, CITY_BORDER_COLOR, (x, y, w, h), max(2, int(3 * scale)), border_radius=max(3, int(5 * scale)))
        pygame.draw.rect(screen, CITY_BORDER_COLOR, (int(sx - 5 * scale), int(y + h - 14 * scale), max(8, int(11 * scale)), max(10, int(14 * scale))))

    def draw(self, screen, textures, camera, hovered=False, selected=False, valid_move=False, valid_city=False):
        texture = textures[self.terrain_key]
        sx, sy = self.screen_position(camera)
        draw_size = max(1, int(HEX_SIZE * 2 * camera.zoom))
        screen.blit(pygame.transform.smoothscale(texture, (draw_size, draw_size)), (sx - draw_size / 2, sy - draw_size / 2))
        points = self.screen_points(camera)
        pygame.draw.polygon(screen, HEX_BORDER_COLOR, points, max(1, int(2 * camera.zoom)))
        if valid_move:
            pygame.draw.polygon(screen, VALID_MOVE_COLOR, points, max(2, int(4 * camera.zoom)))
        if valid_city:
            pygame.draw.polygon(screen, VALID_CITY_COLOR, points, max(2, int(4 * camera.zoom)))
        if hovered:
            pygame.draw.polygon(screen, HEX_HOVER_COLOR, points, max(2, int(5 * camera.zoom)))
        if selected:
            pygame.draw.polygon(screen, HEX_SELECTED_COLOR, points, max(2, int(5 * camera.zoom)))
        self.draw_city(screen, camera)

    def contains_point(self, mouse_pos, camera):
        return point_in_polygon(mouse_pos, self.screen_points(camera))


def make_spiral_path(center_q, center_r, steps, seed=1):
    rng = random.Random(seed)
    coords = [(center_q, center_r)]
    used = {(center_q, center_r)}
    q, r = center_q, center_r
    direction_index = rng.randrange(6)
    directions = neighbors(0, 0)
    while len(coords) < steps:
        preferred = []
        for turn in [0, 1, -1, 2, -2, 3]:
            dq, dr = directions[(direction_index + turn) % 6]
            preferred.append((q + dq, r + dr, (direction_index + turn) % 6))
        moved = False
        for nq, nr, ndir in preferred:
            if (nq, nr) not in used:
                q, r = nq, nr
                direction_index = ndir if rng.random() > 0.25 else rng.randrange(6)
                used.add((q, r))
                coords.append((q, r))
                moved = True
                break
        if not moved:
            border = [coord for coord in used if any(n not in used for n in neighbors(*coord))]
            q, r = rng.choice(border)
            direction_index = rng.randrange(6)
    return coords


def sorted_by_center(coords):
    return sorted(coords, key=lambda coord: (abs(coord[0]) + abs(coord[1]), coord[1], coord[0]))


def add_water_around_land(land_coords, max_tiles=MAX_MAP_TILES):
    land_coords = set(land_coords)
    if len(land_coords) > max_tiles:
        land_coords = set(sorted_by_center(land_coords)[:max_tiles])
    terrain_by_coord = {coord: None for coord in land_coords}
    coast_coords = set()
    for q, r in land_coords:
        for neighbor in neighbors(q, r):
            if neighbor not in land_coords:
                coast_coords.add(neighbor)
    for coord in sorted_by_center(coast_coords):
        if len(terrain_by_coord) >= max_tiles:
            return terrain_by_coord
        terrain_by_coord[coord] = "coast"
    ocean_coords = set()
    for q, r in coast_coords:
        for neighbor in neighbors(q, r):
            if neighbor not in land_coords and neighbor not in coast_coords:
                ocean_coords.add(neighbor)
    for coord in sorted_by_center(ocean_coords):
        if len(terrain_by_coord) >= max_tiles:
            return terrain_by_coord
        terrain_by_coord[coord] = "ocean"
    return terrain_by_coord


def generate_rosette_rows(row_lengths):
    raw_positions = []
    vertical_spacing = HEX_SIZE * 1.5
    horizontal_spacing = HEX_SIZE * math.sqrt(3)
    center_row = (len(row_lengths) - 1) / 2
    for row_index, row_length in enumerate(row_lengths):
        row_width = (row_length - 1) * horizontal_spacing
        y = (row_index - center_row) * vertical_spacing
        for col_index in range(row_length):
            x = col_index * horizontal_spacing - row_width / 2
            raw_positions.append((col_index, row_index, x, y, None))
    return raw_positions


def generate_archipelago_positions():
    rng = random.Random(22)
    land = set()
    for index, center in enumerate([(-4, -3), (4, -2), (-3, 3), (4, 3)]):
        land.update(make_spiral_path(center[0], center[1], [6, 6, 5, 5][index], seed=100 + index))
        border = [coord for coord in land if any(n not in land for n in neighbors(*coord))]
        if border:
            q, r = rng.choice(border)
            land.add(rng.choice(neighbors(q, r)))
    return axial_set_to_positions(add_water_around_land(land, MAX_MAP_TILES))


def generate_fractal_positions():
    rng = random.Random(33)
    land = set(make_spiral_path(0, 0, 34, seed=33))
    for index, start in enumerate(rng.sample(list(land), 3)):
        land.update(make_spiral_path(start[0], start[1], 5, seed=300 + index))
    candidates = [coord for coord in land if len([n for n in neighbors(*coord) if n in land]) >= 4]
    for coord in rng.sample(candidates, min(4, len(candidates))):
        if coord != (0, 0):
            land.remove(coord)
    return axial_set_to_positions(add_water_around_land(land, MAX_MAP_TILES))


def generate_pangea_positions():
    rng = random.Random(44)
    land = set(make_spiral_path(0, 0, 38, seed=44))
    for _ in range(8):
        border = [coord for coord in land if any(n not in land for n in neighbors(*coord))]
        q, r = rng.choice(border)
        land.add(rng.choice(neighbors(q, r)))
    edge_candidates = [coord for coord in land if len([n for n in neighbors(*coord) if n in land]) <= 2]
    for coord in rng.sample(edge_candidates, min(5, len(edge_candidates))):
        land.remove(coord)
    return axial_set_to_positions(add_water_around_land(land, MAX_MAP_TILES))


def generate_map_positions(map_key):
    if map_key == "catan":
        return generate_rosette_rows([3, 4, 5, 4, 3])
    if map_key == "rosette8":
        return generate_rosette_rows([4, 5, 6, 7, 8, 7, 6, 5, 4])
    if map_key == "archipelago":
        return generate_archipelago_positions()
    if map_key == "fractal":
        return generate_fractal_positions()
    if map_key == "pangea":
        return generate_pangea_positions()
    return generate_rosette_rows([4, 5, 6, 7, 8, 7, 6, 5, 4])


def generate_map(map_key):
    land_keys = [key for key, terrain in TERRAINS.items() if terrain.get("land")]
    land_weights = [TERRAINS[key]["weight"] for key in land_keys]
    random.seed(42)
    positions = generate_map_positions(map_key)[:MAX_MAP_TILES]
    tiles = []
    for tile_id, (col, row, x, y, terrain_override) in enumerate(positions, start=1):
        terrain_key = terrain_override or random.choices(land_keys, weights=land_weights, k=1)[0]
        tiles.append(HexTile(tile_id, col, row, x, y, terrain_key))
    return tiles


def map_display_name(map_key):
    for key, name in MAP_OPTIONS:
        if key == map_key:
            return name
    return "Mapa"


def find_start_tiles(tiles):
    passable = [tile for tile in tiles if tile.terrain.get("passable") and tile.terrain.get("city")]
    if not passable:
        return None, None
    start = min(passable, key=lambda tile: math.hypot(tile.x, tile.y))
    adjacent = [tile for tile in passable if are_adjacent_tiles(start, tile)]
    return start, adjacent[0] if adjacent else start


def draw_background(screen):
    screen.fill(BACKGROUND_COLOR)


def build_vertical_buttons(items, start_y, button_width=360, button_height=64, gap=18):
    buttons = []
    x = SCREEN_WIDTH / 2 - button_width / 2
    for index, (text, action) in enumerate(items):
        y = start_y + index * (button_height + gap)
        buttons.append(Button(text, action, (x, y, button_width, button_height)))
    return buttons


def draw_title(screen, title_font, subtitle_font, title, subtitle):
    t = title_font.render(title, True, TEXT_COLOR)
    screen.blit(t, t.get_rect(center=(SCREEN_WIDTH / 2, 170)))
    s = subtitle_font.render(subtitle, True, MUTED_TEXT_COLOR)
    screen.blit(s, s.get_rect(center=(SCREEN_WIDTH / 2, 220)))


def draw_menu(screen, title_font, font, small_font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Rise & Glory", "Strategiczna gra heksowa")
    buttons = build_vertical_buttons([("Nowa gra", "new_game"), ("Multiplayer", "multiplayer"), ("Wyjscie", "exit")], 310)
    for b in buttons:
        b.draw(screen, font, mouse_pos)
    hint = small_font.render("Wybierz opcje z menu", True, MUTED_TEXT_COLOR)
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 90)))
    return buttons


def draw_map_select(screen, title_font, font, small_font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Nowa gra", "Wybierz typ mapy")
    items = [(name, key) for key, name in MAP_OPTIONS] + [("Powrot", "back")]
    buttons = build_vertical_buttons(items, 290, button_width=420, button_height=58, gap=14)
    for b in buttons:
        b.draw(screen, font, mouse_pos)
    hint = small_font.render("Prototyp map: maksymalnie 64 heksy na ten etap testow.", True, MUTED_TEXT_COLOR)
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 80)))
    return buttons


def draw_player_select(screen, title_font, font, small_font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Wybierz gracza", "Start: osadnik + wojownik. Osadnik zaklada pierwsze miasto.")
    buttons = build_vertical_buttons([(p["name"], p["id"]) for p in PLAYERS] + [("Powrot", "back")], 300, button_width=420, button_height=58, gap=14)
    for b in buttons:
        b.draw(screen, font, mouse_pos)
        if isinstance(b.action, int):
            pygame.draw.circle(screen, PLAYERS[b.action - 1]["color"], (b.rect.left + 34, b.rect.centery), 12)
    hint = small_font.render("Kliknij jednostke, potem sasiedni heks. Osadnik ma 2 ruchy na ture.", True, MUTED_TEXT_COLOR)
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 80)))
    return buttons


def draw_multiplayer(screen, title_font, font, small_font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Multiplayer", "Tryb do dodania pozniej")
    info = small_font.render("Na razie zostawilem ekran jako placeholder.", True, MUTED_TEXT_COLOR)
    screen.blit(info, info.get_rect(center=(SCREEN_WIDTH / 2, 310)))
    buttons = build_vertical_buttons([("Powrot", "back")], 390)
    for b in buttons:
        b.draw(screen, font, mouse_pos)
    return buttons


def draw_side_panel(screen, font, small_font, mouse_pos, current_player, selected_tile, selected_unit, cities, units):
    panel_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH
    pygame.draw.rect(screen, PANEL_DARK_COLOR, (panel_x, TOP_UI_HEIGHT, SIDE_PANEL_WIDTH, SCREEN_HEIGHT - TOP_UI_HEIGHT - BOTTOM_UI_HEIGHT))
    pygame.draw.line(screen, BUTTON_BORDER_COLOR, (panel_x, TOP_UI_HEIGHT), (panel_x, SCREEN_HEIGHT - BOTTOM_UI_HEIGHT), 2)
    y = TOP_UI_HEIGHT + 24
    screen.blit(font.render("Panel gracza", True, TEXT_COLOR), (panel_x + 24, y))
    y += 46
    screen.blit(small_font.render("Aktualny gracz:", True, MUTED_TEXT_COLOR), (panel_x + 24, y))
    y += 28
    pygame.draw.circle(screen, current_player["color"], (panel_x + 40, y + 10), 12)
    screen.blit(font.render(current_player["name"], True, TEXT_COLOR), (panel_x + 62, y - 4))
    y += 46
    player_units = [u for u in units if u.player["id"] == current_player["id"]]
    screen.blit(small_font.render(f"Miasta: {len(cities)}   Jednostki: {len(player_units)}", True, MUTED_TEXT_COLOR), (panel_x + 24, y))
    y += 36
    can_found = selected_unit and selected_unit.unit_type == "settler" and selected_unit.tile.can_found_city_here()
    buttons = [(Button("Zaloz miasto z osadnika", "found_city", (panel_x + 24, y, SIDE_PANEL_WIDTH - 48, 48)), not can_found), (Button("Nastepna jednostka", "next_unit", (panel_x + 24, y + 60, SIDE_PANEL_WIDTH - 48, 48)), len(player_units) == 0), (Button("Nowa tura ruchu", "reset_moves", (panel_x + 24, y + 120, SIDE_PANEL_WIDTH - 48, 48)), False), (Button("Anuluj zaznaczenie", "cancel", (panel_x + 24, y + 180, SIDE_PANEL_WIDTH - 48, 48)), False)]
    for b, disabled in buttons:
        b.draw(screen, small_font, mouse_pos, disabled=disabled)
    y += 250
    screen.blit(small_font.render("Wybrany kafel:", True, MUTED_TEXT_COLOR), (panel_x + 24, y))
    y += 28
    if selected_tile:
        screen.blit(font.render(selected_tile.terrain["name"], True, TEXT_COLOR), (panel_x + 24, y))
        y += 30
        txt = "Mozna zalozyc miasto" if selected_tile.can_found_city_here() else "Miasto niedostepne"
        screen.blit(small_font.render(txt, True, TEXT_COLOR if selected_tile.can_found_city_here() else MUTED_TEXT_COLOR), (panel_x + 24, y))
        y += 28
        if selected_tile.city:
            screen.blit(small_font.render(f"Miasto: {selected_tile.city['name']}", True, TEXT_COLOR), (panel_x + 24, y))
    else:
        screen.blit(small_font.render("Kliknij kafel albo jednostke.", True, MUTED_TEXT_COLOR), (panel_x + 24, y))
    y += 64
    screen.blit(small_font.render("Wybrana jednostka:", True, MUTED_TEXT_COLOR), (panel_x + 24, y))
    y += 28
    if selected_unit:
        screen.blit(font.render(selected_unit.name, True, TEXT_COLOR), (panel_x + 24, y))
        y += 30
        screen.blit(small_font.render(f"Ruchy: {selected_unit.moves_left}/{UNIT_MOVES_PER_TURN}", True, TEXT_COLOR), (panel_x + 24, y))
    else:
        screen.blit(small_font.render("Kliknij osadnika lub wojownika.", True, MUTED_TEXT_COLOR), (panel_x + 24, y))
    y = SCREEN_HEIGHT - BOTTOM_UI_HEIGHT - 128
    for line in ["Sterowanie:", "Klik jednostke -> klik sasiedni heks", "B: zaloz miasto osadnikiem", "N: nowa tura ruchu", "TAB: nastepny gracz"]:
        screen.blit(small_font.render(line, True, MUTED_TEXT_COLOR), (panel_x + 24, y))
        y += 22
    return buttons


def draw_game_ui(screen, title_font, font, hovered_tile, current_map_key, tile_count, current_player, selected_unit):
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, TOP_UI_HEIGHT))
    screen.blit(title_font.render(f"Rise & Glory - {map_display_name(current_map_key)}", True, TEXT_COLOR), (28, 18))
    unit_info = f" | {selected_unit.name}: {selected_unit.moves_left} ruchy" if selected_unit else ""
    screen.blit(font.render(f"Kafle: {tile_count}/{MAX_MAP_TILES} | Gracz: {current_player['name']}{unit_info} | ESC | R | F11 | Drag | Scroll", True, MUTED_TEXT_COLOR), (30, 55))
    info_y = SCREEN_HEIGHT - 52
    pygame.draw.rect(screen, PANEL_COLOR, (0, SCREEN_HEIGHT - BOTTOM_UI_HEIGHT, SCREEN_WIDTH, BOTTOM_UI_HEIGHT))
    text = f"Najazd: heks {hovered_tile.tile_id} | {hovered_tile.terrain['name']}" if hovered_tile else "Start zgodnie z kontekstem: osadnik + wojownik. Osadnik ma 2 ruchy i zaklada miasto."
    screen.blit(font.render(text, True, TEXT_COLOR if hovered_tile else MUTED_TEXT_COLOR), (30, info_y))


def create_window(fullscreen=False):
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)


def create_tiles_for_map(map_key, camera):
    tiles = generate_map(map_key)
    camera.center_on_tiles(tiles)
    return tiles


def create_starting_units(tiles, player):
    settler_tile, warrior_tile = find_start_tiles(tiles)
    if not settler_tile:
        return []
    return [Unit(1, "settler", player, settler_tile), Unit(2, "warrior", player, warrior_tile)]


def unit_on_tile(tile, units, player=None):
    for unit in units:
        if unit.tile == tile and (player is None or unit.player["id"] == player["id"]):
            return unit
    return None


def reset_player_units(units, player):
    for unit in units:
        if unit.player["id"] == player["id"]:
            unit.reset_moves()


def next_player_unit(units, player, current_unit):
    player_units = [u for u in units if u.player["id"] == player["id"]]
    if not player_units:
        return None
    if current_unit not in player_units:
        return player_units[0]
    return player_units[(player_units.index(current_unit) + 1) % len(player_units)]


def found_city_from_settler(settler, cities, units):
    if not settler or settler.unit_type != "settler" or not settler.tile.can_found_city_here():
        return False, None
    city = {"name": f"Miasto {len(cities) + 1}", "player": settler.player, "tile_id": settler.tile.tile_id}
    settler.tile.city = city
    cities.append(city)
    units.remove(settler)
    return True, city


def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    fullscreen = False
    screen = create_window(fullscreen)
    pygame.display.set_caption("Rise & Glory")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20, bold=True)
    small_font = pygame.font.SysFont("arial", 17, bold=True)
    token_font = pygame.font.SysFont("arial", 17, bold=True)
    title_font = pygame.font.SysFont("arial", 42, bold=True)
    textures = load_terrain_textures()
    camera = Camera()
    game_state = GAME_STATE_MENU
    current_map_key = "rosette8"
    current_player_index = 0
    tiles = create_tiles_for_map(current_map_key, camera)
    units = []
    cities = []
    selected_tile = None
    selected_unit = None
    running = True
    is_dragging = False
    drag_moved = False
    last_mouse_pos = (0, 0)
    drag_start_pos = (0, 0)
    active_buttons = []
    side_buttons = []
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_in_window = pygame.mouse.get_focused()
        current_player = PLAYERS[current_player_index]
        hovered_tile = None
        if game_state == GAME_STATE_GAME and mouse_in_window and not is_dragging:
            for tile in tiles:
                if tile.contains_point(mouse_pos, camera):
                    hovered_tile = tile
                    break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE and not fullscreen:
                SCREEN_WIDTH = max(MIN_SCREEN_WIDTH, event.w)
                SCREEN_HEIGHT = max(MIN_SCREEN_HEIGHT, event.h)
                screen = create_window(fullscreen)
                if game_state == GAME_STATE_GAME:
                    camera.center_on_tiles(tiles)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == GAME_STATE_GAME:
                        if selected_unit:
                            selected_unit = None
                        else:
                            game_state = GAME_STATE_MENU
                    elif game_state in [GAME_STATE_MAP_SELECT, GAME_STATE_PLAYER_SELECT, GAME_STATE_MULTIPLAYER]:
                        game_state = GAME_STATE_MENU
                    else:
                        running = False
                if event.key == pygame.K_r and game_state == GAME_STATE_GAME:
                    tiles = create_tiles_for_map(current_map_key, camera)
                    units = create_starting_units(tiles, current_player)
                    cities = []
                    selected_unit = units[0] if units else None
                    selected_tile = selected_unit.tile if selected_unit else None
                if event.key == pygame.K_SPACE and game_state == GAME_STATE_GAME:
                    camera.center_on_tiles(tiles)
                if event.key == pygame.K_TAB and game_state == GAME_STATE_GAME:
                    current_player_index = (current_player_index + 1) % len(PLAYERS)
                    selected_unit = None
                    selected_tile = None
                    reset_player_units(units, PLAYERS[current_player_index])
                if event.key == pygame.K_n and game_state == GAME_STATE_GAME:
                    reset_player_units(units, current_player)
                if event.key == pygame.K_b and game_state == GAME_STATE_GAME:
                    ok, city = found_city_from_settler(selected_unit, cities, units)
                    if ok:
                        selected_unit = None
                        selected_tile = next((t for t in tiles if t.tile_id == city["tile_id"]), selected_tile)
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = create_window(fullscreen)
                        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
                    else:
                        SCREEN_WIDTH = 1600
                        SCREEN_HEIGHT = 1000
                        screen = create_window(fullscreen)
                    if game_state == GAME_STATE_GAME:
                        camera.center_on_tiles(tiles)
            if event.type == pygame.MOUSEWHEEL and game_state == GAME_STATE_GAME and mouse_in_window:
                camera.zoom_at(mouse_pos, ZOOM_STEP if event.y > 0 else 1 / ZOOM_STEP)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state == GAME_STATE_GAME and mouse_in_window:
                panel_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH
                if mouse_pos[0] < panel_x and TOP_UI_HEIGHT < mouse_pos[1] < SCREEN_HEIGHT - BOTTOM_UI_HEIGHT:
                    is_dragging = True
                    drag_moved = False
                    drag_start_pos = event.pos
                    last_mouse_pos = event.pos
            if event.type == pygame.MOUSEMOTION and is_dragging and game_state == GAME_STATE_GAME:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                if abs(event.pos[0] - drag_start_pos[0]) > DRAG_THRESHOLD or abs(event.pos[1] - drag_start_pos[1]) > DRAG_THRESHOLD:
                    drag_moved = True
                camera.move(dx, dy)
                last_mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if game_state in [GAME_STATE_MENU, GAME_STATE_MAP_SELECT, GAME_STATE_PLAYER_SELECT, GAME_STATE_MULTIPLAYER]:
                    for button in active_buttons:
                        if button.is_clicked(event.pos):
                            if game_state == GAME_STATE_MENU:
                                if button.action == "new_game":
                                    game_state = GAME_STATE_MAP_SELECT
                                elif button.action == "multiplayer":
                                    game_state = GAME_STATE_MULTIPLAYER
                                elif button.action == "exit":
                                    running = False
                            elif game_state == GAME_STATE_MAP_SELECT:
                                if button.action == "back":
                                    game_state = GAME_STATE_MENU
                                else:
                                    current_map_key = button.action
                                    game_state = GAME_STATE_PLAYER_SELECT
                            elif game_state == GAME_STATE_PLAYER_SELECT:
                                if button.action == "back":
                                    game_state = GAME_STATE_MAP_SELECT
                                else:
                                    current_player_index = int(button.action) - 1
                                    current_player = PLAYERS[current_player_index]
                                    tiles = create_tiles_for_map(current_map_key, camera)
                                    units = create_starting_units(tiles, current_player)
                                    cities = []
                                    selected_unit = units[0] if units else None
                                    selected_tile = selected_unit.tile if selected_unit else None
                                    game_state = GAME_STATE_GAME
                            elif game_state == GAME_STATE_MULTIPLAYER and button.action == "back":
                                game_state = GAME_STATE_MENU
                            break
                elif game_state == GAME_STATE_GAME:
                    is_dragging = False
                    clicked_button = False
                    for button, disabled in side_buttons:
                        if not disabled and button.is_clicked(event.pos):
                            clicked_button = True
                            if button.action == "found_city":
                                ok, city = found_city_from_settler(selected_unit, cities, units)
                                if ok:
                                    selected_unit = None
                                    selected_tile = next((t for t in tiles if t.tile_id == city["tile_id"]), selected_tile)
                            elif button.action == "next_unit":
                                selected_unit = next_player_unit(units, current_player, selected_unit)
                                selected_tile = selected_unit.tile if selected_unit else None
                            elif button.action == "reset_moves":
                                reset_player_units(units, current_player)
                            elif button.action == "cancel":
                                selected_unit = None
                            break
                    if not clicked_button and not drag_moved and mouse_in_window:
                        for tile in tiles:
                            if tile.contains_point(event.pos, camera):
                                selected_tile = tile
                                clicked_unit = unit_on_tile(tile, units, current_player)
                                if clicked_unit:
                                    selected_unit = clicked_unit
                                elif selected_unit and selected_unit.can_move_to(tile, units):
                                    selected_unit.move_to(tile, units)
                                    selected_tile = tile
                                else:
                                    selected_unit = None
                                break
        if not mouse_in_window:
            is_dragging = False
        if game_state == GAME_STATE_MENU:
            active_buttons = draw_menu(screen, title_font, font, small_font, mouse_pos)
            side_buttons = []
        elif game_state == GAME_STATE_MAP_SELECT:
            active_buttons = draw_map_select(screen, title_font, font, small_font, mouse_pos)
            side_buttons = []
        elif game_state == GAME_STATE_PLAYER_SELECT:
            active_buttons = draw_player_select(screen, title_font, font, small_font, mouse_pos)
            side_buttons = []
        elif game_state == GAME_STATE_MULTIPLAYER:
            active_buttons = draw_multiplayer(screen, title_font, font, small_font, mouse_pos)
            side_buttons = []
        elif game_state == GAME_STATE_GAME:
            active_buttons = []
            draw_background(screen)
            for tile in tiles:
                valid_move = selected_unit.can_move_to(tile, units) if selected_unit else False
                valid_city = selected_unit and selected_unit.unit_type == "settler" and selected_unit.tile == tile and tile.can_found_city_here()
                tile.draw(screen, textures, camera, hovered=(tile == hovered_tile), selected=(tile == selected_tile), valid_move=valid_move, valid_city=valid_city)
            units_by_tile = {}
            for unit in units:
                units_by_tile.setdefault(unit.tile.tile_id, []).append(unit)
            for tile_units in units_by_tile.values():
                for index, unit in enumerate(tile_units):
                    unit.draw(screen, camera, token_font, selected=(unit == selected_unit), stack_offset=index)
            draw_game_ui(screen, title_font, font, hovered_tile, current_map_key, len(tiles), current_player, selected_unit)
            side_buttons = draw_side_panel(screen, font, small_font, mouse_pos, current_player, selected_tile, selected_unit, cities, units)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
