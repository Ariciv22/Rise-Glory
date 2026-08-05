from pathlib import Path

import pygame

from rg_data import GOLD, MUTED, PANEL_DARK, TEXT
from rg_dice_animation import DiceRollAnimation, PremiumD20Renderer


_INSTALLED = False
_RENDERER = PremiumD20Renderer(Path(__file__).resolve().parent / "Grafiki" / "kostka_k20")


def _animation(event):
    animation = getattr(event, "dice_animation", None)
    if animation is None:
        animation = DiceRollAnimation()
        event.dice_animation = animation
    return animation


def _premium_event_layout(screen):
    sw, sh = screen.get_size()
    card_w = min(720, sw - 70)
    card_h = min(610, sh - 60)
    card = pygame.Rect((sw - card_w) // 2, (sh - card_h) // 2, card_w, card_h)
    button = pygame.Rect(card.centerx - 125, card.bottom - 66, 250, 44)
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


def _draw_premium_overlay(screen, font, small_font):
    import rg_adventure as adventure

    event = adventure.get_active_adventure()
    if event is None:
        return

    now_ms = pygame.time.get_ticks()
    event.update_animated_roll(now_ms)

    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 194))
    screen.blit(shade, (0, 0))

    card, button = _premium_event_layout(screen)
    pygame.draw.rect(screen, (10, 8, 7), card, border_radius=18)
    pygame.draw.rect(screen, PANEL_DARK, card.inflate(-10, -10), border_radius=15)
    pygame.draw.rect(screen, GOLD, card, 4, border_radius=18)
    pygame.draw.line(
        screen,
        (223, 164, 74),
        (card.x + 34, card.y + 65),
        (card.right - 34, card.y + 65),
        1,
    )

    title = font.render(event.title, True, TEXT)
    screen.blit(title, title.get_rect(center=(card.centerx, card.y + 38)))

    description_y = card.y + 82
    for line in _wrap(small_font, event.description, card.width - 90):
        label = small_font.render(line, True, MUTED)
        screen.blit(label, label.get_rect(center=(card.centerx, description_y)))
        description_y += 23

    rule_y = description_y + 10
    outcome_1 = small_font.render("1-12: otrzymujesz 1 Rane", True, TEXT)
    outcome_2 = small_font.render("13-20: otrzymujesz 3 monety", True, TEXT)
    screen.blit(outcome_1, outcome_1.get_rect(center=(card.centerx - 145, rule_y)))
    screen.blit(outcome_2, outcome_2.get_rect(center=(card.centerx + 145, rule_y)))

    die_center = (card.centerx, card.y + int(card.height * 0.59))
    die_radius = max(76, min(108, int(card.height * 0.18)))
    _RENDERER.draw(
        screen,
        die_center,
        die_radius,
        _animation(event),
        final_value=event.roll,
        now_ms=now_ms,
    )

    result_y = card.bottom - 115
    if event.rolling:
        status = small_font.render("Kostka toczy sie...", True, (255, 205, 116))
        screen.blit(status, status.get_rect(center=(card.centerx, result_y)))
    elif event.resolved:
        result = f"Wynik rzutu: {event.roll}. {event.result_text}"
        for line in _wrap(small_font, result, card.width - 90):
            label = small_font.render(line, True, TEXT)
            screen.blit(label, label.get_rect(center=(card.centerx, result_y)))
            result_y += 21
    else:
        hint = small_font.render("Kliknij przycisk, aby wykonac rzut.", True, MUTED)
        screen.blit(hint, hint.get_rect(center=(card.centerx, result_y)))

    hovered = button.collidepoint(pygame.mouse.get_pos())
    if event.rolling:
        button_color = (44, 39, 34)
        border_color = (91, 74, 49)
        button_text = "Turlanie..."
        text_color = MUTED
    else:
        button_color = (96, 70, 39) if hovered else (67, 50, 31)
        border_color = GOLD
        button_text = "Zamknij" if event.resolved else "Rzuc k20"
        text_color = TEXT

    pygame.draw.rect(screen, button_color, button, border_radius=10)
    pygame.draw.rect(screen, border_color, button, 2, border_radius=10)
    label = font.render(button_text, True, text_color)
    screen.blit(label, label.get_rect(center=button.center))


def install_premium_dice_animation():
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_adventure as adventure

    original_init = adventure.AdventureEvent.__init__
    original_resolve = adventure.AdventureEvent.resolve
    original_clicked = adventure._AdventureControllerButton.clicked

    def event_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.dice_animation = DiceRollAnimation()

    def event_resolve(self, roll=None):
        result = original_resolve(self, roll)
        _animation(self).stop()
        return result

    def start_animated_roll(self, roll=None, now_ms=None, rng=None):
        if self.resolved:
            return False
        return _animation(self).start(result=roll, now_ms=now_ms, rng=rng)

    def update_animated_roll(self, now_ms=None):
        completed = _animation(self).update(now_ms)
        if completed is None or self.resolved:
            return None
        self.resolve(completed)
        return completed

    def is_rolling(self):
        return _animation(self).rolling

    def controller_clicked(self, pos):
        event = adventure.get_active_adventure()
        if event is None:
            return original_clicked(self, pos)

        screen = pygame.display.get_surface()
        self.action = "adventure_event"
        if screen is None:
            return True

        _, button = _premium_event_layout(screen)
        if not button.collidepoint(pos):
            return True

        if event.rolling:
            return True
        if event.resolved:
            adventure.close_active_adventure()
        else:
            event.start_animated_roll()
        return True

    adventure.AdventureEvent.__init__ = event_init
    adventure.AdventureEvent.resolve = event_resolve
    adventure.AdventureEvent.start_animated_roll = start_animated_roll
    adventure.AdventureEvent.update_animated_roll = update_animated_roll
    adventure.AdventureEvent.rolling = property(is_rolling)
    adventure._AdventureControllerButton.clicked = controller_clicked
    adventure.draw_adventure_overlay = _draw_premium_overlay

    _INSTALLED = True
