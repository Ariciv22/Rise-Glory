import copy
import random
import unicodedata
from pathlib import Path

import pygame

from rg_data import GOLD, MAX_WOUNDS, MUTED, TEXT
from rg_ui import Button, draw_lines, wrap

QUEST_ID = "klatwa_katakumb_0"
QUEST_NAME = "Szatańskie siły"
QUEST_PLACE_ACTION = "location_quest_klatwa_katakumb_0"
ARTIUM_NAME = "Artium"
ROOT_DIR = Path(__file__).resolve().parent
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
_IMAGE_TARGET = "uczonywkatakumbach"
_IMAGE_SOURCE = None
_IMAGE_SEARCHED = False
_SCALED_IMAGE_CACHE = {}
_REGISTERED_PLAYERS = []

STAGES = {
    1: {
        "title": "Ołtarz w katakumbach",
        "text": (
            "Lampa oświetla zawiłe korytarze. Po długiej wędrówce odnajdujesz "
            "ołtarzyk pokryty czerwonymi runami. Musisz wybrać sposób zbadania miejsca."
        ),
        "options": [
            {"stat": "Nauka", "threshold": 11, "label": "Przeszukaj bezpiecznie bibliotekę"},
            {"stat": "Intryga", "threshold": 14, "label": "Zbadaj czerwone znaki na ołtarzu"},
            {
                "stat": "Kultura",
                "threshold": 13,
                "label": "Wykonaj podstawowy obrzęd",
                "materials": {"Skóra": 2},
            },
        ],
    },
    2: {
        "title": "Ślady dawnego kultu",
        "text": (
            "W pradawnej bibliotece łączysz fakty. Dawny kult pozostawił miejsce "
            "rytualne splamione krwią niewinnych. Czas rozproszyć jego magię."
        ),
        "options": [
            {"stat": "Nauka", "threshold": 13, "label": "Wypowiedz słowa kończące rytuał"},
            {"stat": "Intryga", "threshold": 15, "label": "Zabierz księgę i ukryj prawdę"},
            {"stat": "Kultura", "threshold": 14, "label": "Odczytaj rozdział o mocach nadprzyrodzonych"},
        ],
    },
    3: {
        "title": "Koniec rytuału",
        "text": (
            "Litery odrywają się od kart księgi i splatają w zaklęcie, które "
            "uspokaja demoniczny ołtarz. Pozostaje przekonać kapitana, że zagrożenie minęło."
        ),
        "options": [
            {"stat": "Nauka", "threshold": 10, "label": "Zniszcz księgę na dziedzińcu"},
            {"stat": "Intryga", "threshold": 13, "label": "Przekonaj kapitana, że księga przepadła"},
        ],
    },
}

QUEST_TEMPLATE = {
    "id": QUEST_ID,
    "name": QUEST_NAME,
    "deck": "Nauki",
    "description": "Śmiałek, który odegna światła i inne dziwy, hojnie zostanie wynagrodzony.",
    "objective": "Dotrzyj do Zamku Artium i zbadaj katakumby.",
    "required_location": ARTIUM_NAME,
    "world_level_min": 1,
    "stage_number": 1,
    "stage": "1/3",
    "failures": 0,
    "difficulty_modifier": 0,
    "status": "offer",
    "last_result": "",
    "reward": {"gold": 8, "legend": 2, "food": 3, "item": "Krótki miecz"},
}

SHORT_SWORD = {
    "id": "krotki_miecz_kapitana",
    "name": "Krótki miecz",
    "category": "weapon",
    "quality": "zwykła",
    "hit_bonus": 1,
    "damage_bonus": 1,
    "price": 6,
    "description": "+1 do rzutu na trafienie i +1 do obrażeń po założeniu.",
}


class QuestActionButton(Button):
    def __init__(self, text, rect, callback, enabled=True):
        super().__init__(text, QUEST_PLACE_ACTION, rect)
        self.callback = callback
        self.enabled = enabled

    def draw(self, screen, font, mouse_pos, active=False):
        if self.enabled:
            super().draw(screen, font, mouse_pos, active=active)
            return
        pygame.draw.rect(screen, (35, 32, 28), self.rect, border_radius=8)
        pygame.draw.rect(screen, (85, 72, 54), self.rect, 1, border_radius=8)
        label = font.render(self.text, True, (120, 116, 108))
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        if self.callback:
            self.callback()
        return True


