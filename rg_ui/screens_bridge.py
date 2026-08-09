"""Most ekranów używany przez starą pętlę aplikacji.

Re-eksportuje dotychczasowe ekrany z ``rg_ui.screens``, ale wejście do Rady
prowadzi przez nowy przepływ: Wieści ze świata -> Wydarzenie -> gotowość graczy
-> właściwy ekran Rady.
"""

from rg_ui.screens import *  # noqa: F401,F403
from rg_ui.council_flow import draw_council

__all__ = [name for name in globals() if not name.startswith("_")]
