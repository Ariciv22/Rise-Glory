from __future__ import annotations

from rg_engine.models import QuestDefinition, QuestExpansionDefinition, QuestOption, QuestStage
from rg_engine.quests import register_quest, register_quest_expansion

SATANIC_FORCES_ID = "klatwa_katakumb_0"
SPOR_O_STUDNIE_ID = "spor_o_studnie"
ZATRUTY_STRUMIEN_ID = "zatruty_strumien"
BRAKUJACY_LADUNEK_ID = "brakujacy_ladunek"

SATANIC_FORCES_NUMBER = 1
SPOR_O_STUDNIE_NUMBER = 13
ZATRUTY_STRUMIEN_NUMBER = 14
BRAKUJACY_LADUNEK_NUMBER = 15

SATANIC_FORCES = QuestDefinition(
    quest_id=SATANIC_FORCES_ID,
    quest_number=SATANIC_FORCES_NUMBER,
    name="Szatańskie siły",
    deck="Questy",
    description=(
        "Po przybyciu do Zamku Artium strażnicy wskazują ogłoszenie dotyczące "
        "dziwnych świateł, szeptów i klątwy w kaplicy oraz katakumbach."
    ),
    board_text="Śmiałek, który odegna światła i inne dziwy, hojnie zostanie wynagrodzony.",
    objective="Dotrzyj do Zamku Artium i zbadaj katakumby.",
    required_location="Artium",
    world_level_min=1,
    world_level=1,
    length="Średni",
    reward_hint="Złoto, Punkty Legendy i możliwy przedmiot.",
    image="uczony w katakumbach",
    unique=True,
    shared=False,
    stages=(
        QuestStage(
            number=1,
            title="Ołtarz w katakumbach",
            text=(
                "Lampa oświetla zawiłe korytarze. Po długiej wędrówce odnajdujesz "
                "ołtarz pokryty czerwonymi runami. Wybierz sposób zbadania miejsca."
            ),
            required_location="Artium",
            options=(
                QuestOption(
                    option_id="klatwa_katakumb_1_nauka",
                    label="Przeszukaj bezpiecznie biblioteki",
                    stat="Nauka",
                    threshold=11,
                    success_effects=(
                        {"type": "set_flag", "key": "znaleziono_notatki", "value": True},
                        {"type": "expansion", "id": "1A"},
                    ),
                ),
                QuestOption(
                    option_id="klatwa_katakumb_1_intryga",
                    label="Dotknij i prześledź czerwone znaki",
                    stat="Intryga",
                    threshold=14,
                    success_effects=(
                        {"type": "set_flag", "key": "poznano_runy", "value": True},
                        {"type": "expansion", "id": "1A"},
                    ),
                ),
                QuestOption(
                    option_id="klatwa_katakumb_1_kultura",
                    label="Wykonaj podstawowy obrzęd",
                    stat="Kultura",
                    threshold=13,
                    consumes={"materials": {"Skóra": 2}},
                    success_effects=(
                        {"type": "set_flag", "key": "wykonano_obrzed", "value": True},
                        {"type": "expansion", "id": "1A"},
                    ),
                ),
            ),
        ),
        QuestStage(
            number=2,
            title="Ślady dawnego kultu",
            text=(
                "W pradawnej bibliotece odkrywasz ślady starego kultu i rytualnych "
                "mordów. Musisz rozproszyć pozostałą w tym miejscu magię."
            ),
            required_location="Artium",
            options=(
                QuestOption(
                    option_id="klatwa_katakumb_2_nauka",
                    label="Wypowiedz słowa rozdziału o końcu rytuału",
                    stat="Nauka",
                    threshold=13,
                    success_effects=(
                        {"type": "quest_item", "item": "Formuła zakończenia rytuału"},
                        {"type": "expansion", "id": "1B"},
                    ),
                ),
                QuestOption(
                    option_id="klatwa_katakumb_2_intryga",
                    label="Zabierz księgę i ukryj prawdę przed kapitanem",
                    stat="Intryga",
                    threshold=15,
                    success_effects=(
                        {"type": "quest_item", "item": "Księga kultu"},
                        {"type": "set_flag", "key": "ukryto_prawde", "value": True},
                        {"type": "expansion", "id": "1B"},
                    ),
                ),
                QuestOption(
                    option_id="klatwa_katakumb_2_kultura",
                    label="Przeczytaj rozdział o mocach nadprzyrodzonych",
                    stat="Kultura",
                    threshold=14,
                    success_effects=(
                        {"type": "quest_item", "item": "Wiedza o klątwie"},
                        {"type": "expansion", "id": "1B"},
                    ),
                ),
            ),
        ),
        QuestStage(
            number=3,
            title="Koniec rytuału",
            text=(
                "Litery odrywają się od kart księgi. Z cienia wyłania się Przeklęty "
                "żołnierz, ostatni strażnik dawnego kultu."
            ),
            required_location="Artium",
            point_of_no_return=True,
            options=(
                QuestOption(
                    option_id="klatwa_katakumb_3_nauka",
                    label="Zniszcz księgę na dziedzińcu",
                    stat="Nauka",
                    threshold=10,
                    on_success="complete:klatwa_zlamana",
                    on_failure="combat:przeklety_zolnierz",
                    failure_enemy_id="przeklety_zolnierz",
                ),
                QuestOption(
                    option_id="klatwa_katakumb_3_intryga",
                    label="Przekonaj kapitana, że księga przepadła",
                    stat="Intryga",
                    threshold=13,
                    on_success="complete:prawda_ukryta",
                    on_failure="combat:przeklety_zolnierz",
                    failure_enemy_id="przeklety_zolnierz",
                ),
                QuestOption(
                    option_id="klatwa_katakumb_3_walka",
                    label="Stań do walki z Przeklętym żołnierzem",
                    option_type="combat",
                    enemy_id="przeklety_zolnierz",
                    on_success="complete:straznik_pokonany",
                    combat_defeat="quest_failure",
                    text="Z ołtarza podnosi się Przeklęty żołnierz. Ucieczka jest niemożliwa.",
                ),
            ),
        ),
    ),
    reward={
        "gold": 8,
        "legend": 2,
        "items": ["Krótki miecz"],
        "food": {"Suszone mieso": 3},
    },
)

