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
    STATE_GAME,
    STATE_HERO_SELECT,
    STATE_MAP_SELECT,
    STATE_MENU,
    STATE_MULTIPLAYER,
    ZOOM_STEP,
    clone_hero,
)
from rg_hud import draw_game_ui
from rg_map import Camera, HeroToken, find_start_tile, load_textures
from rg_screens import draw_hero_select, draw_map_select, draw_menu, draw_multiplayer
from rg_ui import over_ui, ui_rects
from rg_world import generate_world


def create_window(fullscreen=False):
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)


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
    active_player = 1
    hero = clone_hero(HERO_ARCHETYPES[0])
    tiles = generate_world(current_map)
    token = HeroToken(hero, find_start_tile(tiles))
    camera.center_on_tile(token.tile)
    selected_tile = None
    selected_token = token
    buttons = []
    game_buttons = []
    dragging = False
    drag_moved = False
    drag_start = (0, 0)
    last_mouse = (0, 0)
    fullscreen = False
    running = True

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
                if state == STATE_GAME:
                    camera.center_on_tile(token.tile)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = STATE_MENU if state != STATE_MENU else STATE_MENU
                elif event.key == pygame.K_SPACE and state == STATE_GAME:
                    camera.center_on_tile(token.tile)
                elif event.key in [pygame.K_TAB, pygame.K_n] and state == STATE_GAME:
                    active_player = active_player % 4 + 1
                    token.reset_moves()
                elif event.key == pygame.K_r and state == STATE_GAME:
                    tiles = generate_world(current_map)
                    token = HeroToken(hero, find_start_tile(tiles))
                    camera.center_on_tile(token.tile)
                    selected_token = token
                    selected_tile = None
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = create_window(True)
                        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
                    else:
                        SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1000
                        screen = create_window(False)
                    if state == STATE_GAME:
                        camera.center_on_tile(token.tile)
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
                if state in [STATE_MENU, STATE_MAP_SELECT, STATE_HERO_SELECT, STATE_MULTIPLAYER]:
                    for button in buttons:
                        if button.clicked(event.pos):
                            if state == STATE_MENU:
                                if button.action == "new":
                                    state = STATE_MAP_SELECT
                                elif button.action == "multi":
                                    state = STATE_MULTIPLAYER
                                elif button.action == "exit":
                                    running = False
                            elif state == STATE_MAP_SELECT:
                                if button.action == "back":
                                    state = STATE_MENU
                                else:
                                    current_map = button.action
                                    state = STATE_HERO_SELECT
                            elif state == STATE_HERO_SELECT:
                                if button.action == "back":
                                    state = STATE_MAP_SELECT
                                else:
                                    template = next(item for item in HERO_ARCHETYPES if item["id"] == int(button.action))
                                    hero = clone_hero(template)
                                    active_player = 1
                                    tiles = generate_world(current_map)
                                    token = HeroToken(hero, find_start_tile(tiles))
                                    camera.center_on_tile(token.tile)
                                    selected_token = token
                                    selected_tile = None
                                    state = STATE_GAME
                            elif state == STATE_MULTIPLAYER:
                                state = STATE_MENU
                            break
                elif state == STATE_GAME:
                    dragging = False
                    clicked_button = False
                    for button in game_buttons:
                        if button.clicked(event.pos):
                            clicked_button = True
                            if button.action == "end_turn":
                                active_player = active_player % 4 + 1
                                token.reset_moves()
                            break
                    if not clicked_button and not drag_moved and not over_ui(event.pos, rects):
                        for tile in tiles:
                            if tile.contains(event.pos, camera):
                                selected_tile = tile
                                if selected_token and selected_token.can_move_to(tile):
                                    selected_token.move_to(tile)
                                elif tile == token.tile:
                                    selected_token = token
                                else:
                                    selected_token = None
                                break

        if state == STATE_MENU:
            buttons = draw_menu(screen, title_font, font, mouse)
            game_buttons = []
        elif state == STATE_MAP_SELECT:
            buttons = draw_map_select(screen, title_font, font, mouse)
            game_buttons = []
        elif state == STATE_HERO_SELECT:
            buttons = draw_hero_select(screen, title_font, font, small_font, mouse)
            game_buttons = []
        elif state == STATE_MULTIPLAYER:
            buttons = draw_multiplayer(screen, title_font, font, mouse)
            game_buttons = []
        elif state == STATE_GAME:
            screen.fill(BG)
            for tile in tiles:
                valid = selected_token.can_move_to(tile) if selected_token else False
                tile.draw(screen, textures, camera, token_font, hovered=(tile == hovered), selected=(tile == selected_tile), valid_move=valid)
            token.draw(screen, camera, token_font, selected=(selected_token == token))
            game_buttons = draw_game_ui(screen, font, small_font, hero, token, selected_tile, current_map, active_player)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
