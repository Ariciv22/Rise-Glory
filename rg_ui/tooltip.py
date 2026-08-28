from pathlib import Path

import pygame

from rg_core.data import GOLD, MUTED, PANEL, PANEL_DARK, TEXT
from rg_engine.production import potential_summary, site_owner_label
from rg_ui.common import draw_lines

ROOT_DIR = Path(__file__).resolve().parents[1]
HEX_TOOLTIP_ASSET = ROOT_DIR / "Grafiki" / "info_heks_najechanie.png"

# Nowa grafika tooltipa ma proporcje 4:3. Zachowujemy je, zeby ozdobna rama
# Rise & Glory nie byla rozciagana ani zgniatana.
TOOLTIP_W = 360
TOOLTIP_H = 270
TOOLTIP_PADDING_X = 31
TOOLTIP_CONTENT_TOP = 82

_TOOLTIP_SOURCE = None
_TOOLTIP_SOURCE_LOADED = False
_TOOLTIP_SCALED_CACHE = {}


def _tooltip_source():
    global _TOOLTIP_SOURCE, _TOOLTIP_SOURCE_LOADED
    if _TOOLTIP_SOURCE_LOADED:
        return _TOOLTIP_SOURCE

    _TOOLTIP_SOURCE_LOADED = True
    if not HEX_TOOLTIP_ASSET.exists():
        return None

    try:
        _TOOLTIP_SOURCE = pygame.image.load(str(HEX_TOOLTIP_ASSET)).convert_alpha()
    except (OSError, pygame.error):
        _TOOLTIP_SOURCE = None
    return _TOOLTIP_SOURCE


def _tooltip_background(size):
    size = (max(1, int(size[0])), max(1, int(size[1])))
    cached = _TOOLTIP_SCALED_CACHE.get(size)
    if cached is not None:
        return cached

    source = _tooltip_source()
    if source is None:
        return None

    if source.get_size() == size:
        scaled = source
    else:
        scaled = pygame.transform.smoothscale(source, size)
    _TOOLTIP_SCALED_CACHE[size] = scaled
    return scaled


def get_tile_lines(tile):
    location = tile.location
    terrain = tile.terrain
    site = getattr(tile, "production_site", None)
    title = location["name"] if location else f"Heks {tile.id}"
    lines = [
        title,
        f"Teren: {terrain['name']}",
        f"Koszt ruchu: {terrain['move']}",
        f"POTENCJAŁ: {potential_summary(tile)}",
        f"Jurysdykcja: {getattr(tile, 'jurisdiction_name', None) or 'brak'}",
    ]
    if site:
        status = "aktywny" if site.get("status") == "active" else "w budowie"
        lines.append(f"Zakład: {site.get('name', 'Zakład')} ({status})")
        lines.append(f"Właściciel: {site_owner_label(site)}")
    else:
        right_owner = getattr(tile, "extraction_right_owner_name", None)
        lines.append("Zakład: brak")
        lines.append(f"Prawo eksploatacji: {right_owner or 'wolne'}")
    return lines


def clamp_tooltip_position(mouse_pos, tooltip_w, tooltip_h, screen_w, screen_h):
    x = mouse_pos[0] + 22
    y = mouse_pos[1] + 18
    if x + tooltip_w > screen_w - 10:
        x = mouse_pos[0] - tooltip_w - 22
    if y + tooltip_h > screen_h - 10:
        y = mouse_pos[1] - tooltip_h - 18
    return max(10, x), max(10, y)


def _draw_fallback_panel(screen, rect):
    """Stary panel zostaje tylko jako awaryjny fallback bez assetu PNG."""
    pygame.draw.rect(screen, PANEL, rect, border_radius=12)
    pygame.draw.rect(screen, GOLD, rect, 2, border_radius=12)
    title_rect = pygame.Rect(rect.x + 10, rect.y + 10, rect.width - 20, 38)
    pygame.draw.rect(screen, PANEL_DARK, title_rect, border_radius=8)
    return title_rect


def draw_location_tooltip(screen, font, small_font, hovered_tile, mouse_pos):
    if not hovered_tile:
        return

    lines = get_tile_lines(hovered_tile)
    screen_w, screen_h = screen.get_size()
    x, y = clamp_tooltip_position(
        mouse_pos,
        TOOLTIP_W,
        TOOLTIP_H,
        screen_w,
        screen_h,
    )
    rect = pygame.Rect(x, y, TOOLTIP_W, TOOLTIP_H)

    background = _tooltip_background(rect.size)
    if background is not None:
        screen.blit(background, rect.topleft)

        # W wygenerowanym panelu naglowek jest osobna, ozdobna belka. Zloty
        # medalion jest juz czescia PNG, dlatego nie rysujemy na nim starego
        # kola. Tekst zaczyna sie za medalionem.
        title_x = rect.x + int(rect.width * 0.185)
        title_y = rect.y + int(rect.height * 0.112)
        title_max_w = rect.right - int(rect.width * 0.08) - title_x

        title_surface = font.render(lines[0], True, TEXT)
        if title_surface.get_width() > title_max_w:
            title_surface = small_font.render(lines[0], True, TEXT)
        screen.blit(title_surface, (title_x, title_y))

        content_x = rect.x + TOOLTIP_PADDING_X
        content_y = rect.y + TOOLTIP_CONTENT_TOP
        content_w = rect.width - TOOLTIP_PADDING_X * 2
    else:
        title_rect = _draw_fallback_panel(screen, rect)
        if hovered_tile.location:
            color = hovered_tile.location["color"]
        else:
            color = GOLD
        pygame.draw.circle(screen, color, (title_rect.x + 15, title_rect.centery), 8)
        screen.blit(
            font.render(lines[0], True, TEXT),
            (title_rect.x + 32, title_rect.y + 7),
        )
        content_x = rect.x + 18
        content_y = rect.y + 58
        content_w = rect.width - 36

    draw_lines(
        screen,
        small_font,
        lines[1:],
        content_x,
        content_y,
        MUTED,
        line_h=23,
        max_width=content_w,
    )
