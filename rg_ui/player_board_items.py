from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import unicodedata

import pygame

from rg_engine.items import EQUIPMENT_SLOTS, ensure_equipment_state, normalise_item


ROOT_DIR = Path(__file__).resolve().parents[1]
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

_INSTALLED = False
_ORIGINAL_FIND_BOARD_PATH = None
_ORIGINAL_PLAYER_BOARD_LAYOUT = None
_ORIGINAL_DRAW_PLAYER_BOARD = None
_ORIGINAL_CLOSE_PLAYER_BOARD = None
_ORIGINAL_BUTTON_CLICKED = None
_ORIGINAL_DRAW_GAME_UI = None
_ORIGINAL_DRAW_SLOT_TEXT = None

_OPEN_ITEM_DETAILS: tuple[str, int] | None = None
_CURRENT_CLICKABLES: list[tuple[str, int, pygame.Rect]] = []
_LAST_CLICKABLES: list[tuple[str, int, pygame.Rect]] = []
_LAST_BOARD: pygame.Rect | None = None
_LAST_HERO: dict[str, Any] | None = None

_ITEM_FILE_INDEX: dict[str, Path] | None = None
_IMAGE_CACHE: dict[str, pygame.Surface | None] = {}
_SCALED_CACHE: dict[tuple[str, int, int], pygame.Surface | None] = {}

_SLOT_LABELS = {
    "weapon": "Broń",
    "armor": "Pancerz",
    "helmet": "Hełm",
    "boots": "Buty",
    "gloves": "Rękawice",
    "amulet": "Amulet",
    "ring_1": "Pierścień 1",
    "ring_2": "Pierścień 2",
}


def _normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    return "".join(character for character in ascii_text if character.isalnum())


def _preferred_board_path() -> Path | None:
    candidates = (
        ROOT_DIR / "Grafiki" / "planszetka_gracza" / "1.png",
        ROOT_DIR / "Grafiki" / "Planszetka_gracza" / "1.png",
        ROOT_DIR / "Grafiki" / "planszetka gracza" / "1.png",
        ROOT_DIR / "Grafiki" / "Planszetka gracza" / "1.png",
    )
    for path in candidates:
        if path.is_file():
            return path
    return None


def _find_board_path():
    preferred = _preferred_board_path()
    if preferred is not None:
        return preferred
    return _ORIGINAL_FIND_BOARD_PATH()


def _relative_rect(board: pygame.Rect, x: float, y: float, w: float, h: float) -> pygame.Rect:
    return pygame.Rect(
        int(board.x + board.width * x),
        int(board.y + board.height * y),
        max(1, int(board.width * w)),
        max(1, int(board.height * h)),
    )


def _item_layout(board):
    """Geometria pól przedmiotów dopasowana do planszetka_gracza/1.png.

    Bazowy layout statystyk, Questa i portretu pozostaje bez zmian. Zmieniamy
    wyłącznie pola zawartości: 8 Ekwipunek, 5 Pomocników, 10 Plecak i
    10 Materiały. Dzięki temu nowy asset nie zmienia mechaniki gry.
    """
    layout = _ORIGINAL_PLAYER_BOARD_LAYOUT(board)
    board = pygame.Rect(board)

    # W 1.png podpis slotu jest częścią tła. Prostokąt obejmuje wyłącznie
    # ciemne wnętrze, w którym można bezpiecznie narysować asset przedmiotu.
    equipment_slots = []
    for y, height in ((0.095, 0.142), (0.286, 0.140)):
        for x in (0.474, 0.540, 0.606, 0.672):
            equipment_slots.append(_relative_rect(board, x, y, 0.058, height))

    helper_slots = [
        _relative_rect(board, x, 0.493, 0.052, 0.132)
        for x in (0.466, 0.522, 0.578, 0.634, 0.690)
    ]

    backpack_slots = []
    for y in (0.066, 0.164, 0.262, 0.360, 0.458):
        for x in (0.748, 0.800):
            backpack_slots.append(_relative_rect(board, x, y, 0.044, 0.088))

    material_slots = []
    for y in (0.066, 0.164, 0.262, 0.360, 0.458):
        for x in (0.870, 0.922):
            material_slots.append(_relative_rect(board, x, y, 0.044, 0.088))

    layout["equipment_slots"] = equipment_slots
    layout["helper_slots"] = helper_slots
    layout["backpack_slots"] = backpack_slots
    layout["material_slots"] = material_slots
    layout["backpack"] = _relative_rect(board, 0.742, 0.035, 0.112, 0.602)
    layout["materials"] = _relative_rect(board, 0.864, 0.035, 0.121, 0.602)
    return layout


