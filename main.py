"""Punkt startowy Rise & Glory.

Wlasciwa petla aplikacji mieszka w ``rg_core.app``. Ten plik pozostaje maly,
zeby uruchamianie gry nadal bylo tak proste jak ``python main.py``.
"""

import sys

from rg_core.bootstrap import install_legacy_module_aliases

install_legacy_module_aliases()

from rg_core import app as _app
from rg_ui.menu_button_fix import install_menu_button_fix
from rg_ui.title_flow import install_into_main

# Usuwamy jasne tlo/ramke zapisana w grafice panel2.png przyciskow menu.
install_menu_button_fix()

# Zachowujemy zgodnosc z poprawkami ekranu tytulowego, ktore odwolują sie do
# modulu "main". Faktyczna aplikacja jest teraz w rg_core.app.
sys.modules["main"] = _app
install_into_main()


if __name__ == "__main__":
    _app.main()
