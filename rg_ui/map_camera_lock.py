"""Sterowanie plansza heksowa wewnatrz jasnego srodka pergaminu.

Widok planszy ma ksztalt zblizony do owalu widocznego na grafice tlo_heksow.
Przy starcie cala rozeta miesci sie w tym obszarze. Przy przyblizeniu gracz
moze przesuwac mape, ale heksy poza bezpiecznym polem nie sa rysowane.
Nie stosujemy prostokatnego clippingu pikseli: heks jest widoczny w calosci
albo nie jest rysowany, dzieki czemu krawedzie planszy nie sa brutalnie
ucinane prostokatnym oknem.
"""

import math

import pygame

from rg_core.data import HEX_SIZE, MAX_ZOOM, MIN_ZOOM
from rg_ui.common import game_layout_rects
from rg_world.map import Camera, HeroToken, Tile


# Obwiednia jasnego pola pergaminu. Wartosci sa liczone wewnatrz centralnego
# obszaru mapy po odjeciu paneli HUD i dolnego paska informacji.
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

    bottom = layout.get("bottom")
    if bottom is not None and bottom.height > 0:
        rect.height = max(1, rect.height - bottom.height)

    return rect


def playfield_rect():
    """Prostokat opisujacy owalne pole przeznaczone dla planszy."""
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


def _ellipse_value(point, rect, inset=0.0):
    """Zwraca 0 w centrum i 1 na krawedzi elipsy."""
    if rect is None:
        return 0.0

    rx = max(1.0, rect.width / 2.0 - inset)
    ry = max(1.0, rect.height / 2.0 - inset)
    dx = (float(point[0]) - rect.centerx) / rx
    dy = (float(point[1]) - rect.centery) / ry
    return dx * dx + dy * dy


def _point_inside_playfield(point, inset=0.0):
    rect = playfield_rect()
    if rect is None:
        return True
    return _ellipse_value(point, rect, inset) <= 1.0


def _tile_fully_inside_playfield(tile, camera):
    # Kilka pikseli zapasu chroni zlota ramke heksa przed dotykaniem ozdobnej
    # czesci pergaminu.
    inset = max(2.0, 5.0 * camera.zoom)
    return all(_point_inside_playfield(point, inset) for point in tile.screen_points(camera))


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
    """Dopasowuje cala rozete do elipsy, nie tylko do prostokata."""
    bounds = _expanded_world_bounds()
    if rect is None or bounds is None:
        return MIN_ZOOM

    min_x, max_x, min_y, max_y = bounds
    world_w = max(1.0, max_x - min_x)
    world_h = max(1.0, max_y - min_y)

    # Warunek dla naroza prostokata opisujacego cala plansze:
    # (half_w / ellipse_rx)^2 + (half_h / ellipse_ry)^2 <= 1.
    # Jest to celowo konserwatywne i gwarantuje, ze startowo wszystkie heksy
    # mieszcza sie w jasnym owalu pergaminu.
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
    """Ogranicza drag do obwiedni elipsy, bez prostokatnego przycinania."""
    rect = playfield_rect()
    bounds = _expanded_world_bounds()
    if rect is None or bounds is None:
        return

    min_x, max_x, min_y, max_y = bounds
    scaled_w = (max_x - min_x) * camera.zoom
    scaled_h = (max_y - min_y) * camera.zoom

    # Do ograniczenia panowania uzywamy prostokata opisujacego elipse. Sama
    # widocznosc heksow jest nizej liczona po elipsie, wiec nie powstaje twarda
    # prostokatna krawedz jak w poprzedniej wersji.
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
    else:
        # Nie pozwalamy oddalic planszy bardziej niz widok calej rozety.
        if camera.zoom < fit_zoom:
            camera.zoom = fit_zoom
            _center_camera(camera)
        _clamp_camera(camera)


def install_locked_map_camera():
    """Instaluje owalny viewport, zoom, drag i ograniczenia planszy."""
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
        # Bez screen.set_clip(): nie tniemy heksow prostokatnym oknem. Heks
        # pojawia sie dopiero wtedy, gdy miesci sie w calosci w jasnym owalu.
        if not _tile_fully_inside_playfield(self, camera):
            return None
        return original_tile_draw(self, screen, textures, camera, font, *args, **kwargs)

    def tile_contains(self, pos, camera):
        if not _point_inside_playfield(pos):
            return False
        if not _tile_fully_inside_playfield(self, camera):
            return False
        return original_tile_contains(self, pos, camera)

    def token_draw(self, screen, camera, font, *args, **kwargs):
        if not _tile_fully_inside_playfield(self.tile, camera):
            return None
        return original_token_draw(self, screen, camera, font, *args, **kwargs)

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
        # Zmiana aktywnego bohatera nie przesuwa mapy na pionek.
        _sync_generation(self)

    def center_on_tiles(self, tiles):
        _sync_generation(self, reset_zoom=True)

    def move(self, dx, dy):
        # Drag dziala normalnie po przyblizeniu. Przy widoku calej rozety mapa
        # pozostaje wycentrowana, bo nie ma potrzeby jej przesuwac.
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

        # Zoom jest zakotwiczony pod kursorem tylko wtedy, gdy kursor znajduje
        # sie w jasnym owalu. Poza nim zoomujemy wzgledem srodka planszy.
        anchor = mouse_pos if _point_inside_playfield(mouse_pos) else rect.center
        anchor_x, anchor_y = anchor
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
