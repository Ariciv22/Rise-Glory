"""Finalne Questy 9-16."""

from __future__ import annotations

from rg_content.enemies import register_enemy
from rg_content.quest_pack_common import (
    LAMPA_ALRENA,
    O,
    Q,
    R,
    S,
    SWIADEK_DROGI,
    TROFEUM_BESTII,
    fx,
    ri,
    rm,
)


register_enemy({
    "id": "dorosly_skalny_drapiezca",
    "name": "Dorosly skalny drapiezca",
    "base_hp": 5,
    "armor_class": 12,
    "attack_bonus": 2,
    "damage": 1,
    "can_escape": False,
    "scale_with_world": True,
})
register_enemy({
    "id": "dorosly_skalny_drapiezca_garrik",
    "name": "Dorosly skalny drapiezca",
    "base_hp": 5,
    "armor_class": 11,
    "attack_bonus": 2,
    "damage": 1,
    "can_escape": False,
    "scale_with_world": True,
    "special": {"quest_note": "Obnizone KP odwzorowuje +1 do Walki od Garrika w tej walce."},
})


Q9 = Q(
    9,
    "ostatnia_woda",
    "Ostatnia woda",
    board_location="Elarin",
    issuer="Starszyzna Elarin",
    board_text=(
        "Pomiedzy trzema gospodarstwami wybuchl spor o dostep do wody. Jeden z kanalow zostal przegrodzony, nizej "
        "polozone pola wysychaja, a wlasciciele wzajemnie oskarzaja sie o kradziez wody."
    ),
    description="Konflikt o strumien okazuje sie lancuchem decyzji kilku gospodarstw.",
    objective="Ustal, gdzie znika woda, i wybierz sposob jej podzialu.",
    length="Sredni",
    stages=[
        S(1, "Bojka o strumien", "Kazda strona obwinia innego sasiada.",
          O("q09_spor", "Porozmawiaj z gospodarzami", stat="Dyplomacja", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="spor_rovenow", value=True)]),
          O("q09_przeplyw", "Zbadaj przeplyw", stat="Nauka", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="brakujaca_woda", value=True)]),
          O("q09_prawo", "Odszukaj stare prawo wodne", stat="Intryga", threshold=12, on_success="stage:2", success_effects=[fx("quest_item", item="Stare Prawo Wody"), fx("markers", count=1, payload={"label": "Wzgorza nad Elarin"})]), location="Elarin"),
        S(2, "Powyzej wsi", "Bran Cord skierowal czesc strumienia do zbiornika dla bydla.",
          O("q09_model", "Policz caly system", stat="Nauka", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="pelny_model_wody", value=True)]),
          O("q09_bran", "Poznaj motyw Brana", stat="Dyplomacja", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="motyw_brana", value=True)]),
          O("q09_roven", "Poznaj oferte Rovenow", stat="Handel", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="oferta_rovenow", value=True)])),
        S(3, "Podzial wody", "Trzeba ustalic nowy porzadek.",
          O("q09_a", "Przywroc dawne koryto", stat="Dyplomacja", threshold=14, on_success="complete:dawne_koryto"),
          O("q09_a_prawo", "Egzekwuj Stare Prawo Wody", stat="Dyplomacja", threshold=12, requires={"quest_item": "Stare Prawo Wody"}, on_success="complete:dawne_koryto"),
          O("q09_b", "Zbuduj trzy kanaly", stat="Nauka", threshold=14, consumes={"materials": {"Drewno": 4, "Kamien": 4, "Zelazo": 2}}, on_success="complete:trzy_kanaly"),
          O("q09_b_model", "Zbuduj kanaly wedlug pelnego modelu", stat="Nauka", threshold=12, visible_if={"flag": "pelny_model_wody", "equals": True}, consumes={"materials": {"Drewno": 4, "Kamien": 4, "Zelazo": 2}}, on_success="complete:trzy_kanaly"),
          O("q09_c", "Sprzedaj pierwszenstwo Rovenom", stat="Handel", threshold=13, visible_if={"flag": "oferta_rovenow", "equals": True}, on_success="complete:woda_rovenow"), point_of_no_return=True),
    ],
    ending_rewards={
        "dawne_koryto": R(10, 3, random_materials=[rm(3)]),
        "trzy_kanaly": R(7, 2, random_items=[ri("ring", "rzadka")]),
        "woda_rovenow": R(19, 1, random_items=[ri("weapon", "zwykla")], food={"Jedzenie": 2}),
    },
)


