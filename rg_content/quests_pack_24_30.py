"""Finalne Questy 24-30."""

from __future__ import annotations

from rg_content.quest_pack_common import O, Q, R, S, fx, ri, rm


WILK_TOWARZYSZ = {
    "id": "wilk_przy_palenisku",
    "name": "Wilk",
    "category": "companion",
    "effect_text": "+1 do testow Walki i Intrygi. Wilk rozpoznaje tropy ludzi oraz zwierzat.",
    "stat_bonus": {"Walka": 1, "Intryga": 1},
    "effects": {"tracking_companion": True},
}


Q24 = Q(
    24,
    "dlug_zmarlego",
    "Dlug zmarlego",
    board_location="Artium",
    issuer="Merena, wdowa po strazniku",
    board_text=(
        "Po smierci mojego meza w jego dokumentach znalazlam umowe pozyczki udzielonej miejscowemu mlynarzowi. "
        "Rodzina potrzebuje tych pieniedzy, ale mlynarz twierdzi, ze niczego juz nie jest winien. Szukam kogos, kto "
        "sprawdzi rachunki i doprowadzi sprawe do konca."
    ),
    description=(
        "Prawdziwa pozyczka miesza sie z latami nielegalnych oplat ochronnych pobieranych przez zmarlego straznika. "
        "Rodzina nie wiedziala, skad pochodzila czesc jego pieniedzy."
    ),
    objective="Ustal prawdziwy bilans miedzy rodzina zmarlego a mlynarzem i zdecyduj, co zrobic z długiem.",
    length="Sredni",
    stages=[
        S(
            1,
            "Papier po zmarlym",
            "Umowa pozyczki wyglada prawidlowo, ale w notatkach straznika regularnie powtarzaja sie dodatkowe kwoty.",
            O(
                "q24_umowa",
                "Sprawdz warunki pozyczki i terminy splaty",
                stat="Handel",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="prawdziwa_pozyczka", value=True)],
            ),
            O(
                "q24_notatki",
                "Poszukaj ukrytych zapisow w rachunkach straznika",
                stat="Intryga",
                threshold=12,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="dziwne_oplaty", value=True)],
            ),
            location="Artium",
        ),
        S(
            2,
            "Mlynarz Beren",
            "Beren przyznaje, ze pozyczyl pieniadze, ale pokazuje pokwitowania za wieloletnia 'ochrone', ktorej nigdy nie zamawial.",
            O(
                "q24_zeznanie",
                "Naklon Berena do opowiedzenia calej historii",
                stat="Dyplomacja",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="zeznanie_berena", value=True)],
            ),
            O(
                "q24_kwity",
                "Zweryfikuj stare pokwitowania i podpisy",
                stat="Intryga",
                threshold=13,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="dowod_wymuszen", value=True)],
            ),
        ),
        S(
            3,
            "Rachunek po smierci",
            "Pozyczka byla prawdziwa. Tak samo prawdziwe byly nielegalne oplaty pobierane przez zmarlego.",
            O(
                "q24_a",
                "Wyegzekwuj caly dlug dla rodziny",
                stat="Handel",
                threshold=13,
                on_success="complete:dlug_splacony",
            ),
            O(
                "q24_b",
                "Ujawnij wymuszenia i anuluj zobowiazanie",
                stat="Intryga",
                threshold=14,
                visible_if={"flag": "dowod_wymuszen", "equals": True},
                on_success="complete:dlug_anulowany",
            ),
            O(
                "q24_b_latwiej",
                "Polacz pokwitowania z ukrytymi zapisami straznika",
                stat="Intryga",
                threshold=12,
                visible_if={"flag": "dziwne_oplaty", "equals": True},
                on_success="complete:dlug_anulowany",
            ),
            O(
                "q24_c",
                "Doprowadz do ugody: czesc dla wdowy, reszta zostaje u mlynarza",
                stat="Dyplomacja",
                threshold=14,
                on_success="complete:ugoda_wdowy",
            ),
            O(
                "q24_c_latwiej",
                "Oprzyj ugode na obu prawdziwych rachunkach",
                stat="Dyplomacja",
                threshold=12,
                visible_if={"flag": "zeznanie_berena", "equals": True},
                on_success="complete:ugoda_wdowy",
            ),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "dlug_splacony": R(15, 1, random_items=[ri("ring", "zwykla")], random_materials=[rm(2)]),
        "dlug_anulowany": R(8, 3, random_items=[ri("amulet", "rzadka")], random_materials=[rm(3)]),
        "ugoda_wdowy": R(11, 2, random_items=[ri("ring", "rzadka")], random_materials=[rm(2)]),
    },
)


