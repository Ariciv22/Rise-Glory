from __future__ import annotations

import pygame

from rg_content.quest_book import quest_paragraph
from rg_engine.quests import find_player_quest
from rg_core.data import GOLD, MUTED, TEXT
from rg_ui.common import wrap

_INSTALLED = False


def install_quest_book_ui() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import rg_ui.quest as quest_ui

    original_draw_quest_panel = quest_ui.draw_quest_panel

    def draw_quest_panel_with_book(screen, font, small_font, mouse_pos, content, player, quest_id):
        buttons = original_draw_quest_panel(screen, font, small_font, mouse_pos, content, player, quest_id)
        quest = find_player_quest(player, quest_id, include_history=True)
        if not quest:
            return buttons

        paragraph_id = str(quest.get("current_paragraph") or "")
        if not paragraph_id or str(quest.get("_acknowledged_paragraph") or "") == paragraph_id:
            return buttons
        paragraph = quest_paragraph(paragraph_id)
        if not paragraph:
            return buttons

        shade = pygame.Surface(content.size, pygame.SRCALPHA)
        shade.fill((0, 0, 0, 188))
        screen.blit(shade, content.topleft)

        width = min(760, content.width - 100)
        height = min(470, content.height - 80)
        card = pygame.Rect(content.centerx - width // 2, content.centery - height // 2, width, height)
        pygame.draw.rect(screen, (18, 15, 12), card, border_radius=16)
        pygame.draw.rect(screen, GOLD, card, 2, border_radius=16)

        title = paragraph.get("title") or f"Akapit {paragraph_id}"
        screen.blit(font.render(f"Księga Questów — {paragraph_id}", True, GOLD), (card.x + 28, card.y + 24))
        screen.blit(font.render(str(title), True, TEXT), (card.x + 28, card.y + 62))

        y = card.y + 112
        for line in wrap(small_font, paragraph.get("text", ""), card.width - 56)[:12]:
            screen.blit(small_font.render(line, True, TEXT), (card.x + 28, y))
            y += small_font.get_height() + 7

        screen.blit(
            small_font.render("W fizycznej planszówce ten sam numer odsyła do Księgi Questów.", True, MUTED),
            (card.x + 28, card.bottom - 86),
        )

        close_rect = pygame.Rect(card.x + 28, card.bottom - 58, card.width - 56, 38)

        def acknowledge():
            quest["_acknowledged_paragraph"] = paragraph_id
            return True, f"Przeczytano akapit {paragraph_id}."

        close_button = quest_ui.QuestActionButton(
            "ZAMKNIJ AKAPIT I WRÓĆ DO QUESTA",
            close_rect,
            acknowledge,
            enabled=True,
            action=quest_ui.quest_action(quest_id),
        )
        close_button.draw(screen, small_font, mouse_pos)
        return [close_button]

    quest_ui.draw_quest_panel = draw_quest_panel_with_book

    # Moduły interfejsu pobrały funkcję wcześniej jako lokalną referencję.
    try:
        import rg_ui.city as city
        city.draw_quest_panel = draw_quest_panel_with_book
    except (ImportError, AttributeError):
        pass
    try:
        import rg_ui.quest_markers as quest_markers
        quest_markers.draw_quest_panel = draw_quest_panel_with_book
    except (ImportError, AttributeError):
        pass

    _INSTALLED = True
