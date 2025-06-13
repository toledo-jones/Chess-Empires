import pygame

"""
Settings for the game. These values are meant to be tweaked and adjusted to quickly modify gameplay behaviors. 
"""

# Uncomment the section below to enable debug

# DEBUG_START = True
# DISPLAY_STATE_IN_HUD = True
# BOARD_STARTS_WITH_RESOURCES = False
# DEBUG_RITUALS = True
# POP_UPS_ON = False
# SHOW_STONE = False

# Debug settings
DEBUG_STARTING_PRAYER = 200
DEBUG_STARTING_WOOD = 100
DEBUG_STARTING_GOLD = 100
DEBUG_STARTING_STONE = 100
DEBUG_STARTING_PIECES = ["castle", "king", "magician", "monk", "prayer_stone"]

# Window and board sizes
MAX_FPS = 120
VERSION = "alpha 0.05"
NUMBER = ""
pygame.init()
BOARD_HEIGHT_PX = pygame.display.Info().current_h
SQ_SIZE = BOARD_HEIGHT_PX // 10
BOARD_HEIGHT_SQ = BOARD_HEIGHT_PX // SQ_SIZE
BOARD_WIDTH_SQ = 14
BOARD_WIDTH_PX = BOARD_WIDTH_SQ * SQ_SIZE
SIDE_MENU_WIDTH = pygame.display.Info().current_w - BOARD_WIDTH_PX
BOARD_HEIGHT_PX = pygame.display.Info().current_h

# Colors
HIGHLIGHT_ALPHA = 110
MENU_COLOR = pygame.Color((72, 61, 139))
LIGHT_SQUARE_COLOR = pygame.Color((255, 255, 255, 255))
DARK_SQUARE_COLOR = pygame.Color((66.3, 33.6, 21.4, 255))
TINT_COLORS = pygame.Color((225.2, 212.4, 172.6, 255))
UNUSED_PIECE_HIGHLIGHT_COLOR = pygame.Color((237, 225, 199, HIGHLIGHT_ALPHA))
MOVE_SQUARE_HIGHLIGHT_COLOR = pygame.Color((199, 202, 237, HIGHLIGHT_ALPHA))
SELF_SQUARE_HIGHLIGHT_COLOR = pygame.Color(
    0, 0, 255, HIGHLIGHT_ALPHA
)  # Blue with alpha
CHECK_SQUARE_HIGHLIGHT_COLOR = pygame.Color(
    255, 0, 0, HIGHLIGHT_ALPHA
)  # Red with alpha

GOLD = pygame.Color("gold")
DARK_ORANGE = pygame.Color("dark orange")
WHITE = pygame.Color("white")
BLACK = pygame.Color("black")
BLUE = pygame.Color("blue")
RED = pygame.Color("red")

# Toggles
ACTIONS_UPDATE_ON_SPAWN = False
MINING_COSTS_ACTION = False
PRAYING_COSTS_ACTION = False
STEALING_COSTS_ACTION = False
PERSUADE_COSTS_ACTION = True
QUARRY_COSTS_ACTION = False
QUARRY_COSTS_RESOURCE = False
TRAP_COSTS_ACTION = False
TURN_CHANGE_AFTER_START_SPAWN = True

# Lists
SELECTABLE_STARTING_PIECES = ["pawn", "ferz", "rogue_pawn", "builder"]
BONUS_STARTING_PIECES = ["trader", "pikeman", "trapper", "monk"]
MASTER_COST_LIST = [
    "builder",
    "monk",
    "stable",
    "castle",
    "barracks",
    "fortress",
    "circus",
]
STABLE_SPAWN_LIST = {
    -1: ["unicorn", "elephant", "knight"],
    0: ["doe", "oxen", "ram"],
}
FORTRESS_SPAWN_LIST = {
    0: ["duke"],
    -1: ["rogue_rook", "rogue_bishop", "rogue_knight", "rogue_pawn", "trapper"],
}
CASTLE_SPAWN_LIST = {
    -1: ["pawn", "ferz", "builder", "monk", "trader"],
    0: ["cavalry", "pikeman"],
}
BUILDER_SPAWN_LIST = ["wall", "stable", "castle", "barracks", "fortress", "circus"]
BARRACKS_SPAWN_LIST = {
    -1: ["rook", "bishop"],
    0: ["war_tower", "queen", "champion"],
}
CIRCUS_SPAWN_LIST = {
    -1: [
        "jester",
        "persuader",
        "assassin",
    ],
    0: [
        "lion",
        "fire_spinner",
        "acrobat",
        "magician",
    ],
}


