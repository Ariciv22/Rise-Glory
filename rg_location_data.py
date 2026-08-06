import copy
import random

from rg_satanic_forces import activate_quest, create_quest_offer, is_satanic_forces


FOOD_CARDS = [
    {"name": "Bochenek chleba", "category": "food", "price": 2, "description": "Proste jedzenie na droge. Efekt glodu zostanie dodany pozniej."},
    {"name": "Suszone mieso", "category": "food", "price": 3, "description": "Trwale zapasy na dluga podroz."},
    {"name": "Goraca zupa", "category": "food", "price": 2, "description": "Posilek dostepny w lokalnej gospodzie."},
    {"name": "Ser i jablka", "category": "food", "price": 3, "description": "Lekki prowiant dla podroznika."},
    {"name": "Placek z warzywami", "category": "food", "price": 4, "description": "Syty posilek testowy."},
]

BASIC_GOODS_CARDS = [
    {"name": "Bandaze", "category": "basic_good", "price": 3, "description": "Towar jednorazowy. Leczenie zostanie podpiete w kolejnym etapie."},
    {"name": "Ziola lecznicze", "category": "basic_good", "price": 3, "description": "Towar jednorazowy zwiazany z leczeniem."},
    {"name": "Lina", "category": "basic_good", "price": 3, "description": "+1 do Kultury w odpowiednim tescie."},
    {"name": "Krzesiwo", "category": "basic_good", "price": 3, "description": "+1 do Handlu w odpowiednim tescie."},
    {"name": "Pochodnia", "category": "basic_good", "price": 3, "description": "+1 do Nauki w odpowiednim tescie."},
    {"name": "Mapa okolicy", "category": "basic_good", "price": 3, "description": "+1 do ruchu na mapie po podpieciu efektow kart."},
    {"name": "Wytrychy", "category": "basic_good", "price": 3, "description": "+1 do Intrygi w odpowiednim tescie."},
    {"name": "Kamien do ostrzenia", "category": "basic_good", "price": 3, "description": "+2 do Walki w odpowiednim tescie."},
    {"name": "Buklak z woda", "category": "basic_good", "price": 3, "description": "Zwieksza leczenie o 1 po podpieciu pelnego systemu."},
]

LUXURY_CARDS = [
    {"name": "Jedwab z poludnia", "category": "luxury", "price": 6, "description": "Towar luksusowy do questow, handlu i odsprzedazy."},
    {"name": "Srebrna zastawa", "category": "luxury", "price": 6, "description": "Towar luksusowy ceniony na dworach."},
    {"name": "Korzenne przyprawy", "category": "luxury", "price": 6, "description": "Rzadki ladunek kupiecki."},
    {"name": "Barwione sukno", "category": "luxury", "price": 6, "description": "Towar luksusowy dla bogatych odbiorcow."},
    {"name": "Rzezbiona szkatuła", "category": "luxury", "price": 6, "description": "Cenny przedmiot przeznaczony do handlu."},
]

RING_CARDS = [
    {"name": "Pierscien kupca", "category": "ring", "price": 6, "description": "Testowy pierscien wspierajacy Handel."},
    {"name": "Pierscien uczonego", "category": "ring", "price": 6, "description": "Testowy pierscien wspierajacy Nauke."},
    {"name": "Pierscien dyplomaty", "category": "ring", "price": 6, "description": "Testowy pierscien wspierajacy Dyplomacje."},
    {"name": "Pierscien intryganta", "category": "ring", "price": 6, "description": "Testowy pierscien wspierajacy Intryge."},
    {"name": "Pierscien opowiesci", "category": "ring", "price": 6, "description": "Testowy pierscien wspierajacy Kulture."},
]

WEAPON_CARDS = [
    {"name": "Prosty miecz", "category": "weapon", "price": 6, "description": "Zwykla bron testowa."},
    {"name": "Topor wojenny", "category": "weapon", "price": 6, "description": "Ciezka bron do walki wrecz."},
    {"name": "Wlocznia straznika", "category": "weapon", "price": 6, "description": "Bron o duzym zasiegu."},
    {"name": "Mlot bojowy", "category": "weapon", "price": 6, "description": "Bron przeznaczona przeciw pancerzom."},
    {"name": "Krotki luk", "category": "weapon", "price": 6, "description": "Lekka bron dystansowa."},
]

ARMOR_CARDS = [
    {"name": "Skorzana zbroja", "category": "armor", "price": 6, "description": "Zwykla zbroja testowa o docelowej wartosci 12 KP."},
    {"name": "Przeszywanica", "category": "armor", "price": 6, "description": "Lekka ochrona dla podroznika."},
    {"name": "Kolczuga", "category": "armor", "price": 6, "description": "Zbroja testowa do pozniejszego zbalansowania."},
    {"name": "Pancerz straznika", "category": "armor", "price": 6, "description": "Ochrona uzywana przez zamkowa straz."},
    {"name": "Skorzany kaftan", "category": "armor", "price": 6, "description": "Podstawowa ochrona bez ograniczenia ruchu."},
]

