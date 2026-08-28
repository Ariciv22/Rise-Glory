"""Finalne Questy 17-23."""

from __future__ import annotations

from rg_content.quest_pack_common import (
    KONTRAKT_DLUZNY,
    MINIATUROWY_WEDROWNY_DOM,
    O,
    Q,
    R,
    S,
    fx,
    ri,
    rm,
)


Q17 = Q(
    17,
    "miod_wiedzmy",
    "Miod wiedźmy",
    board_location="Elarin",
    issuer="Pszczelarz Radan",
    board_text=(
        "Od kilku tygodni moje ule daja czerwony miod o dziwnym zapachu i gorzkim posmaku. Pszczoly zaczely latac "
        "gleboko w las, w okolice, ktorych mieszkancy Elarin od dawna unikaja. Podejrzewam, ze ktos zatruwa moje pasieki."
    ),
    description="Czerwony miod nie jest klatwa, lecz skutkiem krwistego wrzosu uprawianego przez Mire.",
    objective="Ustal zrodlo czerwonego miodu i zdecyduj o losie Miry oraz pasieki.",
    length="Krotki",
    stages=[
        S(
            1,
            "Zaczarowane ule",
            "Pszczoly sa bardziej agresywne niz zwykle, a na ich odnozach widac czerwony pylek.",
            O(
                "q17_pylek",
                "Podejdz do uli mimo agresywnych pszczol",
                stat="Walka",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="trop_wrzosu", value=True), fx("markers", count=1, payload={"label": "Polana Miry"})],
            ),
            O(
                "q17_wartosc",
                "Ocen wartosc czerwonego miodu",
                stat="Handel",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="wartosc_miodu", value=True), fx("markers", count=1, payload={"label": "Polana Miry"})],
            ),
            location="Elarin",
        ),
        S(
            2,
            "Mira z lasu",
            "Mira uprawia rzadki krwisty wrzos. Nie zaczarowala uli; pszczoly same przylatuja po jego nektar.",
            O("q17_a", "Wypedz Mire i zniszcz wrzos", stat="Walka", threshold=13, on_success="complete:mira_wygnana"),
            O("q17_b", "Utworz wspolprace Radana i Miry", stat="Handel", threshold=14, on_success="complete:czerwony_miod"),
            O(
                "q17_b_latwiej",
                "Oprzyj umowe na prawdziwej wartosci miodu",
                stat="Handel",
                threshold=12,
                visible_if={"flag": "wartosc_miodu", "equals": True},
                on_success="complete:czerwony_miod",
            ),
            O("q17_c", "Wykorzystaj strach Radana i sprzedaj pasieke", stat="Handel", threshold=13, on_success="complete:pasieka_sprzedana"),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "mira_wygnana": R(14, 1, random_items=[ri("weapon", "rzadka")], random_materials=[rm(3)]),
        "czerwony_miod": R(9, 3, random_items=[ri("amulet", "rzadka")]),
        "pasieka_sprzedana": R(23, 1, random_items=[ri("ring", "rzadka"), ri("weapon", "zwykla")]),
    },
)


Q18 = Q(
    18,
    "trzy_filazanki",
    "Trzy filiżanki",
    board_location="Valdren",
    issuer="Olan, stary kupiec",
    board_text=(
        "Poszukuje osoby znajacej dawne prawa kupieckie. Dwadzieścia lat temu zawarlem umowe, ktora nigdy nie zostala "
        "w pelni rozliczona. Dzis syn drugiej strony ma przejezdzac traktem do Durnhal. Potrzebuje swiadka."
    ),
    description="Stary dług Olana moze zostac rozliczony wedlug dawnego zwyczaju Trzech Filizanek.",
    objective="Ustal, czy stary dług nadal obowiazuje, i zdecyduj, jak go rozliczyc.",
    length="Krotki",
    stages=[
        S(
            1,
            "Stol Trzech",
            "Olan ustawia trzy filiżanki: dla sprzedajacego, kupujacego i swiadka.",
            O("q18_zwyczaj", "Rozpoznaj dawny zwyczaj kupiecki", stat="Kultura", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="stol_trzech", value=True)]),
            O("q18_dlug", "Poznaj warunki starej umowy", stat="Handel", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="stary_dlug", value=True)]),
            location="Valdren",
        ),
        S(
            2,
            "Trzeci przy stole",
            "Darven, syn dawnego kupca, odmawia odpowiedzialnosci za dług ojca.",
            O("q18_a", "Potwierdz waznosc dawnego obyczaju", stat="Kultura", threshold=13, on_success="complete:stary_dlug_splacony"),
            O("q18_b", "Wynegocjuj nowy rachunek", stat="Handel", threshold=14, on_success="complete:nowa_umowa"),
            O("q18_c", "Wykup roszczenie Olana", stat="Handel", threshold=13, on_success="complete:roszczenie_bohatera"),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "stary_dlug_splacony": R(12, 3, random_items=[ri("ring", "rzadka")], random_materials=[rm(3)]),
        "nowa_umowa": R(15, 2, random_items=[ri("weapon", "zwykla"), ri("amulet", "zwykla")]),
        "roszczenie_bohatera": R(24, 1, random_items=[ri("amulet", "rzadka")], items=[KONTRAKT_DLUZNY]),
    },
)


