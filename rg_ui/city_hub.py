from pathlib import Path
import unicodedata

import pygame

from rg_ui import city


LOCATION_UI_DIR = city.ROOT_DIR / "Grafiki" / "grafiki_lokacji"
LEFT_PANEL_FILE = LOCATION_UI_DIR / "lewy_ui.png"
RIGHT_PANEL_FILE = LOCATION_UI_DIR / "prawy_ui.png"

# Docelowe proporcje ekranu lokacji sa wzorowane na referencji:
# - szeroki, ale niski panel gorny,
# - duza scena w centrum,
# - czytelne panele po bokach,
# - niski panel dolny.
LOCATION_TOP_SHARE = 0.12
LOCATION_BOTTOM_SHARE = 0.07
LOCATION_LEFT_SHARE = 0.18
LOCATION_RIGHT_SHARE = 0.19

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
_PANEL_CROP_CACHE = {}
_ARROW_FILE_CACHE = {}


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


def _goldish(pixel):
    """Czy piksel nalezy do zlotej/brazowej ramy panelu."""
    r, g, b, a = pixel
    return (
        a > 40
        and r > 55
        and g > 25
        and b < 100
        and (r - g) > 10
        and (g - b) > 4
    )


def _panel_crop_rect(path, source):
    """Usuwa tylko czarny margines na zewnatrz zlotej ramy panelu.

    Wykrywamy wszystkie cztery krawedzie ramy. Dzieki temu panel dochodzi
    wizualnie do sceny, gornego HUD-u i dolnego HUD-u, ale zadna ze zlotych
    krawedzi ani ornamentow nie jest ucinana.
    """
    key = str(path)
    if key in _PANEL_CROP_CACHE:
        return _PANEL_CROP_CACHE[key]

    width, height = source.get_size()
    if width <= 2 or height <= 2:
        rect = pygame.Rect(0, 0, width, height)
        _PANEL_CROP_CACHE[key] = rect
        return rect

    scan_w = max(1, int(round(width * 0.22)))
    step_y = max(1, height // 320)
    samples_y = max(1, (height + step_y - 1) // step_y)
    required_x = max(8, int(round(samples_y * 0.12)))

    def gold_count_x(x):
        count = 0
        for y in range(0, height, step_y):
            if _goldish(source.get_at((x, y))):
                count += 1
                if count >= required_x:
                    return count
        return count

    left_edge = None
    for x in range(scan_w):
        if gold_count_x(x) >= required_x:
            left_edge = x
            break

    right_edge = None
    for x in range(width - 1, max(-1, width - scan_w - 1), -1):
        if gold_count_x(x) >= required_x:
            right_edge = x
            break

    scan_h = max(1, int(round(height * 0.20)))
    step_x = max(1, width // 260)
    samples_x = max(1, (width + step_x - 1) // step_x)
    required_y = max(6, int(round(samples_x * 0.06)))

    def gold_count_y(y):
        count = 0
        for x in range(0, width, step_x):
            if _goldish(source.get_at((x, y))):
                count += 1
                if count >= required_y:
                    return count
        return count

    top_edge = None
    for y in range(scan_h):
        if gold_count_y(y) >= required_y:
            top_edge = y
            break

    bottom_edge = None
    for y in range(height - 1, max(-1, height - scan_h - 1), -1):
        if gold_count_y(y) >= required_y:
            bottom_edge = y
            break

    # Zachowawcze fallbacki - w razie nietypowego assetu lepiej zostawic
    # odrobine czarnego tla niz odciac zlota rame.
    if left_edge is None:
        left_edge = int(round(width * 0.045))
    if right_edge is None:
        right_edge = width - 1 - int(round(width * 0.045))
    if top_edge is None:
        top_edge = int(round(height * 0.025))
    if bottom_edge is None:
        bottom_edge = height - 1 - int(round(height * 0.025))

    frame_padding_x = max(2, int(round(width * 0.006)))
    frame_padding_y = max(2, int(round(height * 0.004)))

    crop_left = max(0, left_edge - frame_padding_x)
    crop_right = min(width, right_edge + frame_padding_x + 1)
    crop_top = max(0, top_edge - frame_padding_y)
    crop_bottom = min(height, bottom_edge + frame_padding_y + 1)

    # Ochrona przed bledna detekcja. Nie pozwalamy automatycznemu cropowi
    # zabrac duzej czesci prawidlowego assetu.
    if crop_right - crop_left < int(round(width * 0.70)):
        crop_left = 0
        crop_right = width
    if crop_bottom - crop_top < int(round(height * 0.72)):
        crop_top = 0
        crop_bottom = height

    rect = pygame.Rect(
        crop_left,
        crop_top,
        max(1, crop_right - crop_left),
        max(1, crop_bottom - crop_top),
    )
    _PANEL_CROP_CACHE[key] = rect
    return rect


def _scaled_panel_asset(path, size):
    """Skaluje panel po usunieciu tylko pustego marginesu poza zlota rama."""
    size = (max(1, int(size[0])), max(1, int(size[1])))
    source = _load_asset(path)
    if source is None:
        return None

    crop_rect = _panel_crop_rect(path, source)
    key = (
        "location-panel-frame-safe-xy",
        str(path),
        size,
        crop_rect.x,
        crop_rect.y,
        crop_rect.width,
        crop_rect.height,
    )
    if key in _SCALED_CACHE:
        return _SCALED_CACHE[key]

    cropped = source.subsurface(crop_rect)
    if cropped.get_size() == size:
        scaled = cropped.copy()
    else:
        scaled = pygame.transform.smoothscale(cropped, size)

    _SCALED_CACHE[key] = scaled
    return scaled


def _draw_panel_asset(screen, rect, path):
    image = _scaled_panel_asset(path, rect.size)
    if image is None:
        city.draw_panel(screen, rect, city.GOLD)
        return
    screen.blit(image, rect.topleft)


def _normalized_asset_name(name):
    normalized = unicodedata.normalize("NFKD", str(name))
    without_marks = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return "".join(char for char in without_marks.lower() if char.isalnum())


def _arrow_asset_file(direction):
    """Znajduje strzalke po nazwie, takze gdy plik ma spacje lub polskie znaki."""
    direction = "left" if direction == "left" else "right"
    if direction in _ARROW_FILE_CACHE:
        return _ARROW_FILE_CACHE[direction]

    exact_names = (
        (
            "strzalka lewa.png",
            "strzałka lewa.png",
            "strzalka_lewa.png",
            "strzałka_lewa.png",
            "strzalka-lewa.png",
            "strzałka-lewa.png",
            "arrow left.png",
            "arrow_left.png",
            "arrow-left.png",
        )
        if direction == "left"
        else (
            "strzalka prawa.png",
            "strzałka prawa.png",
            "strzalka_prawa.png",
            "strzałka_prawa.png",
            "strzalka-prawa.png",
            "strzałka-prawa.png",
            "arrow right.png",
            "arrow_right.png",
            "arrow-right.png",
        )
    )

    for filename in exact_names:
        path = LOCATION_UI_DIR / filename
        if path.exists():
            _ARROW_FILE_CACHE[direction] = path
            return path

    wanted_direction = ("lewa", "left") if direction == "left" else ("prawa", "right")
    try:
        candidates = sorted(LOCATION_UI_DIR.glob("*.png"))
    except OSError:
        candidates = []

    for path in candidates:
        normalized = _normalized_asset_name(path.name)
        has_arrow_word = "strzalka" in normalized or "arrow" in normalized
        has_direction = any(token in normalized for token in wanted_direction)
        if has_arrow_word and has_direction:
            _ARROW_FILE_CACHE[direction] = path
            return path

    _ARROW_FILE_CACHE[direction] = None
    return None


def _draw_asset_contained(screen, path, rect):
    source = _load_asset(path) if path is not None else None
    if source is None or rect.width <= 0 or rect.height <= 0:
        return False

    iw, ih = source.get_size()
    if iw <= 0 or ih <= 0:
        return False

    scale = min(rect.width / iw, rect.height / ih)
    size = (
        max(1, int(round(iw * scale))),
        max(1, int(round(ih * scale))),
    )
    image = _scaled_asset(path, size)
    if image is None:
        return False

    x = rect.centerx - image.get_width() // 2
    y = rect.centery - image.get_height() // 2
    screen.blit(image, (x, y))
    return True


def _right_navigation_rects(right_rect):
    """Pozycje stalych strzalek w stopce prawego panelu."""
    button_w = max(48, int(round(right_rect.width * 0.27)))
    button_h = max(20, int(round(right_rect.height * 0.036)))
    # Strzalki maja siedziec w dolnej stopce, pod separatorem, bez nachodzenia
    # na zlota linie ostatniego wiersza prawego panelu.
    bottom_gap = max(2, int(round(right_rect.height * 0.004)))
    side_gap = max(10, int(round(right_rect.width * 0.15)))

    y = right_rect.bottom - bottom_gap - button_h
    left = pygame.Rect(right_rect.x + side_gap, y, button_w, button_h)
    right = pygame.Rect(right_rect.right - side_gap - button_w, y, button_w, button_h)
    return left, right


def _draw_right_navigation(screen, right_rect):
    """Strzalki sa stale widoczne niezaleznie od wybranej zakladki."""
    left_rect, right_rect_button = _right_navigation_rects(right_rect)
    _draw_asset_contained(screen, _arrow_asset_file("left"), left_rect)
    _draw_asset_contained(screen, _arrow_asset_file("right"), right_rect_button)


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
    """Wypelnia cale pole jedna scena bez deformacji i bez powielania obrazu."""
    source = _load_asset(scene_file)
    if source is None:
        return None

    key = (str(scene_file), rect.size, "reference-cover-single-scene")
    if key in _SCENE_CACHE:
        return _SCENE_CACHE[key]

    rw = max(1, rect.width)
    rh = max(1, rect.height)
    iw, ih = source.get_size()
    if iw <= 0 or ih <= 0:
        return None

    scale = max(rw / iw, rh / ih)
    scaled_size = (
        max(1, int(round(iw * scale))),
        max(1, int(round(ih * scale))),
    )
    scaled = (
        source
        if source.get_size() == scaled_size
        else pygame.transform.smoothscale(source, scaled_size)
    )

    result = pygame.Surface((rw, rh), pygame.SRCALPHA)
    src_x = max(0, (scaled.get_width() - rw) // 2)
    src_y = max(0, (scaled.get_height() - rh) // 2)
    result.blit(scaled, (0, 0), pygame.Rect(src_x, src_y, rw, rh))

    _SCENE_CACHE[key] = result
    return result


def location_hub_layout(screen, scene_file=None):
    """Referencyjny layout: duza scena + rowne boczne panele + top/bottom HUD."""
    _ = scene_file
    sw, sh = screen.get_size()

    top_h = max(56, int(round(sh * LOCATION_TOP_SHARE)))
    bottom_h = max(44, int(round(sh * LOCATION_BOTTOM_SHARE)))

    max_bars = max(2, int(round(sh * 0.23)))
    if top_h + bottom_h > max_bars:
        scale = max_bars / max(1, top_h + bottom_h)
        top_h = max(1, int(round(top_h * scale)))
        bottom_h = max(1, max_bars - top_h)

    body_h = max(1, sh - top_h - bottom_h)

    left_w = max(220, int(round(sw * LOCATION_LEFT_SHARE)))
    right_w = max(230, int(round(sw * LOCATION_RIGHT_SHARE)))

    min_scene_w = max(520, int(round(sw * 0.52)))
    if left_w + right_w + min_scene_w > sw:
        available_for_sides = max(2, sw - min_scene_w)
        side_total = max(1, left_w + right_w)
        left_w = max(1, int(round(available_for_sides * left_w / side_total)))
        right_w = max(1, available_for_sides - left_w)

    scene_w = max(1, sw - left_w - right_w)

    top = pygame.Rect(0, 0, sw, top_h)
    left = pygame.Rect(0, top_h, left_w, body_h)
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
    button_x = left_rect.x + int(left_rect.width * 0.10)
    button_w = int(left_rect.width * 0.82)
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
    # Zostawiamy stale miejsce na strzalki w stopce prawego panelu.
    pad_bottom = int(right_rect.height * 0.10)
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

    # Strzalki sa elementem stalego shellu prawego panelu, wiec rysujemy je
    # zawsze - niezaleznie od miasta/zamku/wsi i wybranej zakladki.
    _draw_right_navigation(screen, layout["right"])
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