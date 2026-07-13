import math
import random
from pathlib import Path

import pygame

from rg_data import (
    ACTIONS_PER_TURN,
    DEFAULT_ZOOM,
    HOVER,
    HEX_SIZE,
    LEFT_PANEL_W,
    MAP_MARGIN,
    MAX_ZOOM,
    MIN_ZOOM,
    MOVE,
    RIGHT_PANEL_W,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SELECTED,
    TEXT,
    TEXTURE_SIZE,
    TERRAINS,
    TOP_BAR_H,
)

ROOT_DIR = Path(__file__).resolve().parent
GRAPHICS_DIR = ROOT_DIR / "Grafiki"


def hex_corners(cx, cy, size):
    return [(cx + size * math.cos(math.radians(60 * i - 30)), cy + size * math.sin(math.radians(60 * i - 30))) for i in range(6)]


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) + 0.00001) + xi):
            inside = not inside
        j = i
    return inside


def axial_to_pixel(q, r):
    return HEX_SIZE * math.sqrt(3) * (q + r / 2), HEX_SIZE * 1.5 * r


def are_adjacent(a, b):
    return math.hypot(a.x - b.x, a.y - b.y) <= HEX_SIZE * 1.85


class Camera:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.zoom = DEFAULT_ZOOM

    def apply(self, x, y):
        return x * self.zoom + self.x, y * self.zoom + self.y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def zoom_at(self, mouse_pos, factor):
        old_zoom = self.zoom
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom * factor))
        if new_zoom == old_zoom:
            return
        mx, my = mouse_pos
        wx = (mx - self.x) / old_zoom
        wy = (my - self.y) / old_zoom
        self.zoom = new_zoom
        self.x = mx - wx * self.zoom
        self.y = my - wy * self.zoom

    def map_view