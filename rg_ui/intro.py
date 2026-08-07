from pathlib import Path

import pygame

from rg_core.data import GOLD, MUTED, PANEL, PANEL_DARK, SCREEN_HEIGHT, SCREEN_WIDTH, TEXT
from rg_ui.common import Button, draw_lines, draw_panel, wrap

ROOT_DIR = Path(__file__).resolve().parents[1]
INTRO_DIRS = [
    ROOT_DIR / "Grafiki" / "intro",
    ROOT_DIR / "Grafiki" / "Intro",
    ROOT_DIR / "Grafiki",
    ROOT_DIR,
]

INTRO_FILE_STEMS = [
    ["intro_1", "intro1", "intro 1", "Intro 1", "intro_01"],
    ["intro_2", "intro2", "intro 2", "Intro 2", "intro_02"],
    ["intro_3", "intro3", "intro 3", "Intro 3", "intro_03"],
]

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]

INTRO_TEXTS = [
    "TODO: Wklej tutaj tekst do pierwszego obrazka intro. Opisz spokojny poczatek swiata i miejsce, z ktorego rusza opowiesc.",
    "TODO: Wklej tutaj tekst do drugiego obrazka intro. Opisz narastajace zagrozenie, wojne, niepokoj albo chaos w krainie.",
    "TODO: Wklej tutaj tekst do trzeciego obrazka intro. Opisz bohaterow, ktorzy wyruszaja po slawe, bogactwo i ratunek dla krainy.",
]

_IMAGE_CACHE = {}


def intro_count():
    return len(INTRO_FILE_STEMS)


def find_intro_image_path(index):
    if index < 0 or index >= len(INTRO_FILE_STEMS):
        return None
    for directory in INTRO_DIRS:
        for stem in INTRO_FILE_STEMS[index]:
            for extension in IMAGE_EXTENSIONS:
                path = directory / f"{stem}{extension}"
                if path.exists():
                    return path
    return None


def load_cover_image(path, size):
    cache_key = (str(path), size)
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

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
    _IMAGE_CACHE[cache_key] = result
    return result


def draw_intro_fallback(screen, index, title_font, font):
    screen.fill((16, 18, 22))
    sw, sh = screen.get_size()
    for step in range(18):
        color = 22 + step * 4
        rect = pygame.Rect(step * 38, step * 26, sw - step * 76, sh - step * 52)
        if rect.width > 0 and rect.height > 0:
            pygame.draw.rect(screen, (color, color - 2, max(12, color - 8)), rect, 1)
    title = title_font.render(f"Brak obrazka intro {index + 1}", True, TEXT)
    screen.blit(title, title.get_rect(center=(sw / 2, sh / 2 - 30)))
    hint = font.render("Wrzuc plik jako intro_1.png, intro_2.png, intro_3.png do Grafiki/intro albo Grafiki.", True, MUTED)
    screen.blit(hint, hint.get_rect(center=(sw / 2, sh / 2 + 24)))


def draw_dark_overlay(screen):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 58))
    screen.blit(overlay, (0, 0))


def draw_intro_text_box(screen, title_font, font, small_font, index, text):
    sw, sh = screen.get_size()
    panel_w = min(1180, sw - 120)
    panel_h = 210
    panel = pygame.Rect((sw - panel_w) // 2, sh - panel_h - 42, panel_w, panel_h)
    draw_panel(screen, panel, GOLD)

    title = f"Rise & Glory - Intro {index + 1}/{intro_count()}"
    screen.blit(font.render(title, True, TEXT), (panel.x + 28, panel.y + 22))

    text_area = pygame.Rect(panel.x + 28, panel.y + 60, panel.width - 56, 92)
    wrapped = []
    for paragraph in text.split("\n"):
        wrapped.extend(wrap(small_font, paragraph, text_area.width))
    draw_lines(screen, small_font, wrapped[:5], text_area.x, text_area.y, MUTED, line_h=22, max_width=text_area.width)

    next_label = "Dalej" if index < intro_count() - 1 else "Przejdz do inicjatywy"
    next_button = Button(next_label, "intro_next", (panel.right - 250, panel.bottom - 56, 220, 38))
    skip_button = Button("Pomin intro", "intro_skip", (panel.x + 28, panel.bottom - 56, 170, 38))
    next_button.draw(screen, font, pygame.mouse.get_pos())
    skip_button.draw(screen, font, pygame.mouse.get_pos())
    return [skip_button, next_button]


def draw_intro_screen(screen, title_font, font, small_font, mouse_pos, intro_index):
    index = max(0, min(intro_index, intro_count() - 1))
    path = find_intro_image_path(index)
    if path:
        image = load_cover_image(path, screen.get_size())
        if image:
            screen.blit(image, (0, 0))
        else:
            draw_intro_fallback(screen, index, title_font, font)
    else:
        draw_intro_fallback(screen, index, title_font, font)

    draw_dark_overlay(screen)
    return draw_intro_text_box(screen, title_font, font, small_font, index, INTRO_TEXTS[index])
