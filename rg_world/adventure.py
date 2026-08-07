import math
import random
from pathlib import Path

import pygame

from rg_core.data import GOLD, MAX_WOUNDS, MUTED, PANEL_DARK, TEXT


ROOT_DIR = Path(__file__).resolve().parents[1]
ADVENTURE_TOKEN_COUNT = 8
ADVENTURE_GOLD_REWARD = 3

_ACTIVE_EVENT = None
_TOKEN_IMAGE = None
_INSTALL_DONE = False


class AdventureEvent:
    def __init__(self, hero, tile):
        self.hero = hero
        self.tile_id = getattr(tile, "id", None)
        self.title = "Wedrowiec i wagabunda na szlaku"
        self.description = (
            "Na trakcie spotykasz wedrowca i podejrzanego wagabunde. "
            "Nie wiesz, czy czeka cie zasadzka, czy niespodziewana nagroda."
        )
        self.roll = None
        self.result_text = ""

    @property
    def resolved(self):
        return self.roll is not None

    def resolve(self, roll=None):
        if self.resolved:
            return self.roll

        self.roll = int(roll if roll is not None else random.randint(1, 20))
        if not 1 <= self.roll <= 20:
            raise ValueError("Rzut k20 musi miescic sie w zakresie 1-20")

        if self.roll <= 12:
            previous = int(self.hero.get("wounds", 0))
            self.hero["wounds"] = min(MAX_WOUNDS, previous + 1)
            if previous >= MAX_WOUNDS:
                self.result_text = "Wagabunda atakuje, ale bohater ma juz maksymalna liczbe Ran."
            else:
                self.result_text = "Wagabunda atakuje. Bohater otrzymuje 1 Rane."
        else:
            self.hero["gold"] = int(self.hero.get("gold", 0)) + ADVENTURE_GOLD_REWARD
            self.result_text = f"Wedrowiec odplaca sie za pomoc. Otrzymujesz {ADVENTURE_GOLD_REWARD} monety."
        return self.roll


def is_adventure_event_open():
    return _ACTIVE_EVENT is not None


def get_active_adventure():
    return _ACTIVE_EVENT


def start_adventure(hero, tile):
    global _ACTIVE_EVENT
    if _ACTIVE_EVENT is not None or not getattr(tile, "adventure", None):
        return _ACTIVE_EVENT
    tile.adventure = None
    _ACTIVE_EVENT = AdventureEvent(hero, tile)
    return _ACTIVE_EVENT


def resolve_active_adventure(roll=None):
    if _ACTIVE_EVENT is None:
        return None
    return _ACTIVE_EVENT.resolve(roll)


def close_active_adventure():
    global _ACTIVE_EVENT
    if _ACTIVE_EVENT is None or not _ACTIVE_EVENT.resolved:
        return False
    _ACTIVE_EVENT = None
    return True


def reset_adventure_event():
    global _ACTIVE_EVENT
    _ACTIVE_EVENT = None


