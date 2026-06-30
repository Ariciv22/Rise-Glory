import math
import random
from pathlib import Path

import pygame

# =========================
# USTAWIENIA
# =========================

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
MIN_SCREEN_WIDTH = 1000
MIN_SCREEN_HEIGHT = 700
FPS = 60

HEX_SIZE = 118
TEXTURE_SIZE = 512
DRAG_THRESHOLD = 4
MAX_MAP_TILES = 64
UNIT_MOVES_PER_TURN = 2

ZOOM_STEP = 1.10
MIN_ZOOM = 0.35
MAX_ZOOM = 1.50
DEFAULT_ZOOM = 1.0

PLAYER_TOPBAR_HEIGHT = 88
LEFT_SCORE_WIDTH = 280
LEFT_SCORE_HEIGHT = 210
LEFT_CARDS_WIDTH = 300
LEFT_CARDS_HEIGHT = 260
RIGHT_LOG_WIDTH = 300
BOTTOM_CITY_HEIGHT = 160
PANEL_HANDLE = 34
PANEL_GAP = 12
EVENT_CARD_W = 210
EVENT_CARD_H = 260

BACKGROUND_COLOR = (18, 22, 26)
PANEL_COLOR = (28, 33, 38)
PANEL_DARK_COLOR = (18, 22, 26)
PANEL_SOFT_COLOR = (35, 42, 49)
BUTTON_COLOR = (42, 50, 58)
BUTTON_HOVER_COLOR = (62, 74, 84)
BUTTON_ACTIVE_COLOR = (74, 92, 72)
BUTTON_BORDER_COLOR = (120, 140, 150)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT_COLOR = (180, 185, 190)
HEX_BORDER_COLOR = (24, 24, 24)
HEX_HOVER_COLOR = (255, 230, 120)
HEX_SELECTED_COLOR = (120, 210, 255)
CITY_COLOR = (245, 230, 170)
CITY_BORDER_COLOR = (42, 32, 18)
UNIT_FILL_COLOR = (238, 238, 220)
VALID_MOVE_COLOR = (120, 210, 255)
UI_PINK = (255, 155, 200)
UI_ORANGE = (255, 122, 30)
UI_GREEN = (20, 180, 70)
UI_BLUE = (0, 160, 220)
UI_RED = (235, 40, 45)
UI_BLACK = (20, 20, 20)
GOLD_BORDER = (145, 104, 48)

ROOT_DIR = Path(__file__).resolve().parent
GRAPHICS_DIR = ROOT_DIR / "Grafiki"
UI_GRAPHICS_DIR = GRAPHICS_DIR / "grafiki UI"

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
    ("rosette9", "Rozeta 9x9"),
]

PLAYERS = [
    {"id": 1, "name": "Gracz 1", "color": (215, 70, 55)},
    {"id": 2, "name": "Gracz 2", "color": (65, 130, 220)},
    {"id": 3, "name": "Gracz 3", "color": (70, 170, 85)},
    {"id": 4, "name": "Gracz 4", "color": (220, 170, 55)},
]

TERRAINS = {
    "plains": {"name": "Rowniny", "image": "rowniny.png", "fallback": (112, 156, 76), "weight": 30, "land": True, "passable": True},
    "forest": {"name": "Las", "image": "las.png", "fallback": (49, 107, 62), "weight": 22, "land": True, "passable": True},
    "hills": {"name": "Wzgorza", "image": "wzgorza.png", "fallback": (139, 116, 73), "weight": 18, "land": True, "passable": True},
    "mountain": {"name": "Gory", "image": "gory.png", "fallback": (116, 116, 112), "weight": 12, "land": True, "passable": False},
    "desert": {"name": "Pustynia", "image": "pustynia.png", "fallback": (194, 165, 92), "weight": 10, "land": True, "passable": True},
    "tundra": {"name": "Tundra", "image": "tundra.png", "fallback": (145, 170, 154), "weight": 8, "land": True, "passable": True},
    "coast": {"name": "Wybrzeze", "image": "wybrzeze.png", "fallback": (56, 128, 164), "weight": 0, "land": False, "passable": False},
    "ocean": {"name": "Ocean", "image": "ocean.png", "fallback": (22, 64, 102), "weight": 0, "land": False, "passable": False},
}

# =========================
# GEOMETRIA HEKSOW
# =========================

def hex_corners(center_x, center_y, size):
    points = []
    for i in range(6):
        angle_rad = math.radians(60 * i - 30)
        points.append((center_x + size * math.cos(angle_rad), center_y + size * math.sin(angle_rad)))
    return points


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) + 0.00001) + xi)
        if intersects:
            inside = not inside
        j = i
    return inside


def axial_to_pixel(q, r):
    return HEX_SIZE * math.sqrt(3) * (q + r / 2), HEX_SIZE * 1.5 * r


def neighbors(q, r):
    return [(q + 1, r), (q - 1, r), (q, r + 1), (q, r - 1), (q + 1, r - 1), (q - 1, r + 1)]


def normalize_pixel_positions(raw_positions):
    min_x = min(pos[2] for pos in raw_positions)
    max_x = max(pos[2] for pos in raw_positions)
    min_y = min(pos[3] for pos in raw_positions)
    max_y = max(pos[3] for pos in raw_positions)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    return [(col, row, x - center_x, y - center_y, terrain) for col, row, x, y, terrain in raw_positions]


def axial_set_to_positions(terrain_by_coord):
    raw_positions = []
    for q, r in sorted(terrain_by_coord.keys(), key=lambda item: (item[1], item[0])):
        x, y = axial_to_pixel(q, r)
        raw_positions.append((q, r, x, y, terrain_by_coord[q, r]))
    return normalize_pixel_positions(raw_positions)


def are_adjacent_tiles(tile_a, tile_b):
    if not tile_a or not tile_b or tile_a == tile_b:
        return False
    distance = math.hypot(tile_a.x - tile_b.x, tile_a.y - tile_b.y)
    return distance <= HEX_SIZE * 1.85

# =========================
# TEKSTURY I GRAFIKI UI
# =========================

def create_hex_texture(source_image):
    target = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    scaled = pygame.transform.smoothscale(source_image, (TEXTURE_SIZE, TEXTURE_SIZE))
    target.blit(scaled, (0, 0))
    center = TEXTURE_SIZE / 2
    radius = TEXTURE_SIZE / 2 - 2
    points = [(int(x), int(y)) for x, y in hex_corners(center, center, radius)]
    mask = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    target.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return target


def create_fallback_texture(color):
    fallback = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    points = hex_corners(TEXTURE_SIZE / 2, TEXTURE_SIZE / 2, TEXTURE_SIZE / 2 - 2)
    pygame.draw.polygon(fallback, color, points)
    pygame.draw.circle(fallback, tuple(min(255, channel + 18) for channel in color), (TEXTURE_SIZE // 2, TEXTURE_SIZE // 2), TEXTURE_SIZE // 4)
    return fallback


def load_terrain_textures():
    textures = {}
    for terrain_key, terrain in TERRAINS.items():
        image_path = GRAPHICS_DIR / terrain["image"]
        if image_path.exists():
            source = pygame.image.load(str(image_path)).convert_alpha()
            textures[terrain_key] = create_hex_texture(source)
        else:
            textures[terrain_key] = create_fallback_texture(terrain["fallback"])
            print(f"Brak grafiki: {image_path}. Uzywam koloru zastepczego.")
    return textures


def find_ui_image(*names):
    extensions = ["", ".png", ".jpg", ".jpeg", ".webp"]
    for name in names:
        for ext in extensions:
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
            checker_white_or_gray = near_gray and r >= 185 and g >= 185 and b >= 185
            if a > 0 and checker_white_or_gray:
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
            image = remove_checker_background(image)
            loaded[key] = crop_to_visible(image)
        else:
            loaded[key] = None
            print(f"Brak grafiki UI dla {key} w: {UI_GRAPHICS_DIR}")
    return loaded


def blit_fit_center(screen, image, rect):
    iw, ih = image.get_size()
    if iw <= 0 or ih <= 0 or rect.width <= 0 or rect.height <= 0:
        return
    scale = min(rect.width / iw, rect.height / ih)
    new_w = max(1, int(iw * scale))
    new_h = max(1, int(ih * scale))
    scaled = pygame.transform.smoothscale(image, (new_w, new_h))
    x = rect.x + (rect.width - new_w) // 2
    y = rect.y + (rect.height - new_h) // 2
    screen.blit(scaled, (x, y))


def blit_fill_crop(screen, image, rect):
    iw, ih = image.get_size()
    if iw <= 0 or ih <= 0 or rect.width <= 0 or rect.height <= 0:
        return
    scale = max(rect.width / iw, rect.height / ih)
    new_w = max(1, int(iw * scale))
    new_h = max(1, int(ih * scale))
    scaled = pygame.transform.smoothscale(image, (new_w, new_h))
    src_x = max(0, (new_w - rect.width) // 2)
    src_y = max(0, (new_h - rect.height) // 2)
    source_rect = pygame.Rect(src_x, src_y, min(rect.width, new_w), min(rect.height, new_h))
    target_x = rect.x + max(0, (rect.width - new_w) // 2)
    target_y = rect.y + max(0, (rect.height - new_h) // 2)
    screen.blit(scaled, (target_x, target_y), source_rect)


def draw_image_panel(screen, rect, image, fallback_border=None, fill_alpha=45, mode="fit"):
    dark_back = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    dark_back.fill((0, 0, 0, 135))
    screen.blit(dark_back, rect.topleft)
    if image:
        if mode == "fill":
            blit_fill_crop(screen, image, rect)
        else:
            blit_fit_center(screen, image, rect)
        if fill_alpha:
            shade = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            shade.fill((0, 0, 0, fill_alpha))
            screen.blit(shade, rect.topleft)
    elif fallback_border:
        pygame.draw.rect(screen, fallback_border, rect, 3, border_radius=8)

# =========================
# KLASY
# =========================

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
        mouse_x, mouse_y = mouse_pos
        world_x = (mouse_x - self.x) / old_zoom
        world_y = (mouse_y - self.y) / old_zoom
        self.zoom = new_zoom
        self.x = mouse_x - world_x * self.zoom
        self.y = mouse_y - world_y * self.zoom

    def center_on_tiles(self, tiles):
        if not tiles:
            self.reset()
            return
        min_x = min(tile.x for tile in tiles) - HEX_SIZE
        max_x = max(tile.x for tile in tiles) + HEX_SIZE
        min_y = min(tile.y for tile in tiles) - HEX_SIZE
        max_y = max(tile.y for tile in tiles) + HEX_SIZE
        map_center_x = (min_x + max_x) / 2
        map_center_y = (min_y + max_y) / 2
        target_x = SCREEN_WIDTH / 2
        target_y = PLAYER_TOPBAR_HEIGHT + (SCREEN_HEIGHT - PLAYER_TOPBAR_HEIGHT - BOTTOM_CITY_HEIGHT) / 2
        self.zoom = DEFAULT_ZOOM
        self.x = target_x - map_center_x * self.zoom
        self.y = target_y - map_center_y * self.zoom

    def reset(self):
        self.x = SCREEN_WIDTH / 2
        self.y = PLAYER_TOPBAR_HEIGHT + (SCREEN_HEIGHT - PLAYER_TOPBAR_HEIGHT - BOTTOM_CITY_HEIGHT) / 2
        self.zoom = DEFAULT_ZOOM


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
        label = font.render(self.text, True, TEXT_COLOR)
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
        if self.unit_type == "settler":
            return "Osadnik"
        return self.unit_type

    def reset_moves(self):
        self.moves_left = UNIT_MOVES_PER_TURN

    def can_move_to(self, target_tile, units):
        if self.moves_left <= 0 or not target_tile:
            return False
        if not target_tile.terrain.get("passable"):
            return False
        if any(unit.tile == target_tile for unit in units):
            return False
        return are_adjacent_tiles(self.tile, target_tile)

    def move_to(self, target_tile, units):
        if not self.can_move_to(target_tile, units):
            return False
        self.tile = target_tile
        self.moves_left -= 1
        return True

    def draw(self, screen, camera, font, selected=False):
        screen_x, screen_y = self.tile.screen_position(camera)
        radius = max(11, int(18 * camera.zoom))
        pygame.draw.circle(screen, self.player["color"], (int(screen_x), int(screen_y - 30 * camera.zoom)), radius + 5)
        pygame.draw.circle(screen, UNIT_FILL_COLOR, (int(screen_x), int(screen_y - 30 * camera.zoom)), radius)
        pygame.draw.circle(screen, (25, 25, 25), (int(screen_x), int(screen_y - 30 * camera.zoom)), radius, max(2, int(3 * camera.zoom)))
        label = font.render("O", True, (20, 20, 20))
        screen.blit(label, label.get_rect(center=(screen_x, screen_y - 30 * camera.zoom)))
        if selected:
            pygame.draw.circle(screen, HEX_SELECTED_COLOR, (int(screen_x), int(screen_y - 30 * camera.zoom)), radius + 10, max(2, int(4 * camera.zoom)))


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

    def can_place_city(self):
        return self.terrain.get("land") and self.terrain_key != "mountain" and self.city is None

    def draw_city(self, screen, camera, font):
        if not self.city:
            return
        screen_x, screen_y = self.screen_position(camera)
        scale = camera.zoom
        base_w = max(30, int(42 * scale))
        base_h = max(20, int(28 * scale))
        roof_h = max(14, int(22 * scale))
        x = int(screen_x - base_w / 2)
        y = int(screen_y - base_h / 2)
        owner = self.city["player"]

        pygame.draw.circle(screen, owner["color"], (int(screen_x), int(screen_y)), max(24, int(31 * scale)))
        pygame.draw.rect(screen, CITY_COLOR, (x, y, base_w, base_h), border_radius=max(3, int(5 * scale)))
        roof = [(screen_x - base_w / 2 - 5 * scale, y), (screen_x, y - roof_h), (screen_x + base_w / 2 + 5 * scale, y)]
        pygame.draw.polygon(screen, owner["color"], roof)
        pygame.draw.polygon(screen, CITY_BORDER_COLOR, roof, max(2, int(3 * scale)))
        pygame.draw.rect(screen, CITY_BORDER_COLOR, (x, y, base_w, base_h), max(2, int(3 * scale)), border_radius=max(3, int(5 * scale)))
        gate_w = max(8, int(10 * scale))
        gate_h = max(10, int(14 * scale))
        pygame.draw.rect(screen, CITY_BORDER_COLOR, (int(screen_x - gate_w / 2), int(y + base_h - gate_h), gate_w, gate_h))

    def draw(self, screen, textures, camera, font, hovered=False, selected=False, placement_mode=False, valid_unit_move=False):
        texture = textures[self.terrain_key]
        screen_x, screen_y = self.screen_position(camera)
        draw_size = max(1, int(HEX_SIZE * 2 * camera.zoom))
        tile_texture = pygame.transform.smoothscale(texture, (draw_size, draw_size))
        screen.blit(tile_texture, (screen_x - draw_size / 2, screen_y - draw_size / 2))
        points = self.screen_points(camera)
        border_width = max(1, int(2 * camera.zoom))
        highlight_width = max(2, int(5 * camera.zoom))
        pygame.draw.polygon(screen, HEX_BORDER_COLOR, points, border_width)
        if valid_unit_move:
            pygame.draw.polygon(screen, VALID_MOVE_COLOR, points, max(2, int(4 * camera.zoom)))
        if hovered:
            pygame.draw.polygon(screen, HEX_HOVER_COLOR, points, highlight_width)
        if selected:
            pygame.draw.polygon(screen, HEX_SELECTED_COLOR, points, highlight_width)
        if placement_mode and self.can_place_city():
            pygame.draw.polygon(screen, (120, 255, 150), points, max(1, int(3 * camera.zoom)))
        self.draw_city(screen, camera, font)

    def contains_point(self, mouse_pos, camera):
        return point_in_polygon(mouse_pos, self.screen_points(camera))


class GameUIState:
    def __init__(self):
        self.score_open = True
        self.cards_open = True
        self.log_open = True
        self.city_open = True
        self.show_event_card = True
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

    def add_log(self, message):
        self.logs.append(message)
        self.logs = self.logs[-12:]

# =========================
# GENERATORY MAP
# =========================

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
    island_centers = [(-4, -3), (4, -2), (-3, 3), (4, 3)]
    sizes = [6, 6, 5, 5]
    land = set()
    for index, center in enumerate(island_centers):
        island = make_spiral_path(center[0], center[1], sizes[index], seed=100 + index)
        land.update(island)
        border = [coord for coord in land if any(n not in land for n in neighbors(*coord))]
        if border:
            q, r = rng.choice(border)
            land.add(rng.choice(neighbors(q, r)))
    return axial_set_to_positions(add_water_around_land(land, MAX_MAP_TILES))


def generate_fractal_positions():
    rng = random.Random(33)
    land = set(make_spiral_path(0, 0, 34, seed=33))
    starts = rng.sample(list(land), 3)
    for index, start in enumerate(starts):
        branch = make_spiral_path(start[0], start[1], 5, seed=300 + index)
        land.update(branch)
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
    if map_key == "rosette9":
        return generate_rosette_rows([5, 6, 7, 8, 9, 8, 7, 6, 5])
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
    positions = generate_map_positions(map_key)
    if len(positions) > MAX_MAP_TILES:
        positions = positions[:MAX_MAP_TILES]
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


def find_start_tile(tiles):
    for tile in tiles:
        if tile.terrain.get("passable") and tile.terrain.get("land"):
            return tile
    return tiles[0] if tiles else None

# =========================
# UI
# =========================

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
    title_surface = title_font.render(title, True, TEXT_COLOR)
    screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH / 2, 170)))
    subtitle_surface = subtitle_font.render(subtitle, True, MUTED_TEXT_COLOR)
    screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(SCREEN_WIDTH / 2, 220)))


def draw_menu(screen, title_font, font, small_font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Rise & Glory", "Strategiczna gra heksowa")
    buttons = build_vertical_buttons([("Nowa gra", "new_game"), ("Multiplayer", "multiplayer"), ("Wyjscie", "exit")], 310)
    for button in buttons:
        button.draw(screen, font, mouse_pos)
    hint = small_font.render("Wybierz opcje z menu", True, MUTED_TEXT_COLOR)
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 90)))
    return buttons


