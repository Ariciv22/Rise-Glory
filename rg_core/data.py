import random

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 860
MIN_SCREEN_WIDTH = 1000
MIN_SCREEN_HEIGHT = 700
FPS = 60

HEX_SIZE = 104
# Grafiki terenu maja natywna rozdzielczosc 1254x1254. Zachowujemy ja zamiast
# wstepnie zmniejszac heksy do 512x512 i potem ponownie je powiekszac.
TEXTURE_SIZE = 1254
MAX_MAP_TILES = 64
ACTIONS_PER_TURN = 4
HERO_MOVES_PER_TURN = ACTIONS_PER_TURN
COUNCIL_ROUNDS = 5
MAX_WOUNDS = 4
DRAG_THRESHOLD = 4
ZOOM_STEP = 1.10
MIN_ZOOM = 0.35
# Przy HEX_SIZE=104 zoom 6.0 daje heks ok. 1248 px szerokosci, czyli nadal
# miesci sie w natywnej rozdzielczosci grafiki 1254 px bez sztucznego upscale.
MAX_ZOOM = 6.0
DEFAULT_ZOOM = 1.0

# Przywracamy pelny dekoracyjny panel gornego HUD-u. Same kafle statystyk
# pozostaja powiekszone do 64 px wysokosci i zajmuja okolo polowy tej belki.
TOP_BAR_H = 126
LEFT_PANEL_W = 330
RIGHT_PANEL_W = 300
SIDE_MARGIN = 12
MAP_MARGIN = 28

# Wyrazne stalowe srebro dla glownego tekstu UI. Chlodniejszy i ciemniejszy
# od bieli, aby na ciemnych panelach bylo jednoznacznie odbierane jako srebro.
TEXT = (168, 181, 198)
# Drugoplanowy tekst pozostaje ciemniejszym, matowym stalowym srebrem.
MUTED = (126, 139, 155)
BG = (18, 22, 26)
PANEL = (24, 20, 16)
PANEL_DARK = (15, 13, 11)
GOLD = (145, 104, 48)
ORANGE = (255, 122, 30)
HOVER = (255, 230, 120)
SELECTED = (120, 210, 255)
MOVE = (120, 210, 255)

STATE_MENU = "menu"
STATE_MAP_SELECT = "map_select"
STATE_PLAYER_COUNT = "player_count"
STATE_PLAYER_CONFIG = "player_config"
STATE_CUSTOM_HERO = "custom_hero"
STATE_HERO_SELECT = "hero_select"
STATE_INITIATIVE = "initiative"
STATE_GAME = "game"
STATE_CITY = "city"
STATE_COUNCIL = "council"
STATE_MULTIPLAYER = "multiplayer"

MAP_OPTIONS = [
    ("rosette9", "Rozeta 9x9"),
]

STAT_NAMES = ["Walka", "Handel", "Intryga", "Dyplomacja", "Kultura", "Nauka"]

PLAYER_COLORS = [
    (215, 70, 55),
    (70, 125, 220),
    (65, 170, 85),
    (225, 190, 55),
    (165, 90, 210),
    (235, 125, 45),
]

START_FOOD = "Bochenek chleba"
BASIC_GOODS = [
    "Bandaze",
    "Ziola lecznicze",
    "Lina",
    "Krzesiwo",
    "Pochodnia",
    "Mapa okolicy",
    "Wytrychy",
    "Kamien do ostrzenia",
    "Buklak z woda",
]