def _load_token_image():
    global _TOKEN_IMAGE
    if _TOKEN_IMAGE is not None:
        return _TOKEN_IMAGE

    candidates = [
        ROOT_DIR / "Grafiki" / "zeton_przygod.png",
        ROOT_DIR / "Grafiki" / "zeton_przygod.jpg",
        ROOT_DIR / "Grafiki" / "zeton_przygod.jpeg",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            _TOKEN_IMAGE = pygame.image.load(str(path)).convert_alpha()
            return _TOKEN_IMAGE
        except pygame.error:
            continue
    _TOKEN_IMAGE = False
    return None


def _draw_adventure_token(tile, screen, camera):
    if not getattr(tile, "adventure", None):
        return

    sx, sy = tile.center(camera)
    diameter = max(24, int(46 * camera.zoom))
    center = (
        int(sx + 39 * camera.zoom),
        int(sy - 34 * camera.zoom),
    )
    pygame.draw.circle(screen, (18, 14, 9), center, diameter // 2 + 3)

    image = _load_token_image()
    if image:
        scaled = pygame.transform.smoothscale(image, (diameter, diameter))
        screen.blit(scaled, scaled.get_rect(center=center))
    else:
        pygame.draw.circle(screen, GOLD, center, diameter // 2)
        fallback_font = pygame.font.SysFont("arial", max(14, diameter // 2), bold=True)
        label = fallback_font.render("?", True, (30, 22, 12))
        screen.blit(label, label.get_rect(center=center))


def _event_layout(screen):
    sw, sh = screen.get_size()
    card_w = min(660, sw - 80)
    card_h = min(540, sh - 80)
    card = pygame.Rect((sw - card_w) // 2, (sh - card_h) // 2, card_w, card_h)
    button = pygame.Rect(card.centerx - 110, card.bottom - 72, 220, 44)
    return card, button


def _wrap(font, text, width):
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


def _d20_points(center, radius):
    cx, cy = center
    return [
        (
            cx + math.cos(math.radians(-90 + index * 36)) * radius,
            cy + math.sin(math.radians(-90 + index * 36)) * radius,
        )
        for index in range(10)
    ]


def _draw_d20(screen, center, radius, value, font):
    points = _d20_points(center, radius)
    pygame.draw.polygon(screen, (166, 116, 48), points)
    pygame.draw.polygon(screen, (238, 205, 128), points, 3)

    cx, cy = center
    top = points[0]
    bottom = points[5]
    left = points[7]
    right = points[3]
    pygame.draw.line(screen, (92, 59, 26), top, bottom, 2)
    pygame.draw.line(screen, (92, 59, 26), left, right, 2)
    for point in (points[1], points[2], points[8], points[9]):
        pygame.draw.line(screen, (92, 59, 26), (cx, cy), point, 1)

    label = font.render(str(value) if value is not None else "k20", True, (32, 23, 13))
    screen.blit(label, label.get_rect(center=(int(cx), int(cy))))


def draw_adventure_overlay(screen, font, small_font):
    event = get_active_adventure()
    if event is None:
        return

    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 188))
    screen.blit(shade, (0, 0))

    card, button = _event_layout(screen)
    pygame.draw.rect(screen, PANEL_DARK, card, border_radius=18)
    pygame.draw.rect(screen, GOLD, card, 4, border_radius=18)

    title = font.render(event.title, True, TEXT)
    screen.blit(title, title.get_rect(center=(card.centerx, card.y + 42)))

    y = card.y + 82
    for line in _wrap(small_font, event.description, card.width - 90):
        label = small_font.render(line, True, MUTED)
        screen.blit(label, label.get_rect(center=(card.centerx, y)))
        y += 23

    outcome_1 = small_font.render("1-12: otrzymujesz 1 Rane", True, TEXT)
    outcome_2 = small_font.render(f"13-20: otrzymujesz {ADVENTURE_GOLD_REWARD} monety", True, TEXT)
    screen.blit(outcome_1, outcome_1.get_rect(center=(card.centerx, y + 20)))
    screen.blit(outcome_2, outcome_2.get_rect(center=(card.centerx, y + 48)))

    die_center = (card.centerx, card.y + 320)
    _draw_d20(screen, die_center, 72, event.roll, font)

    if event.resolved:
        result = f"Wynik rzutu: {event.roll}. {event.result_text}"
        result_y = card.y + 414
        for line in _wrap(small_font, result, card.width - 90):
            label = small_font.render(line, True, TEXT)
            screen.blit(label, label.get_rect(center=(card.centerx, result_y)))
            result_y += 22

    hovered = button.collidepoint(pygame.mouse.get_pos())
    button_color = (93, 72, 42) if hovered else (67, 50, 31)
    pygame.draw.rect(screen, button_color, button, border_radius=10)
    pygame.draw.rect(screen, GOLD, button, 2, border_radius=10)
    button_text = "Zamknij" if event.resolved else "Rzuc k20"
    label = font.render(button_text, True, TEXT)
    screen.blit(label, label.get_rect(center=button.center))


class _AdventureControllerButton:
    def __init__(self, end_turn_button):
        self.end_turn_button = end_turn_button
        self.action = "end_turn"

    def clicked(self, pos):
        event = get_active_adventure()
        if event is None:
            self.action = self.end_turn_button.action
            return self.end_turn_button.clicked(pos)

        screen = pygame.display.get_surface()
        if screen is None:
            self.action = "adventure_event"
            return True

        _, button = _event_layout(screen)
        if button.collidepoint(pos):
            if event.resolved:
                close_active_adventure()
            else:
                resolve_active_adventure()
        self.action = "adventure_event"
        return True


def _assign_adventure_tokens(tiles):
    for tile in tiles:
        tile.adventure = None

    candidates = [
        tile for tile in tiles
        if tile.terrain.get("passable", False) and not tile.location
    ]
    for tile in random.sample(candidates, min(ADVENTURE_TOKEN_COUNT, len(candidates))):
        tile.adventure = {"card": "traveler_and_vagabond"}
    return tiles


def install_adventure_system():
    global _INSTALL_DONE
    if _INSTALL_DONE:
        return

    import rg_world as rg_world_package
    from rg_engine import turns as rg_turns
    from rg_ui import hud as rg_hud
    from rg_ui import player_board as rg_player_board
    from rg_world import map as rg_map

    original_tile_init = rg_map.Tile.__init__
    original_tile_draw = rg_map.Tile.draw
    original_move_to = rg_map.HeroToken.move_to
    original_generate_world = rg_world_package.generate_world
    original_scoreboard = rg_hud._draw_scoreboard
    original_bottom_info = rg_hud._draw_bottom_tile_info
    original_player_board_clicked = rg_hud._PlayerBoardButton.clicked
    original_board_open = rg_player_board.is_player_board_open
    original_end_turn = rg_turns.TurnManager.end_turn

    def tile_init_with_adventure(self, *args, **kwargs):
        original_tile_init(self, *args, **kwargs)
        self.adventure = None

    def tile_draw_with_adventure(self, screen, textures, camera, font, *args, **kwargs):
        result = original_tile_draw(self, screen, textures, camera, font, *args, **kwargs)
        _draw_adventure_token(self, screen, camera)
        return result

    def move_to_with_adventure(self, target):
        moved = original_move_to(self, target)
        if moved and getattr(target, "adventure", None):
            start_adventure(self.hero, target)
        return moved

    def generate_world_with_adventures(map_key="rosette9"):
        return _assign_adventure_tokens(original_generate_world(map_key))

    def scoreboard_with_adventure_controller(*args, **kwargs):
        end_turn = original_scoreboard(*args, **kwargs)
        return _AdventureControllerButton(end_turn)

    def bottom_info_with_adventure_overlay(*args, **kwargs):
        result = original_bottom_info(*args, **kwargs)
        if is_adventure_event_open():
            screen, font, small_font = args[:3]
            draw_adventure_overlay(screen, font, small_font)
        return result

    def player_board_clicked_without_event(self, pos):
        if is_adventure_event_open():
            return False
        return original_player_board_clicked(self, pos)

    def board_or_adventure_open():
        return original_board_open() or is_adventure_event_open()

    def end_turn_without_unresolved_event(self, tokens):
        if is_adventure_event_open():
            return {
                "active_player_index": self.active_player_index,
                "round_completed": False,
                "council_due": False,
            }
        return original_end_turn(self, tokens)

    rg_map.Tile.__init__ = tile_init_with_adventure
    rg_map.Tile.draw = tile_draw_with_adventure
    rg_map.HeroToken.move_to = move_to_with_adventure
    rg_world_package.generate_world = generate_world_with_adventures
    rg_hud._draw_scoreboard = scoreboard_with_adventure_controller
    rg_hud._draw_bottom_tile_info = bottom_info_with_adventure_overlay
    rg_hud._PlayerBoardButton.clicked = player_board_clicked_without_event
    rg_player_board.is_player_board_open = board_or_adventure_open
    rg_turns.TurnManager.end_turn = end_turn_without_unresolved_event
    _INSTALL_DONE = True
