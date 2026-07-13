import pygame

from rg_data import (
    BG,
    COUNCIL_ROUNDS,
    GOLD,
    HERO_ARCHETYPES,
    MAP_OPTIONS,
    MUTED,
    PANEL,
    PLAYER_COLORS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STAT_NAMES,
    TEXT,
)
from rg_ui import Button, centered_x, draw_lines, draw_panel, wrap


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
    draw_title(screen, title_font, font, f"Gracz {player_index + 1} z {player_count}", "Wybierz gotowego bohatera albo stworz wlasny rozklad statystyk")
    _draw_name_field(screen, font, small_font, world_name)

    player_color = PLAYER_COLORS[player_index]
    pygame.draw.circle(screen, player_color, (SCREEN_WIDTH / 2 + 315, 199), 18)
    screen.blit(small_font.render("Kolor gracza", True, MUTED), (SCREEN_WIDTH / 2 + 342, 190))

    selected_id = selected_archetype["id"] if selected_archetype else None
    used_ids = {hero["archetype_id"] for hero in used_archetypes} if used_archetypes else set()

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

    if selected_archetype is None:
        screen.blit(small_font.render("Wybierz gotowego bohatera albo kliknij Stworz bohatera.", True, (235, 170, 95)), (SCREEN_WIDTH / 2 + 30, bottom_y - 28))
    return buttons


def draw_start_set_panel(screen, font, small_font, mouse, selected_set):
    buttons = []
    panel = pygame.Rect(1030, 220, 390, 475)
    draw_panel(screen, panel, GOLD)
    screen.blit(font.render("Set startowy", True, TEXT), (panel.x + 24, panel.y + 22))
    screen.blit(small_font.render("Wyglad i ekwipunek wybierasz tutaj.", True, MUTED), (panel.x + 24, panel.y + 52))

    selected_id = selected_set["id"] if selected_set else None
    y = panel.y + 92
    for hero in HERO_ARCHETYPES:
        rect = pygame.Rect(panel.x + 22, y, panel.width - 44, 52)
        selected = hero["id"] == selected_id
        hovered = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (48, 43, 35) if selected else ((38, 34, 28) if hovered else PANEL), rect, border_radius=10)
        pygame.draw.rect(screen, hero["color"] if selected or hovered else GOLD, rect, 2, border_radius=10)
        pygame.draw.circle(screen, hero["color"], (rect.x + 18, rect.centery), 8)
        screen.blit(small_font.render(hero["name"], True, TEXT), (rect.x + 34, rect.y + 8))
        item_text = f"{hero['basic_item']} + {hero['class_item']}"
        screen.blit(small_font.render(item_text[:42], True, MUTED), (rect.x + 34, rect.y + 28))
        buttons.append(Button("", f"custom_set_{hero['id']}", rect))
        y += 61
    return buttons


def draw_custom_hero(screen, title_font, font, small_font, mouse, player_index, world_name, selected_set, stats):
    screen.fill(BG)
    subtitle = f"Set startowy: {selected_set['name']}" if selected_set else "Wybierz set startowy po prawej stronie"
    draw_title(screen, title_font, font, f"Stworz bohatera - Gracz {player_index + 1}", subtitle)
    remaining = 12 - sum(stats.values())
    screen.blit(font.render(f"Pozostale punkty: {remaining}", True, TEXT), (SCREEN_WIDTH / 2 - 300, 170))
    screen.blit(small_font.render(f"Imie: {world_name or 'domyslne'}", True, MUTED), (SCREEN_WIDTH / 2 - 300, 208))

    buttons = []
    buttons.extend(draw_start_set_panel(screen, font, small_font, mouse, selected_set))

    start_y = 270
    for idx, stat in enumerate(STAT_NAMES):
        y = start_y + idx * 76
        row = pygame.Rect(SCREEN_WIDTH / 2 - 500, y, 680, 58)
        draw_panel(screen, row, GOLD)
        screen.blit(font.render(stat, True, TEXT), (row.x + 24, row.y + 16))
        minus = Button("-", f"stat_minus_{stat}", (row.right - 210, row.y + 8, 52, 42))
        plus = Button("+", f"stat_plus_{stat}", (row.right - 70, row.y + 8, 52, 42))
        minus.draw(screen, font, mouse)
        plus.draw(screen, font, mouse)
        buttons.extend([minus, plus])
        value_label = font.render(str(stats[stat]), True, TEXT)
        screen.blit(value_label, value_label.get_rect(center=(row.right - 120, row.centery)))

    confirm = Button("Zatwierdz bohatera", "confirm_custom", (SCREEN_WIDTH / 2 - 350, 760, 380, 56))
    back = Button("Powrot", "back", (SCREEN_WIDTH / 2 - 260, 840, 240, 48))
    confirm.draw(screen, font, mouse)
    back.draw(screen, font, mouse)
    buttons.extend([confirm, back])
    if remaining != 0:
        screen.blit(small_font.render("Rozdziel dokladnie 12 punktow.", True, (235, 170, 95)), (SCREEN_WIDTH / 2 - 285, 730))
    if selected_set is None:
        screen.blit(small_font.render("Wybierz set startowy po prawej stronie.", True, (235, 170, 95)), (SCREEN_WIDTH / 2 - 285, 708))
    return buttons


