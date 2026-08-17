"""Sterowanie plansza heksowa wewnatrz jasnego srodka pergaminu.

Cala rozeta jest dostepna w obszarze mapy, ale startujemy wyraznie blizej,
zeby heksy byly czytelne i wypelnialy wieksza czesc pergaminu. Przy
przyblizeniu gracz moze przeciagac plansze. Zoom jest zakotwiczony w srodku
aktualnego widoku, dzieki czemu plansza nie "ucieka" w strone kursora.
"""

import math

import pygame

from rg_core.data import HEX_SIZE, HOVER, MAX_ZOOM, MIN_ZOOM, MOVE, SELECTED, TEXT
from rg_ui.common import game_layout_rects
from rg_world.map import Camera, Tile, load_location_marker


# Obszar odpowiada jasnemu, pustemu polu pergaminu wskazanemu na grafice.
SAFE_LEFT_RATIO = 0.12
SAFE_RIGHT_RATIO = 0.12
SAFE_TOP_RATIO = 0.06
SAFE_BOTTOM_RATIO = 0.08
SAFE_PIXEL_PADDING = 10

# Startujemy jeszcze blizej, ale pelny widok mapy nadal jest dostepny po
# oddaleniu. Maksymalny zoom jest ograniczony natywna rozdzielczoscia grafik,
# a nie filtrem wyostrzajacym.
START_ZOOM_SCALE = 3.60

# Aktualne znaczniki lokacji byly ustawione na 116x132. Zmniejszamy je o 5%.
LOCATION_MARKER_SCALE = 0.95

# Dolny pas heksa zawiera nazwe terenu. Ta wartosc wyznacza niewidzialna
# pozioma linie nad napisem. Dolna krawedz znacznika lokacji nigdy nie moze
# zejsc ponizej tej linii, niezaleznie od zoomu i rozmiaru grafiki.
LOCATION_LABEL_GUARD_RATIO = 0.32
LOCATION_LABEL_GUARD_GAP = 5

# Znaczniki lokacji sa lekko przesuniete w prawo, ale ich prawa krawedz nie
# moze przekroczyc bezpiecznej linii wewnatrz heksa.
LOCATION_MARKER_OFFSET_X_RATIO = 0.18
LOCATION_MARKER_RIGHT_GUARD_RATIO = 0.68

_TILE_GENERATION = 0
_TILE_BOUNDS = None

# Kazdy typ terenu wystepuje wiele razy. Bez cache pygame wykonywaloby
# smoothscale tej samej duzej tekstury osobno dla kazdego heksa w kazdej
# klatce. Trzymamy tylko ostatni rozmiar dla kazdego typu terenu.
_TERRAIN_SCALE_CACHE = {}


def _register_tile(tile_id, x, y):
    global _TILE_GENERATION, _TILE_BOUNDS

    if int(tile_id) == 1 or _TILE_BOUNDS is None:
        _TILE_GENERATION += 1
        _TILE_BOUNDS = [float(x), float(x), float(y), float(y)]
        return

    _TILE_BOUNDS[0] = min(_TILE_BOUNDS[0], float(x))
    _TILE_BOUNDS[1] = max(_TILE_BOUNDS[1], float(x))
    _TILE_BOUNDS[2] = min(_TILE_BOUNDS[2], float(y))
    _TILE_BOUNDS[3] = max(_TILE_BOUNDS[3], float(y))


def _center_map_rect():
    screen = pygame.display.get_surface()
    if screen is None:
        return None

    layout = game_layout_rects(screen)
    rect = layout["center"].copy()

    bottom = layout.get("bottom")
    if bottom is not None and bottom.height > 0:
        rect.height = max(1, rect.height - bottom.height)

    return rect


def playfield_rect():
    """Prostokat opisujacy jasny owal pergaminu."""
    rect = _center_map_rect()
    if rect is None:
        return None

    left = int(rect.width * SAFE_LEFT_RATIO)
    right = int(rect.width * SAFE_RIGHT_RATIO)
    top = int(rect.height * SAFE_TOP_RATIO)
    bottom = int(rect.height * SAFE_BOTTOM_RATIO)

    return pygame.Rect(
        rect.x + left,
        rect.y + top,
        max(1, rect.width - left - right),
        max(1, rect.height - top - bottom),
    )


def _expanded_world_bounds():
    if _TILE_BOUNDS is None:
        return None

    min_x, max_x, min_y, max_y = _TILE_BOUNDS
    return (
        min_x - HEX_SIZE,
        max_x + HEX_SIZE,
        min_y - HEX_SIZE,
        max_y + HEX_SIZE,
    )


def _world_center():
    bounds = _expanded_world_bounds()
    if bounds is None:
        return 0.0, 0.0
    min_x, max_x, min_y, max_y = bounds
    return (min_x + max_x) / 2.0, (min_y + max_y) / 2.0