Q25 = Q(
    25,
    "most_bez_wlasciciela",
    "Most bez wlasciciela",
    board_location="Norven",
    issuer="Kupcy traktu Norven-Valdren",
    board_text=(
        "Stary most na trakcie do Valdren czesciowo sie zawalil. Norven twierdzi, ze utrzymanie przeprawy nalezy do "
        "miasta, a Valdren odpowiada, ze most od zawsze byl sprawa wsi. Handel stanal. Potrzebujemy kogos, kto ustali "
        "odpowiedzialnosc i doprowadzi do odbudowy."
    ),
    description=(
        "Dokumenty wlasnosci sa sprzeczne, a kupiec Keld od lat pobieral nieoficjalne myto i odkladal czesc dochodu."
    ),
    objective="Ustal, kto korzystał z mostu i kto powinien zaplacic za jego odbudowe.",
    length="Sredni",
    stages=[
        S(
            1,
            "Pekniete przęslo",
            "Most da sie uratowac, ale bez szybkiej naprawy kolejna wezbrana rzeka moze zabrac cala przeprawe.",
            O(
                "q25_konstrukcja",
                "Ocen stan mostu i zakres koniecznych prac",
                stat="Nauka",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="koszt_naprawy", value=True)],
            ),
            O(
                "q25_myto",
                "Sprawdz, kto faktycznie pobieral oplaty za przejazd",
                stat="Handel",
                threshold=12,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="slad_myta", value=True)],
            ),
            location="Norven",
        ),
        S(
            2,
            "Trzy rachunki",
            "Norven, Valdren i Keld przedstawiaja trzy rozne wersje historii mostu. Zadna nie jest calkiem falszywa.",
            O(
                "q25_keld",
                "Przejrzyj ksiegi kupca Kelda",
                stat="Handel",
                threshold=13,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="fundusz_myta", value=True)],
            ),
            O(
                "q25_strony",
                "Posadz przedstawicieli Norven i Valdren przy jednym stole",
                stat="Dyplomacja",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="gotowosc_do_ugody", value=True)],
            ),
        ),
        S(
            3,
            "Kto zaplaci",
            "Most moze zostac odbudowany natychmiast, ale kazde rozwiazanie stworzy nowego gospodarza przeprawy.",
            O(
                "q25_a",
                "Zmusc Kelda, by sfinansowal odbudowe z nieoficjalnego myta",
                stat="Handel",
                threshold=14,
                on_success="complete:keld_odbudowal",
            ),
            O(
                "q25_a_latwiej",
                "Przedstaw ksiegi funduszu myta",
                stat="Handel",
                threshold=12,
                visible_if={"flag": "fundusz_myta", "equals": True},
                on_success="complete:keld_odbudowal",
            ),
            O(
                "q25_b",
                "Doprowadz do wspolnej odbudowy Norven i Valdren",
                stat="Dyplomacja",
                threshold=14,
                on_success="complete:most_handlowy",
            ),
            O(
                "q25_b_latwiej",
                "Wykorzystaj gotowosc obu stron do ugody",
                stat="Dyplomacja",
                threshold=12,
                visible_if={"flag": "gotowosc_do_ugody", "equals": True},
                on_success="complete:most_handlowy",
            ),
            O(
                "q25_c",
                "Sprzedaj prawa do przeprawy prywatnej gildii",
                stat="Handel",
                threshold=13,
                on_success="complete:most_gildii",
            ),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "keld_odbudowal": R(16, 2, random_items=[ri("armor", "rzadka")], random_materials=[rm(2)]),
        "most_handlowy": R(9, 3, random_items=[ri("ring", "rzadka")], random_materials=[rm(3)]),
        "most_gildii": R(24, 1, random_items=[ri("amulet", "rzadka"), ri("weapon", "zwykla")]),
    },
)