TRAPPER_SPAWN_LIST = ["trap"]
MONK_SPAWN_LIST = ["monolith", "prayer_stone"]
STARTING_PIECES = ["castle", "king"]
SPAWN_LISTS = {
    "stable": STABLE_SPAWN_LIST,
    "fortress": FORTRESS_SPAWN_LIST,
    "castle": CASTLE_SPAWN_LIST,
    "builder": BUILDER_SPAWN_LIST,
    "barracks": BARRACKS_SPAWN_LIST,
    "circus": CIRCUS_SPAWN_LIST,
    "trapper": TRAPPER_SPAWN_LIST,
    "monk": MONK_SPAWN_LIST,
}

FACTION_NAMES = [
    "clique",
    "coterie",
    "cabal",
    "bloc",
    "camp",
    "grouping",
    "side",
    "division",
    "wing",
    "section",
    "countrymen",
    "squad",
    "faction",
    "company",
    "troupe",
    "set",
    "army",
    "party",
    "gang",
    "selection",
    "crew",
    "corps",
    "lineup",
    "sect",
    "band",
    "color",
    "people",
    "squadron",
    "group",
    "allegiance",
    "choice",
    "entourage",
    "aisle",
    "allegiance",
    "cabinet",
    "color",
    "creed",
]
MONOLITH_RITUALS = ["gold_general", "line_destroy", "smite"]
ASSASSIN_RITUALS = ["swap"]
PRAYER_STONE_RITUALS = [
    "protect",
    "swap",
    "teleport",
    "create_resource",
    "portal",
    "destroy_resource",
]
MAGICIAN_RITUALS = ["portal", "swap", "teleport"]

# Values
DECREE_COST = {"gold": 35}
DECREE_INCREMENT = 5
DEFAULT_PIECE_LIMIT = 3
TRADING_GIVE_BOUNDS = (5 / 8, 1 / 2)
TRADING_RECEIVE_BOUNDS = (5 / 8, 15 / 16)
NUMBER_OF_STARTING_PIECES = 4
NUMBER_OF_BONUS_PIECES = 1
DEFAULT_ACTIONS_REMAINING = 1
PRAYER_STONE_YIELD = 2
MONOLITH_YIELD = 2
CASTLE_ADDITIONAL_ACTIONS = 0
BARRACKS_ADDITIONAL_ACTIONS = 0
FORTRESS_ADDITIONAL_ACTIONS = 0
STABLE_ADDITIONAL_ACTIONS = 0
MONOLITH_ADDITIONAL_ACTIONS = 0
PRAYER_STONE_ADDITIONAL_ACTIONS = 0
CIRCUS_ADDITIONAL_ACTIONS = 0
ADDITIONAL_PRAYER_FROM_MONK = 1
MAX_MONOLITH_RITUALS_PER_TURN = 1
MAX_PRAYER_STONE_RITUALS_PER_TURN = 2
MAX_MAGICIAN_RITUALS_PER_TURN = 1

# Dictionaries
PIECE_POINT_VALUES = {
    "king": 8,
    "queen": 32,
    "rook": 16,
    "bishop": 16,
    "knight": 8,
    "pawn": 4,
    "castle": 4,
    "monk": 4,
    "fortress": 13,
    "ram": 24,
    "elephant": 16,
    "barracks": 24,
    "jester": 6,
    "champion": 28,
    "prayer_stone": 4,
    "monolith": 8,
    "pikeman": 8,
    "rogue_rook": 16,
    "rogue_bishop": 16,
    "rogue_knight": 8,
    "rogue_pawn": 4,
    "builder": 7,
    "unicorn": 16,
    "stable": 18,
    "gold_general": 32,
    "duke": 32,
    "oxen": 24,
    "wall": 12,
    "doe": 24,
    "persuader": 8,
    "trader": 4,
    "circus": 12,
    "trapper": 4,
    "trap": 1,
    "lion": 24,
    "fire_spinner": 16,
    "acrobat": 16,
    "magician": 8,
    "cavalry": 8,
    "ferz": 4,
    "assassin": 8,
    "war_tower": 20,
}

