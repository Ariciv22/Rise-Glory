import pygame

from rg_data import BG, GOLD, HERO_ARCHETYPES, MAP_OPTIONS, MUTED, PANEL, PLAYER_COLORS, SCREEN_HEIGHT, SCREEN_WIDTH, STAT_NAMES, TEXT
from rg_ui import Button, centered_x, draw_panel, wrap


def draw_title(screen, title_font, font, title, subtitle):
    title_label = title_font.render(title, True, TEXT)
    subtitle_label = font.render(subtitle, True, MUTED)
    screen.blit(title_label, title_label.get_rect(center=(SCREEN_WIDTH / 2, 90)))
    screen.blit(subtitle_label, subtitle_label.get_rect(center=(SCREEN_WIDTH / 2, 138)))


def vertical_buttons(items, start_y, width=420, height=60, gap=16):
    buttons = []
    x = centered_x(width)
    for idx, (text, action) in enumerate(items):
        buttons.append(Button(text, action, (x, start_y + idx * (height + gap), width, height)))
    return buttons


def draw_menu(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Rise & Glory", "Prototyp v0.1 - lokalna rozgrywka hot-seat")
    buttons = vertical_buttons([("Nowa gra", "new"), ("Multiplayer", "multi"), ("Wyjscie", "exit")], 280)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons


def draw_map_select(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Nowa gra", "Wybierz mape")
    items = [(name, key) for key, name in MAP_OPTIONS] + [("Powrot", "back")]
    buttons = vertical_buttons(items, 300, width=430, height=58, gap=14)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons


def draw_player_count(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Liczba graczy", "Wybierz od 1 do 6 graczy dla trybu hot-seat")
    buttons = []
    start_x = SCREEN_WIDTH / 2 - 340
    for index in range(6):
        rect = pygame.Rect(start_x + (index % 3) * 230, 280 + (index // 3) * 110, 200, 76)
        button = Button(str(index + 1), f"players_{index + 1}", rect)
        button.draw(screen, font, mouse)
        buttons.append(button)
    back = Button("Powrot", "back", (SCREEN_WIDTH / 2 - 120, 560, 240, 52))
    back.draw(screen, font, mouse)
    buttons.append(back)
    return buttons


def _draw_name_field(screen, font, small_font, world_name, active=True):
    rect = pygame.Rect(SCREEN_WIDTH / 2 - 270, 170, 540, 58)
    pygame.draw.rect(screen, (34, 40, 46), rect, border_radius=10)
    pygame.draw.rect(screen, GOLD if active else (90, 90, 90), rect, 2, border_radius=10)
    label = world_name if world_name else "Wpisz imie bohatera..."
    color = TEXT if world_name else MUTED
    screen.blit(font.render(label, True, color), (rect.x + 18, rect.y + 15))
    screen.blit(small_font.render("Imie bohatera w swiecie gry", True, MUTED), (rect.x, rect.y - 24))
    return rect


def draw_player_config(screen, title_font, font, small_font, mouse, player_index, player_count, world_name, selected_archetype, used_archetypes):
    screen.fill(BG)
    draw_title(screen, title_font, font, f"Gracz {player_index + 1} z {player_count}", "Wybierz archetyp, nadaj imie albo stworz wlasny rozklad statystyk")
    _draw_name_field(screen, font, small_font, world_name)

    player_color = PLAYER_COLORS[player_index]
    pygame.draw.circle(screen, player_color, (SCREEN_WIDTH / 2 + 315, 199), 18)
    screen.blit(small_font.render("Kolor gracza", True, MUTED), (SCREEN_WIDTH / 2 + 342, 190))

    selected_id = selected_archetype["id"] if selected_archetype else None
    used_ids = {hero["archetype_id"] for hero in used_archetypes} if used_archetypes and isinstance(used_archetypes[0], dict) else set()

    buttons = []
    card_w, card_h = 360, 142
    gap_x, gap_y = 22, 18
    start_x = SCREEN_WIDTH / 2 - (card_w * 2 + gap_x) / 2
    start_y = 265
    for idx, hero in enumerate(HERO_ARCHETYPES):
        col = idx % 2
        row = idx // 2
        rect = pygame.Rect(start_x + col * (card_w + gap_x), start_y + row * (card_h + gap_y), card_w, card_h)
        selected = hero["id"] == selected_id
        hovered = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (48, 43, 35) if selected else ((38, 34, 28) if hovered else PANEL), rect, border_radius=12)
        border = player_color if selected else (hero["color"] if hovered else GOLD)
        pygame.draw.rect(screen, border, rect, 3, border_radius=12)
        pygame.draw.circle(screen, hero["color"], (rect.x + 24, rect.y + 26), 10)
        screen.blit(font.render(hero["name"], True, TEXT), (rect.x + 44, rect.y + 14))
        if hero["id"] in used_ids:
            screen.blit(small_font.render("Klasa juz wybrana", True, (235, 170, 95)), (rect.right - 158, rect.y + 18))
        stat_line = "  ".join(f"{name[:3]} {hero['stats'].get(name, 0)}" for name in STAT_NAMES)
        screen.blit(small_font.render(stat_line, True, MUTED), (rect.x + 18, rect.y + 52))
        y = rect.y + 82
        for line in wrap(small_font, f"Start: {hero['basic_item']} + {hero['class_item']}", card_w - 36)[:2]:
            screen.blit(small_font.render(line, True, MUTED), (rect.x + 18, y))
            y += 20
        buttons.append(Button("", f"archetype_{hero['id']}", rect))

    bottom_y = 780
    random_button = Button("Losowy bohater", "random_hero", (SCREEN_WIDTH / 2 - 470, bottom_y, 270, 54))
    custom_button = Button("Stworz bohatera", "custom_hero", (SCREEN_WIDTH / 2 - 180, bottom_y, 300, 54))
    next_button = Button("Zatwierdz gracza", "confirm_player", (SCREEN_WIDTH / 2 + 140, bottom_y, 330, 54))
    back = Button("Powrot", "back", (SCREEN_WIDTH / 2 - 120, 860, 240, 48))
    for button in [random_button, custom_button, next_button, back]:
        button.draw(screen, font, mouse)
        buttons.append(button)

    ready = bool(world_name.strip()) and selected_archetype is not None
    if not ready:
        screen.blit(small_font.render("Wpisz imie i wybierz archetyp.", True, (235, 170, 95)), (SCREEN_WIDTH / 2 + 150, bottom_y - 28))
    return buttons


def draw_custom_hero(screen, title_font, font, small_font, mouse, player_index, world_name, base_hero, stats):
    screen.fill(BG)
    draw_title(screen, title_font, font, f"Stworz bohatera - Gracz {player_index + 1}", f"Wyglad i ekwipunek: {base_hero['name']}")
    remaining = 12 - sum(stats.values())
    screen.blit(font.render(f"Pozostale punkty: {remaining}", True, TEXT), (SCREEN_WIDTH / 2 - 120, 170))
    screen.blit(small_font.render(f"Imie: {world_name or 'brak'}", True, MUTED), (SCREEN_WIDTH / 2 - 120, 208))

    buttons = []
    start_y = 270
    for idx, stat in enumerate(STAT_NAMES):
        y = start_y + idx * 76
        row = pygame.Rect(SCREEN_WIDTH / 2 - 340, y, 680, 58)
        draw_panel(screen, row, GOLD)
        screen.blit(font.render(stat, True, TEXT), (row.x + 24, row.y + 16))
        minus = Button("-", f"stat_minus_{stat}", (row.right - 210, row.y + 8, 52, 42))
        plus = Button("+", f"stat_plus_{stat}", (row.right - 70, row.y + 8, 52, 42))
        minus.draw(screen, font, mouse)
        plus.draw(screen, font, mouse)
        buttons.extend([minus, plus])
        value_label = font.render(str(stats[stat]), True, TEXT)
        screen.blit(value_label, value_label.get_rect(center=(row.right - 120, row.centery)))

    confirm = Button("Zatwierdz bohatera", "confirm_custom", (SCREEN_WIDTH / 2 - 190, 760, 380, 56))
    back = Button("Powrot", "back", (SCREEN_WIDTH / 2 - 120, 840, 240, 48))
    confirm.draw(screen, font, mouse)
    back.draw(screen, font, mouse)
    buttons.extend([confirm, back])
    if remaining != 0:
        screen.blit(small_font.render("Rozdziel dokladnie 12 punktow.", True, (235, 170, 95)), (SCREEN_WIDTH / 2 - 115, 730))
    return buttons


def draw_multiplayer(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Multiplayer", "Tryb sieciowy i LAN dodamy pozniej")
    buttons = vertical_buttons([("Powrot", "back")], 390)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons
