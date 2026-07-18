import sys
import pygame
import rg_screens as s


def sync(screen):
    w, h = screen.get_size()
    s.SCREEN_WIDTH, s.SCREEN_HEIGHT = w, h
    return w, h


def background(screen, dim=0):
    w, h = sync(screen)
    image = s._load_menu_background((w, h))
    if image:
        screen.blit(image, (0, 0))
    else:
        screen.fill(s.BG)
    if dim:
        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((0, 0, 0, dim))
        screen.blit(shade, (0, 0))


def themed_button(screen, font, mouse, button):
    texture = s._load_menu_button_texture(button.rect.size)
    if not texture:
        button.draw(screen, font, mouse)
        return
    hovered = button.rect.collidepoint(mouse)
    screen.blit(texture, button.rect)
    if hovered:
        glow = pygame.Surface(button.rect.size, pygame.SRCALPHA)
        glow.fill((255, 220, 120, 24))
        screen.blit(glow, button.rect)
    label = font.render(button.text, True, (255, 232, 170) if hovered else s.TEXT)
    screen.blit(label, label.get_rect(center=button.rect.center))


def draw_map_select(screen, title_font, font, mouse):
    w, h = sync(screen)
    background(screen)
    y = max(390, int(h * 0.42))
    title = font.render("Wybierz mapę", True, s.TEXT)
    screen.blit(title, title.get_rect(center=(w // 2, y)))
    buttons = [
        s.Button(name, key, (w // 2 - 215, y + 50 + i * 76, 430, 58))
        for i, (key, name) in enumerate(s.MAP_OPTIONS)
    ]
    buttons.append(s.Button("Powrót", "back", (w // 2 - 215, y + 50 + len(s.MAP_OPTIONS) * 76, 430, 58)))
    for button in buttons:
        themed_button(screen, font, mouse, button)
    return buttons


def draw_player_count(screen, title_font, font, mouse):
    w, h = sync(screen)
    background(screen)
    y = max(385, int(h * 0.40))
    title = font.render("Wybierz liczbę graczy", True, s.TEXT)
    screen.blit(title, title.get_rect(center=(w // 2, y)))
    buttons = []
    bw, bh, gx, gy = 200, 68, 30, 22
    start_x = w // 2 - (bw * 3 + gx * 2) // 2
    start_y = y + 48
    for index in range(6):
        rect = (start_x + (index % 3) * (bw + gx), start_y + (index // 3) * (bh + gy), bw, bh)
        button = s.Button(str(index + 1), f"players_{index + 1}", rect)
        themed_button(screen, font, mouse, button)
        buttons.append(button)
    back = s.Button("Powrót", "back", (w // 2 - 150, start_y + 2 * (bh + gy) + 18, 300, 54))
    themed_button(screen, font, mouse, back)
    buttons.append(back)
    return buttons


def draw_player_config(screen, title_font, font, small_font, mouse, player_index, player_count, world_name, selected_archetype, used_archetypes):
    w, h = sync(screen)
    background(screen, 0)
    original_title = s.draw_title
    original_draw = s.Button.draw

    def patched_draw(button, target, draw_font, mouse_pos, active=False):
        if button.text and button.text not in {"+", "-"} and button.rect.width >= 120:
            themed_button(target, draw_font, mouse_pos, button)
        else:
            original_draw(button, target, draw_font, mouse_pos, active)

    s.draw_title = lambda *args, **kwargs: None
    s.Button.draw = patched_draw
    try:
        buttons = s.draw_player_config(screen, title_font, font, small_font, mouse, player_index, player_count, world_name, selected_archetype, used_archetypes)
    finally:
        s.draw_title = original_title
        s.Button.draw = original_draw
    return buttons


def draw_custom_hero(screen, title_font, font, small_font, mouse, player_index, world_name, selected_set, stats):
    background(screen, 0)
    original_title = s.draw_title
    original_draw = s.Button.draw

    def patched_draw(button, target, draw_font, mouse_pos, active=False):
        if button.text and button.text not in {"+", "-"} and button.rect.width >= 120:
            themed_button(target, draw_font, mouse_pos, button)
        else:
            original_draw(button, target, draw_font, mouse_pos, active)

    s.draw_title = lambda *args, **kwargs: None
    s.Button.draw = patched_draw
    try:
        buttons = s.draw_custom_hero(screen, title_font, font, small_font, mouse, player_index, world_name, selected_set, stats)
    finally:
        s.draw_title = original_title
        s.Button.draw = original_draw
    return buttons


def install_into_main():
    patches = {
        "draw_map_select": draw_map_select,
        "draw_player_count": draw_player_count,
        "draw_player_config": draw_player_config,
        "draw_custom_hero": draw_custom_hero,
    }
    for module_name in ("__main__", "main"):
        module = sys.modules.get(module_name)
        if module:
            for name, function in patches.items():
                if hasattr(module, name):
                    setattr(module, name, function)