Q10 = Q(
    10,
    "falszywy_krol",
    "Falszywy krol",
    board_location="Lirion",
    issuer="Mennica Lirion",
    board_text=(
        "W miescie pojawila sie seria falszywych monet wyjatkowo dobrej jakosci. Czesc trafila do kupcow bezposrednio "
        "po wyplatach z miejskiego skarbca. Mennica szuka osoby, ktora ustali zrodlo falszerstw."
    ),
    description="Stary falszerz Daven i urzednik mennicy Olvar sa zwiazani z dwiema roznymi falami falszywych monet.",
    objective="Ustal, kto produkuje nowe falszywki, i zdecyduj o losie Davena.",
    length="Sredni",
    stages=[
        S(1, "Monety Davena", "Nowe falszywki nie pasuja do starych metod Davena.",
          O("q10_narzedzia", "Porownaj narzedzia", stat="Nauka", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="inne_narzedzia", value=True)]),
          O("q10_wyplaty", "Przesledz obieg monet", stat="Handel", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="trop_skarbca", value=True)]),
          O("q10_daven", "Odnajdz Davena", stat="Intryga", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="daven_odnaleziony", value=True)]), location="Lirion"),
        S(2, "Mennica", "Daven wskazuje urzednika Olvara Renna.",
          O("q10_magazyn", "Odnajdz magazyn Olvara", stat="Intryga", threshold=14, on_success="stage:3", success_effects=[fx("set_flag", key="magazyn_olvara", value=True)]),
          O("q10_kruszec", "Sprawdz bilans kruszcu", stat="Nauka", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="dowod_kruszcu", value=True)]),
          O("q10_zeznania", "Namow Davena do zeznan", stat="Dyplomacja", threshold=13, visible_if={"flag": "daven_odnaleziony", "equals": True}, on_success="stage:3", success_effects=[fx("set_flag", key="wspolpraca_davena", value=True)]), location="Lirion"),
        S(3, "Dwoch falszerzy", "Dowody pozwalaja rozstrzygnac sprawe.",
          O("q10_a", "Oddaj obu wladzom", option_type="choice", on_success="complete:obaj_skazani"),
          O("q10_b", "Zamien kare Davena na prace dla mennicy", stat="Dyplomacja", threshold=14, on_success="complete:daven_mennica"),
          O("q10_b_latwiej", "Wykorzystaj wspolprace Davena", stat="Dyplomacja", threshold=12, visible_if={"flag": "wspolpraca_davena", "equals": True}, on_success="complete:daven_mennica"),
          O("q10_c", "Pomoz Davenowi uciec z prawdziwymi monetami", stat="Intryga", threshold=15, on_success="complete:daven_uciekl"),
          O("q10_c_latwiej", "Uzyj wiedzy o magazynie", stat="Intryga", threshold=13, visible_if={"flag": "magazyn_olvara", "equals": True}, on_success="complete:daven_uciekl"), location="Lirion", point_of_no_return=True),
    ],
    ending_rewards={
        "obaj_skazani": R(14, 2, random_items=[ri("ring", "zwykla")], random_materials=[rm(3)]),
        "daven_mennica": R(9, 3, random_items=[ri("amulet", "rzadka")]),
        "daven_uciekl": R(24, 1, random_items=[ri("weapon", "rzadka")], goods={"Wytrychy": 2}),
    },
)


