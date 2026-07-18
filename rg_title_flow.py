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


def _menu_header_y(screen):
    _, height = screen.get_size()
    return int(max(370, min(430, height * 0.43)))


def _draw_caption(screen, font, text, y=None):
    width, _ = screen.get_size()
    if y is None:
        y = _menu_header_y(screen)

    shadow = font.render(text, True, (20, 15, 10))
    label = font.render(text, True, _screens.TEXT)
    center_x = width // 2
    screen.blit(shadow, shadow.get_rect(midtop=(center_x + 2, y + 2)))
    rect = label.get_rect(midtop=(center_x, y))
    screen.blit(label, rect)

    ornament_y = rect.bottom + 8
    ornament_w = max(150, min(320, rect.width + 90))
    pygame.draw.line(
        screen,
        _screens.GOLD,
        (center_x - ornament_w // 2, ornament_y),
        (center_x + ornament_w // 2, ornament_y),
        2,
    )
    return rect


def _draw_themed_button(screen, font, mouse, button, fallback_draw=None):
    hovered = button.rect.collidepoint(mouse)
    texture = _screens._load_menu_button_texture(button.rect.size)
    if texture:
        shadow = pygame.Surface(button.rect.size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 80))
        screen.blit(shadow, button.rect.move(3, 4))
        screen.blit(texture, button.rect)
        if hovered:
            glow = pygame.Surface(button.rect.size, pygame.SRCALPHA)
            glow.fill((255, 220, 120, 24))
            screen.blit(glow, button.rect)

        if button.text:
            label_shadow = font.render(button.text, True, (20, 15, 10))
            label = font.render(button.text, True, _screens.TEXT if not hovered else (255, 232, 170))
            screen.blit(label_shadow, label_shadow.get_rect(center=(button.rect.centerx + 2, button.rect.centery + 2)))
            screen.blit(label, label.get_rect(center=button.rect.center))
        return

    if fallback_draw is not None:
        fallback_draw(button, screen, font, mouse)
    else:
        button.draw(screen, font, mouse)


def _render_over_title(screen, draw_function, args, dim_alpha):
    _draw_title_background(screen, dim_alpha)

    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    layer.fill(_screens.BG)

    original_draw_title = _screens.draw_title
    original_button_draw = _screens.Button.draw

    def themed_button_draw(button, target, draw_font, mouse_pos, active=False):
        if button.text and button.text not in {"+", "-"} and button.rect.width >= 120:
            _draw_themed_button(target, draw_font, mouse_pos, button, original_button_draw)
        else:
            original_button_draw(button, target, draw_font, mouse_pos, active)

    _screens.draw_title = lambda *unused_args, **unused_kwargs: None
    _screens.Button.draw = themed_button_draw
    try:
        buttons = draw_function(layer, *args)
    finally:
        _screens.draw_title = original_draw_title
        _screens.Button.draw = original_button_draw

    layer.set_colorkey(_screens.BG)
    screen.blit(layer, (0, 0))
    return buttons


def draw_map_select(screen, title_font, font, mouse):
    _draw_title_background(screen, 42)
    caption = _draw_caption(screen, font, "Wybierz mapę")

    start_y = caption.bottom + 28
    items = [(name, key) for key, name in _screens.MAP_OPTIONS] + [("Powrót", "back")]
    buttons = _screens.vertical_buttons(items, start_y, width=430, height=58, gap=14)
    for button in buttons:
        _draw_themed_button(screen, font, mouse, button)
    return buttons


def draw_player_count(screen, title_font, font, mouse):
    width, height = _sync_layout(screen)
    _draw_title_background(screen, 52)
    caption = _draw_caption(screen, font, "Wybierz liczbę graczy")

    buttons = []
    button_w = 200
    button_h = 68
    gap_x = 30
    gap_y = 22
    grid_w = button_w * 3 + gap_x * 2
    start_x = width // 2 - grid_w // 2
    start_y = caption.bottom + 30

    for index in range(6):
        rect = pygame.Rect(
            start_x + (index % 3) * (button_w + gap_x),
            start_y + (index // 3) * (button_h + gap_y),
            button_w,
            button_h,
        )
        button = _screens.Button(str(index + 1), f"players_{index + 1}", rect)
        _draw_themed_button(screen, font, mouse, button)
        buttons.append(button)

    back_y = min(height - 72, start_y + button_h * 2 + gap_y + 34)
    back = _screens.Button("Powrót", "back", (width // 2 - 150, back_y, 300, 54))
    _draw_themed_button(screen, font, mouse, back)
    buttons.append(back)
    return buttons


def draw_player_config(screen, title_font, font, small_font, mouse, player_index, player_count, world_name, selected_archetype, used_archetypes):
    return _render_over_title(
        screen,
        _screens.draw_player_config,
        (title_font, font, small_font, mouse, player_index, player_count, world_name, selected_archetype, used_archetypes),
        155,
    )


def draw_custom_hero(screen, title_font, font, small_font, mouse, player_index, world_name, selected_set, stats):
    return _render_over_title(
        screen,
        _screens.draw_custom_hero,
        (title_font, font, small_font, mouse, player_index, world_name, selected_set, stats),
        170,
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
