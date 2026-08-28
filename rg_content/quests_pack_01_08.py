"""Finalne Questy 1-8."""

from __future__ import annotations

from rg_content.quest_pack_common import (
    BRAN,
    KROTKI_MIECZ,
    LEKKOMYSLNY_ZNACHOR,
    O,
    Q,
    R,
    S,
    TOPOR_KATA,
    fx,
    ri,
    rm,
)


Q1 = Q(
    1,
    "dzwon_miedzy_nami",
    "Dzwon miedzy nami",
    board_location="Elarin",
    issuer="Wojt Elarin",
    board_text=(
        "Od kilku nocy mieszkancow Elarin budzi bicie starego dzwonu dobiegajace z opuszczonego cmentarza. "
        "Kaplica od lat stoi pusta, a mimo to dzwon odzywa sie po zmroku. Poszukiwany jest ktos, kto zbada sprawe "
        "i sprawi, aby mieszkancy ponownie mogli zaznac spokojnego snu."
    ),
    description="Nocami z okolic starego cmentarza w Elarin slychac bicie dzwonu.",
    objective="Ustal, dlaczego dzwon bije, i zdecyduj jak zakonczyc sprawe.",
    length="Sredni",
    reward_hint="Zloto, ekwipunek lub wyjatkowa nagroda.",
    stages=[
        S(
            1,
            "Co dzieje sie na cmentarzu?",
            "Stary cmentarz i kaplica od lat powinny byc puste.",
            O("q01_mieszkancy", "Wypytaj mieszkancow", stat="Dyplomacja", threshold=12, on_success="stage:2"),
            O("q01_slady", "Zbadaj slady na cmentarzu", stat="Nauka", threshold=10, on_success="stage:4"),
            location="Elarin",
        ),
        S(
            2,
            "Dzwonnica",
            "W starej kaplicy znajduje sie mechanizm dzwonu i rzeczy dawnego opiekuna.",
            O(
                "q01_okno",
                "Przeszukaj okno",
                option_type="automatic",
                on_success="stage:2",
                success_effects=[
                    fx("wound", amount=1),
                    fx("gold", amount=4),
                    fx("random_item", spec=ri("armor", "zwykla")),
                    fx("disable_option", option_id="q01_okno", reason="Okno zostalo juz przeszukane."),
                ],
            ),
            O(
                "q01_mechanizm",
                "Zablokuj mechanizm",
                option_type="payment",
                consumes={"materials": {"Drewno": 4}, "goods": {"Wytrychy": 1}},
                on_success="complete:dzwon_uciszony",
            ),
            O(
                "q01_instrukcja",
                "Uzyj Instrukcji Trolfa",
                option_type="automatic",
                requires={"quest_item": "Instrukcja Trolfa"},
                on_success="complete:dzwon_uciszony",
            ),
            O(
                "q01_zapasy",
                "Przeszukaj zapasy opiekuna",
                option_type="automatic",
                on_success="stage:3",
                success_effects=[
                    fx("materials", values={"Drewno": 2, "Zelazo": 1}),
                    fx("goods", values={"Ziola lecznicze": 3}),
                    fx("markers", count=1, payload={"label": "Trolf w Valdren", "location": "Valdren"}),
                    fx("disable_option", option_id="q01_zapasy", reason="Zapasy zostaly juz przeszukane."),
                ],
            ),
            location="Elarin",
        ),
        S(
            3,
            "Rzemieslnik z Valdren",
            "Trolf nalezal do gildii, ktora montowala mechanizm dzwonu.",
            O("q01_trolf_dypl", "Rozpytaj rzemieslnikow", stat="Dyplomacja", threshold=11, on_success="stage:6", success_effects=[fx("set_flag", key="trolf_found", value=True)]),
            O("q01_trolf_intr", "Szukaj znakow gildii", stat="Intryga", threshold=13, on_success="stage:6", success_effects=[fx("set_flag", key="trolf_found", value=True), fx("set_flag", key="trolf_leverage", value=True)]),
            location="Valdren",
        ),
        S(
            4,
            "Grob opiekuna",
            "Slady prowadza do Eldana, syna dawnego opiekuna cmentarza.",
            O("q01_eldan", "Sklon Eldana do rozmowy", stat="Dyplomacja", threshold=11, on_success="stage:5"),
            location="Elarin",
        ),
        S(
            5,
            "Tajemnica Eldana",
            "Eldan przyznaje, ze nocami uruchamial dzwon, wspominajac ojca. Obiecuje przestac.",
            O("q01_tajemnica", "Zachowaj tajemnice", option_type="choice", on_success="complete:tajemnica_eldana"),
            O("q01_wydaj", "Wydaj Eldana mieszkanca", option_type="choice", on_success="complete:eldan_wygnany"),
            location="Elarin",
            point_of_no_return=True,
        ),
        S(
            6,
            "Spotkanie z Trolfem",
            "Trolf pamieta dzwon i uwaza, ze stary metal ma duza wartosc.",
            O("q01_trolf_bierze", "Pozwol Trolfowi zabrac dzwon", option_type="choice", on_success="complete:dzwon_zabrany"),
            O("q01_trolf_kup", "Kup wiedze o mechanizmie", option_type="payment", consumes={"gold": 3}, on_success="stage:2", success_effects=[fx("quest_item", item="Instrukcja Trolfa")]),
            O("q01_trolf_kup_taniej", "Kup wiedze po nizszej cenie", option_type="payment", consumes={"gold": 2}, visible_if={"flag": "trolf_leverage", "equals": True}, on_success="stage:2", success_effects=[fx("quest_item", item="Instrukcja Trolfa")]),
            location="Valdren",
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "dzwon_uciszony": R(7, 2, random_items=[ri("helmet", "zwykla")]),
        "dzwon_zabrany": R(9, 1, items=[KROTKI_MIECZ], goods={"Wytrychy": 4}),
        "tajemnica_eldana": R(11, 1, helpers=[BRAN]),
        "eldan_wygnany": R(14, 2, random_items=[ri("helmet", "zwykla"), ri("ring", "zwykla")]),
    },
)


Q2 = Q(
    2,
    "pomocnik_kata",
    "Pomocnik kata",
    board_location="Valdren",
    issuer="Kat Garran",
    board_text=(
        "Jutro o swicie wykonanych zostanie osiem prawomocnych wyrokow. Kat Garran szuka osoby o mocnych nerwach, "
        "ktora pomoze przygotowac miejsce egzekucji i dopilnowac skazancow. Za pomoc przewidziano dobra zaplate."
    ),
    description="Garran potrzebuje pomocnika przy egzekucji osmiu skazancow.",
    objective="Pomoz Garranowi albo zbadaj, dlaczego osme nazwisko trafilo na liste.",
    length="Dlugi",
    time_limit={"clock": "player_turn", "amount": 3, "on_expire": "fail"},
    stages=[
        S(
            1,
            "Oferta Garrana",
            "Lista skazancow zawiera osiem nazwisk.",
            O("q02_praca", "Przyjmij prace bez pytan", option_type="choice", on_success="stage:2"),
            O("q02_garran", "Wypytaj Garrana", stat="Dyplomacja", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="podejrzenie_listy", value=True)]),
            O("q02_dokumenty", "Obejrzyj dokumenty", stat="Intryga", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="lista_zmieniona", value=True)]),
            location="Valdren",
        ),
        S(
            2,
            "Szafot",
            "Oren probuje zwrocic uwage bohatera tuz przed egzekucja.",
            O("q02_oren", "Porozmawiaj z Orenem", stat="Dyplomacja", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="zeznanie_orena", value=True)]),
            O("q02_rzeczy", "Przeszukaj rzeczy Orena", stat="Intryga", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="ksiega_orena", value=True)]),
            O("q02_wykonaj", "Zignoruj Orena i wykonuj polecenia", option_type="choice", on_success="complete:rece_kata"),
            location="Valdren",
        ),
        S(
            3,
            "Trop korupcji",
            "Mardek moze stac za dopisaniem Orena do listy.",
            O("q02_pieczecie", "Sprawdz pieczecie i dokument", stat="Nauka", threshold=11, on_success="stage:4", success_effects=[fx("set_flag", key="dowod_falszerstwa", value=True)]),
            O("q02_poslaniec", "Sledz poslanca", stat="Intryga", threshold=14, on_success="stage:4", success_effects=[fx("set_flag", key="dowod_lapowki", value=True)]),
            O("q02_kancelaria", "Odnajdz kancelarie Mardeka", stat="Dyplomacja", threshold=12, on_success="stage:4"),
            location="Valdren",
        ),
        S(
            4,
            "Ostatnia godzina",
            "Egzekucja ma rozpoczac sie lada chwila.",
            O("q02_a", "Wykonaj umowe z Garranem", option_type="choice", on_success="complete:rece_kata"),
            O("q02_b", "Wstrzymaj egzekucje Orena", stat="Dyplomacja", threshold=14, on_success="complete:osmy_skazaniec"),
            O("q02_b_dowod", "Wstrzymaj egzekucje, pokazujac dowody", stat="Dyplomacja", threshold=12, visible_if={"flag": "dowod_falszerstwa", "equals": True}, on_success="complete:osmy_skazaniec"),
            O("q02_c", "Szantazuj Mardeka", stat="Intryga", threshold=15, on_success="complete:brudny_kompromis"),
            O("q02_c_dowod", "Szantazuj Mardeka twardym dowodem", stat="Intryga", threshold=13, visible_if={"flag": "dowod_lapowki", "equals": True}, on_success="complete:brudny_kompromis"),
            location="Valdren",
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "rece_kata": R(15, 2, items=[TOPOR_KATA]),
        "osmy_skazaniec": R(7, 3),
        "brudny_kompromis": R(20, 1),
    },
)


