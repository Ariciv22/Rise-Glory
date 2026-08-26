from __future__ import annotations

from pathlib import Path

import pygame


ROOT_DIR = Path(__file__).resolve().parents[1]
GRAPHICS_DIR = ROOT_DIR / "Grafiki"

# Kazdy wariant ma dwa spojne assety:
# - portrait: postac bez podstawki, uzywana na planszetce/kartcie bohatera,
# - token: ta sama postac z podstawka, uzywana jako pionek na mapie.
FIGURE_VARIANTS = {
    1: [
        {
            "id": "wojownik",
            "name": "Wojownik",
            "portrait": "figurki_bohaterow/Walka/wojownik.png",
            "token": "figurki_bohaterow/Walka/wojownik_podstawka_kolor.png",
        },
        {
            "id": "wojowniczka",
            "name": "Wojowniczka",
            "portrait": "figurki_bohaterow/Walka/wojowniczka_kolor.png",
            "token": "figurki_bohaterow/Walka/wojowniczka_podstawka_kolor.png",
        },
    ],
    2: [
        {
            "id": "handlarz",
            "name": "Handlarz",
            "portrait": "figurki_bohaterow/handel/handlarz.png",
            "token": "figurki_bohaterow/handel/handlarz_podstawka.png",
        },
        {
            "id": "handlarka",
            "name": "Handlarka",
            "portrait": "figurki_bohaterow/handel/handlarka.png",
            "token": "figurki_bohaterow/handel/handlarka_podstawka_kolor.png",
        },
    ],
    3: [
        {
            "id": "dyplomata",
            "name": "Dyplomata",
            "portrait": "figurki_bohaterow/Dyplomacja/dyplomata.png",
            "token": "figurki_bohaterow/Dyplomacja/dyplomata_podstawka.png",
        },
        {
            "id": "dyplomatka",
            "name": "Dyplomatka",
            "portrait": "figurki_bohaterow/Dyplomacja/dyplomatka.png",
            "token": "figurki_bohaterow/Dyplomacja/dyplomatka_podstawka.png",
        },
    ],
    4: [
        {
            "id": "muzykant",
            "name": "Muzykant",
            "portrait": "figurki_bohaterow/kultura/muzykant.png",
            "token": "figurki_bohaterow/kultura/muzykant_podstawka.png",
        },
        {
            "id": "muzykantka",
            "name": "Muzykantka",
            "portrait": "figurki_bohaterow/kultura/Muzykantka.png",
            "token": "figurki_bohaterow/kultura/Muzykantka_podstawka_kolor.png",
        },
    ],
    5: [
        {
            "id": "intrygant",
            "name": "Intrygant",
            "portrait": "figurki_bohaterow/intryga/intrygant.png",
            "token": "figurki_bohaterow/intryga/intrygant_podstawka.png",
        },
        {
            "id": "intrygantka",
            "name": "Intrygantka",
            "portrait": "figurki_bohaterow/intryga/intrygantka.png",
            "token": "figurki_bohaterow/intryga/intrygantka_podstawka_kolor.png",
        },
    ],
    6: [
        {
            "id": "uczony",
            "name": "Uczony",
            "portrait": "figurki_bohaterow/nauka/uczony.png",
            "token": "figurki_bohaterow/nauka/uczony_podstawka_kolor.png",
        },
    ],
}

_SELECTED_VARIANT = {}
_IMAGE_CACHE = {}
_SCALED_CACHE = {}
_INSTALLED = False
_ORIGINAL_TOKEN_DRAW = None
_ORIGINAL_CLONE_HERO = None
_ORIGINAL_PLAYER_CONFIG = None
_ORIGINAL_CUSTOM_HERO = None
_ORIGINAL_PLAYER_BOARD = None


def _archetype_id(value):
    if isinstance(value, dict):
        value = value.get("archetype_id", value.get("id"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def variants_for(value):
    return FIGURE_VARIANTS.get(_archetype_id(value), [])


def selected_variant(value):
    archetype_id = _archetype_id(value)
    variants = FIGURE_VARIANTS.get(archetype_id, [])
    if not variants:
        return None

    preferred = None
    if isinstance(value, dict):
        preferred = value.get("figure_id")
    selected_id = preferred or _SELECTED_VARIANT.get(archetype_id)
    for variant in variants:
        if variant["id"] == selected_id:
            return variant
    return variants[0]


def choose_variant(archetype_id, variant_id):
    archetype_id = _archetype_id(archetype_id)
    variants = FIGURE_VARIANTS.get(archetype_id, [])
    if any(variant["id"] == variant_id for variant in variants):
        _SELECTED_VARIANT[archetype_id] = variant_id
        return True
    return False


def _apply_variant(hero, source=None):
    variant = selected_variant(source or hero)
    if variant is None:
        return hero
    hero["figure_id"] = variant["id"]
    hero["figure_name"] = variant["name"]
    hero["figure_portrait"] = variant["portrait"]
    hero["figure_token"] = variant["token"]
    return hero


def _trim_alpha(image):
    bounds = image.get_bounding_rect(min_alpha=8)
    if bounds.width <= 0 or bounds.height <= 0:
        return image
    bounds = bounds.inflate(6, 6).clip(image.get_rect())
    return image.subsurface(bounds).copy()


def _load_image(relative_path):
    key = str(relative_path or "")
    if not key:
        return None
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]

    path = GRAPHICS_DIR / key
    if not path.is_file():
        _IMAGE_CACHE[key] = None
        return None
    try:
        image = pygame.image.load(str(path)).convert_alpha()
        image = _trim_alpha(image)
    except (OSError, pygame.error):
        image = None
    _IMAGE_CACHE[key] = image
    return image


def _fit_image(relative_path, max_size):
    max_width, max_height = max(1, int(max_size[0])), max(1, int(max_size[1]))
    cache_key = (str(relative_path or ""), max_width, max_height)
    if cache_key in _SCALED_CACHE:
        return _SCALED_CACHE[cache_key]

    source = _load_image(relative_path)
    if source is None:
        _SCALED_CACHE[cache_key] = None
        return None
    width, height = source.get_size()
    if width <= 0 or height <= 0:
        _SCALED_CACHE[cache_key] = None
        return None
    scale = min(max_width / width, max_height / height)
    size = (max(1, int(width * scale)), max(1, int(height * scale)))
    image = pygame.transform.smoothscale(source, size)
    _SCALED_CACHE[cache_key] = image
    return image


class FigureChoiceButton:
    """Przycisk wyboru wygladu bez zmian w glownej petli app.py.

    app.py traktuje go jak zwykly Button. Klikniecie zapisuje wariant tutaj,
    a nieznana dla app.py akcja jest celowo nieszkodliwa.
    """

    def __init__(self, archetype_id, variant, rect):
        self.text = ""
        self.action = f"figure_choice:{variant['id']}"
        self.rect = pygame.Rect(rect)
        self.archetype_id = int(archetype_id)
        self.variant = variant

    def clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        choose_variant(self.archetype_id, self.variant["id"])
        return True


def _draw_choice_button(screen, button, mouse):
    selected = selected_variant(button.archetype_id)
    active = bool(selected and selected["id"] == button.variant["id"])
    hovered = button.rect.collidepoint(mouse)

    fill = (52, 43, 31) if active else ((44, 39, 32) if hovered else (27, 25, 22))
    pygame.draw.rect(screen, fill, button.rect, border_radius=8)
    border = (214, 165, 77) if active else ((181, 139, 68) if hovered else (105, 86, 55))
    pygame.draw.rect(screen, border, button.rect, 2 if not active else 3, border_radius=8)

    preview_width = min(42, max(28, button.rect.width // 3))
    preview = _fit_image(button.variant["portrait"], (preview_width, button.rect.height - 8))
    text_left = button.rect.x + 8
    if preview is not None:
        preview_rect = preview.get_rect(midleft=(button.rect.x + 5, button.rect.centery))
        screen.blit(preview, preview_rect)
        text_left = preview_rect.right + 4

    font_size = 13 if button.rect.width >= 125 else 11
    label_font = pygame.font.SysFont("georgia", font_size, bold=True)
    label = label_font.render(button.variant["name"], True, (226, 210, 178))
    max_text_width = max(20, button.rect.right - text_left - 5)
    if label.get_width() > max_text_width:
        text = button.variant["name"]
        while len(text) > 4 and label_font.size(text + "...")[0] > max_text_width:
            text = text[:-1]
        label = label_font.render(text.rstrip() + "...", True, (226, 210, 178))
    screen.blit(label, label.get_rect(midleft=(text_left, button.rect.centery)))


def _draw_selector(screen, mouse, archetype, area, title="Wybierz figurke"):
    variants = variants_for(archetype)
    if not variants:
        return []

    area = pygame.Rect(area)
    title_font = pygame.font.SysFont("georgia", 14, bold=True)
    title_surface = title_font.render(title, True, (229, 208, 164))
    screen.blit(title_surface, (area.x, area.y))

    y = area.y + 22
    gap = 7
    count = len(variants)
    usable_width = max(1, area.width - gap * (count - 1))
    button_width = max(82, usable_width // count)
    button_height = max(42, min(62, area.height - 24))
    buttons = []
    for index, variant in enumerate(variants):
        rect = pygame.Rect(area.x + index * (button_width + gap), y, button_width, button_height)
        if rect.right > area.right:
            rect.right = area.right
        button = FigureChoiceButton(_archetype_id(archetype), variant, rect)
        _draw_choice_button(screen, button, mouse)
        buttons.append(button)
    return buttons


def _clone_hero_with_figure(template, world_name=None, player_index=0, stats=None):
    hero = _ORIGINAL_CLONE_HERO(template, world_name=world_name, player_index=player_index, stats=stats)
    return _apply_variant(hero, template)


def _draw_token_with_figure(token, screen, camera, font, selected=False):
    relative_path = token.hero.get("figure_token")
    source = _load_image(relative_path)
    if source is None:
        return _ORIGINAL_TOKEN_DRAW(token, screen, camera, font, selected=selected)

    sx, sy = token.tile.center(camera)
    max_width = max(46, int(108 * camera.zoom))
    max_height = max(64, int(132 * camera.zoom))
    rendered = _fit_image(relative_path, (max_width, max_height))
    if rendered is None:
        return _ORIGINAL_TOKEN_DRAW(token, screen, camera, font, selected=selected)

    base_y = int(sy + 58 * camera.zoom)
    rect = rendered.get_rect(midbottom=(int(sx), base_y))
    player_color = token.hero.get("player_color", token.hero.get("color", (220, 220, 220)))

    ring_width = max(26, int(58 * camera.zoom))
    ring_height = max(9, int(16 * camera.zoom))
    ring = pygame.Rect(0, 0, ring_width, ring_height)
    ring.midbottom = (int(sx), base_y + max(1, int(2 * camera.zoom)))
    pygame.draw.ellipse(screen, (20, 18, 15), ring.inflate(max(3, int(6 * camera.zoom)), max(2, int(4 * camera.zoom))))
    pygame.draw.ellipse(screen, player_color, ring, max(2, int(3 * camera.zoom)))

    screen.blit(rendered, rect)
    if selected:
        selected_ring = ring.inflate(max(8, int(16 * camera.zoom)), max(5, int(10 * camera.zoom)))
        pygame.draw.ellipse(screen, (120, 210, 255), selected_ring, max(2, int(4 * camera.zoom)))


def _draw_player_config_with_figures(
    screen,
    title_font,
    font,
    small_font,
    mouse,
    player_index,
    player_count,
    world_name,
    selected_archetype,
    used_archetypes,
):
    buttons = _ORIGINAL_PLAYER_CONFIG(
        screen,
        title_font,
        font,
        small_font,
        mouse,
        player_index,
        player_count,
        world_name,
        selected_archetype,
        used_archetypes,
    )
    if not selected_archetype:
        return buttons

    width, height = screen.get_size()
    compact = height < 1050
    field_y = 300 if compact else 330
    field_width = min(540, max(420, width - 540))
    field_right = int(width / 2 + field_width / 2)
    area_x = field_right + 22
    area_width = width - area_x - 22

    if area_width < 190:
        area_width = min(360, width - 40)
        area_x = (width - area_width) // 2
        area_y = field_y - 92
    else:
        area_y = field_y - 24

    area = pygame.Rect(area_x, area_y, area_width, 86)
    buttons.extend(_draw_selector(screen, mouse, selected_archetype, area, title="Figurka bohatera"))
    return buttons


def _draw_custom_hero_with_figures(
    screen,
    title_font,
    font,
    small_font,
    mouse,
    player_index,
    world_name,
    selected_set,
    stats,
):
    buttons = _ORIGINAL_CUSTOM_HERO(
        screen,
        title_font,
        font,
        small_font,
        mouse,
        player_index,
        world_name,
        selected_set,
        stats,
    )
    if not selected_set:
        return buttons

    from rg_ui import screens

    compact = screen.get_height() < 1050
    panel = screens._start_set_panel_rect(compact)
    footer_height = min(86, max(70, screen.get_height() - panel.bottom - 8))
    area = pygame.Rect(panel.x + 2, panel.bottom + 6, panel.width - 4, footer_height)
    buttons.extend(_draw_selector(screen, mouse, selected_set, area, title="Wyglad figurki"))
    return buttons


def _draw_player_board_with_figure(screen, hero):
    controls = _ORIGINAL_PLAYER_BOARD(screen, hero)

    from rg_ui import player_board

    if player_board.is_quest_details_open():
        return controls
    relative_path = hero.get("figure_portrait")
    if not relative_path:
        return controls
    source = player_board._load_board_source()
    if source is None:
        return controls
    board = player_board._board_rect(screen, source)

    # Wolne pole pomiedzy statystykami po lewej i ekwipunkiem po prawej.
    target = pygame.Rect(
        int(board.x + board.width * 0.270),
        int(board.y + board.height * 0.075),
        max(1, int(board.width * 0.165)),
        max(1, int(board.height * 0.510)),
    )
    rendered = _fit_image(relative_path, target.size)
    if rendered is None:
        return controls
    rect = rendered.get_rect(midbottom=(target.centerx, target.bottom))
    screen.blit(rendered, rect)
    return controls


def install_hero_figure_system(app_module):
    global _INSTALLED
    global _ORIGINAL_TOKEN_DRAW, _ORIGINAL_CLONE_HERO
    global _ORIGINAL_PLAYER_CONFIG, _ORIGINAL_CUSTOM_HERO, _ORIGINAL_PLAYER_BOARD

    if _INSTALLED:
        return

    from rg_core import setup
    from rg_world import map as world_map
    from rg_ui import hud, player_board

    _ORIGINAL_CLONE_HERO = setup.clone_hero
    setup.clone_hero = _clone_hero_with_figure

    _ORIGINAL_TOKEN_DRAW = world_map.HeroToken.draw
    world_map.HeroToken.draw = _draw_token_with_figure

    _ORIGINAL_PLAYER_CONFIG = app_module.draw_player_config
    app_module.draw_player_config = _draw_player_config_with_figures

    _ORIGINAL_CUSTOM_HERO = app_module.draw_custom_hero
    app_module.draw_custom_hero = _draw_custom_hero_with_figures

    _ORIGINAL_PLAYER_BOARD = player_board.draw_player_board
    player_board.draw_player_board = _draw_player_board_with_figure
    # hud.py importuje funkcje bezposrednio, wiec aktualizujemy tez jego referencje.
    hud.draw_player_board = _draw_player_board_with_figure

    _INSTALLED = True
