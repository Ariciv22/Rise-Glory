import random
import unicodedata
from pathlib import Path

import pygame

from rg_core.data import GOLD, MAX_WOUNDS, MUTED, PANEL, TEXT
from rg_engine.combat import attempt_bribe as engine_attempt_bribe
from rg_engine.combat import attempt_escape as engine_attempt_escape
from rg_engine.combat import change_equipment as engine_change_equipment
from rg_engine.combat import clear_combat_statuses
from rg_engine.combat import create_session
from rg_engine.combat import defend as engine_defend
from rg_engine.combat import finalize_victory
from rg_engine.combat import resolve_round as engine_resolve_round
from rg_engine.combat import use_item as engine_use_item
from rg_engine.items import armor_class as engine_armor_class
from rg_engine.items import combat_usable_inventory_indices, eligible_defeat_inventory_indices
from rg_engine.items import equipment_slot_for, item_display_name, normalise_item
from rg_engine.items import weapon_bonuses as engine_weapon_bonuses
from rg_engine.items import weapon_damage as engine_weapon_damage
from rg_ui.common import Button, draw_lines, draw_panel, wrap

ROOT_DIR = Path(__file__).resolve().parents[1]
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
_ACTIVE_COMBAT = None
_IMAGE_CACHE = {}
_SCALED_CACHE = {}


class CombatActionButton(Button):
    def __init__(self, text, rect, callback, action="combat_attack", enabled=True):
        super().__init__(text, action, rect)
        self.callback = callback
        self.enabled = bool(enabled)

    def clicked(self, pos):
        if not self.enabled or not self.rect.collidepoint(pos):
            return False
        self.callback()
        return True

    def draw(self, screen, font, mouse_pos):
        if self.enabled:
            return super().draw(screen, font, mouse_pos)
        pygame.draw.rect(screen, (42, 42, 42), self.rect, border_radius=8)
        pygame.draw.rect(screen, (73, 73, 73), self.rect, 1, border_radius=8)
        label = font.render(self.text, True, MUTED)
        screen.blit(label, label.get_rect(center=self.rect.center))


def _normalize(value):
    text = unicodedata.normalize("NFKD", str(value))
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    return "".join(ch for ch in ascii_text if ch.isalnum())


def weapon_bonuses(player):
    return engine_weapon_bonuses(player)


def hero_armor_class(player):
    return engine_armor_class(player)


def start_combat(player, enemy, on_victory=None, on_defeat=None, on_escape=None, intro_text="", metadata=None):
    global _ACTIVE_COMBAT
    if _ACTIVE_COMBAT is not None:
        return False, "Inna walka jest juz aktywna."
    session = create_session(player, enemy, intro_text=intro_text, metadata=metadata)
    _ACTIVE_COMBAT = {
        "session": session,
        "player": player,
        "enemy": session.enemy,
        "round": 0,
        "last_log": session.last_log,
        "on_victory": on_victory,
        "on_defeat": on_defeat,
        "on_escape": on_escape,
        "phase": "combat",
        "menu": None,
        "victory_summary": None,
        "defeat_choices": [],
    }
    return True, session.last_log


def get_active_combat():
    return _ACTIVE_COMBAT


def is_combat_active():
    return _ACTIVE_COMBAT is not None


def clear_combat():
    global _ACTIVE_COMBAT
    if _ACTIVE_COMBAT is not None:
        clear_combat_statuses(_ACTIVE_COMBAT["session"])
    _ACTIVE_COMBAT = None


def _complete_finish(outcome, message):
    global _ACTIVE_COMBAT
    combat = _ACTIVE_COMBAT
    if combat is None:
        return outcome, message
    callback = {"victory": combat.get("on_victory"), "defeat": combat.get("on_defeat"), "escaped": combat.get("on_escape")}.get(outcome)
    clear_combat_statuses(combat["session"])
    _ACTIVE_COMBAT = None
    if callback:
        callback(message)
    return outcome, message


