from __future__ import annotations

import pygame

from rg_world import map as world_map


_INSTALLED = False
_ORIGINAL_TILE_DRAW = world_map.Tile.draw

_MATERIAL_SHORT = {
    "Żelazo": "Fe",
    "Drewno": "Dr",
    "Skóra": "Sk",
    "Srebro": "Ag",
    "Tkanina": "Tk",
    "Klejnoty": "Kl",
    "Kamień": "Ka",
    "Mroczna Stal": "MS",
    "Proch": "Pr",
    "Odłamek Upadku": "OU",
}


def _draw_production_marker(tile, screen, camera, font):
    site = getattr(tile, "production_site", None)
    if not isinstance(site, dict):
        return

    sx, sy = tile.center(camera)
    radius = max(9, int(15 * camera.zoom))
    center = (int(sx), int(sy + 42 * camera.zoom))
    active = site.get("status") == "active"

    fill = (36, 31, 23) if active else (48, 48, 48)
    border = (196, 151, 78) if active else (145, 145, 145)
    pygame.draw.circle(screen, (8, 8, 8), center, radius + 3)
    pygame.draw.circle(screen, fill, center, radius)
    pygame.draw.circle(screen, border, center, radius, max(2, int(2 * camera.zoom)))

    label_text = _MATERIAL_SHORT.get(str(site.get("material")), "Z")
    try:
        marker_font = pygame.font.SysFont("georgia", max(9, int(12 * camera.zoom)), bold=True)
    except pygame.error:
        marker_font = font
    label = marker_font.render(label_text, True, (226, 211, 177))
    screen.blit(label, label.get_rect(center=center))

    if not active:
        build = marker_font.render("...", True, (205, 205, 205))
        screen.blit(build, build.get_rect(midtop=(center[0], center[1] + radius + 1)))


def _tile_draw_with_production(self, screen, textures, camera, font, hovered=False, selected=False, valid_move=False):
    _ORIGINAL_TILE_DRAW(
        self,
        screen,
        textures,
        camera,
        font,
        hovered=hovered,
        selected=selected,
        valid_move=valid_move,
    )
    _draw_production_marker(self, screen, camera, font)


def install_production_visuals():
    global _INSTALLED
    if _INSTALLED:
        return
    world_map.Tile.draw = _tile_draw_with_production
    _INSTALLED = True
