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

# Wiekszy kafel = czytelniejsze grafiki.
# Plansza nie musi cala miescic sie naraz, bo kamera ma drag i scroll.
HEX_SIZE = 104

# Tekstury renderujemy z duzej jakosci i dopiero potem skalujemy do widoku.
# To poprawia czytelnosc przy zoomie.
TEXTURE_SIZE = 512
SHARPEN_STRENGTH = 70

# Ruch kamery po dojechaniu kursorem do krawedzi ekranu.
CAMERA_EDGE_SIZE = 70
CAMERA_SPEED = 7
DRAG_THRESHOLD = 4

# Zoom kamery.
ZOOM_STEP = 1.10
MIN_ZOOM = 0.50
MAX_ZOOM = 1.60
DEFAULT_ZOOM = 1.0

BACKGROUND_COLOR = (18, 22, 26)
PANEL_COLOR = (28, 33, 38)
TEXT_COLOR = (235, 235, 235)
MUTED_TEXT_COLOR = (180, 185, 190)
HEX_BORDER_COLOR = (24, 24, 24)
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


def sharpen_surface(surface):
    """
    Proste wyostrzenie bez dodatkowych bibliotek.
    Laplacian podbija krawedzie i detale tekstury.
    """
    edges = pygame.transform.laplacian(surface)
    edges.set_alpha(SHARPEN_STRENGTH)

    sharpened = surface.copy()
    sharpened.blit(edges, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return sharpened


def create_hex_texture(source_image):
    target = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)

    scaled = pygame.transform.smoothscale(source_image, (TEXTURE_SIZE, TEXTURE_SIZE))
    scaled = sharpen_surface(scaled)
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
        self.y = -35
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

        # Punkt mapy pod kursorem ma zostac pod kursorem po zmianie zoomu.
        world_x = (mouse_x - self.x) / old_zoom
        world_y = (mouse_y - self.y) / old_zoom

        self.zoom = new_zoom
        self.x = mouse_x - world_x * self.zoom
        self.y = mouse_y - world_y * self.zoom

    def reset(self):
        self.x = 0
        self.y = -35
        self.zoom = DEFAULT_ZOOM

    def update(self, mouse_pos, keys, mouse_in_window, is_dragging):
        # Gdy kursor wyjdzie poza okno pygame, kamera przestaje jechac.
        # Podczas przeciagania myszka wylaczamy auto-scroll z krawedzi.
        mouse_x, mouse_y = mouse_pos

        keyboard_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        keyboard_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        keyboard_up = keys[pygame.K_UP] or keys[pygame.K_w]
        keyboard_down = keys[pygame.K_DOWN] or keys[pygame.K_s]

        mouse_left = mouse_in_window and not is_dragging and mouse_x <= CAMERA_EDGE_SIZE
        mouse_right = mouse_in_window and not is_dragging and mouse_x >= SCREEN_WIDTH - CAMERA_EDGE_SIZE
        mouse_up = mouse_in_window and not is_dragging and mouse_y <= CAMERA_EDGE_SIZE
        mouse_down = mouse_in_window and not is_dragging and mouse_y >= SCREEN_HEIGHT - CAMERA_EDGE_SIZE

        if mouse_left or keyboard_left:
            self.x += CAMERA_SPEED
        if mouse_right or keyboard_right:
            self.x -= CAMERA_SPEED
        if mouse_up or keyboard_up:
            self.y += CAMERA_SPEED
        if mouse_down or keyboard_down:
            self.y -= CAMERA_SPEED


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

        # Skalujemy z bardzo duzej tekstury bazowej 512px, a nie z malego kafla.
        # Dzieki temu szczegoly sa czytelniejsze po przyblizeniu.
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


