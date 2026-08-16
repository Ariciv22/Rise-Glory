from __future__ import annotations

import random
from typing import Any

import pygame

from rg_engine.quests import set_quest_marker_hooks
from rg_engine.world import registered_players
from rg_world.world_event_markers import bound_tiles

_MARKER_TILE_BY_ID: dict[str, int] = {}
_MARKER_DATA_BY_ID: dict[str, dict[str, Any]] = {}
_INSTALL_DONE = False


def _placement(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        return {"type": value}
    return {"type": "random_passable"}


def _matches(tile, placement: dict[str, Any]) -> bool:
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


def _choose_tile(marker: dict[str, Any], used: set[int], rng=None):
    rng = rng or random
    primary = _placement(marker.get("placement"))
    fallback = _placement(marker.get("fallback")) if marker.get("fallback") is not None else None
    candidates = [
        tile for tile in bound_tiles()
        if int(getattr(tile, "id", -1)) not in used and _matches(tile, primary)
    ]
    if not candidates and fallback is not None:
        candidates = [
            tile for tile in bound_tiles()
            if int(getattr(tile, "id", -1)) not in used and _matches(tile, fallback)
        ]
    if not candidates:
        return None
    if str(primary.get("type") or "") == "tile_id":
        return candidates[0]
    return rng.choice(candidates)


def _attach(tile, marker: dict[str, Any]) -> None:
    marker_id = str(marker.get("marker_id") or "")
    if not marker_id:
        return
    markers = getattr(tile, "quest_markers", None)
    if not isinstance(markers, list):
        markers = []
        tile.quest_markers = markers
    if marker_id not in markers:
        markers.append(marker_id)
    tile_id = int(getattr(tile, "id", 0) or 0)
    marker["tile_id"] = tile_id
    _MARKER_TILE_BY_ID[marker_id] = tile_id
    _MARKER_DATA_BY_ID[marker_id] = marker


def _on_markers_created(quest: dict[str, Any], markers: list[dict[str, Any]]) -> None:
    used = {
        int(marker.get("tile_id"))
        for marker in quest.get("markers", []) or []
        if marker.get("tile_id") is not None
    }
    for marker in markers:
        tile = _choose_tile(marker, used)
        if tile is None:
            marker["tile_id"] = None
            marker["placement_failed"] = True
            _MARKER_DATA_BY_ID[str(marker.get("marker_id") or "")] = marker
            continue
        _attach(tile, marker)
        used.add(int(getattr(tile, "id", 0) or 0))


def _on_markers_cleared(_quest: dict[str, Any], markers: list[dict[str, Any]]) -> None:
    for marker in markers:
        marker_id = str(marker.get("marker_id") or "")
        if not marker_id:
            continue
        for tile in bound_tiles():
            refs = getattr(tile, "quest_markers", None)
            if isinstance(refs, list) and marker_id in refs:
                tile.quest_markers = [value for value in refs if str(value) != marker_id]
        _MARKER_TILE_BY_ID.pop(marker_id, None)
        _MARKER_DATA_BY_ID.pop(marker_id, None)


def quest_marker_ids_on_tile(tile) -> list[str]:
    return [str(value) for value in (getattr(tile, "quest_markers", []) or [])]


def marker_tile(marker_id: str):
    tile_id = _MARKER_TILE_BY_ID.get(str(marker_id))
    if tile_id is None:
        return None
    return next((tile for tile in bound_tiles() if int(getattr(tile, "id", -1)) == tile_id), None)


def quest_for_marker(marker_id: str):
    marker_id = str(marker_id)
    for player in registered_players():
        for quest in player.get("active_quests", []) or []:
            for marker in quest.get("markers", []) or []:
                if str(marker.get("marker_id")) == marker_id:
                    return player, quest, marker
    return None, None, _MARKER_DATA_BY_ID.get(marker_id)


def quest_marker_preview(marker_id: str) -> dict[str, Any] | None:
    player, quest, marker = quest_for_marker(marker_id)
    if not marker:
        return None
    return {
        "marker_id": str(marker.get("marker_id") or marker_id),
        "quest_id": str(marker.get("quest_id") or (quest or {}).get("id") or ""),
        "quest_number": int(marker.get("quest_number", (quest or {}).get("quest_number", 0)) or 0),
        "quest_name": str((quest or {}).get("name") or "Quest"),
        "action_label": str(marker.get("action_label") or "Kontynuuj Quest"),
        "description": str(marker.get("description") or (quest or {}).get("objective") or ""),
        "tile": marker_tile(str(marker.get("marker_id") or marker_id)),
        "owner": player,
        "quest": quest,
    }


def _draw_marker(tile, screen, camera):
    refs = quest_marker_ids_on_tile(tile)
    if not refs:
        return
    sx, sy = tile.center(camera)
    diameter = max(26, int(46 * camera.zoom))
    font = pygame.font.SysFont("georgia", max(12, diameter // 3), bold=True)
    for index, marker_id in enumerate(refs):
        data = _MARKER_DATA_BY_ID.get(marker_id) or {}
        col = index % 3
        row = index // 3
        center = (
            int(sx + (40 + col * 28) * camera.zoom),
            int(sy + (-35 + row * 30) * camera.zoom),
        )
        pygame.draw.circle(screen, (19, 23, 29), center, diameter // 2 + 3)
        pygame.draw.circle(screen, (68, 86, 105), center, diameter // 2)
        pygame.draw.circle(screen, (214, 164, 74), center, diameter // 2, max(2, int(2 * camera.zoom)))
        number = int(data.get("quest_number", 0) or 0)
        label = font.render(str(number or "Q"), True, (245, 235, 208))
        screen.blit(label, label.get_rect(center=center))


def marker_screen_rect(marker_id: str, camera):
    tile = marker_tile(marker_id)
    if tile is None or camera is None:
        return None
    refs = quest_marker_ids_on_tile(tile)
    try:
        index = refs.index(str(marker_id))
    except ValueError:
        index = 0
    sx, sy = tile.center(camera)
    diameter = max(26, int(46 * camera.zoom))
    col = index % 3
    row = index // 3
    center = (
        int(sx + (40 + col * 28) * camera.zoom),
        int(sy + (-35 + row * 30) * camera.zoom),
    )
    return pygame.Rect(center[0] - diameter // 2 - 4, center[1] - diameter // 2 - 4, diameter + 8, diameter + 8)


def install_quest_markers() -> None:
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return
    import rg_world as rg_world_package
    from rg_world import map as rg_map

    original_tile_init = rg_map.Tile.__init__
    original_tile_draw = rg_map.Tile.draw
    original_generate_world = rg_world_package.generate_world

    def tile_init_with_quest_markers(self, *args, **kwargs):
        original_tile_init(self, *args, **kwargs)
        self.quest_markers = []

    def tile_draw_with_quest_markers(self, screen, textures, camera, font, *args, **kwargs):
        result = original_tile_draw(self, screen, textures, camera, font, *args, **kwargs)
        _draw_marker(self, screen, camera)
        return result

    def generate_world_with_quest_markers(map_key="rosette9"):
        global _MARKER_TILE_BY_ID, _MARKER_DATA_BY_ID
        tiles = original_generate_world(map_key)
        _MARKER_TILE_BY_ID = {}
        _MARKER_DATA_BY_ID = {}
        for tile in tiles:
            tile.quest_markers = []
        return tiles

    rg_map.Tile.__init__ = tile_init_with_quest_markers
    rg_map.Tile.draw = tile_draw_with_quest_markers
    rg_world_package.generate_world = generate_world_with_quest_markers
    set_quest_marker_hooks(_on_markers_created, _on_markers_cleared)
    _INSTALL_DONE = True
