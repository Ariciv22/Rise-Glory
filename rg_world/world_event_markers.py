from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import pygame

from rg_engine.world_events import (
    DURATION_UNTIL_RESOLVED,
    active_world_events,
    set_problem_placement_validator,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
THREAT_MARKER_PATH = ROOT_DIR / "Grafiki" / "zeton_zagrozen.png"

_BOUND_TILES: list[Any] = []
_MARKER_TILE_BY_EVENT: dict[str, int] = {}
_TOKEN_IMAGE = None
_INSTALL_DONE = False
_ACTIVE_CAMERA = None


def bound_tiles() -> list[Any]:
    return list(_BOUND_TILES)


def active_camera():
    return _ACTIVE_CAMERA


def bind_world_tiles(tiles) -> list[Any]:
    global _BOUND_TILES, _MARKER_TILE_BY_EVENT
    _BOUND_TILES = list(tiles or [])
    _MARKER_TILE_BY_EVENT = {}
    for tile in _BOUND_TILES:
        tile.world_event_markers = []
    return _BOUND_TILES


def _load_token_image():
    global _TOKEN_IMAGE
    if _TOKEN_IMAGE is not None:
        return _TOKEN_IMAGE if _TOKEN_IMAGE is not False else None
    if not THREAT_MARKER_PATH.exists():
        _TOKEN_IMAGE = False
        return None
    try:
        _TOKEN_IMAGE = pygame.image.load(str(THREAT_MARKER_PATH)).convert_alpha()
    except (OSError, pygame.error):
        _TOKEN_IMAGE = False
    return _TOKEN_IMAGE if _TOKEN_IMAGE is not False else None


def _problem(event: dict[str, Any]) -> dict[str, Any]:
    value = event.get("problem") or {}
    return value if isinstance(value, dict) else {}


def _normalise_placement(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        return {"type": value}
    return {"type": "random_passable"}


def _matches_placement(tile, placement: dict[str, Any]) -> bool:
    placement_type = str(placement.get("type") or "random_passable")
    location = getattr(tile, "location", None)

    if placement_type in {"random", "any", "random_passable"}:
        return bool(tile.terrain.get("passable", False))
    if placement_type == "terrain":
        expected = str(placement.get("terrain") or placement.get("terrain_key") or "")
        return bool(tile.terrain.get("passable", False)) and str(getattr(tile, "terrain_key", "")) == expected
    if placement_type == "location_kind":
        expected = str(placement.get("kind") or "")
        return isinstance(location, dict) and str(location.get("kind") or "") == expected
    if placement_type == "location_name":
        expected = str(placement.get("name") or "").casefold()
        return isinstance(location, dict) and str(location.get("name") or "").casefold() == expected
    if placement_type == "tile_id":
        return int(getattr(tile, "id", -1)) == int(placement.get("tile_id", -2))
    return bool(tile.terrain.get("passable", False))


def _placement_candidates(placement: dict[str, Any]) -> list[Any]:
    return [tile for tile in _BOUND_TILES if _matches_placement(tile, placement)]


def choose_problem_tile(event: dict[str, Any], rng=None):
    """Wybiera heks według reguły zapisanej bezpośrednio na karcie wydarzenia.

    Obsługiwane reguły: random_passable, terrain, location_kind,
    location_name i tile_id. Jeżeli reguła podstawowa nie ma kandydatów,
    używana jest reguła `fallback` z karty. Brak fallbacku oznacza brak znacznika.
    """
    if not _BOUND_TILES:
        return None
    rng = rng or random
    problem = _problem(event)
    placement = _normalise_placement(problem.get("placement"))
    candidates = _placement_candidates(placement)
    if not candidates:
        fallback = problem.get("fallback")
        if fallback is None:
            return None
        candidates = _placement_candidates(_normalise_placement(fallback))
    if not candidates:
        return None
    if str(placement.get("type") or "") == "tile_id" and len(candidates) == 1:
        return candidates[0]
    return rng.choice(candidates)


def marker_tile(event_id: str):
    tile_id = _MARKER_TILE_BY_EVENT.get(str(event_id))
    if tile_id is None:
        return None
    return next((tile for tile in _BOUND_TILES if int(getattr(tile, "id", -1)) == int(tile_id)), None)


def marker_event_ids_on_tile(tile) -> list[str]:
    return [str(value) for value in (getattr(tile, "world_event_markers", []) or [])]


def active_problem_event(event_id: str) -> dict[str, Any] | None:
    for event in active_world_events(DURATION_UNTIL_RESOLVED):
        if str(event.get("id")) == str(event_id):
            return event
    return None


def place_problem_marker(event: dict[str, Any], rng=None):
    event_id = str(event.get("id") or "")
    if not event_id:
        return None
    existing = marker_tile(event_id)
    if existing is not None:
        return existing

    tile = choose_problem_tile(event, rng=rng)
    if tile is None:
        return None
    markers = getattr(tile, "world_event_markers", None)
    if not isinstance(markers, list):
        markers = []
        tile.world_event_markers = markers
    if event_id not in markers:
        markers.append(event_id)
    _MARKER_TILE_BY_EVENT[event_id] = int(getattr(tile, "id", 0))
    return tile


def remove_problem_marker(event_id: str) -> bool:
    event_id = str(event_id)
    removed = False
    for tile in _BOUND_TILES:
        markers = getattr(tile, "world_event_markers", None)
        if not isinstance(markers, list) or event_id not in markers:
            continue
        tile.world_event_markers = [value for value in markers if str(value) != event_id]
        removed = True
    _MARKER_TILE_BY_EVENT.pop(event_id, None)
    return removed


def sync_problem_markers(rng=None) -> list[tuple[str, int]]:
    """Synchronizuje fizyczne znaczniki z aktywnymi kartami typu Problem."""
    active = active_world_events(DURATION_UNTIL_RESOLVED)
    active_ids = {str(event.get("id")) for event in active}

    for event_id in list(_MARKER_TILE_BY_EVENT):
        if event_id not in active_ids:
            remove_problem_marker(event_id)

    placed = []
    for event in active:
        event_id = str(event.get("id") or "")
        tile = marker_tile(event_id) or place_problem_marker(event, rng=rng)
        if tile is not None:
            placed.append((event_id, int(getattr(tile, "id", 0))))
    return placed


def problem_marker_preview(event_id: str) -> dict[str, Any] | None:
    event = active_problem_event(event_id)
    if event is None:
        return None
    problem = _problem(event)
    return {
        "id": str(event.get("id")),
        "name": str(event.get("name") or "Problem"),
        "description": str(problem.get("description") or event.get("description") or ""),
        "effect": str(event.get("effect_text") or ""),
        "condition": str(problem.get("condition") or "Rozwiąż problem na wskazanym heksie."),
        "action_label": str(problem.get("action_label") or "Rozwiąż problem"),
        "reward_hint": str(problem.get("reward_hint") or "Nagroda: ???"),
        "tile": marker_tile(event_id),
    }


def _draw_marker(tile, screen, camera):
    event_ids = marker_event_ids_on_tile(tile)
    if not event_ids:
        return

    sx, sy = tile.center(camera)
    diameter = max(28, int(50 * camera.zoom))
    image = _load_token_image()

    for index, event_id in enumerate(event_ids[:3]):
        offset_x = (-40 + index * 28) * camera.zoom
        offset_y = -35 * camera.zoom
        center = (int(sx + offset_x), int(sy + offset_y))
        pygame.draw.circle(screen, (17, 10, 12), center, diameter // 2 + 3)
        if image:
            scaled = pygame.transform.smoothscale(image, (diameter, diameter))
            screen.blit(scaled, scaled.get_rect(center=center))
        else:
            pygame.draw.circle(screen, (126, 25, 30), center, diameter // 2)
            pygame.draw.circle(screen, (214, 164, 74), center, diameter // 2, max(2, int(2 * camera.zoom)))
            font = pygame.font.SysFont("arial", max(12, diameter // 3), bold=True)
            label = font.render("!", True, (238, 224, 188))
            screen.blit(label, label.get_rect(center=center))


def install_world_event_markers():
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return

    import rg_world as rg_world_package
    from rg_world import map as rg_map

    original_tile_init = rg_map.Tile.__init__
    original_tile_draw = rg_map.Tile.draw
    original_generate_world = rg_world_package.generate_world
    original_camera_init = rg_map.Camera.__init__

    def tile_init_with_world_markers(self, *args, **kwargs):
        original_tile_init(self, *args, **kwargs)
        self.world_event_markers = []

    def tile_draw_with_world_markers(self, screen, textures, camera, font, *args, **kwargs):
        result = original_tile_draw(self, screen, textures, camera, font, *args, **kwargs)
        _draw_marker(self, screen, camera)
        return result

    def generate_world_with_world_markers(map_key="rosette9"):
        return bind_world_tiles(original_generate_world(map_key))

    def camera_init_with_world_marker_registry(self, *args, **kwargs):
        global _ACTIVE_CAMERA
        original_camera_init(self, *args, **kwargs)
        _ACTIVE_CAMERA = self

    rg_map.Tile.__init__ = tile_init_with_world_markers
    rg_map.Tile.draw = tile_draw_with_world_markers
    rg_map.Camera.__init__ = camera_init_with_world_marker_registry
    rg_world_package.generate_world = generate_world_with_world_markers
    set_problem_placement_validator(lambda event: place_problem_marker(event) is not None)
    _INSTALL_DONE = True
