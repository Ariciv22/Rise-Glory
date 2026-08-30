from __future__ import annotations

import pygame

from rg_engine.quests import current_stage, quest_definition, quest_tabs_for_location
from rg_ui import hex_info_panel, hud, world_state
from rg_ui.combat import is_combat_active
from rg_ui.common import draw_image_panel
from rg_ui.quest import quest_action
from rg_world import map as world_map


_INSTALLED = False
_ORIGINAL_CAN_MOVE_TO = None
_ORIGINAL_SCOREBOARD = None
_ORIGINAL_HEX_INFO = None


def _fit(font, text, width):
    value = str(text or "")
    if font.size(value)[0] <= width:
        return value
    suffix = "..."
    while value and font.size(value + suffix)[0] > width:
        value = value[:-1]
    return value.rstrip() + suffix


def _find_action_button(controller, action):
    """Znajduje prawdziwy przycisk schowany pod warstwami kontrolerow HUD-u."""
    current = controller
    visited = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        if getattr(current, "action", None) == action and hasattr(current, "rect"):
            return current
        current = getattr(current, "delegate", None)
    return None


def _draw_scoreboard_without_covering_art(
    screen,
    font,
    small_font,
    players,
    tokens,
    active_player_index,
    right,
):
    """Odtwarza panel5, a tekst umieszcza tylko w osobnych polach UI.

    Starszy renderer wypisywal tytul i dane bezposrednio na ornamentach
    zapisanych w panel5.png. Najpierw zachowujemy caly lancuch kontrolerow
    (Wydarzenia Swiata, Problemy, Questy), a potem poprawiamy tylko warstwe
    wizualna tabeli i ponownie rysujemy akcje heksa na dole panelu.
    """
    controller = _ORIGINAL_SCOREBOARD(
        screen,
        font,
        small_font,
        players,
        tokens,
        active_player_index,
        right,
    )

    if is_combat_active():
        return controller

    draw_image_panel(screen, right, 5)

    side_pad = max(12, int(round(right.width * 0.035)))
    safe_top = right.y + max(58, min(86, int(round(right.height * 0.052))))
    header_h = 38
    header = pygame.Rect(
        right.x + side_pad,
        safe_top,
        right.width - side_pad * 2,
        header_h,
    )
    draw_image_panel(screen, header, 2)
    title = font.render("Tabela graczy", True, hud.TEXT)
    screen.blit(title, title.get_rect(center=header.center))

    # Dolna czesc panelu zawiera kompas oraz dynamiczne akcje Problemow i
    # Questow. Tabela konczy sie wyzej, aby tych elementow nie przykrywac.
    reserved_bottom = max(190, min(320, int(round(right.height * 0.24))))
    list_bottom = right.bottom - reserved_bottom
    row_h = 56
    row_gap = 7
    y = header.bottom + 8

    for index, player in enumerate(players):
        if y + row_h + 46 > list_bottom:
            break

        active = index == active_player_index
        row = pygame.Rect(
            right.x + side_pad,
            y,
            right.width - side_pad * 2,
            row_h,
        )
        draw_image_panel(screen, row, 2)
        if active:
            pygame.draw.rect(
                screen,
                player.get("player_color", hud.GOLD),
                row,
                3,
                border_radius=9,
            )

        color = player.get("player_color", hud.GOLD)
        pygame.draw.circle(screen, color, (row.x + 16, row.y + 16), 7)

        marker = "AKTYWNY" if active else f"GRACZ {player.get('player_number', index + 1)}"
        name = str(player.get("name", "Bohater"))
        headline = _fit(small_font, f"{marker}  {name}", row.width - 48)
        screen.blit(
            small_font.render(headline, True, hud.TEXT if active else hud.MUTED),
            (row.x + 30, row.y + 7),
        )

        token = tokens[index] if index < len(tokens) else None
        actions = int(getattr(token, "actions", 0) or 0) if token is not None else 0
        helper_count = len(player.get("helpers", []))
        summary = (
            f"L {player.get('legend', 0)} | Z {player.get('gold', 0)} | "
            f"R {player.get('wounds', 0)}/{hud.MAX_WOUNDS} | A {actions} | P {helper_count}"
        )
        summary = _fit(small_font, summary, row.width - 24)
        screen.blit(
            small_font.render(summary, True, hud.MUTED),
            (row.x + 12, row.y + 31),
        )
        y += row_h + row_gap

    # Koniec tury ma stale miejsce przy samym dole panelu. Nie przesuwa sie
    # juz razem z liczba graczy i nie zajmuje przestrzeni pod tabela. Dolny
    # margines 12 px chroni ozdobna rame panel5, a srodkowanie omija kompas.
    end_rect = pygame.Rect(
        right.centerx - 70,
        right.bottom - 46,
        140,
        34,
    )
    end_button = _find_action_button(controller, "end_turn")
    if end_button is not None:
        end_button.rect = end_rect
        end_button.draw(screen, small_font, pygame.mouse.get_pos())
    else:
        # Awaryjnie zachowujemy wizualna zgodnosc; normalny lancuch zawsze
        # zawiera delegata end_turn zwroconego przez bazowy HUD.
        fallback = hud._HudPanelButton("Koniec tury", "end_turn", end_rect)
        fallback.draw(screen, small_font, pygame.mouse.get_pos())

    # Pelne odtworzenie panel5 wyczyscilo starsze nakladki. Rysujemy ponownie
    # aktualny, juz opakowany renderer akcji, ktory zawiera Problemy i Questy.
    world_state._draw_hex_actions(
        screen,
        small_font,
        players,
        tokens,
        active_player_index,
        right,
    )
    return controller


