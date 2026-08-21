from pathlib import Path

import pygame

from rg_ui import city


LOCATION_UI_DIR = city.ROOT_DIR / "Grafiki" / "grafiki_lokacji"
LEFT_PANEL_FILE = LOCATION_UI_DIR / "lewy_ui.png"
RIGHT_PANEL_FILE = LOCATION_UI_DIR / "prawy_ui.png"

# Stala logiczna siatka ekranu lokacji. Gra bazowo pracuje w 1600x860, a
# elementy lokacji sa skalowane z tej jednej siatki do faktycznego rozmiaru okna.
LOCATION_CANVAS_W = 1600
LOCATION_CANVAS_H = 860
LOCATION_BODY_H = 790
LOCATION_BOTTOM_H = 70
LOCATION_LEFT_W = 320
LOCATION_SCENE_W = 960
LOCATION_RIGHT_W = 320

# Kazda z dziewieciu generowanych lokacji dostaje wlasna scene.
LOCATION_SCENE_FILES = {
    ("city", 1): ("miasto1.png",),
    ("city", 2): ("miasto2.png",),
    ("city", 3): ("miasto3.png",),
    ("castle", 1): ("zamek1.png",),
    ("castle", 2): ("zamek2.png",),
    ("castle", 3): ("zamek3.png",),
    ("village", 1): ("wies1.png",),
    ("village", 2): ("wies2.png", "wieś2.png"),
    ("village", 3): ("wies3.png",),
}

LOCATION_NAME_NUMBERS = {
    "Lirion": 1,
    "Miasto 1": 1,
    "Miasto 2": 2,
    "Miasto 3": 3,
    "Artium": 1,
    "Zamek 1": 1,
    "Zamek 2": 2,
    "Zamek 3": 3,
    "Wies 1": 1,
    "Wies 2": 2,
    "Wies 3": 3,
    "Wieś 1": 1,
    "Wieś 2": 2,
    "Wieś 3": 3,
}

LOCATION_MENU = [
    ("Sklep", "location_shop"),
    ("Karczma", "location_tavern"),
    ("Tablica ogloszen", "location_board"),
    ("Trening", "location_training"),
    ("Leczenie", "location_healing"),
    ("Ekwipunek", "location_equipment"),
]

_GOLD_TEXT = (196, 151, 78)
_GOLD_HOVER = (224, 177, 91)
_DARK_BAR = (13, 12, 11)
_SCENE_BG = (5, 5, 5)
_ASSET_CACHE = {}
_SCALED_CACHE = {}
_SCENE_CACHE = {}


class LocationMenuButton(city.Button):
    """Niewidzialny hitbox nakladany na gotowy przycisk z lewy_ui.png."""

    def draw(self, screen, font, mouse_pos, active=False):
        _ = font
        hovered = self.rect.collidepoint(mouse_pos)
        if hovered or active:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            overlay.fill((205, 145, 45, 25 if hovered else 17))
            screen.blit(overlay, self.rect.topleft)
            pygame.draw.rect(
                screen,
                _GOLD_HOVER if hovered else _GOLD_TEXT,
                self.rect,
                2,
                border_radius=8,
            )


def _load_asset(path):
    path = Path(path)
    key = str(path)
    if key in _ASSET_CACHE:
        return _ASSET_CACHE[key]
    if not path.exists():
        _ASSET_CACHE[key] = None
        return None
    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        image = None
    _ASSET_CACHE[key] = image
    return image


def _scaled_asset(path, size):
    size = (max(1, int(size[0])), max(1, int(size[1])))
    key = (str(path), size)
    if key in _SCALED_CACHE:
        return _SCALED_CACHE[key]
    source = _load_asset(path)
    if source is None:
        return None
    if source.get_size() == size:
        _SCALED_CACHE[key] = source
        return source
    scaled = pygame.transform.smoothscale(source, size)
    _SCALED_CACHE[key] = scaled
    return scaled


def _draw_panel_asset(screen, rect, path):
    # Panel ma zawsze jeden docelowy ksztalt wynikajacy ze stalej siatki
    # 1600x860. Resize okna skaluje caly layout, a nie kazdy panel wg osobnych
    # zasad.
    image = _scaled_asset(path, rect.size)
    if image is None:
        city.draw_panel(screen, rect, city.GOLD)
        return
    screen.blit(image, rect.topleft)


def _location_number(location):
    try:
        number = int(location.get("number", 0) or 0)
    except (TypeError, ValueError):
        number = 0
    if number in {1, 2, 3}:
        return number
    return LOCATION_NAME_NUMBERS.get(str(location.get("name", "")))


def _scene_file_for_location(location):
    kind = str(location.get("kind", ""))
    number = _location_number(location)
    if number is None:
        return None

    for filename in LOCATION_SCENE_FILES.get((kind, number), ()):
        path = LOCATION_UI_DIR / filename
        if path.exists():
            return path
    return None


