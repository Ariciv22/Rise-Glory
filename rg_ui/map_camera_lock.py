"""Sterowanie plansza heksowa wewnatrz jasnego srodka pergaminu.

Cala rozeta jest widoczna przy starcie i dopasowana do jasnego pola mapy.
Przy przyblizeniu gracz moze przeciagac plansze. Nie ukrywamy ani nie
odrzucamy heksow na krawedziach - wszystkie sa zawsze normalnie rysowane.
Zoom jest zakotwiczony w srodku aktualnego widoku, dzieki czemu plansza nie
"ucieka" w strone kursora podczas przyblizania.
"""

import math

import pygame

from rg_core.data import HEX_SIZE, MAX_ZOOM, MIN_ZOOM
from rg_ui.common import game_layout_rects
from rg_world.map import Camera, Tile


# Obszar odpowiada jasnemu, pustemu polu pergaminu wskazanemu na grafice.
SAFE_LEFT_RATIO = 0.12
SAFE_RIGHT_RATIO = 0.12
SAFE_TOP_RATIO = 0.06
SAFE_BOTTOM_RATIO = 0.08
SAFE_PIXEL_PADDING = 10

_TILE_GENERATION = 0
_TILE_BOUNDS = None


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

    # Dolny pasek informacji nalezy do HUD-u, a nie do pola planszy.
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
    """Dopasowuje cala rozete do jasnego owalnego pola przy starcie."""
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
    """Pozwala planszy jezdzic po owalu bez skokow i bez pustego odjazdu.

    Przy zoomie startowym mapa jest idealnie wycentrowana. Im mocniej gracz
    przybliza, tym wiekszy dostaje zakres przeciagania. Srodek planszy porusza
    sie po elipsie, zamiast po prostokatnym pudelku.
    """
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

    # Zakres ruchu rosnie dokladnie o nadmiar rozmiaru powstaly po zoomie.
    # Przy widoku calej mapy wynosi zero, wiec plansza pozostaje na srodku.
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

    if size_changed:
        camera._rg_playfield_size = rect.size
        reset_zoom = True

    fit_zoom = _fit_zoom(rect)
    camera._rg_fit_zoom = fit_zoom

    if reset_zoom:
        camera.zoom = fit_zoom
        _center_camera(camera)
        return

    if camera.zoom < fit_zoom:
        camera.zoom = fit_zoom
        _center_camera(camera)
    else:
        _clamp_camera(camera)


def install_locked_map_camera():
    """Instaluje dopasowanie planszy, stabilny zoom i owalny zakres dragu."""
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
        # Zmiana aktywnego bohatera nie przesuwa kamery na pionek.
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

        # Nie zoomujemy pod kursorem. To bylo powodem "uciekania" heksow:
        # kazdy scroll zmienial jednoczesnie zoom oraz x/y kamery w kierunku
        # myszy. Zachowujemy punkt swiata znajdujacy sie w srodku owalu.
        world_at_center_x = (rect.centerx - self.x) / old_zoom
        world_at_center_y = (rect.centery - self.y) / old_zoom

        self.zoom = new_zoom
        self.x = rect.centerx - world_at_center_x * new_zoom
        self.y = rect.centery - world_at_center_y * new_zoom
        _clamp_camera(self)

    Tile.__init__ = tile_init
    Camera.__init__ = camera_init
    Camera.map_view_center = map_view_center
    Camera.center_on_tile = center_on_tile
    Camera.center_on_tiles = center_on_tiles
    Camera.move = move
    Camera.zoom_at = zoom_at
    Camera._rise_glory_locked_map = True
