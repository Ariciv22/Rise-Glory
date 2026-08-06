import pygame

import rg_satanic_forces as base
from rg_combat import is_combat_active, start_combat
from rg_data import GOLD, MUTED, TEXT
from rg_ui import draw_lines, wrap

QUEST_ID = base.QUEST_ID
QUEST_NAME = base.QUEST_NAME
QUEST_PLACE_ACTION = base.QUEST_PLACE_ACTION


def find_player_quest(player, include_history=True):
    return base.find_player_quest(player, include_history=include_history)


def has_active_quest(player):
    return base.find_player_quest(player, include_history=True) is not None


def _enemy_data():
    world_level = base.current_world_level()
    return {
        "id": "przeklety_zolnierz",
        "name": "Przeklęty żołnierz",
        "max_hp": 4 + world_level * 2,
        "armor_class": 12,
        "attack_bonus": 1,
        "wounds": 1,
        "can_escape": False,
        "image": "przeklety_rycerz",
        "return_action": QUEST_PLACE_ACTION,
    }


def begin_cursed_soldier_combat(player, action_already_paid=False, reason=""):
    quest = base.find_player_quest(player, include_history=False)
    if not quest or quest.get("status") != "active" or int(quest.get("stage_number", 0) or 0) != 3:
        return False, "Walkę można rozpocząć wyłącznie w trzecim etapie questa."
    if is_combat_active():
        return False, "Inna walka jest już aktywna."

    token = base._token(player)
    if token is None:
        return False, "Nie znaleziono pionka bohatera."
    if not action_already_paid:
        if int(getattr(token, "actions", 0) or 0) < 1:
            quest["last_result"] = "Brak akcji. Rozpoczęcie walki kosztuje 1 akcję."
            return False, quest["last_result"]
        token.actions = max(0, token.actions - 1)

    quest["status"] = "combat"
    quest["difficulty_modifier"] = 0
    quest["combat"] = None

    def on_victory(combat_log):
        base._complete_quest(player, quest, f"{combat_log} Klątwa zostaje złamana.")

    def on_defeat(combat_log):
        player["wounds"] = 0
        if getattr(token, "start_tile", None) is not None:
            token.tile = token.start_tile
        base._fail_quest(
            player,
            quest,
            f"{combat_log} Bohater zostaje pokonany, wraca na pole startowe i traci szansę na nagrodę.",
        )

    intro = reason or (
        "Z ołtarza podnosi się Przeklęty żołnierz. Bohater atakuje pierwszy, "
        "a ucieczka z katakumb jest niemożliwa."
    )
    started, message = start_combat(
        player,
        _enemy_data(),
        on_victory=on_victory,
        on_defeat=on_defeat,
        intro_text=intro,
    )
    if not started:
        quest["status"] = "active"
        if not action_already_paid:
            token.actions += 1
        return False, message
    quest["last_result"] = message
    return True, message


def resolve_final_option(player, option_index, rng=None):
    if option_index == 2:
        return begin_cursed_soldier_combat(player)

    result = base.resolve_test(player, option_index, rng=rng)
    quest = base.find_player_quest(player, include_history=False)
    if quest and quest.get("status") == "combat":
        reason = quest.get("last_result", "Nieudany finałowy test budzi Przeklętego żołnierza.")
        quest["status"] = "active"
        quest["combat"] = None
        started, message = begin_cursed_soldier_combat(
            player,
            action_already_paid=True,
            reason=reason.replace("Odkrytym kultystą", "Przeklętym żołnierzem"),
        )
        return False, message if started else result[1]
    return result


def draw_quest_panel(screen, font, small_font, mouse_pos, content, player):
    quest = base.find_player_quest(player, include_history=True)
    if not quest or quest.get("status") != "active" or int(quest.get("stage_number", 0) or 0) != 3:
        return base.draw_quest_panel(screen, font, small_font, mouse_pos, content, player)

    buttons = []
    card = content.inflate(-36, -36)
    pygame.draw.rect(screen, (13, 11, 10), card, border_radius=16)
    pygame.draw.rect(screen, GOLD, card, 2, border_radius=16)

    image_rect = pygame.Rect(card.x + 14, card.y + 14, int(card.width * 0.40), card.height - 28)
    base._draw_cover_image(screen, image_rect)
    pygame.draw.rect(screen, GOLD, image_rect, 2, border_radius=10)

    right = pygame.Rect(image_rect.right + 22, card.y + 16, card.right - image_rect.right - 38, card.height - 32)
    title_font = pygame.font.SysFont("georgia", max(24, font.get_height() + 8), bold=True)
    screen.blit(title_font.render(QUEST_NAME, True, (235, 196, 120)), (right.x, right.y))
    screen.blit(small_font.render(f"Talia Nauki | {base._failure_text(quest)}", True, MUTED), (right.x, right.y + 42))

    screen.blit(font.render("Etap 3/3 — Koniec rytuału", True, TEXT), (right.x, right.y + 82))
    stage_text = (
        "Litery odrywają się od kart księgi. Z cienia wyłania się Przeklęty żołnierz, "
        "ostatni strażnik dawnego kultu. Możesz zakończyć rytuał wiedzą, podstępem albo mieczem."
    )
    draw_lines(screen, small_font, wrap(small_font, stage_text, right.width)[:5], right.x, right.y + 118, MUTED, line_h=21)

    modifier = int(quest.get("difficulty_modifier", 0) or 0)
    if modifier:
        screen.blit(small_font.render(f"Następny test: próg +{modifier}", True, (235, 154, 92)), (right.x, right.y + 226))
    token = base._token(player)
    actions = int(getattr(token, "actions", 0) or 0) if token is not None else 0
    screen.blit(small_font.render(f"Dostępne akcje: {actions} | Każda opcja kosztuje 1 akcję", True, TEXT), (right.x, right.y + 252))

    options = [
        (f"Nauka {10 + modifier}: Zniszcz księgę na dziedzińcu", 0),
        (f"Intryga {13 + modifier}: Przekonaj kapitana, że księga przepadła", 1),
        ("WALKA: Stań do walki z Przeklętym żołnierzem", 2),
    ]
    button_y = right.y + 286
    button_h = 44
    for row, (label, option_index) in enumerate(options):
        rect = pygame.Rect(right.x, button_y + row * (button_h + 8), right.width, button_h)
        button = base.QuestActionButton(
            label,
            rect,
            lambda selected=option_index: resolve_final_option(player, selected),
            enabled=actions >= 1,
        )
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)

    result_y = button_y + len(options) * (button_h + 8) + 6
    result_h = max(74, right.bottom - result_y)
    base._draw_result_box(
        screen,
        small_font,
        pygame.Rect(right.x, result_y, right.width, result_h),
        quest.get("last_result", ""),
    )
    return buttons
