import json
import os
import random
from io import TextIOBase
from typing import cast

# Default Start
DEBUG_START = False
DISPLAY_STATE_IN_HUD = False
BOARD_STARTS_WITH_RESOURCES = True
DEBUG_RITUALS = False
POP_UPS_ON = False
SHOW_STONE = False
SOUND_EFFECTS_ON = None
MUSIC_ON = None
STARTING_PRAYER = 0
STARTING_WOOD = 0
STARTING_GOLD = 0
STARTING_STONE = 0

# Configurable stuff goes here
from settings import *

# Dictionaries for commonly used string conversions
RESOURCE_YIELD_KEY = {
    "gold_tile_1": "gold",
    "quarry_1": "quarry",
    "sunken_quarry_1": "sunken_quarry",
    "tree_tile_1": "wood",
    "tree_tile_4": "wood",
    "tree_tile_2": "wood",
    "tree_tile_3": "wood",
    "tree_tile_5": "wood",
    "tree_tile_6": "wood",
    "tree_tile_7": "wood",
    "tree_tile_8": "wood",
    "depleted_quarry_1": None,
}
RESOURCE_KEY = {
    "gold_tile_1": "gold",
    "quarry_1": "stone",
    "sunken_quarry_1": "stone",
    "tree_tile_1": "wood",
    "tree_tile_2": "wood",
    "tree_tile_3": "wood",
    "tree_tile_4": "wood",
    "tree_tile_5": "wood",
    "tree_tile_6": "wood",
    "tree_tile_7": "wood",
    "tree_tile_8": "wood",
    "gold": "gold",
    "log": "wood",
    "gold_coin": "gold",
    "stone": "stone",
}
turn_to_color = {None: BLACK, "w": WHITE, "b": BLACK}
TURNS = {"w": "b", "b": "w"}

# Lists which tell the game which assets to load
w_pieces = [
    "w_king",
    "w_queen",
    "w_rook",
    "w_ferz",
    "w_assassin",
    "w_bishop",
    "w_knight",
    "w_pawn",
    "w_monk",
    "w_duke",
    "w_rogue_bishop",
    "w_jester",
    "w_pikeman",
    "w_gold_general",
    "w_silver_general",
    "w_rogue_rook",
    "w_elephant",
    "w_elephant_cart",
    "w_champion",
    "w_rogue_pawn",
    "w_rogue_knight",
    "w_builder",
    "w_unicorn",
    "w_ram",
    "w_oxen",
    "w_persuader",
    "w_doe",
    "w_trader",
    "w_trapper",
    "w_lion",
    "w_fire_spinner",
    "w_acrobat",
    "w_magician",
    "w_cavalry",
]
b_pieces = [
    "b_king",
    "b_queen",
    "b_rook",
    "b_ferz",
    "b_assassin",
    "b_bishop",
    "b_knight",
    "b_pawn",
    "b_monk",
    "b_duke",
    "b_rogue_bishop",
    "b_jester",
    "b_pikeman",
    "b_gold_general",
    "b_silver_general",
    "b_rogue_rook",
    "b_elephant",
    "b_elephant_cart",
    "b_champion",
    "b_rogue_pawn",
    "b_rogue_knight",
    "b_builder",
    "b_unicorn",
    "b_ram",
    "b_oxen",
    "b_persuader",
    "b_doe",
    "b_trader",
    "b_trapper",
    "b_lion",
    "b_fire_spinner",
    "b_acrobat",
    "b_magician",
    "b_cavalry",
]
w_buildings = [
    "w_castle",
    "w_fortress",
    "w_barracks",
    "w_wall",
    "w_monolith",
    "w_prayer_stone",
    "w_flag",
    "w_barracks",
    "w_war_tower",
    "w_stable",
    "w_circus",
    "w_trap",
]
b_buildings = [
    "b_castle",
    "b_fortress",
    "b_barracks",
    "b_wall",
    "b_monolith",
    "b_prayer_stone",
    "b_flag",
    "b_barracks",
    "b_war_tower",
    "b_stable",
    "b_circus",
    "b_trap",
]
board_tiles = ["light", "dark"]
w_prayer_rituals = [
    "w_gold_general",
    "w_smite",
    "w_destroy_resource",
    "w_create_resource",
    "w_teleport",
    "w_swap",
    "w_line_destroy",
    "w_protect",
    "w_portal",
]
b_prayer_rituals = [
    "b_gold_general",
    "b_smite",
    "b_destroy_resource",
    "b_create_resource",
    "b_teleport",
    "b_swap",
    "b_line_destroy",
    "b_protect",
    "b_portal",
]
images = [
    "icon",
    "pickaxe",
    "w_game_name",
    "b_game_name",
    "prayer",
    "gold_coin",
    "log",
    "action",
    "prayer_bar_end",
    "units",
    "prayer",
    "prayer_bar",
    "stone",
    "w_boat",
    "b_boat",
    "hour_glass",
    "hammer",
    "axe",
    "resources_button",
    "b_no",
    "b_yes",
    "w_no",
    "w_yes",
    "b_protect",
    "w_protect",
    "steal",
    "persuade",
    "w_block",
    "b_block",
    "w_portal",
    "b_portal",
    "w_decree",
    "b_decree",
    "w_decree_u",
    "b_decree_u",
    "give",
    "receive",
    "sparkle",
    "paper",
]
music = ["music"]
resources = [
    "gold_tile_1",
    "tree_tile_1",
    "tree_tile_2",
    "tree_tile_3",
    "tree_tile_4",
    "tree_tile_5",
    "tree_tile_6",
    "tree_tile_7",
    "tree_tile_8",
    "quarry_1",
    "sunken_quarry_1",
    "depleted_quarry_1",
]
menu_icons = ["gold_coin", "log", "stone", "prayer"]
contextual_menu_icons = [
    "build",
    "pray",
    "mine",
    "steal",
    "persuade",
    "trade",
    "w_flag",
    "b_flag",
    "w_decree_u",
    "w_decree",
    "b_decree_u",
    "b_decree",
    "w_ritual",
    "b_ritual",
]
sounds = []
ambience = []
start_game = []
building_spawning = []
captures = []
harvesting_rock = []
harvesting_wood = []
moves = []
piece_spawning = []
purchase = []
rituals = []
generate_resources = []
pray = []
change_turn = []
instructions = []