Q26 = Q(
    26,
    "czwarty_syn",
    "Czwarty syn",
    board_location="Thalwen",
    issuer="Alena z Thalwen",
    board_text=(
        "Moj syn nie wrocil z polowania. Minely trzy dni, a jego luk znaleziono przy starym trakcie. Straz ma wazniejsze "
        "sprawy. Prosze o odnalezienie go, zywego albo martwego."
    ),
    description=(
        "Zaginiony syn zyje pod nowym imieniem i od lat buduje osobna tozsamosc. Matka wie, ze kiedys uciekl, ale nigdy "
        "nie pogodzila sie z jego decyzja."
    ),
    objective="Odnajdz zaginionego i rozstrzygnij, czy dawna rodzina ma prawo odebrac mu nowe zycie.",
    length="Sredni",
    stages=[
        S(
            1,
            "Slad po polowaniu",
            "Luk lezal przy trakcie celowo. Slady prowadza dalej, ale nie wygladaja jak trop rannego czlowieka.",
            O(
                "q26_trop",
                "Odczytaj slady pozostawione przy trakcie",
                stat="Intryga",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="ucieczka_planowana", value=True), fx("markers", count=1, payload={"label": "Chata Darena"})],
            ),
            O(
                "q26_opowiesci",
                "Popytaj o dawne znikniecia z rodziny Aleny",
                stat="Kultura",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="stara_historia", value=True), fx("markers", count=1, payload={"label": "Chata Darena"})],
            ),
            location="Thalwen",
        ),
        S(
            2,
            "Daren, nie Jorin",
            "Mezczyzna rozpoznaje Alene z opisu, lecz stanowczo twierdzi, ze od lat nazywa sie Daren. Ma dokumenty i wlasne zycie.",
            O(
                "q26_rozmowa",
                "Pozwol mu opowiedziec, dlaczego odszedl",
                stat="Dyplomacja",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="powod_ucieczki", value=True)],
            ),
            O(
                "q26_dokumenty",
                "Sprawdz jego dokumenty i droge nowej tozsamosci",
                stat="Intryga",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="nowa_tozsamosc_legalna", value=True)],
            ),
        ),
        S(
            3,
            "Czyj syn",
            "Alena zna szczegoly dziecinstwa Darena. Daren nie zaprzecza juz, kim byl. Nie chce jednak znow stac sie Jorinem.",
            O(
                "q26_a",
                "Naklon go do powrotu do matki",
                stat="Dyplomacja",
                threshold=14,
                on_success="complete:powrot_syna",
            ),
            O(
                "q26_b",
                "Zachowaj jego nowa tozsamosc w tajemnicy",
                stat="Intryga",
                threshold=13,
                on_success="complete:sekret_darena",
            ),
            O(
                "q26_b_latwiej",
                "Oprzyj historie na legalnych dokumentach Darena",
                stat="Intryga",
                threshold=11,
                visible_if={"flag": "nowa_tozsamosc_legalna", "equals": True},
                on_success="complete:sekret_darena",
            ),
            O(
                "q26_c",
                "Doprowadz do spotkania i pozwol Darenowi samemu zdecydowac",
                stat="Dyplomacja",
                threshold=14,
                on_success="complete:wybor_syna",
            ),
            O(
                "q26_c_latwiej",
                "Przygotuj obie strony na prawde o ucieczce",
                stat="Dyplomacja",
                threshold=12,
                visible_if={"flag": "powod_ucieczki", "equals": True},
                on_success="complete:wybor_syna",
            ),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "powrot_syna": R(14, 1, random_items=[ri("armor", "zwykla")], random_materials=[rm(2)]),
        "sekret_darena": R(9, 2, random_items=[ri("ring", "rzadka")], goods={"Wytrychy": 2}),
        "wybor_syna": R(7, 3, random_items=[ri("amulet", "rzadka")], random_materials=[rm(3)]),
    },
)


