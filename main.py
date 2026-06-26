import math
import random
from pathlib import Path

import pygame

# =========================
# USTAWIENIA
# =========================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 900
FPS = 60

# Pełna plansza 9x9 = 81 heksów.
MAP_COLS = 9
MAP_ROWS = 9
HEX_SIZE = 54

# Efekt kamery 3D / lekko pochylonej planszy.
# Im mniejsza wartość, tym bardziej spłaszczona perspektywa.
CAMERA_Y_SCALE = 0.72
CAMERA_SHEAR = -0.16

BACKGROUND_COLOR = (26, 78, 122)
PANEL_COLOR = (28, 33, 38)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT_COLOR = (180, 185, 190)
HEX_BORDER_COLOR = (22, 22, 22)
HEX_HOVER_COLOR = (255, 230, 120)
HEX_SELECTED_COLOR = (120, 210, 255)
WATER_COLOR = (36, 102, 158)

ROOT_DIR = Path(__file__).resolve().parent
GRAPHICS_DIR = ROOT_DIR / "Grafiki"

TERRAINS = {
    "plains": {
        "name": "Rowniny",
        "image": "rowniny.png",
        "fallback": (112, 156, 76),
        "weight": 30,
    },
    "forest": {
        "name": "Las",
        "image": "las.png",
        "fallback": (49, 107, 62),
        "weight": 24,
    },
    "hills": {
        "name": "Wzgorza",
        "image": "wzgorza.png",
        "fallback": (139, 116, 73),
        "weight": 18,
    },
    "mountain": {
        "name": "Gory",
        "image": "gory.png",
        "fallback": (116, 116, 112),
        "weight": 10,
    },
    "desert": {
        "name": "Pustynia",
        "image": "pustynia.png",
        "fallback": (194, 165, 92),
        "weight": 8,
    },
    "coast": {
        "name": "Wybrzeze",
        "image": "wybrzeze.png",
        "fallback": (70, 130, 170),
        "weight": 7,
    },
    "tundra": {
        "name": "Tundra",
        "image": "tundra.png",
        "fallback": (145, 170, 154),
        "weight": 3,
    },
}


def hex_corners(center_x, center_y, size):
    points = []

    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = math.radians(angle_deg)
        x = center_x + size * math.cos(angle_rad)
        y = center_y + size * math.sin(angle_rad)
        points.append((x, y))

    return points


def axial_to_world(col, row, size):
    x = size * math.sqrt(3) * (col + row / 2)
    y = size * 1.5 * row
    return x, y


def apply_camera(world_x, world_y, origin_x, origin_y):
    """
    Prosta kamera 2.5D:
    - spłaszcza oś Y,
    - lekko przesuwa X zależnie od Y,
    - daje efekt planszy widzianej pod kątem.
    """
    screen_x = origin_x + world_x + world_y * CAMERA_SHEAR
    screen_y = origin_y + world_y * CAMERA_Y_SCALE
    return screen_x, screen_y


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


def camera_transform_points(points, origin_x, origin_y):
    transformed = []
    for x, y in points:
        transformed.append(apply_camera(x, y, origin_x, origin_y))
    return transformed


def create_camera_hex_texture(source_image, size):
    """
    Tworzy teksturę heksa i spłaszcza ją w osi Y,
    żeby każdy kafel też pasował do pochylonej kamery.
    """
    diameter = size * 2
    flat_height = max(1, int(diameter * CAMERA_Y_SCALE))

    base = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    scaled = pygame.transform.smoothscale(source_image, (diameter, diameter))
    base.blit(scaled, (0, 0))

    mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    points = [(int(x), int(y)) for x, y in hex_corners(size, size, size - 1)]
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    base.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return pygame.transform.smoothscale(base, (diameter, flat_height))


def load_terrain_textures():
    textures = {}

    for terrain_key, terrain in TERRAINS.items():
        image_path = GRAPHICS_DIR / terrain["image"]

        if image_path.exists():
            source = pygame.image.load(str(image_path)).convert_alpha()
            textures[terrain_key] = create_camera_hex_texture(source, HEX_SIZE)
        else:
            diameter = HEX_SIZE * 2
            flat_height = max(1, int(diameter * CAMERA_Y_SCALE))
            fallback = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.polygon(
                fallback,
                terrain["fallback"],
                hex_corners(HEX_SIZE, HEX_SIZE, HEX_SIZE - 1),
            )
            textures[terrain_key] = pygame.transform.smoothscale(fallback, (diameter, flat_height))
            print(f"Brak grafiki: {image_path}. Uzywam koloru zastepczego.")

    return textures


class HexTile:
    def __init__(self, tile_id, col, row, world_x, world_y, screen_x, screen_y, terrain_key, origin_x, origin_y):
        self.tile_id = tile_id
        self.col = col
        self.row = row
        self.world_x = world_x
        self.world_y = world_y
        self.x = screen_x
        self.y = screen_y
        self.terrain_key = terrain_key
        self.terrain = TERRAINS[terrain_key]

        world_points = hex_corners(world_x, world_y, HEX_SIZE)
        self.points = camera_transform_points(world_points, origin_x, origin_y)

    def draw(self, screen, textures, hovered=False, selected=False):
        texture = textures[self.terrain_key]
        texture_rect = texture.get_rect(center=(self.x, self.y))

        # Cień pod kaflem, żeby plansza wyglądała bardziej przestrzennie.
        shadow_points = [(x + 5, y + 8) for x, y in self.points]
        pygame.draw.polygon(screen, (0, 0, 0, 80), shadow_points)

        screen.blit(texture, texture_rect)

        pygame.draw.polygon(screen, HEX_BORDER_COLOR, self.points, 2)

        if hovered:
            pygame.draw.polygon(screen, HEX_HOVER_COLOR, self.points, 4)

        if selected:
            pygame.draw.polygon(screen, HEX_SELECTED_COLOR, self.points, 4)

    def contains_point(self, mouse_pos):
        return point_in_polygon(mouse_pos, self.points)


