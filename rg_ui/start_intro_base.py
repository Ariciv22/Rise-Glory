import re
from pathlib import Path

import pygame

from rg_core.data import GOLD, MUTED, PANEL, TEXT

ROOT_DIR = Path(__file__).resolve().parents[1]
INTRO_DIRS = [
    ROOT_DIR / "intro_final",
    ROOT_DIR / "Intro_final",
    ROOT_DIR / "Grafiki" / "intro_final",
    ROOT_DIR / "Grafiki" / "Intro_final",
]
MUSIC_DIRS = [ROOT_DIR / "music", ROOT_DIR / "Music"]
MAP_MUSIC_DIRS = [
    ROOT_DIR / "music" / "Kolejka_muzyczna_na_mapie" / "lv1_swiata",
    ROOT_DIR / "Music" / "Kolejka_muzyczna_na_mapie" / "lv1_swiata",
]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MUSIC_EXTENSIONS = {".mp3", ".ogg", ".wav", ".flac"}
INTRO_SECONDS_PER_IMAGE = 10
MAP_MUSIC_END_EVENT = pygame.USEREVENT + 1
MUSIC_VOLUME_STEP = 0.1

_IMAGE_CACHE = {}
_MUSIC_STARTED = False
_MUSIC_VOLUME = 1.0
_MAP_MUSIC_TRACKS = []
_MAP_MUSIC_INDEX = -1
_MAP_MUSIC_STARTED = False
_GAME_SESSION_ACTIVE = False
_PAUSE_MENU_OPEN = False
_PAUSE_OPTIONS_OPEN = False
_ORIGINAL_EVENT_GET = pygame.event.get
_ORIGINAL_DISPLAY_FLIP = pygame.display.flip
_EVENT_HOOK_INSTALLED = False
_DISPLAY_HOOK_INSTALLED = False
_FONT_CACHE = {}


def _natural_key(path):
    parts = re.split(r"(\d+)", path.stem.lower())
    return [int(part) if part.isdigit() else part for part in parts]


def find_intro_images():
    images = []
    seen = set()
    for directory in INTRO_DIRS:
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and path not in seen:
                images.append(path)
                seen.add(path)
    return sorted(images, key=_natural_key)


def intro_count():
    return len(find_intro_images())


def _load_cover_image(path, size):
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


def _draw_fallback(screen, title_font, font):
    screen.fill((13, 16, 20))
    sw, sh = screen.get_size()
    title = title_font.render("Brak obrazow intro", True, TEXT)
    hint = font.render("Wrzuc obrazy do folderu intro_final.", True, MUTED)
    screen.blit(title, title.get_rect(center=(sw / 2, sh / 2 - 28)))
    screen.blit(hint, hint.get_rect(center=(sw / 2, sh / 2 + 22)))


def draw_start_intro(screen, title_font, font, intro_index):
    images = find_intro_images()
    if not images:
        _draw_fallback(screen, title_font, font)
        return

    index = max(0, min(intro_index, len(images) - 1))
    image = _load_cover_image(images[index], screen.get_size())
    if image:
        screen.blit(image, (0, 0))
    else:
        _draw_fallback(screen, title_font, font)
        return

    sw, sh = screen.get_size()
    overlay = pygame.Surface((sw, 96), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 95))
    screen.blit(overlay, (0, sh - 96))
    counter = font.render(f"Intro {index + 1}/{len(images)}  |  spacja / enter / klik - dalej", True, TEXT)
    screen.blit(counter, counter.get_rect(center=(sw / 2, sh - 48)))


def find_intro_music():
    for directory in MUSIC_DIRS:
        if not directory.exists():
            continue
        music_files = [path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in MUSIC_EXTENSIONS]
        preferred = [path for path in music_files if "the dawn of empires" in path.stem.lower()]
        if preferred:
            return sorted(preferred, key=_natural_key)[0]
        if music_files:
            return sorted(music_files, key=_natural_key)[0]
    return None


def find_map_music():
    tracks = []
    seen = set()
    for directory in MAP_MUSIC_DIRS:
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if not path.is_file() or path.suffix.lower() not in MUSIC_EXTENSIONS:
                continue
            normalized = str(path.resolve()).lower()
            if normalized in seen:
                continue
            tracks.append(path)
            seen.add(normalized)
    return sorted(tracks, key=_natural_key)


def get_music_volume():
    return _MUSIC_VOLUME


def set_music_volume(value):
    global _MUSIC_VOLUME
    _MUSIC_VOLUME = max(0.0, min(1.0, round(float(value), 2)))
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(_MUSIC_VOLUME)
    except pygame.error:
        pass
    return _MUSIC_VOLUME


def change_music_volume(delta):
    return set_music_volume(_MUSIC_VOLUME + delta)


