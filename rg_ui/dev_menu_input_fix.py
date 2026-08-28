from __future__ import annotations

import pygame

_INSTALLED = False
_ORIGINAL_EVENT_GET = None
_LAST_F8_PRESSED = False


def install_dev_menu_input_fix() -> None:
    """Uodparnia F8 i scroll menu DEV na chwilowe blokowanie KEYDOWN przez Pygame.

    Nie zmienia petli gry. Opakowuje tylko pygame.event.get:
    - jesli fizycznie nacisnieto F8, a KEYDOWN nie dotarl do kolejki, dodaje
      pojedynczy syntetyczny KEYDOWN (z debounce),
    - gdy menu programisty bylo rysowane w ostatnich klatkach, kółko myszy
      przewija liste Questow.
    """
    global _INSTALLED, _ORIGINAL_EVENT_GET
    if _INSTALLED:
        return

    from rg_ui.dev_menu import dev_menu_recently_visible, scroll_dev_quests

    _ORIGINAL_EVENT_GET = pygame.event.get

    def event_get_with_dev_support(*args, **kwargs):
        global _LAST_F8_PRESSED
        events = list(_ORIGINAL_EVENT_GET(*args, **kwargs))

        if dev_menu_recently_visible():
            for event in events:
                if event.type == pygame.MOUSEWHEEL and int(getattr(event, "y", 0) or 0):
                    scroll_dev_quests(int(event.y))

        try:
            keys = pygame.key.get_pressed()
            f8_pressed = bool(keys[pygame.K_F8])
        except (pygame.error, IndexError):
            f8_pressed = False

        real_f8_keydown = any(
            event.type == pygame.KEYDOWN and int(getattr(event, "key", -1)) == pygame.K_F8
            for event in events
        )
        if f8_pressed and not _LAST_F8_PRESSED and not real_f8_keydown:
            events.append(
                pygame.event.Event(
                    pygame.KEYDOWN,
                    key=pygame.K_F8,
                    mod=pygame.key.get_mods(),
                    unicode="",
                    scancode=0,
                )
            )

        _LAST_F8_PRESSED = f8_pressed
        return events

    pygame.event.get = event_get_with_dev_support
    _INSTALLED = True