def _candidate_path(value: Any) -> Path | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    raw = raw.replace("\\", "/")
    candidate = Path(raw)
    bases = [ROOT_DIR, ROOT_DIR / "Grafiki", ROOT_DIR / "Grafiki" / "itemy"]
    variants = [candidate]
    if not candidate.suffix:
        variants = [Path(f"{raw}{ext}") for ext in _IMAGE_EXTENSIONS]
    for base in bases:
        for variant in variants:
            path = variant if variant.is_absolute() else base / variant
            if path.is_file() and path.suffix.lower() in _IMAGE_EXTENSIONS:
                return path
    return None


def _build_item_file_index() -> dict[str, Path]:
    global _ITEM_FILE_INDEX
    if _ITEM_FILE_INDEX is not None:
        return _ITEM_FILE_INDEX

    index: dict[str, Path] = {}
    roots = [ROOT_DIR / "Grafiki" / "itemy", ROOT_DIR / "Grafiki" / "Itemy"]
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _IMAGE_EXTENSIONS:
                continue
            key = _normalize(path.stem)
            if key:
                index.setdefault(key, path)
    _ITEM_FILE_INDEX = index
    return index


def _item_image_path(raw_item: Any) -> Path | None:
    if isinstance(raw_item, dict):
        for key in ("image", "image_path", "icon", "graphic", "asset"):
            path = _candidate_path(raw_item.get(key))
            if path is not None:
                return path
        identities = (
            raw_item.get("name"),
            raw_item.get("title"),
            raw_item.get("id"),
            raw_item.get("item_id"),
        )
    else:
        identities = (raw_item,)

    index = _build_item_file_index()
    for identity in identities:
        key = _normalize(identity)
        if key and key in index:
            return index[key]
    return None


def _load_image(path: Path | None) -> pygame.Surface | None:
    if path is None:
        return None
    key = str(path)
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]
    try:
        image = pygame.image.load(key).convert_alpha()
        bounds = image.get_bounding_rect(min_alpha=8)
        if bounds.width > 0 and bounds.height > 0:
            image = image.subsurface(bounds).copy()
    except (OSError, pygame.error):
        image = None
    _IMAGE_CACHE[key] = image
    return image


def _fit_image(path: Path | None, size: tuple[int, int]) -> pygame.Surface | None:
    if path is None:
        return None
    width, height = max(1, int(size[0])), max(1, int(size[1]))
    cache_key = (str(path), width, height)
    if cache_key in _SCALED_CACHE:
        return _SCALED_CACHE[cache_key]
    source = _load_image(path)
    if source is None or source.get_width() <= 0 or source.get_height() <= 0:
        _SCALED_CACHE[cache_key] = None
        return None
    scale = min(width / source.get_width(), height / source.get_height())
    rendered = pygame.transform.smoothscale(
        source,
        (
            max(1, int(source.get_width() * scale)),
            max(1, int(source.get_height() * scale)),
        ),
    )
    _SCALED_CACHE[cache_key] = rendered
    return rendered


def _item_name(raw_item: Any) -> str:
    if isinstance(raw_item, dict):
        return str(raw_item.get("name") or raw_item.get("title") or raw_item.get("id") or "Przedmiot")
    return str(raw_item or "Przedmiot")


def _draw_hover(screen, rect: pygame.Rect) -> None:
    if not rect.collidepoint(pygame.mouse.get_pos()):
        return
    glow = pygame.Surface(rect.size, pygame.SRCALPHA)
    glow.fill((255, 193, 72, 24))
    screen.blit(glow, rect.topleft)
    pygame.draw.rect(screen, (236, 180, 76), rect, 2, border_radius=4)