Q19 = Q(
    19,
    "samotny_grob",
    "Samotny grob",
    board_location="Artium",
    issuer="Straznik traktu z Artium",
    board_text=(
        "Przy drodze odnaleziono samotny, swiezo wykopany grob. Na kamieniu widnieje nazwisko zyjacego podroznego oraz "
        "dzisiejsza data smierci. Wokol mogily pojawily sie czarne korzenie."
    ),
    description="Grob Oczekujacy nie przepowiada smierci; podziemny organizm wykorzystuje go jako przynete.",
    objective="Zbadaj czarne korzenie i zdecyduj, czy oszukac, odizolowac czy zniszczyc organizm.",
    length="Sredni",
    stages=[
        S(
            1,
            "Wlasne imie",
            "Na samotnym nagrobku pojawia sie imie bohatera albo jednego z jego Towarzyszy i dzisiejsza data.",
            O("q19_korzenie", "Zbadaj litery i korzenie", stat="Nauka", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="czarne_korzenie", value=True)]),
            O("q19_legenda", "Przypomnij sobie legendy o takich grobach", stat="Kultura", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="legenda_grobu", value=True)]),
            location="Artium",
        ),
        S(
            2,
            "Pod kamieniem",
            "Korzenie lacza nagrobek z czyms zyjacym gleboko pod ziemia.",
            O(
                "q19_organizm",
                "Zbadaj podziemny organizm",
                stat="Nauka",
                threshold=13,
                visible_if={"flag": "czarne_korzenie", "equals": True},
                on_success="stage:3",
                success_effects=[fx("set_flag", key="organizm_grobu", value=True)],
            ),
            O(
                "q19_rytual",
                "Odtworz rytual zmiany imienia",
                stat="Kultura",
                threshold=13,
                visible_if={"flag": "legenda_grobu", "equals": True},
                on_success="stage:3",
                success_effects=[fx("set_flag", key="rytual_imienia", value=True)],
            ),
        ),
        S(
            3,
            "Zanim zajdzie slonce",
            "Imie na kamieniu nie pozostanie obojetne na zawsze.",
            O("q19_a", "Zastap imie zywego imieniem zmarlego", stat="Kultura", threshold=14, on_success="complete:imie_skreslone"),
            O(
                "q19_a_latwiej",
                "Przeprowadz poznany rytual",
                stat="Kultura",
                threshold=12,
                visible_if={"flag": "rytual_imienia", "equals": True},
                on_success="complete:imie_skreslone",
            ),
            O("q19_b", "Odetnij organizm od powierzchni", stat="Nauka", threshold=14, on_success="complete:grob_unieszkodliwiony"),
            O(
                "q19_b_latwiej",
                "Odetnij poznana strukture korzeni",
                stat="Nauka",
                threshold=12,
                visible_if={"flag": "organizm_grobu", "equals": True},
                on_success="complete:grob_unieszkodliwiony",
            ),
            O(
                "q19_c",
                "Zejdz pod grob i zniszcz rdzen",
                stat="Walka",
                threshold=14,
                on_success="complete:rdzen_zniszczony",
                failure_effects=[fx("wound", amount=1)],
            ),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "imie_skreslone": R(10, 2, random_items=[ri("amulet", "rzadka")], random_materials=[rm(3)]),
        "grob_unieszkodliwiony": R(8, 3, random_items=[ri("ring", "rzadka")], materials={"Probka Czarnego Korzenia": 1}),
        "rdzen_zniszczony": R(16, 2, random_items=[ri("weapon", "rzadka"), ri("armor", "rzadka")]),
    },
)


