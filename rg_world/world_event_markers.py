from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import pygame

from rg_engine.threats import (
    marker_count,
    marker_is_resolved,
    make_marker_ref,
    parse_marker_ref,
    set_marker_tile,
    threat_display_number,
    unresolved_marker_ids,
)
from rg_engine.world_events import DURATION_UNTIL_RESOLVED, active_world_events, set_problem_placement_validator

ROOT_DIR = Path(__file__).resolve().parents[1]
THREAT_MARKER_PATH = ROOT_DIR / "Grafiki" / "zeton_zagrozen.png"

_BOUND_TILES: list[Any] = []
_MARKER_TILE_BY_REF: dict[str, int] = {}
_TOKEN_IMAGE = None
_INSTALL_DONE = False
_ACTIVE_CAMERA = None


def bound_tiles() -> list[Any]:
    return list(_BOUND_TILES)


def active_camera():
    return _ACTIVE_CAMERA


def bind_world_tiles(tiles) -> list[Any]:
    global _BOUND_TILES, _MARKER_TILE_BY_REF
    _BOUND_TILES = list(tiles or [])
    _MARKER_TILE_BY_REF = {}
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
    passable = bool(tile.terrain.get("passable", False))
    if placement_type in {"random", "any", "random_passable"}:
        return passable
    if placement_type == "terrain":
        expected = str(placement.get("terrain") or placement.get("terrain_key") or "")
        return passable and str(getattr(tile, "terrain_key", "")) == expected
    if placement_type == "location_kind":
        expected = str(placement.get("kind") or "")
        return isinstance(location, dict) and str(location.get("kind") or "") == expected
    if placement_type == "location_name":
        expected = str(placement.get("name") or "").casefold()
        return isinstance(location, dict) and str(location.get("name") or "").casefold() == expected
    if placement_type == "tile_id":
        return int(getattr(tile, "id", -1)) == int(placement.get("tile_id", -2))
    return passable


def _placement_candidates(placement: dict[str, Any], excluded: set[int] | None = None) -> list[Any]:
    excluded = excluded or set()
    return [tile for tile in _BOUND_TILES if int(getattr(tile, "id", -1)) not in excluded and _matches_placement(tile, placement)]