def draw_map_select(screen, title_font, font, small_font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Nowa gra", "Wybierz typ mapy")
    items = [(name, key) for key, name in MAP_OPTIONS]
    items.append(("Powrot", "back"))
    buttons = build_vertical_buttons(items, 290, button_width=420, button_height=58, gap=14)
    for button in buttons:
        button.draw(screen, font, mouse_pos)
    hint = small_font.render("Kazdy generator ma maksymalnie 64 kafle, czyli limit 8x8.", True, MUTED_TEXT_COLOR)
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 80)))
    return buttons


def draw_player_select(screen, title_font, font, small_font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Wybierz gracza", "Startujesz z osadnikiem. Osadnik ma 2 ruchy na ture.")
    items = [(player["name"], player["id"]) for player in PLAYERS]
    items.append(("Powrot", "back"))
    buttons = build_vertical_buttons(items, 300, button_width=420, button_height=58, gap=14)
    for button in buttons:
        button.draw(screen, font, mouse_pos)
        if isinstance(button.action, int):
            player = PLAYERS[button.action - 1]
            pygame.draw.circle(screen, player["color"], (button.rect.left + 34, button.rect.centery), 12)
    hint = small_font.render("W grze kliknij osadnika, potem sasiedni heks. C = zaloz miasto.", True, MUTED_TEXT_COLOR)
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 80)))
    return buttons


