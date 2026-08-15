from __future__ import annotations

from rg_engine.threats import make_marker_ref, parse_marker_ref, unresolved_marker_ids
from rg_world.world_event_markers import active_camera, marker_tile

_INSTALL_DONE = False


def _normalise_marker_ref(value: str) -> str:
    raw = str(value or "")
    event_id, marker_id = parse_marker_ref(raw)
    if "::" in raw:
        return make_marker_ref(event_id, marker_id)
    remaining = unresolved_marker_ids(event_id)
    return make_marker_ref(event_id, remaining[0]) if remaining else raw


def install_threat_navigation_fix() -> None:
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return
    from rg_ui import threat_layout_fix, world_state

    def open_problem_preview(value: str):
        marker_ref = _normalise_marker_ref(value)
        world_state._STATE_OPEN = True
        world_state._STATE_TAB = "problems"
        world_state._HISTORY_CARD_INDEX = None
        world_state._PROBLEM_PREVIEW_ID = marker_ref
        threat_layout_fix._PREVIEW_PAGE = 0
        tile = marker_tile(marker_ref)
        camera = active_camera()
        if tile is not None and camera is not None:
            camera.center_on_tile(tile)

    world_state._open_problem_preview = open_problem_preview
    _INSTALL_DONE = True
