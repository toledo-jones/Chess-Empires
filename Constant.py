import os
import random
import pygame
import time

"""

CONSTANT
TODO: Untangle this atrocity 

"""
DEBUG_START = False
DISPLAY_STATE_IN_HUD = False
BOARD_STARTS_WITH_RESOURCES = True
DEBUG_RITUALS = False
POP_UPS_ON = True
GOLD = pygame.Color('gold')
DARK_ORANGE = pygame.Color('dark orange')
WHITE = pygame.Color('white')
BLACK = pygame.Color('black')
BLUE = pygame.Color('blue')
RED = pygame.Color('red')
ICON_COLORS = {0: 'w', 1: 'b'}
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
MENU_COLOR = pygame.Color((72, 61, 139))
win.fill(MENU_COLOR)
LOGO_COLOR = ICON_COLORS[random.randint(0, 1)]
MAIN_MENU_LOGO = pygame.transform.scale(
    pygame.image.load(os.path.join("files/images", LOGO_COLOR + "_game_name.png")), (400, 400))
LOGO_POSITION = (pygame.display.Info().current_w // 2 - 200, pygame.display.Info().current_h // 2 - 300)
win.blit(MAIN_MENU_LOGO, LOGO_POSITION)
pygame.display.update()
time.sleep(2)
from Settings import *
STARTING_PRAYER = 0
STARTING_WOOD = 0
STARTING_GOLD = 0
STARTING_STONE = 0
SPAWN_LISTS = {'stable': STABLE_SPAWN_LIST, 'fortress': FORTRESS_SPAWN_LIST, 'castle': CASTLE_SPAWN_LIST,
               'builder': BUILDER_SPAWN_LIST, 'barracks': BARRACKS_SPAWN_LIST, 'circus': CIRCUS_SPAWN_LIST,
               'trapper': TRAPPER_SPAWN_LIST, 'monk': MONK_SPAWN_LIST}
w_pieces = ['w_king',
            'w_queen',
            'w_rook',
            'w_bishop',
            'w_knight',
            'w_pawn',
            'w_monk',
            'w_duke',
            'w_rogue_bishop',
            'w_jester',
            'w_pikeman',
            'w_gold_general',
            'w_silver_general',
            'w_rogue_rook',
            'w_elephant',
            'w_elephant_cart',
            'w_champion',
            'w_rogue_pawn',
            'w_rogue_knight',
            'w_builder',
            'w_unicorn',
            'w_ram',
            'w_oxen',
            'w_persuader',
            'w_doe',
            'w_trader',
            'w_trapper',
            'w_lion',
            'w_fire_spinner',
            'w_acrobat',
            'w_magician',
            ]
b_pieces = ['b_king', 'b_queen', 'b_rook', 'b_bishop',
            'b_knight', 'b_pawn', 'b_monk', 'b_duke',
            'b_rogue_bishop', 'b_jester', 'b_pikeman',
            'b_gold_general', 'b_silver_general',
            'b_rogue_rook', 'b_elephant', 'b_elephant_cart',
            'b_champion', 'b_rogue_pawn', 'b_rogue_knight',
            'b_builder', 'b_unicorn', 'b_ram', 'b_oxen',
            'b_persuader', 'b_doe', 'b_trader', 'b_trapper', 'b_lion', 'b_fire_spinner', 'b_acrobat', 'b_magician']
w_buildings = ['w_castle',
               'w_fortress',
               'w_barracks',
               'w_wall',
               'w_monolith',
               'w_prayer_stone',
               'w_flag',
               'w_barracks',
               'w_war_tower',
               'w_stable',
               'w_circus', 'w_trap']
b_buildings = ['b_castle', 'b_fortress', 'b_barracks',
               'b_wall', 'b_monolith', 'b_prayer_stone',
               'b_flag', 'b_barracks', 'b_war_tower', 'b_stable', 'b_circus', 'b_trap']
w_prayer_rituals = ['w_gold_general', 'w_smite', 'w_destroy_resource', 'w_create_resource', 'w_teleport',
                    'w_swap', 'w_line_destroy', 'w_protect', 'w_portal']
b_prayer_rituals = ['b_gold_general', 'b_smite', 'b_destroy_resource', 'b_create_resource', 'b_teleport', 'b_swap',
                    'b_line_destroy', 'b_protect', 'b_portal']
images = ['icon', 'pickaxe', 'w_game_name', 'b_game_name', 'prayer', 'gold_coin', 'log', 'action', 'prayer_bar_end',
          'units', 'prayer', 'prayer_bar', 'stone', 'w_boat', 'b_boat', 'hour_glass', 'hammer', 'axe',
          'resources_button',
          'b_no', 'b_yes', 'w_no', 'w_yes', 'b_protect', 'w_protect', 'steal', 'persuade', 'w_block', 'b_block',
          'w_portal', 'b_portal', 'w_decree', 'b_decree', 'w_decree_u', 'b_decree_u', 'give', 'receive']
music = ['music']
resources = ['gold_tile_1',
             'tree_tile_1',
             'tree_tile_2',
             'tree_tile_3',
             'tree_tile_4',
             'quarry_1',
             'sunken_quarry_1',
             'depleted_quarry_1']
menu_icons = ['gold_coin',
              'log',
              'stone',
              'prayer']
sounds = []
RESOURCE_YIELD_KEY = {'gold_tile_1': 'gold',
                      'quarry_1': 'quarry',
                      'sunken_quarry_1': 'sunken_quarry',
                      'tree_tile_1': 'wood',
                      'tree_tile_4': 'wood',
                      'tree_tile_2': 'wood',
                      'tree_tile_3': 'wood',
                      'depleted_quarry_1': None}
RESOURCE_KEY = {'gold_tile_1': 'gold', 'quarry_1': 'stone',
                'sunken_quarry_1': 'stone', 'tree_tile_1': 'wood',
                'tree_tile_2': 'wood', 'tree_tile_3': 'wood',
                'gold': 'gold',
                'tree_tile_4': 'wood', 'log': 'wood', 'gold_coin': 'gold', 'stone': 'stone'}
rand = random.randint(0, len(FACTION_NAMES) - 1)
FACTION = FACTION_NAMES[rand]
rand = random.randint(0, 2)
if rand == 0:
    INTRO_TEXT_COLOR = WHITE
else:
    INTRO_TEXT_COLOR = BLACK
turn_to_color = {'w': WHITE, 'b': BLACK}
TURNS = {'w': 'b', 'b': 'w'}
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
PRAYER_RITUALS = {}
IMAGES = {}
RESOURCES = {}
MENU_ICONS = {}
W_PIECES = {}
W_BUILDINGS = {}
B_PIECES = {}
B_BUILDINGS = {}
MUSIC = {}
ambience = []
for i in range(6):
    ambience.append(i)
building_spawning = []
for i in range(6):
    building_spawning.append(i)
captures = []
for i in range(62):
    captures.append(i)
harvesting_rock = []
for i in range(63):
    harvesting_rock.append(i)
harvesting_wood = []
for i in range(36):
    harvesting_wood.append(i)
moves = []
for i in range(118):
    moves.append(i)
piece_spawning = []
for i in range(16):
    piece_spawning.append(i)
purchase = []
for i in range(25):
    purchase.append(i)
rituals = []
for i in range(54):
    rituals.append(i)
generate_resources = []
for i in range(12):
    generate_resources.append(i)
pray = []
for i in range(19):
    pray.append(i)
change_turn = []
for i in range(8):
    change_turn.append(i)
start_game = []
for i in range(4):
    start_game.append(i)
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


def load_sounds():
    for i in building_spawning:
        filename = str(0) + str(building_spawning[i])
        BUILDING_SPAWNING_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/building_spawning", filename + '.wav'))

    for i in captures:
        filename = str(0) + str(captures[i])
        CAPTURE_SOUNDS[i] = pygame.mixer.Sound(os.path.join("files/sounds/captures", filename + '.wav'))

    for i in harvesting_rock:
        filename = str(0) + str(harvesting_rock[i])
        HARVESTING_ROCK_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/harvesting_rock", filename + '.wav'))

    for i in harvesting_wood:
        filename = str(0) + str(harvesting_wood[i])
        HARVESTING_WOOD_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/harvesting_wood", filename + '.wav'))

    for i in moves:
        filename = str(0) + str(moves[i])
        MOVE_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/moves", filename + '.wav'))

    for i in piece_spawning:
        filename = str(0) + str(piece_spawning[i])
        PIECE_SPAWNING_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/piece_spawning", filename + '.wav'))

    for i in purchase:
        filename = str(0) + str(purchase[i])
        PURCHASE_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/purchase", filename + '.wav'))

    for i in generate_resources:
        filename = str(0) + str(generate_resources[i])
        GENERATE_RESOURCES_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/generate_resources", filename + '.wav'))

    for i in pray:
        filename = str(0) + str(pray[i])
        PRAY_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/pray", filename + '.wav'))

    for i in change_turn:
        filename = str(0) + str(change_turn[i])
        CHANGE_TURN_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/change_turn", filename + '.wav'))

    for i in start_game:
        filename = str(0) + str(start_game[i])
        START_GAME_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/start_game", filename + '.wav'))

    for i in rituals:
        filename = str(0) + str(rituals[i])
        PRAYER_RITUAL_SOUNDS[i] = pygame.mixer.Sound(
            os.path.join("files/sounds/rituals", filename + '.wav'))


def load_music():
    i = random.randint(0, len(ambience))
    filename = str(0) + str(i)
    pygame.mixer.music.load(os.path.join("files/music/ambience", filename + '.wav'))
    pygame.mixer.music.play()


def load_images():
    for image in images:
        scale = IMAGES_IMAGE_MODIFY[image]['SCALE']
        IMAGES[image] = pygame.transform.scale(pygame.image.load(os.path.join("files/images", image + ".png")),
                                               (scale[0], scale[1])).convert_alpha()
    for resource in resources:
        scale = RESOURCES_IMAGE_MODIFY[resource]['SCALE']
        RESOURCES[resource] = pygame.transform.scale(
            pygame.image.load(os.path.join("files/resources", resource + ".png")),
            (scale[0], scale[1])).convert_alpha()
    for menu_icon in menu_icons:
        scale = MENU_ICONS_IMAGE_MODIFY[menu_icon]['SCALE']
        MENU_ICONS[menu_icon] = pygame.transform.scale(
            pygame.image.load(os.path.join("files/menu_icons", menu_icon + ".png")),
            (scale[0], scale[1])).convert_alpha()

    for piece in w_pieces:
        scale = PIECE_IMAGE_MODIFY[piece_color_to_type(piece)]['SCALE']
        W_PIECES[piece] = pygame.transform.scale(pygame.image.load(os.path.join("files/pieces", piece + ".png")),
                                                 (scale[0], scale[1])).convert_alpha()
    for piece in w_buildings:
        scale = PIECE_IMAGE_MODIFY[piece_color_to_type(piece)]['SCALE']
        W_BUILDINGS[piece] = pygame.transform.scale(pygame.image.load(os.path.join("files/pieces", piece + ".png")),
                                                    (scale[0], scale[1])).convert_alpha()
    for piece in b_pieces:
        scale = PIECE_IMAGE_MODIFY[piece_color_to_type(piece)]['SCALE']
        B_PIECES[piece] = pygame.transform.scale(pygame.image.load(os.path.join("files/pieces", piece + ".png")),
                                                 (scale[0], scale[1])).convert_alpha()
    for piece in b_buildings:
        scale = PIECE_IMAGE_MODIFY[piece_color_to_type(piece)]['SCALE']
        B_BUILDINGS[piece] = pygame.transform.scale(pygame.image.load(os.path.join("files/pieces", piece + ".png")),
                                                    (scale[0], scale[1])).convert_alpha()

    for ritual in w_prayer_rituals:
        scale = RITUAL_IMAGE_MODIFY[piece_color_to_type(ritual)]['SCALE']
        PRAYER_RITUALS[ritual] = pygame.transform.scale(
            pygame.image.load(os.path.join("files/prayer_rituals", ritual + ".png")),
            (scale[0], scale[1])).convert_alpha()

    for ritual in b_prayer_rituals:
        scale = RITUAL_IMAGE_MODIFY[piece_color_to_type(ritual)]['SCALE']
        PRAYER_RITUALS[ritual] = pygame.transform.scale(
            pygame.image.load(os.path.join("files/prayer_rituals", ritual + ".png")),
            (scale[0], scale[1])).convert_alpha()


def piece_color_to_type(color_piece):
    return color_piece[2:]


def quarter_squares():
    top_left = []
    top_right = []
    bottom_left = []
    bottom_right = []
    x, y = board_max_index()
    minimum_row = 2
    maximum_row = y - 1
    for c in range(x + 1):
        for r in range(minimum_row, maximum_row):
            if c > x // 2 and r > y // 2:
                bottom_right.append((r, c))
            elif c < x // 2 and r > y // 2:
                bottom_left.append((r, c))
            elif c > x // 2 and r < y // 2:
                top_right.append((r, c))
            elif c < x // 2 and r < y // 2:
                top_left.append((r, c))

    return top_left, top_right, bottom_left, bottom_right


def big_center_squares():
    squares = []
    # x, y equal max val col, row
    x, y = board_max_index()

    for c in range(x // 2 - 2, x // 2 + 4):
        for r in range(y + 1):
            square = (r, c)
            squares.append(square)
    return squares


def center_squares():
    squares = []
    # x, y equal max val col, row
    x, y = board_max_index()

    for c in range(x // 2, x // 2 + 2):
        for r in range(y // 2, y // 2 + 2):
            square = (r, c)
            squares.append(square)
    return squares


def quarter_triangle_sections_a():
    bottom_left = []
    bottom_right = []
    top_left = []
    top_right = []
    # x, y equal max val col, row
    x, y = board_max_index()

    for r in range(6, y + 1):
        for c in range(0, r - 2):
            bottom_left.append((r, c))

    for r in range(6, y + 1):
        for c in range(x, x - (r - 2), -1):
            bottom_right.append((r, c))

    for r in range(0, 6):
        for c in range(6 - r, -1, -1):
            top_left.append((r, c))

    # for r in range(6, 0, -1):
    #     for c in range( x - (r - 2), x, -1):
    #         top_right.append((r, c))

    return bottom_left, bottom_right, top_left, top_right


def quarter_triangle_sections_b():
    bottom_left = []
    bottom_right = []
    top_left = []
    top_right = []
    # x, y equal max val col, row
    x, y = board_max_index()

    # for r in range(6, y + 1):
    #     for c in range(0, r - 2):
    #         bottom_left.append((r, c))
    #
    for r in range(6, y + 1):
        for c in range(x, x - (r - 2), -1):
            bottom_right.append((r, c))

    for r in range(0, 6):
        for c in range(6 - r, -1, -1):
            top_left.append((r, c))

    for r in range(0, 6):
        for c in range(x, x - (6 - r), -1):
            top_right.append((r, c))

    return bottom_left, bottom_right, top_left, top_right


def quarter_triangle_sections_c():
    bottom_left = []
    bottom_right = []
    top_left = []
    top_right = []
    # x, y equal max val col, row
    x, y = board_max_index()

    for r in range(6, y + 1):
        for c in range(0, r - 2):
            bottom_left.append((r, c))

    for r in range(6, y + 1):
        for c in range(x, x - (r - 2), -1):
            bottom_right.append((r, c))

    # for r in range(0, 6):
    #     for c in range(6-r, -1, -1):
    #         top_left.append((r, c))

    for r in range(0, 6):
        for c in range(x, x - (6 - r), -1):
            top_right.append((r, c))

    return bottom_left, bottom_right, top_left, top_right


def quarter_triangle_sections_d():
    bottom_left = []
    bottom_right = []
    top_left = []
    top_right = []
    # x, y equal max val col, row
    x, y = board_max_index()

    for r in range(5, y + 1):
        for c in range(0, r - 2):
            bottom_left.append((r, c))

    # for r in range(6, y + 1):
    #     for c in range(x, x - (r - 2), -1):
    #         bottom_right.append((r, c))

    for r in range(0, 5):
        for c in range(5 - r, -1, -1):
            top_left.append((r, c))

    for r in range(0, 5):
        for c in range(x, x - (5 - r), -1):
            top_right.append((r, c))

    return bottom_left, bottom_right, top_left, top_right


def left_and_right_triangle_sections():
    left_triangle = []
    right_triangle = []
    # x, y equal max val col, row
    x, y = board_max_index()

    for r in range(4, y + 1):
        for c in range(0, r - 2):
            left_triangle.append((r, c))

    for r in range(4, y + 1):
        for c in range(x, x - (r - 2), -1):
            right_triangle.append((r, c))

    return left_triangle, right_triangle


def top_and_bottom_squares():
    top_squares = []
    bottom_squares = []

    # x, y equal max val col, row
    x, y = board_max_index()
    for c in range(3, x - 2):
        for r in range(1, 3):
            square = (r, c)
            top_squares.append(square)
        for r in range(y - 2, y):
            square = (r, c)
            bottom_squares.append(square)
    return top_squares, bottom_squares


def edge_squares():
    squares = []
    # x, y equal max val col, row
    x, y = board_max_index()
    for c in range(0, x + 1):
        for r in range(0, 3):
            square = (r, c)
            squares.append(square)
        for r in range(y - 2, y + 1):
            square = (r, c)
            squares.append(square)
    return squares


def center_circle_squares():
    squares = []
    x, y = board_max_index()
    x += 1
    radius = 5
    increment = 0
    reached_peak = False
    for r in range(y // 2 - radius, y // 2 + radius):
        for c in range(x // 2 - increment, x // 2 + increment):
            square = (r, c)
            squares.append(square)
        if increment == radius:
            reached_peak = True
        if not reached_peak:
            increment += 1
        else:
            increment -= 1

    return squares


def quarter_triangle_sections():
    bottom_left = []
    bottom_right = []
    top_left = []
    top_right = []
    x, y = board_max_index()

    # D TYPE:
    for r in range(5, y + 1):
        for c in range(0, r - 2):
            bottom_left.append((r, c))

    for r in range(y-3, y+1):
        for c in range(x, x - (r - 3), -1):
            bottom_right.append((r, c))

    for r in range(0, 5):
        for c in range(5 - r, -1, -1):
            top_left.append((r, c))

    for r in range(0, 5):
        for c in range(x, x - (5 - r), -1):
            top_right.append((r, c))

    return bottom_left, bottom_right, top_left, top_right


def quarter_triangle_sections_e():
    bottom_left = []
    bottom_right = []
    top_left = []
    top_right = []
    x, y = board_max_index()

    for r in range(y-3, y+1):
        for c in range(0, r-5):
            bottom_left.append((r, c))

    for r in range(y-3, y+1):
        for c in range(x, x - (r - 5), -1):
            bottom_right.append((r, c))

    for r in range(0, 4):
        for c in range(3 - r, -1, -1):
            top_left.append((r, c))

    for r in range(0, 4):
        for c in range(x, x - (4 - r), -1):
            top_right.append((r, c))

    return bottom_left, bottom_right, top_left, top_right


def left_right_squares():
    left_squares, right_squares = [], []
    x, y = board_max_index()
    for r in range(0, y + 1):
        for c in range(0, 3):
            square = (r, c)
            left_squares.append(square)
        for c in range(x - 2, x + 1):
            square = (r, c)
            right_squares.append(square)
    return left_squares, right_squares


def alt_starting_squares_a():
    w_starting_squares, b_starting_squares = [], []
    x, y = board_max_index()
    y_center = y // 2
    for c in range(1, 3):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            w_starting_squares.append(square)
    for c in range(x - 2, x):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            b_starting_squares.append(square)
    return w_starting_squares, b_starting_squares


def alt_starting_squares():
    w_starting_squares, b_starting_squares = [], []
    x, y = board_max_index()
    y_center = y // 2
    for c in range(2, 4):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            w_starting_squares.append(square)
    for c in range(x - 3, x - 1):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            b_starting_squares.append(square)
    return w_starting_squares, b_starting_squares


def starting_squares():
    w_starting_squares, b_starting_squares = [], []
    x, y = board_max_index()
    y_center = y // 2
    for c in range(0, 5):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            w_starting_squares.append(square)
    for c in range(x - 4, x + 1):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            b_starting_squares.append(square)
    return w_starting_squares, b_starting_squares


def outside_corner_squares():
    c, r = board_max_index()
    squares = [(0, 0), (0, c), (r, c), (r, 0)]
    return squares


def board_max_index():
    x = BOARD_WIDTH_SQ - 1
    y = BOARD_HEIGHT_SQ - 1
    return x, y


def pos_in_bounds(pos):
    if BOARD_WIDTH_PX > pos[0] > 0 and BOARD_HEIGHT_PX > pos[1] > 0:
        return True
    else:
        return False


def tile_in_bounds(r, c):
    x, y = board_max_index()
    if c <= x and r <= y:
        if c >= 0 and r >= 0:
            return True
    else:
        return False


def convert_pos(pos):
    row = pos[1] // SQ_SIZE
    col = pos[0] // SQ_SIZE
    return row, col

def board_remainder():
    return BOARD_HEIGHT_SQ / SQ_SIZE