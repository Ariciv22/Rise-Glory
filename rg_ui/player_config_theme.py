from __future__ import annotations

import sys

import pygame

from rg_ui import screens as s
from rg_ui import title_flow as tf


_INSTALLED = False
_NAME_FIELD_ACTIVE = False


def _font(size: int, *, bold: bool = False):
    """Spójny krój fantasy dla ekranu wyboru bohatera.

    W repo nie ma jeszcze finalnego pliku fontu z logo Rise & Glory, dlatego
    używamy Georgii jako stabilnego kroju szeryfowego dostępnego na docelowych
    komputerach. Po dodaniu właściwego fontu zmiana będzie w jednym miejscu.
    """
    return pygame.font.SysFont("georgia", int(size), bold=bold)


def _draw_textured_panel(screen, rect, mouse, *, selected=False):
    """Rysuje dokładnie tę samą teksturę panel2.png co dolne przyciski."""
    texture = s._load_menu_button_texture(rect.size)
    hovered = rect.collidepoint(mouse)

    if texture is not None:
        shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 76))
        screen.blit(shadow, rect.move(3, 4))
        screen.blit(texture, rect)
    else:
        pygame.draw.rect(screen, (28, 24, 19), rect, border_radius=8)
        pygame.draw.rect(screen, s.GOLD, rect, 2, border_radius=8)

    if hovered:
        glow = pygame.Surface(rect.size, pygame.SRCALPHA)
        glow.fill((255, 220, 120, 22))
        screen.blit(glow, rect)

    if selected:
        glow = pygame.Surface(rect.size, pygame.SRCALPHA)
        glow.fill((255, 220, 120, 18))
        screen.blit(glow, rect)
        pygame.draw.rect(screen, s.GOLD, rect, 3, border_radius=7)


def _draw_action_button(screen, font, mouse, button):
    """Dolne przyciski: panel2.png + chłodny srebrno-pergaminowy tekst."""
    texture = s._load_menu_button_texture(button.rect.size)
    hovered = button.rect.collidepoint(mouse)

    if texture is not None:
        shadow = pygame.Surface(button.rect.size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 76))
        screen.blit(shadow, button.rect.move(3, 4))
        screen.blit(texture, button.rect)
    else:
        pygame.draw.rect(screen, (28, 24, 19), button.rect, border_radius=8)
        pygame.draw.rect(screen, s.GOLD, button.rect, 2, border_radius=8)

    if hovered:
        glow = pygame.Surface(button.rect.size, pygame.SRCALPHA)
        glow.fill((220, 235, 240, 24))
        screen.blit(glow, button.rect)

    text_color = (226, 235, 236) if hovered else (184, 199, 204)
    label_shadow = font.render(button.text, True, (24, 18, 13))
    label = font.render(button.text, True, text_color)
    center = button.rect.center
    screen.blit(label_shadow, label_shadow.get_rect(center=(center[0] + 2, center[1] + 2)))
    screen.blit(label, label.get_rect(center=center))


def _patch_name_input_rect(rect):
    """Zapamiętuje fokus pola podczas kliknięcia bez zmian starej pętli gry."""

    def current_name_input_rect():
        global _NAME_FIELD_ACTIVE
        current_rect = pygame.Rect(rect)
        _NAME_FIELD_ACTIVE = current_rect.collidepoint(pygame.mouse.get_pos())
        return current_rect

    for module_name in ("__main__", "main"):
        module = sys.modules.get(module_name)
        if module is not None and hasattr(module, "player_name_input_rect"):
            module.player_name_input_rect = current_name_input_rect


