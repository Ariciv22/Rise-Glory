from __future__ import annotations

import pygame

from rg_ui import hero_figure_system as figures


_INSTALLED = False


def _draw_corner_accents(screen, rect, color, length=12, width=2):
    """Proste ornamentowe narozniki, zeby portret mial czytelna ramke."""
    length = max(5, min(int(length), rect.width // 4, rect.height // 4))
    width = max(1, int(width))

    # lewy gorny
    pygame.draw.line(screen, color, (rect.left, rect.top), (rect.left + length, rect.top), width)
    pygame.draw.line(screen, color, (rect.left, rect.top), (rect.left, rect.top + length), width)
    # prawy gorny
    pygame.draw.line(screen, color, (rect.right - 1, rect.top), (rect.right - 1 - length, rect.top), width)
    pygame.draw.line(screen, color, (rect.right - 1, rect.top), (rect.right - 1, rect.top + length), width)
    # lewy dolny
    pygame.draw.line(screen, color, (rect.left, rect.bottom - 1), (rect.left + length, rect.bottom - 1), width)
    pygame.draw.line(screen, color, (rect.left, rect.bottom - 1), (rect.left, rect.bottom - 1 - length), width)
    # prawy dolny
    pygame.draw.line(screen, color, (rect.right - 1, rect.bottom - 1), (rect.right - 1 - length, rect.bottom - 1), width)
    pygame.draw.line(screen, color, (rect.right - 1, rect.bottom - 1), (rect.right - 1, rect.bottom - 1 - length), width)


def _draw_header(screen, rect, variant, active, hovered):
    fill = (52, 43, 31) if active else ((44, 39, 32) if hovered else (27, 25, 22))
    border = (221, 170, 76) if active else ((188, 144, 69) if hovered else (112, 91, 57))

    pygame.draw.rect(screen, fill, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 3 if active else 2, border_radius=8)

    preview_width = min(46, max(30, rect.width // 4))
    preview = figures._fit_image(variant["portrait"], (preview_width, rect.height - 8))
    text_left = rect.x + 10
    if preview is not None:
        preview_rect = preview.get_rect(midleft=(rect.x + 6, rect.centery))
        screen.blit(preview, preview_rect)
        text_left = preview_rect.right + 6

    font_size = 14 if rect.width >= 150 else 12
    label_font = pygame.font.SysFont("georgia", font_size, bold=True)
    label = label_font.render(variant["name"], True, (230, 214, 181))
    max_width = max(24, rect.right - text_left - 7)
    if label.get_width() > max_width:
        text = variant["name"]
        while len(text) > 4 and label_font.size(text + "...")[0] > max_width:
            text = text[:-1]
        label = label_font.render(text.rstrip() + "...", True, (230, 214, 181))
    screen.blit(label, label.get_rect(midleft=(text_left, rect.centery)))


def _draw_portrait_frame(screen, rect, variant, active, hovered):
    if rect.width <= 8 or rect.height <= 8:
        return

    # Lekko przyciemnione pole pozwala zachowac tlo ekranu, ale oddziela figurke.
    backdrop = pygame.Surface(rect.size, pygame.SRCALPHA)
    backdrop.fill((12, 10, 8, 74 if not active else 92))
    screen.blit(backdrop, rect.topleft)

    outer = (220, 169, 75) if active else ((184, 141, 68) if hovered else (105, 85, 53))
    inner = (92, 69, 39) if not active else (151, 109, 50)
    pygame.draw.rect(screen, outer, rect, 3 if active else 2, border_radius=5)
    inner_rect = rect.inflate(-8, -8)
    if inner_rect.width > 4 and inner_rect.height > 4:
        pygame.draw.rect(screen, inner, inner_rect, 1, border_radius=3)
    _draw_corner_accents(screen, rect, outer, length=max(9, min(18, rect.width // 9)), width=2)

    # CONTAIN, nie COVER: cala postac ma byc widoczna bez ucinania glowy, nog ani bokow.
    image_area = rect.inflate(-22, -22)
    if image_area.width <= 0 or image_area.height <= 0:
        return
    portrait = figures._fit_image(variant["portrait"], image_area.size)
    if portrait is None:
        return
    portrait_rect = portrait.get_rect(center=image_area.center)
    screen.blit(portrait, portrait_rect)


def _draw_full_figure_selector(screen, mouse, archetype, area, title="Wybierz figurke"):
    variants = figures.variants_for(archetype)
    if not variants:
        return []

    area = pygame.Rect(area)

    # Stary selector mial tylko 86 px wysokosci. Rozwijamy go do dolu ekranu,
    # zeby pod naglowkami zmiescily sie pelne pionowe grafiki postaci.
    bottom_margin = 28 if title == "Figurka bohatera" else 14
    available_height = screen.get_height() - area.y - bottom_margin
    if available_height > area.height:
        area.height = available_height

    title_font = pygame.font.SysFont("georgia", 14, bold=True)
    title_surface = title_font.render(title, True, (229, 208, 164))
    screen.blit(title_surface, (area.x, area.y))

    gap = 10
    top = area.y + 24
    usable_height = max(54, area.bottom - top)
    header_h = max(46, min(58, int(usable_height * 0.11)))
    preview_gap = 8

    count = len(variants)
    if count == 1:
        card_width = min(area.width, max(180, min(340, area.width)))
        start_x = area.centerx - card_width // 2
    else:
        card_width = max(94, (area.width - gap * (count - 1)) // count)
        start_x = area.x

    buttons = []
    selected = figures.selected_variant(archetype)
    selected_id = selected["id"] if selected else None

    for index, variant in enumerate(variants):
        x = start_x + index * (card_width + gap)
        card = pygame.Rect(x, top, card_width, usable_height)
        if card.right > area.right:
            card.right = area.right
        if card.width <= 0:
            continue

        button = figures.FigureChoiceButton(figures._archetype_id(archetype), variant, card)
        active = variant["id"] == selected_id
        hovered = card.collidepoint(mouse)

        header = pygame.Rect(card.x, card.y, card.width, min(header_h, card.height))
        _draw_header(screen, header, variant, active, hovered)

        frame_top = header.bottom + preview_gap
        frame = pygame.Rect(card.x, frame_top, card.width, max(1, card.bottom - frame_top))
        _draw_portrait_frame(screen, frame, variant, active, hovered)

        buttons.append(button)

    return buttons


def _draw_token_without_blue_selection(token, screen, camera, font, selected=False):
    relative_path = token.hero.get("figure_token")
    source = figures._load_image(relative_path)
    if source is None:
        return figures._ORIGINAL_TOKEN_DRAW(token, screen, camera, font, selected=selected)

    sx, sy = token.tile.center(camera)
    max_width = max(46, int(108 * camera.zoom))
    max_height = max(64, int(132 * camera.zoom))
    rendered = figures._fit_image(relative_path, (max_width, max_height))
    if rendered is None:
        return figures._ORIGINAL_TOKEN_DRAW(token, screen, camera, font, selected=selected)

    base_y = int(sy + 58 * camera.zoom)
    rect = rendered.get_rect(midbottom=(int(sx), base_y))
    player_color = token.hero.get("player_color", token.hero.get("color", (220, 220, 220)))

    # Zostaje subtelne oznaczenie koloru gracza przy podstawce.
    # Usuwamy natomiast dodatkowy niebieski okrag zaznaczenia aktywnego pionka.
    ring_width = max(26, int(58 * camera.zoom))
    ring_height = max(9, int(16 * camera.zoom))
    ring = pygame.Rect(0, 0, ring_width, ring_height)
    ring.midbottom = (int(sx), base_y + max(1, int(2 * camera.zoom)))
    pygame.draw.ellipse(
        screen,
        (20, 18, 15),
        ring.inflate(max(3, int(6 * camera.zoom)), max(2, int(4 * camera.zoom))),
    )
    pygame.draw.ellipse(screen, player_color, ring, max(2, int(3 * camera.zoom)))

    screen.blit(rendered, rect)


def install_hero_figure_visual_fix():
    global _INSTALLED
    if _INSTALLED:
        return

    from rg_world import map as world_map

    # Wrappery konfiguracji bohatera odwolują sie do tej funkcji globalnie,
    # wiec podmiana zachowuje cala istniejaca logike wyboru i tylko zmienia UI.
    figures._draw_selector = _draw_full_figure_selector

    # HeroToken.draw zostal juz podmieniony przez hero_figure_system, dlatego
    # tutaj ustawiamy finalny renderer bez niebieskiej obwodki zaznaczenia.
    world_map.HeroToken.draw = _draw_token_without_blue_selection

    _INSTALLED = True