SPOR_O_STUDNIE = QuestDefinition(
    quest_id=SPOR_O_STUDNIE_ID,
    quest_number=SPOR_O_STUDNIE_NUMBER,
    name="Spór o studnie",
    deck="Questy",
    description="Dwie rodziny z pobliskiej wsi oskarżają się o odebranie dostępu do wspólnej studni.",
    board_text="We wsi narasta spór o wodę. Ktoś musi rozstrzygnąć go, zanim poleje się krew.",
    objective="Udaj się do Wsi 1 i rozwiąż spór o studnię.",
    required_location="Wies 1",
    world_level_min=1,
    world_level=1,
    length="Krótki",
    reward_hint="Złoto lub Punkty Legendy, zależnie od sposobu rozwiązania.",
    unique=False,
    stages=(
        QuestStage(
            number=1,
            title="Dwie rodziny, jedna studnia",
            text="Obie rodziny zebrały się przy studni. Każda przedstawia własną wersję wydarzeń.",
            required_location="Wies 1",
            options=(
                QuestOption(
                    option_id="studnia_dyplomacja",
                    label="Doprowadź rodziny do ugody",
                    stat="Dyplomacja",
                    threshold=11,
                    on_success="complete:rodziny_zawarly_pokoj",
                    success_paragraph="130A",
                    failure_paragraph="130Z",
                    success_effects=(
                        {"type": "expansion", "id": "13A"},
                        {"type": "set_flag", "key": "rodziny_pogodzone", "value": True, "scope": "player"},
                    ),
                ),
                QuestOption(
                    option_id="studnia_intryga",
                    label="Wskaż winnego i wymuś ustępstwo",
                    stat="Intryga",
                    threshold=12,
                    on_success="complete:spor_zakonczony_przymusem",
                    success_paragraph="131A",
                    failure_paragraph="131Z",
                    success_effects=(
                        {"type": "expansion", "id": "13A"},
                        {"type": "set_flag", "key": "spor_studnia_przymus", "value": True, "scope": "player"},
                    ),
                ),
            ),
        ),
    ),
    reward={"gold": 5, "legend": 1},
)

