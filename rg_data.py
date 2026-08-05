import random

from rg_content import load_archetypes, load_item_pools
from rg_models import Hero

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 860
MIN_SCREEN_WIDTH = 1000
MIN_SCREEN_HEIGHT = 700
FPS = 60

HEX_SIZE = 104
TEXTURE_SIZE = 512
MAX_MAP_TILES = 64
ACTIONS_PER_TURN = 4
HERO_MOVES_PER_TURN = ACTIONS_PER_TURN
COUNCIL_ROUNDS = 5
MAX_WOUNDS = 4
DRAG_THRESHOLD = 4
ZOOM_STEP = 1.10
MIN_ZOOM = 0.35
MAX_ZOOM = 1.55
DEFAULT_ZOOM = 1.0

TOP_BAR_H = 126
LEFT_PANEL_W = 330
RIGHT_PANEL_W = 300
SIDE_MARGIN = 12
MAP_MARGIN = 28

TEXT = (235, 235, 235)
MUTED = (180, 185, 190)
BG = (18, 22, 26)
PANEL = (24, 20, 16)
PANEL_DARK = (15, 13, 11)
GOLD = (145, 104, 48)
ORANGE = (255, 122, 30)
HOVER = (255, 230, 120)
SELECTED = (120, 210, 255)
MOVE = (120, 210, 255)

STATE_START_INTRO = "start_intro"
STATE_MENU = "menu"
STATE_MAP_SELECT = "map_select"
STATE_PLAYER_COUNT = "player_count"
STATE_PLAYER_CONFIG = "player_config"
STATE_CUSTOM_HERO = "custom_hero"
STATE_HERO_SELECT = "hero_select"
STATE_INTRO = "intro"
STATE_INITIATIVE = "initiative"
STATE_GAME = "game"
STATE_CITY = "city"
STATE_COUNCIL = "council"
STATE_MULTIPLAYER = "multiplayer"

MAP_OPTIONS = [("rosette9", "Rozeta 9x9")]
STAT_NAMES = ["Walka", "Handel", "Intryga", "Dyplomacja", "Kultura", "Nauka"]
PLAYER_COLORS = [(215,70,55),(70,125,220),(65,170,85),(225,190,55),(165,90,210),(235,125,45)]
START_FOOD = "Bochenek chleba"
HERO_ARCHETYPES = list(load_archetypes())
BASIC_GOODS = [item.name for item in load_item_pools()["basic_good"]]

TERRAINS = {
    "plains": {"name":"Rowniny","image":"rowniny.png","fallback":(112,156,76),"weight":30,"passable":True,"move":1},
    "forest": {"name":"Las","image":"las.png","fallback":(49,107,62),"weight":22,"passable":True,"move":2},
    "hills": {"name":"Wzgorza","image":"wzgorza.png","fallback":(139,116,73),"weight":18,"passable":True,"move":2},
    "mountain": {"name":"Gory","image":"gory.png","fallback":(116,116,112),"weight":12,"passable":True,"move":2},
    "desert": {"name":"Pustynia","image":"pustynia.png","fallback":(194,165,92),"weight":10,"passable":True,"move":1},
    "tundra": {"name":"Tundra","image":"tundra.png","fallback":(145,170,154),"weight":8,"passable":True,"move":1},
}


def clone_hero(template, world_name=None, player_index=0, stats=None):
    player_color = PLAYER_COLORS[player_index % len(PLAYER_COLORS)]
    return Hero(
        archetype_id=template["id"],
        archetype_name=template["name"],
        archetype_color=template["color"],
        stats=dict(stats if stats is not None else template["stats"]),
        name=(world_name or template["name"]).strip(),
        player_number=player_index + 1,
        player_color=player_color,
        color=player_color,
        basic_item=template["basic_item"],
        class_item=template["class_item"],
        role=template["role"],
        gold=5,
        wounds=0,
        legend=0,
        food=[START_FOOD],
        goods=[random.choice(BASIC_GOODS)],
        custom_stats=stats is not None,
    )


def map_name(key):
    return next((name for item_key, name in MAP_OPTIONS if item_key == key), "Mapa")