# Moves
RIGHT = (0, 1)
LEFT = (0, -1)
UP = (-1, 0)
DOWN = (1, 0)
TWO_RIGHT = (0, 2)
TWO_LEFT = (0, -2)
TWO_UP = (-2, 0)
TWO_DOWN = (2, 0)
THREE_RIGHT = (0, 3)
THREE_LEFT = (0, -3)
THREE_UP = (-3, 0)
THREE_DOWN = (3, 0)
UP_RIGHT = (-1, 1)
DOWN_LEFT = (1, -1)
DOWN_RIGHT = (1, 1)
UP_LEFT = (-1, -1)
TWO_UP_LEFT = (-2, -1)
TWO_LEFT_UP = (-1, -2)
TWO_UP_RIGHT = (-2, 1)
TWO_RIGHT_UP = (-1, 2)
TWO_DOWN_RIGHT = (2, 1)
TWO_RIGHT_DOWN = (1, 2)
TWO_DOWN_LEFT = (2, -1)
TWO_LEFT_DOWN = (1, -2)
THREE_UP_LEFT = (-3, -1)
THREE_LEFT_UP = (-1, -3)
THREE_UP_RIGHT = (-3, 1)
THREE_RIGHT_UP = (-1, 3)
THREE_DOWN_RIGHT = (3, 1)
THREE_RIGHT_DOWN = (1, 3)
THREE_DOWN_LEFT = (3, -1)
THREE_LEFT_DOWN = (1, -3)

# Dictionaries which will contain actual game assets
PRAYER_RITUALS = {}
IMAGES = {}
RESOURCES = {}
MENU_ICONS = {}
W_PIECES = {}
W_BUILDINGS = {}
B_PIECES = {}
B_BUILDINGS = {}
CONTEXTUAL_MENU_ICONS = {}
MUSIC = {}
BUILDING_SPAWNING_SOUNDS = {}
CAPTURE_SOUNDS = {}
HARVESTING_ROCK_SOUNDS = {}
HARVESTING_WOOD_SOUNDS = {}
MOVE_SOUNDS = {}
PIECE_SPAWNING_SOUNDS = {}
PURCHASE_SOUNDS = {}
PRAYER_RITUAL_SOUNDS = {}
GENERATE_RESOURCES_SOUNDS = {}
PRAY_SOUNDS = {}
CHANGE_TURN_SOUNDS = {}
START_GAME_SOUNDS = {}
INSTRUCTIONS = {}
PAPER_TEXTURE = None
BOARD_TILES = {"dark": {}, "light": {}}

# Loops to add lists of numbers to empty asset lists
for j in range(8):
    ambience.append(j)
for j in range(6):
    building_spawning.append(j)
for j in range(62):
    captures.append(j)
for j in range(63):
    harvesting_rock.append(j)
for j in range(36):
    harvesting_wood.append(j)
for j in range(118):
    moves.append(j)
for j in range(16):
    piece_spawning.append(j)
for j in range(25):
    purchase.append(j)