Q11 = Q(
    11,
    "dzwony_na_trwoge",
    "Dzwony na trwoge",
    board_location="Thalwen",
    issuer="Starszyzna Thalwen",
    board_text=(
        "Zwiadowcy donosza o uzbrojonej grupie zblizajacej sie do Thalwen. Wies nie ma dosc ludzi do obrony. "
        "W starej wiezy od pokolen wisi dzwon, ktorego znaczenia prawie nikt juz nie pamieta."
    ),
    description="Dawny system alarmowy moze uratowac Thalwen przed banda Harkela.",
    objective="Przygotuj wies i powstrzymaj najazd.",
    length="Sredni",
    stages=[
        S(1, "Nocny alarm", "Harkel prowadzi ponad dwudziestu uzbrojonych ludzi.",
          O("q11_sygnal", "Odczytaj dawna sekwencje dzwonow", stat="Kultura", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="odczytano_sygnal", value=True)]),
          O("q11_barykady", "Przygotuj wies", stat="Dyplomacja", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="wies_gotowa", value=True)]),
          O("q11_zwiad", "Rozbij zwiad Harkela", stat="Walka", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="plan_najazdu", value=True)]), location="Thalwen"),
        S(2, "Harkel pod Thalwen", "Banda jest juz blisko wsi.",
          O("q11_a", "Uruchom siec dzwonow", stat="Kultura", threshold=14, on_success="complete:dzwony_odpowiedzialy"),
          O("q11_a_latwiej", "Uzyj odczytanej sekwencji", stat="Kultura", threshold=12, visible_if={"flag": "odczytano_sygnal", "equals": True}, on_success="complete:dzwony_odpowiedzialy"),
          O("q11_b", "Przekonaj Harkela, ze atak sie nie oplaca", stat="Dyplomacja", threshold=14, on_success="complete:harkel_odszedl"),
          O("q11_b_latwiej", "Pokaz gotowa obrone wsi", stat="Dyplomacja", threshold=12, visible_if={"flag": "wies_gotowa", "equals": True}, on_success="complete:harkel_odszedl"),
          O("q11_c", "Urzadz zasadzke", stat="Walka", threshold=14, on_success="complete:banda_rozbita"),
          O("q11_c_latwiej", "Uderz wedlug poznanego planu", stat="Walka", threshold=12, visible_if={"flag": "plan_najazdu", "equals": True}, on_success="complete:banda_rozbita"), location="Thalwen", point_of_no_return=True),
    ],
    ending_rewards={
        "dzwony_odpowiedzialy": R(9, 3, random_items=[ri("helmet", "rzadka")]),
        "harkel_odszedl": R(14, 2, random_items=[ri("armor", "zwykla")], random_materials=[rm(3)]),
        "banda_rozbita": R(12, 2, random_items=[ri("weapon", "rzadka")], goods={"Wytrychy": 2}),
    },
)


