import pygame

from rg_data import (
    BG,
    DRAG_THRESHOLD,
    FPS,
    HERO_ARCHETYPES,
    MIN_SCREEN_HEIGHT,
    MIN_SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STATE_CITY,
    STATE_COUNCIL,
    STATE_CUSTOM_HERO,
    STATE_GAME,
    STATE_INITIATIVE,
    STATE_MAP_SELECT,
    STATE_MENU,
    STATE_MULTIPLAYER,
    STATE_PLAYER_CONFIG,
    STATE_PLAYER_COUNT,
    ZOOM_STEP,
)
from rg_city_screen import draw_city_screen
from rg_hud import draw_game_ui
from rg_location_data import buy_shop_item, hire_helper, take_quest
from rg_map import Camera, load_textures
from rg_screens import (
    draw_council,
    draw_custom_hero,
    draw_initiative,
    draw_map_select,
    draw_menu,
    draw_multiplayer,
    draw_player_config,
    draw_player_count,
)
from rg_setup import build_player, create_tokens, default_custom_stats, random_archetype
from rg_tooltip import draw_location_tooltip
from rg_turns import TurnManager, resolve_initiative
from rg_ui import over_ui, ui_rects
from rg_world import generate_world


def create_window(fullscreen=False):
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)


def player_name_input_rect():
    return pygame.Rect(SCREEN_WIDTH / 2 - 270, 170, 540, 58)


def activate_text_input():
    pygame.key.start_text_input()
    pygame.key.set_text_input_rect(player_name_input_rect())


def prepare_game(current_map, players):
    tiles = generate_world(current_map)
    return tiles, create_tokens(players, tiles)


def prepare_initiative(players):
    initiative = resolve_initiative(players)
    return initiative, TurnManager(initiative["turn_order"])


def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    activate_text_input()
    screen = create_window(False)
    pygame.display.set_caption("Rise & Glory")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20, bold=True)
    small_font = pygame.font.SysFont("arial", 17, bold=True)
    token_font = pygame.font.SysFont("arial", 17, bold=True)
    title_font = pygame.font.SysFont("arial", 42, bold=True)

    textures = load_textures()
    camera = Camera()
    state = STATE_MENU
    current_map = "rosette9"
    player_count = 1
    config_player_index = 0
    player_name = ""
    name_input_active = False
    selected_archetype = None
    custom_stats = default_custom_stats()
    players = []
    tiles = generate_world(current_map)
    tokens = []
    initiative = None
    turn_manager = None
    active_player_index = 0
    selected_tile = None
    selected_token = None
    current_city = None
    selected_city_place = None
    location_message = ""
    buttons = []
    game_buttons = []
    city_buttons = []
    dragging = False
    drag_moved = False
    drag_start = (0, 0)
    last_mouse = (0, 0)
    fullscreen = False
    running = True

    def finish_player_configuration(player):
        nonlocal config_player_index, player_name, name_input_active, selected_archetype, custom_stats
        nonlocal players, tiles, tokens, initiative, turn_manager, active_player_index
        nonlocal selected_token, selected_tile, state
        players.append(player)
        config_player_index += 1
        player_name = ""
        name_input_active = True
        selected_archetype = None
        custom_stats = default_custom_stats()
        if config_player_index >= player_count:
            name_input_active = False
            tiles, tokens = prepare_game(current_map, players)
            initiative, turn_manager = prepare_initiative(players)
            active_player_index = turn_manager.active_player_index
            selected_token = tokens[active_player_index]
            selected_tile = None
            state = STATE_INITIATIVE
        else:
            activate_text_input()
            state = STATE_PLAYER_CONFIG

    def advance_turn():
        nonlocal active_player_index, selected_token, selected_tile
        nonlocal current_city, selected_city_place, location_message, state
        if not turn_manager or not tokens:
            return
        result = turn_manager.end_turn(tokens)
        active_player_index = result["active_player_index"]
        selected_token = tokens[active_player_index]
        selected