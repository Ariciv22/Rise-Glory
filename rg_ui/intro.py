from pathlib import Path

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_ui.common import Button, draw_lines, draw_panel, wrap

ROOT_DIR = Path(__file__).resolve().parents[1]

INTRO_DIRS = [
    ROOT_DIR / "Grafiki" / "intro",
    ROOT_DIR / "Grafiki" / "Intro",
    ROOT_DIR / "Grafiki",
    ROOT_DIR,
]

INTRO_UI_DIR = ROOT_DIR / "Grafiki" / "ui_intra"

INTRO_FRAME_STEMS = [
    "ramka1",
    "ramka",
    "frame",
    "intro_frame",
    "intro-frame",
    "text_frame",
    "text-frame",
    "panel",
    "intro_panel",
]

INTRO_SKIP_ICON_STEMS = [
    "skip",
    "skip_icon",
    "skip-icon",
    "intro_skip",
    "pomin",
    "pomin_intro",
]

INTRO_FORWARD_ICON_STEMS = [
    "forward",
    "forward_icon",
    "forward-icon",
    "intro_forward",
    "next",
    "next_icon",
    "dalej",
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


def _find_image_by_stems(directory, stems):
    if not directory.exists():
        return None

    for stem in stems:
        for extension in IMAGE_EXTENSIONS:
            path = directory / f"{stem}{extension}"
            if path.exists():
                return path

    # Dodatkowy fallback na podobna nazwe pliku, np. ramka2.png.
    lowered = [stem.lower().replace("-", "_") for stem in stems]
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        candidate = path.stem.lower().replace("-", "_")
        if any(token in candidate or candidate in token for token in lowered):
            return path

    return None


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
    cache_key = (str(path), tuple(size), "cover")
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None

    iw, ih = image.get_size()
    sw, sh = size
    if iw <= 0 or ih <= 0 or sw <= 0 or sh <= 0:
        return None

    scale = max(sw / iw, sh / ih)
    scaled = pygame.transform.smoothscale(
        image,
        (max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))),
    )

    result = pygame.Surface(size, pygame.SRCALPHA)
    result.blit(
        scaled,
        ((sw - scaled.get_width()) // 2, (sh - scaled.get_height()) // 2),
    )
    _IMAGE_CACHE[cache_key] = result
    return result


def _trim_transparent(surface):
    """Usuwa przezroczyste marginesy z assetu UI.

    Wygenerowane grafiki ramki i ikon maja sporo pustego miejsca dookola.
    Bez przyciecia widoczna ramka i symbole wygladaja jak przesuniete w gore/dol.
    """
    try:
        bounds = surface.get_bounding_rect(min_alpha=8)
    except TypeError:
        bounds = surface.get_bounding_rect()

    if bounds.width <= 0 or bounds.height <= 0:
        return surface

    if bounds.size == surface.get_size() and bounds.topleft == (0, 0):
        return surface

    return surface.subsurface(bounds).copy()


def _load_ui_image(path):
    if not path:
        return None

    cache_key = (str(path), "ui-source-trimmed")
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None

    image = _trim_transparent(image)
    _IMAGE_CACHE[cache_key] = image
    return image


def _scaled_ui_image(path, size):
    if not path:
        return None

    width = max(1, int(size[0]))
    height = max(1, int(size[1]))
    cache_key = (str(path), (width, height), "ui-scaled-trimmed")
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    source = _load_ui_image(path)
    if source is None:
        return None

    result = pygame.transform.smoothscale(source, (width, height))
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

    hint = font.render(
        "Wrzuc plik jako intro_1.png, intro_2.png, intro_3.png do Grafiki/intro albo Grafiki.",
        True,
        MUTED,
    )
    screen.blit(hint, hint.get_rect(center=(sw / 2, sh / 2 + 24)))


def draw_dark_overlay(screen):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 46))
    screen.blit(overlay, (0, 0))


def _draw_icon(screen, icon_path, target_rect):
    source = _load_ui_image(icon_path)
    if source is None:
        return False

    iw, ih = source.get_size()
    if iw <= 0 or ih <= 0:
        return False

    # Sam symbol ma byc wycentrowany W pustym polu przycisku.
    max_w = max(1, int(target_rect.width * 0.44))
    max_h = max(1, int(target_rect.height * 0.62))
    scale = min(max_w / iw, max_h / ih)

    size = (
        max(1, int(round(iw * scale))),
        max(1, int(round(ih * scale))),
    )
    icon = _scaled_ui_image(icon_path, size)
    if icon is None:
        return False

    screen.blit(icon, icon.get_rect(center=target_rect.center))
    return True


