from collections import Counter
from pathlib import Path
import math
import unicodedata

import pygame

from rg_core.data import GOLD, MAX_WOUNDS, MUTED, TEXT


ROOT_DIR = Path(__file__).resolve().parents[1]
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
_TARGET_NAME = "ostatecznywygladplanszetkigraczav1"
_PLAYER_BOARD_OPEN = False
_OPEN_QUEST_INDEX = None
_BOARD_SOURCE = None
_BOARD_PATH = None
_BOARD_SEARCHED = False
_SCALED_CACHE = {}


STAT_ORDER = ("Walka", "Handel", "Dyplomacja", "Intryga", "Nauka", "Kultura")


def open_player_board():
    global _PLAYER_BOARD_OPEN
    _PLAYER_BOARD_OPEN = True


def close_player_board():
    global _PLAYER_BOARD_OPEN, _OPEN_QUEST_INDEX
    _PLAYER_BOARD_OPEN = False
    _OPEN_QUEST_INDEX = None


def is_player_board_open():
    return _PLAYER_BOARD_OPEN


def open_quest_details(index):
    global _OPEN_QUEST_INDEX
    try:
        index = int(index)
    except (TypeError, ValueError):
        return False
    if index < 0:
        return False
    _OPEN_QUEST_INDEX = index
    return True


def close_quest_details():
    global _OPEN_QUEST_INDEX
    was_open = _OPEN_QUEST_INDEX is not None
    _OPEN_QUEST_INDEX = None
    return was_open


def get_open_quest_index():
    return _OPEN_QUEST_INDEX


def is_quest_details_open():
    return _OPEN_QUEST_INDEX is not None


def _normalize_name(value):
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return "".join(character for character in ascii_text.lower() if character.isalnum())


def _find_board_path():
    direct_names = [
        "ostateczny wyglad planszetki gracza v1.png",
        "ostateczny wygląd planszetki gracza v1.png",
        "ostateczny_wyglad_planszetki_gracza_v1.png",
        "ostateczny-wyglad-planszetki-gracza-v1.png",
    ]
    likely_directories = [
        ROOT_DIR,
        ROOT_DIR / "Grafiki",
        ROOT_DIR / "Grafiki" / "Grafiki UI",
        ROOT_DIR / "Grafiki" / "planszetka gracza",
        ROOT_DIR / "Grafiki" / "Planszetka gracza",
    ]

    for directory in likely_directories:
        for name in direct_names:
            path = directory / name
            if path.is_file():
                return path

    search_roots = [ROOT_DIR / "Grafiki", ROOT_DIR]
    fallback = None
    for search_root in search_roots:
        if not search_root.exists():
            continue
        for path in search_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _IMAGE_EXTENSIONS:
                continue
            normalized_stem = _normalize_name(path.stem)
            if _TARGET_NAME in normalized_stem:
                return path
            if fallback is None and "planszetkigracza" in normalized_stem and "v1" in normalized_stem:
                fallback = path
        if fallback is not None:
            return fallback
    return None


def _load_board_source():
    global _BOARD_SOURCE, _BOARD_PATH, _BOARD_SEARCHED
    if _BOARD_SEARCHED:
        return _BOARD_SOURCE

    _BOARD_SEARCHED = True
    _BOARD_PATH = _find_board_path()
    if _BOARD_PATH is None:
        return None
    try:
        _BOARD_SOURCE = pygame.image.load(str(_BOARD_PATH)).convert_alpha()
    except pygame.error:
        _BOARD_SOURCE = None
    return _BOARD_SOURCE


