from __future__ import annotations

import pygame


_INSTALLED = False
_ORIGINAL_LAYOUT = None


def _relative_rect(board: pygame.Rect, x: float, y: float, w: float, h: float) -> pygame.Rect:
    return pygame.Rect(
        int(board.x + board.width * x),
        int(board.y + board.height * y),
        max(1, int(board.width * w)),
        max(1, int(board.height * h)),
    )


def _player_board_layout_with_bottom_return(board):
    """Przenosi przycisk Powrot do mapy razem z jego hitboxem na dol planszetki."""
    layout = _ORIGINAL_LAYOUT(board)
    board = pygame.Rect(board)

    # Cel wskazany na planszetce: srodek dolnego pasa pod aktywnymi Questami.
    # Ten sam rect jest uzywany do rysowania i klikania, wiec stary hitbox
    # w prawym gornym rogu przestaje istniec.
    layout["close"] = _relative_rect(board, 0.508, 0.946, 0.145, 0.042)
    return layout


def install_player_board_return_button() -> None:
    global _INSTALLED, _ORIGINAL_LAYOUT
    if _INSTALLED:
        return

    from rg_core import app as app_module
    from rg_ui import player_board
    from rg_ui.pause_main_menu import install_pause_main_menu

    _ORIGINAL_LAYOUT = player_board.player_board_layout
    player_board.player_board_layout = _player_board_layout_with_bottom_return

    # Ten instalator jest uruchamiany z glownego bootstrapu po zaladowaniu app.py,
    # dlatego w tym samym miejscu bezpiecznie podpinamy menu pauzy z powrotem
    # do menu glownego. Sam kod pozostaje w osobnym module pause_main_menu.py.
    install_pause_main_menu(app_module)

    _INSTALLED = True
