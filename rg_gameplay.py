import random

import pygame

from rg_data import MAX_WOUNDS, MUTED, PANEL_DARK, TEXT
from rg_location_data import helper_bonus_summary
from rg_ui import Button, draw_lines, draw_panel, wrap


VICTORY_LEGEND = 5
QUEST_RULES = {
    "Wojenna": {"stat": "Walka", "difficulty": 8, "gold": 4, "legend": 2},
    "Ekonomiczna": {"stat": "Handel", "difficulty": 8, "gold": 5, "legend": 1},
    "Intrygi": {"stat": "Intryga", "difficulty": 8, "gold": 4, "legend": 2},
    "Dyplomacji": {"stat": "Dyplomacja", "difficulty": 8, "gold": 4, "legend": 2},
    "Kultury": {"stat": "Kultura", "difficulty": 8, "gold": 3, "legend": 2},
    "Nauki": {"stat": "Nauka", "difficulty": 8, "gold": 3, "legend": 2},
}


def quest_rule(quest):
    return QUEST_RULES.get(quest.get("deck"), {"stat": "Walka", "difficulty": 8, "gold": 3, "legend": 1})


def quest_test_preview(player, quest):
    rule = quest_rule(quest)
    stat = rule["stat"]
    base = player.get("stats", {}).get(stat, 0)
    helper_bonus = helper_bonus_summary(player).get(stat, 0)
    return stat, base, helper_bonus, rule["difficulty"]


def resolve_quest(player, quest_index, rng=None):
    rng = rng or random
    quests = player.setdefault("active_quests", [])
    if quest_index < 0 or quest_index >= len(quests):
        return False, "Nieprawidlowy quest."

    quest = quests[quest_index]
    rule = quest_rule(quest)
    stat = rule["stat"]
    base = player.get("stats", {}).get(stat, 0)
    helper_bonus = helper_bonus_summary(player).get(stat, 0)
    roll = rng.randint(1, 6)
    total = roll + base + helper_bonus

    if total >= rule["difficulty"]:
        quests.pop(quest_index)
        player["gold"] = player.get("gold", 0) + rule["gold"]
        player["legend"] = player.get("legend", 0) + rule["legend"]
        player.setdefault("completed_quests", []).append(dict(quest))
        return True, (
            f"SUKCES: {quest['name']} | {stat} {base}+{helper_bonus}, rzut {roll}, razem {total}. "
            f"Nagroda: +{rule['gold']} zlota, +{rule['legend']} Legendy."
        )

    player["wounds"] = min(MAX_WOUNDS, player.get("wounds", 0) + 1)
    return False, (
        f"PORAŻKA: {quest['name']} | {stat} {base}+{helper_bonus}, rzut {roll}, razem {total}/{rule['difficulty']}. "
        "Otrzymujesz 1 Rane. Quest pozostaje aktywny."
    )


def heal_one_wound(player):
    wounds = player.get("wounds", 0)
    if wounds <= 0:
        return False, "Nie masz Ran do wyleczenia."
    cost = 1 if any(helper.get("name") == "Medyk polowy" for helper in player.get("helpers", [])) else 2
    if player.get("gold", 0) < cost:
        return False, f"Leczenie jednej Rany kosztuje {cost} zlota."
    player["gold"] -= cost
    player["wounds"] -= 1
    return True, f"Wyleczono 1 Rane za {cost} zlota."


def train_stat(player, stat):
    if stat not in player.get("stats", {}):
        return False, "Nieprawidlowa statystyka."
    if player["stats"][stat] >= 6:
        return False, f"{stat} ma juz maksymalna wartosc 6."
    cost = 4
    if player.get("gold", 0) < cost:
        return False, f"Trening kosztuje {cost} zlota."
    player["gold"] -= cost
    player["stats"][stat] += 1
    return True, f"Trening zakonczony: {stat} wzrasta do {player['stats'][stat]}."


def has_won(player):
    return player.get("legend", 0) >= VICTORY_LEGEND


def draw_victory_screen(screen, title_font, font, small_font, mouse_pos, winner):
    screen.fill((16, 12, 10))
    sw, sh = screen.get_size()
    panel = pygame.Rect(max(40, sw // 2 - 360), max(40, sh // 2 - 230), 720, 460)
    draw_panel(screen, panel)
    title = title_font.render("ZWYCIĘSTWO", True, TEXT)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 76)))
    subtitle = font.render(f"{winner.get('name', 'Bohater')} zdobyl {winner.get('legend', 0)} punktow Legendy!", True, TEXT)
    screen.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.y + 145)))

    summary = [
        f"Ukonczone questy: {len(winner.get('completed_quests', []))}",
        f"Pozostale zloto: {winner.get('gold', 0)}",
        f"Rany: {winner.get('wounds', 0)}/{MAX_WOUNDS}",
        "Pierwsza grywalna petla zostala zakonczona.",
    ]
    y = panel.y + 205
    for line in summary:
        label = small_font.render(line, True, MUTED)
        screen.blit(label, label.get_rect(center=(panel.centerx, y)))
        y += 36

    button = Button("Powrot do menu", "victory_menu", (panel.centerx - 110, panel.bottom - 76, 220, 46))
    button.draw(screen, font, mouse_pos)
    return [button]