Q3 = Q(
    3,
    "ostatni_spichlerz",
    "Ostatni spichlerz",
    board_location="Thalwen",
    issuer="Klasztor w Thalwen",
    board_text=(
        "Po slabych zbiorach grupa mieszkancow gromadzi sie przed klasztornym spichlerzem i zada wydania zapasow. "
        "Klasztor szuka osoby, ktora opanuje sytuacje zanim dojdzie do rozlewu krwi."
    ),
    description="Glod i zimowa rezerwa stawiaja klasztor oraz mieszkancow po przeciwnych stronach.",
    objective="Poznaj prawdziwy stan zapasow i zdecyduj o losie spichlerza.",
    length="Sredni",
    stages=[
        S(1, "Glod pod murami klasztoru", "Thalwen jest blisko wybuchu.",
          O("q03_ludzie", "Porozmawiaj z mieszkancami", stat="Dyplomacja", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="glod_potwierdzony", value=True)]),
          O("q03_przeor", "Porozmawiaj z przeorem", stat="Dyplomacja", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="stanowisko_klasztoru", value=True)]),
          O("q03_spichlerz", "Zakradnij sie do spichlerza", stat="Intryga", threshold=13, on_success="stage:2", success_effects=[fx("set_flag", key="realne_zapasy", value=True)]), location="Thalwen"),
        S(2, "Kto kontroluje chleb", "Zapasami i cenami manipuluje wiecej niz jedna strona.",
          O("q03_rynek", "Przesledz rynek zboza", stat="Handel", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="radomir_spekuluje", value=True)]),
          O("q03_rezerwa", "Policz zimowa rezerwe", stat="Nauka", threshold=11, on_success="stage:3", success_effects=[fx("set_flag", key="mozliwy_podzial", value=True)]),
          O("q03_transport", "Sprawdz planowane transporty", stat="Intryga", threshold=14, on_success="stage:3", success_effects=[fx("set_flag", key="sprzedaz_valdren", value=True)]), location="Thalwen"),
        S(3, "Noc pod spichlerzem", "Tlum gromadzi sie przed bramami.",
          O("q03_a_d", "Powstrzymaj tlum rozmowa", stat="Dyplomacja", threshold=14, on_success="complete:zamkniete_bramy"),
          O("q03_a_w", "Bron spichlerza", stat="Walka", threshold=13, on_success="complete:zamkniete_bramy"),
          O("q03_b", "Doprowadz do podzialu chleba", stat="Dyplomacja", threshold=14, on_success="complete:podzielony_chleb"),
          O("q03_b_latwiej", "Wykaz, ze podzial jest bezpieczny", stat="Dyplomacja", threshold=12, visible_if={"flag": "mozliwy_podzial", "equals": True}, on_success="complete:podzielony_chleb"),
          O("q03_c_i", "Pomoz przejac spichlerz podstepem", stat="Intryga", threshold=14, on_success="complete:chleb_sila"),
          O("q03_c_w", "Pomoz przejac spichlerz sila", stat="Walka", threshold=14, on_success="complete:chleb_sila"),
          location="Thalwen", point_of_no_return=True),
    ],
    ending_rewards={
        "zamkniete_bramy": R(14, 1, food={"Jedzenie": 2}),
        "podzielony_chleb": R(8, 2, food={"Jedzenie": 3}),
        "chleb_sila": R(5, 1, food={"Jedzenie": 5}),
    },
)


