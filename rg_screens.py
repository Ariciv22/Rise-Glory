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
MENU_BACKGROUND_PATH = ROOT_DIR