NOTIFICATIONS = {
    None: ["cannot select"],
    "invalid_start_spawn": ["select a valid spawn square"],
    "non_occupyable": ["square cannot be occupied"],
    "players_nearby": ["a player is too close"],
    "open_spaces": ["not enough open spaces"],
    "piece_action": ["no piece actions remaining"],
    "player_action": ["no turn actions remaining"],
    "invalid_move": ["cannot move to that square"],
    "resources": ["not enough resources to build"],
    "check": ["your king is in check"],
}
DESCRIPTIONS = {
    "king": [
        "every player gets one.",
        "'right click' to surrender.",
        "checkmate your opponent's and they will have to surrender",
    ],
    "gold_general": ["???"],
    "quarry_1": [
        "can be mined for stone.",
        "may cave in and begin to yield less stone.",
        "eventually becomes depleted if mined after it caves in.",
    ],
    "pawn": [
        "moves two spaces orthogonally on it's first move.",
        "'right click' to harvest resources.",
        "captures one space diagonally.",
    ],
    "ferz": [
        "moves two spaces diagonally on it's first move.",
        "'right click' to harvest resources.",
        "captures one space orthogonally.",
    ],
    "builder": [
        "'right click' to spawn buildings.",
        "buildings can spawn more powerful pieces.",
        "'right click' to harvest resources.",
    ],
    "monk": [
        "'right click' to pray at monoliths or prayer stones to cast powerful rituals."
    ],
    "pikeman": [
        "moves or captures one square in every direction.",
        "a valuable defender.",
        "can capture walls.",
    ],
    "castle": ["'right click' to spawn essential pieces such as pawns and builders."],
    "stable": [
        "'right click' to spawn leapers like knights and elephants.",
        "all leapers can capture walls.",
    ],
    "barracks": [
        "'right click' to spawn standard chess pieces such as rooks and bishops."
    ],
    "fortress": [
        "'right click' to spawn rogue versions of the standard chess pieces.",
        "rogue pieces move through forest tiles and steal resources from enemy pieces.",
    ],
    "queen": [
        "the most powerful piece in a standard chess set.",
        "slides to move and captures in all " "directions.",
        "'right click' ban rituals for a resource cost unique to each map!",
    ],
    "rook": [
        "slides to capture and attack orthogonally",
        "'right click' to pray at prayer sites.",
    ],
    "bishop": [
        "slides to capture and attack diagonally",
        "'right click' to pray at prayer sites.",
    ],
    "knight": [
        "leaps over another piece up two and over one.",
        "able to capture walls.",
    ],
    "jester": [
        "slides to move in all directions.",
        "pieces nearby are distracted and cannot perform any actions such as moving or mining.",
    ],
    "rogue_rook": [
        "slides to capture and attack orthogonally.",
        "'right click' to steal resources from enemy " "pieces.",
        "can move through and land on forest tiles.",
    ],
    "rogue_bishop": [
        "moves diagonally.",
        "can steal a resource of your choosing from a piece of the opposite color.",
        "can move through and land on forest tiles.",
    ],
    "rogue_knight": [
        "leaps over another piece up two and over one.",
        "'right click' to steal resources from enemy ",
        "pieces.",
        "can land on forest tiles.",
    ],
    "rogue_pawn": [
        "moves two spaces orthogonally on it's first move.",
        "'right click' to harvest resources.",
        "'right click' to steal resources from enemy pieces.",
        "captures one space diagonally.",
        "can move through and land on forest tiles.",
    ],
    "oxen": [
        "leaps over another piece up two and over one.",
        "after leaping, slides to move orthogonally.",
        "can capture walls.",
    ],
    "champion": [
        "moves diagonally one square.",
        "after moving, slides to move orthogonally.",
    ],
    "assassin": [
        "'right click' to swap places with an enemy piece.",
        "captures one space in all directions",
    ],
    "elephant": [
        "leaps over another piece up two and over one.",
        "if it's knight move was unobstructed it can move forward one more square",
        "can capture walls.",
    ],
    "ram": [
        "leaps over another piece up two and over one,",
        "then slides diagonally.",
        "can capture walls.",
    ],
    "unicorn": [
        "leaps over another piece up two and over one.",
        "leaps over another piece two spaces orthogonally.",
        "makes an additional knight move if nothing obstructs it's movement.",
        "can capture walls.",
    ],
    "monolith": [
        "'right click' to cast powerful rituals.",
        "rituals cost prayer to use.",
        "prayer is obtained by using a praying piece on a monolith or a prayer stone.",
    ],
    "prayer_stone": [
        "'right click' to cast useful rituals.",
        "rituals cost prayer to use.",
        "prayer is obtained by using a praying piece on a monolith or a prayer stone.",
    ],
    "duke": [
        "the brother of the queen.",
        "slides to move and captures in all " "directions.",
        "'right click' to steal resources from enemy pieces.",
        "can move through and land on forest tiles.",
    ],
    "smite": [
        "select one piece or building to be destroyed.",
        "you cannot smite the king.",
    ],
    "destroy_resource": ["select one resource to be destroyed"],
    "create_resource": ["create a resource of any kind."],
    "wall": ["can only be captured by pieces in the stable or pikeman."],
    "teleport": ["teleport a piece anywhere else on the board."],
    "swap": ["one of your pieces swaps position with one of the enemy's pieces"],
    "line_destroy": ["destroys everything in it's path"],
    "protect": ["protects a square from capture, destruction or being moved through."],
    "doe": [
        "leaps over another piece up two and over one.",
        "slides to move diagonally.",
        "can capture walls.",
    ],
    "persuader": ["'right click' to convert the color of nearby pieces"],
    "portal": [
        "creates a portal on any two squares.",
        "pieces who land on either square will be transported to the other one.",
    ],
    "trader": [
        "'right click' to give one resource and receive another. ",
        "the first menu that appears is the resource you give.",
        "the second menu that appears is the resource you get.",
    ],
    "circus": [
        "'right click' to spawn exotic chess pieces such as the jester and persuader."
    ],
    "lion": [
        "leaps over another piece up two and over one.",
        "slides to move orthogonally.",
    ],
    "fire_spinner": [
        "leaps over another piece up two and over one.",
        "makes an additional 2 knight moves if nothing obstructs it's movement",
    ],
    "acrobat": [
        "slides to capture and attack diagonally",
        "can move through one piece and capture a piece behind it.",
    ],
    "trapper": [
        "moves two spaces orthogonally on it's first move.",
        "'right click' to spawn traps.",
        "traps destroy an enemy piece that lands on them.",
        "captures one space diagonally.",
        "can move through and land on forest tiles.",
    ],
    "magician": [
        "moves one space in every direction.",
        "'right click' to cast rituals for a gold cost",
    ],
    "cavalry": [
        "leaps over another piece up two and over one for it's first move.",
        "moves one space orthogonally after it's first move.",
        "'right click' to harvest resources.",
    ],
    "war_tower": [
        "slides to move orthogonally.",
        "'right click' to arm for explosion.",
        "explosion destroys everything in a radius of 1 square.",
    ],
}

