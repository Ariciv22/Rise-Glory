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

ZOOM_STEP = 1.10
MIN_ZOOM = 0.35
MAX_ZOOM = 1.50
DEFAULT_ZOOM = 1.0

TOP_UI_HEIGHT = 88
BOTTOM_UI_HEIGHT = 70

BACKGROUND_COLOR = (18, 22, 26)
PANEL_COLOR = (28, 33, 38)
BUTTON_COLOR = (42, 50, 58)
BUTTON_HOVER_COLOR = (62, 74, 84)
BUTTON_BORDER_COLOR = (120, 140, 150)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT_COLOR = (180, 185, 190)
HEX_BORDER_COLOR = (24, 24, 24)
HEX_HOVER_COLOR = (255, 230, 120)
HEX_SELECTED_COLOR = (120, 210, 255)

ROOT_DIR = Path(__file__).resolve().parent
GRAPHICS_DIR = ROOT_DIR / "Grafiki"

GAME_STATE_MENU = "menu"
GAME_STATE_MAP_SELECT = "map_select"
GAME_STATE_GAME = "game"
GAME_STATE_MULTIPLAYER = "multiplayer"

MAP_OPTIONS = [
    ("catan", "Rozeta ala Catan"),
    ("rosette8", "Rozeta 8x8"),
    ("archipelago", "Archipelag"),
    ("fractal", "Fraktal"),
    ("pangea", "Pangea"),
]

TERRAINS = {
    "plains": {
        "name": "Rowniny",
        "image": "rowniny.png",
        "fallback": (112, 156, 76),
        "weight": 30,
        "land": True,
    },
    "forest": {
        "name": "Las",
        "image": "las.png",
        "fallback": (49, 107, 62),
        "weight": 22,
        "land": True,
    },
    "hills": {
        "name": "Wzgorza",
        "image": "wzgorza.png",
        "fallback": (139, 116, 73),
        "weight": 18,
        "land": True,
    },
    "mountain": {
        "name": "Gory",
        "image": "gory.png",
        "fallback": (116, 116, 112),
        "weight": 12,
        "land": True,
    },
    "desert": {
        "name": "Pustynia",
        "image": "pustynia.png",
        "fallback": (194, 165, 92),
        "weight": 10,
        "land": True,
    },
    "tundra": {
        "name": "Tundra",
        "image": "tundra.png",
        "fallback": (145, 170, 154),
        "weight": 8,
        "land": True,
    },
    "coast": {
        "name": "Wybrzeze",
        "image": "wybrzeze.png",
        "fallback": (56, 128, 164),
        "weight": 0,
        "land": False,
    },
    "ocean": {
        "name": "Ocean",
        "image": "ocean.png",
        "fallback": (22, 64, 102),
        "weight": 0,
        "land": False,
    },
}


# =========================
# GEOMETRIA HEKSOW
# =========================

def hex_corners(center_x, center_y, size):
    points = []

    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = math.radians(angle_deg)
        x = center_x + size * math.cos(angle_rad)
        y = center_y + size * math.sin(angle_rad)
        points.append((x, y))

    return points


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    j = len(polygon) - 1

    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) + 0.00001) + xi
        )

        if intersects:
            inside = not inside

        j = i

    return inside


def axial_to_pixel(q, r):
    x = HEX_SIZE * math.sqrt(3) * (q + r / 2)
    y = HEX_SIZE * 1.5 * r
    return x, y


def neighbors(q, r):
    return [
        (q + 1, r),
        (q - 1, r),
        (q, r + 1),
        (q, r - 1),
        (q + 1, r - 1),
        (q - 1, r + 1),
    ]


def normalize_pixel_positions(raw_positions):
    min_x = min(pos[2] for pos in raw_positions)
    max_x = max(pos[2] for pos in raw_positions)
    min_y = min(pos[3] for pos in raw_positions)
    max_y = max(pos[3] for pos in raw_positions)

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    positions = []
    for col, row, x, y, terrain_override in raw_positions:
        positions.append((col, row, x - center_x, y - center_y, terrain_override))

    return positions


def axial_set_to_positions(terrain_by_coord):
    raw_positions = []

    for q, r in sorted(terrain_by_coord.keys(), key=lambda item: (item[1], item[0])):
        x, y = axial_to_pixel(q, r)
        raw_positions.append((q, r, x, y, terrain_by_coord[q, r]))

    return normalize_pixel_positions(raw_positions)


# =========================
# TEKSTURY
# =========================

def create_hex_texture(source_image):
    target = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)

    scaled = pygame.transform.smoothscale(source_image, (TEXTURE_SIZE, TEXTURE_SIZE))
    target.blit(scaled, (0, 0))

    center = TEXTURE_SIZE / 2
    radius = TEXTURE_SIZE / 2 - 2
    points = []
    for x, y in hex_corners(center, center, radius):
        points.append((int(x), int(y)))

    mask = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    target.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return target