Q12 = Q(
    12,
    "prawo_gosciny",
    "Prawo gosciny",
    board_location="Lirion",
    issuer="Straz Lirion",
    board_text=(
        "W gospodzie Pod Bialym Jeleniem znaleziono ciala czterech podroznych ulozonych przy stole w niezwykly sposob. "
        "Straz szuka osoby znajacej dawne obyczaje lub metody sledcze."
    ),
    description="Czterech zmarlych, stary rytual i Korzen Drogi tworza pozornie kryminalna zagadke.",
    objective="Ustal przyczyne smierci i zdecyduj o losie zapomnianego zwyczaju.",
    length="Sredni",
    stages=[
        S(1, "Czterech martwych gosci", "Ciala zostaly ulozone zgodnie z nieznanym rytualem.",
          O("q12_rytual", "Rozpoznaj rytual", stat="Kultura", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="ostatnia_goscina", value=True)]),
          O("q12_herman", "Wypytaj Hermana", stat="Dyplomacja", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="pierwszy_stol_trop", value=True)]),
          O("q12_znak", "Zbadaj znak przy podroznych", stat="Intryga", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="znak_domow_goscinnych", value=True)]), location="Lirion"),
        S(2, "Domy Goscinne", "Stare prawo opisywalo obowiazki gospodarza wobec zmarlych pod jego dachem.",
          O("q12_historia", "Poznaj historie Domow Goscinnych", stat="Kultura", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="prawo_gosciny_poznane", value=True)]),
          O("q12_pierwszy", "Odszukaj Prawo Pierwszego Stolu", stat="Kultura", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="pierwszy_stol_poznany", value=True)]),
          O("q12_stol", "Przeszukaj stary pierwszy stol", option_type="automatic", on_success="stage:3", success_effects=[fx("set_flag", key="trop_erema", value=True)]), location="Lirion"),
        S(3, "Erem i Korzen Drogi", "Erem twierdzi, ze znalazl podroznych juz martwych.",
          O("q12_erem", "Porozmawiaj z Eremem", stat="Dyplomacja", threshold=11, on_success="stage:4", success_effects=[fx("set_flag", key="zeznanie_erema", value=True)]),
          O("q12_dzban", "Znajdz gliniany dzban", stat="Intryga", threshold=13, on_success="stage:4", success_effects=[fx("set_flag", key="dzban_korzenia", value=True)]),
          O("q12_korzen", "Rozpoznaj Korzen Drogi", stat="Kultura", threshold=14, on_success="stage:4", success_effects=[fx("set_flag", key="przyczyna_smierci", value=True)]), location="Lirion"),
        S(4, "Co zapisze kronika", "Prawda, kompromis albo cisza.",
          O("q12_a", "Ujawnij prawde i oczysc Erema", stat="Kultura", threshold=14, on_success="complete:prawda_ujawniona"),
          O("q12_a_latwiej", "Ujawnij pelny lancuch wydarzen", stat="Kultura", threshold=11, visible_if={"flag": "przyczyna_smierci", "equals": True}, on_success="complete:prawda_ujawniona"),
          O("q12_b", "Przywroc Pierwszy Stol", stat="Dyplomacja", threshold=13, visible_if={"flag": "pierwszy_stol_poznany", "equals": True}, on_success="complete:pierwszy_stol"),
          O("q12_c", "Ukryj prawdziwa historie", stat="Intryga", threshold=13, on_success="complete:zwyczaj_zapomniany"), location="Lirion", point_of_no_return=True),
    ],
    ending_rewards={
        "prawda_ujawniona": R(11, 3, random_items=[ri("amulet", "rzadka")], random_materials=[rm(3)]),
        "pierwszy_stol": R(7, 2, random_items=[ri("ring", "rzadka")]),
        "zwyczaj_zapomniany": R(20, 1, random_items=[ri("weapon", "zwykla")], goods={"Wytrychy": 2}),
    },
)