def _draw_name_field(screen, world_name, active, y):
    width = min(540, max(420, s.SCREEN_WIDTH - 540))
    rect = pygame.Rect(s.SCREEN_WIDTH / 2 - width / 2, y, width, 58)

    pygame.draw.rect(screen, (27, 27, 25), rect, border_radius=8)
    border_color = s.GOLD if active else (118, 101, 72)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)

    input_font = _font(23, bold=True)
    label_font = _font(16, bold=True)
    text_x = rect.x + 18
    text_y = rect.y + 14

    if world_name:
        value_surface = input_font.render(world_name, True, (232, 213, 174))
        screen.blit(value_surface, (text_x, text_y))
        cursor_x = text_x + value_surface.get_width() + 2
    elif active:
        # Po kliknięciu placeholder znika i zostaje puste pole gotowe do pisania.
        cursor_x = text_x
    else:
        placeholder = input_font.render("Wpisz imię bohatera...", True, (178, 168, 147))
        screen.blit(placeholder, (text_x, text_y))
        cursor_x = text_x

    # Migający kursor widoczny wyłącznie wtedy, gdy gracz kliknął pole.
    if active and (pygame.time.get_ticks() // 500) % 2 == 0:
        cursor_top = rect.y + 14
        cursor_bottom = rect.bottom - 14
        pygame.draw.line(screen, (244, 220, 166), (cursor_x, cursor_top), (cursor_x, cursor_bottom), 2)

    # Jasna etykieta z ciemnym cieniem pozostaje czytelna na jasnym tle mapy.
    label_text = "Imię bohatera w świecie gry"
    label_surface = label_font.render(label_text, True, (244, 223, 180))
    label_shadow = label_font.render(label_text, True, (35, 28, 20))
    label_x = rect.x
    label_y = rect.y - 26
    screen.blit(label_shadow, (label_x + 2, label_y + 2))
    screen.blit(label_surface, (label_x, label_y))
    return rect


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
    global _NAME_FIELD_ACTIVE

    w, h = tf.sync(screen)
    tf.background(screen)

    # Enter kończy edycję tak samo jak kliknięcie poza polem.
    if _NAME_FIELD_ACTIVE and pygame.key.get_pressed()[pygame.K_RETURN]:
        _NAME_FIELD_ACTIVE = False

    # Systemowe TEXTINPUT jest włączane dopiero przez kliknięcie pola w app.py.
    # Dzięki temu samo pisanie na klawiaturze przed kliknięciem nie wpisuje imienia.
    if not _NAME_FIELD_ACTIVE:
        pygame.key.stop_text_input()

    compact = h < 1050
    field_y = 300 if compact else 330
    name_rect = _draw_name_field(screen, world_name, _NAME_FIELD_ACTIVE, field_y)
    _patch_name_input_rect(name_rect)

    class_font = _font(22 if compact else 24, bold=True)
    stat_font = _font(15 if compact else 16, bold=True)
    item_font = _font(14 if compact else 15)
    button_font = _font(20, bold=True)

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
        _draw_textured_panel(screen, rect, mouse, selected=selected)

        title_color = (242, 218, 166) if selected or rect.collidepoint(mouse) else (226, 204, 160)
        title = class_font.render(hero["name"], True, title_color)
        title_rect = title.get_rect(center=(rect.centerx, rect.y + 24))
        screen.blit(title, title_rect)

        if hero["id"] in used_ids:
            used_label = stat_font.render("Klasa już wybrana", True, (235, 170, 95))
            screen.blit(used_label, (rect.right - used_label.get_width() - 16, rect.y + 15))

        stat_line = "  ".join(
            f"{name[:3]} {hero['stats'].get(name, 0)}" for name in s.STAT_NAMES
        )
        stat_label = stat_font.render(stat_line, True, (203, 190, 163))
        screen.blit(stat_label, (rect.x + 18, rect.y + 46))

        item_y = rect.y + (70 if compact else 76)
        item_text = f"Start: {hero['basic_item']} + {hero['class_item']}"
        for line in s.wrap(item_font, item_text, card_w - 36)[:2]:
            if item_y + 18 < rect.bottom:
                screen.blit(
                    item_font.render(line, True, (198, 185, 158)),
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
        _draw_action_button(screen, button_font, mouse, button)
        buttons.append(button)

    return buttons


def install_player_config_theme(app_module=None):
    global _INSTALLED
    if _INSTALLED:
        return

    tf.draw_player_config = draw_player_config

    if app_module is not None and hasattr(app_module, "draw_player_config"):
        app_module.draw_player_config = draw_player_config

    for module_name in ("__main__", "main"):
        module = sys.modules.get(module_name)
        if module is not None and hasattr(module, "draw_player_config"):
            module.draw_player_config = draw_player_config

    _INSTALLED = True
