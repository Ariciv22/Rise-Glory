from pathlib import Path

import pygame

from rg_data import BG, COUNCIL_ROUNDS, GOLD, MUTED, SCREEN_HEIGHT, TEXT
from rg_ui import Button, draw_lines

ROOT_DIR = Path(__file__).resolve().parent
COUNCIL_BACKGROUND_PATH = ROOT_DIR / "Grafiki" / "rada_bohaterów.png"
_BACKGROUND_CACHE = {"size": None, "surface": None}
_SOURCE_CACHE = {"loaded": False, "surface": None}


def _is_compact():
    return SCREEN_HEIGHT < 1050


def _load_source():
    if _SOURCE_CACHE["loaded"]:
        return _SOURCE_CACHE["surface"]

    _SOURCE_CACHE["loaded"] = True
    if not COUNCIL_BACKGROUND_PATH.exists():
        return None

    try:
        source = pygame.image.load(str(COUNCIL_BACKGROUND_PATH)).convert()
    except (OSError, pygame.error):
        source = None

    _SOURCE_CACHE["surface"] = source
    return source


def _load_background(size):
    size = tuple(size)
    if _BACKGROUND_CACHE["size"] == size:
        return _BACKGROUND_CACHE["surface"]

    source = _load_source()
    if source is None:
        _BACKGROUND_CACHE["size"] = size
        _BACKGROUND_CACHE["surface"] = None
        return None

    screen_width, screen_height = size
    image_width, image_height = source.get_size()

    cover_scale = max(screen_width / image_width, screen_height / image_height)
    cover = pygame.transform.smoothscale(
        source,
        (
            max(1, int(image_width * cover_scale)),
            max(1, int(image_height * cover_scale)),
        ),
    )
    background = pygame.Surface(size)
    background.blit(
        cover,
        (
            (screen_width - cover.get_width()) // 2,
            (screen_height - cover.get_height()) // 2,
        ),
    )

    shade = pygame.Surface(size, pygame.SRCALPHA)
    shade.fill((4, 7, 10, 105))
    background.blit(shade, (0, 0))

    portrait_scale = min(
        (screen_width * 0.62) / image_width,
        (screen_height * 0.96) / image_height,
    )
    portrait = pygame.transform.smoothscale(
        source,
        (
            max(1, int(image_width * portrait_scale)),
            max(1, int(image_height * portrait_scale)),
        ),
    )
    background.blit(
        portrait,
        (
            max(12, int(screen_width * 0.03)),
            (screen_height - portrait.get_height()) // 2,
        ),
    )

    _BACKGROUND_CACHE["size"] = size
    _BACKGROUND_CACHE["surface"] = background
    return background


def _draw_title(screen, title_font, font, title, subtitle):
    compact = _is_compact()
    title_y, subtitle_y = (70, 112) if compact else (90, 138)
    center_x = screen.get_width() / 2

    title_label = title_font.render(title, True, TEXT)
    subtitle_label = font.render(subtitle, True, MUTED)
    screen.blit(title_label, title_label.get_rect(center=(center_x, title_y)))
    screen.blit(subtitle_label, subtitle_label.get_rect(center=(center_x, subtitle_y)))


def draw_council(screen, title_font, font, small_font, mouse, round_number):
    background = _load_background(screen.get_size())
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BG)

    compact = _is_compact()
    _draw_title(
        screen,
        title_font,
        font,
        "Rada Bohaterow",
        f"Zakonczono {COUNCIL_ROUNDS} pelnych rund. Nastepna runda: {round_number}",
    )

    screen_width, screen_height = screen.get_size()
    panel_width = min(700, max(540, int(screen_width * 0.39)))
    panel_y = 180 if compact else 220
    panel_height = min(470, screen_height - panel_y - 135)
    panel = pygame.Rect(
        max(24, screen_width - panel_width - 48),
        panel_y,
        panel_width,
        panel_height,
    )

    panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
    pygame.draw.rect(
        panel_surface,
        (18, 20, 23, 205),
        panel_surface.get_rect(),
        border_radius=12,
    )
    pygame.draw.rect(
        panel_surface,
        GOLD,
        panel_surface.get_rect(),
        2,
        border_radius=12,
    )
    screen.blit(panel_surface, panel.topleft)

    screen.blit(
        font.render("Porzadek Rady", True, TEXT),
        (panel.x + 32, panel.y + 28),
    )
    lines = [
        "1. Rozpatrz Wydarzenie Swiata - w tej wersji ekran testowy.",
        "2. Handel miedzy graczami zostanie podpiety w kolejnym etapie.",
        "3. Po zakonczeniu Rady licznik cyklu wraca do 1/5.",
        "4. Nastepna ture rozpoczyna gracz wynikajacy z ustalonej kolejnosci.",
    ]
    line_height = 44 if compact else 54
    draw_lines(
        screen,
        font,
        lines,
        panel.x + 36,
        panel.y + 86,
        MUTED,
        line_h=line_height,
        max_width=panel.width - 72,
    )

    close_y = min(screen_height - 76, panel.bottom + 26)
    close = Button(
        "Zakoncz Rade",
        "close_council",
        (panel.centerx - 190, close_y, 380, 56),
    )
    close.draw(screen, font, mouse)
    return [close]
