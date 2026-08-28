from __future__ import annotations

from rg_world import map as world_map


_INSTALLED = False


def install_hex_selection_theme():
    """Wylacza wszystkie wizualne podswietlenia heksow na mapie.

    Logika wyboru heksa nadal dziala normalnie (klikniecie moze aktualizowac
    HUD, potencjal, zaklad itd.), ale sam kafel nie zmienia wygladu. Nie ma
    hoveru, obrysu selected, zmiany koloru ramy, glow ani podswietlenia
    mozliwego ruchu. Na ekran trafia wyłącznie oryginalny asset heksa.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    current_tile_draw = world_map.Tile.draw

    def tile_draw_without_interaction_highlights(
        self,
        screen,
        textures,
        camera,
        font,
        hovered=False,
        selected=False,
        valid_move=False,
    ):
        return current_tile_draw(
            self,
            screen,
            textures,
            camera,
            font,
            hovered=False,
            selected=False,
            valid_move=False,
        )

    tile_draw_without_interaction_highlights._rise_glory_no_hex_highlights = True
    world_map.Tile.draw = tile_draw_without_interaction_highlights
    _INSTALLED = True
