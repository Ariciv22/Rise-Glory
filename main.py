"""Punkt startowy Rise & Glory.

Wlasciwa petla aplikacji mieszka w ``rg_core.app``. Ten plik pozostaje maly,
zeby uruchamianie gry nadal bylo tak proste jak ``python main.py``.
"""

import sys

from rg_core.bootstrap import install_legacy_module_aliases
from rg_ui.map_camera_lock import install_locked_map_camera

# Szybki renderer planszy musi zostac zalozony zanim bootstrap zaimportuje
# rg_core.setup. Setup doklada potem znaczniki Questow, Miejsc i Wydarzen Swiata
# jako nakladki na ten renderer. Gdy kolejnosc byla odwrotna, pozniejsza podmiana
# Tile.draw kasowala czesc nakladek, a modul Zakladow potrafil przywrocic stary,
# wolny renderer skalujacy teksture osobno dla kazdego heksa w kazdej klatce.
install_locked_map_camera()
install_legacy_module_aliases()

# Motyw czcionek instalujemy przed importem glownej aplikacji. Dzieki temu
# wszystkie ekrany korzystajace dotad z Ariala automatycznie dostaja bardziej
# klimatyczny kroj fantasy-serif bez przepisywania kazdego panelu osobno.
from rg_ui.font_theme import install_font_theme

install_font_theme()

from rg_core import app as _app
from rg_ui.city_hub import install_location_hub
from rg_ui.dev_council_reset import install_dev_council_reset
from rg_ui.hero_figure_system import install_hero_figure_system
from rg_ui.hero_figure_visual_fix import install_hero_figure_visual_fix
from rg_ui.hud_top_stat_theme import install_hud_top_stat_theme
from rg_ui.location_edge_bar_theme import install_location_edge_bar_theme
from rg_ui.location_menu_hitbox_fix import install_location_menu_hitbox_fix
from rg_ui.location_navigation_fix import install_location_navigation_fix
from rg_ui.location_quest_board import install_location_quest_board
from rg_ui.map_background_fix import install_map_background
from rg_ui.menu_button_fix import install_menu_button_fix
from rg_ui.player_config_theme import install_player_config_theme
from rg_ui.production_hud import install_production_hud
from rg_ui.production_location_hub import install_production_location_hub
from rg_ui.title_flow import install_into_main
from rg_ui.village_hub import install_village_hub
from rg_world.location_names import install_quest_location_name_compatibility
from rg_world.production_visuals import install_production_visuals

# DEV: kazde reczne otwarcie Rady rozpoczyna swieza sesje UI i dobiera kolejna
# karte z biezacej talii. Nie resetujemy samej talii Wydarzen Swiata.
install_dev_council_reset(_app)

# Stare techniczne nazwy lokacji (np. Wies 1) nadal sa rozpoznawane przez
# questy, ale gracz widzi juz stale nazwy wlasne wszystkich 9 lokacji.
install_quest_location_name_compatibility()

# Usuwamy jasne tlo/ramke zapisana w grafice panel2.png przyciskow menu.
install_menu_button_fix()

# Renderer planszy zostal zainstalowany przed bootstrapem. W tym miejscu
# rg_core.setup zdazyl juz dolozyc swoje nakladki na Tile.draw, wiec teraz
# bezpiecznie opakowujemy caly lancuch tlem mapy.
install_map_background()

# Gotowe i budowane zaklady dostaja osobny, maly znacznik na swoim heksie.
# Modul przechwytuje aktualny Tile.draw dopiero tutaj, dzieki czemu zachowuje
# szybki renderer, tlo oraz nakladki Questow/Wydarzen.
install_production_visuals()

# Zachowujemy zgodnosc z poprawkami ekranu tytulowego, ktore odwoluja sie do
# modulu "main". Faktyczna aplikacja jest teraz w rg_core.app.
sys.modules["main"] = _app
install_into_main()

# Kafle klas na ekranie wyboru bohatera korzystaja z dokladnie tej samej
# grafiki panel2.png co dolne przyciski. Instalujemy to po title_flow, aby
# docelowy renderer nie zostal nadpisany przez starszy motyw ekranu.
install_player_config_theme(_app)

# Wybor wygladu bohatera steruje od teraz dwiema spojnymi grafikami: postacia
# bez podstawki na planszetce bohatera oraz ta sama postacia z podstawka jako
# pionkiem na mapie. Dziala dla gotowego, losowego i tworzonego bohatera.
install_hero_figure_system(_app)

# Wybory wygladu dostaja wysokie ramki z pelnymi sylwetkami, a aktywny pionek
# nie ma dodatkowego niebieskiego okregu pod podstawka.
install_hero_figure_visual_fix()

# Wszystkie gorne pola HUD-u (Gracz, Bohater, Klasa, Legenda, Zloto, Rany,
# Akcje, Runda i Rada) korzystaja teraz z tej samej grafiki panel2.png co
# pozostale przyciski UI, zamiast z prostych placeholderowych ramek.
install_hud_top_stat_theme()

# Dolny HUD pokazuje zawsze POTENCJAL wybranego heksa i daje akcje budowy lub
# testowego przejmowania, gdy aktywny bohater stoi na tym heksie.
install_production_hud(_app)

# Starszy ekran wsi zostaje pod spodem jako fallback dla malego okna, questow
# oraz sytuacji, w ktorej zabraknie ktoregos assetu nowego ekranu.
install_village_hub(_app)

# Wspolny shell lokacji obsluguje wszystkie 9 generowanych miejsc:
# miasto1/2/3, zamek1/2/3 oraz wies1/2/3. Lewy i prawy panel sa wspolne,
# a srodkowa scena jest dobierana z numeru oraz typu konkretnej lokacji.
install_location_hub(_app)

# Zakladka Zaklady pokazuje trzy gotowe inwestycje nalezace do lokacji oraz
# wolne prawa eksploatacji heksow podlegajacych tej lokacji.
install_production_location_hub()

# Lewy panel ma szesc widocznych kafelkow. Hitbox kazdego jest centrowany na
# srodku jego ikony i obejmuje cala widoczna ramke, bez martwych pasow pomiedzy
# tekstem a ikona. Usuwamy tez niewidoczny siodmy hitbox dodawany przez modul
# Zakladow, bo nie ma dla niego kafelka w aktualnym assetcie panelu.
install_location_menu_hitbox_fix()

# Tablica Ogloszen wypelnia gotowe pola prawego UI: ikona w kolku, grafika
# tablicy, trzy kafle ofert oraz pozioma karta Questa otwierana po kliknieciu.
# Instalujemy ja po Zakladach, aby oba moduly mogly wspoldzielic prawy panel.
install_location_quest_board()

# Strzalki na dole prawego panelu sa centrowane w prawdziwej wolnej stopce
# pomiedzy separatorem ostatniego slotu a ozdobna rama dolna. Przy renderze
# wycinany jest tez pusty czarny margines zapisany dookola assetow strzalek.
install_location_navigation_fix()

# Gorny i dolny pas ekranu lokacji korzystaja z pelnego panel2.png, dzieki
# czemu widoczne sa zlote naroza i ornamenty na calej ramie zamiast samych linii.
install_location_edge_bar_theme()


if __name__ == "__main__":
    _app.main()
