from __future__ import annotations

from rg_engine.world_events import register_world_event

WORLD_EVENTS = (
    {
        "id": "obfite_zbiory",
        "name": "Obfite zbiory",
        "description": "Pola rodzą lepiej niż zwykle, a trakty wypełniają wozy z żywnością.",
        "effect_text": "Każdy bohater otrzymuje 2× Bochenek chleba.",
        "duration": "instant",
        "effects": [{"type": "food", "item": "Bochenek chleba", "amount": 2}],
    },
    {
        "id": "krolewski_podatek",
        "name": "Królewski podatek",
        "description": "Korona zbiera dodatkowe daniny na utrzymanie dróg, straży i garnizonów.",
        "effect_text": "Każdy bohater traci do 2 monet.",
        "duration": "instant",
        "effects": [{"type": "gold", "amount": -2}],
    },
    {
        "id": "wielki_jarmark",
        "name": "Wielki jarmark",
        "description": "Kupcy z wielu krain zjeżdżają do miast, wsi i zamków z pełnymi wozami towarów.",
        "effect_text": "Do następnej Rady ceny zakupów i pomocników są niższe o 1 monetę, minimum 1.",
        "duration": "until_next_council",
        "modifiers": {"market_price_modifier": -1},
    },
    {
        "id": "niebezpieczne_szlaki",
        "name": "Niebezpieczne szlaki",
        "description": "Ulewy, osuwiska i rozbójnicy utrudniają podróż przez najtrudniejsze odcinki szlaków.",
        "effect_text": "Do następnej Rady wejście na teren o bazowym koszcie 2 akcji kosztuje dodatkową 1 akcję.",
        "duration": "until_next_council",
        "modifiers": {"difficult_terrain_action_modifier": 1},
    },
    {
        "id": "dzien_uzdrowicieli",
        "name": "Dzień Uzdrowicieli",
        "description": "Cyrulicy, zielarze i medycy otwierają swoje lecznice dla podróżnych i bohaterów.",
        "effect_text": "Do następnej Rady leczenie każdej Rany kosztuje o 1 monetę mniej, minimum 1.",
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