def start_intro_music():
    global _MUSIC_STARTED
    if _MUSIC_STARTED:
        return False
    music_path = find_intro_music()
    if not music_path:
        return False
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(str(music_path))
        pygame.mixer.music.set_volume(_MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
        _MUSIC_STARTED = True
        return True
    except pygame.error:
        return False


def stop_intro_music():
    global _MUSIC_STARTED
    if _MUSIC_STARTED:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
            _MUSIC_STARTED = False
        except pygame.error:
            return False
    start_map_music_queue()
    return True


def _play_map_track(start_index):
    global _MAP_MUSIC_INDEX, _MAP_MUSIC_STARTED
    if not _MAP_MUSIC_TRACKS:
        return False

    for offset in range(len(_MAP_MUSIC_TRACKS)):
        index = (start_index + offset) % len(_MAP_MUSIC_TRACKS)
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.set_endevent(MAP_MUSIC_END_EVENT)
            pygame.mixer.music.load(str(_MAP_MUSIC_TRACKS[index]))
            pygame.mixer.music.set_volume(_MUSIC_VOLUME)
            pygame.mixer.music.play()
            _MAP_MUSIC_INDEX = index
            _MAP_MUSIC_STARTED = True
            return True
        except (pygame.error, OSError):
            continue

    _MAP_MUSIC_STARTED = False
    return False


def _font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont("arial", size, bold=bold)
    return _FONT_CACHE[key]


def _pause_layout():
    screen = pygame.display.get_surface()
    if screen is None:
        return {}

    sw, sh = screen.get_size()
    panel_w = min(520, max(390, sw - 80))
    panel_h = 430 if _PAUSE_OPTIONS_OPEN else 370
    panel = pygame.Rect((sw - panel_w) // 2, (sh - panel_h) // 2, panel_w, panel_h)
    button_w = min(340, panel_w - 80)
    button_h = 58
    button_x = panel.centerx - button_w // 2

    layout = {"panel": panel}
    if _PAUSE_OPTIONS_OPEN:
        control_y = panel.y + 190
        layout.update(
            {
                "minus": pygame.Rect(panel.x + 56, control_y, 86, 58),
                "plus": pygame.Rect(panel.right - 142, control_y, 86, 58),
                "back": pygame.Rect(button_x, panel.bottom - 86, button_w, button_h),
                "bar": pygame.Rect(panel.x + 86, panel.y + 142, panel_w - 172, 18),
            }
        )
    else:
        layout.update(
            {
                "resume": pygame.Rect(button_x, panel.y + 154, button_w, button_h),
                "options": pygame.Rect(button_x, panel.y + 230, button_w, button_h),
            }
        )
    return layout


def _draw_pause_button(screen, rect, label, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)
    shadow = rect.move(0, 5)
    pygame.draw.rect(screen, (0, 0, 0, 110), shadow, border_radius=10)
    fill = (66, 76, 82) if hovered else (38, 44, 49)
    border = (210, 165, 90) if hovered else (135, 103, 54)
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, border, rect, 2, border_radius=10)
    text = _font(22, True).render(label, True, TEXT)
    screen.blit(text, text.get_rect(center=rect.center))


def _draw_pause_overlay():
    if not _PAUSE_MENU_OPEN:
        return

    screen = pygame.display.get_surface()
    if screen is None:
        return

    layout = _pause_layout()
    panel = layout.get("panel")
    if panel is None:
        return

    sw, sh = screen.get_size()
    dim = pygame.Surface((sw, sh), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 178))
    screen.blit(dim, (0, 0))

    pygame.draw.rect(screen, (0, 0, 0, 150), panel.move(0, 8), border_radius=18)
    pygame.draw.rect(screen, PANEL, panel, border_radius=18)
    pygame.draw.rect(screen, GOLD, panel, 3, border_radius=18)

    mouse = pygame.mouse.get_pos()
    title_text = "OPCJE" if _PAUSE_OPTIONS_OPEN else "PAUZA"
    title = _font(40, True).render(title_text, True, TEXT)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 58)))

    if _PAUSE_OPTIONS_OPEN:
        label = _font(20, True).render("GŁOŚNOŚĆ MUZYKI", True, MUTED)
        screen.blit(label, label.get_rect(center=(panel.centerx, panel.y + 112)))

        bar = layout["bar"]
        pygame.draw.rect(screen, (22, 25, 28), bar, border_radius=9)
        fill_width = int(bar.width * _MUSIC_VOLUME)
        if fill_width > 0:
            pygame.draw.rect(screen, GOLD, (bar.x, bar.y, fill_width, bar.height), border_radius=9)
        pygame.draw.rect(screen, (120, 105, 75), bar, 2, border_radius=9)

        percent = _font(30, True).render(f"{int(round(_MUSIC_VOLUME * 100))}%", True, TEXT)
        screen.blit(percent, percent.get_rect(center=(panel.centerx, layout["minus"].centery)))

        _draw_pause_button(screen, layout["minus"], "−", mouse)
        _draw_pause_button(screen, layout["plus"], "+", mouse)
        _draw_pause_button(screen, layout["back"], "WRÓĆ", mouse)
    else:
        subtitle = _font(18).render("Gra została wstrzymana", True, MUTED)
        screen.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.y + 108)))
        _draw_pause_button(screen, layout["resume"], "WZNÓW GRĘ", mouse)
        _draw_pause_button(screen, layout["options"], "OPCJE", mouse)

    hint = _font(15).render("ESC — powrót", True, MUTED)
    screen.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 24)))


