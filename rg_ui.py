from pathlib import Path

import pygame

from rg_data import GOLD, LEFT_PANEL_W, MUTED, PANEL, RIGHT_PANEL_W, SCREEN_WIDTH, SIDE_MARGIN, TEXT, TOP_BAR_H


ROOT_DIR = Path(__file__).resolve().parent
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


def _load_panel_image(panel_number):
    panel_number = int(panel_number)
    if panel_number in _IMAGE_PANEL_CACHE:
        return _IMAGE_PANEL_CACHE[panel_number]

    image = None
    for path in _panel_image_paths(panel_number):
        if not path.exists():
            continue
        try:
            image = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            image = None
        break

    _IMAGE_PANEL_CACHE[panel_number] = image
    return image


def draw_image_panel(screen, rect, panel_number, fallback_border=GOLD):
    """Rysuje wskazany panel z katalogu Grafiki/Grafiki UI w podanym prostokacie."""
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


def ui_rects(screen):
    sw, sh = screen.get_size()
    bottom_info_w = sw - LEFT_PANEL_W - RIGHT_PANEL_W - SIDE_MARGIN * 4
    return [
        pygame.Rect(0, 0, sw, TOP_BAR_H),
        pygame.Rect(SIDE_MARGIN, TOP_BAR_H + SIDE_MARGIN, LEFT_PANEL_W, sh - TOP_BAR_H - SIDE_MARGIN * 2),
        pygame.Rect(sw - RIGHT_PANEL_W - SIDE_MARGIN, TOP_BAR_H + SIDE_MARGIN, RIGHT_PANEL_W, sh - TOP_BAR_H - SIDE_MARGIN * 2),
        pygame.Rect(LEFT_PANEL_W + SIDE_MARGIN * 2, sh - 66, max(0, bottom_info_w), 54),
    ]


def over_ui(pos, rects):
    return any(rect.collidepoint(pos) for rect in rects)


def centered_x(width):
    return SCREEN_WIDTH / 2 - width / 2