Q27 = Q(
    27,
    "cena_ciszy",
    "Cena ciszy",
    board_location="Eryndor",
    issuer="Halvar, wlasciciel magazynow",
    board_text=(
        "Od kilku nocy ktos wybija okna w moim domu i zostawia na murze czarne znaki. Nie chce skandalu ani plotek. "
        "Zaplace dobrze osobie, ktora znajdzie sprawce i zakonczy sprawe."
    ),
    description=(
        "Sprawczynia jest corka robotnika zabitego w przeciazonym magazynie Halvara. Oficjalne odszkodowanie wyplacono, "
        "ale inspektor bezpieczenstwa zostal przekupiony."
    ),
    objective="Ustal motyw atakow na dom Halvara i zdecyduj, ile kosztuje prawda o smierci robotnika.",
    length="Sredni",
    stages=[
        S(
            1,
            "Czarne znaki",
            "Uszkodzenia wygladaja groznie, ale sprawca zawsze wybiera godziny, gdy domownicy sa z dala od okien.",
            O(
                "q27_wzor",
                "Odczytaj schemat nocnych atakow",
                stat="Intryga",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="brak_zamiaru_zabojstwa", value=True)],
            ),
            O(
                "q27_sasiedzi",
                "Porozmawiaj z robotnikami mieszkajacymi obok",
                stat="Dyplomacja",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="imie_lery", value=True)],
            ),
            location="Eryndor",
        ),
        S(
            2,
            "Lera",
            "Lera nie chce pieniedzy za wybite okna. Chce, by Halvar publicznie przyznal, ze wiedzial o przeciazonym magazynie.",
            O(
                "q27_dowody",
                "Odnajdz dokumenty po dawnym przegladzie magazynu",
                stat="Intryga",
                threshold=13,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="dowod_lapowki", value=True)],
            ),
            O(
                "q27_odszkodowanie",
                "Sprawdz, ile Halvar faktycznie wyplacil rodzinie",
                stat="Handel",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="zaniżone_odszkodowanie", value=True)],
            ),
        ),
        S(
            3,
            "Ile kosztuje prawda",
            "Halvar rozumie, ze sprawa moze trafic przed cale Eryndor. Lera czeka na decyzje.",
            O(
                "q27_a",
                "Oddaj Lere strazy i przyjmij zaplate Halvara",
                stat="Dyplomacja",
                threshold=12,
                on_success="complete:lera_aresztowana",
            ),
            O(
                "q27_b",
                "Zmusc Halvara do publicznego przyznania sie",
                stat="Dyplomacja",
                threshold=14,
                on_success="complete:halvar_przyznal_sie",
            ),
            O(
                "q27_b_latwiej",
                "Pokaz dowod przekupienia inspektora",
                stat="Dyplomacja",
                threshold=12,
                visible_if={"flag": "dowod_lapowki", "equals": True},
                on_success="complete:halvar_przyznal_sie",
            ),
            O(
                "q27_c",
                "Wynegocjuj wysokie odszkodowanie w zamian za cisze",
                stat="Handel",
                threshold=14,
                on_success="complete:odszkodowanie_za_cisze",
            ),
            O(
                "q27_c_latwiej",
                "Oprzyj kwote na prawdziwej wartosci zaniżonego odszkodowania",
                stat="Handel",
                threshold=12,
                visible_if={"flag": "zaniżone_odszkodowanie", "equals": True},
                on_success="complete:odszkodowanie_za_cisze",
            ),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "lera_aresztowana": R(20, 1, random_items=[ri("ring", "rzadka"), ri("weapon", "zwykla")]),
        "halvar_przyznal_sie": R(8, 3, random_items=[ri("armor", "rzadka")], random_materials=[rm(3)]),
        "odszkodowanie_za_cisze": R(17, 2, random_items=[ri("amulet", "rzadka")], random_materials=[rm(2)]),
    },
)