def calculate_origin():
    world_points = []

    for row in range(MAP_ROWS):
        for col in range(MAP_COLS):
            world_x, world_y = axial_to_world(col, row, HEX_SIZE)
            world_points.extend(hex_corners(world_x, world_y, HEX_SIZE))

    projected = []
    for x, y in world_points:
        projected_x = x + y * CAMERA_SHEAR
        projected_y = y * CAMERA_Y_SCALE
        projected.append((projected_x, projected_y))

    min_x = min(x for x, y in projected)
    max_x = max(x for x, y in projected)
    min_y = min(y for x, y in projected)
    max_y = max(y for x, y in projected)

    map_width = max_x - min_x
    map_height = max_y - min_y

    origin_x = (SCREEN_WIDTH - map_width) / 2 - min_x
    origin_y = (SCREEN_HEIGHT - map_height) / 2 - min_y + 25

    return origin_x, origin_y


def generate_map():
    terrain_keys = list(TERRAINS.keys())
    terrain_weights = [TERRAINS[key]["weight"] for key in terrain_keys]

    random.seed(42)
    origin_x, origin_y = calculate_origin()

    tiles = []
    tile_id = 1

    for row in range(MAP_ROWS):
        for col in range(MAP_COLS):
            world_x, world_y = axial_to_world(col, row, HEX_SIZE)
            screen_x, screen_y = apply_camera(world_x, world_y, origin_x, origin_y)
            terrain_key = random.choices(terrain_keys, weights=terrain_weights, k=1)[0]

            tiles.append(
                HexTile(
                    tile_id=tile_id,
                    col=col,
                    row=row,
                    world_x=world_x,
                    world_y=world_y,
                    screen_x=screen_x,
                    screen_y=screen_y,
                    terrain_key=terrain_key,
                    origin_x=origin_x,
                    origin_y=origin_y,
                )
            )
            tile_id += 1

    # Rysujemy od góry mapy do dołu, żeby dolne kafle naturalnie przykrywały górne.
    tiles.sort(key=lambda tile: tile.row + tile.col * 0.01)
    return tiles


def draw_water_background(screen):
    screen.fill(WATER_COLOR)

    center_x = SCREEN_WIDTH / 2
    center_y = SCREEN_HEIGHT / 2 + 30
    island_border = hex_corners(center_x, center_y, 500)
    island_border = [(x, center_y + (y - center_y) * CAMERA_Y_SCALE) for x, y in island_border]

    pygame.draw.polygon(screen, (30, 92, 145), island_border)
    pygame.draw.polygon(screen, (17, 63, 105), island_border, 5)


def draw_ui(screen, title_font, font, selected_tile, hovered_tile):
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, 88))

    title = title_font.render("Rise & Glory - mapa 9x9 z kamera 3D", True, TEXT_COLOR)
    screen.blit(title, (28, 18))

    subtitle = font.render(
        "81 heksow | LPM: wybierz heks | R: losuj od nowa | ESC: zamknij",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(subtitle, (30, 55))

    info_y = SCREEN_HEIGHT - 52
    pygame.draw.rect(screen, PANEL_COLOR, (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 70))

    if hovered_tile:
        hover_text = font.render(
            f"Najazd: heks {hovered_tile.tile_id} | {hovered_tile.terrain['name']} | kolumna {hovered_tile.col + 1}, rzad {hovered_tile.row + 1}",
            True,
            TEXT_COLOR,
        )
        screen.blit(hover_text, (30, info_y))
    else:
        hover_text = font.render("Najedz myszka na heks, zeby zobaczyc informacje.", True, MUTED_TEXT_COLOR)
        screen.blit(hover_text, (30, info_y))

    if selected_tile:
        selected_text = font.render(
            f"Wybrany: heks {selected_tile.tile_id} | {selected_tile.terrain['name']}",
            True,
            TEXT_COLOR,
        )
        screen.blit(selected_text, (720, info_y))


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rise & Glory - mapa 9x9 3D")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=True)
    title_font = pygame.font.SysFont("arial", 28, bold=True)

    textures = load_terrain_textures()
    tiles = generate_map()

    selected_tile = None
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        hovered_tile = None

        for tile in reversed(tiles):
            if tile.contains_point(mouse_pos):
                hovered_tile = tile
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    tiles = generate_map()
                    selected_tile = None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered_tile:
                    selected_tile = hovered_tile
                    print(
                        f"Wybrano heks {selected_tile.tile_id}: "
                        f"{selected_tile.terrain['name']} "
                        f"({selected_tile.col + 1}, {selected_tile.row + 1})"
                    )

        draw_water_background(screen)

        for tile in tiles:
            tile.draw(
                screen,
                textures,
                hovered=(tile == hovered_tile),
                selected=(tile == selected_tile),
            )

        draw_ui(screen, title_font, font, selected_tile, hovered_tile)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
