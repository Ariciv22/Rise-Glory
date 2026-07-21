from pathlib import Path

import pygame

from rg_data import GOLD, LEFT_PANEL_W, MUTED, PANEL, RIGHT_PANEL_W, SCREEN_WIDTH, SIDE_MARGIN, TEXT, TOP_BAR_H


ROOT_DIR = Path(__file__).resolve().parent
UI_TEXTURE_PATHS = {
    "panel": [
        ROOT_DIR / "Grafiki" / "Grafiki UI" / "panel1.png",
        ROOT_DIR / "Grafiki" / "Grafiki UI" / "panel 1.png",
        ROOT_DIR / "Grafiki" / "Grafiki UI" / "panel_1.png",
    ],
    "control": [
        ROOT_DIR / "Grafiki" / "Grafiki UI" / "panel2.png",
        ROOT_DIR / "Grafiki" / "Grafiki UI" / "panel 2.png",
        ROOT_DIR / "Grafiki" / "Grafiki UI" / "panel_2.png",
    ],
}
_UI_SOURCE_CACHE = {}
_UI_SCALED_CACHE = {}


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


def _find_ui_texture(style):
    for path in UI_TEXTURE_PATHS.get(style, UI_TEXTURE_PATHS["panel"]):
        if path.exists():
            return path
    return None


def _load_ui_source(style):
    path = _find_ui_texture(style)
    cache_key = (style, str(path) if path else None)
    if cache_key in _UI_SOURCE_CACHE:
        return _UI_SOURCE_CACHE[cache_key]
    if path is None:
        _UI_SOURCE_CACHE[cache_key] = None
        return None
    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        image = None
    _UI_SOURCE_CACHE[cache_key] = image
    return image


def _load_ui_texture(style, size):
    source = _load_ui_source(style)
    if source is None:
        return None
    size = (max(1, int(size[0])), max(1, int(size[1])))
    cache_key = (style, size)
    if cache_key not in _UI_SCALED_CACHE:
        _UI_SCALED_CACHE[cache_key] = pygame.transform.smoothscale(source, size)
    return _UI_SCALED_CACHE[cache_key]


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


def draw_textured_panel(screen, rect, style="panel", fallback_border=GOLD, fill_color=PANEL, fill_alpha=245):
    rect = pygame.Rect(rect)
    if rect.width <= 0 or rect.height <= 0:
        return rect

    if fill_alpha >= 255:
        pygame.draw.rect(screen, fill_color, rect, border_radius=12)
    else:
        fill = pygame.Surface(rect.size, pygame.SRCALPHA)
        fill.fill((*fill_color, max(0, min(255, int(fill_alpha)))))
        screen.blit(fill, rect.topleft)

    texture = _load_ui_texture(style, rect.size)
    if texture is not None:
        screen.blit(texture, rect.topleft)
    else:
        draw_panel(screen, rect, fallback_border)
    return rect


def draw_textured_frame(screen, rect, style="panel", fallback_border=GOLD, slice_size=28):
    """Rysuje wyłącznie ozdobne krawędzie panelu, bez zasłaniania środka mapy."""
    rect = pygame.Rect(rect)
    source = _load_ui_source(style)
    if source is None or rect.width <= 0 or rect.height <= 0:
        pygame.draw.rect(screen, fallback_border, rect, 2, border_radius=12)
        return rect

    source_w, source_h = source.get_size()
    source_slice = max(2, min(int(slice_size), source_w // 3, source_h // 3))
    target_slice = max(2, min(int(slice_size), rect.width // 3, rect.height // 3))

    src = {
        "tl": pygame.Rect(0, 0, source_slice, source_slice),
        "tr": pygame.Rect(source_w - source_slice, 0, source_slice, source_slice),
        "bl": pygame.Rect(0, source_h - source_slice, source_slice, source_slice),
        "br": pygame.Rect(source_w - source_slice, source_h - source_slice, source_slice, source_slice),
        "top": pygame.Rect(source_slice, 0, source_w - source_slice * 2, source_slice),
        "bottom": pygame.Rect(source_slice, source_h - source_slice, source_w - source_slice * 2, source_slice),
        "left": pygame.Rect(0, source_slice, source_slice, source_h - source_slice * 2),
        "right": pygame.Rect(source_w - source_slice, source_slice, source_slice, source_h - source_slice * 2),
    }
    dst = {
        "tl": pygame.Rect(rect.left, rect.top, target_slice, target_slice),
        "tr": pygame.Rect(rect.right - target_slice, rect.top, target_slice, target_slice),
        "bl": pygame.Rect(rect.left, rect.bottom - target_slice, target_slice, target_slice),
        "br": pygame.Rect(rect.right - target_slice, rect.bottom - target_slice, target_slice, target_slice),
        "top": pygame.Rect(rect.left + target_slice, rect.top, rect.width - target_slice * 2, target_slice),
        "bottom": pygame.Rect(rect.left + target_slice, rect.bottom - target_slice, rect.width - target_slice * 2, target_slice),
        "left": pygame.Rect(rect.left, rect.top + target_slice, target_slice, rect.height - target_slice * 2),
        "right": pygame.Rect(rect.right - target_slice, rect.top + target_slice, target_slice, rect.height - target_slice * 2),
    }

    for key in ("tl", "tr", "bl", "br", "top", "bottom", "left", "right"):
        if dst[key].width <= 0 or dst[key].height <= 0 or src[key].width <= 0 or src[key].height <= 0:
            continue
        piece = source.subsurface(src[key])
        if piece.get_size() != dst[key].size:
            piece = pygame.transform.smoothscale(piece, dst[key].size)
        screen.blit(piece, dst[key].topleft)
    return rect


def draw_textured_button(screen, font, mouse_pos, button, active=False):
    hovered = button.rect.collidepoint(mouse_pos)
    fill_color = (52, 49, 42) if active else ((48, 45, 38) if hovered else (28, 25, 21))
    draw_textured_panel(screen, button.rect, style="control", fill_color=fill_color, fill_alpha=255)

    if hovered or active:
        glow = pygame.Surface(button.rect.size, pygame.SRCALPHA)
        glow.fill((255, 218, 130, 28 if hovered else 20))
        screen.blit(glow, button.rect.topleft)

    if button.text:
        shadow = font.render(button.text, True, (18, 12, 8))
        label = font.render(button.text, True, (255, 232, 180) if hovered else TEXT)
        screen.blit(shadow, shadow.get_rect(center=(button.rect.centerx + 2, button.rect.centery + 2)))
        screen.blit(label, label.get_rect(center=button.rect.center))
    return button


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
