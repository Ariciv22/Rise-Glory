"""Punkt startowy Rise & Glory.

Wlasciwa petla aplikacji mieszka w ``rg_core.app``. Ten plik pozostaje maly,
zeby uruchamianie gry nadal bylo tak proste jak ``python main.py``.
"""

import sys

from rg_core.bootstrap import install_legacy_module_aliases

install_legacy_module_aliases()

from rg_core import app as _app
from rg_ui.dev_council_reset import install_dev_council_reset
from rg_ui.map_background_fix import install_map_background
from rg_ui.map_camera_lock import install_locked_map_camera
from rg_ui.menu_button_fix import install_menu_button_fix
from rg_ui.title_flow import install_into_main

# DEV: kazde reczne otwarcie Rady rozpoczyna swieza sesje UI i dobiera kolejna
# karte z biezacej talii. Nie resetujemy samej talii Wydarzen Swiata.
install_dev_council_reset(_app)

# Usuwamy jasne tlo/ramke zapisana w grafice panel2.png przyciskow menu.
install_menu_button_fix()

# Najpierw instalujemy viewport planszy. Dzieki temu same heksy i pionki sa
# przycinane do jasnego srodka pergaminu, ale tlo moze zostac narysowane na
# calym centralnym obszarze.
install_locked_map_camera()

# Zamiast czarnego tla pod plansza rysujemy grafike Grafiki/tlo_heksow.png.
install_map_background()

# Zachowujemy zgodnosc z poprawkami ekranu tytulowego, ktore odwolują sie do
# modulu "main". Faktyczna aplikacja jest teraz w rg_core.app.
sys.modules["main"] = _app
install_into_main()


if __name__ == "__main__":
    _app.main()
