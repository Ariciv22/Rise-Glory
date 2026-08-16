from __future__ import annotations

from rg_engine.models import QuestDefinition, QuestExpansionDefinition, QuestOption, QuestStage
from rg_engine.quests import register_quest, register_quest_expansion

SATANIC_FORCES_ID = "klatwa_katakumb_0"
SATANIC_FORCES_NUMBER = 1

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

_REGISTERED = False


def register_all_quests() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    register_quest(SATANIC_FORCES)
    for expansion in SATANIC_FORCES_EXPANSIONS:
        register_quest_expansion(expansion)
    _REGISTERED = True