def draw_multiplayer(screen, title_font, font, small_font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Multiplayer", "Tryb do dodania pozniej")
    info = small_font.render("Na razie zostawilem ekran jako placeholder.", True, MUTED_TEXT_COLOR)
    screen.blit(info, info.get_rect(center=(SCREEN_WIDTH / 2, 310)))
    buttons = build_vertical_buttons([("Powrot", "back")], 390)
    for button in buttons:
        button.draw(screen, font, mouse_pos)
    return buttons


def draw_text_lines(screen, font, lines, x, y, color=MUTED_TEXT_COLOR, line_height=22, max_width=None):
    for line in lines:
        text = line
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


def draw_top_resource_bar(screen, font, small_font, current_player, tile_count, current_map_key, city_count, unit_count, ui_graphics):
    rect = pygame.Rect(0, 0, SCREEN_WIDTH, PLAYER_TOPBAR_HEIGHT)
    draw_image_panel(screen, rect, ui_graphics.get("panel4"), UI_ORANGE, fill_alpha=25, mode="fill")
    pygame.draw.line(screen, UI_ORANGE, (0, PLAYER_TOPBAR_HEIGHT - 2), (SCREEN_WIDTH, PLAYER_TOPBAR_HEIGHT - 2), 2)

    title = font.render(f"Rise & Glory - {map_display_name(current_map_key)}", True, TEXT_COLOR)
    screen.blit(title, (24, 12))
    subtitle = small_font.render("Surowce i najwazniejsze informacje gracza", True, (255, 210, 150))
    screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH / 2, 32)))

    resources = [
        ("Zywnosc", city_count * 2),
        ("Produkcja", city_count + 1),
        ("Zloto", 3),
        ("Nauka", 0),
        ("Kultura", 0),
        ("Kafle", f"{tile_count}/{MAX_MAP_TILES}"),
        ("Jedn.", unit_count),
    ]
    x = 24
    y = 54
    pygame.draw.circle(screen, current_player["color"], (x + 12, y + 12), 11)
    screen.blit(small_font.render(current_player["name"], True, TEXT_COLOR), (x + 32, y))
    x += 130
    for label, value in resources:
        chip = pygame.Rect(x, y - 3, 116, 32)
        pygame.draw.rect(screen, (20, 18, 15), chip, border_radius=14)
        pygame.draw.rect(screen, GOLD_BORDER, chip, 1, border_radius=14)
        screen.blit(small_font.render(f"{label}: {value}", True, TEXT_COLOR), (x + 10, y + 4))
        x += 124


