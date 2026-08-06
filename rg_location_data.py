import copy
import random

from rg_content.quests import SATANIC_FORCES_ID, register_all_quests
from rg_engine.locations import (
    accept_quest_card,
    equip_from_backpack,
    heal_in_location,
    hire_helper_card,
    purchase_card,
    sell_from_backpack,
    train_in_location,
    unequip_to_backpack,
)
from rg_engine.quests import create_offer

register_all_quests()

FOOD_CARDS = [
    {"name": "Bochenek chleba", "category": "food", "price": 2, "description": "Proste jedzenie na droge."},
    {"name": "Suszone mieso", "category": "food", "price": 3, "description": "Trwale zapasy na dluga podroz."},
    {"name": "Goraca zupa", "category": "food", "price": 2, "description": "Posilek dostepny w lokalnej gospodzie."},
    {"name": "Ser i jablka", "category": "food", "price": 3, "description": "Lekki prowiant dla podroznika."},
    {"name": "Placek z warzywami", "category": "food", "price": 4, "description": "Syty posilek testowy."},
]

BASIC_GOODS_CARDS = [
    {"name": "Bandaze", "category": "basic_good", "price": 3, "description": "Jednorazowy towar leczniczy."},
    {"name": "Ziola lecznicze", "category": "basic_good", "price": 3, "description": "Jednorazowy towar leczniczy."},
    {"name": "Lina", "category": "basic_good", "price": 3, "description": "+1 do Kultury w odpowiednim tescie."},
    {"name": "Krzesiwo", "category": "basic_good", "price": 3, "description": "+1 do Handlu w odpowiednim tescie."},
    {"name": "Pochodnia", "category": "basic_good", "price": 3, "description": "+1 do Nauki w odpowiednim tescie."},
    {"name": "Mapa okolicy", "category": "basic_good", "price": 3, "description": "+1 do ruchu na mapie po podpieciu efektow kart."},
    {"name": "Wytrychy", "category": "basic_good", "price": 3, "description": "+1 do Intrygi w odpowiednim tescie."},
    {"name": "Kamien do ostrzenia", "category": "basic_good", "price": 3, "description": "+2 do Walki w odpowiednim tescie."},
    {"name": "Buklak z woda", "category": "basic_good", "price": 3, "description": "Zwieksza leczenie o 1."},
]

LUXURY_CARDS = [
    {"name": "Jedwab z poludnia", "category": "luxury", "price": 6, "description": "Towar luksusowy do questow i handlu."},
    {"name": "Srebrna zastawa", "category": "luxury", "price": 6, "description": "Towar luksusowy ceniony na dworach."},
    {"name": "Korzenne przyprawy", "category": "luxury", "price": 6, "description": "Rzadki ladunek kupiecki."},
    {"name": "Barwione sukno", "category": "luxury", "price": 6, "description": "Towar luksusowy dla bogatych odbiorcow."},
    {"name": "Rzezbiona szkatuła", "category": "luxury", "price": 6, "description": "Cenny przedmiot przeznaczony do handlu."},
]

RING_CARDS = [
    {"name": "Pierscien kupiecki", "category": "ring", "price": 6, "stat_bonus": {"Handel": 1}, "description": "+1 do Handlu po zalozeniu."},
    {"name": "Pierscien uczonego", "category": "ring", "price": 6, "stat_bonus": {"Nauka": 1}, "description": "+1 do Nauki po zalozeniu."},
    {"name": "Pierscien dyplomaty", "category": "ring", "price": 6, "stat_bonus": {"Dyplomacja": 1}, "description": "+1 do Dyplomacji po zalozeniu."},
    {"name": "Pierscien intryganta", "category": "ring", "price": 6, "stat_bonus": {"Intryga": 1}, "description": "+1 do Intrygi po zalozeniu."},
    {"name": "Pierscien opowiesci", "category": "ring", "price": 6, "stat_bonus": {"Kultura": 1}, "description": "+1 do Kultury po zalozeniu."},
]

