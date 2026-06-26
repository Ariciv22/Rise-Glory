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

# Uklad jak w Catanie: 3 / 4 / 5 / 4 / 3, razem 19 heksow.
CATAN_ROW_LENGTHS = [3, 4, 5, 4, 3]
HEX_SIZE = 62

BACKGROUND_COLOR = (32, 76, 116)
PANEL_COLOR = (28, 33, 38)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT_COLOR = (180, 185, 190)
HEX_BORDER_COLOR = (24, 24, 24)
HEX_HOVER_COLOR = (255, 230, 120)
HEX_SELECTED_COLOR = (120, 210, 255)
WATER_COLOR = (38, 104, 158)

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
        "weight": 22,
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
        "weight": 12,
    },
    "desert": {
        "name": "Pustynia",
        "image": "pustynia.png",
        "fallback": (194, 165, 92),
        "weight": 10,
    },
    "tundra": {
        "name": "Tundra",
        "image": "tundra.png",
        "fallback": (145, 170, 154),
        "weight": 8,
    },
}

# Numery jak w Catanie, bez 7. Na start sa tylko wizualne.
CATAN_NUMBER_TOKENS = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]


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
    def __init__(self, tile_id, board_col, board_row, x, y, terrain_key, number_token=None):
        self.tile_id = tile_id
        self.board_col = board_col
        self.board_row = board_row
        self.x = x
        self.y = y
        self.terrain_key = terrain_key
        self.terrain = TERRAINS[terrain_key]
        self.number_token = number_token
        self.points = hex_corners(x, y, HEX_SIZE)

    def draw(self, screen, textures, font, token_font, hovered=False, selected=False):
        texture = textures[self.terrain_key]
        screen.blit(texture, (self.x - HEX_SIZE, self.y - HEX_SIZE))

        pygame.draw.polygon(screen, HEX_BORDER_COLOR, self.points, 2)

        if self.number_token is not None:
            self.draw_number_token(screen, token_font)

        if hovered:
            pygame.draw.polygon(screen, HEX_HOVER_COLOR, self.points, 5)

        if selected:
            pygame.draw.polygon(screen, HEX_SELECTED_COLOR, self.points, 5)

    def draw_number_token(self, screen, token_font):
        token_radius = 18
        token_color = (232, 218, 169)
        token_border = (84, 62, 34)
        text_color = (40, 29, 18)

        if self.number_token in [6, 8]:
            text_color = (170, 24, 24)

        pygame.draw.circle(screen, token_color, (int(self.x), int(self.y)), token_radius)
        pygame.draw.circle(screen, token_border, (int(self.x), int(self.y)), token_radius, 2)

        text = token_font.render(str(self.number_token), True, text_color)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

    def contains_point(self, mouse_pos):
        return point_in_polygon(mouse_pos, self.points)


def catan_positions():
    positions = []
    vertical_spacing = HEX_SIZE * 1.5
    horizontal_spacing = HEX_SIZE * math.sqrt(3)

    max_row_length = max(CATAN_ROW_LENGTHS)
    map_width = max_row_length * horizontal_spacing
    map_height = len(CATAN_ROW_LENGTHS) * vertical_spacing

    start_y = (SCREEN_HEIGHT - map_height) / 2 + HEX_SIZE + 35

    for row_index, row_length in enumerate(CATAN_ROW_LENGTHS):
        row_width = row_length * horizontal_spacing
        start_x = (SCREEN_WIDTH - row_width) / 2 + HEX_SIZE * 0.85
        y = start_y + row_index * vertical_spacing

        for col_index in range(row_length):
            x = start_x + col_index * horizontal_spacing
            positions.append((col_index, row_index, x, y))

    return positions


def generate_map():
    terrain_keys = list(TERRAINS.keys())
    terrain_weights = [TERRAINS[key]["weight"] for key in terrain_keys]

    random.seed(42)

    positions = catan_positions()
    random.shuffle(CATAN_NUMBER_TOKENS)

    tiles = []
    tile_id = 1
    number_index = 0

    # Srodek mapy robimy jako pustynie bez numeru, podobnie jak w klasycznym Catanie.
    center_index = len(positions) // 2

    for index, (col, row, x, y) in enumerate(positions):
        if index == center_index:
            terrain_key = "desert"
            number_token = None
        else:
            terrain_key = random.choices(terrain_keys, weights=terrain_weights, k=1)[0]
            if terrain_key == "desert":
                terrain_key = "plains"

            number_token = CATAN_NUMBER_TOKENS[number_index]
            number_index += 1

        tiles.append(HexTile(tile_id, col, row, x, y, terrain_key, number_token))
        tile_id += 1

    return tiles


def draw_water_background(screen):
    screen.fill(WATER_COLOR)

    # Duzy szesciokat w tle, zeby cala plansza bardziej przypominala wyspe z Catana.
    center_x = SCREEN_WIDTH / 2
    center_y = SCREEN_HEIGHT / 2 + 40
    island_border = hex_corners(center_x, center_y, 390)
    pygame.draw.polygon(screen, (30, 92, 145), island_border)
    pygame.draw.polygon(screen, (17, 63, 105), island_border, 5)


def draw_ui(screen, title_font, font, selected_tile, hovered_tile):
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, 88))

    title = title_font.render("Rise & Glory - mapa w stylu Catan", True, TEXT_COLOR)
    screen.blit(title, (28, 18))

    subtitle = font.render(
        "Uklad: 3 / 4 / 5 / 4 / 3 | LPM: wybierz heks | R: losuj od nowa | ESC: zamknij",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(subtitle, (30, 55))

    info_y = SCREEN_HEIGHT - 52
    pygame.draw.rect(screen, PANEL_COLOR, (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 70))

    if hovered_tile:
        token = hovered_tile.number_token if hovered_tile.number_token is not None else "brak"
        hover_text = font.render(
            f"Najazd: heks {hovered_tile.tile_id} | {hovered_tile.terrain['name']} | token: {token}",
            True,
            TEXT_COLOR,
        )
        screen.blit(hover_text, (30, info_y))
    else:
        hover_text = font.render("Najedz myszka na heks, zeby zobaczyc informacje.", True, MUTED_TEXT_COLOR)
        screen.blit(hover_text, (30, info_y))

    if selected_tile:
        token = selected_tile.number_token if selected_tile.number_token is not None else "brak"
        selected_text = font.render(
            f"Wybrany: heks {selected_tile.tile_id} | {selected_tile.terrain['name']} | token: {token}",
            True,
            TEXT_COLOR,
        )
        screen.blit(selected_text, (690, info_y))


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rise & Glory - mapa Catan")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=True)
    title_font = pygame.font.SysFont("arial", 28, bold=True)
    token_font = pygame.font.SysFont("arial", 20, bold=True)

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
                        f"{selected_tile.terrain['name']} | token: {selected_tile.number_token}"
                    )

        draw_water_background(screen)

        for tile in tiles:
            tile.draw(
                screen,
                textures,
                font,
                token_font,
                hovered=(tile == hovered_tile),
                selected=(tile == selected_tile),
            )

        draw_ui(screen, title_font, font, selected_tile, hovered_tile)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