def _handle_pause_event(event):
    global _PAUSE_MENU_OPEN, _PAUSE_OPTIONS_OPEN

    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        if _PAUSE_OPTIONS_OPEN:
            _PAUSE_OPTIONS_OPEN = False
        else:
            _PAUSE_MENU_OPEN = False
        return True

    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        layout = _pause_layout()
        if _PAUSE_OPTIONS_OPEN:
            if layout.get("minus") and layout["minus"].collidepoint(event.pos):
                change_music_volume(-MUSIC_VOLUME_STEP)
            elif layout.get("plus") and layout["plus"].collidepoint(event.pos):
                change_music_volume(MUSIC_VOLUME_STEP)
            elif layout.get("back") and layout["back"].collidepoint(event.pos):
                _PAUSE_OPTIONS_OPEN = False
        else:
            if layout.get("resume") and layout["resume"].collidepoint(event.pos):
                _PAUSE_MENU_OPEN = False
            elif layout.get("options") and layout["options"].collidepoint(event.pos):
                _PAUSE_OPTIONS_OPEN = True
        return True

    return event.type not in {pygame.QUIT, pygame.VIDEORESIZE}


def _install_map_music_event_hook():
    global _EVENT_HOOK_INSTALLED
    if _EVENT_HOOK_INSTALLED:
        return

    def hooked_event_get(*args, **kwargs):
        global _PAUSE_MENU_OPEN, _PAUSE_OPTIONS_OPEN
        events = _ORIGINAL_EVENT_GET(*args, **kwargs)
        filtered_events = []
        for event in events:
            if event.type == MAP_MUSIC_END_EVENT:
                play_next_map_music()
                continue

            if _PAUSE_MENU_OPEN:
                if _handle_pause_event(event):
                    continue
                filtered_events.append(event)
                continue

            if _GAME_SESSION_ACTIVE and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                _PAUSE_MENU_OPEN = True
                _PAUSE_OPTIONS_OPEN = False
                continue

            filtered_events.append(event)
        return filtered_events

    pygame.event.get = hooked_event_get
    _EVENT_HOOK_INSTALLED = True


def _install_pause_display_hook():
    global _DISPLAY_HOOK_INSTALLED
    if _DISPLAY_HOOK_INSTALLED:
        return

    def hooked_display_flip():
        _draw_pause_overlay()
        return _ORIGINAL_DISPLAY_FLIP()

    pygame.display.flip = hooked_display_flip
    _DISPLAY_HOOK_INSTALLED = True


def start_map_music_queue():
    global _MAP_MUSIC_TRACKS, _MAP_MUSIC_INDEX, _GAME_SESSION_ACTIVE
    _GAME_SESSION_ACTIVE = True
    _install_map_music_event_hook()
    _install_pause_display_hook()

    if _MAP_MUSIC_STARTED:
        return False

    _MAP_MUSIC_TRACKS = find_map_music()
    _MAP_MUSIC_INDEX = -1
    if not _MAP_MUSIC_TRACKS:
        return False
    return _play_map_track(0)


def play_next_map_music():
    if not _MAP_MUSIC_STARTED or not _MAP_MUSIC_TRACKS:
        return False
    return _play_map_track(_MAP_MUSIC_INDEX + 1)


def stop_map_music_queue():
    global _MAP_MUSIC_TRACKS, _MAP_MUSIC_INDEX, _MAP_MUSIC_STARTED
    global _GAME_SESSION_ACTIVE, _PAUSE_MENU_OPEN, _PAUSE_OPTIONS_OPEN
    if _MAP_MUSIC_STARTED:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.set_endevent()
                pygame.mixer.music.stop()
        except pygame.error:
            pass
    _MAP_MUSIC_TRACKS = []
    _MAP_MUSIC_INDEX = -1
    _MAP_MUSIC_STARTED = False
    _GAME_SESSION_ACTIVE = False
    _PAUSE_MENU_OPEN = False
    _PAUSE_OPTIONS_OPEN = False
    return True