WEAPON_CARDS = [
    {"name": "Prosty miecz", "category": "weapon", "price": 6, "hit_bonus": 0, "damage_bonus": 0, "description": "Podstawowa bron."},
    {"name": "Topor wojenny", "category": "weapon", "price": 6, "hit_bonus": 0, "damage_bonus": 0, "description": "Ciezka bron do walki wrecz."},
    {"name": "Wlocznia straznika", "category": "weapon", "price": 6, "hit_bonus": 0, "damage_bonus": 0, "description": "Bron o duzym zasiegu."},
    {"name": "Mlot bojowy", "category": "weapon", "price": 6, "hit_bonus": 0, "damage_bonus": 0, "description": "Bron przeznaczona przeciw pancerzom."},
    {"name": "Krotki luk", "category": "weapon", "price": 6, "hit_bonus": 0, "damage_bonus": 0, "description": "Lekka bron dystansowa."},
]

ARMOR_CARDS = [
    {"name": "Skorzana zbroja", "category": "armor", "price": 6, "armor_class": 12, "description": "Zwykla zbroja: 12 KP."},
    {"name": "Przeszywanica", "category": "armor", "price": 6, "armor_class": 12, "description": "Zwykla zbroja: 12 KP."},
    {"name": "Kolczuga", "category": "armor", "price": 10, "quality": "rzadka", "armor_class": 14, "description": "Rzadka zbroja: 14 KP."},
    {"name": "Pancerz straznika", "category": "armor", "price": 6, "armor_class": 12, "description": "Zwykla zbroja: 12 KP."},
    {"name": "Skorzany kaftan", "category": "armor", "price": 6, "armor_class": 12, "description": "Zwykla zbroja: 12 KP."},
]

HELPER_CARDS = [
    {"name": "Zwiadowca", "price": 4, "stat_bonus": {"Intryga": 1}, "effect_text": "+1 Intryga przy zwiadzie i omijaniu zagrozen.", "description": "Pomaga podczas podrozy i obserwacji terenu."},
    {"name": "Najemny miecz", "price": 5, "stat_bonus": {"Walka": 1}, "effect_text": "+1 Walka w testach bojowych.", "description": "Pomocnik przeznaczony do walki."},
    {"name": "Medyk polowy", "price": 5, "effect_text": "Leczenie kazdej Rany jest o 1 monete tansze.", "description": "Pomocnik zwiazany z leczeniem Ran."},
    {"name": "Skryba", "price": 4, "stat_bonus": {"Nauka": 1}, "effect_text": "+1 Nauka przy dokumentach, ruinach i badaniach.", "description": "Pomaga w testach Nauki i odczytywaniu dokumentow."},
    {"name": "Posel", "price": 4, "stat_bonus": {"Dyplomacja": 1}, "effect_text": "+1 Dyplomacja w rozmowach i negocjacjach.", "description": "Pomaga w testach Dyplomacji."},
    {"name": "Przewodnik", "price": 4, "effect_text": "Pierwszy trudny teren w turze moze miec koszt nizszy o 1.", "description": "Pomaga w podrozy przez trudny teren."},
]

QUEST_CARDS = [
    {"name": "Wilki na trakcie", "deck": "Wojenna", "description": "Dotrzyj na wskazany trakt i rozpraw sie z wataha."},
    {"name": "Zaginiony patrol", "deck": "Wojenna", "description": "Odszukaj zolnierzy, ktorzy nie wrocili do zamku."},
    {"name": "Brakujacy ladunek", "deck": "Ekonomiczna", "description": "Pomoz kupcowi odzyskac potrzebne towary."},
    {"name": "Spor o studnie", "deck": "Ekonomiczna", "description": "Rozwiaz konflikt o dostep do wody."},
    {"name": "Zatruty strumien", "deck": "Intrygi", "description": "Ustal, kto potajemnie zatruwa wode."},
    {"name": "Szpieg na dworze", "deck": "Intrygi", "description": "Zdobadz dowody przeciw ukrytemu agentowi."},
    {"name": "Poselstwo do sasiadow", "deck": "Dyplomacji", "description": "Dostarcz warunki porozumienia i zakoncz spor."},
    {"name": "Dwie sklocone rodziny", "deck": "Dyplomacji", "description": "Doprowadz do ugody miedzy rodami."},
    {"name": "Festiwal bez artystow", "deck": "Kultury", "description": "Pomoz przygotowac wydarzenie dla mieszkancow."},
    {"name": "Zaginiona kronika", "deck": "Kultury", "description": "Odzyskaj cenna kronike miejscowego rodu."},
    {"name": "Spadajace gwiazdy", "deck": "Nauki", "description": "Wyjasnij niepokojace zjawisko nad traktem."},
]

