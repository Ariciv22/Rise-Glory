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


def prepare_game(current_map, players):
    tiles = generate_world(current_map)
    tokens = create_tokens(players, tiles)
    return tiles, tokens


def prepare_initiative(players):
    initiative = resolve_initiative(players)
    turn_manager = TurnManager(initiative["turn_order"])
    return initiative, turn_manager


def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
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
        nonlocal config_player_index, player_name, selected_archetype, custom_stats
        nonlocal players, tiles, tokens, initiative, turn_manager, active_player_index
        nonlocal selected_token, selected_tile, state

        players.append(player)
        config_player_index += 1
        player_name = ""
        selected_archetype = None
        custom_stats = default_custom_stats()

        if config_player_index >= player_count:
            tiles, tokens = prepare_game(current_map, players)
            initiative, turn_manager = prepare_initiative(players)
            active_player_index = turn_manager.active_player_index
            selected_token = tokens[active_player_index]
            selected_tile = None
            state = STATE_INITIATIVE
        else:
            state = STATE_PLAYER_CONFIG

    def advance_turn():
        nonlocal active_player_index, selected_token, selected_tile
        nonlocal current_city, selected_city_place, state

        if not turn_manager or not tokens:
            return
        result = turn_manager.end_turn(tokens)
        active_player_index = result["active_player_index"]
        selected_token = tokens[active_player_index]
        selected_tile = None
        current_city = None
        selected_city_place = None
        if result["council_due"]:
            state = STATE_COUNCIL
        else:
            camera.center_on_tile(selected_token.tile)

    while running:
        mouse = pygame.mouse.get_pos()
        hovered = None
        rects = ui_rects(screen) if state == STATE_GAME else []
        if state == STATE_GAME and not dragging and not over_ui(mouse, rects):
            for tile in tiles:
                if tile.contains(mouse, camera):
                    hovered = tile
                    break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE and not fullscreen:
                SCREEN_WIDTH = max(MIN_SCREEN_WIDTH, event.w)
                SCREEN_HEIGHT = max(MIN_SCREEN_HEIGHT, event.h)
                screen = create_window(False)
                if state == STATE_GAME and selected_token:
                    camera.center_on_tile(selected_token.tile)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == STATE_CITY:
                        state = STATE_GAME
                    elif state == STATE_COUNCIL:
                        state = STATE_GAME
                        if selected_token:
                            camera.center_on_tile(selected_token.tile)
                    elif state in [STATE_PLAYER_COUNT, STATE_PLAYER_CONFIG, STATE_CUSTOM_HERO, STATE_MAP_SELECT, STATE_MULTIPLAYER, STATE_INITIATIVE]:
                        state = STATE_MENU
                    else:
                        state = STATE_MENU
                elif state in [STATE_PLAYER_CONFIG, STATE_CUSTOM_HERO]:
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        pass
                    elif event.unicode and event.unicode.isprintable() and len(player_name) < 24:
                        player_name += event.unicode
                elif event.key == pygame.K_SPACE and state == STATE_GAME and selected_token:
                    camera.center_on_tile(selected_token.tile)
                elif event.key in [pygame.K_TAB, pygame.K_n] and state == STATE_GAME:
                    advance_turn()
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = create_window(True)
                        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
                    else:
                        SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1000
                        screen = create_window(False)
                    if state == STATE_GAME and selected_token:
                        camera.center_on_tile(selected_token.tile)
            elif event.type == pygame.MOUSEWHEEL and state == STATE_GAME and not over_ui(mouse, rects):
                camera.zoom_at(mouse, ZOOM_STEP if event.y > 0 else 1 / ZOOM_STEP)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and state == STATE_GAME and not over_ui(event.pos, rects):
                dragging = True
                drag_moved = False
                drag_start = event.pos
                last_mouse = event.pos
            elif event.type == pygame.MOUSEMOTION and dragging and state == STATE_GAME:
                dx = event.pos[0] - last_mouse[0]
                dy = event.pos[1] - last_mouse[1]
                if abs(event.pos[0] - drag_start[0]) > DRAG_THRESHOLD or abs(event.pos[1] - drag_start[1]) > DRAG_THRESHOLD:
                    drag_moved = True
                camera.move(dx, dy)
                last_mouse = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
                if state in [
                    STATE_MENU,
                    STATE_MAP_SELECT,
                    STATE_PLAYER_COUNT,
                    STATE_PLAYER_CONFIG,
                    STATE_CUSTOM_HERO,
                    STATE_MULTIPLAYER,
                    STATE_INITIATIVE,
                    STATE_COUNCIL,
                ]:
                    for button in buttons:
                        if not button.clicked(event.pos):
                            continue
                        action = str(button.action)
                        if state == STATE_MENU:
                            if action == "new":
                                state = STATE_MAP_SELECT
                            elif action == "multi":
                                state = STATE_MULTIPLAYER
                            elif action == "exit":
                                running = False
                        elif state == STATE_MAP_SELECT:
                            if action == "back":
                                state = STATE_MENU
                            else:
                                current_map = action
                                state = STATE_PLAYER_COUNT
                        elif state == STATE_PLAYER_COUNT:
                            if action == "back":
                                state = STATE_MAP_SELECT
                            elif action.startswith("players_"):
                                player_count = int(action.split("_")[1])
                                config_player_index = 0
                                players = []
                                player_name = ""
                                selected_archetype = None
                                custom_stats = default_custom_stats()
                                state = STATE_PLAYER_CONFIG
                        elif state == STATE_PLAYER_CONFIG:
                            if action == "back":
                                if config_player_index > 0:
                                    config_player_index -= 1
                                    players = players[:config_player_index]
                                else:
                                    state = STATE_PLAYER_COUNT
                                player_name = ""
                                selected_archetype = None
                            elif action.startswith("archetype_"):
                                archetype_id = int(action.split("_")[1])
                                selected_archetype = next(item for item in HERO_ARCHETYPES if item["id"] == archetype_id)
                            elif action == "random_hero":
                                selected_archetype = random_archetype()
                            elif action == "custom_hero":
                                selected_archetype = selected_archetype or HERO_ARCHETYPES[0]
                                custom_stats = default_custom_stats()
                                state = STATE_CUSTOM_HERO
                            elif action == "confirm_player" and selected_archetype:
                                name = player_name.strip() or f"Gracz {config_player_index + 1}"
                                player = build_player(selected_archetype, name, config_player_index)
                                finish_player_configuration(player)
                        elif state == STATE_CUSTOM_HERO:
                            if action == "back":
                                state = STATE_PLAYER_CONFIG
                            elif action.startswith("stat_plus_"):
                                stat = action.removeprefix("stat_plus_")
                                if stat in custom_stats and sum(custom_stats.values()) < 12 and custom_stats[stat] < 6:
                                    custom_stats[stat] += 1
                            elif action.startswith("stat_minus_"):
                                stat = action.removeprefix("stat_minus_")
                                if stat in custom_stats and custom_stats[stat] > 0:
                                    custom_stats[stat] -= 1
                            elif action == "confirm_custom" and selected_archetype and sum(custom_stats.values()) == 12:
                                name = player_name.strip() or f"Gracz {config_player_index + 1}"
                                player = build_player(selected_archetype, name, config_player_index, custom_stats=dict(custom_stats))
                                finish_player_configuration(player)
                        elif state == STATE_INITIATIVE and action == "start_game":
                            active_player_index = turn_manager.active_player_index
                            selected_token = tokens[active_player_index]
                            selected_token.reset_actions()
                            selected_tile = None
                            camera.center_on_tile(selected_token.tile)
                            state = STATE_GAME
                        elif state == STATE_COUNCIL and action == "close_council":
                            state = STATE_GAME
                            if selected_token:
                                camera.center_on_tile(selected_token.tile)
                        elif state == STATE_MULTIPLAYER:
                            state = STATE_MENU
                        break
                elif state == STATE_CITY:
                    for button in city_buttons:
                        if button.clicked(event.pos):
                            if button.action == "back_to_map":
                                state = STATE_GAME
                            else:
                                selected_city_place = button.action
                            break
                elif state == STATE_GAME:
                    clicked_button = False
                    for button in game_buttons:
                        if button.clicked(event.pos):
                            clicked_button = True
                            if button.action == "end_turn":
                                advance_turn()
                            break
                    if not clicked_button and not drag_moved and not over_ui(event.pos, rects):
                        for tile in tiles:
                            if tile.contains(event.pos, camera):
                                selected_tile = tile
                                if tile.location and tile.location.get("kind") in {"city", "village", "castle"} and selected_token and tile == selected_token.tile:
                                    current_city = tile.location
                                    selected_city_place = None
                                    state = STATE_CITY
                                elif selected_token and selected_token.can_move_to(tile):
                                    selected_token.move_to(tile)
                                break

        if state == STATE_MENU:
            buttons = draw_menu(screen, title_font, font, mouse)
            game_buttons = []
            city_buttons = []
        elif state == STATE_MAP_SELECT:
            buttons = draw_map_select(screen, title_font, font, mouse)
            game_buttons = []
            city_buttons = []
        elif state == STATE_PLAYER_COUNT:
            buttons = draw_player_count(screen, title_font, font, mouse)
            game_buttons = []
            city_buttons = []
        elif state == STATE_PLAYER_CONFIG:
            buttons = draw_player_config(
                screen,
                title_font,
                font,
                small_font,
                mouse,
                config_player_index,
                player_count,
                player_name,
                selected_archetype,
                players,
            )
            game_buttons = []
            city_buttons = []
        elif state == STATE_CUSTOM_HERO:
            buttons = draw_custom_hero(
                screen,
                title_font,
                font,
                small_font,
                mouse,
                config_player_index,
                player_name,
                selected_archetype or HERO_ARCHETYPES[0],
                custom_stats,
            )
            game_buttons = []
            city_buttons = []
        elif state == STATE_INITIATIVE:
            buttons = draw_initiative(screen, title_font, font, small_font, mouse, players, initiative or {})
            game_buttons = []
            city_buttons = []
        elif state == STATE_COUNCIL:
            round_number = turn_manager.round_number if turn_manager else 1
            buttons = draw_council(screen, title_font, font, small_font, mouse, round_number)
            game_buttons = []
            city_buttons = []
        elif state == STATE_MULTIPLAYER:
            buttons = draw_multiplayer(screen, title_font, font, mouse)
            game_buttons = []
            city_buttons = []
        elif state == STATE_CITY:
            buttons = []
            game_buttons = []
            city = current_city or {"name": "Lokacja", "type_name": "Lokacja"}
            city_buttons = draw_city_screen(screen, title_font, font, small_font, mouse, city, selected_city_place)
        elif state == STATE_GAME:
            buttons = []
            city_buttons = []
            screen.fill(BG)
            for tile in tiles:
                valid = selected_token.can_move_to(tile) if selected_token else False
                tile.draw(screen, textures, camera, token_font, hovered=(tile == hovered), selected=(tile == selected_tile), valid_move=valid)
            for index, token in enumerate(tokens):
                token.draw(screen, camera, token_font, selected=(index == active_player_index))

            active_player_index = turn_manager.active_player_index if turn_manager else 0
            selected_token = tokens[active_player_index]
            active_hero = players[active_player_index]
            round_number = turn_manager.round_number if turn_manager else 1
            council_cycle = turn_manager.council_cycle if turn_manager else 1
            game_buttons = draw_game_ui(
                screen,
                font,
                small_font,
                active_hero,
                selected_token,
                selected_tile,
                current_map,
                active_player_index,
                players,
                tokens,
                round_number,
                council_cycle,
            )
            draw_location_tooltip(screen, font, small_font, hovered, mouse)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
