from __future__ import annotations

from rg_engine.models import QuestDefinition, QuestOption, QuestStage
from rg_engine.quests import register_quest

SATANIC_FORCES_ID = "klatwa_katakumb_0"

SATANIC_FORCES = QuestDefinition(
    quest_id=SATANIC_FORCES_ID,
    name="Szatańskie siły",
    deck="Nauki",
    description=(
        "Po przybyciu do Zamku Artium strażnicy wskazują ogłoszenie dotyczące "
        "dziwnych świateł, szeptów i klątwy w kaplicy oraz katakumbach."
    ),
    board_text="Śmiałek, który odegna światła i inne dziwy, hojnie zostanie wynagrodzony.",
    objective="Dotrzyj do Zamku Artium i zbadaj katakumby.",
    required_location="Artium",
    world_level_min=1,
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
                ),
                QuestOption(
                    option_id="klatwa_katakumb_1_intryga",
                    label="Dotknij i prześledź czerwone znaki",
                    stat="Intryga",
                    threshold=14,
                ),
                QuestOption(
                    option_id="klatwa_katakumb_1_kultura",
                    label="Wykonaj podstawowy obrzęd",
                    stat="Kultura",
                    threshold=13,
                    materials={"Skóra": 2},
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
                ),
                QuestOption(
                    option_id="klatwa_katakumb_2_intryga",
                    label="Zabierz księgę i ukryj prawdę przed kapitanem",
                    stat="Intryga",
                    threshold=15,
                ),
                QuestOption(
                    option_id="klatwa_katakumb_2_kultura",
                    label="Przeczytaj rozdział o mocach nadprzyrodzonych",
                    stat="Kultura",
                    threshold=14,
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
            options=(
                QuestOption(
                    option_id="klatwa_katakumb_3_nauka",
                    label="Zniszcz księgę na dziedzińcu",
                    stat="Nauka",
                    threshold=10,
                    on_success="complete",
                    on_failure="combat",
                    failure_enemy_id="przeklety_zolnierz",
                ),
                QuestOption(
                    option_id="klatwa_katakumb_3_intryga",
                    label="Przekonaj kapitana, że księga przepadła",
                    stat="Intryga",
                    threshold=13,
                    on_success="complete",
                    on_failure="combat",
                    failure_enemy_id="przeklety_zolnierz",
                ),
                QuestOption(
                    option_id="klatwa_katakumb_3_walka",
                    label="Stań do walki z Przeklętym żołnierzem",
                    option_type="combat",
                    enemy_id="przeklety_zolnierz",
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

_REGISTERED = False


def register_all_quests() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    register_quest(SATANIC_FORCES)
    _REGISTERED = True
