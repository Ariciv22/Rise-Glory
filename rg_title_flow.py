import sys

import pygame

import rg_screens as _screens


def _sync_layout(screen):
    width, height = screen.get_size()
    _screens.SCREEN_WIDTH = width
    _screens.SCREEN_HEIGHT = height
    return width, height


def _draw_title_background(screen, dim_alpha):
    width, height = _sync_layout(screen)
    background = _screens._load_menu_background((width, height))
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(_screens.BG)

    if dim_alpha > 0:
        shade = pygame.Surface((width, height), pygame.SRCALPHA