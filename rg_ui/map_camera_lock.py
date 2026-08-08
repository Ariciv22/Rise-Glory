"""Blokada planszy heksowej w centrum obszaru mapy.

Plansza jest zawsze zakotwiczona w srodku dostepnego obszaru pomiedzy
panelami HUD. Uzytkownik moze ja tylko przyblizac i oddalac. Przeciagniecie
mysza nie przesuwa kamery, a zmiana aktywnego bohatera nie centruje widoku na
pionku.
"""

import pygame

from rg_core.data import HEX_SIZE, MAX_ZOOM, MIN_ZOOM
from rg_ui.common import game_layout_rects
from rg_world.map import Camera, Tile


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


def _playfield_rect():
    screen = pygame.display.get_surface()
    if screen is None:
        return None

    layout = game_layout_rects(screen)
    rect = layout["center"].copy()

    # Dolny pasek informacji nalezy do HUD, dlatego plansze centrujemy w
    # rzeczywiscie widocznym fragmencie mapy nad nim.
    bottom = layout.get("bottom")
    if bottom is not None and bottom.height > 0:
        rect.height = max(1, rect.height - bottom.height)

    return rect


def _world_center():
    if _TILE_BOUNDS is None:
        return 0.0, 0.0
    min_x, max_x, min_y, max_y = _TILE_BOUNDS
    return (min_x + max_x) / 2.0, (min_y + max_y) / 2.0


def _fit_zoom(rect):
    if rect is None or _TILE_BOUNDS is None:
        return MIN_ZOOM

    min_x, max_x, min_y, max_y = _TILE_BOUNDS
    world_w = max(1.0, (max_x - min_x) + HEX_SIZE * 2.0)
    world_h = max(1.0, (max_y - min_y) + HEX_SIZE * 2.0)

    padding = 22
    available_w = max(1, rect.width - padding * 2)
    available_h = max(1, rect.height - padding * 2)
    fitted = min(available_w / world_w, available_h / world_h)
    return max(MIN_ZOOM, min(MAX_ZOOM, fitted))


def _anchor_camera(camera, reset_zoom=False):
    rect = _playfield_rect()
    if rect is None:
        return

    generation_changed = getattr(camera, "_rg_map_generation", -1) != _TILE_GENERATION
    if generation_changed:
        camera._rg_map_generation = _TILE_GENERATION
        camera._rg_world_center = _world_center()
        reset_zoom = True

    if not hasattr(camera, "_rg_world_center"):
        camera._rg_world_center = _world_center()

    if reset_zoom:
        camera.zoom = _fit_zoom(rect)

    world_x, world_y = camera._rg_world_center
    camera.x = rect.centerx - world_x * camera.zoom
    camera.y = rect.centery - world_y * camera.zoom


def install_locked_map_camera():
    """Zakotwicza mape heksowa i pozostawia tylko sterowanie zoomem."""
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
        self._rg_world_center = (0.0, 0.0)

    def map_view_center(self):
        rect = _playfield_rect()
        if rect is None:
            return self.x, self.y
        return rect.centerx, rect.centery

    def center_on_tile(self, tile):
        # Zmiana aktywnego bohatera nie przesuwa planszy. Przy pierwszym
        # wejsciu do nowej mapy dobieramy jedynie zoom tak, aby cala rozeta
        # byla czytelnie widoczna.
        _anchor_camera(self)

    def center_on_tiles(self, tiles):
        _anchor_camera(self, reset_zoom=True)

    def move(self, dx, dy):
        # Celowo ignorujemy panowanie/przeciaganie mapy.
        _anchor_camera(self)

    def zoom_at(self, mouse_pos, factor):
        # Zoom odbywa sie wzgledem stalego srodka planszy, a nie kursora.
        _anchor_camera(self)
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom * factor))
        if new_zoom == self.zoom:
            return
        self.zoom = new_zoom
        _anchor_camera(self)

    Tile.__init__ = tile_init
    Camera.__init__ = camera_init
    Camera.map_view_center = map_view_center
    Camera.center_on_tile = center_on_tile
    Camera.center_on_tiles = center_on_tiles
    Camera.move = move
    Camera.zoom_at = zoom_at
    Camera._rise_glory_locked_map = True
