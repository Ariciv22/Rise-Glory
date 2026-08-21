from pathlib import Path

import pygame

from rg_ui import city


LOCATION_UI_DIR = city.ROOT_DIR / "Grafiki" / "grafiki_lokacji"
LEFT_PANEL_FILE = LOCATION_UI_DIR / "lewy_ui.png"
RIGHT_PANEL_FILE = LOCATION_UI_DIR / "prawy_ui.png"

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


def _asset_ratio(path, fallback):
    image = _load_asset(path)
    if image is None:
        return fallback
    width, height = image.get_size()
    if width <= 0 or height <= 0:
        return fallback
    return width / height


def _draw_panel_asset(screen, rect, path):
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


def _fit_scene(rect, scene_file):
    """Renderuje scene jeden raz, bez cropu, tla i powielania fragmentow."""
    source = _load_asset(scene_file)
    if source is None:
        return None

    key = (str(scene_file), rect.size, "native-ratio-single-scene")
    if key in _SCENE_CACHE:
        return _SCENE_CACHE[key]

    if source.get_size() == rect.size:
        scene = source
    else:
        scene = pygame.transform.smoothscale(source, rect.size)

    _SCENE_CACHE[key] = scene
    return scene


def location_hub_layout(screen, scene_file=None):
    """Uklad wynika z PRAWDZIWYCH proporcji PNG, nie z wymuszonych 320/960/320.

    Najpierw liczymy wspolna wysokosc dla lewego panelu, sceny i prawego panelu
    tak, aby wszystkie trzy zachowaly swoje oryginalne proporcje i razem
    wypelnily szerokosc okna. Cala pozostala wysokosc ekranu jest dzielona po
    rowno miedzy gorny i dolny panel.
    """
    sw, sh = screen.get_size()

    left_ratio = _asset_ratio(LEFT_PANEL_FILE, 2 / 3)
    right_ratio = _asset_ratio(RIGHT_PANEL_FILE, 2 / 3)
    scene_ratio = _asset_ratio(scene_file, 16 / 9) if scene_file else 16 / 9

    total_ratio = max(0.1, left_ratio + scene_ratio + right_ratio)

    # Minimalnie zostawiamy miejsce na oba poziome panele. W typowym 16:9
    # wysokosc wynika przede wszystkim z szerokosci i naturalnych proporcji PNG.
    min_bar_h = max(28, int(round(sh * 0.045)))
    max_body_h = max(1, sh - 2 * min_bar_h)
    body_h = min(max_body_h, max(1, int(round(sw / total_ratio))))

    left_w = max(1, int(round(body_h * left_ratio)))
    scene_w = max(1, int(round(body_h * scene_ratio)))
    right_w = max(1, int(round(body_h * right_ratio)))

    body_w = left_w + scene_w + right_w

    # Korekta pojedynczych pikseli po zaokragleniach.
    if body_w > sw:
        overflow = body_w - sw
        scene_w = max(1, scene_w - overflow)
        body_w = left_w + scene_w + right_w

    body_x = max(0, (sw - body_w) // 2)
    free_h = max(0, sh - body_h)
    top_h = free_h // 2
    bottom_h = free_h - top_h

    top = pygame.Rect(0, 0, sw, top_h)
    left = pygame.Rect(body_x, top_h, left_w, body_h)
    scene = pygame.Rect(left.right, top_h, scene_w, body_h)
    right = pygame.Rect(scene.right, top_h, right_w, body_h)
    bottom = pygame.Rect(0, top_h + body_h, sw, bottom_h)

    return {
        "top": top,
        "left": left,
        "scene": scene,
        "right": right,
        "bottom": bottom,
    }


city_hub_layout = location_hub_layout


def _menu_button_rects(left_rect):
    button_x = left_rect.x + int(left_rect.width * 0.17)
    button_w = int(left_rect.width * 0.68)
    button_h = max(28, int(left_rect.height * 0.108))
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
        max(28, int(left_rect.height * 0.10)),
    )
    return rows, back


def right_content_rect(right_rect):
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


def _draw_edge_bar(screen, rect, message=""):
    if rect.height <= 0:
        return

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
        bar_font = pygame.font.SysFont("arial", 16, bold=True)
        label = bar_font.render(str(message)[:150], True, city.MUTED)
        screen.blit(
            label,
            (rect.x + 24, rect.centery - label.get_height() // 2),
        )


def _draw_bottom_bar(screen, rect, message=""):
    _draw_edge_bar(screen, rect, message)


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

    _draw_edge_bar(screen, layout["top"])
    _draw_edge_bar(
        screen,
        layout["bottom"],
        message or player.get("_location_message", ""),
    )

    _draw_panel_asset(screen, layout["left"], LEFT_PANEL_FILE)
    screen.blit(scene_image, layout["scene"].topleft)
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