Q20 = Q(
    20,
    "kamien_szczescia",
    "Kamien szczescia",
    board_location="Valdren",
    issuer="Kupcy z targu w Valdren",
    board_text=(
        "Na targu pojawil sie Beldo, ktory sprzedaje niewielkie kamienie majace zapewniac siedem dni szczescia. Wielu "
        "mieszkancow wydaje na nie oszczednosci. Kupcy prosza o sprawdzenie, czy talizmany rzeczywiscie dzialaja."
    ),
    description="Kamienie Belda sa zwykle, ale jego ustawione gry w kosci wykorzystuja prawdziwy stary zwyczaj Dnia Dobrego Losu.",
    objective="Ujawnij oszustwo, odnow zwyczaj albo dolacz do interesu Belda.",
    length="Krotki",
    stages=[
        S(
            1,
            "Szczescie za cztery monety",
            "Beldo sprzedaje kamienie i dba, by nowi klienci szybko zobaczyli pozorny dowod ich mocy.",
            O("q20_zwyczaj", "Zbadaj pochodzenie symbolu", stat="Kultura", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="prawdziwy_zwyczaj", value=True)]),
            O("q20_oszustwo", "Sprawdz pierwsze wygrane klientow", stat="Handel", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="mechanizm_oszustwa", value=True)]),
            location="Valdren",
        ),
        S(
            2,
            "Co sprzedac ludziom",
            "Mozna zniszczyc proceder, odnowic tradycje albo ulepszyc oszustwo.",
            O(
                "q20_a",
                "Publicznie ujawnij schemat Belda",
                stat="Handel",
                threshold=13,
                visible_if={"flag": "mechanizm_oszustwa", "equals": True},
                on_success="complete:oszustwo_ujawnione",
            ),
            O(
                "q20_b",
                "Przywroc Dzien Dobrego Losu",
                stat="Kultura",
                threshold=13,
                visible_if={"flag": "prawdziwy_zwyczaj", "equals": True},
                on_success="complete:dzien_dobrego_losu",
            ),
            O(
                "q20_b_latwiej",
                "Oddziel prawdziwy zwyczaj od oszustwa",
                stat="Kultura",
                threshold=11,
                visible_if={"flag": "mechanizm_oszustwa", "equals": True},
                on_success="complete:dzien_dobrego_losu",
            ),
            O("q20_c", "Dolacz do Belda i ulepsz system", stat="Handel", threshold=14, on_success="complete:wspolnik_belda"),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "oszustwo_ujawnione": R(12, 2, random_items=[ri("ring", "zwykla")], random_materials=[rm(3)]),
        "dzien_dobrego_losu": R(8, 3, random_items=[ri("amulet", "rzadka")]),
        "wspolnik_belda": R(24, 1, random_items=[ri("ring", "rzadka")], goods={"Wytrychy": 2}),
    },
)


Q21_ACCEPT_TEXT = (
    "Teren podchodzi do ciebie zaraz po przyjeciu zlecenia. 'To ty wziales moje ogloszenie? Dobrze. Jest cos, czego "
    "na nim nie napisalem. Kiedy moj woz sie przewrocil, widzialem kruka. Zwykle ptaki zabieraja blyskotki, jesli "
    "nadarzy sie okazja. Ten ich szukal. Rozrzucal rzeczy dziobem, atakowal mnie, gdy probowalem go odpedzic, i "
    "wybieral tylko zloto oraz kamienie. Widziałem, jak porwal jeden z pierscieni i odlecial w strone lasu. Jesli "
    "znajdziemy tego ptaka, byc moze znajdziemy tez reszte mojego ladunku.'"
)