Q4 = Q(
    4,
    "zelazo_pod_sianem",
    "Zelazo pod sianem",
    board_location="Norven",
    issuer="Straz Vargard",
    board_text=(
        "Podczas kontroli w Norven odnaleziono ukryty sklad starej i nowej broni. Wladze Vargard szukaja kogos, "
        "kto ustali pochodzenie arsenalu i sprawdzi, czy wies przygotowuje dzialania zbrojne."
    ),
    description="W stodole Norven ukryto arsenal, ktorego historia siega dawnej wiejskiej strazy.",
    objective="Ustal pochodzenie broni i zdecyduj o losie arsenalu.",
    length="Sredni",
    stages=[
        S(1, "Arsenal w stodole", "Bron nie pochodzi z jednego okresu.",
          O("q04_stara", "Zbadaj stara bron", stat="Nauka", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="stara_bron", value=True)]),
          O("q04_historia", "Wypytaj gospodarza", stat="Dyplomacja", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="historia_strazy", value=True)]),
          O("q04_nowa", "Szukaj swiezych sladow", stat="Intryga", threshold=13, on_success="stage:2", success_effects=[fx("set_flag", key="nowa_bron", value=True)]), location="Norven"),
        S(2, "Seran i dawna straz", "Dokumenty i nocne szkolenia moga wyjasnic sprawe.",
          O("q04_rejestry", "Sprawdz stare rejestry w Vargard", stat="Nauka", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="stare_dokumenty", value=True)]),
          O("q04_szkolenia", "Obserwuj Norven noca", stat="Intryga", threshold=14, on_success="stage:3", success_effects=[fx("set_flag", key="szkolenia_serana", value=True)]),
          O("q04_seran", "Porozmawiaj z Seranem", stat="Dyplomacja", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="motyw_serana", value=True)])),
        S(3, "Los arsenalu", "Decyzja przesadzi o obronie Norven.",
          O("q04_a", "Przekaz arsenal Vargard", option_type="choice", on_success="complete:rozbrojona_wies"),
          O("q04_b", "Zalegalizuj Straz Norven", stat="Dyplomacja", threshold=14, on_success="complete:straz_norven"),
          O("q04_b_dok", "Powołaj sie na stare dokumenty", stat="Dyplomacja", threshold=12, visible_if={"flag": "stare_dokumenty", "equals": True}, on_success="complete:straz_norven"),
          O("q04_c", "Ukryj najlepsza bron", stat="Intryga", threshold=15, on_success="complete:tajny_arsenal"),
          O("q04_c_latwiej", "Wykorzystaj wiedze o szkoleniach", stat="Intryga", threshold=13, visible_if={"flag": "szkolenia_serana", "equals": True}, on_success="complete:tajny_arsenal"), point_of_no_return=True),
    ],
    ending_rewards={
        "rozbrojona_wies": R(13, 1, random_items=[ri("weapon", "zwykla")]),
        "straz_norven": R(7, 2, random_items=[ri("ring", "rzadka")]),
        "tajny_arsenal": R(5, 1, random_items=[ri("weapon", "rzadka")]),
    },
)