SHOP_POOLS = {
    "food": FOOD_CARDS,
    "basic_good": BASIC_GOODS_CARDS,
    "luxury": LUXURY_CARDS,
    "ring": RING_CARDS,
    "weapon": WEAPON_CARDS,
    "armor": ARMOR_CARDS,
}
SHOP_LAYOUTS = {
    "village": ["food", "food", "basic_good", "basic_good", "basic_good"],
    "city": ["luxury", "luxury", "luxury", "ring", "ring"],
    "castle": ["weapon", "weapon", "weapon", "armor", "armor"],
}


def helper_effect_text(helper):
    return helper.get("effect_text") or helper.get("description", "Brak opisanego efektu.")


def helper_bonus_summary(player):
    bonuses = {}
    for helper in player.get("helpers", []):
        for stat, value in helper.get("stat_bonus", {}).items():
            bonuses[stat] = bonuses.get(stat, 0) + value
    return bonuses


def _copy_card(card):
    return copy.deepcopy(card)


def _draw_unique(pool, visible, rng):
    visible_names = {card["name"] for card in visible if card}
    candidates = [card for card in pool if card["name"] not in visible_names]
    return _copy_card(rng.choice(candidates or pool))


def _draw_quest(visible, rng):
    visible_decks = {card["deck"] for card in visible if card}
    candidates = [card for card in QUEST_CARDS if card["deck"] not in visible_decks]
    if not candidates:
        visible_names = {card["name"] for card in visible if card}
        candidates = [card for card in QUEST_CARDS if card["name"] not in visible_names]
    return _copy_card(rng.choice(candidates or QUEST_CARDS))


def initialize_location(location, rng=None):
    if location.get("offers_ready"):
        return location
    rng = rng or random
    layout = list(SHOP_LAYOUTS.get(location.get("kind"), SHOP_LAYOUTS["city"]))
    shop = [_draw_unique(SHOP_POOLS[category], [], rng) for category in layout]
    helpers = []
    for _ in range(3):
        helpers.append(_draw_unique(HELPER_CARDS, helpers, rng))
    quests = []
    if location.get("name") == "Artium" and not location.get("special_quest_claimed"):
        quests.append(create_offer(SATANIC_FORCES_ID))
    while len(quests) < 3:
        quests.append(_draw_quest(quests, rng))
    location["shop_layout"] = layout
    location["shop_offers"] = shop
    location["helper_offers"] = helpers
    location["quest_offers"] = quests
    location["offers_ready"] = True
    return location


def buy_shop_item(location, player, slot_index, rng=None):
    rng = rng or random
    initialize_location(location, rng)
    offers = location["shop_offers"]
    if slot_index < 0 or slot_index >= len(offers):
        return False, "Nieprawidlowy slot sklepu."
    card = offers[slot_index]
    success, message = purchase_card(player, card)
    if not success:
        return False, message
    category = card["category"]
    visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
    offers[slot_index] = _draw_unique(SHOP_POOLS[category], visible_without_slot, rng)
    return True, message


def hire_helper(location, player, slot_index, rng=None):
    rng = rng or random
    initialize_location(location, rng)
    offers = location["helper_offers"]
    if slot_index < 0 or slot_index >= len(offers):
        return False, "Nieprawidlowy slot pomocnika."
    helper = offers[slot_index]
    success, message = hire_helper_card(player, helper)
    if not success:
        return False, message
    visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
    offers[slot_index] = _draw_unique(HELPER_CARDS, visible_without_slot, rng)
    return True, message


def take_quest(location, player, slot_index, rng=None):
    rng = rng or random
    initialize_location(location, rng)
    offers = location["quest_offers"]
    if slot_index < 0 or slot_index >= len(offers):
        return False, "Nieprawidlowy slot questa."
    quest = offers[slot_index]
    success, message = accept_quest_card(player, quest)
    if not success:
        return False, message
    if quest.get("id") == SATANIC_FORCES_ID:
        location["special_quest_claimed"] = True
    visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
    offers[slot_index] = _draw_quest(visible_without_slot, rng)
    return True, message


def train_player(location, player, stat):
    return train_in_location(player, player.get("_token_ref"), location, stat)


def heal_player(location, player, amount=None):
    return heal_in_location(player, player.get("_token_ref"), amount)


def equip_inventory_item(player, inventory_index):
    return equip_from_backpack(player, inventory_index)


def unequip_equipment_slot(player, slot):
    return unequip_to_backpack(player, slot)


def sell_inventory_item(player, inventory_index):
    return sell_from_backpack(player, inventory_index)