Q21 = Q(
    21,
    "kruk_z_pierscieniem",
    "Kruk z pierscieniem",
    board_location="Eryndor",
    issuer="Jubiler Teren",
    board_text=(
        "Jubiler Teren prosi o pomoc w odzyskaniu kosztownosci po wypadku wozu. Czesc ladunku zaginela, a kilka "
        "przedmiotow moglo zostac zabranych z miejsca zdarzenia."
    ),
    accept_text=Q21_ACCEPT_TEXT,
    description="Nietypowo agresywny kruk prowadzi do rozsypanego ladunku jubilera Terena.",
    objective="Podazaj tropem kruka, odtworz manifest i zdecyduj, ile odzyskanego ladunku zwrocic.",
    length="Krotki",
    stages=[
        S(
            1,
            "Sladem kruka",
            "Teren wskazuje kierunek, w ktory odlecial kruk z pierscieniem.",
            O(
                "q21_pierscien",
                "Ocen porwany pierscien i znak gildii",
                stat="Handel",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="znak_jubilera", value=True), fx("markers", count=1, payload={"label": "Slad kruka"})],
            ),
            O(
                "q21_kruk",
                "Podazaj za krukiem",
                option_type="automatic",
                on_success="stage:2",
                success_effects=[fx("markers", count=1, payload={"label": "Przewrocony woz Terena"})],
            ),
            location="Eryndor",
        ),
        S(
            2,
            "Rozrzucony ladunek",
            "Przy przewroconym wozie leza rzeczy Terena i kosztownosci powierzone mu przez klientow.",
            O("q21_manifest", "Sprawdz manifest i wlascicieli", stat="Handel", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="manifest_terena", value=True)]),
            O("q21_zbierz", "Zbierz rozsypane kosztownosci", option_type="automatic", on_success="stage:3"),
        ),
        S(
            3,
            "Prawo do znaleziska",
            "Towar jest odzyskany, ale nie wszystko Teren potrafi natychmiast przypisac do konkretnego klienta.",
            O("q21_a", "Zwroc calosc Terenowi", option_type="choice", on_success="complete:uczciwy_zwrot"),
            O("q21_b", "Wynegocjuj legalna prowizje", stat="Handel", threshold=13, on_success="complete:prowizja"),
            O("q21_c", "Zatrzymaj najcenniejszy niepoliczony element", stat="Handel", threshold=14, on_success="complete:czesc_zatrzymana"),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "uczciwy_zwrot": R(13, 3, random_items=[ri("ring", "rzadka")], random_materials=[rm(3)]),
        "prowizja": R(18, 2, random_items=[ri("amulet", "rzadka"), ri("weapon", "zwykla")]),
        "czesc_zatrzymana": R(21, 1, random_items=[ri("ring", "rzadka"), ri("armor", "rzadka")]),
    },
)


Q22 = Q(
    22,
    "porzucony_namiot",
    "Porzucony namiot",
    board_location="Thalwen",
    issuer="Straz Thalwen",
    board_text=(
        "Kilku podroznych zaginelo na lesnym trakcie prowadzacym do Thalwen. Przy drodze odnaleziono opuszczony namiot, "
        "swieze jedzenie i wygaszone ognisko, ale nie znaleziono cial ani sladow walki."
    ),
    description="Porzucony oboz jest przyneta bandytow wykorzystujacych usypiajaca zywice.",
    objective="Zbadaj oboz, znajdz kryjowke i zdecyduj o losie wiezniow oraz bandy.",
    length="Sredni",
    stages=[
        S(
            1,
            "Ciepla kolacja",
            "Jedzenie jest podejrzanie swieze jak na opuszczony oboz.",
            O(
                "q22_dym",
                "Zbadaj jedzenie i dym",
                stat="Nauka",
                threshold=11,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="usypiajacy_dym", value=True), fx("markers", count=1, payload={"label": "Lesna kryjowka"})],
            ),
            O(
                "q22_slady",
                "Zbadaj slady wokol namiotu",
                stat="Intryga",
                threshold=12,
                on_success="stage:2",
                success_effects=[fx("set_flag", key="oboz_przyneta", value=True), fx("markers", count=1, payload={"label": "Lesna kryjowka"})],
            ),
            location="Thalwen",
        ),
        S(
            2,
            "Lowcy podroznych",
            "W kryjowce bandytow nadal zyje trzech wiezniow.",
            O("q22_a", "Zneutralizuj opary i uwolnij jencow", stat="Nauka", threshold=13, on_success="complete:jency_uratowani"),
            O(
                "q22_a_latwiej",
                "Uzyj wiedzy o usypiajacej zywicy",
                stat="Nauka",
                threshold=11,
                visible_if={"flag": "usypiajacy_dym", "equals": True},
                on_success="complete:jency_uratowani",
            ),
            O("q22_b", "Udawaj nieprzytomnego i odwroc zasadzke", stat="Intryga", threshold=14, on_success="complete:banda_schwytana"),
            O(
                "q22_b_latwiej",
                "Wykorzystaj wiedze, ze oboz jest przyneta",
                stat="Intryga",
                threshold=12,
                visible_if={"flag": "oboz_przyneta", "equals": True},
                on_success="complete:banda_schwytana",
            ),
            O("q22_c", "Zawrzyj uklad z banda", stat="Intryga", threshold=13, on_success="complete:uklad_z_banda"),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "jency_uratowani": R(10, 3, random_items=[ri("amulet", "rzadka")], random_materials=[rm(3)]),
        "banda_schwytana": R(15, 2, random_items=[ri("weapon", "rzadka"), ri("armor", "zwykla")], goods={"Wytrychy": 2}),
        "uklad_z_banda": R(25, 1, random_items=[ri("ring", "rzadka"), ri("armor", "rzadka")]),
    },
)


