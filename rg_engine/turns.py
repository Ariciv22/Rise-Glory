import random

from rg_core.data import COUNCIL_ROUNDS
from rg_engine.heroes import begin_hero_turn


def resolve_initiative(players, rng=None):
    rng = rng or random
    if not players:
        return {
            "initial_rolls": {},
            "reroll_rounds": [],
            "starter_index": 0,
            "turn_order": [],
        }

    initial_rolls = {index: rng.randint(1, 20) for index in range(len(players))}
    highest = max(initial_rolls.values())
    tied = [index for index, value in initial_rolls.items() if value == highest]
    reroll_rounds = []

    while len(tied) > 1:
        rerolls = {index: rng.randint(1, 20) for index in tied}
        reroll_rounds.append(rerolls)
        highest = max(rerolls.values())
        tied = [index for index, value in rerolls.items() if value == highest]

    starter_index = tied[0]
    turn_order = list(range(starter_index, len(players))) + list(range(0, starter_index))
    return {
        "initial_rolls": initial_rolls,
        "reroll_rounds": reroll_rounds,
        "starter_index": starter_index,
        "turn_order": turn_order,
    }


class TurnManager:
    def __init__(self, turn_order):
        if not turn_order:
            raise ValueError("Turn order cannot be empty")
        self.turn_order = list(turn_order)
        self.position = 0
        self.round_number = 1
        self.council_cycle = 1

    @property
    def active_player_index(self):
        return self.turn_order[self.position]

    def end_turn(self, tokens):
        current_index = self.active_player_index
        tokens[current_index].actions = 0

        round_completed = self.position == len(self.turn_order) - 1
        self.position = (self.position + 1) % len(self.turn_order)
        next_index = self.active_player_index
        tokens[next_index].reset_actions()
        begin_hero_turn(tokens[next_index].hero, tokens[next_index])

        council_due = False
        if round_completed:
            self.round_number += 1
            if self.council_cycle >= COUNCIL_ROUNDS:
                council_due = True
                self.council_cycle = 1
            else:
                self.council_cycle += 1

        return {
            "active_player_index": next_index,
            "round_completed": round_completed,
            "council_due": council_due,
        }
