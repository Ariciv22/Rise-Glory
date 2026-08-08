"""Sterowanie plansza heksowa wewnatrz centralnego pergaminu.

Domyslnie cala rozeta jest dopasowana do jasnego srodka grafiki
``tlo_heksow``. Gracz moze przyblizac, oddalac i przeciagac plansze, ale widok
jest ograniczony do obszaru pergaminu: heksy nie sa rysowane na ozdobnych
brzegach, a kamera nie pozwala odsunac planszy tak daleko, aby pokazac pusta
przestrzen zamiast mapy.
"""

import pygame

from rg_core.data import HEX_SIZE, MAX_ZOOM, MIN_ZOOM
from rg_ui.common import game_layout_rects
from rg_world.map import Camera, HeroToken, Tile


# Proporcje odpowiadaja jasnemu, pustemu polu pergaminu w tlo_heksow.png.
# Sa liczone wewnatrz centralnego prostokata mapy, juz po odjeciu HUD-u.
SAFE_LEFT_RATIO = 0.15
SAFE_RIGHT_RATIO = 0.15
SAFE_TOP_RATIO = 0.08
SAFE_BOTTOM_RATIO = 0.10
SAFE_PIXEL_PADDING = 8

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

    # Dolny pasek informacji jest elementem HUD-u i nie nalezy do obszaru
    # sterowania plansza.
    bottom = layout.get("bottom")
    if bottom is not None and bottom.height > 0:
        rect.height = max(1, rect.height - bottom.height)

    return rect


def playfield_rect():
    """Jasny srodek pergaminu, w ktorym wolno wyswietlac heksy."""
    rect = _center_map_rect()
    if rect is None:
        return None

    left = int(rect.width * SAFE_LEFT_RATIO)
    right = int(rect.width * SAFE_RIGHT_RATIO)
    top = int(rect.height * SAFE_TOP_RATIO)
    bottom = int(rect.height * SAFE_BOTTOM_RATIO)

    safe = pygame.Rect(
        rect.x + left,
        rect.y + top,
        max(1, rect.width - left - right),
        max(1, rect.height - top - bottom),
    )
    return safe


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


def _fit_zoom(rect):
    bounds = _expanded_world_bounds()
    if rect is None or bounds is None:
        return MIN_ZOOM

    min_x, max_x, min_y, max_y = bounds
    world_w = max(1.0, max_x - min_x)
    world_h = max(1.0, max_y - min_y)
    available_w = max(1, rect.width - SAFE_PIXEL_PADDING * 2)
    available_h = max(1, rect.height - SAFE_PIXEL_PADDING * 2)

    fitted = min(available_w / world_w, available_h / world_h)
    return max(MIN_ZOOM, min(MAX_ZOOM, fitted))


def _center_camera(camera):
    rect = playfield_rect()
    if rect is None:
        return
    world_x, world_y = _world_center()
    camera.x = rect.centerx - world_x * camera.zoom
    camera.y = rect.centery - world_y * camera.zoom


def _clamp_camera(camera):
    """Ogranicza panowanie tak, aby mapa zawsze pokrywala viewport."""
    rect = playfield_rect()
    bounds = _expanded_world_bounds()
    if rect is None or bounds is None:
        return

    min_x, max_x, min_y, max_y = bounds
    scaled_w = (max_x - min_x) * camera.zoom
    scaled_h = (max_y - min_y) * camera.zoom

    if scaled_w <= rect.width:
        world_cx = (min_x + max_x) / 2.0
        camera.x = rect.centerx - world_cx * camera.zoom
    else:
        min_offset_x = rect.right - max_x * camera.zoom
        max_offset_x = rect.left - min_x * camera.zoom
        camera.x = max(min_offset_x, min(max_offset_x, camera.x))

    if scaled_h <= rect.height:
        world_cy = (min_y + max_y) / 2.0
        camera.y = rect.centery - world_cy * camera.zoom
    else:
        min_offset_y = rect.bottom - max_y * camera.zoom
        max_offset_y = rect.top - min_y * camera.zoom
        camera.y = max(min_offset_y, min(max_offset_y, camera.y))