def _world_size():
    bounds = _expanded_world_bounds()
    if bounds is None:
        return 1.0, 1.0
    min_x, max_x, min_y, max_y = bounds
    return max(1.0, max_x - min_x), max(1.0, max_y - min_y)


def _fit_zoom(rect):
    """Wylicza zoom, przy ktorym cala rozeta miesci sie w polu mapy."""
    if rect is None or _TILE_BOUNDS is None:
        return MIN_ZOOM

    world_w, world_h = _world_size()

    ellipse_rx = max(1.0, rect.width / 2.0 - SAFE_PIXEL_PADDING)
    ellipse_ry = max(1.0, rect.height / 2.0 - SAFE_PIXEL_PADDING)
    x_term = world_w / (2.0 * ellipse_rx)
    y_term = world_h / (2.0 * ellipse_ry)
    denominator = math.sqrt(x_term * x_term + y_term * y_term)
    fitted = 1.0 / max(0.0001, denominator)

    return max(MIN_ZOOM, min(MAX_ZOOM, fitted))


def _center_camera(camera):
    rect = playfield_rect()
    if rect is None:
        return

    world_x, world_y = _world_center()
    camera.x = rect.centerx - world_x * camera.zoom
    camera.y = rect.centery - world_y * camera.zoom


def _clamp_camera(camera):
    """Pozwala planszy jezdzic po owalu bez skokow i bez pustego odjazdu."""
    rect = playfield_rect()
    if rect is None or _TILE_BOUNDS is None:
        return

    fit_zoom = getattr(camera, "_rg_fit_zoom", _fit_zoom(rect))
    world_w, world_h = _world_size()
    world_cx, world_cy = _world_center()

    map_center_x = camera.x + world_cx * camera.zoom
    map_center_y = camera.y + world_cy * camera.zoom
    dx = map_center_x - rect.centerx
    dy = map_center_y - rect.centery

    max_dx = max(0.0, world_w * (camera.zoom - fit_zoom) / 2.0)
    max_dy = max(0.0, world_h * (camera.zoom - fit_zoom) / 2.0)

    if max_dx <= 0.5:
        dx = 0.0
    if max_dy <= 0.5:
        dy = 0.0

    if max_dx > 0.5 and max_dy > 0.5:
        ellipse_value = (dx / max_dx) ** 2 + (dy / max_dy) ** 2
        if ellipse_value > 1.0:
            scale = 1.0 / math.sqrt(ellipse_value)
            dx *= scale
            dy *= scale
    elif max_dx > 0.5:
        dx = max(-max_dx, min(max_dx, dx))
        dy = 0.0
    elif max_dy > 0.5:
        dx = 0.0
        dy = max(-max_dy, min(max_dy, dy))

    camera.x = rect.centerx + dx - world_cx * camera.zoom
    camera.y = rect.centery + dy - world_cy * camera.zoom


def _sync_generation(camera, reset_zoom=False):
    rect = playfield_rect()
    if rect is None:
        return

    generation_changed = getattr(camera, "_rg_map_generation", -1) != _TILE_GENERATION
    size_changed = getattr(camera, "_rg_playfield_size", None) != rect.size

    if generation_changed:
        camera._rg_map_generation = _TILE_GENERATION
        reset_zoom = True
        _TERRAIN_SCALE_CACHE.clear()

    if size_changed:
        camera._rg_playfield_size = rect.size
        reset_zoom = True
        _TERRAIN_SCALE_CACHE.clear()

    fit_zoom = _fit_zoom(rect)
    camera._rg_fit_zoom = fit_zoom

    if reset_zoom:
        camera.zoom = min(MAX_ZOOM, fit_zoom * START_ZOOM_SCALE)
        _center_camera(camera)
        _clamp_camera(camera)
        return

    if camera.zoom < fit_zoom:
        camera.zoom = fit_zoom
        _center_camera(camera)
    else:
        _clamp_camera(camera)


def _location_label_guard_y(sy, camera):
    """Niewidzialna linia, pod ktora nie moze zejsc zeton lokacji."""
    hex_radius = HEX_SIZE * camera.zoom
    return int(sy + hex_radius * LOCATION_LABEL_GUARD_RATIO)