Q28 = Q(
    28,
    "kamienie_pamietaja",
    "Kamienie pamietaja",
    board_location="Lirion",
    issuer="Rada Lirion",
    board_text=(
        "Podczas kopania fundamentow w nowej dzielnicy robotnicy odslonili rzad kamiennych tablic. Budowe wstrzymano, "
        "poniewaz czesc mieszkancow uwaza je za groby, a inni za stare znaki graniczne. Rada potrzebuje niezaleznej oceny."
    ),
    description=(
        "Tablice sa dawnymi znacznikami granicznymi sprzed powstania obecnej dzielnicy. Ich uznanie podwaza dzisiejsze "
        "prawa wlasnosci do kilku bardzo drogich parceli."
    ),
    objective="Ustal znaczenie kamieni i zdecyduj, czy starsze prawo ziemi ma pierwszenstwo przed wspolczesnymi dokumentami.",
    length="Sredni",
    stages=[
        S(
            1,
            "Rzad kamieni",
            "Tablice nie stoja jak nagrobki. Tworza linie, ktora przecina kilka dzisiejszych parceli.",
            O(
                "q28_badanie",
                "Zbadaj sposob obrobki i ustawienie tablic",
                stat="Nauka",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="stare_znaczniki", value=True)],
            ),
            O(
                "q28_symbole",
                "Rozpoznaj dawne symbole ziemskie",
                stat="Kultura",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="dawne_prawo", value=True)],
            ),
            location="Lirion",
        ),
        S(
            2,
            "Nazwisko pod miastem",
            "Stare rejestry wskazuja rod Veyr. Ich potomkowie nadal mieszkaja w Lirion, lecz od pokolen nie roscili praw do tej ziemi.",
            O(
                "q28_rejestry",
                "Porownaj kamienie z dawnymi rejestrami miasta",
                stat="Kultura",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="ciaglosc_praw", value=True)],
            ),
            O(
                "q28_wartosc",
                "Policz wartosc dzisiejszych parceli i mozliwe odszkodowanie",
                stat="Handel",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="wartosc_ugody", value=True)],
            ),
        ),
        S(
            3,
            "Dwie mapy Lirion",
            "Jedna mapa pokazuje obecne miasto. Druga, starsza, pokazuje granice rodu Veyr. Obie sa prawdziwe.",
            O(
                "q28_a",
                "Uznaj dawne prawo rodu Veyr",
                stat="Kultura",
                threshold=14,
                on_success="complete:stare_prawo_uznane",
            ),
            O(
                "q28_a_latwiej",
                "Udowodnij ciaglosc dawnych praw w rejestrach",
                stat="Kultura",
                threshold=12,
                visible_if={"flag": "ciaglosc_praw", "equals": True},
                on_success="complete:stare_prawo_uznane",
            ),
            O(
                "q28_b",
                "Uznaj wspolczesne dokumenty za nadrzedne",
                stat="Nauka",
                threshold=13,
                on_success="complete:nowe_prawo_utrzymane",
            ),
            O(
                "q28_c",
                "Wynegocjuj rekompensate bez zmiany obecnych granic",
                stat="Handel",
                threshold=14,
                on_success="complete:ugoda_graniczna",
            ),
            O(
                "q28_c_latwiej",
                "Oprzyj ugode na wyliczonej wartosci parceli",
                stat="Handel",
                threshold=12,
                visible_if={"flag": "wartosc_ugody", "equals": True},
                on_success="complete:ugoda_graniczna",
            ),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "stare_prawo_uznane": R(10, 3, random_items=[ri("amulet", "rzadka")], random_materials=[rm(3)]),
        "nowe_prawo_utrzymane": R(18, 1, random_items=[ri("armor", "rzadka")], random_materials=[rm(2)]),
        "ugoda_graniczna": R(13, 2, random_items=[ri("ring", "rzadka"), ri("armor", "zwykla")]),
    },
)