def _draw_custom_intro_box(screen, font, small_font, index, text, frame_path):
    sw, sh = screen.get_size()
    source = _load_ui_image(frame_path)
    if source is None:
        return None

    iw, ih = source.get_size()
    if iw <= 0 or ih <= 0:
        return None

    # Zmniejszamy cala ramke proporcjonalnie. Szerokosc i wysokosc dostaja
    # dokladnie ten sam wspolczynnik, wiec asset nigdy nie jest rozciagany ani
    # zgniatany w jednej osi.
    full_w = min(sw - 8, 1720)
    target_w = max(1, int(round(full_w * 0.50)))
    target_h = max(1, int(round(target_w * ih / iw)))

    # Dodatkowy bezpiecznik na bardzo niskie okna nadal skaluje obie osie
    # wspolnie, zachowujac oryginalne proporcje ramki.
    max_h = max(125, int(sh * 0.26))
    if target_h > max_h:
        scale = max_h / target_h
        target_w = max(1, int(round(target_w * scale)))
        target_h = max(1, int(round(target_h * scale)))

    frame = _scaled_ui_image(frame_path, (target_w, target_h))
    if frame is None:
        return None

    panel = frame.get_rect()
    panel.midbottom = (sw // 2, sh + 1)
    screen.blit(frame, panel.topleft)

    text_area = pygame.Rect(
        panel.x + int(panel.width * 0.075),
        panel.y + int(panel.height * 0.19),
        int(panel.width * 0.85),
        int(panel.height * 0.47),
    )

    wrapped = []
    for paragraph in text.split("\n"):
        wrapped.extend(wrap(small_font, paragraph, text_area.width))

    line_h = max(18, int(small_font.get_height() * 1.14))
    max_lines = max(1, text_area.height // line_h)
    draw_lines(
        screen,
        small_font,
        wrapped[:max_lines],
        text_area.x,
        text_area.y,
        TEXT,
        line_h=line_h,
        max_width=text_area.width,
    )

    counter = small_font.render(f"{index + 1}/{intro_count()}", True, MUTED)
    screen.blit(
        counter,
        (
            panel.right - int(panel.width * 0.075) - counter.get_width(),
            panel.y + int(panel.height * 0.10),
        ),
    )

    # Srodki hitboxow trafiaja w geometryczne srodki ozdobnych pol ramki.
    # Pola sa lekko odsuniete od samych krawedzi panelu, wiec oba srodki
    # przesuwamy symetrycznie do wewnatrz: Skip w prawo, Forward w lewo.
    button_w = max(1, int(panel.width * 0.15))
    button_h = max(1, int(panel.height * 0.15))
    button_center_y = panel.y + int(panel.height * 0.875)

    skip_rect = pygame.Rect(0, 0, button_w, button_h)
    skip_rect.center = (
        panel.x + int(panel.width * 0.1175),
        button_center_y,
    )

    next_rect = pygame.Rect(0, 0, button_w, button_h)
    next_rect.center = (
        panel.x + int(panel.width * 0.8825),
        button_center_y,
    )

    skip_icon = _find_image_by_stems(INTRO_UI_DIR, INTRO_SKIP_ICON_STEMS)
    forward_icon = _find_image_by_stems(INTRO_UI_DIR, INTRO_FORWARD_ICON_STEMS)

    _draw_icon(screen, skip_icon, skip_rect)
    _draw_icon(screen, forward_icon, next_rect)

    # Button sluzy tylko jako klikany hitbox. Nie rysujemy standardowego buttona Pygame.
    return [
        Button("", "intro_skip", skip_rect),
        Button("", "intro_next", next_rect),
    ]


def _draw_fallback_intro_box(screen, font, small_font, index, text):
    sw, sh = screen.get_size()
    panel_w = min(1180, sw - 80)
    panel_h = 190
    panel = pygame.Rect((sw - panel_w) // 2, sh - panel_h, panel_w, panel_h)
    draw_panel(screen, panel, GOLD)

    counter = small_font.render(f"{index + 1}/{intro_count()}", True, MUTED)
    screen.blit(counter, (panel.right - counter.get_width() - 24, panel.y + 18))

    text_area = pygame.Rect(panel.x + 28, panel.y + 34, panel.width - 56, 92)
    wrapped = []
    for paragraph in text.split("\n"):
        wrapped.extend(wrap(small_font, paragraph, text_area.width))

    draw_lines(
        screen,
        small_font,
        wrapped[:5],
        text_area.x,
        text_area.y,
        MUTED,
        line_h=22,
        max_width=text_area.width,
    )

    next_button = Button("Dalej", "intro_next", (panel.right - 220, panel.bottom - 48, 190, 36))
    skip_button = Button("Pomin intro", "intro_skip", (panel.x + 28, panel.bottom - 48, 160, 36))
    next_button.draw(screen, font, pygame.mouse.get_pos())
    skip_button.draw(screen, font, pygame.mouse.get_pos())
    return [skip_button, next_button]


def draw_intro_text_box(screen, title_font, font, small_font, index, text):
    frame_path = _find_image_by_stems(INTRO_UI_DIR, INTRO_FRAME_STEMS)
    if frame_path:
        custom_buttons = _draw_custom_intro_box(
            screen,
            font,
            small_font,
            index,
            text,
            frame_path,
        )
        if custom_buttons is not None:
            return custom_buttons

    return _draw_fallback_intro_box(screen, font, small_font, index, text)


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
    return draw_intro_text_box(
        screen,
        title_font,
        font,
        small_font,
        index,
        INTRO_TEXTS[index],
    )