Q5 = Q(
    5,
    "ogrod_umartego",
    "Ogrod umarlego",
    board_location="Eryndor",
    issuer="Straz Eryndor",
    board_text=(
        "Przy drodze odnaleziono cialo nieznanego mezczyzny. Wkrotce ziemia wokol zwlok zaczela porastac setkami "
        "kwiatow mimo wczesniejszej jalowosci. Straz chce ustalic, czy zjawisko stanowi zagrozenie."
    ),
    description="Czarne nasiono zaszyte w ciele prowadzi do historii Starego Ogrodu.",
    objective="Poznaj przeznaczenie nasiona i zdecyduj, co z nim zrobic.",
    length="Sredni",
    stages=[
        S(1, "Kwiaty na zwlokach", "Cialo skrywa wiecej niz przyczyne smierci.",
          O("q05_nasiono", "Zbadaj cialo", stat="Nauka", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="odkryto_nasiono", value=True)]),
          O("q05_symbole", "Rozpoznaj symbole", stat="Kultura", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="straznicy_ogrodow", value=True)]),
          O("q05_mapa", "Przeszukaj rzeczy zmarlego", stat="Intryga", threshold=13, on_success="stage:2", success_effects=[fx("set_flag", key="trop_calvena", value=True)]), location="Eryndor"),
        S(2, "Nasiono", "Zmarły mial dostarczyc nasiono do miejsca zwanego Starym Ogrodem.",
          O("q05_wydobadz", "Bezpiecznie wydobadz nasiono", stat="Nauka", threshold=13, on_success="stage:3", success_effects=[fx("quest_item", item="Nasiono Ogrodu"), fx("set_flag", key="nasiono_zabezpieczone", value=True)]),
          O("q05_ogrod", "Ustal polozenie Starego Ogrodu", stat="Kultura", threshold=13, on_success="stage:3", success_effects=[fx("markers", count=1, payload={"label": "Stary Ogrod", "place_id": "stary_ogrod"})]),
          O("q05_calven", "Odnajdz Calvena", stat="Dyplomacja", threshold=12, visible_if={"flag": "trop_calvena", "equals": True}, on_success="stage:3", success_effects=[fx("set_flag", key="oferta_calvena", value=True)])),
        S(3, "Los nasiona", "Nasiono moze zostac zniszczone, zwrocone albo sprzedane.",
          O("q05_a", "Zniszcz nasiono", stat="Nauka", threshold=12, on_success="complete:nasiono_zniszczone"),
          O("q05_b", "Zasadz nasiono w Starym Ogrodzie", stat="Nauka", threshold=13, on_success="complete:ogrod_odrodzony"),
          O("q05_b_auto", "Zasadz bezpiecznie zabezpieczone nasiono", option_type="automatic", visible_if={"flag": "nasiono_zabezpieczone", "equals": True}, on_success="complete:ogrod_odrodzony"),
          O("q05_c", "Sprzedaj nasiono Calvenowi", option_type="choice", requires={"quest_item": "Nasiono Ogrodu"}, visible_if={"flag": "oferta_calvena", "equals": True}, on_success="complete:nasiono_sprzedane"), point_of_no_return=True),
    ],
    ending_rewards={
        "nasiono_zniszczone": R(10, 1, random_materials=[rm(3)]),
        "ogrod_odrodzony": R(6, 2, random_items=[ri("amulet", "rzadka")]),
        "nasiono_sprzedane": R(18, 1, random_materials=[rm(1, rare=True)]),
    },
)


