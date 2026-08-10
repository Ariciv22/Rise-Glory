"""Sterowanie plansza heksowa wewnatrz pergaminu.

Najwazniejsza zasada tego modulu: pelny obrys rozety ma zawsze pozostawac
wewnatrz bezpiecznego pola pergaminu. Nie ukrywamy heksow i nie przycinamy ich
maska. Zamiast tego ograniczamy zoom oraz drag tak, aby cala plansza zawsze
byla widoczna na mapie.
"""

import pygame

from rg_core.data import HEX_SIZE, MAX_ZOOM
from rg_ui.common import game_layout_rects
from rg_world.map import Camera, Tile


# Bezpieczny obszar wewnatrz grafiki pergaminu. Ratio odsuwa plansze od
# postrzepionych krawedzi grafiki, a dodatkowy margines pikselowy chroni przed
# dotykaniem ramki przez skrajne heksy.
SAFE_LEFT_RATIO = 0.04
SAFE_RIGHT_RATIO = 0.04
SAFE_TOP_RATIO = 0.04
SAFE_BOTTOM_RATIO = 0.05
SAFE_EDGE_MARGIN = 24

# Zakres zoomu jest celowo niewielki. Maksimum oznacza najwieksza plansze,
# ktora nadal w calosci miesci sie na pergaminie. Minimum daje troche miejsca
# na oddalenie oraz drag, ale nigdy nie pozwala wyjechac heksom poza mape.
MIN_ZOOM_RATIO = 0.86
START_ZOOM_RATIO = 0.93
ABSOLUTE_MIN_ZOOM = 0.10

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

    # Dolny pasek informacji jest HUD-em, a nie czescia pergaminu dostepna dla
    # planszy.
    bottom = layout.get("bottom")
    if bottom is not None and bottom.height > 0:
        rect.height = max(1, rect.height - bottom.height)

    return rect


def playfield_rect():
    """Zwraca bezpieczny prostokat, w ktorym musi zmiescic sie cala rozeta."""
    rect = _center_map_rect()
    if rect is None:
        return None

    left = int(rect.width * SAFE_LEFT_RATIO) + SAFE_EDGE_MARGIN
    right = int(rect.width * SAFE_RIGHT_RATIO) + SAFE_EDGE_MARGIN
    top = int(rect.height * SAFE_TOP_RATIO) + SAFE_EDGE_MARGIN
    bottom = int(rect.height * SAFE_BOTTOM_RATIO) + SAFE_EDGE_MARGIN

    return pygame.Rect(
        rect.x + left,
        rect.y + top,
        max(1, rect.width - left - right),
        max(1, rect.height - top - bottom),
    )


def _expanded_world_bounds():
    """Pelny obrys planszy razem ze skrajnymi ramkami heksow."""
    if _TILE_BOUNDS is None:
        return None

    min_x, max_x, min_y, max_y = _TILE_BOUNDS
    padding = HEX_SIZE * 1.05
    return (
        min_x - padding,
        max_x + padding,
        min_y - padding,
        max_y + padding,
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


def _zoom_limits(rect):
    """Wylicza zoom, przy ktorym cala plansza zawsze miesci sie na mapie."""
    if rect is None or _TILE_BOUNDS is None:
        return ABSOLUTE_MIN_ZOOM, ABSOLUTE_MIN_ZOOM

    world_w, world_h = _world_size()

    # To jest twardy limit. Wiekszy zoom oznaczalby, ze przynajmniej jedna
    # krawedz rozety musi wyjsc poza pergamin, czego teraz zabraniamy.
    safe_max = min(
        MAX_ZOOM,
        rect.width / max(1.0, world_w),
        rect.height / max(1.0, world_h),
    )
    safe_max = max(ABSOLUTE_MIN_ZOOM, safe_max)

    safe_min = max(ABSOLUTE_MIN_ZOOM, safe_max * MIN_ZOOM_RATIO)
    safe_min = min(safe_min, safe_max)
    return safe_min, safe_max


def _center_camera(camera):
    rect = playfield_rect()
    if rect is None:
        return

    world_x, world_y = _world_center()
    camera.x = rect.centerx - world_x * camera.zoom
    camera.y = rect.centery - world_y * camera.zoom


def _clamp_camera(camera):
    """Pilnuje, aby pelny obrys rozety nigdy nie wyszedl poza pergamin."""
    rect = playfield_rect()
    bounds = _expanded_world_bounds()
    if rect is None or bounds is None:
        return

    min_x, max_x, min_y, max_y = bounds

    # Dopuszczalne przesuniecie kamery wynika bezposrednio z warunku:
    # rect.left <= screen_min_x oraz screen_max_x <= rect.right.
    min_camera_x = rect.left - min_x * camera.zoom
    max_camera_x = rect.right - max_x * camera.zoom
    min_camera_y = rect.top - min_y * camera.zoom
    max_camera_y = rect.bottom - max_y * camera.zoom

    # Przy bezpiecznym zoomie dolna granica nie jest wieksza od gornej. Jesli
    # przez zaokraglenia pikseli zdarzy sie odwrotnie, centrujemy dana os.
    if min_camera_x <= max_camera_x:
        camera.x = max(min_camera_x, min(max_camera_x, camera.x))
    else:
        world_cx, _ = _world_center()
        camera.x = rect.centerx - world_cx * camera.zoom

    if min_camera_y <= max_camera_y:
        camera.y = max(min_camera_y, min(max_camera_y, camera.y))
    else:
        _, world_cy = _world_center()
        camera.y = rect.centery - world_cy * camera.zoom


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

    min_zoom, max_zoom = _zoom_limits(rect)
    camera._rg_min_zoom = min_zoom
    camera._rg_max_zoom = max_zoom

    if reset_zoom:
        start_zoom = max(min_zoom, min(max_zoom, max_zoom * START_ZOOM_RATIO))
        camera.zoom = start_zoom
        _center_camera(camera)
        _clamp_camera(camera)
        return

    camera.zoom = max(min_zoom, min(max_zoom, camera.zoom))
    _clamp_camera(camera)


def install_locked_map_camera():
    """Instaluje bezpieczny zoom i drag bez wychodzenia heksow poza mape."""
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
        self._rg_min_zoom = ABSOLUTE_MIN_ZOOM
        self._rg_max_zoom = ABSOLUTE_MIN_ZOOM

    def map_view_center(self):
        rect = playfield_rect()
        if rect is None:
            return self.x, self.y
        return rect.centerx, rect.centery

    def center_on_tile(self, tile):
        # Zmiana aktywnego bohatera nie przesuwa planszy na pionek.
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
        min_zoom = getattr(self, "_rg_min_zoom", ABSOLUTE_MIN_ZOOM)
        max_zoom = getattr(self, "_rg_max_zoom", old_zoom)
        new_zoom = max(min_zoom, min(max_zoom, old_zoom * factor))
        if abs(new_zoom - old_zoom) < 0.000001:
            return

        # Zoom pozostaje stabilny wzgledem srodka pola gry, wiec plansza nie
        # ucieka w strone kursora podczas krecenia kolkiem myszy.
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