for j in range(54):
    rituals.append(j)
for j in range(12):
    generate_resources.append(j)
for j in range(19):
    pray.append(j)
for j in range(8):
    change_turn.append(j)
for j in range(4):
    start_game.append(j)
for j in range(14):
    instructions.append(j)


def load_sounds():
    for i in building_spawning:
        filename = str(0) + str(building_spawning[i])
        BUILDING_SPAWNING_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/building_spawning", filename + ".wav")
        )

    for i in captures:
        filename = str(0) + str(captures[i])
        CAPTURE_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/captures", filename + ".wav")
        )

    for i in harvesting_rock:
        filename = str(0) + str(harvesting_rock[i])
        HARVESTING_ROCK_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/harvesting_rock", filename + ".wav")
        )

    for i in harvesting_wood:
        filename = str(0) + str(harvesting_wood[i])
        HARVESTING_WOOD_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/harvesting_wood", filename + ".wav")
        )

    for i in moves:
        filename = str(0) + str(moves[i])
        MOVE_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/moves", filename + ".wav")
        )

    for i in piece_spawning:
        filename = str(0) + str(piece_spawning[i])
        PIECE_SPAWNING_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/piece_spawning", filename + ".wav")
        )

    for i in purchase:
        filename = str(0) + str(purchase[i])
        PURCHASE_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/purchase", filename + ".wav")
        )

    for i in generate_resources:
        filename = str(0) + str(generate_resources[i])
        GENERATE_RESOURCES_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/generate_resources", filename + ".wav")
        )

    for i in pray:
        filename = str(0) + str(pray[i])
        PRAY_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/pray", filename + ".wav")
        )

    for i in change_turn:
        filename = str(0) + str(change_turn[i])
        CHANGE_TURN_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/change_turn", filename + ".wav")
        )

    for i in start_game:
        filename = str(0) + str(start_game[i])
        START_GAME_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/start_game", filename + ".wav")
        )

    for i in rituals:
        filename = str(0) + str(rituals[i])
        PRAYER_RITUAL_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/rituals", filename + ".wav")
        )


def load_settings():
    global MUSIC_ON
    global SOUND_EFFECTS_ON
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
            # Load the flags from the file
            MUSIC_ON = settings.get("MUSIC_ON", True)  # Default to True if not set
            SOUND_EFFECTS_ON = settings.get(
                "SOUND_EFFECTS_ON", True
            )  # Default to True if not set
    except FileNotFoundError:
        # If the file doesn't exist, initialize with defaults
        MUSIC_ON = True
        SOUND_EFFECTS_ON = True


def save_settings():
    """
    Saves the current settings to a JSON file.
    """
    settings = {"MUSIC_ON": MUSIC_ON, "SOUND_EFFECTS_ON": SOUND_EFFECTS_ON}

    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, cast(TextIOBase, f))


def load_music(play_music: bool):
    if play_music:
        i = random.randint(0, len(ambience))
        filename = str(0) + str(i)
        pygame.mixer.music.load(os.path.join("files/music/ambience", filename + ".wav"))
        pygame.mixer.music.play()
    else:
        pygame.mixer.music.stop()


def load_and_scale_image(path: str, scale: tuple[int, int]) -> pygame.Surface:
    """
    Loads an image from the given path and scales it.

    :param path: The path to the image file.
    :param scale: The scale to resize the image to.
    :return: The scaled image as a pygame.Surface.
    """
    # Load the image from the given path
    image: pygame.Surface = pygame.image.load(path)
    # Scale the image to the specified size
    scaled_image: pygame.Surface = pygame.transform.scale(image, (scale[0], scale[1]))
    # Convert the image to include alpha transparency
    return scaled_image.convert_alpha()


