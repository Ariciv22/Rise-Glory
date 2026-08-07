import math
import random
from pathlib import Path

import pygame

from rg_core.data import (
    ACTIONS_PER_TURN,
    DEFAULT_ZOOM,
    HOVER,
    HEX_SIZE,
    LEFT_PANEL_W,
    MAP_MARGIN,
    MAX_ZOOM,
    MIN_ZOOM,
    MOVE,
    RIGHT_PANEL_W,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SELECTED,
    TEXT,
    TEXTURE_SIZE,
    TERRAINS,
    TOP_BAR_H,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
GRAPHICS_DIR = ROOT_DIR / "Grafiki"
LOCATION_MARKER_FILES = {
    "city": "pionek_miasto.png",
    "village": "pionek_wies.png",
    "castle": "pionek_zamek.png",
}
_LOCATION_MARKER_IMAGES = {}


def remove_location_marker_background(surface):
    cleaned = surface.copy().convert_alpha()
    width, height = cleaned.get_size()
    if width <= 0 or height <= 0:
        return cleaned

    visited = bytearray(width * height)
    stack = []
    border_depth = min(4, max(1, width // 2), max(1, height // 2))

    for offset in range(border_depth):
        top = offset
        bottom = height - 1 - offset
        left = offset
        right = width - 1 - offset
        for x in range(left, right + 1):
            stack.append(top * width + x)
            stack.append(bottom * width + x)
        for y in range(top + 1, bottom):
            stack.append(y * width + left)
            stack.append(y * width + right)

    while stack:
        index = stack.pop()
        if visited[index]:
            continue
        visited[index] = 1

        x = index % width
        y = index // width
        color = cleaned.get_at((x, y))
        rgb_min = min(color.r, color.g, color.b)
        rgb_max = max(color.r, color.g, color.b)
        is_light_neutral_background = rgb_min >= 195 and rgb_max - rgb_min <= 35
        if color.a > 0 and not is_light_neutral_background:
            continue

        if color.a > 0:
            cleaned.set_at((x, y), (color.r, color.g, color.b, 0))

        if x > 0:
            stack.append(index - 1)
        if x + 1 < width:
            stack.append(index + 1)
        if y > 0:
            stack.append(index - width)
        if y + 1 < height:
            stack.append(index + width)

    visible = cleaned.get_bounding_rect(min_alpha=8)
    if visible.width <= 0 or visible.height <= 0:
        return cleaned

    visible = visible.inflate(8, 8).clip(cleaned.get_rect())
    return cleaned.subsurface(visible).copy()


def load_location_marker(kind):
    if kind in _LOCATION_MARKER_IMAGES:
        return _LOCATION_MARKER_IMAGES[kind]

    filename = LOCATION_MARKER_FILES.get(kind)
    if not filename:
        _LOCATION_MARKER_IMAGES[kind] = None
        return None

    path = GRAPHICS_DIR / filename
    if not path.exists():
        _LOCATION_MARKER_IMAGES[kind] = None
        return None

    try:
        marker = pygame.image.load(str(path)).convert_alpha()
        marker = remove_location_marker_background(marker)
    except (OSError, pygame.error):
        marker = None

    _LOCATION_MARKER_IMAGES[kind] = marker
    return marker


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

    def map_view_center(self):
        map_left = LEFT_PANEL_W + MAP_MARGIN
        map_right = SCREEN_WIDTH - RIGHT_PANEL_W - MAP_MARGIN
        map_top = TOP_BAR_H + MAP_MARGIN
        map_bottom = SCREEN_HEIGHT - MAP_MARGIN
        return map_left + (map_right - map_left) / 2, map_top + (map_bottom - map_top) / 2

    def center_on_tiles(self, tiles):
        if not tiles:
            return
        min_x = min(tile.x for tile in tiles) - HEX_SIZE
        max_x = max(tile.x for tile in tiles) + HEX_SIZE
        min_y = min(tile.y for tile in tiles) - HEX_SIZE
        max_y = max(tile.y for tile in tiles) + HEX_SIZE
        self.zoom = DEFAULT_ZOOM
        cx, cy = self.map_view_center()
        self.x = cx - ((min_x + max_x) / 2) * self.zoom
        self.y = cy - ((min_y + max_y) / 2) * self.zoom

    def center_on_tile(self, tile):
        if not tile:
            return
        self.zoom = DEFAULT_ZOOM
        cx, cy = self.map_view_center()
        self.x = cx - tile.x * self.zoom
        self.y = cy - tile.y * self.zoom


class Tile:
    def __init__(self, tile_id, q, r, x, y, terrain_key):
        self.id = tile_id
        self.q = q
        self.r = r
        self.x = x
        self.y = y
        self.terrain_key = terrain_key
        self.terrain = TERRAINS[terrain_key]
        self.location = None
        self.points = hex_corners(x, y, HEX_SIZE)

    def screen_points(self, camera):
        return [camera.apply(x, y) for x, y in self.points]

    def center(self, camera):
        return camera.apply(self.x, self.y)

    def contains(self, pos, camera):
        return point_in_polygon(pos, self.screen_points(camera))

    def draw_location_marker(self, screen, camera, font):
        if not self.location:
            return

        sx, sy = self.center(camera)
        marker = load_location_marker(self.location.get("kind"))
        if marker:
            max_width = max(34, int(84 * camera.zoom))
            max_height = max(38, int(96 * camera.zoom))
            scale = min(max_width / marker.get_width(), max_height / marker.get_height())
            marker_size = (
                max(1, int(marker.get_width() * scale)),
                max(1, int(marker.get_height() * scale)),
            )
            rendered_marker = pygame.transform.smoothscale(marker, marker_size)
            marker_bottom = int(sy + 50 * camera.zoom)
            marker_rect = rendered_marker.get_rect(midbottom=(int(sx), marker_bottom))
            screen.blit(rendered_marker, marker_rect)
            return

        radius = max(13, int(19 * camera.zoom))
        marker_y = int(sy + 30 * camera.zoom)
        color = self.location["color"]
        pygame.draw.circle(screen, (15, 12, 9), (int(sx), marker_y), radius + 4)
        pygame.draw.circle(screen, color, (int(sx), marker_y), radius)
        pygame.draw.circle(screen, (30, 24, 18), (int(sx), marker_y), radius, max(2, int(3 * camera.zoom)))
        label = font.render(self.location["symbol"], True, TEXT)
        screen.blit(label, label.get_rect(center=(int(sx), marker_y)))

    def draw(self, screen, textures, camera, font, hovered=False, selected=False, valid_move=False):
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
        self.draw_location_marker(screen, camera, font)


class HeroToken:
    def __init__(self, hero, tile):
        self.hero = hero
        self.tile = tile
        self.actions = ACTIONS_PER_TURN

    @property
    def moves(self):
        return self.actions

    @moves.setter
    def moves(self, value):
        self.actions = value

    def reset_actions(self):
        self.actions = ACTIONS_PER_TURN

    def reset_moves(self):
        self.reset_actions()

    def can_move_to(self, target):
        if not target or not target.terrain["passable"]:
            return False
        if not are_adjacent(self.tile, target):
            return False
        return self.actions > 0

    def move_to(self, target):
        if not self.can_move_to(target):
            return False
        self.actions = max(0, self.actions - target.terrain["move"])
        self.tile = target
        return True

    def draw(self, screen, camera, font, selected=False):
        sx, sy = self.tile.center(camera)
        center = (int(sx), int(sy - 30 * camera.zoom))
        radius = max(11, int(18 * camera.zoom))
        player_color = self.hero.get("player_color", self.hero.get("color", (220, 220, 220)))
        pygame.draw.circle(screen, player_color, center, radius + 5)
        pygame.draw.circle(screen, (238, 238, 220), center, radius)
        pygame.draw.circle(screen, (25, 25, 25), center, radius, max(2, int(3 * camera.zoom)))
        label = font.render(str(self.hero.get("player_number", "B")), True, (20, 20, 20))
        screen.blit(label, label.get_rect(center=center))
        if selected:
            pygame.draw.circle(screen, SELECTED, center, radius + 10, max(2, int(4 * camera.zoom)))


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
    return [(q, r, *axial_to_pixel(q, r)) for q, r in coords]


def generate_positions(map_key):
    if map_key == "rosette9":
        return generate_rosette_rows([5, 6, 7, 8, 9, 8, 7, 6, 5])
    if map_key == "rosette8":
        return generate_rosette_rows([4, 5, 6, 7, 8, 7, 6, 5, 4])
    if map_key == "small":
        return generate_rosette_rows([3, 4, 5, 4, 3])
    return make_spiral(48, random.randint(1, 999999))


def generate_map(map_key):
    terrain_keys = list(TERRAINS.keys())
    weights = [TERRAINS[key]["weight"] for key in terrain_keys]
    tiles = []
    for idx, (q, r, x, y) in enumerate(generate_positions(map_key), start=1):
        terrain_key = random.choices(terrain_keys, weights=weights, k=1)[0]
        tiles.append(Tile(idx, q, r, x, y, terrain_key))
    return tiles


def find_start_tile(tiles):
    for tile in tiles:
        if tile.terrain["passable"]:
            return tile
    return tiles[0]