Q13 = Q(
    13,
    "zlodziej_zlodzieja",
    "Zlodziej zlodzieja",
    board_location="Valdren",
    issuer="Dyskretny kontakt z polswiatka",
    board_text=(
        "Poszukiwany ktos dyskretny i skuteczny. Pewien ladunek zostal przejety przez bande zwana Czarnymi Psami. "
        "Towar nalezy odzyskac, zanim zostanie sprzedany dalej. Zaplata odpowiednia do ryzyka. Bez pytan."
    ),
    description="Rogar chce odzyskac skrzynie, ktora jego ludzie sami wczesniej ukradli.",
    objective="Odzyskaj skrzynie Czarnych Psow i zdecyduj, do kogo naprawde nalezy lup.",
    length="Sredni",
    stages=[
        S(1, "Prosba Rogara", "Rogar chce odzyskac skrzynie przejeta przez Czarne Psy.",
          O("q13_rogar", "Wypytaj Rogara", stat="Dyplomacja", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="dokumenty_rogara", value=True), fx("markers", count=1, payload={"label": "Kamieniolom Czarnych Psow"})]),
          O("q13_napad", "Odtworz pierwotny napad", stat="Intryga", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="prawdziwi_wlasciciele", value=True), fx("markers", count=1, payload={"label": "Kamieniolom Czarnych Psow"})]),
          O("q13_bezpytan", "Przyjmij zlecenie bez pytan", option_type="choice", on_success="stage:2", success_effects=[fx("markers", count=1, payload={"label": "Kamieniolom Czarnych Psow"})]), location="Valdren"),
        S(2, "Czarne Psy", "Skrzynia jest pilnowana w kamieniolomie.",
          O("q13_skrycie", "Ukradnij skrzynie", stat="Intryga", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="skrzynia_odzyskana", value=True), fx("set_flag", key="znana_kryjowka", value=True)]),
          O("q13_kup", "Wykup skrzynie od Vareka", stat="Handel", threshold=14, consumes={"gold": 6}, on_success="stage:3", success_effects=[fx("set_flag", key="skrzynia_odzyskana", value=True)]),
          O("q13_walka", "Zmusc bande do porzucenia lupu", stat="Walka", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="skrzynia_odzyskana", value=True)])),
        S(3, "Do kogo nalezy lup", "Skrzynia zawiera tez wyplaty robotnikow i dokumenty paserow.",
          O("q13_a", "Oddaj wszystko Rogarowi", option_type="choice", on_success="complete:rogar_odzyskal"),
          O("q13_b", "Zwroc lup prawowitym wlascicielom", option_type="choice", visible_if={"flag": "prawdziwi_wlasciciele", "equals": True}, on_success="complete:lup_zwrocony"),
          O("q13_c", "Skroc obie bandy i zatrzymaj skrzynie", stat="Intryga", threshold=15, on_success="complete:trzeci_zlodziej"),
          O("q13_c_latwiej", "Wykorzystaj poznana kryjowke", stat="Intryga", threshold=13, visible_if={"flag": "znana_kryjowka", "equals": True}, on_success="complete:trzeci_zlodziej"), point_of_no_return=True),
    ],
    ending_rewards={
        "rogar_odzyskal": R(17, 1, random_items=[ri("weapon", "zwykla")], goods={"Wytrychy": 2}),
        "lup_zwrocony": R(8, 3, random_items=[ri("armor", "rzadka")], random_materials=[rm(3)]),
        "trzeci_zlodziej": R(23, 1, random_items=[ri("weapon", "rzadka"), ri("ring", "rzadka")]),
    },
)


Q14 = Q(
    14,
    "pogrzeb_przy_drodze",
    "Pogrzeb przy drodze",
    board_location="Artium",
    issuer="Zarzadca ziem przy Artium",
    board_text=(
        "Przy trakcie obcy podrozni przygotowuja pochowek jednego ze swoich. Wlasciciel ziemi zada przerwania ceremonii, "
        "a przybysze powoluja sie na stare Prawo Drogi. Potrzebny jest ktos, kto rozstrzygnie spor."
    ),
    description="Pogrzeb Sarvena laczy dawne prawo traktu z nieuczciwie przesunieta granica pola.",
    objective="Poznaj obrzad Szarego Traktu i zdecyduj, gdzie spocznie Sarven.",
    length="Sredni",
    stages=[
        S(1, "Swiadek Drogi", "Ludzie Szarego Traktu prosza obcego, by stal sie swiadkiem pogrzebu.",
          O("q14_lud", "Rozpoznaj Lud Szarego Traktu", stat="Kultura", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="szary_trakt", value=True)]),
          O("q14_mara", "Porozmawiaj z Mara", stat="Dyplomacja", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="historia_sarvena", value=True)]),
          O("q14_granica", "Zbadaj miejsce grobu", stat="Intryga", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="sporna_granica", value=True), fx("markers", count=1, payload={"label": "Miejsce pogrzebu Sarvena"})]), location="Artium"),
        S(2, "Obrzed i ziemia", "Derron obawia sie, ze grob stworzy precedens.",
          O("q14_obrzed", "Poznaj znaczenie obrzadu", stat="Kultura", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="obrzad_drogi", value=True)]),
          O("q14_derr", "Poznaj obawy Derrona", stat="Dyplomacja", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="obawa_derrora", value=True)]),
          O("q14_kamien", "Sprawdz kamienie graniczne", stat="Intryga", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="przesuniety_kamien", value=True)]),
          O("q14_prawo", "Odczytaj Prawo Drogi", stat="Kultura", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="prawo_drogi", value=True)])),
        S(3, "Los Sarvena", "Obie strony czekaja na rozstrzygniecie.",
          O("q14_a", "Przeprowadz pelny obrzad przy trakcie", stat="Kultura", threshold=14, on_success="complete:swiadek_drogi"),
          O("q14_a_latwiej", "Powołaj sie na Prawo Drogi", stat="Kultura", threshold=12, visible_if={"flag": "prawo_drogi", "equals": True}, on_success="complete:swiadek_drogi"),
          O("q14_b", "Doprowadz do dwoch pozegnan", stat="Dyplomacja", threshold=13, visible_if={"flag": "obrzad_drogi", "equals": True}, on_success="complete:dwa_pozegnania"),
          O("q14_c", "Przenies cialo na lokalny cmentarz", stat="Dyplomacja", threshold=14, on_success="complete:obrzad_przerwany"), point_of_no_return=True),
    ],
    ending_rewards={
        "swiadek_drogi": R(8, 3, random_items=[ri("amulet", "rzadka")], statuses=[SWIADEK_DROGI]),
        "dwa_pozegnania": R(12, 2, random_items=[ri("ring", "rzadka")], random_materials=[rm(3)]),
        "obrzad_przerwany": R(16, 1, random_items=[ri("weapon", "zwykla")], goods={"Wytrychy": 2}),
    },
)


