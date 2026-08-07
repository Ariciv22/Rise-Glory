from __future__ import annotations

from rg_engine.world_events import register_world_event

WORLD_EVENTS = (
    {
        "id": "obfite_zbiory",
        "name": "Obfite zbiory",
        "description": "Pola rodza lepiej niz zwykle, a trakty wypelniaja wozy z zywnoscia.",
        "effect_text": "Kazdy bohater otrzymuje 2x Bochenek chleba.",
        "duration": "instant",
        "effects": [{"type": "food", "item": "Bochenek chleba", "amount": 2}],
    },
    {
        "id": "krolewski_podatek",
        "name": "Krolewski podatek",
        "description": "Korona zbiera dodatkowe daniny na utrzymanie drog, strazy i garnizonow.",
        "effect_text": "Kazdy bohater traci do 2 monet.",
        "duration": "instant",
        "effects": [{"type": "gold", "amount": -2}],
    },
    {
        "id": "wielki_jarmark",
        "name": "Wielki jarmark",
        "description": "Kupcy z wielu krain zjezdzaja do miast, wsi i zamkow z pelnymi wozami towarow.",
        "effect_text": "Do nastepnej Rady ceny zakupow i pomocnikow sa nizsze o 1 monete, minimum 1.",
        "duration": "until_next_council",
        "modifiers": {"market_price_modifier": -1},
    },
    {
        "id": "niebezpieczne_szlaki",
        "name": "Niebezpieczne szlaki",
        "description": "Ulewy, osuwiska i rozbojnicy utrudniaja podroz przez najtrudniejsze odcinki szlakow.",
        "effect_text": "Do nastepnej Rady wejscie na teren o bazowym koszcie 2 akcji kosztuje dodatkowa 1 akcje.",
        "duration": "until_next_council",
        "modifiers": {"difficult_terrain_action_modifier": 1},
    },
    {
        "id": "dzien_uzdrowicieli",
        "name": "Dzien Uzdrowicieli",
        "description": "Cyrulicy, zielarze i medycy otwieraja swoje lecznice dla podroznych i bohaterow.",
        "effect_text": "Do nastepnej Rady leczenie kazdej Rany kosztuje o 1 monete mniej, minimum 1.",
        "duration": "until_next_council",
        "modifiers": {"healing_cost_modifier": -1},
    },
)

_REGISTERED = False


def register_all_world_events() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    for event in WORLD_EVENTS:
        register_world_event(event)
    _REGISTERED = True