def register_players(players):
    global _REGISTERED_PLAYERS
    _REGISTERED_PLAYERS = list(players or [])


def current_world_level():
    leader_legend = max((int(player.get("legend", 0) or 0) for player in _REGISTERED_PLAYERS), default=0)
    if leader_legend >= 30:
        return 4
    if leader_legend >= 20:
        return 3
    if leader_legend >= 10:
        return 2
    return 1


def create_quest_offer():
    return copy.deepcopy(QUEST_TEMPLATE)


def activate_quest(card=None):
    quest = copy.deepcopy(card or QUEST_TEMPLATE)
    quest.update({
        "status": "active",
        "stage_number": 1,
        "stage": "1/3",
        "failures": 0,
        "difficulty_modifier": 0,
        "objective": "W Zamku Artium otwórz zakładkę questa i wykonaj pierwszy etap.",
        "last_result": "Quest pobrany. Udaj się do Zamku Artium.",
        "combat": None,
    })
    return quest


def is_satanic_forces(quest):
    return isinstance(quest, dict) and quest.get("id") == QUEST_ID


def find_player_quest(player, include_history=True):
    for quest in player.get("active_quests", []) or []:
        if is_satanic_forces(quest):
            return quest
    if include_history:
        for key in ("completed_quests", "failed_quests"):
            for quest in player.get(key, []) or []:
                if is_satanic_forces(quest):
                    return quest
    return None


def has_active_quest(player):
    quest = find_player_quest(player, include_history=False)
    return bool(quest and quest.get("status") in {"active", "combat"})


def _normalize(value):
    text = unicodedata.normalize("NFKD", str(value))
    return "".join(ch for ch in text.encode("ascii", "ignore").decode("ascii").lower() if ch.isalnum())


def _material_count(player, requested_name):
    target = _normalize(requested_name)
    accepted = {target, "skora", "skory"}
    materials = player.get("materials", {})
    if isinstance(materials, dict):
        return sum(int(amount or 0) for name, amount in materials.items() if _normalize(name) in accepted)
    if isinstance(materials, (list, tuple)):
        return sum(1 for item in materials if _normalize(item) in accepted)
    return 0


def _consume_material(player, requested_name, amount):
    if _material_count(player, requested_name) < amount:
        return False
    materials = player.get("materials", {})
    accepted = {_normalize(requested_name), "skora", "skory"}
    if isinstance(materials, dict):
        remaining = amount
        for name in list(materials):
            if _normalize(name) not in accepted:
                continue
            take = min(remaining, int(materials[name] or 0))
            materials[name] -= take
            remaining -= take
            if materials[name] <= 0:
                del materials[name]
            if remaining <= 0:
                break
        return remaining <= 0
    if isinstance(materials, list):
        remaining = amount
        for index in range(len(materials) - 1, -1, -1):
            if _normalize(materials[index]) in accepted:
                materials.pop(index)
                remaining -= 1
                if remaining <= 0:
                    break
        return remaining <= 0
    return False


def _single_helper_bonus(player, stat):
    return max((int(helper.get("stat_bonus", {}).get(stat, 0) or 0) for helper in player.get("helpers", []) or []), default=0)


def _token(player):
    return player.get("_token_ref")


def _remove_active_quest(player, quest):
    active = player.setdefault("active_quests", [])
    for index, candidate in enumerate(list(active)):
        if candidate is quest or is_satanic_forces(candidate):
            active.pop(index)
            return