def _finish_combat(outcome, message):
    combat = _ACTIVE_COMBAT
    if combat is None:
        return outcome, message
    combat["last_log"] = message
    combat["menu"] = None
    if outcome == "victory":
        combat["victory_summary"] = finalize_victory(combat["session"])
        combat["phase"] = "victory"
        return "victory_pending", message
    if outcome == "defeat":
        clear_combat_statuses(combat["session"])
        choices = eligible_defeat_inventory_indices(combat["player"])
        if choices:
            combat["defeat_choices"] = choices
            combat["phase"] = "defeat_choice"
            return "defeat_pending", message
        return _complete_finish("defeat", message)
    if outcome == "escaped":
        return _complete_finish("escaped", message)
    return outcome, message


def _handle_engine_result(result):
    combat = _ACTIVE_COMBAT
    if combat is None:
        return "inactive", "Walka nie jest aktywna."
    combat["round"] = combat["session"].round_number
    combat["last_log"] = result.get("log", "")
    outcome = result.get("outcome", "ongoing")
    if outcome in {"victory", "defeat", "escaped"}:
        return _finish_combat(outcome, combat["last_log"])
    return outcome, combat["last_log"]


def resolve_combat_round(rng=None):
    combat = _ACTIVE_COMBAT
    if combat is None or combat.get("phase") != "combat":
        return "inactive", "Walka nie jest gotowa na atak."
    return _handle_engine_result(engine_resolve_round(combat["session"], rng=rng or random))


def defend(rng=None):
    combat = _ACTIVE_COMBAT
    if combat is None or combat.get("phase") != "combat":
        return "inactive", "Walka nie jest gotowa na Obrone."
    return _handle_engine_result(engine_defend(combat["session"], rng=rng or random))


def attempt_escape(rng=None):
    combat = _ACTIVE_COMBAT
    if combat is None or combat.get("phase") != "combat":
        return "inactive", "Walka nie jest gotowa na ucieczke."
    return _handle_engine_result(engine_attempt_escape(combat["session"], rng=rng or random))


def attempt_bribe(rng=None):
    combat = _ACTIVE_COMBAT
    if combat is None or combat.get("phase") != "combat":
        return "inactive", "Walka nie jest gotowa na przekupstwo."
    return _handle_engine_result(engine_attempt_bribe(combat["session"], rng=rng or random))


def use_combat_item(inventory_index, rng=None):
    combat = _ACTIVE_COMBAT
    if combat is None or combat.get("phase") != "combat":
        return "inactive", "Walka nie jest gotowa na uzycie przedmiotu."
    combat["menu"] = None
    return _handle_engine_result(engine_use_item(combat["session"], int(inventory_index), rng=rng or random))


def change_combat_equipment(inventory_index, rng=None):
    combat = _ACTIVE_COMBAT
    if combat is None or combat.get("phase") != "combat":
        return "inactive", "Walka nie jest gotowa na zmiane ekwipunku."
    combat["menu"] = None
    return _handle_engine_result(engine_change_equipment(combat["session"], int(inventory_index), rng=rng or random))


def toggle_combat_menu(menu_name):
    combat = _ACTIVE_COMBAT
    if combat is not None and combat.get("phase") == "combat":
        combat["menu"] = None if combat.get("menu") == menu_name else menu_name


def confirm_victory():
    combat = _ACTIVE_COMBAT
    if combat is None or combat.get("phase") != "victory":
        return "inactive", "Brak zwyciestwa do zatwierdzenia."
    return _complete_finish("victory", combat.get("last_log", ""))


def choose_defeat_item(choice_position):
    combat = _ACTIVE_COMBAT
    if combat is None or combat.get("phase") != "defeat_choice":
        return "inactive", "Brak kary przedmiotowej do rozpatrzenia."
    choices = list(combat.get("defeat_choices") or [])
    position = int(choice_position)
    if position < 0 or position >= len(choices):
        return "blocked", "Nieprawidlowy wybor karty."
    combat["player"]["_combat_defeat_item_index"] = int(choices[position])
    return _complete_finish("defeat", combat.get("last_log", ""))