Q15 = Q(
    15,
    "swieca_ktora_nie_gasnie",
    "Swieca, ktora nie gasnie",
    board_location="Eryndor",
    issuer="Kupiec Nerin",
    board_text=(
        "W moje rece trafila niezwykla swieca nalezaca niegdys do alchemika Alrena Vossa. Plomien nie gasnie mimo "
        "uplywu wielu godzin. Poszukuje osoby obeznanej z alchemia lub dawnymi wynalazkami."
    ),
    description="Samopodtrzymujacy sie plomien jest prototypem alchemicznej lampy o niebezpiecznym cisnieniu.",
    objective="Zbadaj wynalazek Alrena i zdecyduj, czy go zniszczyc, dokonczyc czy sprzedac.",
    length="Sredni",
    stages=[
        S(1, "Niemozliwy plomien", "Swieca pali sie nawet w warunkach, w ktorych zwykly ogien gasnie.",
          O("q15_plomien", "Zbadaj plomien", stat="Nauka", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="samopodtrzymanie", value=True)]),
          O("q15_rdzen", "Zbadaj metalowy rdzen", stat="Nauka", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="metalowy_rdzen", value=True)]),
          O("q15_pochodzenie", "Ustal pochodzenie", stat="Intryga", threshold=11, on_success="stage:2", success_effects=[fx("markers", count=1, payload={"label": "Pracownia Alrena"})]), location="Eryndor"),
        S(2, "Pracownia Alrena", "Notatki opisuja prototyp do kopaln, statkow i tuneli.",
          O("q15_notatki", "Odczytaj notatki", stat="Nauka", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="ryzyko_eksplozji", value=True)]),
          O("q15_reakcja", "Rozbierz nieudany rdzen", stat="Nauka", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="zasada_reakcji", value=True)])),
        S(3, "Los wynalazku", "Technologia moze zostac pogrzebana, uratowana albo sprzedana.",
          O("q15_a", "Rozdziel reagenty i zniszcz prototyp", stat="Nauka", threshold=13, on_success="complete:prototyp_zniszczony"),
          O("q15_b", "Zbuduj bezpieczna Lampe Alrena", stat="Nauka", threshold=15, on_success="complete:lampa_alrena"),
          O("q15_b_latwiej", "Dokoncz projekt na podstawie pelnych badan", stat="Nauka", threshold=12, visible_if={"flag": "ryzyko_eksplozji", "equals": True}, on_success="complete:lampa_alrena"),
          O("q15_c", "Sprzedaj prototyp Teralowi Mornowi", stat="Handel", threshold=13, on_success="complete:prototyp_sprzedany"), point_of_no_return=True),
    ],
    ending_rewards={
        "prototyp_zniszczony": R(12, 2, random_materials=[rm(3)], random_items=[ri("amulet", "zwykla")]),
        "lampa_alrena": R(8, 3, random_items=[ri("ring", "rzadka")], items=[LAMPA_ALRENA]),
        "prototyp_sprzedany": R(24, 1, random_items=[ri("weapon", "rzadka")], random_materials=[rm(2, distinct=False)]),
    },
)