def create_fallback_texture(color):
    fallback = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    points = hex_corners(TEXTURE_SIZE / 2, TEXTURE_SIZE / 2, TEXTURE_SIZE / 2 - 2)
    pygame.draw.polygon(fallback, color, points)

    pygame.draw.circle(
        fallback,
        tuple(min(255, channel + 18) for channel in color),
        (TEXTURE_SIZE // 2, TEXTURE_SIZE // 2),
        TEXTURE_SIZE // 4,
    )
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
        target_y = (TOP_UI_HEIGHT + (SCREEN_HEIGHT - BOTTOM_UI_HEIGHT)) / 2

        self.zoom = DEFAULT_ZOOM
        self.x = target_x - map_center_x * self.zoom
        self.y = target_y - map_center_y * self.zoom

    def reset(self):
        self.x = SCREEN_WIDTH / 2
        self.y = (TOP_UI_HEIGHT + (SCREEN_HEIGHT - BOTTOM_UI_HEIGHT)) / 2
        self.zoom = DEFAULT_ZOOM


class Button:
    def __init__(self, text, action, rect):
        self.text = text
        self.action = action
        self.rect = pygame.Rect(rect)

    def draw(self, screen, font, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        color = BUTTON_HOVER_COLOR if hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, self.rect, 2, border_radius=12)

        label = font.render(self.text, True, TEXT_COLOR)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


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

    def screen_points(self, camera):
        return [camera.apply(x, y) for x, y in self.base_points]

    def screen_position(self, camera):
        return camera.apply(self.x, self.y)

    def draw(self, screen, textures, camera, hovered=False, selected=False):
        texture = textures[self.terrain_key]
        screen_x, screen_y = self.screen_position(camera)
        draw_size = max(1, int(HEX_SIZE * 2 * camera.zoom))

        tile_texture = pygame.transform.smoothscale(texture, (draw_size, draw_size))
        screen.blit(tile_texture, (screen_x - draw_size / 2, screen_y - draw_size / 2))

        points = self.screen_points(camera)
        border_width = max(1, int(2 * camera.zoom))
        highlight_width = max(2, int(5 * camera.zoom))

        pygame.draw.polygon(screen, HEX_BORDER_COLOR, points, border_width)

        if hovered:
            pygame.draw.polygon(screen, HEX_HOVER_COLOR, points, highlight_width)

        if selected:
            pygame.draw.polygon(screen, HEX_SELECTED_COLOR, points, highlight_width)

    def contains_point(self, mouse_pos, camera):
        return point_in_polygon(mouse_pos, self.screen_points(camera))


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

    terrain_by_coord = {}
    for coord in land_coords:
        terrain_by_coord[coord] = None

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
        for _ in range(1):
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
    tile_id = 1

    for col, row, x, y, terrain_override in positions:
        if terrain_override:
            terrain_key = terrain_override
        else:
            terrain_key = random.choices(land_keys, weights=land_weights, k=1)[0]

        tiles.append(HexTile(tile_id, col, row, x, y, terrain_key))
        tile_id += 1

    return tiles


def map_display_name(map_key):
    for key, name in MAP_OPTIONS:
        if key == map_key:
            return name
    return "Mapa"


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
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 170))
    screen.blit(title_surface, title_rect)

    subtitle_surface = subtitle_font.render(subtitle, True, MUTED_TEXT_COLOR)
    subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH / 2, 220))
    screen.blit(subtitle_surface, subtitle_rect)