PIECE_POPULATION = {
    "king": 1,
    "queen": 1,
    "rook": 1,
    "bishop": 1,
    "knight": 1,
    "pawn": 1,
    "castle": 0,
    "duke": 1,
    "rogue_bishop": 1,
    "jester": 1,
    "rogue_rook": 1,
    "war_tower": 0,
    "elephant": 1,
    "pikeman": 1,
    "champion": 1,
    "gold_general": 6,
    "silver_general": 1,
    "elephant_cart": 1,
    "flag": 0,
    "barracks": 0,
    "rogue_pawn": 1,
    "monolith": 0,
    "prayer_stone": 0,
    "monk": 1,
    "fortress": 0,
    "rogue_knight": 1,
    "builder": 1,
    "quarry_1": 0,
    "stable": 0,
    "unicorn": 1,
    "ram": 1,
    "oxen": 1,
    "wall": 0,
    "doe": 1,
    "persuader": 1,
    "trader": 1,
    "circus": 0,
    "trapper": 1,
    "trap": 0,
    "lion": 1,
    "fire_spinner": 1,
    "acrobat": 1,
    "magician": 1,
    "cavalry": 1,
    "ferz": 1,
    "assassin": 1,
}
RITUAL_STRENGTH = {"gold_general": 12,
                   "smite": 12,
                   "destroy_resource": 6,
                   "create_resource": 5,
                   "teleport": 6,
                   "swap": 2,
                   "line_destroy": 9,
                   "portal": 2,
                   "protect": 2
}