def _find_image(image_name):
    target = _normalize(image_name)
    if target in _IMAGE_CACHE:
        return _IMAGE_CACHE[target]
    if not target:
        _IMAGE_CACHE[target] = None
        return None
    for root in (ROOT_DIR / "Grafiki", ROOT_DIR):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _IMAGE_EXTENSIONS or target not in _normalize(path.stem):
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
        label = pygame.font.SysFont("georgia", max(22, rect.height // 18), bold=True).render("Przeciwnik", True, (225, 190, 120))
        screen.blit(label, label.get_rect(center=rect.center))
        return
    key = (_normalize(image_name), rect.width, rect.height)
    scaled = _SCALED_CACHE.get(key)
    if scaled is None:
        iw, ih = image.get_size()
        scale = max(rect.width / iw, rect.height / ih)
        large = pygame.transform.smoothscale(image, (max(1, int(iw * scale)), max(1, int(ih * scale))))
        crop = pygame.Rect(max(0, (large.get_width() - rect.width) // 2), max(0, (large.get_height() - rect.height) // 2), rect.width, rect.height)
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


def _reward_lines(summary):
    lines = []
    if summary.get("gold"):
        lines.append(f"Zloto: +{summary['gold']}")
    if summary.get("legend"):
        lines.append(f"Legenda: +{summary['legend']}")
    for entry in summary.get("items", []) or []:
        lines.append(f"Przedmiot: {entry.get('name', 'Przedmiot')}" + ("" if entry.get("in_backpack") else " (oczekuje - brak miejsca)"))
    if summary.get("goods"):
        lines.append("Towary: " + ", ".join(map(str, summary["goods"])))
    if summary.get("food"):
        lines.append("Jedzenie: " + ", ".join(map(str, summary["food"])))
    for name, amount in (summary.get("materials") or {}).items():
        lines.append(f"{name}: +{amount}")
    return lines or ["Brak dodatkowego lootu z karty przeciwnika."]


def _draw_victory(screen, title_font, font, small_font, mouse_pos):
    combat = _ACTIVE_COMBAT
    sw, sh = screen.get_size()
    card = pygame.Rect(sw // 2 - 390, sh // 2 - 270, 780, 540)
    screen.fill((12, 10, 9))
    draw_panel(screen, card, GOLD)
    title = title_font.render("ZWYCIESTWO", True, (235, 196, 120))
    screen.blit(title, title.get_rect(center=(card.centerx, card.y + 60)))
    defeated = font.render(f"Pokonano: {combat['enemy'].get('name', 'Przeciwnik')}", True, TEXT)
    screen.blit(defeated, defeated.get_rect(center=(card.centerx, card.y + 125)))
    y = card.y + 180
    for line in _reward_lines(combat.get("victory_summary") or {}):
        screen.blit(small_font.render(line, True, TEXT), (card.x + 70, y))
        y += small_font.get_height() + 10
    player = combat["player"]
    state = f"Bohater: HP {player.get('hp', 0)}/{player.get('max_hp', 10)} | Rany {player.get('wounds', 0)}/{MAX_WOUNDS}"
    screen.blit(small_font.render(state, True, MUTED), (card.x + 70, card.bottom - 120))
    rect = pygame.Rect(card.centerx - 150, card.bottom - 72, 300, 48)
    button = CombatActionButton("KONTYNUUJ", rect, confirm_victory, action="combat_victory_continue")
    button.draw(screen, font, mouse_pos)
    return [button]


def _draw_defeat_choice(screen, title_font, font, small_font, mouse_pos):
    combat = _ACTIVE_COMBAT
    sw, sh = screen.get_size()
    card = pygame.Rect(sw // 2 - 430, sh // 2 - 290, 860, 580)
    screen.fill((12, 10, 9))
    draw_panel(screen, card, GOLD)
    title = title_font.render("PORAZKA", True, (205, 123, 105))
    screen.blit(title, title.get_rect(center=(card.centerx, card.y + 54)))
    screen.blit(small_font.render("Wybierz jedna zakryta karte z plecaka. Wybrany Przedmiot zostanie odrzucony.", True, TEXT), (card.x + 48, card.y + 112))
    buttons, choices = [], list(combat.get("defeat_choices") or [])
    cols, card_w, card_h, gap_x, gap_y = 5, 126, 150, 22, 24
    total_w = cols * card_w + (cols - 1) * gap_x
    start_x, start_y = card.centerx - total_w // 2, card.y + 175
    for position, _inventory_index in enumerate(choices):
        row, col = divmod(position, cols)
        rect = pygame.Rect(start_x + col * (card_w + gap_x), start_y + row * (card_h + gap_y), card_w, card_h)
        button = CombatActionButton(f"KARTA {position + 1}", rect, lambda pos=position: choose_defeat_item(pos), action="combat_defeat_item")
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)
    return buttons


def _draw_inventory_menu(screen, combat, rect, small_font, mouse_pos, menu_name):
    player, buttons = combat["player"], []
    pygame.draw.rect(screen, (23, 22, 20), rect, border_radius=10)
    pygame.draw.rect(screen, GOLD, rect, 1, border_radius=10)
    if menu_name == "items":
        indices, title = combat_usable_inventory_indices(player), "Przedmioty do uzycia"
    else:
        indices = [i for i, raw in enumerate(player.get("inventory", []) or []) if equipment_slot_for(normalise_item(raw), player.get("equipment") or {})]
        title = "Zmiana ekwipunku"
    screen.blit(small_font.render(title, True, GOLD), (rect.x + 12, rect.y + 10))
    y = rect.y + 38
    if not indices:
        screen.blit(small_font.render("Brak dostepnych pozycji.", True, MUTED), (rect.x + 12, y))
    for inventory_index in indices[:7]:
        label = item_display_name(player.get("inventory", [])[inventory_index])
        row = pygame.Rect(rect.x + 10, y, rect.width - 20, 34)
        callback = (lambda idx=inventory_index: use_combat_item(idx)) if menu_name == "items" else (lambda idx=inventory_index: change_combat_equipment(idx))
        button = CombatActionButton(label, row, callback, action=f"combat_{menu_name}")
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)
        y += 39
    close_rect = pygame.Rect(rect.right - 104, rect.y + 7, 92, 27)
    close = CombatActionButton("ZAMKNIJ", close_rect, lambda: toggle_combat_menu(menu_name), action="combat_menu_close")
    close.draw(screen, small_font, mouse_pos)
    buttons.append(close)
    return buttons


def draw_combat_screen(screen, title_font, font, small_font, mouse_pos):
    combat = _ACTIVE_COMBAT
    if combat is None:
        screen.fill((12, 11, 10))
        return []
    if combat.get("phase") == "victory":
        return _draw_victory(screen, title_font, font, small_font, mouse_pos)
    if combat.get("phase") == "defeat_choice":
        return _draw_defeat_choice(screen, title_font, font, small_font, mouse_pos)

    player, enemy = combat["player"], combat["enemy"]
    screen.fill((12, 10, 9))
    sw, sh = screen.get_size()
    margin = max(24, int(min(sw, sh) * 0.035))
    arena = pygame.Rect(margin, margin, sw - margin * 2, sh - margin * 2)
    draw_panel(screen, arena, GOLD)
    image_rect = pygame.Rect(arena.x + 18, arena.y + 18, int(arena.width * 0.57), arena.height - 36)
    _draw_cover(screen, image_rect, enemy.get("image", ""))
    pygame.draw.rect(screen, GOLD, image_rect, 2, border_radius=14)
    panel = pygame.Rect(image_rect.right + 22, arena.y + 22, arena.right - image_rect.right - 44, arena.height - 44)
    pygame.draw.rect(screen, PANEL, panel, border_radius=14)
    pygame.draw.rect(screen, GOLD, panel, 2, border_radius=14)
    screen.blit(title_font.render(enemy.get("name", "Przeciwnik"), True, (235, 196, 120)), (panel.x + 24, panel.y + 22))
    screen.blit(small_font.render(combat["session"].metadata.get("context_label", "Walka"), True, MUTED), (panel.x + 26, panel.y + 78))

    hp_bar = pygame.Rect(panel.x + 24, panel.y + 112, panel.width - 48, 28)
    _draw_hp_bar(screen, hp_bar, enemy.get("hp", 0), enemy.get("max_hp", 1))
    hp_label = font.render(f"HP {enemy.get('hp', 0)}/{enemy.get('max_hp', 0)}", True, TEXT)
    screen.blit(hp_label, hp_label.get_rect(center=hp_bar.center))
    screen.blit(small_font.render("Pozostale statystyki przeciwnika sa ukryte.", True, MUTED), (panel.x + 24, panel.y + 154))

    hero_y = panel.y + 196
    screen.blit(font.render(player.get("name", "Bohater"), True, TEXT), (panel.x + 24, hero_y))
    hero_bar = pygame.Rect(panel.x + 24, hero_y + 38, panel.width - 48, 22)
    _draw_hp_bar(screen, hero_bar, player.get("hp", 0), player.get("max_hp", 10))
    hero_hp = small_font.render(f"HP {player.get('hp', 0)}/{player.get('max_hp', 10)}", True, TEXT)
    screen.blit(hero_hp, hero_hp.get_rect(center=hero_bar.center))
    hero_stats = f"Walka {player.get('stats', {}).get('Walka', 0)} | KP {hero_armor_class(player)} | Rany {player.get('wounds', 0)}/{MAX_WOUNDS}"
    screen.blit(small_font.render(hero_stats, True, MUTED), (panel.x + 24, hero_y + 70))
    hit_bonus, _ = weapon_bonuses(player)
    screen.blit(small_font.render(f"Bron: +{hit_bonus} do trafienia | {engine_weapon_damage(player)} obrazen", True, MUTED), (panel.x + 24, hero_y + 96))

    log_rect = pygame.Rect(panel.x + 24, panel.y + 320, panel.width - 48, max(110, panel.height - 510))
    buttons, menu_name = [], combat.get("menu")
    if menu_name in {"items", "equipment"}:
        buttons.extend(_draw_inventory_menu(screen, combat, log_rect, small_font, mouse_pos, menu_name))
    else:
        pygame.draw.rect(screen, (25, 23, 21), log_rect, border_radius=10)
        pygame.draw.rect(screen, (91, 75, 51), log_rect, 1, border_radius=10)
        draw_lines(screen, small_font, wrap(small_font, combat.get("last_log", ""), log_rect.width - 24)[:7], log_rect.x + 12, log_rect.y + 12, TEXT, line_h=small_font.get_height() + 4)

    escape, can_escape = dict(enemy.get("escape") or {}), bool(enemy.get("can_escape", True))
    specs = [
        ("ATAKUJ", resolve_combat_round, True, "combat_attack"),
        ("OBRONA", defend, True, "combat_defend"),
        ("PRZEDMIOT", lambda: toggle_combat_menu("items"), True, "combat_items"),
        ("EKWIPUNEK", lambda: toggle_combat_menu("equipment"), True, "combat_equipment"),
    ]
    if can_escape and escape.get("threshold") is not None:
        specs.append(("UCIEKAJ", attempt_escape, True, "combat_escape"))
    bribe_cost = max(0, int(escape.get("gold", 0) or 0))
    if bribe_cost > 0:
        specs.append((f"PRZEKUP - {bribe_cost} ZL", attempt_bribe, int(player.get("gold", 0) or 0) >= bribe_cost, "combat_bribe"))
    cols, gap, row_h = 2, 8, 42
    rows = (len(specs) + cols - 1) // cols
    area_y = panel.bottom - 20 - rows * row_h - (rows - 1) * gap
    col_w = (panel.width - 48 - gap) // 2
    for index, (label, callback, enabled, action) in enumerate(specs):
        row, col = divmod(index, cols)
        rect = pygame.Rect(panel.x + 24 + col * (col_w + gap), area_y + row * (row_h + gap), col_w, row_h)
        button = CombatActionButton(label, rect, callback, action=action, enabled=enabled)
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)
    return buttons