import math
import random
from pathlib import Path

import pygame

from game_ui import (
    BOTTOM_CITY_HEIGHT,
    Button,
    GameUIState,
    PLAYER_TOPBAR_HEIGHT,
    TEXT_COLOR,
    MUTED_TEXT_COLOR,
    draw_background,
    draw_player_ui,
    is_over_ui,
    load_ui_panel_graphics,
)

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

HEX_BORDER_COLOR = (24, 24, 24)
HEX_HOVER_COLOR = (255, 230, 120)
HEX_SELECTED_COLOR = (120, 210, 255)
CITY_COLOR = (245, 230, 170)
CITY_BORDER_COLOR = (42, 32, 18)
UNIT_FILL_COLOR = (238, 238, 220)
VALID_MOVE_COLOR = (120, 210, 255)
BACKGROUND_COLOR = (18, 22, 26)

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
        self.zoom = DEFAULT_ZOOM
        self.x = SCREEN_WIDTH / 2 - ((min_x + max_x) / 2) * self.zoom
        self.y = PLAYER_TOPBAR_HEIGHT + (SCREEN_HEIGHT - PLAYER_TOPBAR_HEIGHT - BOTTOM_CITY_HEIGHT) / 2 - ((min_y + max_y) / 2) * self.zoom

    def reset(self):
        self.x = SCREEN_WIDTH / 2
        self.y = PLAYER_TOPBAR_HEIGHT + (SCREEN_HEIGHT - PLAYER_TOPBAR_HEIGHT - BOTTOM_CITY_HEIGHT) / 2
        self.zoom = DEFAULT_ZOOM


class Unit:
    def __init__(self, unit_id, unit_type, player, tile):
        self.unit_id = unit_id
        self.unit_type = unit_type
        self.player = player
        self.tile = tile
        self.moves_left = UNIT_MOVES_PER_TURN

    @property
    def name(self):
        return "Osadnik" if self.unit_type == "settler" else self.unit_type

    def reset_moves(self):
        self.moves_left = UNIT_MOVES_PER_TURN

    def can_move_to(self, target_tile, units):
        if self.moves_left <= 0 or not target_tile or not target_tile.terrain.get("passable"):
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
        center = (int(screen_x), int(screen_y - 30 * camera.zoom))
        pygame.draw.circle(screen, self.player["color"], center, radius + 5)
        pygame.draw.circle(screen, UNIT_FILL_COLOR, center, radius)
        pygame.draw.circle(screen, (25, 25, 25), center, radius, max(2, int(3 * camera.zoom)))
        label = font.render("O", True, (20, 20, 20))
        screen.blit(label, label.get_rect(center=center))
        if selected:
            pygame.draw.circle(screen, HEX_SELECTED_COLOR, center, radius + 10, max(2, int(4 * camera.zoom)))


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

    def draw_city(self, screen, camera):
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

    def draw(self, screen, textures, camera, font, hovered=False, selected=False, placement_mode=False, valid_unit_move=False):
        texture = textures[self.terrain_key]
        screen_x, screen_y = self.screen_position(camera)
        draw_size = max(1, int(HEX_SIZE * 2 * camera.zoom))
        tile_texture = pygame.transform.smoothscale(texture, (draw_size, draw_size))
        screen.blit(tile_texture, (screen_x - draw_size / 2, screen_y - draw_size / 2))
        points = self.screen_points(camera)
        pygame.draw.polygon(screen, HEX_BORDER_COLOR, points, max(1, int(2 * camera.zoom)))
        if valid_unit_move:
            pygame.draw.polygon(screen, VALID_MOVE_COLOR, points, max(2, int(4 * camera.zoom)))
        if hovered:
            pygame.draw.polygon(screen, HEX_HOVER_COLOR, points, max(2, int(5 * camera.zoom)))
        if selected:
            pygame.draw.polygon(screen, HEX_SELECTED_COLOR, points, max(2, int(5 * camera.zoom)))
        if placement_mode and self.can_place_city():
            pygame.draw.polygon(screen, (120, 255, 150), points, max(1, int(3 * camera.zoom)))
        self.draw_city(screen, camera)

    def contains_point(self, mouse_pos, camera):
        return point_in_polygon(mouse_pos, self.screen_points(camera))


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
    return axial_set_to_positions(add_water_around_land(set(make_spiral_path(-3, -2, 12, 22) + make_spiral_path(3, 2, 12, 23))))


def generate_fractal_positions():
    return axial_set_to_positions(add_water_around_land(set(make_spiral_path(0, 0, 42, 33))))


def generate_pangea_positions():
    return axial_set_to_positions(add_water_around_land(set(make_spiral_path(0, 0, 48, 44))))


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
    positions = generate_map_positions(map_key)[:MAX_MAP_TILES]
    tiles = []
    for tile_id, (col, row, x, y, terrain_override) in enumerate(positions, start=1):
        terrain_key = terrain_override or random.choices(land_keys, weights=land_weights, k=1)[0]
        tiles.append(HexTile(tile_id, col, row, x, y, terrain_key))
    return tiles