# PRAYER_COSTS = {
#     "gold_general": {
#         "prayer": 12,
#         "monk": 2,
#         "gold": 0,
#     },
#     "smite": {
#         "prayer": 12,
#         "monk": 1,
#         "gold": 0,
#     },
#     "destroy_resource": {"prayer": 6, "monk": 0, "gold": 0},
#     "create_resource": {"prayer": 5, "monk": 0, "gold": 0},
#     "teleport": {"prayer": 6, "monk": 0, "gold": 4},
#     "swap": {"prayer": 2, "monk": 0, "gold": 3},
#     "line_destroy": {"prayer": 9, "monk": 1, "gold": 0},
#     "portal": {"prayer": 2, "monk": 0, "gold": 2},
#     "protect": {"prayer": 2, "monk": 0, "gold": 0},
# }
ADDITIONAL_PIECE_LIMIT = {
    "castle": 5,
    "castle_0": 9,
    "castle_1": 100,
    "barracks": 5,
    "barracks_0": 9,
    "fortress": 3,
    "fortress_0": 7,
    "stable": 3,
    "stable_0": 7,
    "circus": 3,
    "circus_0": 6,
    "king": 0,
    "queen": 0,
    "rook": 0,
    "bishop": 0,
    "knight": 0,
    "pawn": 0,
    "monk": 0,
    "jester": 0,
    "silver_general": 0,
    "gold_general": 0,
    "pikeman": 0,
    "champion": 0,
    "rogue_rook": 0,
    "rogue_bishop": 0,
    "rogue_knight": 0,
    "rogue_pawn": 0,
    "elephant": 0,
    "elephant_cart": 0,
    "monolith": 2,
    "prayer_stone": 1,
    "wall": 0,
    "flag": 0,
    "duke": 0,
    "war_tower": 0,
    "quarry_1": 0,
    "builder": 0,
    "unicorn": 0,
    "ram": 0,
    "oxen": 0,
    "doe": 0,
    "persuader": 0,
    "trader": 0,
    "trapper": 0,
    "trap": 0,
    "lion": 0,
    "fire_spinner": 0,
    "acrobat": 0,
    "magician": 0,
    "cavalry": 0,
    "ferz": 0,
    "assassin": 0,
}
BASE_TOTAL_YIELD = {"wood": 8, "gold": 25, "quarry": 8, "sunken_quarry": 1}
TOTAL_YIELD_VARIANCE = {
    "wood": (-2, 2),
    "gold": (-3, 3),
    "quarry": (-1, 2),
    "sunken_quarry": (0, 1),
}
BASE_YIELD_PER_HARVEST = {
    "pawn": {"wood": 10, "gold": 7, "quarry": 5, "sunken_quarry": 1},
    "ferz": {"wood": 10, "gold": 7, "quarry": 5, "sunken_quarry": 1},
    "rogue_pawn": {"wood": 7, "gold": 2, "quarry": 4, "sunken_quarry": 1},
    "cavalry": {"wood": 10, "gold": 7, "quarry": 5, "sunken_quarry": 1},
    "builder": {"wood": 7, "gold": 2, "quarry": 4, "sunken_quarry": 1},
}
HARVEST_YIELD_VARIANCE = {
    "wood": (-2, 2),
    "gold": (-2, 2),
    "quarry": (-2, 2),
    "sunken_quarry": (0, 1),
}
STEALING_KEY = {
    "building": {
        "wood": {"variance": (-2, 2), "value": 5},
        "gold": {"variance": (-2, 2), "value": 5},
        "stone": {"variance": (-2, 2), "value": 5},
    },
    "trader": {
        "wood": {"variance": (-3, 4), "value": 15},
        "gold": {"variance": (-3, 4), "value": 15},
        "stone": {"variance": (-3, 4), "value": 15},
    },
    "piece": {
        "wood": {"variance": (-2, 2), "value": 4},
        "gold": {"variance": (-2, 2), "value": 4},
        "stone": {"variance": (-2, 2), "value": 4},
    },
}

