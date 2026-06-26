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

MAP_COLS = 9
MAP_ROWS = 9
HEX_SIZE = 46

BACKGROUND_COLOR = (18, 22, 26)
PANEL_COLOR = (28, 33, 38)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT_COLOR = (180, 185, 190)
HEX_BORDER_COLOR = (20, 20, 20)
HEX_HOVER_COLOR = (255, 230, 120)
HEX_SELECTED_COLOR = (120, 210, 255)

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


def axial_to_pixel(col, row, size, offset_x, offset_y):
    x = size * math.sqrt(3) * (col + row / 2) + offset_x
    y = size * 1.5 * row + offset_y
    return x, y


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


def create_hex_texture(source_image, size):
    diameter = size * 2
    target = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

    scaled = pygame.transform.smoothscale(source_image, (diameter, diameter))
    target.blit(scaled, (0, 0))

    center = (size, size)
    points = []
    for x, y in hex_corners(center[0], center[1], size - 1):
        points.append((int(x), int(y)))

    mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    target.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return target


def load_terrain_textures():
    textures = {}

    for terrain_key, terrain in TERRAINS.items():
        image_path = GRAPHICS_DIR / terrain["image"]

        if image_path.exists():
            source = pygame.image.load(str(image_path)).convert_alpha()
            textures[terrain_key] = create_hex_texture(source, HEX_SIZE)
        else:
            fallback = pygame.Surface((HEX_SIZE * 2, HEX_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.polygon(
                fallback,
                terrain["fallback"],
                hex_corners(HEX_SIZE, HEX_SIZE, HEX_SIZE - 1),
            )
            textures[terrain_key] = fallback
            print(f"Brak grafiki: {image_path}. Uzywam koloru zastepczego.")

    return textures


class HexTile:
    def __init__(self, tile_id, col, row, x, y, terrain_key):
        self.tile_id = tile_id
        self.col = col
        self.row = row
        self.x = x
        self.y = y
        self.terrain_key = terrain_key
        self.terrain = TERRAINS[terrain_key]
        self.points = hex_corners(x, y, HEX_SIZE)

    def draw(self, screen, textures, font, hovered=False, selected=False):
        texture = textures[self.terrain_key]
        screen.blit(texture, (self.x - HEX_SIZE, self.y - HEX_SIZE))

        pygame.draw.polygon(screen, HEX_BORDER_COLOR, self.points, 2)

        if hovered:
            pygame.draw.polygon(screen, HEX_HOVER_COLOR, self.points, 4)

        if selected:
            pygame.draw.polygon(screen, HEX_SELECTED_COLOR, self.points, 4)

        label = font.render(str(self.tile_id), True, (245, 245, 245))
        label_rect = label.get_rect(center=(self.x, self.y))

        shadow = font.render(str(self.tile_id), True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(self.x + 1, self.y + 1))
        screen.blit(shadow, shadow_rect)
        screen.blit(label, label_rect)

    def contains_point(self, mouse_pos):
        return point_in_polygon(mouse_pos, self.points)


def generate_map():
    terrain_keys = list(TERRAINS.keys())
    terrain_weights = [TERRAINS[key]["weight"] for key in terrain_keys]

    # Wyliczenie przesuniecia tak, zeby mapa 9x9 byla mniej wiecej na srodku okna.
    map_width = HEX_SIZE * math.sqrt(3) * (MAP_COLS + MAP_ROWS / 2)
    map_height = HEX_SIZE * 1.5 * MAP_ROWS
    offset_x = (SCREEN_WIDTH - map_width) / 2 + HEX_SIZE
    offset_y = (SCREEN_HEIGHT - map_height) / 2 + HEX_SIZE - 20

    tiles = []
    tile_id = 1

    random.seed(42)

    for row in range(MAP_ROWS):
        for col in range(MAP_COLS):
            x, y = axial_to_pixel(col, row, HEX_SIZE, offset_x, offset_y)
            terrain_key = random.choices(terrain_keys, weights=terrain_weights, k=1)[0]
            tiles.append(HexTile(tile_id, col, row, x, y, terrain_key))
            tile_id += 1

    return tiles


def draw_ui(screen, title_font, font, selected_tile, hovered_tile):
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, 88))

    title = title_font.render("Rise & Glory - prototyp mapy 9x9", True, TEXT_COLOR)
    screen.blit(title, (28, 18))

    subtitle = font.render(
        "LPM: wybierz heks | R: losuj od nowa | ESC: zamknij",
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
    pygame.display.set_caption("Rise & Glory - mapa 9x9")

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

        for tile in tiles:
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

        screen.fill(BACKGROUND_COLOR)

        for tile in tiles:
            tile.draw(
                screen,
                textures,
                font,
                hovered=(tile == hovered_tile),
                selected=(tile == selected_tile),
            )

        draw_ui(screen, title_font, font, selected_tile, hovered_tile)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