def _draw_quantity(screen, board, rect: pygame.Rect, amount: Any) -> None:
    try:
        value = int(amount)
    except (TypeError, ValueError):
        return
    if value <= 1:
        return
    font = pygame.font.SysFont("georgia", max(11, int(16 * board.height / 1080)), bold=True)
    label = font.render(str(value), True, (245, 220, 158))
    padding = max(4, int(5 * board.height / 1080))
    badge = label.get_rect(bottomright=(rect.right - padding, rect.bottom - padding)).inflate(8, 4)
    badge.clamp_ip(rect)
    backdrop = pygame.Surface(badge.size, pygame.SRCALPHA)
    backdrop.fill((8, 7, 6, 190))
    screen.blit(backdrop, badge.topleft)
    screen.blit(label, label.get_rect(center=badge.center))


def _draw_item(screen, board, rect: pygame.Rect, raw_item: Any, *, amount: Any = None, font_size: int = 11) -> None:
    if raw_item is None:
        return
    margin = max(5, int(7 * board.height / 1080))
    target = rect.inflate(-margin * 2, -margin * 2)
    image = _fit_image(_item_image_path(raw_item), target.size)
    if image is not None:
        screen.blit(image, image.get_rect(center=target.center))
    else:
        text = _item_name(raw_item)
        if amount not in (None, 1, "1"):
            text = f"{text} x{amount}"
        _ORIGINAL_DRAW_SLOT_TEXT(screen, board, rect, text, font_size=font_size)
    _draw_quantity(screen, board, rect, amount)
    _draw_hover(screen, rect)


def _remember_clickable(kind: str, index: int, rect: pygame.Rect) -> None:
    _CURRENT_CLICKABLES.append((str(kind), int(index), pygame.Rect(rect)))


def _equipment_items(hero: dict[str, Any]) -> list[Any]:
    ensure_equipment_state(hero)
    return [hero.get("equipment", {}).get(slot) for slot in EQUIPMENT_SLOTS]


def _backpack_items(hero: dict[str, Any]) -> list[Any]:
    ensure_equipment_state(hero)
    return list(hero.get("inventory", []) or [])


def _material_items(hero: dict[str, Any]) -> list[tuple[str, Any]]:
    materials = hero.get("materials", {})
    if isinstance(materials, dict):
        return [(str(name), amount) for name, amount in materials.items()]
    if isinstance(materials, (list, tuple)):
        return list(Counter(_item_name(item) for item in materials).items())
    return []


def _draw_equipment(screen, board, hero, layout=None):
    layout = _item_layout(board)
    for index, (rect, raw_item) in enumerate(zip(layout["equipment_slots"], _equipment_items(hero))):
        if raw_item:
            _draw_item(screen, board, rect, raw_item)
            _remember_clickable("equipment", index, rect)


def _draw_helpers(screen, board, hero, layout=None):
    layout = _item_layout(board)
    helpers = list(hero.get("helpers", []) or [])[: len(layout["helper_slots"])]
    for index, (rect, helper) in enumerate(zip(layout["helper_slots"], helpers)):
        _draw_item(screen, board, rect, helper, font_size=10)
        _remember_clickable("helper", index, rect)


def _draw_backpack(screen, board, hero, layout=None):
    layout = _item_layout(board)
    items = _backpack_items(hero)[: len(layout["backpack_slots"])]
    for index, (rect, raw_item) in enumerate(zip(layout["backpack_slots"], items)):
        _draw_item(screen, board, rect, raw_item, font_size=9)
        _remember_clickable("backpack", index, rect)


def _draw_materials(screen, board, hero, layout=None):
    layout = _item_layout(board)
    slots = layout.get("material_slots", [])
    items = _material_items(hero)[: len(slots)]
    for index, (rect, (name, amount)) in enumerate(zip(slots, items)):
        raw_item = {"name": name, "category": "material", "amount": amount}
        _draw_item(screen, board, rect, raw_item, amount=amount, font_size=9)
        _remember_clickable("material", index, rect)


def _draw_food(screen, board, hero, layout=None):
    # planszetka_gracza/1.png nie ma osobnej sekcji żywności. Nie kasujemy
    # danych z bohatera; po prostu nie rysujemy starej tekstowej nakładki na
    # nowych polach Materiałów.
    return None


