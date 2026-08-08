from pathlib import Path

import pygame

from rg_core import data as rg_data
from rg_core.data import GOLD, LEFT_PANEL_W, MUTED, PANEL, RIGHT_PANEL_W, SIDE_MARGIN, TEXT, TOP_BAR_H


ROOT_DIR = Path(__file__).resolve().parents[1]
_IMAGE_PANEL_CACHE = {}
_IMAGE_PANEL_SCALED_CACHE = {}


class Button:
    def __init__(self, text, action, rect):
        self.text = text
        self.action = action
        self.rect = pygame.Rect(rect)

    def draw(self, screen, font, mouse_pos, active=False):
        hovered = self.rect.collidepoint(mouse_pos)
        bg = (74, 92, 72) if active else ((62, 74, 84) if hovered else (42, 50, 58))
        pygame.draw.rect(screen, bg, self.rect, border_radius=12)
        pygame.draw.rect(screen, (120, 140, 150), self.rect, 2, border_radius=12)
        if self.text:
            label = font.render(self.text, True, TEXT)
            screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


def _panel_image_paths(panel_number):
    number = str(panel_number)
    base = ROOT_DIR / "Grafiki" / "Grafiki UI"
    return [
        base / f"panel{number}.png",
        base / f"panel {number}.png",
        base / f"panel_{number}.png",
    ]


def _remove_light_canvas(image):
    """Usuwa zapisana w PNG jasna szachownice i przycina puste marginesy."""
    cleaned = image.copy().convert_alpha()

    try:
        rgb = pygame.surfarray.pixels3d(cleaned)
        alpha = pygame.surfarray.pixels_alpha(cleaned)
        channel_min = rgb.min(axis=2)
        channel_max = rgb.max(axis=2)
        light_neutral = (channel_min >= 150) & ((channel_max - channel_min) <= 24)
        alpha[light_neutral] = 0
        del alpha
        del rgb
    except (ImportError, NotImplementedError, ValueError, pygame.error):
        pixels = pygame.PixelArray(cleaned)
        width, height = cleaned.get_size()
        for x in range(width):
            for y in range(height):
                color = cleaned.unmap_rgb(pixels[x, y])
                low = min(color.r, color.g, color.b)
                high = max(color.r, color.g, color.b)
                if color.a > 0 and low >= 150 and high - low <= 24:
                    pixels[x, y] = (0, 0, 0, 0)
        del pixels

    mask = pygame.mask.from_surface(cleaned, 8)
    components = mask.get_bounding_rects()
    if not components:
        return image

    max_area = max(rect.width * rect.height for rect in components)
    meaningful = [
        rect for rect in components
        if rect.width * rect.height >= max(16, int(max_area * 0.01))
    ]
    if not meaningful:
        meaningful = components

    bounds = meaningful[0].copy()
    for rect in meaningful[1:]:
        bounds.union_ip(rect)

    bounds.inflate_ip(4, 4)
    bounds.clamp_ip(cleaned.get_rect())
    return cleaned.subsurface(bounds).copy()


def _load_panel_image(panel_number):
    panel_number = int(panel_number)
    if panel_number in _IMAGE_PANEL_CACHE:
        return _IMAGE_PANEL_CACHE[panel_number]

    image = None
    for path in _panel_image_paths(panel_number):
        if not path.exists():
            continue
        try:
            image = _remove_light_canvas(pygame.image.load(str(path)).convert_alpha())
        except pygame.error:
            image = None
        break

    _IMAGE_PANEL_CACHE[panel_number] = image
    return image


def draw_image_panel(screen, rect, panel_number, fallback_border=GOLD):
    """Rysuje przycieta grafike panelu bez szachownicy i pustych marginesow."""
    rect = pygame.Rect(rect)
    pygame.draw.rect(screen, PANEL, rect, border_radius=12)

    source = _load_panel_image(panel_number)
    if source is None:
        pygame.draw.rect(screen, fallback_border, rect, 2, border_radius=12)
        return rect

    cache_key = (int(panel_number), rect.size)
    texture = _IMAGE_PANEL_SCALED_CACHE.get(cache_key)
    if texture is None:
        texture = pygame.transform.smoothscale(source, rect.size)
        _IMAGE_PANEL_SCALED_CACHE[cache_key] = texture

    screen.blit(texture, rect.topleft)
    return rect


def wrap(font, text, width):
    words = str(text).split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(screen, font, lines, x, y, color=MUTED, line_h=22, max_width=None):
    for line in lines:
        text = str(line)
        if max_width:
            while font.size(text)[0] > max_width and len(text) > 4:
                text = text[:-4] + "..."
        screen.blit(font.render(text, True, color), (x, y))
        y += line_h
    return y


def draw_panel(screen, rect, border=GOLD):
    pygame.draw.rect(screen, PANEL, rect, border_radius=12)
    pygame.draw.rect(screen, border, rect, 2, border_radius=12)


def game_layout_rects(screen):
    """Zwraca spojny uklad HUD bez szczelin miedzy glownymi panelami."""
    sw, sh = screen.get_size()
    center_w = max(0, sw - LEFT_PANEL_W - RIGHT_PANEL_W)
    side_h = max(0, sh - TOP_BAR_H)
    bottom_h = min(54, side_h)

    top = pygame.Rect(0, 0, sw, TOP_BAR_H)
    left = pygame.Rect(0, TOP_BAR_H, LEFT_PANEL_W, side_h)
    right = pygame.Rect(sw - RIGHT_PANEL_W, TOP_BAR_H, RIGHT_PANEL_W, side_h)
    center = pygame.Rect(LEFT_PANEL_W, TOP_BAR_H, center_w, side_h)
    bottom = pygame.Rect(LEFT_PANEL_W, sh - bottom_h, center_w, bottom_h)
    return {
        "top": top,
        "left": left,
        "right": right,
        "center": center,
        "bottom": bottom,
    }


def ui_rects(screen):
    try:
        from rg_ui.player_board import is_player_board_open

        if is_player_board_open():
            return [screen.get_rect()]
    except (ImportError, AttributeError):
        pass

    layout = game_layout_rects(screen)
    return [layout["top"], layout["left"], layout["right"], layout["bottom"]]


def over_ui(pos, rects):
    return any(rect.collidepoint(pos) for rect in rects)


def centered_x(width):
    return rg_data.SCREEN_WIDTH / 2 - width / 2