def draw_menu(screen, title_font, font, small_font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Rise & Glory", "Strategiczna gra heksowa")

    items = [
        ("Nowa gra", "new_game"),
        ("Multiplayer", "multiplayer"),
        ("Wyjscie", "exit"),
    ]
    buttons = build_vertical_buttons(items, 310)

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

    hint = small_font.render(
        "Kazdy generator ma maksymalnie 64 kafle, czyli limit 8x8.",
        True,
        MUTED_TEXT_COLOR,
    )
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


def draw_game_ui(screen, title_font, font, selected_tile, hovered_tile, camera, current_map_key, tile_count):
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, TOP_UI_HEIGHT))

    title = title_font.render(f"Rise & Glory - {map_display_name(current_map_key)}", True, TEXT_COLOR)
    screen.blit(title, (28, 18))

    subtitle = font.render(
        f"Kafle: {tile_count}/{MAX_MAP_TILES} | ESC: menu | R: generuj ponownie | F11: fullscreen | Drag kamera | Scroll zoom | SPACJA: srodek",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(subtitle, (30, 55))

    info_y = SCREEN_HEIGHT - 52
    pygame.draw.rect(screen, PANEL_COLOR, (0, SCREEN_HEIGHT - BOTTOM_UI_HEIGHT, SCREEN_WIDTH, BOTTOM_UI_HEIGHT))

    if hovered_tile:
        hover_text = font.render(
            f"Najazd: heks {hovered_tile.tile_id} | {hovered_tile.terrain['name']}",
            True,
            TEXT_COLOR,
        )
        screen.blit(hover_text, (30, info_y))
    else:
        hover_text = font.render("Mapy archipelag, fraktal i pangea sa ograniczone do maksymalnie 8x8 kafli.", True, MUTED_TEXT_COLOR)
        screen.blit(hover_text, (30, info_y))

    camera_text = font.render(
        f"Kamera x={int(camera.x)} y={int(camera.y)} zoom={camera.zoom:.2f}",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(camera_text, (760, info_y))

    if selected_tile:
        selected_text = font.render(
            f"Wybrany: heks {selected_tile.tile_id} | {selected_tile.terrain['name']}",
            True,
            TEXT_COLOR,
        )
        screen.blit(selected_text, (1040, info_y))


def create_window(fullscreen=False):
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)


def create_tiles_for_map(map_key, camera):
    tiles = generate_map(map_key)
    camera.center_on_tiles(tiles)
    return tiles


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
    title_font = pygame.font.SysFont("arial", 42, bold=True)

    textures = load_terrain_textures()
    camera = Camera()

    game_state = GAME_STATE_MENU
    current_map_key = "rosette8"
    tiles = create_tiles_for_map(current_map_key, camera)
    selected_tile = None
    running = True

    is_dragging = False
    drag_moved = False
    drag_start_pos = (0, 0)
    last_mouse_pos = (0, 0)

    active_buttons = []

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_in_window = pygame.mouse.get_focused()
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
                    tiles = create_tiles_for_map(current_map_key, camera)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == GAME_STATE_GAME:
                        game_state = GAME_STATE_MENU
                        selected_tile = None
                    elif game_state in [GAME_STATE_MAP_SELECT, GAME_STATE_MULTIPLAYER]:
                        game_state = GAME_STATE_MENU
                    else:
                        running = False

                if event.key == pygame.K_r and game_state == GAME_STATE_GAME:
                    tiles = create_tiles_for_map(current_map_key, camera)
                    selected_tile = None

                if event.key == pygame.K_SPACE and game_state == GAME_STATE_GAME:
                    camera.center_on_tiles(tiles)

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
                        tiles = create_tiles_for_map(current_map_key, camera)

            if event.type == pygame.MOUSEWHEEL and game_state == GAME_STATE_GAME:
                if mouse_in_window:
                    if event.y > 0:
                        camera.zoom_at(mouse_pos, ZOOM_STEP)
                    elif event.y < 0:
                        camera.zoom_at(mouse_pos, 1 / ZOOM_STEP)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == GAME_STATE_GAME and mouse_in_window:
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
                if game_state in [GAME_STATE_MENU, GAME_STATE_MAP_SELECT, GAME_STATE_MULTIPLAYER]:
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
                                    tiles = create_tiles_for_map(current_map_key, camera)
                                    selected_tile = None
                                    game_state = GAME_STATE_GAME

                            elif game_state == GAME_STATE_MULTIPLAYER:
                                if button.action == "back":
                                    game_state = GAME_STATE_MENU
                            break

                elif game_state == GAME_STATE_GAME:
                    is_dragging = False

                    if not drag_moved and mouse_in_window:
                        for tile in tiles:
                            if tile.contains_point(event.pos, camera):
                                selected_tile = tile
                                print(
                                    f"Wybrano heks {selected_tile.tile_id}: "
                                    f"{selected_tile.terrain['name']}"
                                )
                                break

        if not mouse_in_window:
            is_dragging = False

        if game_state == GAME_STATE_MENU:
            active_buttons = draw_menu(screen, title_font, font, small_font, mouse_pos)

        elif game_state == GAME_STATE_MAP_SELECT:
            active_buttons = draw_map_select(screen, title_font, font, small_font, mouse_pos)

        elif game_state == GAME_STATE_MULTIPLAYER:
            active_buttons = draw_multiplayer(screen, title_font, font, small_font, mouse_pos)

        elif game_state == GAME_STATE_GAME:
            active_buttons = []
            draw_background(screen)

            for tile in tiles:
                tile.draw(
                    screen,
                    textures,
                    camera,
                    hovered=(tile == hovered_tile),
                    selected=(tile == selected_tile),
                )

            draw_game_ui(screen, title_font, font, selected_tile, hovered_tile, camera, current_map_key, len(tiles))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