def _close_player_board():
    global _OPEN_ITEM_DETAILS
    _OPEN_ITEM_DETAILS = None
    return _ORIGINAL_CLOSE_PLAYER_BOARD()


def _draw_player_board(screen, hero):
    global _CURRENT_CLICKABLES, _LAST_CLICKABLES, _LAST_BOARD, _LAST_HERO

    _CURRENT_CLICKABLES = []
    controls = _ORIGINAL_DRAW_PLAYER_BOARD(screen, hero)
    _LAST_CLICKABLES = list(_CURRENT_CLICKABLES)
    _LAST_HERO = hero

    layout = controls.get("layout") or {}
    board = layout.get("board")
    _LAST_BOARD = pygame.Rect(board) if board is not None else None
    if _LAST_BOARD is not None:
        visual_layout = _item_layout(_LAST_BOARD)
        for key in ("equipment_slots", "helper_slots", "backpack_slots", "material_slots", "backpack", "materials"):
            layout[key] = visual_layout[key]
        hitboxes = controls.setdefault("hitboxes", {})
        hitboxes["equipment_slots"] = visual_layout["equipment_slots"]
        hitboxes["helper_slots"] = visual_layout["helper_slots"]
        hitboxes["backpack_slots"] = visual_layout["backpack_slots"]
        hitboxes["material_slots"] = visual_layout["material_slots"]
        hitboxes["materials"] = visual_layout["materials"]
    controls["item_buttons"] = [
        {
            "kind": kind,
            "index": index,
            "rect": pygame.Rect(rect),
            "action": f"board_item:{kind}:{index}",
        }
        for kind, index, rect in _LAST_CLICKABLES
    ]
    return controls


def _resolve_selected(hero: dict[str, Any]) -> dict[str, Any] | None:
    if _OPEN_ITEM_DETAILS is None:
        return None
    kind, index = _OPEN_ITEM_DETAILS

    if kind == "equipment":
        items = _equipment_items(hero)
        if 0 <= index < len(items) and items[index]:
            raw = items[index]
            item = normalise_item(raw)
            item["_ui_source"] = f"Ekwipunek · {_SLOT_LABELS.get(EQUIPMENT_SLOTS[index], EQUIPMENT_SLOTS[index])}"
            return item
        return None

    if kind == "backpack":
        items = _backpack_items(hero)
        if 0 <= index < len(items):
            item = normalise_item(items[index])
            item["_ui_source"] = "Plecak"
            return item
        return None

    if kind == "helper":
        helpers = list(hero.get("helpers", []) or [])
        if 0 <= index < len(helpers):
            raw = helpers[index]
            item = dict(raw) if isinstance(raw, dict) else {"name": str(raw)}
            item["_ui_source"] = "Pomocnik"
            return item
        return None

    if kind == "material":
        materials = _material_items(hero)
        if 0 <= index < len(materials):
            name, amount = materials[index]
            return {
                "name": name,
                "category": "material",
                "amount": amount,
                "description": f"Posiadana ilość: {amount}.",
                "_ui_source": "Materiały",
            }
    return None