Q6 = Q(
    6,
    "za_zamknieta_brama",
    "Za zamknieta brama",
    board_location="Lirion",
    issuer="Rada Lirion",
    board_text=(
        "Jedna z dzielnic Lirion zostala objeta kwarantanna po wystapieniu gwaltownej goraczki i ciemnych plam. "
        "Liczba chorych rosnie, a rada szuka osoby, ktora ustali zrodlo choroby i zatrzyma jej rozprzestrzenianie."
    ),
    description="Kwarantanna skrywa skazone zboze i interesy kupca Malvena.",
    objective="Ustal zrodlo choroby i zdecyduj o losie zamknietej dzielnicy.",
    length="Dlugi",
    stages=[
        S(1, "Kordon", "Straz pilnuje zamknietej dzielnicy.",
          O("q06_varlen", "Porozmawiaj z Varlenem", stat="Dyplomacja", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="mapa_choroby", value=True)]),
          O("q06_pyl", "Zbadaj chorego", stat="Nauka", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="trop_zboza", value=True)]),
          O("q06_malven", "Obserwuj ludzi Malvena", stat="Intryga", threshold=13, on_success="stage:2", success_effects=[fx("set_flag", key="malven_omija_kordon", value=True)]), location="Lirion"),
        S(2, "Magazyn Pod Trzema Kolami", "W magazynie leza worki podejrzanego zboza.",
          O("q06_zrodlo", "Zbadaj zboze", stat="Nauka", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="zrodlo_potwierdzone", value=True)]),
          O("q06_dowod", "Przeszukaj dokumenty Malvena", stat="Intryga", threshold=14, on_success="stage:3", success_effects=[fx("set_flag", key="dowod_malvena", value=True)]),
          O("q06_spal", "Zniszcz skazone zboze", option_type="automatic", visible_if={"flag": "zrodlo_potwierdzone", "equals": True}, on_success="stage:3", success_effects=[fx("set_flag", key="zboze_zniszczone", value=True)]), location="Lirion"),
        S(3, "Kryzys kwarantanny", "Mieszkancy domagaja sie decyzji.",
          O("q06_a_d", "Utrzymaj kordon rozmowa", stat="Dyplomacja", threshold=14, on_success="complete:zelazny_kordon"),
          O("q06_a_w", "Utrzymaj kordon sila", stat="Walka", threshold=13, on_success="complete:zelazny_kordon"),
          O("q06_b", "Zorganizuj lazaret", stat="Nauka", threshold=14, on_success="complete:lazaret"),
          O("q06_b_latwiej", "Zorganizuj lazaret po zniszczeniu zrodla", stat="Nauka", threshold=12, visible_if={"flag": "zboze_zniszczone", "equals": True}, on_success="complete:lazaret"),
          O("q06_c_d", "Otworz bramy negocjacja", stat="Dyplomacja", threshold=15, on_success="complete:otwarte_bramy"),
          O("q06_c_i", "Przelam kordon podstepem", stat="Intryga", threshold=14, on_success="complete:otwarte_bramy"), location="Lirion", point_of_no_return=True),
    ],
    ending_rewards={
        "zelazny_kordon": R(14, 1, random_items=[ri("boots", "zwykla", count=2)], helpers=[LEKKOMYSLNY_ZNACHOR]),
        "lazaret": R(8, 2, random_items=[ri("amulet", "rzadka")]),
        "otwarte_bramy": R(18, 1, random_items=[ri("ring", "rzadka")], random_materials=[rm(1, rare=True)]),
    },
)