def _sync_generation(camera, reset_zoom=False):
    rect = playfield_rect()
    if rect is None:
        return

    generation_changed = getattr(camera, "_rg_map_generation", -1) != _TILE_GENERATION
    if generation_changed:
        camera._rg_map_generation = _TILE_GENERATION
        reset_zoom = True

    if reset_zoom:
        camera.zoom = _fit_zoom(rect)
        _center_camera(camera)
    else:
        _clamp_camera(camera)


def _with_playfield_clip(screen, draw_call):
    rect = playfield_rect()
    if rect is None:
        return draw_call()

    previous = screen.get_clip()
    screen.set_clip(rect)
    try:
        return draw_call()
    finally:
        screen.set_clip(previous)


def install_locked_map_camera():
    """Instaluje dopasowanie, zoom, drag, ograniczenia i clipping planszy."""
    if getattr(Camera, "_rise_glory_locked_map", False):
        return

    original_tile_init = Tile.__init__
    original_tile_draw = Tile.draw
    original_tile_contains = Tile.contains
    original_token_draw = HeroToken.draw
    original_camera_init = Camera.__init__

    def tile_init(self, tile_id, q, r, x, y, terrain_key):
        original_tile_init(self, tile_id, q, r, x, y, terrain_key)
        _register_tile(tile_id, x, y)

    def tile_draw(self, screen, textures, camera, font, *args, **kwargs):
        return _with_playfield_clip(
            screen,
            lambda: original_tile_draw(self, screen, textures, camera, font, *args, **kwargs),
        )

    def tile_contains(self, pos, camera):
        rect = playfield_rect()
        if rect is not None and not rect.collidepoint(pos):
            return False
        return original_tile_contains(self, pos, camera)

    def token_draw(self, screen, camera, font, *args, **kwargs):
        return _with_playfield_clip(
            screen,
            lambda: original_token_draw(self, screen, camera, font, *args, **kwargs),
        )

    def camera_init(self, *args, **kwargs):
        original_camera_init(self, *args, **kwargs)
        self._rg_map_generation = -1

    def map_view_center(self):
        rect = playfield_rect()
        if rect is None:
            return self.x, self.y
        return rect.centerx, rect.centery

    def center_on_tile(self, tile):
        # Zmiana aktywnego gracza nie centruje kamery na pionku. Przy nowej
        # mapie dopasowujemy cala rozete, a pozniej tylko pilnujemy ograniczen.
        _sync_generation(self)

    def center_on_tiles(self, tiles):
        _sync_generation(self, reset_zoom=True)

    def move(self, dx, dy):
        # Drag jest dozwolony. Po ruchu kamera jest ograniczana do pergaminu.
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
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, old_zoom * factor))
        if new_zoom == old_zoom:
            return

        # Zoom pod kursorem, jesli kursor jest nad plansza. Poza plansza zoom
        # odbywa sie wzgledem srodka pergaminu.
        anchor_x, anchor_y = mouse_pos if rect.collidepoint(mouse_pos) else rect.center
        world_x = (anchor_x - self.x) / old_zoom
        world_y = (anchor_y - self.y) / old_zoom

        self.zoom = new_zoom
        self.x = anchor_x - world_x * new_zoom
        self.y = anchor_y - world_y * new_zoom
        _clamp_camera(self)

    Tile.__init__ = tile_init
    Tile.draw = tile_draw
    Tile.contains = tile_contains
    HeroToken.draw = token_draw
    Camera.__init__ = camera_init
    Camera.map_view_center = map_view_center
    Camera.center_on_tile = center_on_tile
    Camera.center_on_tiles = center_on_tiles
    Camera.move = move
    Camera.zoom_at = zoom_at
    Camera._rise_glory_locked_map = True