Q29 = Q(
    29,
    "wilk_przy_palenisku",
    "Wilk przy palenisku",
    board_location="Durnhal",
    issuer="Pasterze z okolic Durnhal",
    board_text=(
        "W poblizu Durnhal znaleziono kolejne martwe owce. Mieszkancy widzieli duzego wilka, ktory podchodzi pod domy i "
        "nie boi sie ognia. Zanim ktos zginie, potrzebujemy kogos, kto odnajdzie zwierze i zakonczy problem."
    ),
    description=(
        "Wilk byl oswojonym zwierzeciem zmarlego mysliwego. Czesc owiec padla jego ofiara, ale reszte kradnie czlowiek, "
        "ktory wykorzystuje strach przed drapieznikiem jako przykrywke."
    ),
    objective="Ustal, za ktore ataki odpowiada wilk, odnajdz prawdziwego zlodzieja i zdecyduj o losie zwierzecia.",
    length="Sredni",
    stages=[
        S(
            1,
            "Slady przy owczarni",
            "Nie wszystkie martwe owce maja takie same rany. Przy jednej z zagród widac rowniez slady butow.",
            O(
                "q29_rany",
                "Porownaj rany zwierzat",
                stat="Nauka",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="dwa_rodzaje_atakow", value=True)],
            ),
            O(
                "q29_trop",
                "Podejmij trop duzego wilka",
                stat="Walka",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="trop_wilka", value=True), fx("markers", count=1, payload={"label": "Stare palenisko mysliwego"})],
            ),
            location="Durnhal",
        ),
        S(
            2,
            "Obroza przy ogniu",
            "Wilk spi przy wygaslym palenisku i nosi stara obroze. Nie atakuje od razu. Niedaleko widac swieze slady czlowieka.",
            O(
                "q29_obroza",
                "Rozpoznaj zachowanie oswojonego zwierzecia",
                stat="Nauka",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="wilk_oswojony", value=True)],
            ),
            O(
                "q29_czlowiek",
                "Podaz za ludzkimi sladami zamiast za wilkiem",
                stat="Intryga",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="trop_zlodzieja", value=True)],
            ),
        ),
        S(
            3,
            "Dwa drapiezniki",
            "Zlodziejem jest pomocnik rzeznika Merek. Zabiera mieso, a reszte zostawia tak, by winny wygladal wilk.",
            O(
                "q29_a",
                "Zabij wilka i zakoncz panike",
                stat="Walka",
                threshold=14,
                on_success="complete:wilk_zabity",
            ),
            O(
                "q29_b",
                "Ujawnij Merka i oddaj wilka pod opieke mysliwego",
                stat="Intryga",
                threshold=13,
                on_success="complete:zlodziej_ujawniony",
            ),
            O(
                "q29_b_latwiej",
                "Przedstaw slad Merka znaleziony przy owczarni",
                stat="Intryga",
                threshold=11,
                visible_if={"flag": "trop_zlodzieja", "equals": True},
                on_success="complete:zlodziej_ujawniony",
            ),
            O(
                "q29_c",
                "Wykorzystaj wilka do schwytania Merka i zatrzymaj zwierze",
                stat="Intryga",
                threshold=14,
                on_success="complete:wilk_towarzysz",
            ),
            O(
                "q29_c_latwiej",
                "Podejdz do wilka jak do oswojonego zwierzecia",
                stat="Intryga",
                threshold=12,
                visible_if={"flag": "wilk_oswojony", "equals": True},
                on_success="complete:wilk_towarzysz",
            ),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "wilk_zabity": R(16, 1, random_items=[ri("weapon", "rzadka")], random_materials=[rm(2, rare=True)]),
        "zlodziej_ujawniony": R(12, 3, random_items=[ri("armor", "rzadka")], random_materials=[rm(3)]),
        "wilk_towarzysz": R(7, 3, random_items=[ri("ring", "rzadka")], helpers=[WILK_TOWARZYSZ]),
    },
)