ZATRUTY_STRUMIEN = QuestDefinition(
    quest_id=ZATRUTY_STRUMIEN_ID,
    quest_number=ZATRUTY_STRUMIEN_NUMBER,
    name="Zatruty strumień",
    deck="Questy",
    description="Mieszkańcy Lirion podejrzewają, że ktoś celowo zatruwa wodę dopływającą do miasta.",
    board_text="Woda ma metaliczny posmak, a nocami nad strumieniem widziano zakapturzoną postać.",
    objective="Rozpocznij śledztwo w Lirion.",
    required_location="",
    world_level_min=1,
    world_level=1,
    length="Krótki",
    reward_hint="Złoto, Legenda i możliwa zmiana sytuacji w mieście.",
    unique=False,
    stages=(
        QuestStage(
            number=1,
            title="Pierwsze ślady",
            text="Próbki wody i zeznania mieszkańców wskazują, że trucizna trafia do strumienia poza murami.",
            required_location="Lirion",
            options=(
                QuestOption(
                    option_id="strumien_nauka",
                    label="Zbadaj osad w wodzie",
                    stat="Nauka",
                    threshold=11,
                    on_success="stage:2",
                    success_effects=(
                        {"type": "expansion", "id": "14A"},
                        {
                            "type": "markers",
                            "count": 1,
                            "placement": {"type": "random_passable"},
                            "payload": {
                                "action_label": "Zbadaj źródło trucizny",
                                "description": "Ślady prowadzą do miejsca poza murami, gdzie trucizna trafia do wody.",
                            },
                        },
                    ),
                ),
                QuestOption(
                    option_id="strumien_intryga",
                    label="Wypytaj ludzi, którzy kręcą się nocą przy wodzie",
                    stat="Intryga",
                    threshold=12,
                    on_success="stage:2",
                    success_effects=(
                        {"type": "expansion", "id": "14A"},
                        {
                            "type": "markers",
                            "count": 1,
                            "placement": {"type": "random_passable"},
                            "payload": {
                                "action_label": "Śledź podejrzanego",
                                "description": "Świadek wskazuje miejsce, w którym nocą widziano podejrzanego.",
                            },
                        },
                    ),
                ),
            ),
        ),
        QuestStage(
            number=2,
            title="Źródło zatrucia",
            text="Na miejscu odnajdujesz ślady celowego skażania strumienia. Teraz trzeba przerwać proceder.",
            required_location=None,
            options=(
                QuestOption(
                    option_id="strumien_zatrzymaj",
                    label="Zdemaskuj i zatrzymaj truciciela",
                    stat="Intryga",
                    threshold=13,
                    on_success="complete:truciciel_zdemaskowany",
                    success_effects=(
                        {"type": "resolve_marker"},
                        {"type": "set_flag", "key": "truciciel_zdemaskowany", "value": True, "scope": "player"},
                    ),
                ),
                QuestOption(
                    option_id="strumien_przekup",
                    label="Zapłać za nazwisko zleceniodawcy",
                    option_type="payment",
                    consumes={"gold": 5},
                    on_success="complete:poznano_zleceniodawce",
                    success_effects=(
                        {"type": "resolve_marker"},
                        {"type": "set_flag", "key": "poznano_zleceniodawce", "value": True, "scope": "player"},
                    ),
                ),
            ),
        ),
    ),
    reward={"gold": 6, "legend": 1},
)