def _explicit_location_quests(hero, selected_tile):
    location = getattr(selected_tile, "location", None)
    if not isinstance(location, dict):
        return []

    location_name = str(location.get("name") or "")
    if not location_name:
        return []

    result = []
    for quest in quest_tabs_for_location(hero, location_name):
        if not isinstance(quest, dict) or quest.get("status") != "active":
            continue
        definition = quest_definition(str(quest.get("id") or "")) or {}
        stage = current_stage(quest) or {}
        required = stage.get("required_location") or definition.get("required_location")

        # Nie pokazujemy Questa bez konkretnego celu na kazdym miescie.
        # quest_tabs_for_location zwraca takie globalne etapy celowo, ale
        # przycisk na heksie ma oznaczac: "to jest miejsce wykonania".
        if required:
            result.append(quest)
    return result


class _MapQuestButton(hex_info_panel.HexInfoButton):
    def __init__(self, text, rect, hero, quest_id, enabled=True):
        super().__init__(text, quest_action(quest_id), rect, enabled=enabled)
        self.hero = hero
        self.quest_id = str(quest_id)

    def clicked(self, pos):
        if not self.enabled or not self.rect.collidepoint(pos):
            return False

        active = next(
            (
                quest
                for quest in self.hero.get("active_quests", []) or []
                if isinstance(quest, dict)
                and str(quest.get("id") or "") == self.quest_id
                and quest.get("status") == "active"
            ),
            None,
        )
        if active is None:
            self.hero["_map_message"] = "Ten Quest nie jest juz aktywny."
            return True

        # Korzystamy z istniejacego modala Questa na mapie. Dzieki temu
        # wykonanie Questa nie zajmuje zadnego z 6 slotow budynkow lokacji.
        from rg_ui import quest_markers as quest_marker_ui

        quest_marker_ui._QUEST_PREVIEW_ID = None
        quest_marker_ui._QUEST_PANEL_ID = self.quest_id
        quest_marker_ui._QUEST_PANEL_PLAYER = self.hero
        return True


def _draw_hex_info_with_location_quest(
    screen,
    font,
    small_font,
    hero,
    token,
    selected_tile,
    mouse_pos,
):
    buttons = list(
        _ORIGINAL_HEX_INFO(
            screen,
            font,
            small_font,
            hero,
            token,
            selected_tile,
            mouse_pos,
        )
        or []
    )

    if selected_tile is None or hero is None:
        return buttons

    quests = _explicit_location_quests(hero, selected_tile)
    if not quests:
        return buttons

    enter = next(
        (button for button in buttons if getattr(button, "action", None) == "enter_selected_location"),
        None,
    )
    if enter is None:
        return buttons

    # Ten sam dolny wiersz tooltipa dzielimy na dwa pola. Nie zabieramy miejsca
    # opisowi heksa i nie dokladamy siodmego kafla do ekranu miasta.
    buttons = [button for button in buttons if button is not enter]
    row = pygame.Rect(enter.rect)
    pygame.draw.rect(screen, hex_info_panel.PANEL_DARK, row)

    gap = 6
    usable = max(2, row.width - gap)
    quest_w = max(1, int(round(usable * 0.60)))
    enter_w = max(1, usable - quest_w)
    quest_rect = pygame.Rect(row.x, row.y, quest_w, row.height)
    enter_rect = pygame.Rect(quest_rect.right + gap, row.y, enter_w, row.height)

    on_tile = token is not None and getattr(token, "tile", None) is selected_tile
    selected_quest = quests[0]
    quest_name = str(selected_quest.get("name") or "Quest")
    quest_label = _fit(small_font, f"QUEST: {quest_name}", quest_rect.width - 18)
    quest_button = _MapQuestButton(
        quest_label,
        quest_rect,
        hero,
        selected_quest.get("id"),
        enabled=on_tile,
    )
    quest_button.draw(screen, small_font, mouse_pos)

    enter_label = "WEJDZ" if on_tile else "PODEJDZ"
    enter_button = hex_info_panel.HexInfoButton(
        enter_label,
        "enter_selected_location",
        enter_rect,
        enabled=on_tile,
    )
    enter_button.draw(screen, small_font, mouse_pos)

    # Quest pierwszy: prostokaty sie nie nakladaja, ale ten porzadek gwarantuje,
    # ze nawet po przyszlej zmianie geometrii klik w QUEST nie otworzy miasta.
    buttons.extend([quest_button, enter_button])
    return buttons


def _can_move_without_spending_action_on_current_tile(self, target):
    if target is self.tile:
        return False
    return _ORIGINAL_CAN_MOVE_TO(self, target)


def install_map_ui_regression_fixes(app_module=None):
    global _INSTALLED, _ORIGINAL_CAN_MOVE_TO, _ORIGINAL_SCOREBOARD, _ORIGINAL_HEX_INFO
    if _INSTALLED:
        return

    _ORIGINAL_CAN_MOVE_TO = world_map.HeroToken.can_move_to
    world_map.HeroToken.can_move_to = _can_move_without_spending_action_on_current_tile

    # Instalujemy po world_state/threat/quest_markers z rg_core.setup, wiec
    # zachowujemy caly istniejacy lancuch kontrolerow i poprawiamy tylko render.
    _ORIGINAL_SCOREBOARD = hud._draw_scoreboard
    hud._draw_scoreboard = _draw_scoreboard_without_covering_art

    _ORIGINAL_HEX_INFO = hex_info_panel.draw_hex_info_panel
    hex_info_panel.draw_hex_info_panel = _draw_hex_info_with_location_quest
    if app_module is not None:
        app_module.draw_hex_info_panel = _draw_hex_info_with_location_quest

    _INSTALLED = True
