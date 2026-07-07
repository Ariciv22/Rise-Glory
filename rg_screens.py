import pygame

from rg_data import BG, GOLD, HERO_ARCHETYPES, MAP_OPTIONS, MUTED, PANEL, SCREEN_HEIGHT, SCREEN_WIDTH, TEXT
from rg_ui import Button, centered_x, draw_panel, wrap


def draw_title(screen, title_font, font, title, subtitle):
    title_label = title_font.render(title, True, TEXT)
    subtitle_label = font.render(subtitle, True, MUTED)
    screen.blit(title_label, title_label.get_rect(center=(SCREEN_WIDTH / 2, 130)))
    screen.blit(subtitle_label, subtitle_label.get_rect(center=(SCREEN_WIDTH / 2, 178)))


def vertical_buttons(items, start_y, width=420, height=60, gap=16):
    buttons = []
    x = centered_x(width)
    for idx, (text, action) in enumerate(items):
        buttons.append(Button(text, action, (x, start_y + idx * (height + gap), width, height)))
    return buttons


def draw_menu(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Rise & Glory", "Prototyp v0.1 - bohater, mapa i pierwsze testy")
    buttons = vertical_buttons([("Nowa gra", "new"), ("Multiplayer", "multi"), ("Wyjscie", "exit")], 310)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons


def draw_map_select(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Nowa gra", "Wybierz mape testowa")
    items = [(name, key) for key, name in MAP_OPTIONS] + [("Powrot", "back")]
    buttons = vertical_buttons(items, 280, width=430, height=58, gap=14)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons


def draw_hero_select(screen, title_font, font, small_font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Wybierz bohatera", "Start: 3 zlota, 0 ran, 0 Punktow Legendy, item podstawowy i klasowy")
    buttons = []
    card_w, card_h = 430, 188
    gap_x, gap_y = 28, 24
    start_x = SCREEN_WIDTH / 2 - (card_w * 2 + gap_x) / 2
    start_y = 230
    for idx, hero in enumerate(HERO_ARCHETYPES):
        col = idx % 2
        row = idx // 2
        rect = pygame.Rect(start_x + col * (card_w + gap_x), start_y + row * (card_h + gap_y), card_w, card_h)
        hovered = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (38, 34, 28) if hovered else PANEL, rect, border_radius=14)
        pygame.draw.rect(screen, hero["color"] if hovered else GOLD, rect, 3, border_radius=14)
        pygame.draw.circle(screen, hero["color"], (rect.x + 28, rect.y + 30), 12)
        screen.blit(font.render(hero["name"], True, TEXT), (rect.x + 52, rect.y + 18))
        stat_line = "  ".join(f"{name[:3]} {value}" for name, value in hero["stats"].items())
        screen.blit(small_font.render(stat_line, True, MUTED), (rect.x + 24, rect.y + 58))
        y = rect.y + 88
        for line in wrap(small_font, hero["role"], card_w - 48)[:2]:
            screen.blit(small_font.render(line, True, TEXT), (rect.x + 24, y))
            y += 22
        eq = f"Start: {hero['basic_item']} + {hero['class_item']}"
        for line in wrap(small_font, eq, card_w - 48)[:2]:
            screen.blit(small_font.render(line, True, MUTED), (rect.x + 24, y))
            y += 21
        buttons.append(Button("", hero["id"], rect))
    back = Button("Powrot", "back", (SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT - 84, 240, 52))
    back.draw(screen, font, mouse)
    buttons.append(back)
    return buttons


def draw_multiplayer(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Multiplayer", "Tryb do dodania pozniej")
    buttons = vertical_buttons([("Powrot", "back")], 390)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons
