from __future__ import annotations

import pygame

from rg_core.data import BG, MUTED, TEXT
from rg_ui.common import Button
from rg_ui.lan_mode import run_lan_mode
from rg_world.map import load_textures


class _LaunchLanButton(Button):
    def __init__(self, *args, screen=None, title_font=None, font=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._screen = screen
        self._title_font = title_font
        self._font = font

    def clicked(self, pos):
        if not super().clicked(pos):
            return False
        if self.action == "launch_lan" and self._screen is not None:
            small_font = pygame.font.SysFont("arial", 17, bold=True)
            token_font = pygame.font.SysFont("arial", 17, bold=True)
            textures = load_textures()
            run_lan_mode(self._screen, self._title_font, self._font, small_font, token_font, textures)
        return True


def draw_multiplayer(screen, title_font, font, mouse):
    screen.fill(BG)
    title = title_font.render("Multiplayer", True, TEXT)
    screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 105)))
    subtitle = font.render("Pierwsza wersja: wspolna siec LAN / Wi-Fi, do 6 graczy", True, MUTED)
    screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 155)))

    launch = _LaunchLanButton(
        "Uruchom Multiplayer LAN",
        "launch_lan",
        (screen.get_width() // 2 - 230, 285, 460, 62),
        screen=screen,
        title_font=title_font,
        font=font,
    )
    back = Button("Powrot", "back", (screen.get_width() // 2 - 130, 380, 260, 52))
    launch.draw(screen, font, mouse)
    back.draw(screen, font, mouse)
    return [launch, back]