def _board_rect(screen, source):
    sw, sh = screen.get_size()
    iw, ih = source.get_size()
    scale = min(sw / iw, sh / ih)
    width = max(1, int(iw * scale))
    height = max(1, int(ih * scale))
    return pygame.Rect((sw - width) // 2, (sh - height) // 2, width, height)


def _draw_board_background(screen):
    source = _load_board_source()
    if source is None:
        screen.fill((11, 10, 9))
        rect = screen.get_rect().inflate(-24, -24)
        pygame.draw.rect(screen, (18, 16, 13), rect)
        pygame.draw.rect(screen, GOLD, rect, 3)
        return rect, False

    rect = _board_rect(screen, source)
    cache_key = rect.size
    scaled = _SCALED_CACHE.get(cache_key)
    if scaled is None:
        scaled = pygame.transform.smoothscale(source, rect.size)
        _SCALED_CACHE[cache_key] = scaled
    screen.fill((7, 7, 7))
    screen.blit(scaled, rect.topleft)
    return rect, True


def _point(rect, x_ratio, y_ratio):
    return int(rect.x + rect.width * x_ratio), int(rect.y + rect.height * y_ratio)


def _relative_rect(rect, x_ratio, y_ratio, width_ratio, height_ratio):
    return pygame.Rect(
        int(rect.x + rect.width * x_ratio),
        int(rect.y + rect.height * y_ratio),
        max(1, int(rect.width * width_ratio)),
        max(1, int(rect.height * height_ratio)),
    )


def player_board_layout(board):
    """Jedyny kontrakt geometrii planszetki bohatera.

    Wszystkie przyszle assety, dane i hitboxy powinny korzystac z tych samych
    prostokatow. Dzięki temu grafika nie moze odjechac od klikanej strefy.
    """
    stat_y = (0.205, 0.256, 0.307, 0.357, 0.408, 0.458)
    stat_x = (0.103, 0.136, 0.169, 0.201, 0.233)
    stat_cell_w = 0.028
    stat_cell_h = 0.038
    stat_cells = {}
    for stat, y in zip(STAT_ORDER, stat_y):
        cells = []
        for x in stat_x:
            cell = _relative_rect(board, x - stat_cell_w / 2, y - stat_cell_h / 2, stat_cell_w, stat_cell_h)
            cells.append(cell)
        stat_cells[stat] = cells

    wound_centers = [_point(board, x, 0.556) for x in (0.030, 0.055, 0.081, 0.107)]
    legend_cells = []
    for y in (0.669, 0.724, 0.780, 0.836, 0.892):
        for x in (0.031, 0.062, 0.094, 0.126, 0.158, 0.190, 0.222):
            legend_cells.append(_relative_rect(board, x - 0.0135, y - 0.018, 0.027, 0.036))

    equipment_slots = []
    for y, height in ((0.066, 0.160), (0.244, 0.160)):
        for x in (0.466, 0.526, 0.586, 0.646):
            equipment_slots.append(_relative_rect(board, x, y, 0.055, height))

    helper_slots = [
        _relative_rect(board, x, 0.486, 0.052, 0.135)
        for x in (0.466, 0.522, 0.578, 0.634, 0.690)
    ]

    backpack_slots = []
    for y in (0.066, 0.158, 0.250, 0.342, 0.434):
        for x in (0.724, 0.772, 0.820):
            backpack_slots.append(_relative_rect(board, x, y, 0.043, 0.083))

    quest_rows = [
        _relative_rect(board, 0.276, 0.694 + index * 0.086, 0.706, 0.078)
        for index in range(3)
    ]

    return {
        "board": pygame.Rect(board),
        "close": _relative_rect(board, 0.840, 0.012, 0.145, 0.048),
        "identity": _relative_rect(board, 0.060, 0.028, 0.185, 0.100),
        "identity_name": _relative_rect(board, 0.082, 0.039, 0.150, 0.038),
        "identity_class": _relative_rect(board, 0.087, 0.082, 0.145, 0.032),
        "attributes": _relative_rect(board, 0.018, 0.155, 0.225, 0.330),
        "stat_cells": stat_cells,
        "wounds": _relative_rect(board, 0.018, 0.510, 0.105, 0.093),
        "wound_centers": wound_centers,
        "gold": _relative_rect(board, 0.127, 0.510, 0.118, 0.093),
        "gold_value": _point(board, 0.220, 0.556),
        "legend": _relative_rect(board, 0.018, 0.630, 0.227, 0.320),
        "legend_cells": legend_cells,
        "portrait": _relative_rect(board, 0.270, 0.075, 0.165, 0.510),
        "equipment": _relative_rect(board, 0.455, 0.035, 0.260, 0.395),
        "equipment_slots": equipment_slots,
        "helpers": _relative_rect(board, 0.455, 0.455, 0.255, 0.180),
        "helper_slots": helper_slots,
        "backpack": _relative_rect(board, 0.715, 0.035, 0.145, 0.600),
        "backpack_slots": backpack_slots,
        "materials": _relative_rect(board, 0.875, 0.060, 0.105, 0.405),
        "food": _relative_rect(board, 0.875, 0.500, 0.105, 0.150),
        "quest_area": _relative_rect(board, 0.270, 0.640, 0.715, 0.320),
        "quest_tabs": {
            "active": _relative_rect(board, 0.282, 0.646, 0.165, 0.038),
            "history": _relative_rect(board, 0.455, 0.646, 0.190, 0.038),
        },
        "quest_pagination": {
            "prev": _relative_rect(board, 0.656, 0.646, 0.035, 0.038),
            "page": _relative_rect(board, 0.695, 0.646, 0.053, 0.038),
            "next": _relative_rect(board, 0.752, 0.646, 0.035, 0.038),
        },
        "quest_rows": quest_rows,
    }


def _font(rect, size, bold=False):
    scaled_size = max(11, int(size * rect.height / 941))
    return pygame.font.SysFont("georgia", scaled_size, bold=bold)


def _draw_text(screen, font, text, pos, color=TEXT, anchor="topleft", shadow=True):
    label = font.render(str(text), True, color)
    target = label.get_rect()
    setattr(target, anchor, pos)
    if shadow:
        shadow_label = font.render(str(text), True, (5, 5, 5))
        screen.blit(shadow_label, target.move(2, 2))
    screen.blit(label, target)
    return target


def _shorten(font, text, max_width):
    value = str(text)
    if font.size(value)[0] <= max_width:
        return value
    while len(value) > 4 and font.size(value + "...")[0] > max_width:
        value = value[:-1]
    return value.rstrip() + "..."


def _wrap(font, text, max_width):
    words = str(text).split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_identity(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    name_font = _font(board, 27, bold=True)
    class_font = _font(board, 18, bold=True)
    _draw_text(screen, name_font, hero.get("name", "Bohater"), layout["identity_name"].topleft, (224, 188, 113))
    _draw_text(screen, class_font, hero.get("archetype_name", hero.get("class", "-")), layout["identity_class"].topleft, (202, 166, 99))


def _draw_stat_markers(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    scale = board.height / 941
    radius = max(9, int(16 * scale))
    for stat in STAT_ORDER:
        value = int(hero.get("stats", {}).get(stat, 0) or 0)
        if value < 1:
            continue
        value = min(5, value)
        center = layout["stat_cells"][stat][value - 1].center
        points = []
        for index in range(6):
            angle = math.radians(60 * index - 30)
            points.append((center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(overlay, (116, 54, 15, 90), points)
        screen.blit(overlay, (0, 0))
        pygame.draw.polygon(screen, (255, 128, 35), points, max(2, int(3 * scale)))


def _draw_hearts(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    heart_font = _font(board, 27, bold=True)
    wounds = max(0, min(MAX_WOUNDS, int(hero.get("wounds", 0) or 0)))
    healthy = MAX_WOUNDS - wounds
    for index, center in enumerate(layout["wound_centers"]):
        color = (190, 38, 38) if index < healthy else (25, 25, 25)
        _draw_text(screen, heart_font, "♥", center, color, anchor="center")


def _draw_gold(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    gold_font = _font(board, 25, bold=True)
    _draw_text(screen, gold_font, hero.get("gold", 0), layout["gold_value"], (238, 193, 92), anchor="center")


def _draw_legend(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    legend = max(0, min(35, int(hero.get("legend", 0) or 0)))
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for cell in layout["legend_cells"][:legend]:
        pygame.draw.rect(overlay, (173, 112, 30, 105), cell, border_radius=max(1, int(4 * board.height / 941)))
    screen.blit(overlay, (0, 0))
    if legend > 0:
        current = layout["legend_cells"][legend - 1].inflate(4, 4)
        pygame.draw.rect(screen, (255, 135, 38), current, max(2, int(3 * board.height / 941)))


def _item_name(item):
    if isinstance(item, dict):
        return str(item.get("name") or item.get("title") or item.get("id") or "Przedmiot")
    return str(item)


def _equipment_values(hero):
    slots = [None] * 8
    equipment = hero.get("equipment")
    if isinstance(equipment, dict):
        aliases = [
            ("weapon", "bron", "Broń"),
            ("armor", "pancerz", "Pancerz"),
            ("helmet", "helm", "Hełm"),
            ("boots", "buty", "Buty"),
            ("gloves", "rekawice", "Rękawice"),
            ("amulet", "Amulet"),
            ("ring_1", "ring1", "pierscien_1", "Pierścień 1"),
            ("ring_2", "ring2", "pierscien_2", "Pierścień 2"),
        ]
        for index, names in enumerate(aliases):
            for name in names:
                if equipment.get(name):
                    slots[index] = _item_name(equipment[name])
                    break
    elif isinstance(equipment, (list, tuple)):
        for index, item in enumerate(equipment[:8]):
            slots[index] = _item_name(item)
    if not slots[0] and hero.get("basic_item"):
        slots[0] = _item_name(hero["basic_item"])
    if not slots[1] and hero.get("class_item"):
        slots[1] = _item_name(hero["class_item"])
    return slots


def _draw_slot_text(screen, board, rect, value, font_size=13):
    if not value:
        return
    font = _font(board, font_size, bold=True)
    words = str(value).split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= rect.width - 8:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    lines = lines[:3]
    line_height = font.get_height() + 1
    y = rect.centery - len(lines) * line_height // 2
    for line in lines:
        text = _shorten(font, line, rect.width - 8)
        _draw_text(screen, font, text, (rect.centerx, y), (218, 185, 120), anchor="midtop")
        y += line_height


def _draw_equipment(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    for rect, value in zip(layout["equipment_slots"], _equipment_values(hero)):
        _draw_slot_text(screen, board, rect, value)


def _draw_helpers(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    helpers = list(hero.get("helpers", []) or [])[:5]
    for rect, helper in zip(layout["helper_slots"], helpers):
        _draw_slot_text(screen, board, rect, _item_name(helper), font_size=12)


def _collect_backpack_items(hero):
    result = []
    for key in ("inventory", "items", "backpack"):
        value = hero.get(key)
        if isinstance(value, dict):
            for item, amount in value.items():
                result.append(f"{item} x{amount}")
        elif isinstance(value, (list, tuple)):
            result.extend(_item_name(item) for item in value)
    result.extend(_item_name(item) for item in hero.get("goods", []) or [])
    return result[:15]


def _draw_backpack(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    for rect, item in zip(layout["backpack_slots"], _collect_backpack_items(hero)):
        _draw_slot_text(screen, board, rect, item, font_size=10)


def _materials_items(hero):
    materials = hero.get("materials", {})
    if isinstance(materials, dict):
        return [(str(name), amount) for name, amount in materials.items()]
    if isinstance(materials, (list, tuple)):
        return list(Counter(_item_name(item) for item in materials).items())
    return []


def _draw_materials(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    items = _materials_items(hero)[:10]
    font = _font(board, 12, bold=True)
    area = layout["materials"]
    line_h = max(font.get_height() + 4, area.height // 10)
    y = area.y + 6
    for name, amount in items:
        _draw_text(screen, font, _shorten(font, name, max(20, area.width - 44)), (area.x + 6, y), (212, 184, 126))
        _draw_text(screen, font, amount, (area.right - 6, y), (232, 201, 137), anchor="topright")
        y += line_h


def _draw_food(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    food = Counter(_item_name(item) for item in (hero.get("food", []) or []))
    font = _font(board, 11, bold=True)
    area = layout["food"]
    line_h = max(font.get_height() + 5, area.height // 3)
    y = area.y + 5
    for name, amount in list(food.items())[:3]:
        _draw_text(screen, font, _shorten(font, name, max(20, area.width - 42)), (area.x + 6, y), (212, 184, 126))
        if amount > 1:
            _draw_text(screen, font, f"x{amount}", (area.right - 6, y), (232, 201, 137), anchor="topright")
        y += line_h


def _quest_row_rects(board, hero):
    quests = list(hero.get("active_quests", []) or [])[:3]
    return player_board_layout(board)["quest_rows"][: len(quests)]


def _draw_quests(screen, board, hero, layout=None):
    layout = layout or player_board_layout(board)
    quests = list(hero.get("active_quests", []) or [])[:3]
    rows = layout["quest_rows"][: len(quests)]
    title_font = _font(board, 16, bold=True)
    description_font = _font(board, 12)
    mouse_pos = pygame.mouse.get_pos()
    if not is_quest_details_open():
        for row in rows:
            if row.collidepoint(mouse_pos):
                overlay = pygame.Surface(row.size, pygame.SRCALPHA)
                overlay.fill((196, 137, 48, 32))
                screen.blit(overlay, row.topleft)
    for index, (quest, row) in enumerate(zip(quests, rows)):
        if isinstance(quest, dict):
            title = quest.get("name") or quest.get("title") or f"Quest {index + 1}"
            description = quest.get("objective") or quest.get("description") or quest.get("deck") or ""
        else:
            title = str(quest)
            description = ""
        title_y = row.y + max(4, int(row.height * 0.22))
        _draw_text(screen, title_font, _shorten(title_font, title, int(row.width * 0.46)), (row.x + int(row.width * 0.057), title_y), (232, 196, 126))
        if description:
            _draw_text(screen, description_font, _shorten(description_font, description, int(row.width * 0.64)), (row.x + int(row.width * 0.057), title_y + title_font.get_height() + 2), MUTED)
    return rows


def _draw_quest_details(screen, board, quest):
    board_shade = pygame.Surface(board.size, pygame.SRCALPHA)
    board_shade.fill((0, 0, 0, 176))
    screen.blit(board_shade, board.topleft)
    panel = _relative_rect(board, 0.305, 0.205, 0.505, 0.500)
    radius = max(8, int(14 * board.height / 941))
    pygame.draw.rect(screen, (12, 11, 10), panel, border_radius=radius)
    pygame.draw.rect(screen, (190, 134, 48), panel, max(2, int(3 * board.height / 941)), border_radius=radius)
    if isinstance(quest, dict):
        title = quest.get("name") or quest.get("title") or "Aktywny quest"
        description = quest.get("objective") or quest.get("description") or "Brak opisu zadania."
        deck = quest.get("deck") or quest.get("category") or "Nieznana talia"
        stage = quest.get("stage") or quest.get("step") or quest.get("progress")
    else:
        title = str(quest)
        description = "Brak opisu zadania."
        deck = "Nieznana talia"
        stage = None
    title_font = _font(board, 25, bold=True)
    subtitle_font = _font(board, 14, bold=True)
    body_font = _font(board, 15)
    _draw_text(screen, title_font, title, (panel.centerx, panel.y + int(panel.height * 0.10)), (235, 199, 126), anchor="center")
    _draw_text(screen, subtitle_font, f"Talia: {deck}", (panel.centerx, panel.y + int(panel.height * 0.22)), MUTED, anchor="center")
    if stage is not None:
        _draw_text(screen, subtitle_font, f"Etap: {stage}", (panel.centerx, panel.y + int(panel.height * 0.29)), (211, 179, 113), anchor="center")
        body_y = panel.y + int(panel.height * 0.38)
    else:
        body_y = panel.y + int(panel.height * 0.32)
    max_width = int(panel.width * 0.82)
    for line in _wrap(body_font, description, max_width)[:6]:
        _draw_text(screen, body_font, line, (panel.centerx, body_y), TEXT, anchor="midtop")
        body_y += body_font.get_height() + max(3, int(4 * board.height / 941))
    status_font = _font(board, 13, bold=True)
    _draw_text(screen, status_font, "Status: aktywny", (panel.centerx, panel.bottom - int(panel.height * 0.20)), (216, 170, 83), anchor="center")
    close_rect = pygame.Rect(0, 0, int(panel.width * 0.34), max(34, int(panel.height * 0.11)))
    close_rect.center = (panel.centerx, panel.bottom - int(panel.height * 0.085))
    hovered = close_rect.collidepoint(pygame.mouse.get_pos())
    button_color = (75, 62, 43) if hovered else (46, 38, 28)
    pygame.draw.rect(screen, button_color, close_rect, border_radius=max(5, int(8 * board.height / 941)))
    pygame.draw.rect(screen, (190, 134, 48), close_rect, max(1, int(2 * board.height / 941)), border_radius=max(5, int(8 * board.height / 941)))
    close_font = _font(board, 15, bold=True)
    _draw_text(screen, close_font, "Zamknij quest", close_rect.center, TEXT, anchor="center", shadow=False)
    return close_rect


def draw_player_board(screen, hero):
    board, source_found = _draw_board_background(screen)
    layout = player_board_layout(board)
    quest_rows = []
    quest_close_rect = None
    if not source_found:
        warning_font = _font(board, 24, bold=True)
        detail_font = _font(board, 16)
        _draw_text(screen, warning_font, "Nie znaleziono planszetki gracza", board.center, (230, 180, 80), anchor="center")
        _draw_text(screen, detail_font, "Oczekiwany plik: ostateczny wyglad planszetki gracza v1", (board.centerx, board.centery + warning_font.get_height() + 10), MUTED, anchor="midtop")
    else:
        # Na tym etapie rysujemy tylko dane/markery. Dekoracyjne ramki beda
        # dokladane pozniej jako assety dokladnie do prostokatow z layoutu.
        _draw_identity(screen, board, hero, layout)
        _draw_stat_markers(screen, board, hero, layout)
        _draw_hearts(screen, board, hero, layout)
        _draw_gold(screen, board, hero, layout)
        _draw_legend(screen, board, hero, layout)
        _draw_equipment(screen, board, hero, layout)
        _draw_helpers(screen, board, hero, layout)
        _draw_backpack(screen, board, hero, layout)
        _draw_materials(screen, board, hero, layout)
        _draw_food(screen, board, hero, layout)
        quest_rows = _draw_quests(screen, board, hero, layout)
        selected_index = get_open_quest_index()
        quests = list(hero.get("active_quests", []) or [])[:3]
        if selected_index is not None:
            if 0 <= selected_index < len(quests):
                quest_close_rect = _draw_quest_details(screen, board, quests[selected_index])
                quest_rows = []
            else:
                close_quest_details()
    hitboxes = {
        "close": layout["close"],
        "quest_rows": quest_rows,
        "quest_tabs": layout["quest_tabs"],
        "quest_pagination": layout["quest_pagination"],
        "equipment_slots": layout["equipment_slots"],
        "helper_slots": layout["helper_slots"],
        "backpack_slots": layout["backpack_slots"],
        "materials": layout["materials"],
        "food": layout["food"],
        "portrait": layout["portrait"],
    }
    return {
        "close_rect": layout["close"],
        "quest_rows": quest_rows,
        "quest_close_rect": quest_close_rect,
        "layout": layout,
        "hitboxes": hitboxes,
    }
