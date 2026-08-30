from __future__ import annotations

from rg_world import map as world_map


_INSTALLED = False


def _draw_production_marker(tile, screen, camera, font):
    """Miejsce na docelowe assety zakladow produkcyjnych.

    Stare znaczniki byly technicznymi kolkami z literami materialow (Fe, Dr,
    Sk, Ag itd.). Zostaly celowo usuniete z mapy. Dane zakladu pozostaja na
    heksie i sa nadal widoczne w panelu informacji; tutaj pozniej podepniemy
    male grafiki kopalni, tartakow, kamieniolomow, lowisk i pozostalych
    zakladow w stylu Rise & Glory.
    """
    _ = tile, screen, camera, font
    return None


def install_production_visuals():
    """Zachowuje bezpieczny hook na przyszle assetowe znaczniki zakladow.

    Renderer Tile.draw jest modyfikowany przez kilka systemow (szybkie
    skalowanie tekstur, tlo mapy, Questy, Miejsca i Wydarzenia Swiata), dlatego
    przechwytujemy aktualna funkcje dopiero w chwili instalacji. Na obecnym
    etapie hook niczego nie rysuje - usunelismy tymczasowe literowe kolka.
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
            hovered=hovered,
            selected=selected,
            valid_move=valid_move,
        )
        _draw_production_marker(self, screen, camera, font)
        return result

    tile_draw_with_production._rise_glory_production_visuals = True
    world_map.Tile.draw = tile_draw_with_production
    _INSTALLED = True