def _complete_quest(player, quest, note=""):
    failures = int(quest.get("failures", 0) or 0)
    gold_reward = max(0, 8 - failures * 2)
    player["gold"] = int(player.get("gold", 0) or 0) + gold_reward
    player["legend"] = int(player.get("legend", 0) or 0) + 2
    player.setdefault("inventory", []).append(copy.deepcopy(SHORT_SWORD))
    player.setdefault("food", []).extend(["Suszone mieso"] * 3)
    quest["status"] = "completed"
    quest["stage"] = "Ukończony"
    quest["objective"] = "Quest ukończony."
    quest["last_result"] = (f"{note} Otrzymujesz {gold_reward} złota, 2 Punkty Legendy, Krótki miecz i 3 paczki suszonego mięsa.").strip()
    _remove_active_quest(player, quest)
    player.setdefault("completed_quests", []).append(quest)
    return quest["last_result"]


def _fail_quest(player, quest, note):
    quest["status"] = "failed"
    quest["stage"] = "Przegrany"
    quest["objective"] = "Quest przegrany."
    quest["last_result"] = note
    _remove_active_quest(player, quest)
    player.setdefault("failed_quests", []).append(quest)
    return note


def _advance_after_success(player, quest, roll):
    stage = int(quest.get("stage_number", 1) or 1)
    if stage >= 3:
        return _complete_quest(player, quest, "Rytuał zostaje zakończony.")
    next_stage = stage + 1
    skipped = False
    if roll == 20 and next_stage < 3:
        next_stage += 1
        skipped = True
    elif roll == 20 and next_stage == 3:
        return _complete_quest(player, quest, "Naturalne 20 zalicza również finałowy test.")
    quest["stage_number"] = next_stage
    quest["stage"] = f"{next_stage}/3"
    quest["objective"] = f"Wykonaj etap {next_stage} w Zamku Artium."
    if roll == 1:
        quest["difficulty_modifier"] = 2
    quest["last_result"] = (
        f"Sukces. Naturalne 20 zalicza także następny etap. Przechodzisz do etapu {next_stage}."
        if skipped else f"Sukces. Przechodzisz do etapu {next_stage}."
    )
    return quest["last_result"]


def resolve_test(player, option_index, rng=None):
    rng = rng or random
    quest = find_player_quest(player, include_history=False)
    if not quest or quest.get("status") != "active":
        return False, "Nie masz aktywnego etapu tego questa."
    token = _token(player)
    if token is None:
        return False, "Nie znaleziono pionka bohatera."
    if int(getattr(token, "actions", 0) or 0) < 1:
        quest["last_result"] = "Brak akcji. Każdy test kosztuje 1 akcję."
        return False, quest["last_result"]
    stage_number = int(quest.get("stage_number", 1) or 1)
    stage = STAGES.get(stage_number)
    if not stage or option_index < 0 or option_index >= len(stage["options"]):
        quest["last_result"] = "Nieprawidłowy wariant testu."
        return False, quest["last_result"]
    option = stage["options"][option_index]
    for material, amount in option.get("materials", {}).items():
        if _material_count(player, material) < amount:
            quest["last_result"] = f"Ten wariant wymaga {amount} szt. materiału: {material}."
            return False, quest["last_result"]
    for material, amount in option.get("materials", {}).items():
        _consume_material(player, material, amount)
    token.actions = max(0, token.actions - 1)
    modifier = int(quest.get("difficulty_modifier", 0) or 0)
    quest["difficulty_modifier"] = 0
    threshold = int(option["threshold"]) + modifier
    roll = int(rng.randint(1, 20))
    stat = option["stat"]
    stat_value = int(player.get("stats", {}).get(stat, 0) or 0)
    helper_bonus = _single_helper_bonus(player, stat)
    total = roll + stat_value + helper_bonus
    success = roll == 20 or total >= threshold
    details = f"Rzut {roll} + {stat} {stat_value} + pomocnik {helper_bonus} = {total} przeciw {threshold}."
    if success:
        result = _advance_after_success(player, quest, roll)
        quest["last_result"] = f"{details} {result}"
        return True, quest["last_result"]
    quest["failures"] = int(quest.get("failures", 0) or 0) + 1
    if quest["failures"] >= 4:
        return False, _fail_quest(player, quest, f"{details} Czwarty znacznik porażki. Quest przegrany.")
    quest["difficulty_modifier"] = 2 if roll == 1 else 1
    if stage_number == 3:
        level = current_world_level()
        quest["status"] = "combat"
        quest["combat"] = {
            "enemy_name": "Odkryty kultysta",
            "enemy_hp": 4 + level * 2,
            "enemy_max_hp": 4 + level * 2,
            "enemy_ac": 11,
            "enemy_attack_bonus": 0,
            "enemy_wounds": 1,
            "action_paid": False,
            "round": 0,
        }
        quest["last_result"] = f"{details} Porażka uruchamia walkę z Odkrytym kultystą."
        return False, quest["last_result"]
    quest["last_result"] = f"{details} Porażka. Dodano znacznik porażki. Następny test ma próg wyższy o {quest['difficulty_modifier']}."
    return False, quest["last_result"]