Q30 = Q(
    30,
    "dom_bez_drzwi",
    "Dom bez drzwi",
    board_location="Elarin",
    issuer="Drwale z Elarin",
    board_text=(
        "W lesie znalezlismy niewielki kamienny dom bez drzwi i okien. Nikt nie potrafi wejsc do srodka, a jednak nocami "
        "slychac przesuwanie skrzyn i kroki. Nie chcemy dalej pracowac obok tego miejsca, dopoki ktos go nie zbada."
    ),
    description=(
        "Kamienny budynek jest magazynem przemytnikow. Wejscie prowadzi tunelem z innego miejsca, a czesc kontrabandy "
        "stanowia lekarstwa i zywnosc omijajace blokade handlowa lokalnego wlasciciela ziemskiego."
    ),
    objective="Znajdz wejscie do domu bez drzwi i zdecyduj, co zrobic z dzialajacym szlakiem przemytniczym.",
    length="Sredni",
    stages=[
        S(
            1,
            "Sciana bez wejscia",
            "Dom jest szczelny tylko z pozoru. Kamienie przy podstawie sa cieplejsze, a ziemia za budynkiem byla niedawno ruszana.",
            O(
                "q30_konstrukcja",
                "Zbadaj wentylacje i fundamenty",
                stat="Nauka",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="tunel_pod_domem", value=True), fx("markers", count=1, payload={"label": "Wejscie do tunelu"})],
            ),
            O(
                "q30_slady",
                "Szukaj sladow ludzi, ktorzy musza dostawac sie do srodka",
                stat="Intryga",
                threshold=12,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="trasa_przemytnikow", value=True), fx("markers", count=1, payload={"label": "Wejscie do tunelu"})],
            ),
            location="Elarin",
        ),
        S(
            2,
            "Pod ziemia",
            "Tunel prowadzi do magazynu pelnego kontrabandy. Obok drogich towarow leza worki zboza, opatrunki i lekarstwa.",
            O(
                "q30_ladunek",
                "Rozdziel towary luksusowe od zywnosci i lekarstw",
                stat="Handel",
                threshold=12,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="pomoc_dla_biednych", value=True)],
            ),
            O(
                "q30_ksiegi",
                "Odczytaj ksiegi dostaw i odbiorcow",
                stat="Intryga",
                threshold=13,
                on_success="stage:3",
                success_effects=[fx("set_flag", key="blokada_handlowa", value=True)],
            ),
        ),
        S(
            3,
            "Towar i potrzeba",
            "Przemytnicy zarabiaja na kontrabandzie, ale ten sam szlak utrzymuje przy zyciu ludzi odcietych od legalnego handlu.",
            O(
                "q30_a",
                "Wydaj caly magazyn i szlak wladzom",
                stat="Intryga",
                threshold=13,
                on_success="complete:magazyn_zlikwidowany",
            ),
            O(
                "q30_b",
                "Pozwol przemytnikom dzialac dalej bez zmian",
                stat="Handel",
                threshold=12,
                on_success="complete:przemytnicy_dzialaja",
            ),
            O(
                "q30_c",
                "Przejmij zasady szlaku: tylko zywnosc, lekarstwa i bezpieczne towary",
                stat="Handel",
                threshold=14,
                on_success="complete:ukryty_magazyn",
            ),
            O(
                "q30_c_latwiej",
                "Oprzyj nowe zasady na ksiegach odbiorcow i realnych potrzebach",
                stat="Handel",
                threshold=12,
                visible_if={"flag": "pomoc_dla_biednych", "equals": True},
                on_success="complete:ukryty_magazyn",
            ),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "magazyn_zlikwidowany": R(17, 1, random_items=[ri("weapon", "rzadka")], random_materials=[rm(3)]),
        "przemytnicy_dzialaja": R(10, 2, random_items=[ri("ring", "rzadka")], goods={"Wytrychy": 2}),
        "ukryty_magazyn": R(8, 3, random_items=[ri("amulet", "rzadka")], random_materials=[rm(3)]),
    },
)


QUESTS_24_30 = (Q24, Q25, Q26, Q27, Q28, Q29, Q30)