def _draw_location_marker_scaled(self, screen, camera, font):
    if not self.location:
        return

    sx, sy = self.center(camera)
    hex_radius = HEX_SIZE * camera.zoom
    guard_y = _location_label_guard_y(sy, camera)
    guard_gap = max(3, int(LOCATION_LABEL_GUARD_GAP * camera.zoom))
    marker_bottom_limit = guard_y - guard_gap

    marker = load_location_marker(self.location.get("kind"))
    if marker:
        max_width = max(46, int(116 * LOCATION_MARKER_SCALE * camera.zoom))
        max_height = max(51, int(132 * LOCATION_MARKER_SCALE * camera.zoom))
        scale = min(max_width / marker.get_width(), max_height / marker.get_height())
        marker_size = (
            max(1, int(marker.get_width() * scale)),
            max(1, int(marker.get_height() * scale)),
        )
        rendered_marker = pygame.transform.smoothscale(marker, marker_size)

        desired_bottom = int(sy + 60 * camera.zoom)
        marker_bottom = min(desired_bottom, marker_bottom_limit)
        desired_center_x = int(sx + hex_radius * LOCATION_MARKER_OFFSET_X_RATIO)
        marker_rect = rendered_marker.get_rect(midbottom=(desired_center_x, marker_bottom))

        right_guard = int(sx + hex_radius * LOCATION_MARKER_RIGHT_GUARD_RATIO)
        if marker_rect.right > right_guard:
            marker_rect.right = right_guard

        screen.blit(rendered_marker, marker_rect)
        return

    radius = max(16, int(25 * LOCATION_MARKER_SCALE * camera.zoom))
    desired_marker_y = int(sy + 36 * camera.zoom)
    max_marker_y = marker_bottom_limit - radius
    marker_y = min(desired_marker_y, max_marker_y)
    desired_marker_x = int(sx + hex_radius * LOCATION_MARKER_OFFSET_X_RATIO)
    right_guard = int(sx + hex_radius * LOCATION_MARKER_RIGHT_GUARD_RATIO)
    marker_x = min(desired_marker_x, right_guard - radius - 5)
    color = self.location["color"]
    pygame.draw.circle(screen, (15, 12, 9), (marker_x, marker_y), radius + 5)
    pygame.draw.circle(screen, color, (marker_x, marker_y), radius)
    pygame.draw.circle(screen, (30, 24, 18), (marker_x, marker_y), radius, max(2, int(3 * camera.zoom)))
    label = font.render(self.location["symbol"], True, TEXT)
    screen.blit(label, label.get_rect(center=(marker_x, marker_y)))


def _scaled_terrain_texture(textures, terrain_key, size):
    cached = _TERRAIN_SCALE_CACHE.get(terrain_key)
    if cached is not None and cached[0] == size:
        return cached[1]

    source = textures[terrain_key]
    if source.get_width() == size and source.get_height() == size:
        scaled = source
    else:
        scaled = pygame.transform.smoothscale(source, (size, size))
    _TERRAIN_SCALE_CACHE[terrain_key] = (size, scaled)
    return scaled


def _draw_tile_high_res(self, screen, textures, camera, font, hovered=False, selected=False, valid_move=False):
    sx, sy = self.center(camera)
    size = max(1, int(HEX_SIZE * 2 * camera.zoom))
    texture = _scaled_terrain_texture(textures, self.terrain_key, size)
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


def install_locked_map_camera():
    """Instaluje dopasowanie planszy, stabilny zoom i tuning znacznikow."""
    if getattr(Camera, "_rise_glory_locked_map", False):
        return

    original_tile_init = Tile.__init__
    original_camera_init = Camera.__init__

    def tile_init(self, tile_id, q, r, x, y, terrain_key):
        original_tile_init(self, tile_id, q, r, x, y, terrain_key)
        _register_tile(tile_id, x, y)

    def camera_init(self, *args, **kwargs):
        original_camera_init(self, *args, **kwargs)
        self._rg_map_generation = -1
        self._rg_playfield_size = None
        self._rg_fit_zoom = MIN_ZOOM

    def map_view_center(self):
        rect = playfield_rect()
        if rect is None:
            return self.x, self.y
        return rect.centerx, rect.centery

    def center_on_tile(self, tile):
        _sync_generation(self)

    def center_on_tiles(self, tiles):
        _sync_generation(self, reset_zoom=True)

    def move(self, dx, dy):
        _sync_generation(self)
        self.x += dx
        self.y += dy
        _clamp_camera(self)

    def zoom_at(self, mouse_pos, factor):
        _sync_generation(self)
        rect = playfield_rect()
        if rect is None:
            return

        old_zoom = self.zoom
        fit_zoom = getattr(self, "_rg_fit_zoom", _fit_zoom(rect))
        new_zoom = max(fit_zoom, min(MAX_ZOOM, old_zoom * factor))
        if new_zoom == old_zoom:
            return

        world_at_center_x = (rect.centerx - self.x) / old_zoom
        world_at_center_y = (rect.centery - self.y) / old_zoom

        self.zoom = new_zoom
        self.x = rect.centerx - world_at_center_x * new_zoom
        self.y = rect.centery - world_at_center_y * new_zoom
        _clamp_camera(self)
        _TERRAIN_SCALE_CACHE.clear()

    Tile.__init__ = tile_init
    Tile.draw_location_marker = _draw_location_marker_scaled
    Tile.draw = _draw_tile_high_res
    Camera.__init__ = camera_init
    Camera.map_view_center = map_view_center
    Camera.center_on_tile = center_on_tile
    Camera.center_on_tiles = center_on_tiles
    Camera.move = move
    Camera.zoom_at = zoom_at
    Camera._rise_glory_locked_map = True