Q23 = Q(
    23,
    "wedrowny_dom",
    "Wedrowny dom",
    board_location="Norven",
    issuer="Podrozni z traktu",
    board_text=(
        "Od kilku dni pomiedzy Norven a Durnhal widywany jest drewniany dom poruszajacy sie samodzielnie przez las. "
        "Konstrukcja chodzi na czterech mechanicznych nogach i zdaje sie krazyc po tej samej trasie."
    ),
    description="Mobilna pracownia Mervena nadal wykonuje ostatni program zmarlego konstruktora.",
    objective="Zrozum mechanizm Wedrownego Domu i zdecyduj, czy go zatrzymac, naprawic czy przeprogramowac.",
    length="Sredni",
    stages=[
        S(
            1,
            "Chatka na nogach",
            "Dom porusza sie regularnie pomiedzy starymi znacznikami trasy.",
            O("q23_maszyna", "Zbadaj mechaniczne nogi", stat="Nauka", threshold=11, on_success="stage:2", success_effects=[fx("set_flag", key="to_maszyna", value=True)]),
            O("q23_znacznik", "Zbadaj trase domu", stat="Nauka", threshold=12, on_success="stage:2", success_effects=[fx("set_flag", key="uszkodzony_znacznik", value=True), fx("markers", count=1, payload={"label": "Przewrocony znacznik Mervena"})]),
            location="Norven",
        ),
        S(
            2,
            "Pracownia Mervena",
            "W pustym domu sa notatki konstruktora, przekladnie, przeciwwagi i alchemiczny rdzen cieplny.",
            O("q23_sterowanie", "Zrozum uklad sterowania", stat="Nauka", threshold=13, on_success="stage:3", success_effects=[fx("set_flag", key="sterowanie_mervena", value=True)]),
            O("q23_naped", "Zbadaj rdzen i przeciwwagi", stat="Nauka", threshold=12, on_success="stage:3", success_effects=[fx("set_flag", key="naped_mervena", value=True)]),
        ),
        S(
            3,
            "Nowa droga",
            "Mechanizm mozna zatrzymac, przywrocic do starego programu albo nauczyc nowej trasy.",
            O("q23_a", "Bezpiecznie odlacz glowna przekladnie", stat="Nauka", threshold=12, on_success="complete:dom_zatrzymany"),
            O("q23_b", "Przywroc oryginalna trase", stat="Nauka", threshold=14, on_success="complete:trasa_naprawiona"),
            O(
                "q23_b_latwiej",
                "Napraw trase po odnalezieniu uszkodzonego znacznika",
                stat="Nauka",
                threshold=12,
                visible_if={"flag": "uszkodzony_znacznik", "equals": True},
                on_success="complete:trasa_naprawiona",
            ),
            O("q23_c", "Przeprogramuj Wedrowny Dom", stat="Nauka", threshold=15, on_success="complete:dom_przeprogramowany"),
            O(
                "q23_c_latwiej",
                "Przeprogramuj poznany uklad sterowania",
                stat="Nauka",
                threshold=13,
                visible_if={"flag": "sterowanie_mervena", "equals": True},
                on_success="complete:dom_przeprogramowany",
            ),
            point_of_no_return=True,
        ),
    ],
    ending_rewards={
        "dom_zatrzymany": R(14, 2, random_materials=[rm(5)], random_items=[ri("weapon", "zwykla")]),
        "trasa_naprawiona": R(9, 3, random_items=[ri("amulet", "rzadka")]),
        "dom_przeprogramowany": R(18, 2, items=[MINIATUROWY_WEDROWNY_DOM]),
    },
)


QUESTS_17_23 = (Q17, Q18, Q19, Q20, Q21, Q22, Q23)