def _cover_surface(source, size):
    """Wypelnia caly prostokat scena bez deformacji, dopuszczajac tylko crop tla."""
    rw, rh = max(1, int(size[0])), max(1, int(size[1]))
    iw, ih = source.get_size()
    if iw <= 0 or ih <= 0:
        return None

    scale = max(rw / iw, rh / ih)
    scaled_size = (
        max(1, int(round(iw * scale))),
        max(1, int(round(ih * scale))),
    )
    scaled = pygame.transform.smoothscale(source, scaled_size)

    result = pygame.Surface((rw, rh), pygame.SRCALPHA)
    src_x = max(0, (scaled.get_width() - rw) // 2)
    src_y = max(0, (scaled.get_height() - rh) // 2)
    result.blit(scaled, (0, 0), pygame.Rect(src_x, src_y, rw, rh))
    return result


def _fit_scene(rect, scene_file):
    """Pokazuje CALA scene i jednoczesnie nie zostawia czarnych pasow.

    Oryginalna grafika jest skalowana proporcjonalnie w trybie contain i zawsze
    pozostaje widoczna w calosci. Wolne miejsce wynikajace z innych proporcji
    srodkowego pola wypelnia przyciemnione powiekszenie tej samej sceny zamiast
    czarnych dziur.
    """
    source = _load_asset(scene_file)
    if source is None:
        return None

    key = (str(scene_file), rect.size, "fixed-grid-full-scene")
    if key in _SCENE_CACHE:
        return _SCENE_CACHE[key]

    rw, rh = max(1, rect.width), max(1, rect.height)
    background = _cover_surface(source, (rw, rh))
    if background is None:
        return None

    shade = pygame.Surface((rw, rh), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 82))
    background.blit(shade, (0, 0))

    iw, ih = source.get_size()
    scale = min(rw / iw, rh / ih)
    full_size = (
        max(1, int(round(iw * scale))),
        max(1, int(round(ih * scale))),
    )
    full_scene = (
        source
        if source.get_size() == full_size
        else pygame.transform.smoothscale(source, full_size)
    )

    full_x = (rw - full_scene.get_width()) // 2
    full_y = (rh - full_scene.get_height()) // 2
    background.blit(full_scene, (full_x, full_y))

    _SCENE_CACHE[key] = background
    return background


def _scaled_grid_value(value, actual, logical):
    return int(round(actual * value / logical))


def location_hub_layout(screen, scene_file=None):
    """Staly layout 1600x860: 320 | 960 | 320 oraz dolny pas 70 px."""
    _ = scene_file
    sw, sh = screen.get_size()

    bottom_h = max(
        1,
        min(
            sh - 1,
            _scaled_grid_value(
                LOCATION_BOTTOM_H,
                sh,
                LOCATION_CANVAS_H,
            ),
        ),
    )
    body_h = max(1, sh - bottom_h)

    left_w = _scaled_grid_value(LOCATION_LEFT_W, sw, LOCATION_CANVAS_W)
    scene_w = _scaled_grid_value(LOCATION_SCENE_W, sw, LOCATION_CANVAS_W)
    right_w = max(1, sw - left_w - scene_w)

    left = pygame.Rect(0, 0, left_w, body_h)
    scene = pygame.Rect(left.right, 0, scene_w, body_h)
    right = pygame.Rect(scene.right, 0, right_w, body_h)
    bottom = pygame.Rect(0, body_h, sw, sh - body_h)
    return {"left": left, "scene": scene, "right": right, "bottom": bottom}


city_hub_layout = location_hub_layout


def _menu_button_rects(left_rect):
    button_x = left_rect.x + int(left_rect.width * 0.17)
    button_w = int(left_rect.width * 0.68)
    button_h = max(36, int(left_rect.height * 0.108))
    start_y = left_rect.y + int(left_rect.height * 0.075)
    step = int(left_rect.height * 0.118)

    rows = []
    for index, (label, action) in enumerate(LOCATION_MENU):
        rows.append(
            (
                label,
                action,
                pygame.Rect(
                    button_x,
                    start_y + index * step,
                    button_w,
                    button_h,
                ),
            )
        )

    back = pygame.Rect(
        button_x,
        left_rect.y + int(left_rect.height * 0.85),
        button_w,
        max(36, int(left_rect.height * 0.10)),
    )
    return rows, back


def right_content_rect(right_rect):
    """Docelowy obszar na zmienny content prawego panelu."""
    pad_x = int(right_rect.width * 0.08)
    pad_top = int(right_rect.height * 0.06)
    pad_bottom = int(right_rect.height * 0.05)
    return pygame.Rect(
        right_rect.x + pad_x,
        right_rect.y + pad_top,
        right_rect.width - pad_x * 2,
        right_rect.height - pad_top - pad_bottom,
    )


def _draw_left_menu(screen, font, mouse_pos, selected_place, rect):
    buttons = []
    rows, back_rect = _menu_button_rects(rect)

    for label, action, button_rect in rows:
        button = LocationMenuButton(label, action, button_rect)
        button.draw(screen, font, mouse_pos, active=(selected_place == action))
        buttons.append(button)

    back = LocationMenuButton("Powrot na mape", "back_to_map", back_rect)
    back.draw(screen, font, mouse_pos)
    buttons.append(back)
    return buttons


def _draw_right_content(
    screen,
    font,
    small_font,
    mouse_pos,
    location,
    player,
    selected_place,
    rect,
):
    """Pusty kontener na docelowy content prawego panelu."""
    _ = (
        screen,
        font,
        small_font,
        mouse_pos,
        location,
        player,
        selected_place,
        right_content_rect(rect),
    )
    return []


def _draw_bottom_bar(screen, rect, message=""):
    pygame.draw.rect(screen, _DARK_BAR, rect)
    pygame.draw.line(
        screen,
        (87, 55, 26),
        (rect.left, rect.top),
        (rect.right, rect.top),
        2,
    )
    pygame.draw.line(
        screen,
        (171, 112, 42),
        (rect.left + 10, rect.top + 4),
        (rect.right - 10, rect.top + 4),
        1,
    )
    pygame.draw.rect(screen, (111, 71, 29), rect, 2)

    if message:
        font = pygame.font.SysFont("arial", 16, bold=True)
        label = font.render(str(message)[:150], True, city.MUTED)
        screen.blit(
            label,
            (rect.x + 24, rect.centery - label.get_height() // 2),
        )


def draw_location_hub_screen(
    screen,
    title_font,
    font,
    small_font,
    mouse_pos,
    location,
    player,
    selected_place=None,
    message="",
):
    _ = title_font
    city.initialize_location(location)
    scene_file = _scene_file_for_location(location)
    if scene_file is None:
        return None

    layout = location_hub_layout(screen, scene_file)
    scene_image = _fit_scene(layout["scene"], scene_file)
    if scene_image is None:
        return None

    screen.fill(_SCENE_BG)
    screen.blit(scene_image, layout["scene"].topleft)

    _draw_panel_asset(screen, layout["left"], LEFT_PANEL_FILE)
    _draw_panel_asset(screen, layout["right"], RIGHT_PANEL_FILE)

    pygame.draw.line(
        screen,
        (104, 67, 27),
        (layout["left"].right - 1, layout["left"].top),
        (layout["left"].right - 1, layout["left"].bottom),
        2,
    )
    pygame.draw.line(
        screen,
        (104, 67, 27),
        (layout["right"].left, layout["right"].top),
        (layout["right"].left, layout["right"].bottom),
        2,
    )

    buttons = _draw_left_menu(
        screen,
        font,
        mouse_pos,
        selected_place,
        layout["left"],
    )
    buttons += _draw_right_content(
        screen,
        font,
        small_font,
        mouse_pos,
        location,
        player,
        selected_place,
        layout["right"],
    )

    effective_message = message or player.get("_location_message", "")
    _draw_bottom_bar(screen, layout["bottom"], effective_message)
    return buttons


def draw_lirion_city_screen(
    screen,
    title_font,
    font,
    small_font,
    mouse_pos,
    location,
    player,
    selected_place=None,
    message="",
):
    return draw_location_hub_screen(
        screen,
        title_font,
        font,
        small_font,
        mouse_pos,
        location,
        player,
        selected_place,
        message,
    )


def install_city_hub(app_module):
    """Instaluje wspolny shell UI dla 3 miast, 3 zamkow i 3 wsi."""
    if getattr(app_module, "_rise_glory_city_hub_installed", False):
        return

    original = app_module.draw_city_screen

    def wrapped(
        screen,
        title_font,
        font,
        small_font,
        mouse_pos,
        location,
        player,
        selected_place=None,
        message="",
    ):
        scene_file = _scene_file_for_location(location)
        use_location_ui = (
            location.get("kind") in {"city", "castle", "village"}
            and scene_file is not None
            and not city.is_combat_active()
            and screen.get_width() >= 1100
            and screen.get_height() >= 700
            and not city.parse_quest_action(selected_place)
        )
        if use_location_ui:
            result = draw_location_hub_screen(
                screen,
                title_font,
                font,
                small_font,
                mouse_pos,
                location,
                player,
                selected_place,
                message,
            )
            if result is not None:
                return result
        return original(
            screen,
            title_font,
            font,
            small_font,
            mouse_pos,
            location,
            player,
            selected_place,
            message,
        )

    app_module.draw_city_screen = wrapped
    app_module._rise_glory_city_hub_installed = True


install_location_hub = install_city_hub