def _equipped_weapon(player):
    equipment = player.get("equipment")
    if isinstance(equipment, dict):
        for key in ("weapon", "bron", "Broń"):
            if equipment.get(key):
                return equipment[key]
    return None


def _weapon_bonuses(player):
    weapon = _equipped_weapon(player)
    if isinstance(weapon, dict):
        return int(weapon.get("hit_bonus", 0) or 0), int(weapon.get("damage_bonus", 0) or 0)
    return 0, 0


def _hero_ac(player):
    equipment = player.get("equipment")
    if isinstance(equipment, dict):
        armor = equipment.get("armor") or equipment.get("pancerz") or equipment.get("Pancerz")
        if isinstance(armor, dict):
            return int(armor.get("armor_class", armor.get("ac", 12)) or 12)
        if armor:
            return 12
    class_item = _normalize(player.get("class_item", ""))
    if "zbroja" in class_item or "pancerz" in class_item:
        return 12
    return 10


def resolve_combat_round(player, rng=None):
    rng = rng or random
    quest = find_player_quest(player, include_history=False)
    if not quest or quest.get("status") != "combat" or not quest.get("combat"):
        return False, "Walka nie jest aktywna."
    token = _token(player)
    combat = quest["combat"]
    if not combat.get("action_paid"):
        if token is None or int(getattr(token, "actions", 0) or 0) < 1:
            quest["last_result"] = "Rozpoczęcie całej walki kosztuje 1 akcję."
            return False, quest["last_result"]
        token.actions = max(0, token.actions - 1)
        combat["action_paid"] = True
    combat["round"] = int(combat.get("round", 0) or 0) + 1
    hit_bonus, damage_bonus = _weapon_bonuses(player)
    hero_roll = int(rng.randint(1, 20))
    hero_total = hero_roll + int(player.get("stats", {}).get("Walka", 0) or 0) + hit_bonus
    hero_hits = 0 if hero_roll == 1 else (2 if hero_roll == 20 else (1 if hero_total >= combat["enemy_ac"] else 0))
    hero_damage = hero_hits * (1 + damage_bonus)
    combat["enemy_hp"] = max(0, int(combat["enemy_hp"]) - hero_damage)
    log = [f"Runda {combat['round']}: bohater rzuca {hero_roll}, wynik {hero_total}; zadaje {hero_damage} obrażeń."]
    if combat["enemy_hp"] <= 0:
        result = _complete_quest(player, quest, "Odkryty kultysta zostaje pokonany.")
        return True, " ".join(log + [result])
    enemy_roll = int(rng.randint(1, 20))
    enemy_total = enemy_roll + int(combat.get("enemy_attack_bonus", 0) or 0)
    enemy_hits = 0 if enemy_roll == 1 else (2 if enemy_roll == 20 else (1 if enemy_total >= _hero_ac(player) else 0))
    wounds = enemy_hits * int(combat.get("enemy_wounds", 1) or 1)
    player["wounds"] = min(MAX_WOUNDS, int(player.get("wounds", 0) or 0) + wounds)
    log.append(f"Kultysta rzuca {enemy_roll}, wynik {enemy_total}; zadaje {wounds} Ran.")
    if player["wounds"] >= MAX_WOUNDS:
        level = current_world_level()
        player["gold"] = max(0, int(player.get("gold", 0) or 0) - level)
        player["wounds"] = 0
        if token is not None and getattr(token, "start_tile", None) is not None:
            token.tile = token.start_tile
        result = _fail_quest(player, quest, "Bohater zostaje pokonany i wraca na pole startowe. Quest przegrany.")
        return False, " ".join(log + [result])
    quest["last_result"] = " ".join(log)
    return False, quest["last_result"]


def _find_image_path():
    global _IMAGE_SEARCHED, _IMAGE_SOURCE
    if _IMAGE_SEARCHED:
        return _IMAGE_SOURCE
    _IMAGE_SEARCHED = True
    likely = [
        ROOT_DIR / "Grafiki" / "uczony w katakumbach.png",
        ROOT_DIR / "Grafiki" / "questy" / "uczony w katakumbach.png",
        ROOT_DIR / "uczony w katakumbach.png",
    ]
    for path in likely:
        if path.is_file():
            _IMAGE_SOURCE = path
            return path
    for root in (ROOT_DIR / "Grafiki", ROOT_DIR):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in _IMAGE_EXTENSIONS and _IMAGE_TARGET in _normalize(path.stem):
                _IMAGE_SOURCE = path
                return path
    return None


def _load_image():
    path = _find_image_path()
    if not path:
        return None
    try:
        return pygame.image.load(str(path)).convert_alpha()
    except (OSError, pygame.error):
        return None


def _draw_cover_image(screen, rect):
    source = _load_image()
    if source is None:
        pygame.draw.rect(screen, (22, 18, 16), rect, border_radius=10)
        for index in range(8):
            radius = max(8, int(rect.height * (0.42 - index * 0.035)))
            pygame.draw.circle(screen, (44 + index * 4, 27, 23), rect.center, radius, 2)
        fallback_font = pygame.font.SysFont("georgia", max(14, rect.height // 18), bold=True)
        label = fallback_font.render("Katakumby Artium", True, (210, 175, 108))
        screen.blit(label, label.get_rect(center=rect.center))
        return
    key = (rect.width, rect.height)
    scaled = _SCALED_IMAGE_CACHE.get(key)
    if scaled is None:
        iw, ih = source.get_size()
        scale = max(rect.width / iw, rect.height / ih)
        size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        large = pygame.transform.smoothscale(source, size)
        crop = pygame.Rect((large.get_width() - rect.width) // 2, (large.get_height() - rect.height) // 2, rect.width, rect.height)
        scaled = large.subsurface(crop).copy()
        _SCALED_IMAGE_CACHE[key] = scaled
    screen.blit(scaled, rect.topleft)
    shade = pygame.Surface(rect.size, pygame.SRCALPHA)
    shade.fill((0, 0, 0, 42))
    screen.blit(shade, rect.topleft)


def _failure_text(quest):
    failures = int(quest.get("failures", 0) or 0)
    return "Porażki: " + " ".join("●" if i < failures else "○" for i in range(4))


def _draw_result_box(screen, small_font, rect, text):
    if not text:
        return
    pygame.draw.rect(screen, (28, 31, 28), rect, border_radius=8)
    pygame.draw.rect(screen, (90, 100, 82), rect, 1, border_radius=8)
    lines = wrap(small_font, text, rect.width - 20)[:3]
    draw_lines(screen, small_font, lines, rect.x + 10, rect.y + 8, TEXT, line_h=small_font.get_height() + 2)


def draw_quest_panel(screen, font, small_font, mouse_pos, content, player):
    quest = find_player_quest(player, include_history=True)
    buttons = []
    card = content.inflate(-36, -36)
    pygame.draw.rect(screen, (13, 11, 10), card, border_radius=16)
    pygame.draw.rect(screen, GOLD, card, 2, border_radius=16)
    if quest is None:
        draw_lines(screen, font, ["Nie posiadasz questa Szatańskie siły."], card.x + 24, card.y + 24, MUTED)
        return buttons
    image_rect = pygame.Rect(card.x + 14, card.y + 14, int(card.width * 0.40), card.height - 28)
    _draw_cover_image(screen, image_rect)
    pygame.draw.rect(screen, GOLD, image_rect, 2, border_radius=10)
    right = pygame.Rect(image_rect.right + 22, card.y + 16, card.right - image_rect.right - 38, card.height - 32)
    title_font = pygame.font.SysFont("georgia", max(24, font.get_height() + 8), bold=True)
    screen.blit(title_font.render(QUEST_NAME, True, (235, 196, 120)), (right.x, right.y))
    screen.blit(small_font.render(f"Talia Nauki | {_failure_text(quest)}", True, MUTED), (right.x, right.y + 42))
    status = quest.get("status")
    if status == "completed":
        draw_lines(screen, font, ["QUEST UKOŃCZONY"], right.x, right.y + 88, (180, 220, 130))
        draw_lines(screen, small_font, wrap(small_font, quest.get("last_result", ""), right.width), right.x, right.y + 132, TEXT, line_h=22)
        return buttons
    if status == "failed":
        draw_lines(screen, font, ["QUEST PRZEGRANY"], right.x, right.y + 88, (220, 110, 100))
        draw_lines(screen, small_font, wrap(small_font, quest.get("last_result", ""), right.width), right.x, right.y + 132, TEXT, line_h=22)
        return buttons
    if status == "combat":
        combat = quest.get("combat") or {}
        screen.blit(font.render("Finałowa walka", True, TEXT), (right.x, right.y + 84))
        stats = f"Odkryty kultysta | HP {combat.get('enemy_hp', 0)}/{combat.get('enemy_max_hp', 0)} | KP {combat.get('enemy_ac', 11)} | Atak +0 | 1 Rana"
        draw_lines(screen, small_font, wrap(small_font, stats, right.width), right.x, right.y + 120, MUTED, line_h=21)
        screen.blit(small_font.render(f"Twoje Rany: {player.get('wounds', 0)}/{MAX_WOUNDS}", True, TEXT), (right.x, right.y + 176))
        action_text = "Atakuj — koszt walki: 1 akcja" if not combat.get("action_paid") else "Atakuj — kolejna runda"
        attack_rect = pygame.Rect(right.x, right.y + 218, min(360, right.width), 48)
        button = QuestActionButton(action_text, attack_rect, lambda: resolve_combat_round(player))
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)
        _draw_result_box(screen, small_font, pygame.Rect(right.x, right.bottom - 112, right.width, 100), quest.get("last_result", ""))
        return buttons
    stage_number = int(quest.get("stage_number", 1) or 1)
    stage = STAGES[stage_number]
    screen.blit(font.render(f"Etap {stage_number}/3 — {stage['title']}", True, TEXT), (right.x, right.y + 82))
    draw_lines(screen, small_font, wrap(small_font, stage["text"], right.width)[:5], right.x, right.y + 118, MUTED, line_h=21)
    modifier = int(quest.get("difficulty_modifier", 0) or 0)
    if modifier:
        screen.blit(small_font.render(f"Następny test: próg +{modifier}", True, (235, 154, 92)), (right.x, right.y + 226))
    token = _token(player)
    actions = int(getattr(token, "actions", 0) or 0) if token is not None else 0
    screen.blit(small_font.render(f"Dostępne akcje: {actions} | Każdy test kosztuje 1 akcję", True, TEXT), (right.x, right.y + 252))
    button_y = right.y + 286
    button_h = 44
    for index, option in enumerate(stage["options"]):
        threshold = int(option["threshold"]) + modifier
        label = f"{option['stat']} {threshold}: {option['label']}"
        enabled = actions >= 1
        if option.get("materials"):
            required = next(iter(option["materials"].values()))
            available = _material_count(player, "Skóra")
            label += f" | skóry {available}/{required}"
            enabled = enabled and available >= required
        rect = pygame.Rect(right.x, button_y + index * (button_h + 8), right.width, button_h)
        button = QuestActionButton(label, rect, lambda option_index=index: resolve_test(player, option_index), enabled=enabled)
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)
    result_y = button_y + len(stage["options"]) * (button_h + 8) + 6
    result_h = max(74, right.bottom - result_y)
    _draw_result_box(screen, small_font, pygame.Rect(right.x, result_y, right.width, result_h), quest.get("last_result", ""))
    return buttons