# Sound
SOUND_EFFECT_VOLUME = 0.5

# Sprite scaling and sizes
DEFAULT_PIECE_SCALE = (SQ_SIZE, SQ_SIZE)
SPAWNING_MENU_WIDTH = round(SQ_SIZE * 5.5)
SPAWNING_MENU_HEIGHT_BUFFER = SQ_SIZE * 1.3
SIDE_MENU_HEIGHT = BOARD_HEIGHT_PX
GAME_NAME_SCALE = (round(SQ_SIZE * 1.5), round(SQ_SIZE * 1.5))
PICKAXE_SCALE = (SQ_SIZE * 2, SQ_SIZE * 2)
CENTER_X = BOARD_WIDTH_SQ * SQ_SIZE // 2 + SQ_SIZE // 2
CENTER_Y = BOARD_HEIGHT_SQ * SQ_SIZE // 2
KING_MENU_HEIGHT = (SQ_SIZE // 6) * 2 + SQ_SIZE
KING_MENU_WIDTH = KING_MENU_HEIGHT
DECREE_SCALE = round(SQ_SIZE * 9 / 10), round(SQ_SIZE * 9 / 10)
START_MENU_WIDTH = round(SQ_SIZE * 6.5)
START_MENU_HEIGHT = round(SQ_SIZE * 3.5)
PRAYER_BAR_WIDTH = round(SQ_SIZE // 64)
PRAYER_BAR_END_WIDTH = round(SQ_SIZE // 6)
PRAYER_BAR_HEIGHT = round(SQ_SIZE // 2.8)
PRAYER_BAR_SCALE = (PRAYER_BAR_WIDTH, PRAYER_BAR_HEIGHT)
PRAYER_BAR_END_SCALE = (PRAYER_BAR_END_WIDTH, PRAYER_BAR_HEIGHT)
TREE_SCALE = (round(SQ_SIZE * 1.4), round(SQ_SIZE * 1.4))
GOLD_SCALE = (round(SQ_SIZE * 1.3), round(SQ_SIZE * 1.3))
QUARRY_SCALE = (round(SQ_SIZE * 1.1), round(SQ_SIZE * 1.1))
TREE_OFFSET = 0, 0
GOLD_OFFSET = 0, 0
CASTLE_SCALE = round(SQ_SIZE * 1.1), round(SQ_SIZE * 1.1)
CASTLE_OFFSET = (0, -10)
MENU_ICON_DEFAULT_SCALE = (SQ_SIZE // 2, SQ_SIZE // 2)
BARRACKS_SCALE = (round(SQ_SIZE * 1.2), round(SQ_SIZE * 1.2))
BARRACKS_OFFSET = (-10, -10)
PAWN_MENU_ICON_SCALE = (100, 100)
FORTRESS_SCALE = (round(SQ_SIZE * 1.15), round(SQ_SIZE * 1.15))
FORTRESS_OFFSET = (0, -10)
WALL_OFFSET = (-10, -10)
PRAYER_RITUAL_SCALE = (round(SQ_SIZE * 1.5), round(SQ_SIZE * 1.5))
RESOURCES_BUTTON_SCALE = (SIDE_MENU_WIDTH, 2 * SQ_SIZE)
YES_NO_BUTTON_SCALE = (SQ_SIZE // 3, SQ_SIZE // 3)
CONTEXTUAL_MENU_ICON_DEFAULT_SCALE = (SQ_SIZE // 2, SQ_SIZE // 2)
PROTECT_SQUARE_SCALE = (SQ_SIZE, SQ_SIZE)
PROTECT_SQUARE_OFFSET = (
    SQ_SIZE // 2 - PROTECT_SQUARE_SCALE[0] // 2,
    SQ_SIZE // 2 - PROTECT_SQUARE_SCALE[1] // 2,
)

# Image Modify
RITUAL_IMAGE_MODIFY = {
    "gold_general": {"SCALE": PRAYER_RITUAL_SCALE, "OFFSET": (0, 0)},
    "smite": {"SCALE": PRAYER_RITUAL_SCALE, "OFFSET": (0, 0)},
    "destroy_resource": {"SCALE": PRAYER_RITUAL_SCALE, "OFFSET": (0, 0)},
    "create_resource": {"SCALE": PRAYER_RITUAL_SCALE, "OFFSET": (0, 0)},
    "teleport": {"SCALE": PRAYER_RITUAL_SCALE, "OFFSET": (0, 0)},
    "swap": {"SCALE": PRAYER_RITUAL_SCALE, "OFFSET": (0, 0)},
    "line_destroy": {"SCALE": PRAYER_RITUAL_SCALE, "OFFSET": (0, 0)},
    "portal": {"SCALE": PRAYER_RITUAL_SCALE, "OFFSET": (0, 0)},
    "protect": {"SCALE": PRAYER_RITUAL_SCALE, "OFFSET": (0, 0)},
}
PIECE_IMAGE_MODIFY = {
    "king": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "queen": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "rook": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "bishop": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "knight": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "pawn": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "monk": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "duke": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "rogue_bishop": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "jester": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "pikeman": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "gold_general": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "silver_general": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "rogue_rook": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "elephant": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "elephant_cart": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "champion": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "rogue_pawn": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "rogue_knight": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "castle": {"SCALE": CASTLE_SCALE, "OFFSET": CASTLE_OFFSET},
    "fortress": {"SCALE": FORTRESS_SCALE, "OFFSET": FORTRESS_OFFSET},
    "wall": {"SCALE": FORTRESS_SCALE, "OFFSET": WALL_OFFSET},
    "monolith": {"SCALE": BARRACKS_SCALE, "OFFSET": BARRACKS_OFFSET},
    "prayer_stone": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "flag": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "barracks": {"SCALE": BARRACKS_SCALE, "OFFSET": BARRACKS_OFFSET},
    "war_tower": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "builder": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "unicorn": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "ram": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "stable": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "oxen": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "trader": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "doe": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "persuader": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "circus": {"SCALE": BARRACKS_SCALE, "OFFSET": BARRACKS_OFFSET},
    "trapper": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "trap": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "lion": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "fire_spinner": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "acrobat": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "magician": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "cavalry": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "ferz": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "assassin": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "war_tower_0": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "war_tower_1": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "war_tower_2": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "castle_0": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "stable_0": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "fortress_0": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "circus_0": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "barracks_0": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
}
IMAGES_IMAGE_MODIFY = {
    "icon": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "pickaxe": {"SCALE": PICKAXE_SCALE, "OFFSET": (0, 0)},
    "w_game_name": {"SCALE": GAME_NAME_SCALE, "OFFSET": (0, 0)},
    "b_game_name": {"SCALE": GAME_NAME_SCALE, "OFFSET": (0, 0)},
    "prayer": {"SCALE": PICKAXE_SCALE, "OFFSET": (0, 0)},
    "gold_coin": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "give": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "receive": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "log": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "action": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "prayer_bar_end": {"SCALE": PRAYER_BAR_END_SCALE, "OFFSET": (0, 0)},
    "units": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "prayer_bar": {"SCALE": PRAYER_BAR_SCALE, "OFFSET": (0, 0)},
    "hour_glass": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "stone": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "w_boat": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "hammer": {"SCALE": PICKAXE_SCALE, "OFFSET": (0, 0)},
    "axe": {"SCALE": PICKAXE_SCALE, "OFFSET": (0, 0)},
    "b_boat": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "resources_button": {"SCALE": RESOURCES_BUTTON_SCALE, "OFFSET": (0, 0)},
    "b_no": {"SCALE": YES_NO_BUTTON_SCALE, "OFFSET": (0, 0)},
    "b_yes": {"SCALE": YES_NO_BUTTON_SCALE, "OFFSET": (0, 0)},
    "w_no": {"SCALE": YES_NO_BUTTON_SCALE, "OFFSET": (0, 0)},
    "w_yes": {"SCALE": YES_NO_BUTTON_SCALE, "OFFSET": (0, 0)},
    "w_protect": {"SCALE": PROTECT_SQUARE_SCALE, "OFFSET": PROTECT_SQUARE_OFFSET},
    "b_protect": {"SCALE": PROTECT_SQUARE_SCALE, "OFFSET": PROTECT_SQUARE_OFFSET},
    "w_decree": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "b_decree": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "w_decree_u": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "b_decree_u": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "persuade": {"SCALE": PICKAXE_SCALE, "OFFSET": (0, 0)},
    "w_block": {"SCALE": PROTECT_SQUARE_SCALE, "OFFSET": PROTECT_SQUARE_OFFSET},
    "b_block": {"SCALE": PROTECT_SQUARE_SCALE, "OFFSET": PROTECT_SQUARE_OFFSET},
    "w_portal": {"SCALE": PROTECT_SQUARE_SCALE, "OFFSET": PROTECT_SQUARE_OFFSET},
    "b_portal": {"SCALE": PROTECT_SQUARE_SCALE, "OFFSET": PROTECT_SQUARE_OFFSET},
    "steal": {"SCALE": PICKAXE_SCALE, "OFFSET": (0, 0)},
    "sparkle": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET:": (0, 0)},
    "paper": {"SCALE": (8000, 5422), "OFFSET": (0, 0)},
    "w_upgrade": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
    "b_upgrade": {"SCALE": DEFAULT_PIECE_SCALE, "OFFSET": (0, 0)},
}
RESOURCES_IMAGE_MODIFY = {
    "gold_tile_1": {"SCALE": GOLD_SCALE, "OFFSET": GOLD_OFFSET},
    "tree_tile_1": {"SCALE": TREE_SCALE, "OFFSET": TREE_OFFSET},
    "tree_tile_2": {"SCALE": TREE_SCALE, "OFFSET": TREE_OFFSET},
    "tree_tile_3": {"SCALE": TREE_SCALE, "OFFSET": TREE_OFFSET},
    "tree_tile_4": {"SCALE": TREE_SCALE, "OFFSET": TREE_OFFSET},
    "tree_tile_5": {"SCALE": TREE_SCALE, "OFFSET": TREE_OFFSET},
    "tree_tile_6": {"SCALE": TREE_SCALE, "OFFSET": TREE_OFFSET},
    "tree_tile_7": {"SCALE": TREE_SCALE, "OFFSET": TREE_OFFSET},
    "tree_tile_8": {"SCALE": TREE_SCALE, "OFFSET": TREE_OFFSET},
    "quarry_1": {"SCALE": QUARRY_SCALE, "OFFSET": (0, 0)},
    "sunken_quarry_1": {"SCALE": QUARRY_SCALE, "OFFSET": (0, 0)},
    "depleted_quarry_1": {"SCALE": QUARRY_SCALE, "OFFSET": (0, 0)},
}
MENU_ICONS_IMAGE_MODIFY = {
    "gold_coin": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "log": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "stone": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
    "prayer": {"SCALE": MENU_ICON_DEFAULT_SCALE, "OFFSET": (0, 0)},
}
CONTEXTUAL_MENU_ICONS_IMAGE_MODIFY = {
    "steal": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "trade": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "persuade": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "build": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "mine": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "pray": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "w_flag": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "b_flag": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "w_decree_u": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "w_decree": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "b_decree_u": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "b_decree": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "w_ritual": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "b_ritual": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "arm": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
    "purchase": {"SCALE": DECREE_SCALE, "OFFSET": (0, 0)},
}