Q16 = Q(
    16,
    "falszywy_bohater",
    "Falszywy bohater",
    board_location="Norven",
    issuer="Starszyzna Norven",
    board_text=(
        "Lowca Garrik przybyl do Norven z glowa bestii i oglosil zakonczenie problemu drapieznika. Tej samej nocy "
        "doszlo jednak do kolejnego ataku, a jeden z pasterzy zaginal. Starszyzna szuka kogos, kto sprawdzi sprawe."
    ),
    description="Garrik zabil tylko mlode stworzenie; dorosly skalny drapiezca nadal zyje.",
    objective="Odnajdz pasterza, odkryj prawde o Garriku i pokonaj dorosla bestie.",
    length="Sredni",
    stages=[
        S(1, "Bohater Norven", "Trofeum Garrika nie pasuje do sladów nowego ataku.",
          O("q16_trofeum", "Zbadaj trofeum", stat="Kultura", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="mlody_osobnik", value=True)]),
          O("q16_historia", "Wypytaj Garrika", stat="Dyplomacja", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="garrik_klamie", value=True)]),
          O("q16_slady", "Zbadaj nowy atak", stat="Intryga", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="dorosla_bestia", value=True)]), location="Norven"),
        S(2, "Prawda o trofeum", "Slady prowadza do rannego pasterza i legowiska doroslej bestii.",
          O("q16_swiadek", "Znajdz swiadka oszustwa", stat="Intryga", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="dowod_oszustwa", value=True)]),
          O("q16_pasterz", "Odnajdz i wyprowadz pasterza", stat="Walka", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="legowisko", value=True), fx("markers", count=1, payload={"label": "Legowisko skalnego drapieznika"})]),
          O("q16_garrik", "Skonfrontuj Garrika", stat="Dyplomacja", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="garrik_przyznal", value=True)])),
        S(3, "Prawdziwa bestia", "Trzeba zdecydowac, kto stanie przeciw doroslemu drapiezcy.",
          O("q16_a", "Daj Garrikowi druga szanse", stat="Dyplomacja", threshold=14, on_success="stage:4"),
          O("q16_a_latwiej", "Przekonaj Garrika po jego przyznaniu sie", stat="Dyplomacja", threshold=12, visible_if={"flag": "garrik_przyznal", "equals": True}, on_success="stage:4"),
          O("q16_b", "Zapoluj sam i ujawnij klamstwo", option_type="combat", enemy_id="dorosly_skalny_drapiezca", on_success="complete:bohater_prawdziwy"),
          O("q16_c", "Zachowaj klamstwo i zabij bestie po cichu", option_type="combat", enemy_id="dorosly_skalny_drapiezca", on_success="stage:5"), point_of_no_return=True),
        S(4, "Bohater za drugim razem", "Garrik idzie z toba i naprawde staje do walki.",
          O("q16_a_walka", "Walcz razem z Garrikiem", option_type="combat", enemy_id="dorosly_skalny_drapiezca_garrik", on_success="complete:garrik_odkupiony")),
        S(5, "Legenda za zloto", "Bestia nie zyje. Trzeba jeszcze utrzymac historie Garrika.",
          O("q16_c_intryga", "Upozoruj drugie zwyciestwo Garrika", stat="Intryga", threshold=13, on_success="complete:legenda_garrika", on_failure="complete:bohater_prawdziwy")),
    ],
    ending_rewards={
        "garrik_odkupiony": R(12, 3, random_items=[ri("weapon", "rzadka")], random_materials=[rm(3)]),
        "bohater_prawdziwy": R(16, 2, random_items=[ri("armor", "rzadka")], items=[TROFEUM_BESTII]),
        "legenda_garrika": R(22, 1, random_items=[ri("ring", "rzadka"), ri("weapon", "zwykla")]),
    },
)


QUESTS_09_16 = (Q9, Q10, Q11, Q12, Q13, Q14, Q15, Q16)