Q7 = Q(
    7,
    "ziarno_za_murami",
    "Ziarno za murami",
    board_location="Valdren",
    issuer="Rada Valdren",
    board_text=(
        "Po slabych zbiorach Valdren wprowadzilo czasowy zakaz wywozu zboza. Przy bramie zatrzymano wozy kupieckie, "
        "ktorych wlasciciel twierdzi, ze kupil towar legalnie jeszcze przed wprowadzeniem zakazu."
    ),
    description="Zakaz wywozu zboza zderza interes miasta, kupcow i skorumpowanych urzednikow.",
    objective="Zbadaj transport i zdecyduj, gdzie trafi zboze.",
    length="Sredni",
    stages=[
        S(1, "Wozy przy bramie", "Transport zostal zatrzymany przez straz.",
          O("q07_umowa", "Sprawdz dokumenty zakupu", stat="Handel", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="legalny_zakup", value=True)]),
          O("q07_rezerwy", "Ocen miejskie rezerwy", stat="Nauka", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="realne_zapasy", value=True)]),
          O("q07_brama", "Sprawdz boczna brame", stat="Intryga", threshold=13, on_success="stage:2", success_effects=[fx("set_flag", key="boczna_brama", value=True)]), location="Valdren"),
        S(2, "Zakaz i jego beneficjenci", "Nie wszyscy rajcy traca na zakazie.",
          O("q07_skup", "Zbadaj ceny skupu", stat="Handel", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="niesprawiedliwy_skup", value=True)]),
          O("q07_gerold", "Zdobadz ksiege lapowek", stat="Intryga", threshold=14, on_success="stage:3", success_effects=[fx("set_flag", key="dowod_gerolda", value=True)]),
          O("q07_rada", "Porozmawiaj z rada", stat="Dyplomacja", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="rada_negocjuje", value=True)]), location="Valdren"),
        S(3, "Decyzja przy bramie", "Wozy czekaja na ostateczny rozkaz.",
          O("q07_a", "Poprzyj konfiskate transportu", option_type="choice", on_success="complete:zboze_zostalo"),
          O("q07_b", "Wynegocjuj ograniczony legalny handel", stat="Handel", threshold=14, on_success="complete:otwarty_handel"),
          O("q07_b_latwiej", "Oprzyj kompromis na realnych rezerwach", stat="Handel", threshold=12, visible_if={"flag": "realne_zapasy", "equals": True}, on_success="complete:otwarty_handel"),
          O("q07_c", "Przemyc wozy boczna brama", stat="Intryga", threshold=14, on_success="complete:nocny_transport"),
          O("q07_c_latwiej", "Uzyj poznanej bocznej bramy", stat="Intryga", threshold=12, visible_if={"flag": "boczna_brama", "equals": True}, on_success="complete:nocny_transport"), location="Valdren", point_of_no_return=True),
    ],
    ending_rewards={
        "zboze_zostalo": R(14, 1, food={"Jedzenie": 3}, random_items=[ri("armor", "zwykla")]),
        "otwarty_handel": R(9, 2, random_items=[ri("ring", "rzadka")], random_materials=[rm(3)]),
        "nocny_transport": R(20, 1, random_items=[ri("weapon", "rzadka")], goods={"Wytrychy": 2}),
    },
)


