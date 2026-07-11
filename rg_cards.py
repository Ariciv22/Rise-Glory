import random
from dataclasses import dataclass, field

from rg_data import HERO_MOVES_PER_TURN


HAND_LIMIT = 5
MAX_WOUNDS = 5


@dataclass(frozen=True)
class Card:
    card_id: str
    name: str
    category: str
    description: str
    effect_text: str
    effects: dict = field(default_factory=dict)
    cost: int = 0


class Deck:
    def __init__(self, cards, hand_limit=HAND_LIMIT):
        self.hand_limit = hand_limit
        self.draw_pile = list(cards)
        self.discard_pile = []
        self.hand = []
        random.shuffle(self.draw_pile)

    def reshuffle_discard(self):
        if self.draw_pile or not self.discard_pile:
            return False
        self.draw_pile = self.discard_pile
        self.discard_pile = []
        random.shuffle(self.draw_pile)
        return True

    def draw(self, count=1):
        drawn = []
        for _ in range(count):
            if len(self.hand) >= self.hand_limit:
                break
            if not self.draw_pile:
                self.reshuffle_discard()
            if not self.draw_pile:
                break
            card = self.draw_pile.pop()
            self.hand.append(card)
            drawn.append(card)
        return drawn

    def draw_to_hand_limit(self):
        return self.draw(self.hand_limit - len(self.hand))

    def discard_card(self, index):
        if index < 0 or index >= len(self.hand):
            return None
        card = self.hand.pop(index)
        self.discard_pile.append(card)
        return card

    def play_card(self, index, hero, token):
        if index < 0 or index >= len(self.hand):
            return False, "Nie znaleziono tej karty."

        card = self.hand[index]
        if hero.get("gold", 0) < card.cost:
            return False, f"Za malo zlota. Karta kosztuje {card.cost}."

        hero["gold"] = max(0, hero.get("gold", 0) - card.cost)
        changes = []

        gold_change = int(card.effects.get("gold", 0))
        if gold_change:
            hero["gold"] = max(0, hero.get("gold", 0) + gold_change)
            changes.append(_format_change("zlota", gold_change))

        legend_change = int(card.effects.get("legend", 0))
        if legend_change:
            hero["legend"] = max(0, hero.get("legend", 0) + legend_change)
            changes.append(_format_change("Legendy", legend_change))

        wound_change = int(card.effects.get("wounds", 0))
        if wound_change:
            old_wounds = hero.get("wounds", 0)
            hero["wounds"] = max(0, min(MAX_WOUNDS, old_wounds + wound_change))
            actual_change = hero["wounds"] - old_wounds
            if actual_change:
                changes.append(_format_change("ran", actual_change))

        move_change = int(card.effects.get("moves", 0))
        if move_change and token:
            token.moves = max(0, token.moves + move_change)
            changes.append(_format_change("ruchu", move_change))

        self.hand.pop(index)
        self.discard_pile.append(card)

        cost_text = f" Koszt: {card.cost} zlota." if card.cost else ""
        result_text = ", ".join(changes) if changes else "bez natychmiastowego efektu"
        return True, f"Zagrano: {card.name}.{cost_text} Efekt: {result_text}."

    def counts(self):
        return {
            "draw": len(self.draw_pile),
            "hand": len(self.hand),
            "discard": len(self.discard_pile),
        }


def _format_change(label, value):
    sign = "+" if value > 0 else ""
    return f"{sign}{value} {label}"


def _card(card_id, name, category, description, effect_text, effects, cost=0):
    return Card(
        card_id=card_id,
        name=name,
        category=category,
        description=description,
        effect_text=effect_text,
        effects=effects,
        cost=cost,
    )


def class_card_for(hero_name):
    cards = {
        "Wojownik": _card(
            "class_warrior",
            "Wyzwanie Pojedynku",
            "Bitewna",
            "Publicznie rzucasz wyzwanie niebezpiecznemu przeciwnikowi.",
            "+2 Legenda, +1 rana",
            {"legend": 2, "wounds": 1},
        ),
        "Handlarz": _card(
            "class_merchant",
            "Zyskowny Kontrakt",
            "Handlowa",
            "Wykorzystujesz okazje, zanim dowiedza sie o niej inni kupcy.",
            "+3 zlota",
            {"gold": 3},
        ),
        "Dyplomata": _card(
            "class_diplomat",
            "Udane Poselstwo",
            "Dyplomatyczna",
            "Dobrze dobrane slowa otwieraja bramy i sakiewki.",
            "+1 Legenda, +1 zlota",
            {"legend": 1, "gold": 1},
        ),
        "Kulturowiec": _card(
            "class_culture",
            "Publiczny Wystep",
            "Kulturowa",
            "Finansujesz wystep, o ktorym mowi cale miasto.",
            "+2 Legenda",
            {"legend": 2},
            cost=1,
        ),
        "Intrygant": _card(
            "class_intrigue",
            "Tajna Umowa",
            "Intryga",
            "Nie wszyscy musza wiedziec, kto naprawde zarobil na ukladzie.",
            "+2 zlota",
            {"gold": 2},
        ),
        "Uczony": _card(
            "class_scholar",
            "Odczytanie Inskrypcji",
            "Naukowa",
            "Rozwiazujesz zagadke, ktorej inni nie potrafili zrozumiec.",
            "+1 Legenda, +1 zlota",
            {"legend": 1, "gold": 1},
        ),
    }
    return cards.get(hero_name, cards["Wojownik"])


def build_starter_deck(hero):
    small_trade = _card(
        "small_trade",
        "Drobny Handel",
        "Handlowa",
        "Sprzedajesz zapasy z zyskiem na lokalnym targu.",
        "+1 zlota",
        {"gold": 1},
    )
    rest = _card(
        "road_rest",
        "Odpoczynek w Drodze",
        "Przygoda",
        "Bezpieczny nocleg pozwala opatrzyc rany.",
        "-1 rana",
        {"wounds": -1},
    )
    quick_march = _card(
        "quick_march",
        "Szybki Marsz",
        "Przygoda",
        "Znajdujesz krotsza droge i odzyskujesz tempo wyprawy.",
        "+1 ruchu",
        {"moves": 1},
    )
    heroic_choice = _card(
        "heroic_choice",
        "Bohaterska Decyzja",
        "Osobista",
        "Podejmujesz decyzje, ktora buduje twoja opowiesc.",
        "+1 Legenda",
        {"legend": 1},
    )
    risky_expedition = _card(
        "risky_expedition",
        "Ryzykowna Wyprawa",
        "Przygoda",
        "Wracasz z lupem, ale nie bez sladov niebezpiecznej drogi.",
        "+2 zlota, +1 rana",
        {"gold": 2, "wounds": 1},
    )
    investment = _card(
        "investment",
        "Kosztowna Inwestycja",
        "Handlowa",
        "Wykladasz zloto teraz, aby szybko odzyskac je z zyskiem.",
        "+3 zlota",
        {"gold": 3},
        cost=1,
    )
    class_card = class_card_for(hero.get("name", "Wojownik"))

    cards = [
        small_trade,
        small_trade,
        rest,
        rest,
        quick_march,
        quick_march,
        heroic_choice,
        heroic_choice,
        risky_expedition,
        investment,
        class_card,
        class_card,
    ]
    deck = Deck(cards)
    deck.draw_to_hand_limit()
    return deck
