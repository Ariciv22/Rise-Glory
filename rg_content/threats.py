from __future__ import annotations

from rg_engine.world_events import DURATION_UNTIL_RESOLVED, register_world_event

ROZBOJNICY_ID = "rozbojnicy_na_trakcie"
LAWINY_ID = "lawiny_w_gorach"
CHOROBA_DRZEW_ID = "choroba_wsrod_drzew"
ZAWALONE_PRZEJSCIA_ID = "zawalone_przejscia_na_wzgorzach"

THREATS = (
    {
        "id": ROZBOJNICY_ID,
        "name": "Rozbójnicy na trakcie",
        "world_level": 1,
        "duration": DURATION_UNTIL_RESOLVED,
        "description": "Banda rozbójników rozbiła obóz przy uczęszczanym trakcie i wymusza haracz od podróżnych.",
        "effect_text": "Dopóki obóz działa, zakupy i zatrudnianie Pomocników kosztują +1 Złota.",
        "problem": {
            "description": "Rozbójnicy kontrolują trakt, zatrzymują wozy i terroryzują kupców.",
            "condition": "Rozbij, przechytrz albo przepędź bandę.",
            "action_label": "Zajmij się rozbójnikami",
            "marker_count": 1,
            "placement": {"type": "terrain", "terrain": "plains"},
            "fallback": {"type": "random_passable"},
            "effects": [
                {"type": "modifier", "name": "market_price_modifier", "amount": 1, "scope": "global"},
            ],
            "reward": {"gold": 4, "legend": 1},
            "methods": [
                {
                    "id": "walka",
                    "label": "Zaatakuj obóz rozbójników",
                    "mode": "combat",
                    "enemy": {
                        "name": "Przywódca rozbójników",
                        "max_hp": 6,
                        "hp": 6,
                        "armor_class": 12,
                        "attack_bonus": 2,
                        "wounds": 1,
                        "can_escape": True,
                        "image": "rozbojnik",
                    },
                    "success_text": "Obóz zostaje rozbity, a trakt ponownie jest bezpieczny.",
                    "failure_text": "Banda odpiera atak i zmusza bohatera do odwrotu.",
                },
                {
                    "id": "podstep",
                    "label": "Wkradnij się do obozu i skłóć bandę",
                    "mode": "test",
                    "stat": "Intryga",
                    "difficulty": 12,
                    "success_text": "Rozbójnicy zaczynają walczyć między sobą i porzucają obóz.",
                    "failure_text": "Podstęp zostaje odkryty; ucieczka kosztuje cię sakiewkę.",
                    "failure": {"gold": 2},
                },
                {
                    "id": "ugodowo",
                    "label": "Przekonaj bandę, że trakt jest zbyt gorący",
                    "mode": "test",
                    "stat": "Dyplomacja",
                    "difficulty": 13,
                    "costs": {"gold": 3},
                    "success_text": "Rozbójnicy biorą zapłatę i znikają z okolicy.",
                    "failure_text": "Banda bierze pieniądze, ale nigdzie się nie rusza.",
                    "failure": {"actions": 1},
                },
            ],
        },
    },
    {
        "id": LAWINY_ID,
        "name": "Lawiny w górach",
        "world_level": 1,
        "duration": DURATION_UNTIL_RESOLVED,
        "description": "Potężne lawiny zasypały kilka górskich szlaków.",
        "effect_text": "Pięć oznaczonych heksów Gór jest zablokowanych. Każdy oczyszczony punkt natychmiast otwiera się dla wszystkich bohaterów.",
        "problem": {
            "description": "Kamienie, śnieg i połamane drzewa zasypały przejścia przez góry.",
            "condition": "Oczyść wszystkie pięć oznaczonych przejść.",
            "action_label": "Oczyść górski szlak",
            "marker_count": 5,
            "placement": {"type": "terrain", "terrain": "mountain"},
            "effects": [
                {"type": "block_entry", "scope": "marker_tiles"},
            ],
            "reward_mode": "contributors",
            "reward": {},
            "deferred_reward": "Do następnej Rady każdy Szlak Handlowy przechodzący przez góry daje +2 Złota; integracja nastąpi w module Szlaków Handlowych.",
            "methods": [
                {
                    "id": "smialkowie",
                    "label": "Znajdź śmiałków do oczyszczenia szlaku",
                    "mode": "test",
                    "stat": "Handel",
                    "difficulty": 16,
                    "costs": {"gold": 12},
                    "failure_text": "Ekipa rezygnuje po zobaczeniu rozmiaru lawiny.",
                },
                {
                    "id": "wspinaczka",
                    "label": "Samemu znajdź bezpieczne przejście",
                    "mode": "test",
                    "stat": "Walka",
                    "difficulty": 17,
                    "requirements": {"goods": "Lina"},
                    "failure_text": "Podczas wspinaczki tracisz oparcie i zostajesz ranny.",
                    "failure": {"wounds": 1},
                },
            ],
        },
    },
    {
        "id": CHOROBA_DRZEW_ID,
        "name": "Choroba wśród drzew",
        "world_level": 2,
        "duration": DURATION_UNTIL_RESOLVED,
        "description": "Ktoś rozprzestrzenia w lasach chorobę niszczącą drzewa od środka.",
        "effect_text": "Na trzech oznaczonych heksach Lasu produkcja Drewna jest całkowicie zablokowana do czasu usunięcia ich znaczników.",
        "problem": {
            "description": "Truciciele zakażają młode drzewa i niszczą miejsca pozyskiwania Drewna.",
            "condition": "Usuń wszystkie trzy ogniska zarazy.",
            "action_label": "Powstrzymaj trucicieli",
            "marker_count": 3,
            "placement": {"type": "terrain", "terrain": "forest"},
            "effects": [
                {"type": "block_interaction", "interaction": "wood_production", "scope": "marker_tiles"},
            ],
            "reward_mode": "contributors",
            "reward": {"materials": {"Drewno": 4}},
            "deferred_reward": "Do następnej Rady każde miejsce produkcji Drewna danego bohatera produkuje +1 Drewna; integracja nastąpi wraz z systemem produkcji.",
            "methods": [
                {
                    "id": "wytrop",
                    "label": "Wytrop i zwiąż trucicieli",
                    "mode": "test",
                    "stat": "Intryga",
                    "difficulty": 14,
                    "requirements": {"goods": "Lina"},
                    "failure_text": "Gubisz trop i także siebie w lesie.",
                    "failure": {"actions": 2},
                },
                {
                    "id": "przekup",
                    "label": "Przekup ich i przepędź",
                    "mode": "test",
                    "stat": "Handel",
                    "difficulty": 11,
                    "costs": {"gold": 6},
                    "failure_text": "Biorą pieniądze i nadal zatruwają młode drzewa.",
                    "failure": {"actions": 1},
                },
                {
                    "id": "dyplomacja",
                    "label": "Daj im do zrozumienia, że nie tylko oni potrzebują drewna",
                    "mode": "test",
                    "stat": "Dyplomacja",
                    "difficulty": 15,
                    "costs": {"gold": 3},
                    "failure_text": "Rozmowa przeradza się w groźby i tracisz część sławy.",
                    "failure": {"legend": 1},
                },
            ],
        },
    },
    {
        "id": ZAWALONE_PRZEJSCIA_ID,
        "name": "Zawalony trakt na wzgórzach",
        "world_level": 1,
        "duration": DURATION_UNTIL_RESOLVED,
        "description": "Osuwiska odcięły dwa przejścia prowadzące przez wzgórza.",
        "effect_text": "Dwa oznaczone heksy Wzgórz są niedostępne, dopóki ich przejścia nie zostaną udrożnione.",
        "problem": {
            "description": "Kamienie i ziemia całkowicie zasypały drogę.",
            "condition": "Udrożnij oba przejścia.",
            "action_label": "Udrożnij przejście",
            "marker_count": 2,
            "placement": {"type": "terrain", "terrain": "hills"},
            "effects": [{"type": "block_entry", "scope": "marker_tiles"}],
            "reward_mode": "contributors",
            "reward": {"gold": 3, "legend": 1},
            "methods": [
                {
                    "id": "narzedzia",
                    "label": "Zorganizuj materiały i naprawę",
                    "mode": "automatic",
                    "requirements": {"materials": {"Drewno": 2, "Żelazo": 1}},
                    "costs": {"materials": {"Drewno": 2, "Żelazo": 1}},
                    "success_text": "Materiały wystarczają, aby bezpiecznie udrożnić przejście.",
                },
                {
                    "id": "nauka",
                    "label": "Znajdź bezpieczny sposób usunięcia rumowiska",
                    "mode": "test",
                    "stat": "Nauka",
                    "difficulty": 13,
                    "failure_text": "Źle oceniasz osuwisko i tracisz czas.",
                    "failure": {"actions": 1},
                },
                {
                    "id": "robotnicy",
                    "label": "Wynajmij robotników z okolicy",
                    "mode": "test",
                    "stat": "Handel",
                    "difficulty": 11,
                    "costs": {"gold": 8},
                    "failure_text": "Robotnicy biorą zaliczkę, ale odmawiają dalszej pracy.",
                },
            ],
        },
    },
)

_REGISTERED = False


def register_all_threats() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    for threat in THREATS:
        register_world_event(threat)
    _REGISTERED = True
