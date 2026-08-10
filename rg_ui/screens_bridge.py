"""Most ekranów używany przez starą pętlę aplikacji.

Re-eksportuje dotychczasowe ekrany z ``rg_ui.screens``, ale wejście do Rady
prowadzi przez nowy przepływ: Wieści ze świata -> Wydarzenie -> gotowość graczy
-> przygotowanie ofert -> docelowy, sekwencyjny handel Rady.
"""

from rg_ui.screens import *  # noqa: F401,F403
from rg_ui import council as _legacy_council
from rg_ui.council_market_rules_bridge import draw_council as _draw_council_market

# ``council_flow`` korzysta z modułu ``rg_ui.council`` do samej sesji Wieści.
# Po fazie gotowości deleguje wywołanie ``draw_council`` z tego modułu, dlatego
# podmieniamy wyłącznie renderer właściwej Rady, pozostawiając losowanie
# Wydarzenia Świata i istniejące tło bez zmian.
_legacy_council.draw_council = _draw_council_market

from rg_ui.council_flow import draw_council  # noqa: E402
from rg_ui.council_market_ui_fixes import install_council_market_ui_fixes  # noqa: E402
from rg_ui.council_chat_position_fix import install_council_chat_position_fix  # noqa: E402
from rg_ui.council_docked_layout import install_council_docked_layout  # noqa: E402
from rg_ui.lan_entry import draw_multiplayer  # noqa: E402,F401

install_council_market_ui_fixes()
install_council_chat_position_fix()
install_council_docked_layout()

__all__ = [name for name in globals() if not name.startswith("_")]
