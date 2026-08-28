"""Trwale Miejsca tworzone przez zakonczenia Questow.

Miejsca wynikaja wylacznie z qXX_result i nie tworza dodatkowych flag.
Na tym etapie sa znacznikami swiata z nazwa i zrodlem. Ich przyszle akcje
(lecznictwo, handel, produkcja, badania itd.) beda dokladane osobno.
"""

from __future__ import annotations

import unicodedata
from typing import Any

import pygame

from rg_content.quest_runtime_ext import quest_created_places
from rg_world.world_event_markers import bound_tiles

_INSTALL_DONE = False

# Kotwica wskazuje istniejaca lokacje, przy ktorej pojawia sie nowe Miejsce.
# Nie zmieniamy tile.location, wiec np. Folwark pozostaje osobnym Miejscem
# utworzonym przez Questa, a Elarin nadal jest wsia.
PLACE_ANCHORS = {
    "stary_ogrod": "Eryndor",
    "lazaret_lirion": "Lirion",
    "srebrna_mewa": "Eryndor",
    "folwark_elarin": "Elarin",
    "pierwszy_stol": "Lirion",
    "pasieka_czerwonego_miodu": "Elarin",
    "jarmark_dobrego_losu": "Valdren",
    "wedrowne_laboratorium_mervena": "Norven",
    "most_handlowy": "Norven",
    "ukryty_magazyn": "Elarin",
}


def _norm(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(ch for ch in text.encode("ascii", "ignore").decode("ascii").casefold() if ch.isalnum())


def _anchor_tile(place: dict[str, Any]):
    anchor_name = PLACE_ANCHORS.get(str(place.get("id") or ""))
    if not anchor_name:
        return None
    wanted = _norm(anchor_name)
    for tile in bound_tiles():
        location = getattr(tile, "location", None)
        if isinstance(location, dict) and _norm(location.get("name")) == wanted:
            return tile
    return None


def quest_places_on_tile(tile) -> list[dict[str, Any]]:
    result = []
    tile_id = int(getattr(tile, "id", -1))
    for place in quest_created_places():
        anchor = _anchor_tile(place)
        if anchor is not None and int(getattr(anchor, "id", -2)) == tile_id:
            row = dict(place)
            row["anchor_location"] = PLACE_ANCHORS.get(str(place.get("id") or ""), "")
            row["tile_id"] = tile_id
            result.append(row)
    return result


def quest_place_preview(place_id: str) -> dict[str, Any] | None:
    for place in quest_created_places():
        if str(place.get("id") or "") != str(place_id):
            continue
        tile = _anchor_tile(place)
        row = dict(place)
        row["anchor_location"] = PLACE_ANCHORS.get(str(place.get("id") or ""), "")
        row["tile_id"] = int(getattr(tile, "id", -1)) if tile is not None else None
        row["actions_ready"] = False
        row["note"] = "Miejsce istnieje. Jego akcje zostana okreslone w osobnym module Miejsc."
        return row
    return None


def _draw_quest_places(tile, screen, camera) -> None:
    places = quest_places_on_tile(tile)
    if not places:
        return

    sx, sy = tile.center(camera)
    base_x = int(sx - 48 * camera.zoom)
    base_y = int(sy - 52 * camera.zoom)
    radius = max(11, int(15 * camera.zoom))
    font = pygame.font.SysFont("georgia", max(10, int(12 * camera.zoom)), bold=True)

    for index, place in enumerate(places):
        col = index % 2
        row = index // 2
        center = (
            base_x - int(col * 34 * camera.zoom),
            base_y + int(row * 34 * camera.zoom),
        )
        pygame.draw.circle(screen, (17, 23, 20), center, radius + 4)
        pygame.draw.circle(screen, (82, 125, 103), center, radius)
        pygame.draw.circle(screen, (224, 190, 113), center, radius, max(2, int(2 * camera.zoom)))
        label = font.render("M", True, (248, 240, 218))
        screen.blit(label, label.get_rect(center=center))

        # Nazwa jest widoczna przy markerze, dzieki czemu gracz wie, co
        # powstalo w wyniku Questa nawet zanim Miejsce dostanie wlasne akcje.
        name = str(place.get("name") or "Miejsce")
        name_font = pygame.font.SysFont("georgia", max(9, int(10 * camera.zoom)))
        name_surface = name_font.render(name, True, (238, 225, 194))
        name_rect = name_surface.get_rect(midtop=(center[0], center[1] + radius + 3))
        screen.blit(name_surface, name_rect)


def install_quest_places() -> None:
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return

    from rg_world import map as rg_map

    original_tile_draw = rg_map.Tile.draw

    def tile_draw_with_quest_places(self, screen, textures, camera, font, *args, **kwargs):
        result = original_tile_draw(self, screen, textures, camera, font, *args, **kwargs)
        _draw_quest_places(self, screen, camera)
        return result

    rg_map.Tile.draw = tile_draw_with_quest_places
    _INSTALL_DONE = True
