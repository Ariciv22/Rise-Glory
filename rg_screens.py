from pathlib import Path

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

ROOT_DIR = Path(__file__).resolve().parent
MENU_BACKGROUND_PATH = ROOT_DIR / "Grafiki" / "Tytulowy_ekran.png"
_MENU_BACKGROUND_CACHE = {"size": None, "surface": None}


def is_compact():
    return SCREEN_HEIGHT < 1050


def title_positions():
    return (70, 112) if is_compact() else (90, 138)


def clamp(value, low, high):
    return max(low, min(value, high))


def _load_menu_background(size):
    if _MENU_BACKGROUND_CACHE["size"] == size:
        return _MENU_BACKGROUND_CACHE["surface"]
    if not MENU_BACKGROUND_PATH.exists():
        _MENU_BACKGROUND_CACHE["size"] = size
        _MENU_BACKGROUND_CACHE["surface"] = None
        return None
    try:
        image = pygame.image.load(str(MENU_BACKGROUND_PATH)).convert_alpha()
    except pygame.error:
        _MENU_BACKGROUND_CACHE["size"] = size
        _MENU_BACKGROUND_CACHE["surface"] = None
        return None

    iw, ih = image.get_size()
    sw, sh = size
    scale = max(sw / iw, sh / ih)
    scaled = pygame.transform.smoothscale(image, (int(iw * scale), int(ih * scale)))
    background = pygame.Surface(size, pygame.SRCALPHA)
    background.blit(scaled, ((sw - scaled.get_width()) // 2, (sh - scaled.get_height()) // 2))
    _MENU_BACKGROUND_CACHE["size"] = size
    _MENU_BACKGROUND_CACHE["surface"] = background
    return background


def draw_title(screen, title_font, font, title, subtitle):
    title_y, subtitle_y = title_positions()
    title_label = title_font.render(title, True, TEXT)
    subtitle_label = font.render(subtitle, True, MUTED)
    screen.blit(title_label, title_label.get_rect(center=(SCREEN_WIDTH / 2, title_y)))
    screen.blit(subtitle_label, subtitle_label.get_rect(center=(SCREEN_WIDTH / 2, subtitle_y)))


def vertical_buttons(items, start_y, width=420, height=60, gap=16):
    buttons = []
    x = centered_x(width)
    for idx, (text, action) in enumerate(items):
        buttons.append(Button(text, action, (x, start_y + idx * (height + gap), width, height)))
    return buttons


def draw_menu(screen, title_font, font, mouse):
    background = _load_menu_background(screen.get_size())
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BG)
        draw_title(screen, title_font, font, "Rise & Glory", "Prototyp v0.1 - lokalna rozgrywka hot-seat")
    start_y = int(clamp(SCREEN_HEIGHT * 0.33, 250, 320))
    buttons = vertical_buttons([("Nowa gra", "new"), ("Multiplayer", "multi"), ("Wyjscie", "exit")], start_y)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons


def draw_map_select(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Nowa gra", "Wybierz mape")
    start_y = 250 if is_compact() else 300
    items = [(name, key) for key, name in MAP_OPTIONS] + [("Powrot", "back")]
    buttons = vertical_buttons(items, start_y, width=430, height=56 if is_compact() else 58, gap=12 if is_compact() else 14)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons


def draw_player_count(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Liczba graczy", "Wybierz od 1 do 6 graczy dla trybu hot-seat")
    buttons = []
    compact = is_compact()
    start_x = SCREEN_WIDTH / 2 - 340
    start_y = 245 if compact else 280
    row_gap = 92 if compact else 110
    for index in range(6):
        rect = pygame.Rect(start_x + (index % 3) * 230, start_y + (index // 3) * row_gap, 200, 68 if compact else 76)
        button = Button(str(index + 1), f"players_{index + 1}", rect)
        button.draw(screen, font, mouse)
        buttons.append(button)
    back_y = min(SCREEN_HEIGHT - 78, start_y + row_gap * 2 + 30)
    back = Button("Powrot", "back", (SCREEN_WIDTH / 2 - 120, back_y, 240, 52))
    back.draw(screen, font, mouse)
    buttons.append(back)
    return buttons


def _draw_name_field(screen, font, small_font, world_name, active=True, y=None):
    if y is None:
        y = 145 if is_compact() else 170
    width = min(540, max(420, SCREEN_WIDTH - 540))
    rect = pygame.Rect(SCREEN_WIDTH / 2 - width / 2, y, width, 58)
    pygame.draw.rect(screen, (34, 40, 46), rect, border_radius=10)
    pygame.draw.rect(screen, GOLD if active else (90, 90, 90), rect, 2, border_radius=10)
    label = world_name if world_name else "Wpisz imie bohatera..."
    color = TEXT if world_name else MUTED
    screen.blit(font.render(label, True, color), (rect.x + 18, rect.y + 15))
    screen.blit(small_font.render("Imie bohatera w swiecie gry", True, MUTED), (rect.x, rect.y - 24))
    return rect


def draw_player_config(screen, title_font, font, small_font, mouse, player_index, player_count, world_name, selected_archetype, used_archetypes):
    screen.fill(BG)
    compact = is_compact()
    draw_title(screen, title_font, font, f"Gracz {player_index + 1} z {player_count}", "Wybierz gotowego bohatera albo stworz wlasny rozklad statystyk")
    field_y = 140 if compact else 170
    name_rect = _draw_name_field(screen, font, small_font, world_name, y=field_y)

    player_color = PLAYER_COLORS[player_index]
    color_x = min(SCREEN_WIDTH - 230, name_rect.right + 55)
    pygame.draw.circle(screen, player_color, (color_x, name_rect.centery), 18)
    screen.blit(small_font.render("Kolor gracza", True, MUTED), (color_x + 32, name_rect.centery - 9))

    selected_id = selected_archetype["id"] if selected_archetype else None
    used_ids = {hero["archetype_id"] for hero in used_archetypes} if used_archetypes else set()

    buttons = []
    card_w = 360
    card_h = 108 if compact else 142
    gap_x = 22
    gap_y = 10 if compact else 18
    start_x = SCREEN_WIDTH / 2 - (card_w * 2 + gap_x) / 2
    start_y = 238 if compact else 265
    for idx, hero in enumerate(HERO_ARCHETYPES):
        col = idx % 2
        row = idx // 2
        rect = pygame.Rect(start_x + col * (card_w + gap_x), start_y + row * (card_h + gap_y), card_w, card_h)
        selected = hero["id"] == selected_id
        hovered = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (48, 43, 35) if selected else ((38, 34, 28) if hovered else PANEL), rect, border_radius=12)
        border = player_color if selected else (hero["color"] if hovered else GOLD)
        pygame.draw.rect(screen, border, rect, 3, border_radius=12)
        pygame.draw.circle(screen, hero["color"], (rect.x + 24, rect.y + 24), 10)
        screen.blit(font.render(hero["name"], True, TEXT), (rect.x + 44, rect.y + 12))
        if hero["id"] in used_ids:
            screen.blit(small_font.render("Klasa juz wybrana", True, (235, 170, 95)), (rect.right - 158, rect.y + 16))
        stat_line = "  ".join(f"{name[:3]} {hero['stats'].get(name, 0)}" for name in STAT_NAMES)
        screen.blit(small_font.render(stat_line, True, MUTED), (rect.x + 18, rect.y + 46))
        y = rect.y + (70 if compact else 82)
        for line in wrap(small_font, f"Start: {hero['basic_item']} + {hero['class_item']}", card_w - 36)[:2]:
            if y + 18 < rect.bottom:
                screen.blit(small_font.render(line, True, MUTED), (rect.x + 18, y))
            y += 18 if compact else 20
        buttons.append(Button("", f"archetype_{hero['id']}", rect))

    cards_bottom = start_y + 3 * card_h + 2 * gap_y
    bottom_y = min(SCREEN_HEIGHT - 124, cards_bottom + (12 if compact else 28))
    group_w = 270 + 20 + 300 + 20 + 330
    group_x = SCREEN_WIDTH / 2 - group_w / 2
    random_button = Button("Losowy bohater", "random_hero", (group_x, bottom_y, 270, 54))
    custom_button = Button("Stworz bohatera", "custom_hero", (group_x + 290, bottom_y, 300, 54))
    next_button = Button("Zatwierdz gracza", "confirm_player", (group_x + 610, bottom_y, 330, 54))
    back_y = min(SCREEN_HEIGHT - 56, bottom_y + 64)
    back = Button("Powrot", "back", (SCREEN_WIDTH / 2 - 120, back_y, 240, 48))
    for button in [random_button, custom_button, next_button, back]:
        button.draw(screen, font, mouse)
        buttons.append(button)

    if selected_archetype is None and bottom_y > cards_bottom + 6:
        hint_x = group_x + 610 if SCREEN_WIDTH >= 1100 else SCREEN_WIDTH / 2 - 250
        screen.blit(small_font.render("Wybierz gotowego bohatera albo kliknij Stworz bohatera.", True, (235, 170, 95)), (hint_x, bottom_y - 24))
    return buttons


def _start_set_panel_rect(compact=False):
    panel_w = min(390, max(320, int(SCREEN_WIDTH * 0.27)))
    panel_x = min(1030, SCREEN_WIDTH - panel_w - 40)
    panel_y = 185 if compact else 220
    panel_h = min(475, max(360, SCREEN_HEIGHT - panel_y - 135))
    return pygame.Rect(panel_x, panel_y, panel_w, panel_h)


def draw_start_set_panel(screen, font, small_font, mouse, selected_set, compact=False):
    buttons = []
    panel = _start_set_panel_rect(compact)
    draw_panel(screen, panel, GOLD)
    screen.blit(font.render("Set startowy", True, TEXT), (panel.x + 24, panel.y + 22))
    screen.blit(small_font.render("Wyglad i ekwipunek wybierasz tutaj.", True, MUTED), (panel.x + 24, panel.y + 52))

    selected_id = selected_set["id"] if selected_set else None
    y = panel.y + 86
    row_h = 48 if compact else 52
    gap = 8 if compact else 9
    for hero in HERO_ARCHETYPES:
        rect = pygame.Rect(panel.x + 22, y, panel.width - 44, row_h)
        selected = hero["id"] == selected_id
        hovered = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (48, 43, 35) if selected else ((38, 34, 28) if hovered else PANEL), rect, border_radius=10)
        pygame.draw.rect(screen, hero["color"] if selected or hovered else GOLD, rect, 2, border_radius=10)
        pygame.draw.circle(screen, hero["color"], (rect.x + 18, rect.centery), 8)
        screen.blit(small_font.render(hero["name"], True, TEXT), (rect.x + 34, rect.y + 6))
        item_text = f"{hero['basic_item']} + {hero['class_item']}"
        screen.blit(small_font.render(item_text[:42], True, MUTED), (rect.x + 34, rect.y + 26))
        buttons.append(Button("", f"custom_set_{hero['id']}", rect))
        y += row_h + gap
    return buttons


def draw_custom_hero(screen, title_font, font, small_font, mouse, player_index, world_name, selected_set, stats):
    screen.fill(BG)
    compact = is_compact()
    subtitle = f"Set startowy: {selected_set['name']}" if selected_set else "Wybierz set startowy po prawej stronie"
    draw_title(screen, title_font, font, f"Stworz bohatera - Gracz {player_index + 1}", subtitle)
    remaining = 12 - sum(stats.values())
    info_y = 140 if compact else 170
    screen.blit(font.render(f"Pozostale punkty: {remaining}", True, TEXT), (SCREEN_WIDTH / 2 - 300, info_y))
    screen.blit(small_font.render(f"Imie: {world_name or 'domyslne'}", True, MUTED), (SCREEN_WIDTH / 2 - 300, info_y + 36))

    buttons = []
    buttons.extend(draw_start_set_panel(screen, font, small_font, mouse, selected_set, compact))
    panel = _start_set_panel_rect(compact)

    start_y = 230 if compact else 270
    row_h = 50 if compact else 58
    row_step = 60 if compact else 76
    stats_right = panel.x - 40
    row_w = min(680, max(430, stats_right - 60))
    row_x = max(40, stats_right - row_w)
    for idx, stat in enumerate(STAT_NAMES):
        y = start_y + idx * row_step
        row = pygame.Rect(row_x, y, row_w, row_h)
        draw_panel(screen, row, GOLD)
        screen.blit(font.render(stat, True, TEXT), (row.x + 24, row.y + 13))
        minus = Button("-", f"stat_minus_{stat}", (row.right - 210, row.y + 6, 52, 40))
        plus = Button("+", f"stat_plus_{stat}", (row.right - 70, row.y + 6, 52, 40))
        minus.draw(screen, font, mouse)
        plus.draw(screen, font, mouse)
        buttons.extend([minus, plus])
        value_label = font.render(str(stats[stat]), True, TEXT)
        screen.blit(value_label, value_label.get_rect(center=(row.right - 120, row.centery)))

    stats_bottom = start_y + len(STAT_NAMES) * row_step
    confirm_y = min(SCREEN_HEIGHT - 126, stats_bottom + 10)
    confirm = Button("Zatwierdz bohatera", "confirm_custom", (row_x, confirm_y, 380, 54))
    back = Button("Powrot", "back", (row_x + 400, confirm_y, 240, 48))
    confirm.draw(screen, font, mouse)
    back.draw(screen, font, mouse)
    buttons.extend([confirm, back])
    if remaining != 0:
        screen.blit(small_font.render("Rozdziel dokladnie 12 punktow.", True, (235, 170, 95)), (row_x, confirm_y - 28))
    if selected_set is None:
        screen.blit(small_font.render("Wybierz set startowy po prawej stronie.", True, (235, 170, 95)), (row_x, confirm_y - 50))
    return buttons


def draw_initiative(screen, title_font, font, small_font, mouse, players, initiative):
    screen.fill(BG)
    compact = is_compact()
    draw_title(screen, title_font, font, "Rzut na kolejnosc", "Najwyzszy wynik rozpoczyna, a dalsza kolejnosc biegnie zgodnie z ustawieniem graczy")

    panel_y = 155 if compact else 185
    panel_h = min(610, SCREEN_HEIGHT - panel_y - 130)
    panel = pygame.Rect(SCREEN_WIDTH / 2 - 470, panel_y, 940, panel_h)
    draw_panel(screen, panel, GOLD)
    screen.blit(font.render("Wyniki k20", True, TEXT), (panel.x + 28, panel.y + 24))

    rolls = initiative.get("initial_rolls", {})
    y = panel.y + 70
    row_h = 52 if compact else 58
    row_step = 60 if compact else 68
    for index, player in enumerate(players):
        row = pygame.Rect(panel.x + 24, y, panel.width - 48, row_h)
        pygame.draw.rect(screen, (31, 30, 28), row, border_radius=9)
        pygame.draw.rect(screen, player.get("player_color", GOLD), row, 2, border_radius=9)
        pygame.draw.circle(screen, player.get("player_color", GOLD), (row.x + 20, row.centery), 9)
        text = f"Gracz {player.get('player_number', index + 1)} - {player['name']} ({player.get('archetype_name', '-')})"
        screen.blit(font.render(text, True, TEXT), (row.x + 40, row.y + 13))
        roll_text = font.render(str(rolls.get(index, "-")), True, TEXT)
        screen.blit(roll_text, (row.right - 54, row.y + 13))
        y += row_step

    rerolls = initiative.get("reroll_rounds", [])
    if rerolls and y < panel.bottom - 110:
        y += 4
        screen.blit(small_font.render("Dogrywki przy remisie:", True, TEXT), (panel.x + 28, y))
        y += 26
        for round_index, reroll in enumerate(rerolls, start=1):
            parts = [f"{players[index]['name']}: {value}" for index, value in reroll.items()]
            line = f"Dogrywka {round_index}: " + ", ".join(parts)
            if y < panel.bottom - 84:
                screen.blit(small_font.render(line, True, MUTED), (panel.x + 28, y))
            y += 24

    order_names = [players[index]["name"] for index in initiative.get("turn_order", [])]
    order_text = " -> ".join(order_names)
    order_y = panel.bottom - 68
    screen.blit(font.render("Kolejnosc tur:", True, TEXT), (panel.x + 28, order_y))
    draw_lines(screen, small_font, wrap(small_font, order_text, panel.width - 250), panel.x + 188, order_y + 3, MUTED, max_width=panel.width - 220)

    start_y = min(SCREEN_HEIGHT - 76, panel.bottom + 26)
    start = Button("Rozpocznij gre", "start_game", (SCREEN_WIDTH / 2 - 190, start_y, 380, 56))
    start.draw(screen, font, mouse)
    return [start]


def draw_council(screen, title_font, font, small_font, mouse, round_number):
    screen.fill(BG)
    compact = is_compact()
    draw_title(screen, title_font, font, "Rada Bohaterow", f"Zakonczono {COUNCIL_ROUNDS} pelnych rund. Nastepna runda: {round_number}")

    panel_y = 180 if compact else 220
    panel_h = min(470, SCREEN_HEIGHT - panel_y - 135)
    panel = pygame.Rect(SCREEN_WIDTH / 2 - 420, panel_y, 840, panel_h)
    draw_panel(screen, panel, GOLD)
    screen.blit(font.render("Porzadek Rady", True, TEXT), (panel.x + 32, panel.y + 28))
    lines = [
        "1. Rozpatrz Wydarzenie Swiata - w tej wersji ekran testowy.",
        "2. Handel miedzy graczami zostanie podpiety w kolejnym etapie.",
        "3. Po zakonczeniu Rady licznik cyklu wraca do 1/5.",
        "4. Nastepna ture rozpoczyna gracz wynikajacy z ustalonej kolejnosci.",
    ]
    line_h = 44 if compact else 54
    draw_lines(screen, font, lines, panel.x + 36, panel.y + 86, MUTED, line_h=line_h, max_width=panel.width - 72)

    close_y = min(SCREEN_HEIGHT - 76, panel.bottom + 26)
    close = Button("Zakoncz Rade", "close_council", (SCREEN_WIDTH / 2 - 190, close_y, 380, 56))
    close.draw(screen, font, mouse)
    return [close]


def draw_multiplayer(screen, title_font, font, mouse):
    screen.fill(BG)
    draw_title(screen, title_font, font, "Multiplayer", "Tryb sieciowy i LAN dodamy pozniej")
    buttons = vertical_buttons([("Powrot", "back")], 330 if is_compact() else 390)
    for button in buttons:
        button.draw(screen, font, mouse)
    return buttons