def draw_score_panel(screen, font, small_font, mouse_pos, ui_state, cities, units, ui_graphics):
    buttons = []
    x = 0 if ui_state.score_open else -LEFT_SCORE_WIDTH + PANEL_HANDLE
    y = PLAYER_TOPBAR_HEIGHT + PANEL_GAP
    panel = pygame.Rect(x, y, LEFT_SCORE_WIDTH, LEFT_SCORE_HEIGHT)
    draw_image_panel(screen, panel, ui_graphics.get("panel1"), UI_GREEN, fill_alpha=25)
    handle = pygame.Rect(x + LEFT_SCORE_WIDTH - PANEL_HANDLE, y + 14, PANEL_HANDLE, 54)
    draw_arrow_handle(screen, handle, "left" if ui_state.score_open else "right", mouse_pos)
    buttons.append(Button("", "toggle_score", handle))

    if ui_state.score_open:
        screen.blit(font.render("Tabela wynikow", True, TEXT_COLOR), (x + 54, y + 22))
        py = y + 70
        for player in PLAYERS:
            city_count = len([city for city in cities if city["player"]["id"] == player["id"]])
            unit_count = len([unit for unit in units if unit.player["id"] == player["id"]])
            score = city_count * 3 + unit_count
            pygame.draw.circle(screen, player["color"], (x + 30, py + 10), 8)
            screen.blit(small_font.render(f"{player['name']}  {score} pkt", True, TEXT_COLOR), (x + 48, py))
            py += 28
    return buttons, [panel]


def draw_cards_panel(screen, font, small_font, mouse_pos, ui_state, ui_graphics):
    buttons = []
    x = 0 if ui_state.cards_open else -LEFT_CARDS_WIDTH + PANEL_HANDLE
    y = PLAYER_TOPBAR_HEIGHT + LEFT_SCORE_HEIGHT + PANEL_GAP * 2 + 145
    panel = pygame.Rect(x, y, LEFT_CARDS_WIDTH, LEFT_CARDS_HEIGHT)
    draw_image_panel(screen, panel, ui_graphics.get("panel1"), UI_BLACK, fill_alpha=25)
    handle = pygame.Rect(x + LEFT_CARDS_WIDTH - PANEL_HANDLE, y + 14, PANEL_HANDLE, 54)
    draw_arrow_handle(screen, handle, "left" if ui_state.cards_open else "right", mouse_pos)
    buttons.append(Button("", "toggle_cards", handle))

    if ui_state.cards_open:
        screen.blit(font.render("Talie kart", True, TEXT_COLOR), (x + 54, y + 24))
        lines = [
            "Przygody: 50",
            "Technologie: 0 / do dodania",
            "Polityki: 0 / do dodania",
            "Cuda: 0 / do dodania",
            "Liderzy: 0 / do dodania",
            "Klik w zeton odkrycia -> karta",
        ]
        draw_text_lines(screen, small_font, lines, x + 24, y + 76, max_width=LEFT_CARDS_WIDTH - 48)
    return buttons, [panel]


def draw_log_panel(screen, font, small_font, mouse_pos, ui_state, ui_graphics):
    buttons = []
    x = SCREEN_WIDTH - RIGHT_LOG_WIDTH if ui_state.log_open else SCREEN_WIDTH - PANEL_HANDLE
    y = PLAYER_TOPBAR_HEIGHT
    h = SCREEN_HEIGHT - PLAYER_TOPBAR_HEIGHT
    if ui_state.city_open:
        h -= BOTTOM_CITY_HEIGHT
    panel = pygame.Rect(x, y, RIGHT_LOG_WIDTH, h)
    draw_image_panel(screen, panel, ui_graphics.get("panel3"), UI_BLUE, fill_alpha=25)
    handle = pygame.Rect(x, y + 18, PANEL_HANDLE, 54)
    draw_arrow_handle(screen, handle, "right" if ui_state.log_open else "left", mouse_pos)
    buttons.append(Button("", "toggle_log", handle))

    if ui_state.log_open:
        screen.blit(font.render("Chat i logi gry", True, TEXT_COLOR), (x + 48, y + 24))
        screen.blit(small_font.render("Co sie dzieje na planszy", True, MUTED_TEXT_COLOR), (x + 48, y + 54))
        py = y + 92
        for line in ui_state.logs[-10:]:
            pygame.draw.rect(screen, (20, 18, 15), (x + 18, py - 4, RIGHT_LOG_WIDTH - 36, 34), border_radius=8)
            pygame.draw.rect(screen, (125, 92, 52), (x + 18, py - 4, RIGHT_LOG_WIDTH - 36, 34), 1, border_radius=8)
            draw_text_lines(screen, small_font, [line], x + 28, py + 4, TEXT_COLOR, max_width=RIGHT_LOG_WIDTH - 56)
            py += 40
    return buttons, [panel]


def draw_event_card(screen, font, small_font, mouse_pos, ui_state, selected_tile):
    if not ui_state.show_event_card:
        handle = pygame.Rect(SCREEN_WIDTH // 2 - 45, PLAYER_TOPBAR_HEIGHT + 12, 90, 34)
        draw_arrow_handle(screen, handle, "down", mouse_pos)
        return [Button("", "toggle_event", handle)], [handle]

    card_x = SCREEN_WIDTH / 2 - EVENT_CARD_W / 2
    card_y = PLAYER_TOPBAR_HEIGHT + 250
    card = pygame.Rect(card_x, card_y, EVENT_CARD_W, EVENT_CARD_H)
    hex_points = hex_corners(SCREEN_WIDTH / 2, PLAYER_TOPBAR_HEIGHT + 285, 270)
    pygame.draw.polygon(screen, (34, 19, 22), hex_points)
    pygame.draw.polygon(screen, (130, 85, 38), hex_points, 5)
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
    buttons = []
    y = SCREEN_HEIGHT - BOTTOM_CITY_HEIGHT if ui_state.city_open else SCREEN_HEIGHT - PANEL_HANDLE
    h = BOTTOM_CITY_HEIGHT if ui_state.city_open else PANEL_HANDLE
    panel = pygame.Rect(LEFT_CARDS_WIDTH + PANEL_GAP, y, SCREEN_WIDTH - LEFT_CARDS_WIDTH - RIGHT_LOG_WIDTH - PANEL_GAP * 2, h)
    if not ui_state.log_open:
        panel.width += RIGHT_LOG_WIDTH - PANEL_HANDLE
    draw_image_panel(screen, panel, ui_graphics.get("panel2"), UI_PINK, fill_alpha=25)
    handle = pygame.Rect(panel.right - 70, y + 8, 54, PANEL_HANDLE)
    draw_arrow_handle(screen, handle, "down" if ui_state.city_open else "up", mouse_pos)
    buttons.append(Button("", "toggle_city", handle))

    if ui_state.city_open:
        screen.blit(font.render("Miasta gracza i ich rozwoj", True, TEXT_COLOR), (panel.x + 18, panel.y + 18))
        player_cities = [city for city in cities if city["player"]["id"] == current_player["id"]]
        city_text = ", ".join(city["name"] for city in player_cities) if player_cities else "Brak miast - zaloz pierwsze miasto osadnikiem."
        draw_text_lines(screen, small_font, [city_text], panel.x + 18, panel.y + 52, MUTED_TEXT_COLOR, max_width=panel.width - 36)

        bx = panel.x + 18
        by = panel.y + 92
        action_buttons = [
            Button("Zaloz miasto", "place_city", (bx, by, 160, 42)),
            Button("Nastepny gracz", "next_player", (bx + 172, by, 170, 42)),
            Button("Nowa tura ruchu", "reset_moves", (bx + 354, by, 180, 42)),
            Button("Anuluj akcje", "cancel_action", (bx + 546, by, 150, 42)),
        ]
        for button in action_buttons:
            button.draw(screen, small_font, mouse_pos, active=(placement_mode and button.action == "place_city"))
        buttons.extend(action_buttons)

        info_x = bx + 720
        selected_tile_name = selected_tile.terrain["name"] if selected_tile else "brak"
        selected_unit_name = selected_unit.name if selected_unit else "brak"
        lines = [
            f"Kafel: {selected_tile_name}",
            f"Jednostka: {selected_unit_name}",
            f"Ruchy: {selected_unit.moves_left}/{UNIT_MOVES_PER_TURN}" if selected_unit else "Ruchy: -",
        ]
        draw_text_lines(screen, small_font, lines, info_x, panel.y + 50, TEXT_COLOR, max_width=max(120, panel.right - info_x - 20))
    return buttons, [panel]


def draw_player_ui(screen, title_font, font, small_font, mouse_pos, ui_state, hovered_tile, camera, current_map_key, tile_count, current_player, placement_mode, selected_tile, selected_unit, cities, units, ui_graphics):
    draw_top_resource_bar(screen, font, small_font, current_player, tile_count, current_map_key, len(cities), len(units), ui_graphics)
    buttons = []
    blocking_rects = [pygame.Rect(0, 0, SCREEN_WIDTH, PLAYER_TOPBAR_HEIGHT)]

    score_buttons, score_rects = draw_score_panel(screen, font, small_font, mouse_pos, ui_state, cities, units, ui_graphics)
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

    if not ui_state.city_open:
        info = "Kliknij osadnika i rusz nim maksymalnie 2 heksy. C = miasto, TAB = gracz, N = ruchy, SPACJA = kamera."
        screen.blit(small_font.render(info, True, MUTED_TEXT_COLOR), (24, SCREEN_HEIGHT - 28))
    return buttons, blocking_rects


def is_over_ui(mouse_pos, rects):
    return any(rect.collidepoint(mouse_pos) for rect in rects)

# =========================
# LOGIKA GRY
# =========================

def create_window(fullscreen=False):
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)


def create_tiles_for_map(map_key, camera):
    tiles = generate_map(map_key)
    camera.center_on_tiles(tiles)
    return tiles


def create_starting_units(tiles, player):
    start_tile = find_start_tile(tiles)
    if not start_tile:
        return []
    return [Unit(1, "settler", player, start_tile)]


def place_city_on_tile(tile, player, cities):
    if not tile or not tile.can_place_city():
        return False
    city_number = len(cities) + 1
    city = {"name": f"Miasto {city_number}", "player": player, "tile_id": tile.tile_id}
    tile.city = city
    cities.append(city)
    return True


def unit_on_tile(tile, units):
    for unit in units:
        if unit.tile == tile:
            return unit
    return None


def reset_player_units(units, player):
    for unit in units:
        if unit.player["id"] == player["id"]:
            unit.reset_moves()

# =========================
# GLOWNA PETLA
# =========================

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
    ui_graphics = load_ui_panel_graphics()
    camera = Camera()
    ui_state = GameUIState()

    game_state = GAME_STATE_MENU
    current_map_key = "rosette8"
    current_player_index = 0
    tiles = create_tiles_for_map(current_map_key, camera)
    units = []
    cities = []
    selected_tile = None
    selected_unit = None
    placement_mode = False
    running = True

    is_dragging = False
    drag_moved = False
    drag_start_pos = (0, 0)
    last_mouse_pos = (0, 0)
    active_buttons = []
    game_ui_buttons = []
    ui_blocking_rects = []

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_in_window = pygame.mouse.get_focused()
        hovered_tile = None
        current_player = PLAYERS[current_player_index]

        if game_state == GAME_STATE_GAME and mouse_in_window and not is_dragging and not is_over_ui(mouse_pos, ui_blocking_rects):
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
                        if placement_mode:
                            placement_mode = False
                        elif selected_unit:
                            selected_unit = None
                        else:
                            game_state = GAME_STATE_MENU
                            selected_tile = None
                    elif game_state in [GAME_STATE_MAP_SELECT, GAME_STATE_PLAYER_SELECT, GAME_STATE_MULTIPLAYER]:
                        game_state = GAME_STATE_MENU
                    else:
                        running = False
                if event.key == pygame.K_r and game_state == GAME_STATE_GAME:
                    tiles = create_tiles_for_map(current_map_key, camera)
                    units = create_starting_units(tiles, current_player)
                    cities = []
                    selected_tile = None
                    selected_unit = units[0] if units else None
                    placement_mode = False
                    ui_state.add_log("Mapa zresetowana.")
                if event.key == pygame.K_SPACE and game_state == GAME_STATE_GAME:
                    camera.center_on_tiles(tiles)
                if event.key == pygame.K_TAB and game_state == GAME_STATE_GAME:
                    current_player_index = (current_player_index + 1) % len(PLAYERS)
                    selected_unit = None
                    placement_mode = False
                    reset_player_units(units, PLAYERS[current_player_index])
                    ui_state.add_log(f"Tura: {PLAYERS[current_player_index]['name']}.")
                if event.key == pygame.K_c and game_state == GAME_STATE_GAME:
                    placement_mode = True
                    selected_unit = None
                    ui_state.add_log("Tryb zakladania miasta wlaczony.")
                if event.key == pygame.K_n and game_state == GAME_STATE_GAME:
                    reset_player_units(units, current_player)
                    ui_state.add_log(f"Odnowiono ruchy: {current_player['name']}.")
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

            if event.type == pygame.MOUSEWHEEL and game_state == GAME_STATE_GAME and mouse_in_window and not is_over_ui(mouse_pos, ui_blocking_rects):
                camera.zoom_at(mouse_pos, ZOOM_STEP if event.y > 0 else 1 / ZOOM_STEP)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == GAME_STATE_GAME and mouse_in_window and not is_over_ui(mouse_pos, ui_blocking_rects):
                    is_dragging = True
                    drag_moved = False
                    drag_start_pos = event.pos
                    last_mouse_pos = event.pos

            if event.type == pygame.MOUSEMOTION and is_dragging and game_state == GAME_STATE_GAME:
                current_pos = event.pos
                dx = current_pos[0] - last_mouse_pos[0]
                dy = current_pos[1] - last_mouse_pos[1]
                if abs(current_pos[0] - drag_start_pos[0]) > DRAG_THRESHOLD or abs(current_pos[1] - drag_start_pos[1]) > DRAG_THRESHOLD:
                    drag_moved = True
                camera.move(dx, dy)
                last_mouse_pos = current_pos

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
                                    selected_tile = None
                                    selected_unit = units[0] if units else None
                                    placement_mode = False
                                    ui_state = GameUIState()
                                    ui_state.add_log(f"Nowa gra: {map_display_name(current_map_key)}.")
                                    game_state = GAME_STATE_GAME
                            elif game_state == GAME_STATE_MULTIPLAYER:
                                if button.action == "back":
                                    game_state = GAME_STATE_MENU
                            break

                elif game_state == GAME_STATE_GAME:
                    is_dragging = False
                    clicked_ui_button = False
                    for button in game_ui_buttons:
                        if button.is_clicked(event.pos):
                            clicked_ui_button = True
                            if button.action.startswith("toggle_"):
                                ui_state.toggle(button.action.replace("toggle_", ""))
                            elif button.action == "place_city":
                                placement_mode = True
                                selected_unit = None
                                ui_state.add_log("Wybierz heks pod miasto.")
                            elif button.action == "next_player":
                                current_player_index = (current_player_index + 1) % len(PLAYERS)
                                selected_unit = None
                                placement_mode = False
                                reset_player_units(units, PLAYERS[current_player_index])
                                ui_state.add_log(f"Tura: {PLAYERS[current_player_index]['name']}.")
                            elif button.action == "reset_moves":
                                reset_player_units(units, current_player)
                                ui_state.add_log(f"Odnowiono ruchy: {current_player['name']}.")
                            elif button.action == "cancel_action":
                                placement_mode = False
                                selected_unit = None
                                ui_state.add_log("Anulowano akcje.")
                            break

                    if not clicked_ui_button and not drag_moved and mouse_in_window and not is_over_ui(event.pos, ui_blocking_rects):
                        for tile in tiles:
                            if tile.contains_point(event.pos, camera):
                                selected_tile = tile
                                tile_unit = unit_on_tile(tile, units)
                                if placement_mode:
                                    if place_city_on_tile(tile, current_player, cities):
                                        placement_mode = False
                                        ui_state.add_log(f"{current_player['name']} zalozyl miasto na heksie {tile.tile_id}.")
                                    else:
                                        ui_state.add_log("Nie mozna zalozyc miasta na tym heksie.")
                                elif selected_unit and selected_unit.can_move_to(tile, units):
                                    selected_unit.move_to(tile, units)
                                    selected_tile = tile
                                    ui_state.add_log(f"{selected_unit.name} ruszyl sie na heks {tile.tile_id}.")
                                elif tile_unit and tile_unit.player["id"] == current_player["id"]:
                                    selected_unit = tile_unit
                                    placement_mode = False
                                    ui_state.add_log(f"Wybrano jednostke: {tile_unit.name}.")
                                else:
                                    selected_unit = None
                                break

        if not mouse_in_window:
            is_dragging = False

        if game_state == GAME_STATE_MENU:
            active_buttons = draw_menu(screen, title_font, font, small_font, mouse_pos)
            game_ui_buttons = []
            ui_blocking_rects = []
        elif game_state == GAME_STATE_MAP_SELECT:
            active_buttons = draw_map_select(screen, title_font, font, small_font, mouse_pos)
            game_ui_buttons = []
            ui_blocking_rects = []
        elif game_state == GAME_STATE_PLAYER_SELECT:
            active_buttons = draw_player_select(screen, title_font, font, small_font, mouse_pos)
            game_ui_buttons = []
            ui_blocking_rects = []
        elif game_state == GAME_STATE_MULTIPLAYER:
            active_buttons = draw_multiplayer(screen, title_font, font, small_font, mouse_pos)
            game_ui_buttons = []
            ui_blocking_rects = []
        elif game_state == GAME_STATE_GAME:
            active_buttons = []
            draw_background(screen)
            for tile in tiles:
                valid_move = selected_unit.can_move_to(tile, units) if selected_unit else False
                tile.draw(screen, textures, camera, token_font, hovered=(tile == hovered_tile), selected=(tile == selected_tile), placement_mode=placement_mode, valid_unit_move=valid_move)
            for unit in units:
                unit.draw(screen, camera, token_font, selected=(unit == selected_unit))
            game_ui_buttons, ui_blocking_rects = draw_player_ui(
                screen, title_font, font, small_font, mouse_pos, ui_state, hovered_tile, camera,
                current_map_key, len(tiles), current_player, placement_mode, selected_tile, selected_unit, cities, units, ui_graphics,
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
