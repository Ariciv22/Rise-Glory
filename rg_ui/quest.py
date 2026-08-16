from __future__ import annotations

import unicodedata
from pathlib import Path

import pygame

from rg_core.data import GOLD, MUTED, TEXT
from rg_engine.quests import (
    current_stage,
    find_player_quest,
    option_state,
    prepare_quest_test,
    quest_definition,
    quest_tabs_for_location,
)
from rg_engine.world import quest_difficulty_from_legend_gap
from rg_core.quest_runtime import resolve_quest_option
from rg_ui.common import Button, draw_lines, wrap

ROOT_DIR = Path(__file__).resolve().parents[1]
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
_IMAGE_CACHE = {}
_SCALED_CACHE = {}
QUEST_ACTION_PREFIX = "location_quest:"


class QuestActionButton(Button):
    def __init__(self, text, rect, callback, enabled=True, action="quest_action"):
        super().__init__(text, action, rect)
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
        if not self.enabled or not self.rect.collidepoint(pos):
            return False
        if self.callback:
            self.callback()
        return True


def _normalize(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    return "".join(character for character in ascii_text if character.isalnum())


def quest_action(quest_id):
    return f"{QUEST_ACTION_PREFIX}{quest_id}"


def parse_quest_action(action):
    value = str(action)
    return value.split(":", 1)[1] if value.startswith(QUEST_ACTION_PREFIX) else None


def location_quest_tabs(player, location_name):
    return quest_tabs_for_location(player, location_name)


def _find_image(image_name):
    target = _normalize(image_name)
    if target in _IMAGE_CACHE:
        return _IMAGE_CACHE[target]
    for root in (ROOT_DIR / "Grafiki", ROOT_DIR):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _IMAGE_EXTENSIONS:
                continue
            if target and target not in _normalize(path.stem):
                continue
            try:
                image = pygame.image.load(str(path)).convert_alpha()
            except (OSError, pygame.error):
                image = None
            _IMAGE_CACHE[target] = image
            return image
    _IMAGE_CACHE[target] = None
    return None


def _draw_image(screen, rect, image_name):
    source = _find_image(image_name)
    if source is None:
        pygame.draw.rect(screen, (22, 18, 16), rect, border_radius=10)
        pygame.draw.circle(screen, (71, 40, 34), rect.center, max(28, rect.height // 4), 3)
        fallback_font = pygame.font.SysFont("georgia", max(15, rect.height // 20), bold=True)
        label = fallback_font.render("Quest", True, (210, 175, 108))
        screen.blit(label, label.get_rect(center=rect.center))
        return
    key = (_normalize(image_name), rect.width, rect.height)
    scaled = _SCALED_CACHE.get(key)
    if scaled is None:
        iw, ih = source.get_size()
        scale = max(rect.width / iw, rect.height / ih)
        large = pygame.transform.smoothscale(source, (max(1, int(iw * scale)), max(1, int(ih * scale))))
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
    shade.fill((0, 0, 0, 42))
    screen.blit(shade, rect.topleft)


def _failure_text(quest):
    failures = int(quest.get("failures", 0) or 0)
    return "Porażki: " + " ".join("●" if index < failures else "○" for index in range(5))


def _draw_result_box(screen, small_font, rect, text):
    if not text:
        return
    pygame.draw.rect(screen, (28, 31, 28), rect, border_radius=8)
    pygame.draw.rect(screen, (90, 100, 82), rect, 1, border_radius=8)
    lines = wrap(small_font, text, rect.width - 20)[:4]
    draw_lines(screen, small_font, lines, rect.x + 10, rect.y + 8, TEXT, line_h=small_font.get_height() + 2)


def _requirement_summary(option):
    chunks = []
    requires = option.get("requires") or {}
    consumes = option.get("consumes") or {}
    if requires:
        chunks.append("Wymaga")
    if consumes or option.get("materials") or option.get("gold_cost") or option.get("item_cost"):
        chunks.append("Zużywa")
    return " / ".join(chunks)


def _option_label(option, modifier):
    option_type = str(option.get("type", "test"))
    if option_type == "combat":
        label = f"WALKA: {option.get('label', 'Rozpocznij walkę')}"
    elif option_type in {"choice", "automatic", "payment"}:
        label = str(option.get("label", "Wybierz"))
    else:
        threshold = int(option.get("threshold", 0) or 0) + modifier
        label = f"{option.get('stat', '-')} {threshold}: {option.get('label', 'Wykonaj test')}"
    summary = _requirement_summary(option)
    if summary:
        label += f" | {summary}"
    return label


def _prepare(player, quest):
    success, message = prepare_quest_test(player, quest)
    quest["last_result"] = message
    return success


def _status_line(quest, definition):
    number = int(quest.get("quest_number", definition.get("quest_number", 0)) or 0)
    prefix = f"Quest #{number}" if number else "Quest"
    length = quest.get("length", definition.get("length", ""))
    started = "Rozpoczęty" if quest.get("started") else "Nierozpoczęty"
    return f"{prefix} | {length} | {started} | {_failure_text(quest)}"


def draw_quest_panel(screen, font, small_font, mouse_pos, content, player, quest_id):
    quest = find_player_quest(player, quest_id, include_history=True)
    definition = quest_definition(quest_id)
    buttons = []
    card = content.inflate(-36, -36)
    pygame.draw.rect(screen, (13, 11, 10), card, border_radius=16)
    pygame.draw.rect(screen, GOLD, card, 2, border_radius=16)
    if quest is None or definition is None:
        draw_lines(screen, font, ["Nie znaleziono tego Questa."], card.x + 24, card.y + 24, MUTED)
        return buttons

    stage = current_stage(quest)
    image_name = (stage or {}).get("image") or definition.get("image", "")
    image_rect = pygame.Rect(card.x + 14, card.y + 14, int(card.width * 0.40), card.height - 28)
    _draw_image(screen, image_rect, image_name)
    pygame.draw.rect(screen, GOLD, image_rect, 2, border_radius=10)

    right = pygame.Rect(image_rect.right + 22, card.y + 16, card.right - image_rect.right - 38, card.height - 32)
    title_font = pygame.font.SysFont("georgia", max(24, font.get_height() + 8), bold=True)
    screen.blit(title_font.render(quest.get("name", definition["name"]), True, (235, 196, 120)), (right.x, right.y))
    screen.blit(small_font.render(_status_line(quest, definition), True, MUTED), (right.x, right.y + 42))

    expansions = list(quest.get("discovered_expansions", []) or [])
    if expansions:
        expansion_text = "Odkryte rozwinięcia: " + " → ".join(str(value) for value in expansions)
        screen.blit(small_font.render(expansion_text, True, GOLD), (right.x, right.y + 64))

    status = quest.get("status")
    if status == "completed":
        draw_lines(screen, font, ["QUEST UKOŃCZONY"], right.x, right.y + 92, (180, 220, 130))
        ending = quest.get("ending_id")
        if ending:
            screen.blit(small_font.render(f"Zakończenie: {ending}", True, GOLD), (right.x, right.y + 126))
        draw_lines(screen, small_font, wrap(small_font, quest.get("last_result", ""), right.width), right.x, right.y + 154, TEXT, line_h=22)
        return buttons
    if status == "failed":
        draw_lines(screen, font, ["QUEST PRZEGRANY"], right.x, right.y + 92, (220, 110, 100))
        draw_lines(screen, small_font, wrap(small_font, quest.get("last_result", ""), right.width), right.x, right.y + 136, TEXT, line_h=22)
        return buttons
    if status == "abandoned":
        draw_lines(screen, font, ["QUEST PORZUCONY"], right.x, right.y + 92, (190, 150, 105))
        draw_lines(screen, small_font, wrap(small_font, quest.get("last_result", ""), right.width), right.x, right.y + 136, TEXT, line_h=22)
        return buttons
    if status == "combat":
        screen.blit(font.render("Trwa walka", True, TEXT), (right.x, right.y + 92))
        draw_lines(screen, small_font, ["Dokończ walkę na ekranie przeciwnika."], right.x, right.y + 136, MUTED)
        return buttons
    if not stage:
        draw_lines(screen, font, ["Brak aktualnego etapu Questa."], right.x, right.y + 92, MUTED)
        return buttons

    total_stages = len(definition.get("stages", []))
    screen.blit(font.render(f"Etap {stage['number']}/{total_stages} — {stage['title']}", True, TEXT), (right.x, right.y + 88))
    draw_lines(screen, small_font, wrap(small_font, stage.get("text", ""), right.width)[:4], right.x, right.y + 122, MUTED, line_h=20)

    info_y = right.y + 208
    if quest.get("point_of_no_return") or stage.get("point_of_no_return"):
        screen.blit(small_font.render("PUNKT BEZ POWROTU — tego Questa nie można teraz porzucić.", True, (225, 135, 105)), (right.x, info_y))
        info_y += 22

    paragraph = quest.get("current_paragraph")
    if paragraph:
        screen.blit(small_font.render(f"Księga Questów: przeczytaj akapit {paragraph}", True, GOLD), (right.x, info_y))
        info_y += 22

    retry_modifier = int(quest.get("difficulty_modifier", 0) or 0)
    legend_modifier = quest_difficulty_from_legend_gap(player)
    effective_modifier = retry_modifier + legend_modifier
    modifier_parts = []
    if legend_modifier:
        modifier_parts.append(f"przewaga Legendy +{legend_modifier}")
    if retry_modifier:
        modifier_parts.append(f"kara kolejnego testu +{retry_modifier}")
    if modifier_parts:
        screen.blit(small_font.render("Próg zwiększony: " + " | ".join(modifier_parts), True, (235, 154, 92)), (right.x, info_y))
        info_y += 22

    token = player.get("_token_ref")
    actions = int(getattr(token, "actions", 0) or 0) if token is not None else 0
    prep = "wykorzystane" if quest.get("preparation_used") else "dostępne"
    screen.blit(small_font.render(f"Akcje: {actions} | Przygotowanie: {prep}", True, TEXT), (right.x, info_y))
    info_y += 28

    if not quest.get("preparation_used"):
        prep_rect = pygame.Rect(right.x, info_y, right.width, 36)
        prep_button = QuestActionButton(
            "PRZYGOTUJ SIĘ — 1 Akcja, +2 do najbliższego testu",
            prep_rect,
            lambda: _prepare(player, quest),
            enabled=actions >= 1,
            action=quest_action(quest_id),
        )
        prep_button.draw(screen, small_font, mouse_pos)
        buttons.append(prep_button)
        info_y += 44

    options = list(stage.get("options", []))
    visible_options = []
    for real_index, option in enumerate(options):
        state = option_state(player, quest, option)
        if state["visible"]:
            visible_options.append((real_index, option, state))

    button_y = info_y
    button_h = 42
    for row, (real_index, option, state) in enumerate(visible_options):
        rect = pygame.Rect(right.x, button_y + row * (button_h + 7), right.width, button_h)
        required_actions = int(option.get("action_cost", 1) or 0)
        label = _option_label(option, effective_modifier)
        if state["disabled"] and state["reason"]:
            label += f" — {state['reason']}"
        button = QuestActionButton(
            label,
            rect,
            lambda selected=real_index: resolve_quest_option(player, quest, selected),
            enabled=actions >= required_actions and not state["disabled"],
            action=quest_action(quest_id),
        )
        button.draw(screen, small_font, mouse_pos)
        buttons.append(button)

    result_y = button_y + len(visible_options) * (button_h + 7) + 6
    result_h = max(60, right.bottom - result_y)
    _draw_result_box(screen, small_font, pygame.Rect(right.x, result_y, right.width, result_h), quest.get("last_result", ""))
    return buttons
