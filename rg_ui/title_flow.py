import sys

import pygame

from rg_ui import screens as s


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


def themed_button(screen, font, mouse, button, fallback_draw=None):
    texture = s._load_menu_button_texture(button.rect.size)
    if not texture:
        if fallback_draw is not None:
            fallback_draw(button, screen, font, mouse)
        else:
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
    buttons.append(
        s.Button(
            "Powrót",
            "back",
            (w // 2 - 215, y + 50 + len(s.MAP_OPTIONS) * 76, 430, 58),
        )
    )
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
        rect = (
            start_x + (index % 3) * (bw + gx),
            start_y + (index // 3) * (bh + gy),
            bw,
            bh,
        )
        button = s.Button(str(index + 1), f"players_{index + 1}", rect)
        themed_button(screen, font, mouse, button)
        buttons.append(button)

    back = s.Button(
        "Powrót",
        "back",
        (w // 2 - 150, start_y + 2 * (bh + gy) + 18, 300, 54),
    )
    themed_button(screen, font, mouse, back)
    buttons.append(back)
    return buttons


def _patch_name_input_rect(rect):
    def current_name_input_rect():
        return pygame.Rect(rect)

    for module_name in ("__main__", "main"):
        module = sys.modules.get(module_name)
        if module is not None and hasattr(module, "player_name_input_rect"):
            module.player_name_input_rect = current_name_input_rect


def draw_player_config(
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
    w, h = sync(screen)
    background(screen)

    compact = h < 1050
    field_y = 300 if compact else 330
    name_rect = s._draw_name_field(screen, font, small_font, world_name, y=field_y)
    _patch_name_input_rect(name_rect)

    player_color = s.PLAYER_COLORS[player_index]
    color_x = min(w - 230, int(name_rect.right + 55))
    pygame.draw.circle(screen, player_color, (color_x, name_rect.centery), 18)
    screen.blit(
        small_font.render("Kolor gracza", True, s.MUTED),
        (color_x + 32, name_rect.centery - 9),
    )

    selected_id = selected_archetype["id"] if selected_archetype else None
    used_ids = (
        {hero["archetype_id"] for hero in used_archetypes}
        if used_archetypes
        else set()
    )

    buttons = []
    card_w = 360
    card_h = 108 if compact else 128
    gap_x = 22
    gap_y = 10 if compact else 14
    start_x = w / 2 - (card_w * 2 + gap_x) / 2
    start_y = name_rect.bottom + 28

    for idx, hero in enumerate(s.HERO_ARCHETYPES):
        col = idx % 2
        row = idx // 2
        rect = pygame.Rect(
            start_x + col * (card_w + gap_x),
            start_y + row * (card_h + gap_y),
            card_w,
            card_h,
        )
        selected = hero["id"] == selected_id
        hovered = rect.collidepoint(mouse)

        fill = (48, 43, 35) if selected else ((38, 34, 28) if hovered else s.PANEL)
        pygame.draw.rect(screen, fill, rect, border_radius=12)
        border = player_color if selected else (hero["color"] if hovered else s.GOLD)
        pygame.draw.rect(screen, border, rect, 3, border_radius=12)

        pygame.draw.circle(screen, hero["color"], (rect.x + 24, rect.y + 24), 10)
        screen.blit(font.render(hero["name"], True, s.TEXT), (rect.x + 44, rect.y + 12))

        if hero["id"] in used_ids:
            used_label = small_font.render("Klasa już wybrana", True, (235, 170, 95))
            screen.blit(used_label, (rect.right - used_label.get_width() - 14, rect.y + 16))

        stat_line = "  ".join(
            f"{name[:3]} {hero['stats'].get(name, 0)}" for name in s.STAT_NAMES
        )
        screen.blit(
            small_font.render(stat_line, True, s.MUTED),
            (rect.x + 18, rect.y + 46),
        )

        item_y = rect.y + (70 if compact else 76)
        item_text = f"Start: {hero['basic_item']} + {hero['class_item']}"
        for line in s.wrap(small_font, item_text, card_w - 36)[:2]:
            if item_y + 18 < rect.bottom:
                screen.blit(
                    small_font.render(line, True, s.MUTED),
                    (rect.x + 18, item_y),
                )
            item_y += 18

        buttons.append(s.Button("", f"archetype_{hero['id']}", rect))

    cards_bottom = start_y + 3 * card_h + 2 * gap_y
    button_y = cards_bottom + (12 if compact else 22)

    button_gap = 20
    random_w, custom_w, confirm_w = 270, 300, 330
    group_w = random_w + button_gap + custom_w + button_gap + confirm_w
    group_x = w / 2 - group_w / 2

    random_button = s.Button("Losowy bohater", "random_hero", (group_x, button_y, random_w, 54))
    custom_button = s.Button(
        "Stwórz bohatera",
        "custom_hero",
        (group_x + random_w + button_gap, button_y, custom_w, 54),
    )
    confirm_button = s.Button(
        "Zatwierdź gracza",
        "confirm_player",
        (
            group_x + random_w + button_gap + custom_w + button_gap,
            button_y,
            confirm_w,
            54,
        ),
    )
    back_button = s.Button("Powrót", "back", (w / 2 - 120, button_y + 66, 240, 48))

    for button in [random_button, custom_button, confirm_button, back_button]:
        themed_button(screen, font, mouse, button)
        buttons.append(button)

    return buttons


def _draw_screen_over_background(screen, draw_function, args):
    background(screen)
    layer = pygame.Surface(screen.get_size())
    layer.fill(s.BG)

    original_title = s.draw_title
    original_draw = s.Button.draw

    def patched_draw(button, target, draw_font, mouse_pos, active=False):
        if button.text and button.text not in {"+", "-"} and button.rect.width >= 120:
            themed_button(target, draw_font, mouse_pos, button, original_draw)
        else:
            original_draw(button, target, draw_font, mouse_pos, active)

    s.draw_title = lambda *unused_args, **unused_kwargs: None
    s.Button.draw = patched_draw
    try:
        buttons = draw_function(layer, *args)
    finally:
        s.draw_title = original_title
        s.Button.draw = original_draw

    layer.set_colorkey(s.BG)
    screen.blit(layer, (0, 0))
    return buttons


def draw_custom_hero(
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
    sync(screen)
    return _draw_screen_over_background(
        screen,
        s.draw_custom_hero,
        (
            title_font,
            font,
            small_font,
            mouse,
            player_index,
            world_name,
            selected_set,
            stats,
        ),
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
        if module:
            for name, function in patches.items():
                if hasattr(module, name):
                    setattr(module, name, function)
