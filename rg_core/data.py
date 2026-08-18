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

TOP_BAR_H = 126
LEFT_PANEL_W = 330
RIGHT_PANEL_W = 300
SIDE_MARGIN = 12
MAP_MARGIN = 28

# Chlodne srebro dla glownego tekstu UI. Jest wyraznie bardziej metaliczne
# od poprzedniej prawie-bieli, ale nadal zachowuje wysoki kontrast na ciemnych panelach.
TEXT = (205, 210, 218)
# Drugoplanowy tekst pozostaje ciemniejszym, matowym srebrem.
MUTED = (158, 164, 172)
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
        "id": "warrior",
        "name": "Wojownik",
        "role": "Najlepszy do walki i eskorty.",
        "stats": {"Walka": 5, "Handel": 2, "Dyplomacja": 2, "Intryga": 1, "Nauka": 1, "Kultura": 1},
        "item": "Prosty miecz",
        "class_item": "Skorzana zbroja",
    },
    {
        "id": "merchant",
        "name": "Handlarz",
        "role": "Zarabia i handluje korzystniej.",
        "stats": {"Walka": 1, "Handel": 5, "Dyplomacja": 2, "Intryga": 2, "Nauka": 1, "Kultura": 1},
        "item": "Waga kupiecka",
        "class_item": "Sakiewka kupiecka",
    },
    {
        "id": "diplomat",
        "name": "Dyplomata",
        "role": "Rozwiazuje konflikty i negocjuje.",
        "stats": {"Walka": 1, "Handel": 2, "Dyplomacja": 5, "Intryga": 1, "Nauka": 1, "Kultura": 2},
        "item": "List polecajacy",
        "class_item": "Pieczec dyplomatyczna",
    },
    {
        "id": "intriguer",
        "name": "Intrygant",
        "role": "Szpieg, manipulant i mistrz podstepu.",
        "stats": {"Walka": 1, "Handel": 2, "Dyplomacja": 1, "Intryga": 5, "Nauka": 1, "Kultura": 2},
        "item": "Wytrychy",
        "class_item": "Zakapturzony plaszcz",
    },
    {
        "id": "scholar",
        "name": "Uczony",
        "role": "Badacz ruin, klatw i tajemnic.",
        "stats": {"Walka": 1, "Handel": 1, "Dyplomacja": 2, "Intryga": 1, "Nauka": 5, "Kultura": 2},
        "item": "Pochodnia",
        "class_item": "Stara ksiega",
    },
    {
        "id": "cultured",
        "name": "Czlowiek kultury",
        "role": "Artysta, bard i znawca obyczajow.",
        "stats": {"Walka": 1, "Handel": 1, "Dyplomacja": 2, "Intryga": 1, "Nauka": 2, "Kultura": 5},
        "item": "Lutnia",
        "class_item": "Ozdobny stroj",
    },
]


def clone_hero(archetype, world_name="Bohater", player_index=0, stats=None):
    return {
        "name": world_name,
        "player_number": player_index + 1,
        "player_color": PLAYER_COLORS[player_index % len(PLAYER_COLORS)],
        "archetype_id": archetype["id"],
        "archetype_name": archetype["name"],
        "role": archetype["role"],
        "stats": dict(stats if stats is not None else archetype["stats"]),
        "basic_item": archetype["item"],
        "class_item": archetype["class_item"],
        "food": [START_FOOD],
        "goods": ["Lina"],
        "gold": 5,
        "legend": 0,
        "wounds": 0,
        "helpers": [],
        "inventory": [],
        "equipment": {},
        "active_quests": [],
        "completed_quests": [],
        "failed_quests": [],
        "abandoned_quests": [],
    }


def map_name(map_key):
    return dict(MAP_OPTIONS).get(map_key, map_key)
