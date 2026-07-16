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
        if not