def find_start_tile(tiles):
    for tile in tiles:
        if tile.terrain.get("passable") and tile.terrain.get("land"):
            return tile
    return tiles[0] if tiles else None


def map_display_name(map_key):
    for key, name in MAP_OPTIONS:
        if key == map_key:
            return name
    return "Mapa"


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


def draw_menu(screen, title_font, font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Rise & Glory", "Strategiczna gra heksowa")
    buttons = build_vertical_buttons([("Nowa gra", "new_game"), ("Multiplayer", "multiplayer"), ("Wyjscie", "exit")], 310)
    for button in buttons:
        button.draw(screen, font, mouse_pos)
    return buttons


def draw_map_select(screen, title_font, font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Nowa gra", "Wybierz typ mapy")
    items = [(name, key) for key, name in MAP_OPTIONS]
    items.append(("Powrot", "back"))
    buttons = build_vertical_buttons(items, 290, button_width=420, button_height=58, gap=14)
    for button in buttons:
        button.draw(screen, font, mouse_pos)
    return buttons


def draw_player_select(screen, title_font, font, mouse_pos):
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
    return buttons


def draw_multiplayer(screen, title_font, font, mouse_pos):
    draw_background(screen)
    draw_title(screen, title_font, font, "Multiplayer", "Tryb do dodania pozniej")
    buttons = build_vertical_buttons([("Powrot", "back")], 390)
    for button in buttons:
        button.draw(screen, font, mouse_pos)
    return buttons


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
    return [Unit(1, "settler", player, start_tile)] if start_tile else []


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


def handle_ui_action(action, ui_state, units, current_player, current_player_index):
    placement_mode = None
    selected_unit = None
    next_player_index = current_player_index
    if action.startswith("toggle_"):
        ui_state.toggle(action.replace("toggle_", ""))
    elif action.startswith("select_player:"):
        player_id = int(action.split(":", 1)[1])
        ui_state.select_player(player_id)
        ui_state.add_log(f"Podglad statystyk: Gracz {player_id}.")
    elif action == "place_city":
        placement_mode = True
        selected_unit = None
        ui_state.add_log("Wybierz heks pod miasto.")
    elif action == "next_player":
        next_player_index = (current_player_index + 1) % len(PLAYERS)
        selected_unit = None
        placement_mode = False
        reset_player_units(units, PLAYERS[next_player_index])
        ui_state.add_log(f"Tura: {PLAYERS[next_player_index]['name']}.")
    elif action == "reset_moves":
        reset_player_units(units, current_player)
        ui_state.add_log(f"Odnowiono ruchy: {current_player['name']}.")
    elif action == "cancel_action":
        placement_mode = False
        selected_unit = None
        ui_state.add_log("Anulowano akcje.")
    return placement_mode, selected_unit, next_player_index


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
                                    ui_state.selected_player_id = current_player["id"]
                                    ui_state.add_log(f"Nowa gra: {map_display_name(current_map_key)}.")
                                    game_state = GAME_STATE_GAME
                            elif game_state == GAME_STATE_MULTIPLAYER and button.action == "back":
                                game_state = GAME_STATE_MENU
                            break
                elif game_state == GAME_STATE_GAME:
                    is_dragging = False
                    clicked_ui_button = False
                    for button in game_ui_buttons:
                        if button.is_clicked(event.pos):
                            clicked_ui_button = True
                            new_placement, new_selected_unit, next_player_index = handle_ui_action(button.action, ui_state, units, current_player, current_player_index)
                            if new_placement is not None:
                                placement_mode = new_placement
                            if new_selected_unit is not None or button.action in ["place_city", "next_player", "cancel_action"]:
                                selected_unit = new_selected_unit
                            current_player_index = next_player_index
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
            active_buttons = draw_menu(screen, title_font, font, mouse_pos)
            game_ui_buttons = []
            ui_blocking_rects = []
        elif game_state == GAME_STATE_MAP_SELECT:
            active_buttons = draw_map_select(screen, title_font, font, mouse_pos)
            game_ui_buttons = []
            ui_blocking_rects = []
        elif game_state == GAME_STATE_PLAYER_SELECT:
            active_buttons = draw_player_select(screen, title_font, font, mouse_pos)
            game_ui_buttons = []
            ui_blocking_rects = []
        elif game_state == GAME_STATE_MULTIPLAYER:
            active_buttons = draw_multiplayer(screen, title_font, font, mouse_pos)
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
            current_player = PLAYERS[current_player_index]
            game_ui_buttons, ui_blocking_rects = draw_player_ui(
                screen, title_font, font, small_font, mouse_pos, ui_state, hovered_tile, camera,
                current_map_key, len(tiles), current_player, placement_mode, selected_tile, selected_unit,
                cities, units, ui_graphics, PLAYERS, MAP_OPTIONS, MAX_MAP_TILES,
            )
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
