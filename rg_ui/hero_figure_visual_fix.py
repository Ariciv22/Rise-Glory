from __future__ import annotations

import sys

import pygame

from rg_ui import hero_figure_system as figures


_INSTALLED = False
_ORIGINAL_FIGURE_LOAD = figures._load_image
_CLEAN_FIGURE_CACHE = {}


def _is_opaque_dark(color, threshold=44):
    return color.a > 8 and max(color.r, color.g, color.b) <= threshold


def _remove_connected_dark_canvas(image):
    """Usuwa tylko ciemne tlo polaczone z krawedzia obrazu.

    Nie wycinamy wszystkich czarnych pikseli globalnie, bo postacie maja
    czarne ubrania, wlosy i cienie. Usuwany jest wylacznie ciemny komponent
    tla dochodzacy do brzegu PNG.
    """
    if image is None:
        return None

    cleaned = image.copy().convert_alpha()
    width, height = cleaned.get_size()
    if width <= 2 or height <= 2:
        return cleaned

    corners = [
        cleaned.get_at((0, 0)),
        cleaned.get_at((width - 1, 0)),
        cleaned.get_at((0, height - 1)),
        cleaned.get_at((width - 1, height - 1)),
    ]
    if sum(_is_opaque_dark(color) for color in corners) < 2:
        return cleaned

    try:
        dark = pygame.mask.from_threshold(
            cleaned,
            (0, 0, 0, 255),
            (44, 44, 44, 255),
        )
        background = pygame.mask.Mask((width, height), fill=False)

        # Zwykle caly czarny canvas jest jednym komponentem. Probkujemy jednak
        # cala krawedz, aby dzialalo rowniez przy przerwanych rogach.
        step = max(4, min(width, height) // 48)
        edge_points = []
        for x in range(0, width, step):
            edge_points.append((x, 0))
            edge_points.append((x, height - 1))
        for y in range(0, height, step):
            edge_points.append((0, y))
            edge_points.append((width - 1, y))
        edge_points.extend(
            [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
        )

        for point in edge_points:
            if dark.get_at(point) and not background.get_at(point):
                component = dark.connected_component(point)
                if component.count():
                    background.draw(component, (0, 0))

        if not background.count():
            return cleaned

        alpha_cut = background.to_surface(
            setcolor=(255, 255, 255, 0),
            unsetcolor=(255, 255, 255, 255),
        )
        cleaned.blit(alpha_cut, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return figures._trim_alpha(cleaned)
    except (AttributeError, TypeError, ValueError, pygame.error):
        # Fallback tylko dla ewidentnie czarnego canvasa.
        pixels = pygame.PixelArray(cleaned)
        try:
            for x in range(width):
                for y in range(height):
                    color = cleaned.unmap_rgb(pixels[x, y])
                    if color.a > 8 and max(color.r, color.g, color.b) <= 18:
                        pixels[x, y] = (0, 0, 0, 0)
        finally:
            del pixels
        return figures._trim_alpha(cleaned)


def _load_figure_without_dark_canvas(relative_path):
    key = str(relative_path or "")
    if not key:
        return None
    if key in _CLEAN_FIGURE_CACHE:
        return _CLEAN_FIGURE_CACHE[key]

    source = _ORIGINAL_FIGURE_LOAD(relative_path)
    if source is None:
        _CLEAN_FIGURE_CACHE[key] = None
        return None

    cleaned = _remove_connected_dark_canvas(source)
    _CLEAN_FIGURE_CACHE[key] = cleaned
    return cleaned


def _union_rects(rects):
    rects = [pygame.Rect(rect) for rect in rects if rect is not None]
    if not rects:
        return None
    result = rects[0].copy()
    for rect in rects[1:]:
        result.union_ip(rect)
    return result


def _draw_panel_asset(screen, rect, active=False, hovered=False):
    """Panel figurki korzysta z tego samego panel2.png co reszta wyboru."""
    from rg_ui import screens

    rect = pygame.Rect(rect)
    texture = screens._load_menu_button_texture(rect.size)
    if texture is not None:
        shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 72))
        screen.blit(shadow, rect.move(3, 4))
        screen.blit(texture, rect)
    else:
        # Awaryjnie korzystamy ze wspolnego renderera paneli UI.
        from rg_ui.common import draw_image_panel

        draw_image_panel(screen, rect, 2)

    if hovered or active:
        glow = pygame.Surface(rect.size, pygame.SRCALPHA)
        glow.fill((255, 220, 120, 22 if hovered and not active else 34))
        screen.blit(glow, rect)

    if active:
        # To tylko stan zaznaczenia; sama ramka nadal pochodzi z assetu panel2.
        pygame.draw.rect(screen, (225, 174, 78), rect, 2, border_radius=7)


def _draw_figure_card(screen, card, variant, active, hovered):
    card = pygame.Rect(card)
    _draw_panel_asset(screen, card, active=active, hovered=hovered)

    label_font = pygame.font.SysFont(
        "georgia",
        15 if card.width >= 145 else 12,
        bold=True,
    )
    label_shadow = label_font.render(variant["name"], True, (24, 18, 12))
    label = label_font.render(
        variant["name"],
        True,
        (247, 225, 178) if active or hovered else (224, 207, 173),
    )
    label_center = (card.centerx, card.y + min(28, max(20, card.height // 12)))
    screen.blit(
        label_shadow,
        label_shadow.get_rect(center=(label_center[0] + 1, label_center[1] + 2)),
    )
    screen.blit(label, label.get_rect(center=label_center))

    # Pelna sylwetka. Nie ma osobnego czarnego prostokata obrazu:
    # przezroczysta postac lezy bezposrednio na teksturze panelu UI.
    top_pad = max(42, int(card.height * 0.10))
    image_area = pygame.Rect(
        card.x + 14,
        card.y + top_pad,
        max(1, card.width - 28),
        max(1, card.height - top_pad - 16),
    )
    portrait = figures._fit_image(variant["portrait"], image_area.size)
    if portrait is None:
        return

    portrait_rect = portrait.get_rect(midbottom=(image_area.centerx, image_area.bottom))
    screen.blit(portrait, portrait_rect)


def _draw_full_figure_selector(screen, mouse, archetype, area, title="Wybierz figurke"):
    variants = figures.variants_for(archetype)
    if not variants:
        return []

    area = pygame.Rect(area).clip(screen.get_rect())
    if area.width < 70 or area.height < 90:
        return []

    title_font = pygame.font.SysFont("georgia", 14, bold=True)
    title_shadow = title_font.render(title, True, (35, 27, 18))
    title_surface = title_font.render(title, True, (235, 213, 169))
    title_pos = (area.x, area.y)
    screen.blit(title_shadow, (title_pos[0] + 1, title_pos[1] + 2))
    screen.blit(title_surface, title_pos)

    top = area.y + 24
    usable_height = area.bottom - top
    if usable_height < 60:
        return []

    gap = 8
    count = len(variants)
    usable_width = area.width - gap * (count - 1)

    if count == 1:
        card_width = min(260, usable_width)
        start_x = area.centerx - card_width // 2
    else:
        card_width = max(1, usable_width // count)
        start_x = area.x

    buttons = []
    selected = figures.selected_variant(archetype)
    selected_id = selected["id"] if selected else None

    for index, variant in enumerate(variants):
        x = start_x + index * (card_width + gap)
        card = pygame.Rect(x, top, card_width, usable_height)
        if card.right > area.right:
            card.width = max(1, area.right - card.x)
        if card.width < 36:
            continue

        button = figures.FigureChoiceButton(
            figures._archetype_id(archetype),
            variant,
            card,
        )
        active = variant["id"] == selected_id
        hovered = card.collidepoint(mouse)
        _draw_figure_card(screen, card, variant, active, hovered)
        buttons.append(button)

    return buttons


def _player_selector_area(screen, buttons):
    """Znajduje wolna kolumne obok kart klas i konczy ja przed akcjami."""
    sw, sh = screen.get_size()
    class_rects = [
        button.rect
        for button in buttons
        if str(getattr(button, "action", "")).startswith("archetype_")
    ]
    class_bounds = _union_rects(class_rects)
    if class_bounds is None:
        return pygame.Rect(max(18, sw - 300), 330, min(282, sw - 36), 330)

    action_rects = [
        button.rect
        for button in buttons
        if getattr(button, "action", "")
        in {"random_hero", "custom_hero", "confirm_player"}
    ]
    action_top = min((rect.top for rect in action_rects), default=sh - 20)

    top = max(18, class_bounds.top)
    bottom = min(sh - 18, action_top - 12)
    if bottom <= top + 90:
        bottom = min(sh - 18, class_bounds.bottom)

    margin = 16
    right_x = class_bounds.right + margin
    right_width = sw - right_x - 18
    left_x = 18
    left_width = class_bounds.left - margin - left_x

    # Wybieramy szersza faktycznie wolna strone. Nie nakladamy selektora
    # na karty klas nawet wtedy, gdy szerokosc okna jest nietypowa.
    if right_width >= left_width:
        x, width = right_x, right_width
    else:
        x, width = left_x, left_width

    width = max(0, width)
    height = max(0, bottom - top)
    return pygame.Rect(x, top, width, height).clip(screen.get_rect())


def _draw_player_config_without_overlap(
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
    buttons = figures._ORIGINAL_PLAYER_CONFIG(
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

    area = _player_selector_area(screen, buttons)
    buttons.extend(
        _draw_full_figure_selector(
            screen,
            mouse,
            selected_archetype,
            area,
            title="Figurka bohatera",
        )
    )
    return buttons


def _draw_custom_hero_without_overlap(
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
    buttons = figures._ORIGINAL_CUSTOM_HERO(
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
    area = pygame.Rect(
        panel.x,
        panel.bottom + 8,
        panel.width,
        max(0, screen.get_height() - panel.bottom - 22),
    ).clip(screen.get_rect())

    buttons.extend(
        _draw_full_figure_selector(
            screen,
            mouse,
            selected_set,
            area,
            title="Wyglad figurki",
        )
    )
    return buttons


def _draw_token_clean(token, screen, camera, font, selected=False):
    relative_path = token.hero.get("figure_token")
    source = figures._load_image(relative_path)
    if source is None:
        return figures._ORIGINAL_TOKEN_DRAW(
            token,
            screen,
            camera,
            font,
            selected=selected,
        )

    sx, sy = token.tile.center(camera)
    max_width = max(46, int(108 * camera.zoom))
    max_height = max(64, int(132 * camera.zoom))
    rendered = figures._fit_image(relative_path, (max_width, max_height))
    if rendered is None:
        return figures._ORIGINAL_TOKEN_DRAW(
            token,
            screen,
            camera,
            font,
            selected=selected,
        )

    base_y = int(sy + 58 * camera.zoom)
    rect = rendered.get_rect(midbottom=(int(sx), base_y))

    # Asset ma wlasna podstawke. Bez dodatkowej elipsy i bez okregu zaznaczenia.
    screen.blit(rendered, rect)


def install_hero_figure_visual_fix():
    global _INSTALLED
    if _INSTALLED:
        return

    from rg_core import app as app_module
    from rg_world import map as world_map

    # Najpierw usuwamy czarny canvas z figur. Cache skalowanych obrazow trzeba
    # wyczyscic, aby nie zostaly w nim stare wersje z czarnym prostokatem.
    figures._load_image = _load_figure_without_dark_canvas
    figures._IMAGE_CACHE.clear()
    figures._SCALED_CACHE.clear()

    # Finalny selector korzysta z panel2.png i pelnych sylwetek.
    figures._draw_selector = _draw_full_figure_selector

    # Nie uzywamy starego wrappera, bo jego pole wyboru bylo wyliczane
    # niezaleznie od faktycznych kart i przez to moglo na nie nachodzic.
    app_module.draw_player_config = _draw_player_config_without_overlap
    app_module.draw_custom_hero = _draw_custom_hero_without_overlap

    for module_name in ("__main__", "main"):
        module = sys.modules.get(module_name)
        if module is not None:
            if hasattr(module, "draw_player_config"):
                module.draw_player_config = _draw_player_config_without_overlap
            if hasattr(module, "draw_custom_hero"):
                module.draw_custom_hero = _draw_custom_hero_without_overlap

    world_map.HeroToken.draw = _draw_token_clean

    _INSTALLED = True