def draw_initiative(screen, title_font, font, small_font, mouse, players, initiative):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Rzut na kolejnosc", "Najwyzszy wynik rozpoczyna, a dalsza kolejnosc biegnie zgodnie z ustawieniem graczy")

    panel = pygame.Rect(SCREEN_WIDTH / 2 - 470, 185, 940, 610)
    draw_panel(screen, panel, GOLD)
    screen.blit(font.render("Wyniki k20", True, TEXT), (panel.x + 28, panel.y + 24))

    rolls = initiative.get("initial_rolls", {})
    y = panel.y + 72
    for index, player in enumerate(players):
        row = pygame.Rect(panel.x + 24, y, panel.width - 48, 58)
        pygame.draw.rect(screen, (31, 30, 28), row, border_radius=9)
        pygame.draw.rect(screen, player.get("player_color", GOLD), row, 2, border_radius=9)
        pygame.draw.circle(screen, player.get("player_color", GOLD), (row.x + 20, row.centery), 9)
        text = f"Gracz {player.get('player_number', index + 1)} - {player['name']} ({player.get('archetype_name', '-')})"
        screen.blit(font.render(text, True, TEXT), (row.x + 40, row.y + 15))
        roll_text = font.render(str(rolls.get(index, "-")), True, TEXT)
        screen.blit(roll_text, (row.right - 54, row.y + 15))
        y += 68

    rerolls = initiative.get("reroll_rounds", [])
    if rerolls:
        y += 4
        screen.blit(small_font.render("Dogrywki przy remisie:", True, TEXT), (panel.x + 28, y))
        y += 26
        for round_index, reroll in enumerate(rerolls, start=1):
            parts = [f"{players[index]['name']}: {value}" for index, value in reroll.items()]
            line = f"Dogrywka {round_index}: " + ", ".join(parts)
            screen.blit(small_font.render(line, True, MUTED), (panel.x + 28, y))
            y += 24

    order_names = [players[index]["name"] for index in initiative.get("turn_order", [])]
    order_text = " -> ".join(order_names)
    order_y = panel.bottom - 74
    screen.blit(font.render("Kolejnosc tur:", True, TEXT), (panel.x + 28, order_y))
    draw_lines(screen, small_font, wrap(small_font, order_text, panel.width - 250), panel.x + 188, order_y + 3, MUTED, max_width=panel.width - 220)

    start = Button("Rozpocznij gre", "start_game", (SCREEN_WIDTH / 2 - 190, 830, 380, 58))
    start.draw(screen, font, mouse)
    return [start]


def draw_council(screen, title_font, font, small_font, mouse, round_number):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Rada Bohaterow", f"Zakonczono {COUNCIL_ROUNDS} pelnych rund. Nastepna runda: {round_number}")

    panel = pygame.Rect(SCREEN_WIDTH / 2 - 420, 220, 840, 470)
    draw_panel(screen, panel, GOLD)
    screen.blit(font.render("Porzadek Rady", True, TEXT), (panel.x + 32, panel.y + 28))
    lines = [
        "1. Rozpatrz Wydarzenie Swiata - w tej wersji ekran testowy.",
        "2. Handel miedzy graczami zostanie podpiety w kolejnym etapie.",
        "3. Po zakonczeniu Rady licznik cyklu wraca do 1/5.",
        "4. Nastepna ture rozpoczyna gracz wynikajacy z ustalonej kolejnosci.",
    ]
    draw_lines(screen, font, lines, panel.x + 36, panel.y + 92, MUTED, line_h=54, max_width=panel.width - 72)

    close = Button("Zakoncz Rade", "close_council", (SCREEN_WIDTH / 2 - 190, 740, 380, 58))
    close.draw(screen, font, mouse)
    return [close]


def draw_multiplayer(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Multiplayer", "Tryb sieciowy i LAN dodamy pozniej")
    buttons = vertical_buttons([("Powrot", "back")], 390)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons
