import random
import unicodedata
from pathlib import Path

import pygame

from rg_data import GOLD, MAX_WOUNDS, MUTED, PANEL, TEXT
from rg_ui import Button, draw_lines, draw_panel, wrap

ROOT_DIR = Path(__file__).resolve().parent
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
_ACTIVE_COMBAT = None
_IMAGE_CACHE = {}
_SCALED_CACHE = {}


class CombatActionButton(Button):
    def __init__(self, text, rect, callback, action="combat_attack"):
        super().__init__(text, action, rect)
        self.callback = callback

    def clicked(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        self.callback()
        return True


def _normalize(value):
    text = unicodedata.normalize("NFKD", str(value))
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    return "".join(ch for ch in ascii_text if ch.isalnum())


def _equipped_weapon(player):
    equipment = player.get("equipment")
    if not isinstance(equipment, dict):
        return None
    for key in ("weapon", "bron", "Broń"):
        weapon = equipment.get(key)
        if weapon:
            return weapon
    return None


def weapon_bonuses(player):
    weapon = _equipped_weapon(player)
    if not isinstance(weapon, dict):
        return 0, 0
    return int(weapon.get("hit_bonus", 0) or 0), int(weapon.get("damage_bonus", 0) or 0)


def hero_armor_class(player):
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


def start_combat(player, enemy, on_victory=None, on_defeat=None, intro_text=""):
    global _ACTIVE_COMBAT
    if _ACTIVE_COMBAT is not None:
        return False, "Inna walka jest już aktywna."

    enemy_state = dict(enemy)
    max_hp = int(enemy_state.get("max_hp", enemy_state.get("hp", 1)) or 1)
    enemy_state["max_hp"] = max_hp
    enemy_state["hp"] = max_hp
    enemy_state.setdefault("armor_class", 10)
    enemy_state.setdefault("attack_bonus", 0)
    enemy_state.setdefault("wounds", 1)
    enemy_state.setdefault("image", "")
    enemy_state.setdefault("can_escape", False)

    _ACTIVE_COMBAT = {
        "player": player,
        "enemy": enemy_state,
        "round": 0,
        "last_log": intro_text or f"Rozpoczyna się walka z przeciwnikiem: {enemy_state.get('name', 'Przeciwnik')}.",
        "on_victory": on_victory,
        "on_defeat": on_defeat,
    }
    return True, _ACTIVE_COMBAT["last_log"]


def get_active_combat():
    return _ACTIVE_COMBAT


def is_combat_active():
    return _ACTIVE_COMBAT is not None


def clear_combat():
    global _ACTIVE_COMBAT
    _ACTIVE_COMBAT = None


def resolve_combat_round(rng=None):
    global _ACTIVE_COMBAT
    rng = rng or random
    combat = _ACTIVE_COMBAT
    if combat is None:
        return "inactive", "Walka nie jest aktywna."

    player = combat["player"]
    enemy = combat["enemy"]
    combat["round"] += 1

    hit_bonus, damage_bonus = weapon_bonuses(player)
    hero_roll = int(rng.randint(1, 20))
    hero_total = hero_roll + int(player.get("stats", {}).get("Walka", 0) or 0) + hit_bonus
    if hero_roll == 1:
        hero_hits = 0
    elif hero_roll == 20:
        hero_hits = 2
    else:
        hero_hits = 1 if hero_total >= int(enemy.get("armor_class", 10) or 10) else 0
    hero_damage = hero_hits * (1 + damage_bonus)
    enemy["hp"] = max(0, int(enemy.get("hp", 0) or 0) - hero_damage)

    log = [
        f"Runda {combat['round']}: bohater rzuca {hero_roll}, wynik {hero_total}; "
        f"zadaje {hero_damage} obrażeń."
    ]

    if enemy["hp"] <= 0:
        message = " ".join(log + [f"{enemy.get('name', 'Przeciwnik')} zostaje pokonany."])
        callback = combat.get("on_victory")
        _ACTIVE_COMBAT = None
        if callback:
            callback(message)
        return "victory", message

    enemy_roll = int(rng.randint(1, 20))
    enemy_total = enemy_roll + int(enemy.get("attack_bonus", 0) or 0)
    if enemy_roll == 1:
        enemy_hits = 0
    elif enemy_roll == 20:
        enemy_hits = 2
    else:
        enemy_hits = 1 if enemy_total >= hero_armor_class(player) else 0
    wounds = enemy_hits * int(enemy.get("wounds", 1) or 1)
    player["wounds"] = min(MAX_WOUNDS, int(player.get("wounds", 0) or 0) + wounds)
    log.append(
        f"{enemy.get('name', 'Przeciwnik')} rzuca {enemy_roll}, wynik {enemy_total}; "
        f"zadaje {wounds} Ran."
    )
    message = " ".join(log)

    if player["wounds"] >= MAX_WOUNDS:
        callback = combat.get("on_defeat")
        _ACTIVE_COMBAT = None
        if callback:
            callback(message)
        return "defeat", message

    combat["last_log"] = message
    return "ongoing", message


def _find_image(image_name):
    target = _normalize(image_name)
    if target in _IMAGE_CACHE:
        return _IMAGE_CACHE[target]
    if not target:
        _IMAGE_CACHE[target] = None
        return None

    roots = [ROOT_DIR / "Grafiki", ROOT_DIR]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _IMAGE_EXTENSIONS:
                continue
            if target not in _normalize(path.stem):
                continue
            try:
                image = pygame.image.load(str(path)).convert_alpha()
            except (OSError, pygame.error):
                image = None
            _IMAGE_CACHE[target] = image
            return image
    _IMAGE_CACHE[target] = None
    return None


def _draw_cover(screen, rect, image_name):
    image = _find_image(image_name)
    if image is None:
        pygame.draw.rect(screen, (17, 14, 13), rect, border_radius=14)
        pygame.draw.circle(screen, (93, 51, 45), rect.center, max(30, rect.height // 4), 4)
        fallback_font = pygame.font.SysFont("georgia", max(22, rect.height // 18), bold=True)
        label = fallback_font.render("Przeklęty żołnierz", True, (225, 190, 120))
        screen.blit(label, label.get_rect(center=rect.center))
        return

    key = (_normalize(image_name), rect.width, rect.height)
    scaled = _SCALED_CACHE.get(key)
    if scaled is None:
        iw, ih = image.get_size()
        scale = max(rect.width / iw, rect.height / ih)
        size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        large = pygame.transform.smoothscale(image, size)
        crop = pygame.Rect(
            max(0, (large.get_width() - rect.width) // 2),
            max(0, (large.get_height() - rect.height) // 2),
            rect.width,
            rect.height,
        )
        scaled = large.subsurface(crop).copy()
        _SCALED_CACHE[key] = scaled
    screen.blit(scaled, rect.topleft)
    shade = pygame.Surface(rect.size, pygame.SRCALPHA)
    shade.fill((0, 0, 0, 36))
    screen.blit(shade, rect.topleft)


def _draw_hp_bar(screen, rect, current, maximum):
    maximum = max(1, int(maximum or 1))
    current = max(0, min(maximum, int(current or 0)))
    pygame.draw.rect(screen, (45, 24, 23), rect, border_radius=8)
    fill = rect.copy()
    fill.width = int(rect.width * current / maximum)
    if fill.width > 0:
        pygame.draw.rect(screen, (137, 45, 39), fill, border_radius=8)
    pygame.draw.rect(screen, (205, 151, 74), rect, 2, border_radius=8)


def draw_combat_screen(screen, title_font, font, small_font, mouse_pos):
    combat = _ACTIVE_COMBAT
    if combat is None:
        screen.fill((12, 11, 10))
        return []

    player = combat["player"]
    enemy = combat["enemy"]
    screen.fill((12, 10, 9))

    sw, sh = screen.get_size()
    margin = max(24, int(min(sw, sh) * 0.035))
    arena = pygame.Rect(margin, margin, sw - margin * 2, sh - margin * 2)
    draw_panel(screen, arena, GOLD)

    image_rect = pygame.Rect(arena.x + 18, arena.y + 18, int(arena.width * 0.57), arena.height - 36)
    _draw_cover(screen, image_rect, enemy.get("image", "przeklety_rycerz"))
    pygame.draw.rect(screen, GOLD, image_rect, 2, border_radius=14)

    panel = pygame.Rect(image_rect.right + 22, arena.y + 22, arena.right - image_rect.right - 44, arena.height - 44)
    pygame.draw.rect(screen, PANEL, panel, border_radius=14)
    pygame.draw.rect(screen, GOLD, panel, 2, border_radius=14)

    name = enemy.get("name", "Przeciwnik")
    screen.blit(title_font.render(name, True, (235, 196, 120)), (panel.x + 24, panel.y + 22))
    screen.blit(small_font.render("Finałowa walka questa: Szatańskie siły", True, MUTED), (panel.x + 26, panel.y + 78))

    hp_bar = pygame.Rect(panel.x + 24, panel.y + 116, panel.width - 48, 28)
    _draw_hp_bar(screen, hp_bar, enemy.get("hp", 0), enemy.get("max_hp", 1))
    hp_label = font.render(f"HP {enemy.get('hp', 0)}/{enemy.get('max_hp', 0)}", True, TEXT)
    screen.blit(hp_label, hp_label.get_rect(center=hp_bar.center))

    enemy_stats = (
        f"KP {enemy.get('armor_class', 10)} | Atak +{enemy.get('attack_bonus', 0)} | "
        f"Obrażenia: {enemy.get('wounds', 1)} Rana"
    )
    screen.blit(small_font.render(enemy_stats, True, MUTED), (panel.x + 24, panel.y + 164))

    hero_y = panel.y + 218
    screen.blit(font.render(player.get("name", "Bohater"), True, TEXT), (panel.x + 24, hero_y))
    hit_bonus, damage_bonus = weapon_bonuses(player)
    hero_stats = (
        f"Walka {player.get('stats', {}).get('Walka', 0)} | KP {hero_armor_class(player)} | "
        f"Rany {player.get('wounds', 0)}/{MAX_WOUNDS}"
    )
    screen.blit(small_font.render(hero_stats, True, MUTED), (panel.x + 24, hero_y + 38))
    weapon_text = f"Broń: +{hit_bonus} do trafienia, +{damage_bonus} do obrażeń"
    screen.blit(small_font.render(weapon_text, True, MUTED), (panel.x + 24, hero_y + 68))

    log_rect = pygame.Rect(panel.x + 24, panel.y + 336, panel.width - 48, max(110, panel.height - 470))
    pygame.draw.rect(screen, (25, 23, 21), log_rect, border_radius=10)
    pygame.draw.rect(screen, (91, 75, 51), log_rect, 1, border_radius=10)
    lines = wrap(small_font, combat.get("last_log", ""), log_rect.width - 24)[:6]
    draw_lines(screen, small_font, lines, log_rect.x + 12, log_rect.y + 12, TEXT, line_h=small_font.get_height() + 4)

    attack_rect = pygame.Rect(panel.x + 24, panel.bottom - 94, panel.width - 48, 54)
    button = CombatActionButton(
        "ATAKUJ",
        attack_rect,
        resolve_combat_round,
        action=enemy.get("return_action", "combat_attack"),
    )
    button.draw(screen, font, mouse_pos)
    no_escape = small_font.render("Ucieczka jest niemożliwa", True, (205, 123, 105))
    screen.blit(no_escape, no_escape.get_rect(midbottom=(panel.centerx, attack_rect.y - 10)))
    return [button]
