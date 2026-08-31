from __future__ import annotations

import pygame

from rg_ui import city_hub


_INSTALLED = False

# Awaryjny aspekt oryginalnego lewego UI. Przy normalnej pracy szerokosc jest
# liczona z faktycznego, widocznego fragmentu lewy_ui.png po usunieciu jedynie
# zewnetrznego czarnego marginesu.
_LEFT_PANEL_FALLBACK_ASPECT = 1023 / 1537


def _left_panel_aspect() -> float:
    source = city_hub._load_asset(city_hub.LEFT_PANEL_FILE)
    if source is None:
        return _LEFT_PANEL_FALLBACK_ASPECT

    try:
        crop = city_hub._panel_crop_rect(city_hub.LEFT_PANEL_FILE, source)
    except (ValueError, pygame.error):
        return _LEFT_PANEL_FALLBACK_ASPECT

    if crop.width <= 0 or crop.height <= 0:
        return _LEFT_PANEL_FALLBACK_ASPECT
    return crop.width / crop.height


def install_location_panel_aspect_fix() -> None:
    """Nie pozwala sciskac lewy_ui.png do arbitralnych 18% ekranu.

    Wysokosc panelu nadal wynika z dostepnego miejsca pomiedzy gornym i dolnym
    HUD-em, ale jego szerokosc jest liczona z proporcji samego assetu. Dzieki
    temu kafle, ikony i napisy zachowuja naturalne proporcje na ekranach miast,
    zamkow i wsi.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    original_layout = city_hub.location_hub_layout

    def location_hub_layout(screen, scene_file=None):
        base = original_layout(screen, scene_file)
        sw, _sh = screen.get_size()

        body_y = base["left"].y
        body_h = base["left"].height
        right_w = base["right"].width

        desired_left_w = max(220, int(round(body_h * _left_panel_aspect())))

        # Scena nadal musi zostac duza i czytelna. Ten limit jest tylko
        # bezpiecznikiem dla malych okien; przy typowych 1080p/1440p lewy panel
        # dostaje pelna szerokosc wynikajaca z jego oryginalnych proporcji.
        min_scene_w = max(440, int(round(sw * 0.40)))
        max_left_w = max(1, sw - right_w - min_scene_w)
        left_w = min(desired_left_w, max_left_w)

        # Nowy shell jest uruchamiany dopiero od 1100 px szerokosci, wiec w
        # praktyce ten fallback nie powinien byc potrzebny. Chroni jednak layout
        # przed ujemna szerokoscia przy nietypowym resize okna.
        if left_w < 1:
            left_w = max(1, base["left"].width)

        scene_w = max(1, sw - left_w - right_w)

        left = pygame.Rect(0, body_y, left_w, body_h)
        scene = pygame.Rect(left.right, body_y, scene_w, body_h)
        right = pygame.Rect(scene.right, body_y, right_w, body_h)

        return {
            "top": base["top"],
            "left": left,
            "scene": scene,
            "right": right,
            "bottom": base["bottom"],
        }

    city_hub.location_hub_layout = location_hub_layout
    city_hub.city_hub_layout = location_hub_layout
    city_hub._rise_glory_location_panel_aspect_fix_installed = True
    _INSTALLED = True