HERO_ARCHETYPES = [
    {
        "id": 1,
        "name": "Wojownik",
        "color": (215, 70, 55),
        "stats": {"Walka": 5, "Handel": 2, "Dyplomacja": 2, "Intryga": 1, "Nauka": 1, "Kultura": 1},
        "basic_item": "Prosty miecz",
        "class_item": "Skorzana zbroja",
        "role": "Najlepszy do walki i eskorty.",
    },
    {
        "id": 2,
        "name": "Handlarz",
        "color": (220, 170, 55),
        "stats": {"Handel": 5, "Dyplomacja": 3, "Intryga": 2, "Kultura": 1, "Nauka": 1, "Walka": 0},
        "basic_item": "Sakwa kupca",
        "class_item": "Pierscien kupiecki",
        "role": "Najlepszy do wymiany, kontraktow i towarow.",
    },
    {
        "id": 3,
        "name": "Dyplomata",
        "color": (90, 145, 220),
        "stats": {"Dyplomacja": 5, "Kultura": 3, "Handel": 2, "Nauka": 1, "Intryga": 1, "Walka": 0},
        "basic_item": "Elegancki stroj",
        "class_item": "Pieczec rodu / glejt",
        "role": "Najlepszy do rozmow, lokacji i konfliktow spolecznych.",
    },
    {
        "id": 4,
        "name": "Kulturowiec",
        "color": (170, 95, 210),
        "stats": {"Kultura": 5, "Dyplomacja": 3, "Handel": 1, "Nauka": 1, "Intryga": 1, "Walka": 1},
        "basic_item": "Ozdobny stroj",
        "class_item": "Instrument / kronika",
        "role": "Najlepszy do wydarzen, tlumu i slawy.",
    },
    {
        "id": 5,
        "name": "Intrygant",
        "color": (70, 170, 85),
        "stats": {"Intryga": 5, "Dyplomacja": 2, "Handel": 2, "Walka": 1, "Nauka": 1, "Kultura": 1},
        "basic_item": "Sztylet",
        "class_item": "Kaptur intryganta / pierscien sekretow",
        "role": "Najlepszy do omijania, sabotazu i informacji.",
    },
    {
        "id": 6,
        "name": "Uczony",
        "color": (70, 190, 190),
        "stats": {"Nauka": 5, "Kultura": 2, "Handel": 2, "Dyplomacja": 1, "Intryga": 1, "Walka": 1},
        "basic_item": "Torba badacza",
        "class_item": "Ksiega / mapa ruin",
        "role": "Najlepszy do ruin, mechanizmow i odkrywania slabosci.",
    },
]

TERRAINS = {
    "plains": {"name": "Rowniny", "image": "rowniny.png", "fallback": (112, 156, 76), "weight": 30, "passable": True, "move": 1},
    "forest": {"name": "Las", "image": "las.png", "fallback": (49, 107, 62), "weight": 22, "passable": True, "move": 2},
    "hills": {"name": "Wzgorza", "image": "wzgorza.png", "fallback": (139, 116, 73), "weight": 18, "passable": True, "move": 2},
    "mountain": {"name": "Gory", "image": "gory.png", "fallback": (116, 116, 112), "weight": 12, "passable": True, "move": 2},
    "desert": {"name": "Pustynia", "image": "pustynia.png", "fallback": (194, 165, 92), "weight": 10, "passable": True, "move": 1},
    "tundra": {"name": "Tundra", "image": "tundra.png", "fallback": (145, 170, 154), "weight": 8, "passable": True, "move": 1},
}


def clone_hero(template, world_name=None, player_index=0, stats=None):
    from rg_engine.heroes import ensure_hero_state

    hero = dict(template)
    hero["archetype_id"] = template["id"]
    hero["archetype_name"] = template["name"]
    hero["archetype_color"] = template["color"]
    hero["stats"] = dict(stats if stats is not None else template["stats"])
    hero["name"] = (world_name or template["name"]).strip()
    hero["player_number"] = player_index + 1
    hero["player_color"] = PLAYER_COLORS[player_index % len(PLAYER_COLORS)]
    hero["color"] = hero["player_color"]
    hero["gold"] = 5
    hero["wounds"] = 0
    hero["legend"] = 0
    hero["food"] = [START_FOOD]
    hero["goods"] = [random.choice(BASIC_GOODS)]
    hero["custom_stats"] = stats is not None
    return ensure_hero_state(hero)


def map_name(key):
    return next((name for item_key, name in MAP_OPTIONS if item_key == key), "Mapa")