HELPER_CARDS = [
    {"name": "Zwiadowca", "price": 4, "stat_bonus": {"Intryga": 1}, "effect_text": "+1 Intryga przy zwiadzie i omijaniu zagrozen.", "description": "Pomaga podczas podrozy i obserwacji terenu."},
    {"name": "Najemny miecz", "price": 5, "stat_bonus": {"Walka": 1}, "effect_text": "+1 Walka w testach bojowych.", "description": "Pomocnik przeznaczony do walki."},
    {"name": "Medyk polowy", "price": 5, "effect_text": "Leczenie Ran jest o 1 monete tansze.", "description": "Pomocnik zwiazany z leczeniem Ran."},
    {"name": "Skryba", "price": 4, "stat_bonus": {"Nauka": 1}, "effect_text": "+1 Nauka przy dokumentach, ruinach i badaniach.", "description": "Pomaga w testach Nauki i odczytywaniu dokumentow."},
    {"name": "Posel", "price": 4, "stat_bonus": {"Dyplomacja": 1}, "effect_text": "+1 Dyplomacja w rozmowach i negocjacjach.", "description": "Pomaga w testach Dyplomacji."},
    {"name": "Przewodnik", "price": 4, "effect_text": "Pierwszy trudny teren w turze ma koszt nizszy o 1 akcje po podpieciu ruchu pomocnikow.", "description": "Pomaga w podrozy przez trudny teren."},
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

SHOP_POOLS = {"food": FOOD_CARDS, "basic_good": BASIC_GOODS_CARDS, "luxury": LUXURY_CARDS, "ring": RING_CARDS, "weapon": WEAPON_CARDS, "armor": ARMOR_CARDS}
SHOP_LAYOUTS = {"village": ["food", "food", "basic_good", "basic_good", "basic_good"], "city": ["luxury", "luxury", "luxury", "ring", "ring"], "castle": ["weapon", "weapon", "weapon", "armor", "armor"]}


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
    shop = []
    for category in layout:
        shop.append(_draw_unique(SHOP_POOLS[category], shop, rng))
    helpers = []
    for _ in range(3):
        helpers.append(_draw_unique(HELPER_CARDS, helpers, rng))
    quests = []
    if location.get("name") == "Artium" and not location.get("special_quest_claimed"):
        quests.append(create_quest_offer())
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
    price = card["price"]
    if player.get("gold", 0) < price:
        return False, "Nie masz wystarczajacej liczby monet."
    player["gold"] -= price
    category = card["category"]
    if category == "food":
        player.setdefault("food", []).append(card["name"])
    elif category in {"basic_good", "luxury"}:
        player.setdefault("goods", []).append(card["name"])
    else:
        player.setdefault("inventory", []).append(_copy_card(card))
    visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
    offers[slot_index] = _draw_unique(SHOP_POOLS[category], visible_without_slot, rng)
    return True, f"Kupiono: {card['name']} za {price} monet."


def hire_helper(location, player, slot_index, rng=None):
    rng = rng or random
    initialize_location(location, rng)
    offers = location["helper_offers"]
    if slot_index < 0 or slot_index >= len(offers):
        return False, "Nieprawidlowy slot pomocnika."
    if len(player.setdefault("helpers", [])) >= 5:
        return False, "Masz juz maksymalnie 5 pomocnikow."
    helper = offers[slot_index]
    price = helper["price"]
    if player.get("gold", 0) < price:
        return False, "Nie masz wystarczajacej liczby monet."
    player["gold"] -= price
    player["helpers"].append(_copy_card(helper))
    visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
    offers[slot_index] = _draw_unique(HELPER_CARDS, visible_without_slot, rng)
    return True, f"Zatrudniono: {helper['name']} - {helper_effect_text(helper)}"


def take_quest(location, player, slot_index, rng=None):
    rng = rng or random
    initialize_location(location, rng)
    offers = location["quest_offers"]
    if slot_index < 0 or slot_index >= len(offers):
        return False, "Nieprawidlowy slot questa."
    if len(player.setdefault("active_quests", [])) >= 3:
        return False, "Masz juz maksymalnie 3 aktywne questy."
    quest = offers[slot_index]
    if is_satanic_forces(quest):
        for key in ("active_quests", "completed_quests", "failed_quests"):
            if any(is_satanic_forces(existing) for existing in player.get(key, []) or []):
                return False, "Ten bohater ma juz zapisany quest Szatanskie sily."
        player["active_quests"].append(activate_quest(quest))
        location["special_quest_claimed"] = True
    else:
        player["active_quests"].append(_copy_card(quest))
    visible_without_slot = [offer for index, offer in enumerate(offers) if index != slot_index]
    offers[slot_index] = _draw_quest(visible_without_slot, rng)
    return True, f"Pobrano quest: {quest['name']}."