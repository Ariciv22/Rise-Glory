import re
from pathlib import Path

import pygame

from rg_data import MUTED, TEXT

ROOT_DIR = Path(__file__).resolve().parent
INTRO_DIRS = [
    ROOT_DIR / "intro_final",
    ROOT_DIR / "Intro_final",
    ROOT_DIR / "Grafiki" / "intro_final",
    ROOT_DIR / "Grafiki" / "Intro_final",
]
MUSIC_DIRS = [ROOT_DIR / "music", ROOT_DIR / "Music"]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MUSIC_EXTENSIONS = {".mp3", ".ogg", ".wav", ".flac"}
INTRO_SECONDS_PER_IMAGE = 10

_IMAGE_CACHE = {}
_MUSIC_STARTED = False


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
        pygame.mixer.music.play(-1)
        _MUSIC_STARTED = True
        return True
    except pygame.error:
        return False


def stop_intro_music():
    global _MUSIC_STARTED
    if not _MUSIC_STARTED:
        return False
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        _MUSIC_STARTED = False
        return True
    except pygame.error:
        return False
