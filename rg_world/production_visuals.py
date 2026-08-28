from __future__ import annotations

import pygame

from rg_world import map as world_map


_INSTALLED = False
_FONT_CACHE = {}

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

# Finalna rama heksa jest osobna nakladka rysowana po bazowym rendererze.
# Wszystkie jej linie leza wyraznie wewnatrz wielokata heksa, dlatego kafel
# renderowany pozniej nie moze juz uciac prawej albo dolnej krawedzi ramy.
HEX_FRAME_SHADOW = (31, 22, 14)
HEX_FRAME_BRONZE = (105, 72, 34)
HEX_FRAME_GOLD = (184, 137, 67)
HEX_FRAME_HIGHLIGHT = (230, 194, 117)

HEX_HOVER_DARK = (120, 79, 28)
HEX_HOVER_LIGHT = (244, 205, 111)

HEX_SELECTED_DARK = (92, 35, 31)
HEX_SELECTED_MID = (184, 82, 48)
HEX_SELECTED_LIGHT = (245, 195, 102)

HEX_MOVE_DARK = (47, 79, 54)
HEX_MOVE_LIGHT = (132, 174, 106)


def _marker_font(base_font, camera):
    size = max(9, int(12 * camera.zoom))
    cached = _FONT_CACHE.get(size)
    if cached is not None:
        return cached
    try:
        cached = pygame.font.SysFont("georgia", size, bold=True)
    except pygame.error:
        cached = base_font
    _FONT_CACHE[size] = cached
    return cached


def _inset_polygon(points, factor):
    if not points:
        return []
    cx = sum(point[0] for point in points) / len(points)
    cy = sum(point[1] for point in points) / len(points)
    return [
        (cx + (x - cx) * factor, cy + (y - cy) * factor)
        for x, y in points
    ]


def _draw_hex_frame_overlay(tile, screen, camera, hovered=False, selected=False, valid_move=False):
    """Rysuje pelna rame UI wewnatrz heksa zamiast kreski na wspolnej krawedzi."""
    points = tile.screen_points(camera)
    zoom = max(0.35, float(camera.zoom))

    # Stala rama wszystkich heksow: cien -> braz -> zloto -> cienki refleks.
    # Najbardziej zewnetrzna linia nadal ma zapas od prawdziwej krawedzi.
    frame_shadow = _inset_polygon(points, 0.958)
    frame_bronze = _inset_polygon(points, 0.936)
    frame_gold = _inset_polygon(points, 0.916)
    frame_light = _inset_polygon(points, 0.898)

    pygame.draw.polygon(screen, HEX_FRAME_SHADOW, frame_shadow, max(3, int(8 * zoom)))
    pygame.draw.polygon(screen, HEX_FRAME_BRONZE, frame_bronze, max(2, int(5 * zoom)))
    pygame.draw.polygon(screen, HEX_FRAME_GOLD, frame_gold, max(2, int(3 * zoom)))
    pygame.draw.polygon(screen, HEX_FRAME_HIGHLIGHT, frame_light, max(1, int(1.4 * zoom)))

    # Dostepny ruch jest celowo zielony, zeby nie mieszal sie z wyborem heksa.
    if valid_move and not selected:
        move_outer = _inset_polygon(points, 0.872)
        move_inner = _inset_polygon(points, 0.850)
        pygame.draw.polygon(screen, HEX_MOVE_DARK, move_outer, max(2, int(5 * zoom)))
        pygame.draw.polygon(screen, HEX_MOVE_LIGHT, move_inner, max(1, int(2 * zoom)))

    # Hover pozostaje w palecie zlota planszy.
    if hovered and not selected:
        hover_outer = _inset_polygon(points, 0.865)
        hover_inner = _inset_polygon(points, 0.838)
        pygame.draw.polygon(screen, HEX_HOVER_DARK, hover_outer, max(3, int(6 * zoom)))
        pygame.draw.polygon(screen, HEX_HOVER_LIGHT, hover_inner, max(1, int(2 * zoom)))

    # Zaznaczenie nie jest juz niebieska linia na brzegu. To osobna,
    # bordowo-miedziana rama osadzona jeszcze glebiej w kaflu.
    if selected:
        selected_outer = _inset_polygon(points, 0.862)
        selected_mid = _inset_polygon(points, 0.830)
        selected_inner = _inset_polygon(points, 0.804)
        pygame.draw.polygon(screen, HEX_SELECTED_DARK, selected_outer, max(4, int(8 * zoom)))
        pygame.draw.polygon(screen, HEX_SELECTED_MID, selected_mid, max(2, int(5 * zoom)))
        pygame.draw.polygon(screen, HEX_SELECTED_LIGHT, selected_inner, max(1, int(2 * zoom)))


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
    marker_font = _marker_font(font, camera)
    label = marker_font.render(label_text, True, (226, 211, 177))
    screen.blit(label, label.get_rect(center=center))

    if not active:
        build = marker_font.render("...", True, (205, 205, 205))
        screen.blit(build, build.get_rect(midtop=(center[0], center[1] + radius + 1)))


def install_production_visuals():
    """Doklada finalna rame heksa i znaczniki Zakladow na aktywny renderer mapy.

    Renderer Tile.draw jest modyfikowany przez kilka systemow (szybkie
    skalowanie tekstur, tlo mapy, Questy, Wydarzenia Swiata). Przechwytujemy
    go dopiero tutaj. Stare flagi hover/selected/valid_move przekazujemy jako
    False, bo finalny renderer mapy nadal rysowal dawny niebieski outline na
    samej wspolnej krawedzi heksow. Interakcje rysujemy ponownie jako osobna
    nakladke, wyraznie wewnatrz kafla.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    current_tile_draw = world_map.Tile.draw

    def tile_draw_with_production(
        self,
        screen,
        textures,
        camera,
        font,
        hovered=False,
        selected=False,
        valid_move=False,
    ):
        result = current_tile_draw(
            self,
            screen,
            textures,
            camera,
            font,
            hovered=False,
            selected=False,
            valid_move=False,
        )
        _draw_hex_frame_overlay(
            self,
            screen,
            camera,
            hovered=hovered,
            selected=selected,
            valid_move=valid_move,
        )
        _draw_production_marker(self, screen, camera, font)
        return result

    tile_draw_with_production._rise_glory_production_visuals = True
    tile_draw_with_production._rise_glory_hex_frame_overlay = True
    world_map.Tile.draw = tile_draw_with_production
    _INSTALLED = True