def catan_positions():
    positions = []
    vertical_spacing = HEX_SIZE * 1.5
    horizontal_spacing = HEX_SIZE * math.sqrt(3)

    map_height = len(CATAN_ROW_LENGTHS) * vertical_spacing

    # Plansza jest duza, wiec startowo widzimy jej centrum i gora nie wchodzi pod UI.
    start_y = (SCREEN_HEIGHT - map_height) / 2 + HEX_SIZE + 80

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

    tiles = []
    tile_id = 1

    center_index = len(positions) // 2

    for index, (col, row, x, y) in enumerate(positions):
        if index == center_index:
            terrain_key = "desert"
        else:
            terrain_key = random.choices(terrain_keys, weights=terrain_weights, k=1)[0]

        tiles.append(HexTile(tile_id, col, row, x, y, terrain_key))
        tile_id += 1

    return tiles


def draw_background(screen):
    screen.fill(BACKGROUND_COLOR)


def draw_ui(screen, title_font, font, selected_tile, hovered_tile, camera):
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, 88))

    title = title_font.render("Rise & Glory - mapa", True, TEXT_COLOR)
    screen.blit(title, (28, 18))

    subtitle = font.render(
        "Duże kafle + wyostrzone tekstury | Drag / scroll zoom / WASD | SPACJA: reset",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(subtitle, (30, 55))

    info_y = SCREEN_HEIGHT - 52
    pygame.draw.rect(screen, PANEL_COLOR, (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 70))

    if hovered_tile:
        hover_text = font.render(
            f"Najazd: heks {hovered_tile.tile_id} | {hovered_tile.terrain['name']}",
            True,
            TEXT_COLOR,
        )
        screen.blit(hover_text, (30, info_y))
    else:
        hover_text = font.render("Kafle sa wieksze i wyostrzone. Przesun kamera drag albo oddal/przybliz scrollem.", True, MUTED_TEXT_COLOR)
        screen.blit(hover_text, (30, info_y))

    camera_text = font.render(
        f"Kamera x={int(camera.x)} y={int(camera.y)} zoom={camera.zoom:.2f}",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(camera_text, (500, info_y))

    if selected_tile:
        selected_text = font.render(
            f"Wybrany: heks {selected_tile.tile_id} | {selected_tile.terrain['name']}",
            True,
            TEXT_COLOR,
        )
        screen.blit(selected_text, (760, info_y))


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rise & Glory - mapa")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=True)
    title_font = pygame.font.SysFont("arial", 28, bold=True)

    textures = load_terrain_textures()
    tiles = generate_map()
    camera = Camera()

    selected_tile = None
    running = True

    is_dragging = False
    drag_moved = False
    drag_start_pos = (0, 0)
    last_mouse_pos = (0, 0)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        mouse_in_window = pygame.mouse.get_focused()
        camera.update(mouse_pos, keys, mouse_in_window, is_dragging)

        hovered_tile = None

        if mouse_in_window and not is_dragging:
            for tile in tiles:
                if tile.contains_point(mouse_pos, camera):
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
                if event.key == pygame.K_SPACE:
                    camera.reset()

            if event.type == pygame.MOUSEWHEEL:
                if mouse_in_window:
                    if event.y > 0:
                        camera.zoom_at(mouse_pos, ZOOM_STEP)
                    elif event.y < 0:
                        camera.zoom_at(mouse_pos, 1 / ZOOM_STEP)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mouse_in_window:
                    is_dragging = True
                    drag_moved = False
                    drag_start_pos = event.pos
                    last_mouse_pos = event.pos

            if event.type == pygame.MOUSEMOTION and is_dragging:
                current_pos = event.pos
                dx = current_pos[0] - last_mouse_pos[0]
                dy = current_pos[1] - last_mouse_pos[1]

                if abs(current_pos[0] - drag_start_pos[0]) > DRAG_THRESHOLD or abs(current_pos[1] - drag_start_pos[1]) > DRAG_THRESHOLD:
                    drag_moved = True

                camera.move(dx, dy)
                last_mouse_pos = current_pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
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

        draw_background(screen)

        for tile in tiles:
            tile.draw(
                screen,
                textures,
                camera,
                hovered=(tile == hovered_tile),
                selected=(tile == selected_tile),
            )

        draw_ui(screen, title_font, font, selected_tile, hovered_tile, camera)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