def _marker_placement(event: dict[str, Any], marker_id: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    problem = _problem(event)
    placements = problem.get("placements")
    if isinstance(placements, list):
        index = max(0, int(marker_id) - 1) if str(marker_id).isdigit() else 0
        if index < len(placements):
            row = placements[index]
            if isinstance(row, dict) and ("placement" in row or "fallback" in row):
                placement = _normalise_placement(row.get("placement"))
                fallback = row.get("fallback", problem.get("fallback"))
                return placement, _normalise_placement(fallback) if fallback is not None else None
            return _normalise_placement(row), _normalise_placement(problem.get("fallback")) if problem.get("fallback") is not None else None
    placement = _normalise_placement(problem.get("placement"))
    fallback = problem.get("fallback")
    return placement, _normalise_placement(fallback) if fallback is not None else None


def _select_distinct_tiles(event: dict[str, Any], marker_ids: list[str], rng=None, excluded: set[int] | None = None) -> dict[str, Any] | None:
    if not _BOUND_TILES:
        return None
    rng = rng or random
    used = set(excluded or set())
    selected: dict[str, Any] = {}
    if marker_ids:
        placements = [_marker_placement(event, marker_id) for marker_id in marker_ids]
        if all(placements[0] == value for value in placements):
            primary, fallback = placements[0]
            candidates = _placement_candidates(primary, used)
            chosen_pool = candidates if len(candidates) >= len(marker_ids) else (_placement_candidates(fallback, used) if fallback else [])
            if len(chosen_pool) < len(marker_ids):
                return None
            chosen_pool = list(chosen_pool)
            rng.shuffle(chosen_pool)
            return {marker_id: tile for marker_id, tile in zip(marker_ids, chosen_pool[: len(marker_ids)])}
    for marker_id in marker_ids:
        placement, fallback = _marker_placement(event, marker_id)
        candidates = _placement_candidates(placement, used)
        if not candidates and fallback is not None:
            candidates = _placement_candidates(fallback, used)
        if not candidates:
            return None
        tile = candidates[0] if str(placement.get("type") or "") == "tile_id" else rng.choice(candidates)
        selected[marker_id] = tile
        used.add(int(getattr(tile, "id", 0)))
    return selected


def can_place_problem_markers(event: dict[str, Any]) -> bool:
    marker_ids = [str(index) for index in range(1, marker_count(event) + 1)]
    return _select_distinct_tiles(event, marker_ids, rng=random.Random(0)) is not None


def choose_problem_tile(event: dict[str, Any], rng=None):
    selected = _select_distinct_tiles(event, ["1"], rng=rng)
    return selected.get("1") if selected else None


def marker_tile(event_or_ref: str):
    event_id, marker_id = parse_marker_ref(str(event_or_ref))
    if "::" in str(event_or_ref):
        tile_id = _MARKER_TILE_BY_REF.get(make_marker_ref(event_id, marker_id))
    else:
        tile_id = None
        for unresolved in unresolved_marker_ids(event_id):
            value = _MARKER_TILE_BY_REF.get(make_marker_ref(event_id, unresolved))
            if value is not None:
                tile_id = value
                break
    if tile_id is None:
        return None
    return next((tile for tile in _BOUND_TILES if int(getattr(tile, "id", -1)) == int(tile_id)), None)


def marker_tiles(event_id: str) -> list[Any]:
    result = []
    for marker_id in unresolved_marker_ids(event_id):
        tile = marker_tile(make_marker_ref(event_id, marker_id))
        if tile is not None:
            result.append(tile)
    return result


def marker_event_ids_on_tile(tile) -> list[str]:
    return [str(value) for value in (getattr(tile, "world_event_markers", []) or [])]


def active_problem_event(event_or_ref: str) -> dict[str, Any] | None:
    event_id, _marker_id = parse_marker_ref(str(event_or_ref))
    for event in active_world_events(DURATION_UNTIL_RESOLVED):
        if str(event.get("id")) == event_id:
            return event
    return None


def _attach_marker(tile, marker_ref: str) -> None:
    markers = getattr(tile, "world_event_markers", None)
    if not isinstance(markers, list):
        markers = []
        tile.world_event_markers = markers
    if marker_ref not in markers:
        markers.append(marker_ref)
    _MARKER_TILE_BY_REF[marker_ref] = int(getattr(tile, "id", 0))
    event_id, marker_id = parse_marker_ref(marker_ref)
    set_marker_tile(event_id, marker_id, int(getattr(tile, "id", 0)))


def place_problem_markers(event: dict[str, Any], rng=None) -> list[Any]:
    event_id = str(event.get("id") or "")
    if not event_id:
        return []
    unresolved = unresolved_marker_ids(event_id)
    existing_tiles: dict[str, Any] = {}
    used_ids: set[int] = set()
    missing: list[str] = []
    for marker_id in unresolved:
        ref = make_marker_ref(event_id, marker_id)
        tile = marker_tile(ref)
        if tile is None:
            missing.append(marker_id)
        else:
            existing_tiles[marker_id] = tile
            used_ids.add(int(getattr(tile, "id", 0)))
    if missing:
        selected = _select_distinct_tiles(event, missing, rng=rng, excluded=used_ids)
        if selected is None:
            return []
        for marker_id, tile in selected.items():
            _attach_marker(tile, make_marker_ref(event_id, marker_id))
            existing_tiles[marker_id] = tile
    return [existing_tiles[mid] for mid in unresolved if mid in existing_tiles]


def place_problem_marker(event: dict[str, Any], rng=None):
    tiles = place_problem_markers(event, rng=rng)
    return tiles[0] if tiles else None


def remove_problem_marker(event_or_ref: str) -> bool:
    value = str(event_or_ref)
    event_id, marker_id = parse_marker_ref(value)
    refs = [make_marker_ref(event_id, marker_id)] if "::" in value else [ref for ref in list(_MARKER_TILE_BY_REF) if parse_marker_ref(ref)[0] == event_id]
    removed = False
    for ref in refs:
        for tile in _BOUND_TILES:
            markers = getattr(tile, "world_event_markers", None)
            if not isinstance(markers, list) or ref not in markers:
                continue
            tile.world_event_markers = [entry for entry in markers if str(entry) != ref]
            removed = True
        _MARKER_TILE_BY_REF.pop(ref, None)
        ref_event, ref_marker = parse_marker_ref(ref)
        set_marker_tile(ref_event, ref_marker, None)
    return removed


def sync_problem_markers(rng=None) -> list[tuple[str, int]]:
    active = active_world_events(DURATION_UNTIL_RESOLVED)
    active_ids = {str(event.get("id")) for event in active}
    for ref in list(_MARKER_TILE_BY_REF):
        event_id, marker_id = parse_marker_ref(ref)
        if event_id not in active_ids or marker_is_resolved(event_id, marker_id):
            remove_problem_marker(ref)
    placed: list[tuple[str, int]] = []
    for event in active:
        event_id = str(event.get("id") or "")
        for tile in place_problem_markers(event, rng=rng):
            refs = [ref for ref in marker_event_ids_on_tile(tile) if parse_marker_ref(ref)[0] == event_id]
            for ref in refs:
                placed.append((ref, int(getattr(tile, "id", 0))))
    return placed


def problem_marker_preview(event_or_ref: str) -> dict[str, Any] | None:
    event = active_problem_event(event_or_ref)
    if event is None:
        return None
    event_id, marker_id = parse_marker_ref(str(event_or_ref))
    problem = _problem(event)
    return {
        "id": event_id,
        "marker_id": marker_id,
        "marker_ref": make_marker_ref(event_id, marker_id),
        "display_number": threat_display_number(event_id),
        "name": str(event.get("name") or "Problem"),
        "description": str(problem.get("description") or event.get("description") or ""),
        "effect": str(event.get("effect_text") or ""),
        "condition": str(problem.get("condition") or "Rozwiąż problem na wskazanym heksie."),
        "action_label": str(problem.get("action_label") or "Rozwiąż problem"),
        "reward_hint": "Nagroda: ???",
        "tile": marker_tile(make_marker_ref(event_id, marker_id)),
        "markers_remaining": len(unresolved_marker_ids(event_id)),
        "markers_total": marker_count(event),
    }


def _draw_marker(tile, screen, camera):
    refs = marker_event_ids_on_tile(tile)
    if not refs:
        return
    sx, sy = tile.center(camera)
    diameter = max(28, int(50 * camera.zoom))
    image = _load_token_image()
    columns = 3
    for index, ref in enumerate(refs):
        col = index % columns
        row = index // columns
        offset_x = (-40 + col * 28) * camera.zoom
        offset_y = (-35 + row * 30) * camera.zoom
        center = (int(sx + offset_x), int(sy + offset_y))
        pygame.draw.circle(screen, (17, 10, 12), center, diameter // 2 + 3)
        if image:
            scaled = pygame.transform.smoothscale(image, (diameter, diameter))
            screen.blit(scaled, scaled.get_rect(center=center))
        else:
            pygame.draw.circle(screen, (126, 25, 30), center, diameter // 2)
            pygame.draw.circle(screen, (214, 164, 74), center, diameter // 2, max(2, int(2 * camera.zoom)))
        event_id, _marker_id = parse_marker_ref(ref)
        number = threat_display_number(event_id)
        font = pygame.font.SysFont("georgia", max(12, diameter // 3), bold=True)
        label = font.render(str(number or "!"), True, (245, 235, 208))
        badge_y = center[1] + diameter // 5
        shadow = font.render(str(number or "!"), True, (20, 12, 10))
        screen.blit(shadow, shadow.get_rect(center=(center[0] + 1, badge_y + 1)))
        screen.blit(label, label.get_rect(center=(center[0], badge_y)))


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
    set_problem_placement_validator(can_place_problem_markers)
    _INSTALL_DONE = True