BRAKUJACY_LADUNEK = QuestDefinition(
    quest_id=BRAKUJACY_LADUNEK_ID,
    quest_number=BRAKUJACY_LADUNEK_NUMBER,
    name="Brakujący ładunek",
    deck="Questy",
    description="Kupiec w Lirion nie otrzymał transportu i prosi o szybkie uzupełnienie braków.",
    board_text="Kilka pustych skrzyń na straganie mówi więcej niż skargi kupca.",
    objective="Pomóż kupcowi w Lirion odzyskać lub zastąpić brakujący ładunek.",
    required_location="Lirion",
    world_level_min=1,
    world_level=1,
    length="Krótki",
    reward_hint="Złoto i możliwa przychylność kupców.",
    unique=False,
    stages=(
        QuestStage(
            number=1,
            title="Puste skrzynie",
            text="Kupiec może czekać na śledztwo albo natychmiast kupić towary zastępcze.",
            required_location="Lirion",
            options=(
                QuestOption(
                    option_id="ladunek_handel",
                    label="Znajdź tańszy transport zastępczy",
                    stat="Handel",
                    threshold=11,
                    on_success="complete:transport_zastepczy",
                    success_effects=(
                        {"type": "expansion", "id": "15A"},
                        {"type": "set_flag", "key": "kupcy_lirion_przychylni", "value": True, "scope": "player"},
                    ),
                ),
                QuestOption(
                    option_id="ladunek_zaplata",
                    label="Dołóż z własnej sakwy do pilnego zakupu",
                    option_type="payment",
                    consumes={"gold": 4},
                    on_success="complete:ladunek_odkupiony",
                    success_effects=(
                        {"type": "expansion", "id": "15A"},
                        {"type": "set_flag", "key": "kupcy_lirion_przychylni", "value": True, "scope": "player"},
                    ),
                ),
            ),
        ),
    ),
    reward={"gold": 6, "legend": 1},
)

SATANIC_FORCES_EXPANSIONS = (
    QuestExpansionDefinition(
        expansion_id="1A",
        quest_id=SATANIC_FORCES_ID,
        title="Ślady dawnego kultu",
        text=(
            "Odkryte ślady prowadzą głębiej pod kaplicę. Między regałami i kamiennymi "
            "niszami zachowały się zapiski ludzi, którzy próbowali zakończyć rytuał."
        ),
        image="ślady dawnego kultu",
    ),
    QuestExpansionDefinition(
        expansion_id="1B",
        quest_id=SATANIC_FORCES_ID,
        title="Ostatni strażnik",
        text=(
            "Wiedza zdobyta w katakumbach prowadzi do finału. Zanim klątwa zgaśnie, "
            "bohater musi zmierzyć się z ostatnią wolą dawnego kultu."
        ),
        image="przeklęty żołnierz w katakumbach",
    ),
)

TEST_EXPANSIONS = (
    QuestExpansionDefinition(
        expansion_id="13A",
        quest_id=SPOR_O_STUDNIE_ID,
        title="Rozstrzygnięcie sporu",
        text="Spór o wodę dobiegł końca. Sposób rozwiązania zostanie zapamiętany przez obie rodziny.",
    ),
    QuestExpansionDefinition(
        expansion_id="14A",
        quest_id=ZATRUTY_STRUMIEN_ID,
        title="Ślad poza murami",
        text="Pierwszy etap śledztwa prowadzi do konkretnego punktu na mapie oznaczonego numerem 14.",
    ),
    QuestExpansionDefinition(
        expansion_id="15A",
        quest_id=BRAKUJACY_LADUNEK_ID,
        title="Kupiec znowu handluje",
        text="Stragan ponownie zapełnia się towarem, a kupiec zapamiętuje, kto pomógł mu w kryzysie.",
    ),
)

QUESTS = (
    SATANIC_FORCES,
    SPOR_O_STUDNIE,
    ZATRUTY_STRUMIEN,
    BRAKUJACY_LADUNEK,
)

EXPANSIONS = (*SATANIC_FORCES_EXPANSIONS, *TEST_EXPANSIONS)

_REGISTERED = False


def register_all_quests() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    for quest in QUESTS:
        register_quest(quest)
    for expansion in EXPANSIONS:
        register_quest_expansion(expansion)
    _REGISTERED = True