def _detail_lines(item: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    description = item.get("description") or item.get("effect") or item.get("text") or item.get("flavor")
    if description:
        lines.append(str(description))

    quality = item.get("quality")
    category = item.get("category")
    meta = []
    if category and str(category) not in {"misc", "material"}:
        meta.append(f"Typ: {category}")
    if quality and str(quality) not in {"zwykla", "zwykly", "common"}:
        meta.append(f"Jakość: {quality}")
    if item.get("amount") is not None:
        meta.append(f"Ilość: {item.get('amount')}")
    if item.get("price"):
        meta.append(f"Wartość bazowa: {item.get('price')} złota")
    if meta:
        lines.append(" · ".join(meta))

    bonuses = []
    hit_bonus = int(item.get("hit_bonus", 0) or 0)
    damage_bonus = int(item.get("damage_bonus", 0) or 0)
    armor_class = int(item.get("armor_class", 0) or 0)
    if hit_bonus:
        bonuses.append(f"trafienie {hit_bonus:+d}")
    if damage_bonus:
        bonuses.append(f"obrażenia {damage_bonus:+d}")
    if armor_class:
        bonuses.append(f"KP {armor_class}")
    for stat, value in (item.get("stat_bonus") or {}).items():
        value = int(value or 0)
        if value:
            bonuses.append(f"{stat} {value:+d}")
    if bonuses:
        lines.append("Premie: " + ", ".join(bonuses))

    effects = item.get("effects") or {}
    if effects:
        rendered = ", ".join(f"{key}: {value}" for key, value in effects.items())
        lines.append("Efekty: " + rendered)
    return lines or ["Brak dodatkowego opisu."]


def _draw_item_details(screen, hero: dict[str, Any], board: pygame.Rect) -> pygame.Rect | None:
    global _OPEN_ITEM_DETAILS

    item = _resolve_selected(hero)
    if item is None:
        _OPEN_ITEM_DETAILS = None
        return None

    from rg_ui import player_board

    panel = _relative_rect(board, 0.285, 0.205, 0.435, 0.455)
    shadow = pygame.Surface(panel.size, pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 220))
    screen.blit(shadow, panel.topleft)
    pygame.draw.rect(screen, (24, 20, 16), panel, border_radius=12)
    pygame.draw.rect(screen, (203, 147, 52), panel, max(2, int(3 * board.height / 1080)), border_radius=12)

    pad = max(16, int(22 * board.height / 1080))
    image_rect = pygame.Rect(panel.x + pad, panel.y + pad * 2, int(panel.width * 0.30), panel.height - pad * 4)
    image = _fit_image(_item_image_path(item), image_rect.size)
    if image is not None:
        screen.blit(image, image.get_rect(center=image_rect.center))
    else:
        pygame.draw.rect(screen, (13, 12, 10), image_rect, border_radius=8)
        pygame.draw.rect(screen, (115, 86, 42), image_rect, 1, border_radius=8)

    title_font = player_board._font(board, 24, bold=True)
    source_font = player_board._font(board, 12, bold=True)
    body_font = player_board._font(board, 13)
    title_x = image_rect.right + pad
    text_width = panel.right - pad - title_x

    title = _item_name(item)
    player_board._draw_text(screen, title_font, player_board._shorten(title_font, title, text_width), (title_x, panel.y + pad), (238, 204, 133), shadow=True)
    source = str(item.get("_ui_source") or "Przedmiot")
    player_board._draw_text(screen, source_font, source, (title_x, panel.y + pad + title_font.get_height() + 4), (177, 155, 112), shadow=False)

    y = panel.y + pad + title_font.get_height() + source_font.get_height() + 18
    max_y = panel.bottom - pad * 2
    for paragraph in _detail_lines(item):
        for line in player_board._wrap(body_font, paragraph, text_width):
            if y + body_font.get_height() > max_y:
                break
            player_board._draw_text(screen, body_font, line, (title_x, y), (224, 214, 192), shadow=False)
            y += body_font.get_height() + 4
        y += 7
        if y >= max_y:
            break

    close_size = max(34, int(42 * board.height / 1080))
    close_rect = pygame.Rect(panel.right - close_size - 10, panel.y + 10, close_size, close_size)
    hovered = close_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, (75, 58, 34) if hovered else (42, 34, 25), close_rect, border_radius=6)
    pygame.draw.rect(screen, (203, 147, 52), close_rect, 2, border_radius=6)
    x_font = player_board._font(board, 18, bold=True)
    player_board._draw_text(screen, x_font, "×", close_rect.center, (236, 208, 150), anchor="center", shadow=False)
    return close_rect


def _button_clicked(self, pos):
    global _OPEN_ITEM_DETAILS

    action = str(getattr(self, "action", ""))
    if action.startswith("board_item:") and self.rect.collidepoint(pos):
        parts = action.split(":", 2)
        if len(parts) == 3:
            try:
                index = int(parts[2])
            except (TypeError, ValueError):
                return False
            _OPEN_ITEM_DETAILS = (parts[1], index)
            return True
    if action == "close_board_item" and self.rect.collidepoint(pos):
        _OPEN_ITEM_DETAILS = None
        return True

    clicked = _ORIGINAL_BUTTON_CLICKED(self, pos)
    if clicked and action == "close_player_board":
        _OPEN_ITEM_DETAILS = None
    return clicked


def _draw_game_ui(*args, **kwargs):
    result = list(_ORIGINAL_DRAW_GAME_UI(*args, **kwargs) or [])

    from rg_ui import hud, player_board

    if not player_board.is_player_board_open():
        return result

    screen = kwargs.get("screen")
    if screen is None and args:
        screen = args[0]
    hero = kwargs.get("hero")
    if hero is None and len(args) >= 4:
        hero = args[3]
    hero = hero or _LAST_HERO or {}

    extras = []
    if not player_board.is_quest_details_open():
        extras = [
            hud._PlayerBoardButton("", f"board_item:{kind}:{index}", rect)
            for kind, index, rect in _LAST_CLICKABLES
        ]

    if _OPEN_ITEM_DETAILS is not None and screen is not None and _LAST_BOARD is not None and not player_board.is_quest_details_open():
        close_rect = _draw_item_details(screen, hero, _LAST_BOARD)
        if close_rect is not None:
            extras.append(hud._PlayerBoardButton("", "close_board_item", close_rect))

        # Modal opisu ma pierwszeństwo nad questami i ich zakładkami. Pozostawiamy
        # tylko hitboxy przedmiotów (żeby można było przejść do innego opisu),
        # zamknięcie opisu, powrót z planszetki i końcowy blocker planszy.
        allowed = {"close_player_board", "player_board_block"}
        result = [
            button
            for button in result
            if str(getattr(button, "action", "")) in allowed
        ]

    if result and str(getattr(result[-1], "action", "")) == "player_board_block":
        return [*result[:-1], *extras, result[-1]]
    return [*result, *extras]


def is_item_details_open() -> bool:
    return _OPEN_ITEM_DETAILS is not None


def close_item_details() -> bool:
    global _OPEN_ITEM_DETAILS
    was_open = _OPEN_ITEM_DETAILS is not None
    _OPEN_ITEM_DETAILS = None
    return was_open


def install_player_board_items() -> None:
    global _INSTALLED
    global _ORIGINAL_FIND_BOARD_PATH, _ORIGINAL_PLAYER_BOARD_LAYOUT
    global _ORIGINAL_DRAW_PLAYER_BOARD, _ORIGINAL_CLOSE_PLAYER_BOARD
    global _ORIGINAL_BUTTON_CLICKED, _ORIGINAL_DRAW_GAME_UI, _ORIGINAL_DRAW_SLOT_TEXT

    if _INSTALLED:
        return

    from rg_ui import hud, player_board

    _ORIGINAL_FIND_BOARD_PATH = player_board._find_board_path
    _ORIGINAL_PLAYER_BOARD_LAYOUT = player_board.player_board_layout
    _ORIGINAL_DRAW_PLAYER_BOARD = player_board.draw_player_board
    _ORIGINAL_CLOSE_PLAYER_BOARD = player_board.close_player_board
    _ORIGINAL_DRAW_SLOT_TEXT = player_board._draw_slot_text
    _ORIGINAL_BUTTON_CLICKED = hud._PlayerBoardButton.clicked
    _ORIGINAL_DRAW_GAME_UI = hud.draw_game_ui

    player_board._find_board_path = _find_board_path
    player_board._draw_equipment = _draw_equipment
    player_board._draw_helpers = _draw_helpers
    player_board._draw_backpack = _draw_backpack
    player_board._draw_materials = _draw_materials
    player_board._draw_food = _draw_food
    player_board.close_player_board = _close_player_board
    player_board.draw_player_board = _draw_player_board

    # hud.py importuje funkcje z player_board bezpośrednio, dlatego podmieniamy
    # również jego referencje po zainstalowanych wcześniej wrapperach Questów.
    hud.close_player_board = _close_player_board
    hud.draw_player_board = _draw_player_board
    hud._PlayerBoardButton.clicked = _button_clicked
    hud.draw_game_ui = _draw_game_ui

    # Wymuszamy ponowne wyszukanie tła, żeby nowy plik 1.png wygrał ze starym
    # assetem nawet jeżeli planszetkę zdążono już wcześniej otworzyć.
    player_board._BOARD_SOURCE = None
    player_board._BOARD_PATH = None
    player_board._BOARD_SEARCHED = False
    player_board._SCALED_CACHE.clear()

    _INSTALLED = True
