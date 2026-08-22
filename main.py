"""Punkt startowy Rise & Glory.

Wlasciwa petla aplikacji mieszka w ``rg_core.app``. Ten plik pozostaje maly,
zeby uruchamianie gry nadal bylo tak proste jak ``python main.py``.
"""

import sys

from rg_core.bootstrap import install_legacy_module_aliases

install_legacy_module_aliases()

# Motyw czcionek instalujemy przed importem glownej aplikacji. Dzieki temu
# wszystkie ekrany korzystajace dotad z Ariala automatycznie dostaja bardziej
# klimatyczny kroj fantasy-serif bez przepisywania kazdego panelu osobno.
from rg_ui.font_theme import install_font_theme

install_font_theme()

from rg_core import app as _app
from rg_ui.city_hub import install_location_hub
from rg_ui.dev_council_reset import install_dev_council_reset
from rg_ui.hud_top_stat_theme import install_hud_top_stat_theme
from rg_ui.location_edge_bar_theme import install_location_edge_bar_theme
from rg_ui.map_background_fix import install_map_background
from rg_ui.map_camera_lock import install_locked_map_camera
from rg_ui.menu_button_fix import install_menu_button_fix
from rg_ui.player_config_theme import install_player_config_theme
from rg_ui.title_flow import install_into_main
from rg_ui.village_hub import install_village_hub
from rg_world.location_names import install_quest_location_name_compatibility

# DEV: kazde reczne otwarcie Rady rozpoczyna swieza sesje UI i dobiera kolejna
# karte z biezacej talii. Nie resetujemy samej talii Wydarzen Swiata.
install_dev_council_reset(_app)

# Stare techniczne nazwy lokacji (np. Wies 1) nadal sa rozpoznawane przez
# questy, ale gracz widzi juz stale nazwy wlasne wszystkich 9 lokacji.
install_quest_location_name_compatibility()

# Usuwamy jasne tlo/ramke zapisana w grafice panel2.png przyciskow menu.
install_menu_button_fix()

# Najpierw instalujemy viewport planszy. Dzieki temu same heksy i pionki sa
# przycinane do jasnego srodka pergaminu, ale tlo moze zostac narysowane na
# calym centralnym obszarze.
install_locked_map_camera()

# Zamiast czarnego tla pod plansza rysujemy grafike Grafiki/tlo_heksow.png.
install_map_background()

# Zachowujemy zgodnosc z poprawkami ekranu tytulowego, ktore odwoluja sie do
# modulu "main". Faktyczna aplikacja jest teraz w rg_core.app.
sys.modules["main"] = _app
install_into_main()

# Kafle klas na ekranie wyboru bohatera korzystaja z dokladnie tej samej
# grafiki panel2.png co dolne przyciski. Instalujemy to po title_flow, aby
# docelowy renderer nie zostal nadpisany przez starszy motyw ekranu.
install_player_config_theme(_app)

# Wszystkie gorne pola HUD-u (Gracz, Bohater, Klasa, Legenda, Zloto, Rany,
# Akcje, Runda i Rada) korzystaja teraz z tej samej grafiki panel2.png co
# pozostale przyciski UI, zamiast z prostych placeholderowych ramek.
install_hud_top_stat_theme()

# Starszy ekran wsi zostaje pod spodem jako fallback dla malego okna, questow
# oraz sytuacji, w ktorej zabraknie ktoregos assetu nowego ekranu.
install_village_hub(_app)

# Wspolny shell lokacji obsluguje wszystkie 9 generowanych miejsc:
# miasto1/2/3, zamek1/2/3 oraz wies1/2/3. Lewy i prawy panel sa wspolne,
# a srodkowa scena jest dobierana z numeru oraz typu konkretnej lokacji.
# Prawy content nadal pozostaje pustym kontenerem do dalszego projektowania.
install_location_hub(_app)

# Gorny i dolny pas ekranu lokacji korzystaja z pelnego panel2.png, dzieki
# czemu widoczne sa zlote naroza i ornamenty na calej ramie zamiast samych linii.
install_location_edge_bar_theme()


if __name__ == "__main__":
    _app.main()