Q8 = Q(
    8,
    "martwy_poklad",
    "Martwy poklad",
    board_location="Eryndor",
    issuer="Zarzadca portu Eryndor",
    board_text=(
        "Do portu przydryfowala Srebrna Mewa bez zalogi. Na pokladzie znaleziono porzucone rzeczy marynarzy, slady "
        "choroby i nietkniety ladunek. Port szuka kogos, kto zbada statek i odnajdzie zaloge."
    ),
    description="Pusty statek wyglada na dotkniety zaraza, ale prawdziwe zrodlo problemu znajduje sie w beczkach z woda.",
    objective="Odnajdz zaloge, ustal zrodlo zatrucia i zdecyduj o losie Srebrnej Mewy.",
    length="Sredni",
    stages=[
        S(1, "Srebrna Mewa", "Statek przydryfowal pusty do Eryndor.",
          O("q08_objawy", "Zbadaj objawy na pokladzie", stat="Nauka", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="podejrzenie_wody", value=True)]),
          O("q08_lodz", "Sprawdz lodz ratunkowa", stat="Intryga", threshold=11, on_success="stage:2", success_effects=[fx("markers", count=1, payload={"label": "Stara latarnia"})]),
          O("q08_manifest", "Sprawdz manifest", stat="Handel", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="dodatkowe_beczki", value=True)]), location="Eryndor"),
        S(2, "Zaloga i woda", "Przy starej latarni odnajdujesz siedmiu zywych marynarzy.",
          O("q08_zatrucie", "Potwierdz zatrucie woda", stat="Nauka", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="zatrucie_potwierdzone", value=True)]),
          O("q08_dalven", "Przesledz pochodzenie beczek", stat="Intryga", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="dowod_dalvena", value=True)]),
          O("q08_oferta", "Skonfrontuj Dalvena", stat="Dyplomacja", threshold=13, visible_if={"flag": "dowod_dalvena", "equals": True}, on_success="stage:3", success_effects=[fx("set_flag", key="oferta_dalvena", value=True)])),
        S(3, "Los statku", "Port czeka na decyzje w sprawie statku i raportu.",
          O("q08_a", "Spal statek i ladunek", option_type="choice", on_success="complete:statek_spalony"),
          O("q08_b", "Oczysc statek i uratuj zaloge", stat="Nauka", threshold=14, on_success="complete:mewa_uratowana"),
          O("q08_b_latwiej", "Oczysc statek po potwierdzeniu zatrucia", stat="Nauka", threshold=11, visible_if={"flag": "zatrucie_potwierdzone", "equals": True}, on_success="complete:mewa_uratowana"),
          O("q08_c", "Przyjmij zaplate za cisze", stat="Dyplomacja", threshold=12, visible_if={"flag": "oferta_dalvena", "equals": True}, on_success="complete:dalven_ukryty"), point_of_no_return=True),
    ],
    ending_rewards={
        "statek_spalony": R(13, 1, random_materials=[rm(2, distinct=False)], random_items=[ri("armor", "rzadka")]),
        "mewa_uratowana": R(8, 2, random_items=[ri("armor", "rzadka"), ri("weapon", "zwykla")]),
        "dalven_ukryty": R(22, 1, random_items=[ri("amulet", "rzadka"), ri("weapon", "zwykla")]),
    },
)


QUESTS_01_08 = (Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8)
