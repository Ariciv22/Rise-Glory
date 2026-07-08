from pathlib import Path

import pygame

from rg_data import BG, GOLD, MUTED, PANEL, PANEL_DARK, SCREEN_HEIGHT, SCREEN_WIDTH, TEXT
from rg_ui import Button, draw_lines, draw_panel

ROOT_DIR = Path(__file__).resolve().parent
CITY_GRAPHICS_DIRS = [
    ROOT_DIR / "Grafiki" / "grafiki_miast",
    ROOT_DIR / "grafiki_miast",
]

CITY_PLACES = [
    ("Rynek", "city_market", "Kupcy, towary i handel. Mechanike dodamy pozniej."),
    ("Karczma", "city_tavern", "Plotki, odpoczynek i najemnicy. Mechanike dodamy pozniej."),
    ("Tablica ogloszen", "city_board", "Questy miasta pojawia sie w kolejnym kroku."),
    ("Kowal", "city_blacksmith", "Ekwipunek i naprawy. Mechanike dodamy pozniej."),
    ("Rada miasta", "city_council", "Decyzje, reputacja i dyplomacja. Mechanike dodamy pozniej."),
]


def find_city_background(city):
    background = city.get("background") or ""
    names = [background] if background else []
    if city.get("name") == "Lirion":
        names.append("lirion_miasto")
    for directory in CITY_GRAPHICS_DIRS:
        for name in names:
            for ext in ["", ".png", ".jpg", ".jpeg", ".webp"]:
                path = directory / f"{name}{ext}"
                if path.exists():
                    return path
    return None


def load_city_background(city, size):
    path = find_city_background(city)
    if not path:
        return None
    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None
    iw, ih = image.get_size()
    sw, sh = size
    scale = max(sw / iw, sh / ih)
    scaled = pygame.transform.smoothscale(image, (int(iw * scale), int(ih * scale)))
    result = pygame.Surface(size, pygame.SRCALPHA)
    result.blit(scaled, ((sw - scaled.get_width()) // 2, (sh - scaled.get_height()) // 2))
    return result


def draw_fallback_background(screen):
    screen.fill((19, 15, 12))
    sw, sh = screen.get_size()
    for i in range(18):
        shade = 22 + i * 4
        rect = pygame.Rect(i * 35, i * 24, sw - i * 70, sh - i * 48)
        if rect.width > 0 and rect.height > 0:
            pygame.draw.rect(screen, (shade, 25, 16), rect, 1)


def draw_city_screen(screen, title_font, font, small_font, mouse_pos, city, selected_place=None):
    bg = load_city_background(city, screen.get_size())
    if bg:
        screen.blit(bg, (0, 0))
    else:
        draw_fallback_background(screen)

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 95))
    screen.blit(overlay, (0, 0))

    header = pygame.Rect(40, 34, SCREEN_WIDTH - 80, 112)
    draw_panel(screen, header, GOLD)
    city_type = city.get("type_name", "Miasto")
    title = f"{city_type}: {city.get('name', 'Miasto')}"
    screen.blit(title_font.render(title, True, TEXT), (header.x + 30, header.y + 22))
    subtitle = "Ekran miasta - wybierz miejsce, do ktorego chcesz pojsc."
    screen.blit(font.render(subtitle, True, MUTED), (header.x + 32, header.y + 72))

    left = pygame.Rect(58, 190, 360, 520)
    draw_panel(screen, left, GOLD)
    screen.blit(font.render("Miejsca w miescie", True, TEXT), (left.x + 24, left.y + 24))

    buttons = []
    y = left.y + 78
    for label, action, _desc in CITY_PLACES:
        button = Button(label, action, (left.x + 24, y, left.width - 48, 52))
        button.draw(screen, font, mouse_pos, active=(selected_place == action))
        buttons.append(button)
        y += 66

    back = Button("Powrot na mape", "back_to_map", (left.x + 24, left.bottom - 72, left.width - 48, 52))
    back.draw(screen, font, mouse_pos)
    buttons.append(back)

    info = pygame.Rect(450, 190, SCREEN_WIDTH - 508, 520)
    draw_panel(screen, info, GOLD)
    chosen = next((place for place in CITY_PLACES if place[1] == selected_place), None)
    if chosen:
        title_text = chosen[0]
        lines = [chosen[2], "Tutaj pozniej pojawi sie osobny panel tej lokacji."]
    else:
        title_text = "Wybierz miejsce"
        lines = [
            "Kliknij jedno z miejsc po lewej stronie.",
            "Na razie to makieta nawigacji miasta.",
            "Nastepny krok: podepniemy konkretne akcje albo questy.",
        ]
    screen.blit(font.render(title_text, True, TEXT), (info.x + 28, info.y + 28))
    draw_lines(screen, small_font, lines, info.x + 30, info.y + 72, MUTED, line_h=24, max_width=info.width - 60)

    return buttons
