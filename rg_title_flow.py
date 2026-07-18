import sys

import pygame

import rg_screens as _screens


def _sync_layout(screen):
    width, height = screen.get_size()
    _screens.SCREEN_WIDTH = width
    _screens.SCREEN_HEIGHT = height
    return width, height


def _draw_title_background(screen, dim_alpha):
    width, height = _sync_layout(screen)
    background = _screens._load_menu_background((width, height))
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(_screens.BG)

    if dim_alpha > 0:
        shade = pygame.Surface((width, height), pygame.SRCALPHA)
        shade.fill((0, 0, 0, dim_alpha))
        screen.blit(shade, (0, 0))


def _draw_caption(screen, font, text, position="center"):
    width, height = screen.get_size()
    label = font.render(text, True, _screens.TEXT)
    pad_x, pad_y = 18, 10
    box = pygame.Rect(0, 0, label.get_width() + pad_x * 2, label.get_height() + pad_y * 2)

    if position == "right":
        box.topright = (width - 24, 24)
    else:
        box.midtop = (width // 2, max(245, int(height * 0.25)))

    panel = pygame.Surface(box.size, pygame.SRCALPHA)
    panel.fill((0, 0, 0, 150))
    screen.blit(panel, box.topleft)
    pygame.draw.rect(screen, _screens.GOLD, box, 2, border_radius=8)
    screen.blit(label, (box.x + pad_x, box.y + pad_y))


def _render_over_title(screen, draw_function, args, dim_alpha, caption=None, caption_font=None, caption_position="center"):
    _draw_title_background(screen, dim_alpha)

    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    layer.fill(_screens.BG)

    original_draw_title = _screens.draw_title
    _screens.draw_title = lambda *unused_args, **unused_kwargs: None
    try:
        buttons = draw_function(layer, *args)
    finally:
        _screens.draw_title = original_draw_title

    layer.set_colorkey(_screens.BG)
    screen.blit(layer, (0, 0))

    if caption and caption_font:
        _draw_caption(screen, caption_font, caption, caption_position)
    return buttons


def draw_map_select(screen, title_font, font, mouse):
    return _render_over_title(
        screen,
        _screens.draw_map_select,
        (title_font, font, mouse),
        32,
        "Wybierz mapę",
        font,
    )


def draw_player_count(screen, title_font, font, mouse):
    return _render_over_title(
        screen,
        _screens.draw_player_count,
        (title_font, font, mouse),
        42,
        "Wybierz liczbę graczy",
        font,
    )


def draw_player_config(screen, title_font, font, small_font, mouse, player_index, player_count, world_name, selected_archetype, used_archetypes):
    return _render_over_title(
        screen,
        _screens.draw_player_config,
        (title_font, font, small_font, mouse, player_index, player_count, world_name, selected_archetype, used_archetypes),
        105,
        f"Gracz {player_index + 1} z {player_count}",
        font,
        "right",
    )


def draw_custom_hero(screen, title_font, font, small_font, mouse, player_index, world_name, selected_set, stats):
    return _render_over_title(
        screen,
        _screens.draw_custom_hero,
        (title_font, font, small_font, mouse, player_index, world_name, selected_set, stats),
        115,
        f"Tworzenie bohatera — Gracz {player_index + 1}",
        font,
        "right",
    )


def install_into_main():
    patches = {
        "draw_map_select": draw_map_select,
        "draw_player_count": draw_player_count,
        "draw_player_config": draw_player_config,
        "draw_custom_hero": draw_custom_hero,
    }
    for module_name in ("__main__", "main"):
        module = sys.modules.get(module_name)
        if module is None or not hasattr(module, "draw_map_select"):
            continue
        for name, function in patches.items():
            setattr(module, name, function)