def load_images():
    """
    Loads and scales all required images.
    """
    # Load and scale general images
    for image in images:
        # Load and scale each image
        IMAGES[image] = load_and_scale_image(
            os.path.join("files/images", f"{image}.png"),
            IMAGES_IMAGE_MODIFY[image]["SCALE"],
        )

    # Load instructions without scaling
    for instruction in instructions:
        # Load each instruction image
        INSTRUCTIONS[instruction] = pygame.image.load(
            os.path.join("files/instructions", f"{instruction}.png")
        ).convert_alpha()

    # Load and scale resource images
    for resource in resources:
        # Load and scale each resource image
        RESOURCES[resource] = load_and_scale_image(
            os.path.join("files/resources", f"{resource}.png"),
            RESOURCES_IMAGE_MODIFY[resource]["SCALE"],
        )

    # Load and scale menu icons
    for menu_icon in menu_icons:
        # Load and scale each menu icon
        MENU_ICONS[menu_icon] = load_and_scale_image(
            os.path.join("files/menu_icons", f"{menu_icon}.png"),
            MENU_ICONS_IMAGE_MODIFY[menu_icon]["SCALE"],
        )

    # Load and scale contextual menu icons
    for contextual_menu_icon in contextual_menu_icons:
        # Load and scale each contextual menu icon
        CONTEXTUAL_MENU_ICONS[contextual_menu_icon] = load_and_scale_image(
            os.path.join("files/contextual_menu_icons", f"{contextual_menu_icon}.png"),
            CONTEXTUAL_MENU_ICONS_IMAGE_MODIFY[contextual_menu_icon]["SCALE"],
        )

    # Load and scale pieces and buildings for both white and black
    for piece_set, storage in [
        (w_pieces, W_PIECES),
        (b_pieces, B_PIECES),
        (w_buildings, W_BUILDINGS),
        (b_buildings, B_BUILDINGS),
    ]:
        for piece in piece_set:
            # Load and scale each piece or building
            storage[piece] = load_and_scale_image(
                os.path.join("files/pieces", f"{piece}.png"),
                PIECE_IMAGE_MODIFY[piece_string_to_color(piece)]["SCALE"],
            )

    # Load and scale prayer rituals for both white and black
    for ritual_set, storage in [
        (w_prayer_rituals, PRAYER_RITUALS),
        (b_prayer_rituals, PRAYER_RITUALS),
    ]:
        for ritual in ritual_set:
            # Load and scale each prayer ritual
            storage[ritual] = load_and_scale_image(
                os.path.join("files/prayer_rituals", f"{ritual}.png"),
                RITUAL_IMAGE_MODIFY[piece_string_to_color(ritual)]["SCALE"],
            )

    # Load and scale board tiles
    for board_tile in board_tiles:
        for index in range(47):
            # Load and scale each board tile
            BOARD_TILES[board_tile][index] = load_and_scale_image(
                os.path.join(f"files/board/{board_tile}/{index}.png"),
                (SQ_SIZE, SQ_SIZE),
            )


def piece_string_to_color(color_piece: str) -> str:
    """
    Extracts the type of piece from its color-prefixed name.

    :param color_piece: The name of the piece with color prefix.
    :return: The type of the piece.
    """
    # Return the substring starting from the third character
    return color_piece[2:]


def board_max_index() -> tuple[int, int]:
    """
    Calculates the maximum indices for the board.

    :return: A tuple containing the maximum row and column indices.
    """
    # Calculate the maximum row index
    max_row: int = BOARD_WIDTH_SQ - 1
    # Calculate the maximum column index
    max_col: int = BOARD_HEIGHT_SQ - 1
    return max_row, max_col


def pos_in_board(pos: tuple[int, int]) -> bool:
    """
    Checks if a position is within the board boundaries.

    :param pos: The position to check.
    :return: True if the position is within the board, False otherwise.
    """
    # Check if the position is within the board boundaries
    return BOARD_WIDTH_PX > pos[0] > 0 and BOARD_HEIGHT_PX > pos[1] > 0


def tile_in_bounds(row: int, col: int) -> bool:
    """
    Checks if a tile is within the board boundaries.

    :param row: The row index of the tile.
    :param col: The column index of the tile.
    :return: True if the tile is within the board, False otherwise.
    """
    # Get the maximum row and column indices
    max_row, max_col = board_max_index()
    # Check if the tile is within the board boundaries
    return 0 <= col <= max_col and 0 <= row <= max_row


def convert_pos(pos: tuple[int, int]) -> tuple[int, int]:
    """
    Converts a pixel position to board coordinates.

    :param pos: The pixel position.
    :return: The board coordinates as a tuple (row, col).
    """
    # Calculate the row index
    row: int = pos[1] // SQ_SIZE
    # Calculate the column index
    col: int = pos[0] // SQ_SIZE
    return row, col


def board_remainder() -> float:
    """
    Calculates the remainder of the board height divided by the square size.

    :return: The remainder of the division.
    """
    # Calculate the remainder of the board height divided by the square size
    return BOARD_HEIGHT_SQ / SQ_SIZE


def create_highlight_surface(size: tuple) -> pygame.Surface:
    """
    Helper function to create a transparent pygame surface intended to be used for highlighting various menu items.

    :param size: The size of the surface to create.
    :return: The created highlight surface.
    """
    # Create a new surface with the given size
    surface: pygame.Surface = pygame.Surface(size)
    # Set the alpha transparency for the surface
    surface.set_alpha(HIGHLIGHT_ALPHA)
    # Fill the surface with the highlight color
    surface.fill(UNUSED_PIECE_HIGHLIGHT_COLOR)
    return surface
