import pygame
"""

SETTINGS FILE

-Debug
-Configuring game settings
-All values should be configurable
-Minimal boilerplate

"""
# DEBUG_START = True
# DISPLAY_STATE_IN_HUD = True
# BOARD_STARTS_WITH_RESOURCES = False
# DEBUG_RITUALS = True
# POP_UPS_ON = True
""" 

DEBUG

"""
DEBUG_STARTING_PRAYER = 30
DEBUG_STARTING_WOOD = 999
DEBUG_STARTING_GOLD = 999
DEBUG_STARTING_STONE = 99
DEBUG_STARTING_PIECES = ['castle', 'king', 'rogue_pawn']
"""

WINDOW / BOARD / SIDE MENU

"""
BOARD_HEIGHT_PX = pygame.display.Info().current_h
SQ_SIZE = BOARD_HEIGHT_PX // 10
BOARD_HEIGHT_SQ = BOARD_HEIGHT_PX // SQ_SIZE
BOARD_WIDTH_SQ = 14
BOARD_WIDTH_PX = BOARD_WIDTH_SQ * SQ_SIZE
SIDE_MENU_WIDTH = pygame.display.Info().current_w - BOARD_WIDTH_PX
BOARD_HEIGHT_PX = pygame.display.Info().current_h
"""

COLORS

"""
MENU_COLOR = pygame.Color((72, 61, 139))
LIGHT_SQUARE_COLOR = pygame.Color((238, 232, 170))
DARK_SQUARE_COLOR = pygame.Color((222, 184, 135))
UNUSED_PIECE_HIGHLIGHT_COLOR = pygame.Color((248, 127, 0))
SELF_SQUARE_HIGHLIGHT_COLOR = pygame.Color('blue')
MOVE_SQUARE_HIGHLIGHT_COLOR = pygame.Color((72, 61, 139))
"""

TOGGLES

"""
ACTIONS_UPDATE_ON_SPAWN = False
MINING_COSTS_ACTION = False
PRAYING_COSTS_ACTION = False
STEALING_COSTS_ACTION = False
PERSUADE_COSTS_ACTION = True
QUARRY_COSTS_ACTION = False
QUARRY_COSTS_RESOURCE = False
TRAP_COSTS_ACTION = False
TURN_CHANGE_AFTER_START_SPAWN = True
"""

LISTS

"""
SELECTABLE_STARTING_PIECES = ['pawn', 'builder', 'trader', 'trapper', 'rogue_pawn', 'monk', 'pikeman']
MASTER_COST_LIST = ['builder', 'monk', 'stable', 'castle', 'barracks', 'fortress', 'circus']
STABLE_SPAWN_LIST = ['doe', 'oxen', 'unicorn', 'ram', 'elephant', 'knight']
FORTRESS_SPAWN_LIST = ['rogue_rook', 'rogue_bishop', 'rogue_knight', 'rogue_pawn']
CASTLE_SPAWN_LIST = ['pawn', 'builder', 'pikeman', 'monk', 'trader', 'trapper']
BUILDER_SPAWN_LIST = ['wall', 'stable', 'castle', 'barracks', 'fortress', 'circus']
BARRACKS_SPAWN_LIST = ['duke', 'queen', 'champion', 'rook', 'bishop']
CIRCUS_SPAWN_LIST = ['jester', 'persuader', 'lion', 'fire_spinner', 'acrobat', 'magician']
TRAPPER_SPAWN_LIST = ['trap']
MONK_SPAWN_LIST = ['monolith', 'prayer_stone']
STARTING_PIECES = ['castle', 'king']
FACTION_NAMES = ['clique', 'coterie', 'cabal', 'bloc', 'camp', 'grouping',
                 'side', 'division', 'wing', 'section', 'countrymen', 'squad', 'faction',
                 'company', 'troupe', 'set', 'army', 'party', 'gang', 'selection', 'crew',
                 'corps', 'lineup', 'sect', 'band', 'color', 'people', 'squadron', 'group',
                 'allegiance', 'choice']
MONOLITH_RITUALS = ['gold_general',
                    'line_destroy',
                    'smite']
PRAYER_STONE_RITUALS = ['protect',
                        'swap',
                        'teleport',
                        'create_resource',
                        'portal',
                        'destroy_resource', ]
MAGICIAN_RITUALS = ['portal', 'swap', 'teleport']
"""

VALUES

"""
DECREE_COST = 25
DECREE_INCREMENT = 5
DEFAULT_PIECE_LIMIT = 3
TRADING_GIVE_BOUNDS = (5 / 8, 1 / 2)
TRADING_RECEIVE_BOUNDS = (5 / 8, 15 / 16)
NUMBER_OF_STARTING_PIECES = 5
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
"""

DICTIONARIES

"""
PIECE_COSTS = {'king': {'log': 0, 'gold': 0, 'stone': 0},
               'gold_general': {'log': 0, 'gold': 0, 'stone': 0},
               'quarry_1': {'log': 3, 'gold': 0, 'stone': 0},
               'pawn': {'log': 6, 'gold': 0, 'stone': 0},
               'builder': {'log': 6, 'gold': 0, 'stone': 0},
               'monk': {'log': 6, 'gold': 0, 'stone': 1},
               'pikeman': {'log': 0, 'gold': 4, 'stone': 4},
               'castle': {'log': 10, 'gold': 0, 'stone': 0},
               'stable': {'log': 10, 'gold': 0, 'stone': 10},
               'barracks': {'log': 4, 'gold': 10, 'stone': 0},
               'fortress': {'log': 0, 'gold': 12, 'stone': 12},
               'queen': {'log': 0, 'gold': 12, 'stone': 12},
               'rook': {'log': 0, 'gold': 5, 'stone': 5},
               'bishop': {'log': 5, 'gold': 5, 'stone': 0},
               'knight': {'log': 1, 'gold': 0, 'stone': 3},
               'jester': {'log': 0, 'gold': 10, 'stone': 0},
               'rogue_rook': {'log': 0, 'gold': 10, 'stone': 10},
               'rogue_bishop': {'log': 7, 'gold': 7, 'stone': 0},
               'rogue_knight': {'log': 5, 'gold': 0, 'stone': 5},
               'rogue_pawn': {'log': 6, 'gold': 0, 'stone': 0},
               'elephant': {'log': 8, 'gold': 0, 'stone': 8},
               'ram': {'log': 8, 'gold': 0, 'stone': 8},
               'unicorn': {'log': 12, 'gold': 0, 'stone': 12},
               'monolith': {'log': 0, 'gold': 0, 'stone': 16},
               'prayer_stone': {'log': 0, 'gold': 0, 'stone': 8},
               'duke': {'log': 6, 'gold': 12, 'stone': 13},
               'oxen': {'log': 12, 'gold': 0, 'stone': 12},
               'champion': {'log': 0, 'gold': 7, 'stone': 7},
               'wall': {'log': 0, 'gold': 0, 'stone': 3},
               'persuader': {'log': 0, 'gold': 14, 'stone': 0},
               'doe': {'log': 14, 'gold': 0, 'stone': 14},
               'trader': {'log': 6, 'gold': 0, 'stone': 0},
               'circus': {'log': 0, 'gold': 10, 'stone': 0},
               'trapper': {'log': 6, 'gold': 0, 'stone': 0},
               'trap': {'log': 0, 'gold': 0, 'stone': 1},
               'lion': {'log': 0, 'gold': 20, 'stone': 0},
               'fire_spinner': {'log': 0, 'gold': 18, 'stone': 0},
               'acrobat': {'log': 0, 'gold': 18, 'stone': 0},
               'magician': {'log': 0, 'gold': 10, 'stone': 0},

               }
NOTIFICATIONS = {None: ['cannot select'],
                 'invalid_start_spawn': ['select a valid spawn square'],
                 'non_occupyable': ['square cannot be occupied'],
                 'players_nearby': ['a player is too close'],
                 'open_spaces': ['not enough open spaces'],
                 'piece_action': ['no piece actions remaining'],
                 'player_action': ['no turn actions remaining'],
                 'invalid_move': ['cannot move to that square'],
                 'resources': ['not enough resources to build'],
                 }
DESCRIPTIONS = {'king': ['every player gets one', 'capture your opponent\'s to win'],
                'gold_general': ['???'],
                'quarry_1': ['can be mined for stone', 'may cave in and begin to yield less stone',
                             'eventually becomes depleted if mined after it caves in'],
                'pawn': ['moves two spaces orthogonally', 'harvests resources',
                         'mines certain empty squares to create quarries'],
                'builder': ['creates buildings used to purchase more powerful pieces'],
                'monk': ['prays at monoliths to cast powerful rituals'],
                'pikeman': ['moves one square orthogonally', 'a valuable defender'],
                'castle': ['creates essential pieces such as pawns and builders'],
                'stable': ['creates cavalry such as knights, elephants and rams', 'these pieces are known as leapers',
                           'all leapers can capture walls'],
                'barracks': ['creates standard chess pieces such as rooks and bishops'],
                'fortress': ['creates rogue versions of the standard chess pieces',
                             'rogue pieces move through forest tiles and steal resources from pieces of the opposite color'],
                'queen': ['the most powerful piece in a standard chess set', 'attacks orthogonally and diagonally',
                          'right clicking her will allow you to ban all rituals for a gold cost'],
                'rook': ['attacks orthogonally', 'is able to pray at prayer sites'],
                'bishop': ['attacks diagonally', 'is able to pray at prayer sites'],
                'knight': ['moves up two and over one'],
                'jester': ['does not capture pieces', 'moves like a queen',
                           'pieces nearby are distracted by his performance and cannot act'],
                'rogue_rook': ['moves orthoganlly',
                               'can steal a resource of your choosing from a piece of the opposite color',
                               'can move onto forest tiles as if they are not there'],
                'rogue_bishop': ['moves diagonally',
                                 'can steal a resource of your choosing from a piece of the opposite color',
                                 'can move onto forest tiles as if they are not there'],
                'rogue_knight': ['moves up two and over one',
                                 'can steal a resource of your choosing from a piece of the opposite color',
                                 'can move onto forest tiles as if they are not there'],
                'rogue_pawn': ['moves orthogonally up to two spaces', 'attacks diagonally one space',
                               'able to harvest resources',
                               'can steal a resource of your choosing from a piece of the opposite color',
                               'can move through forest tiles as if they are not there'],
                'oxen': ['moves like a knight, then like a rook from that square'],
                'champion': ['moves diagonally one square',
                             'then moves like a rook from that square in the same two directions'],
                'elephant': ['moves like a knight',
                             'if it\'s knight move was unobstructed it can move forward one more square'],
                'ram': ['moves like a knight, then like a bishop in those two directions'],
                'unicorn': ['moves like a knight ', 'moves two forward in every direction',
                            'makes an additional knight move if nothing obstructs it\'s movement'],
                'monolith': ['casts powerful rituals', 'requires praying pieces to use'],
                'prayer_stone': ['casts useful rituals', 'requiring praying pieces to use'],
                'duke': ['moves like a queen', 'is able to pray at prayer sites'],
                'smite': ['select one piece or building to be destroyed'],
                'destroy_resource': ['select one resource to be destroyed'],
                'create_resource': ['create a resource'],
                'wall': ['blocks pieces from passing through', 'can be destroyed by units in the stable or pikeman'],
                'teleport': ['teleport a piece anywhere else on the board'],
                'swap': ['trade places with another piece'],
                'line_destroy': ['destroys everything in it\'s path'],
                'protect': ['protects a square from capture or destruction'],
                'doe': ['moves like a knight and a bishop'],
                'persuader': ['can convert the color of nearby pieces'],
                'portal': ['creates a portal on any two squares',
                           'pieces who land on either square will be transported', 'to the other one'],
                'trader': ['converts resources into one another'],
                'circus': ['creates unique and strange pieces like the jester'],
                'lion': ['moves like a knight and a rook'],
                'fire_spinner': ['makes knight moves until it is blocked'],
                'acrobat': ['moves like a bishop but can jump over a piece'],
                'trapper': ['creates traps which, once moved onto', 'destroy the piece that moved onto them'],
                'magician': ['casts certain rituals for a gold cost'],
                }
PIECE_POPULATION = {'king': 1,
                    'queen': 1,
                    'rook': 1,
                    'bishop': 1,
                    'knight': 1,
                    'pawn': 1,
                    'castle': 0,
                    'duke': 1,
                    'rogue_bishop': 1,
                    'jester': 1,
                    'rogue_rook': 1,
                    'war_tower': 0,
                    'elephant': 1,
                    'pikeman': 1,
                    'champion': 1,
                    'gold_general': 6,
                    'silver_general': 1,
                    'elephant_cart': 1,
                    'flag': 0,
                    'barracks': 0,
                    'rogue_pawn': 1,
                    'monolith': 0,
                    'prayer_stone': 0,
                    'monk': 1,
                    'fortress': 0,
                    'rogue_knight': 1,
                    'builder': 1,
                    'quarry_1': 0,
                    'stable': 0,
                    'unicorn': 1,
                    'ram': 1,
                    'oxen': 1,
                    'wall': 0,
                    'doe': 1,
                    'persuader': 1,
                    'trader': 1,
                    'circus': 0,
                    'trapper': 1,
                    'trap': 0,
                    'lion': 1,
                    'fire_spinner': 1,
                    'acrobat': 1,
                    'magician': 1}
PRAYER_COSTS = {'gold_general': {'prayer': 12, 'monk': 2, 'gold': 0},  # monk yields 3, other pieces yield 2
                'smite': {'prayer': 12, 'monk': 1, 'gold': 0},  # rituals have a prayer cost & monk cost
                'destroy_resource': {'prayer': 6, 'monk': 0, 'gold': 0},
                # & a gold cost, accessed by the magician or rogue monk?
                'create_resource': {'prayer': 5, 'monk': 0, 'gold': 0},
                'teleport': {'prayer': 6, 'monk': 0, 'gold': 4},
                'swap': {'prayer': 2, 'monk': 0, 'gold': 3},
                'line_destroy': {'prayer': 9, 'monk': 1, 'gold': 0},
                'portal': {'prayer': 2, 'monk': 0, 'gold': 2},
                'protect': {'prayer': 2, 'monk': 0, 'gold': 0}}
ADDITIONAL_PIECE_LIMIT = {'castle': 5, 'barracks': 5, 'fortress': 3, 'stable': 3, 'circus': 3,
                          'king': 0,
                          'queen': 0,
                          'rook': 0,
                          'bishop': 0,
                          'knight': 0,
                          'pawn': 0,
                          'monk': 0,
                          'jester': 0,
                          'silver_general': 0,
                          'gold_general': 0,
                          'pikeman': 0,
                          'champion': 0,
                          'rogue_rook': 0,
                          'rogue_bishop': 0,
                          'rogue_knight': 0,
                          'rogue_pawn': 0,
                          'elephant': 0,
                          'elephant_cart': 0,
                          'monolith': 2,
                          'prayer_stone': 1,
                          'wall': 0,
                          'flag': 0,
                          'duke': 0,
                          'war_tower': 0,
                          'quarry_1': 0,
                          'builder': 0,
                          'unicorn': 0,
                          'ram': 0,
                          'oxen': 0,
                          'doe': 0,
                          'persuader': 0,
                          'trader': 0,
                          'trapper': 0,
                          'trap': 0,
                          'lion': 0,
                          'fire_spinner': 0,
                          'acrobat': 0,
                          'magician': 0}
BASE_TOTAL_YIELD = {'wood': 8,
                    'gold': 25,
                    'quarry': 12,
                    'sunken_quarry': 2}
TOTAL_YIELD_VARIANCE = {'wood': (-2, 2),
                        'gold': (-3, 3),
                        'quarry': (-2, 2),
                        'sunken_quarry': (0, 2)}
BASE_YIELD_PER_HARVEST = {'pawn':
                              {'wood': 10,
                               'gold': 7,
                               'quarry': 8,
                               'sunken_quarry': 1},
                          'rogue_pawn':
                              {'wood': 7,
                               'gold': 2,
                               'quarry': 5,
                               'sunken_quarry': 1}}
HARVEST_YIELD_VARIANCE = {'wood': (-2, 2),
                          'gold': (-2, 2),
                          'quarry': (-3, 3),
                          'sunken_quarry': (0, 2)}
STEALING_KEY = {'building': {
                'wood': {'variance': (-2, 2), 'value': 5},
                'gold': {'variance': (-2, 2), 'value': 5},
                'stone': {'variance': (-2, 2), 'value': 5}},
                'trader': {
                'wood': {'variance': (-3, 4), 'value': 10},
                'gold': {'variance': (-3, 4), 'value': 10},
                'stone': {'variance': (-3, 4), 'value': 10}},
                'piece': {
                'wood': {'variance': (-2, 2), 'value': 4},
                'gold': {'variance': (-2, 2), 'value': 4},
                'stone': {'variance': (-2, 2), 'value': 4}}}
"""  

SOUND

"""
SOUND_EFFECT_VOLUME = .5


VERSION = "v24"
NUMBER = ""
MAX_FPS = 120

"""

SPRITE SCALING

"""
DEFAULT_PIECE_SCALE = (SQ_SIZE, SQ_SIZE)
HIGHLIGHT_ALPHA = 110
SPAWNING_MENU_WIDTH = round(SQ_SIZE * 5.5)
SPAWNING_MENU_HEIGHT_BUFFER = SQ_SIZE * 1.3
SIDE_MENU_HEIGHT = BOARD_HEIGHT_PX
GAME_NAME_SCALE = (round(SQ_SIZE * 1.5), round(SQ_SIZE * 1.5))
PICKAXE_SCALE = (SQ_SIZE * 2, SQ_SIZE * 2)
CENTER_X = BOARD_WIDTH_SQ * SQ_SIZE // 2 + SQ_SIZE // 2
CENTER_Y = BOARD_HEIGHT_SQ * SQ_SIZE // 2
KING_MENU_HEIGHT = (SQ_SIZE // 6) * 2 + SQ_SIZE
KING_MENU_WIDTH = KING_MENU_HEIGHT
DECREE_SCALE = (KING_MENU_WIDTH, KING_MENU_HEIGHT)
START_MENU_WIDTH = round(SQ_SIZE * 6.5)
START_MENU_HEIGHT = round(SQ_SIZE * 3.5)
PRAYER_BAR_WIDTH = round(SQ_SIZE // 64)
PRAYER_BAR_END_WIDTH = round(SQ_SIZE // 6)
PRAYER_BAR_HEIGHT = round(SQ_SIZE // 2.8)
PRAYER_BAR_SCALE = (PRAYER_BAR_WIDTH, PRAYER_BAR_HEIGHT)
PRAYER_BAR_END_SCALE = (PRAYER_BAR_END_WIDTH, PRAYER_BAR_HEIGHT)
TREE_SCALE_1 = (round(SQ_SIZE * 1.3), round(SQ_SIZE * 1.3))
TREE_SCALE_2 = (round(SQ_SIZE * 1.38), round(SQ_SIZE * 1.38))
TREE_SCALE_3 = (round(SQ_SIZE * 1.35), round(SQ_SIZE * 1.35))
TREE_SCALE_4 = (round(SQ_SIZE * 1.38), round(SQ_SIZE * 1.38))
GOLD_SCALE = (round(SQ_SIZE * 1.1), round(SQ_SIZE * 1.1))
QUARRY_SCALE = (round(SQ_SIZE * 1.1), round(SQ_SIZE * 1.1))
TREE_OFFSET = (round(SQ_SIZE // -5.5), round(SQ_SIZE // -3.5))
GOLD_OFFSET = (round(SQ_SIZE // -10), round(SQ_SIZE // -10))
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
PROTECT_SQUARE_SCALE = (SQ_SIZE, SQ_SIZE)
PROTECT_SQUARE_OFFSET = (SQ_SIZE // 2 - PROTECT_SQUARE_SCALE[0] // 2, SQ_SIZE // 2 - PROTECT_SQUARE_SCALE[1] // 2)
RITUAL_IMAGE_MODIFY = {'gold_general': {'SCALE': PRAYER_RITUAL_SCALE, 'OFFSET': (0, 0)},
                       'smite': {'SCALE': PRAYER_RITUAL_SCALE, 'OFFSET': (0, 0)},
                       'destroy_resource': {'SCALE': PRAYER_RITUAL_SCALE, 'OFFSET': (0, 0)},
                       'create_resource': {'SCALE': PRAYER_RITUAL_SCALE, 'OFFSET': (0, 0)},
                       'teleport': {'SCALE': PRAYER_RITUAL_SCALE, 'OFFSET': (0, 0)},
                       'swap': {'SCALE': PRAYER_RITUAL_SCALE, 'OFFSET': (0, 0)},
                       'line_destroy': {'SCALE': PRAYER_RITUAL_SCALE, 'OFFSET': (0, 0)},
                       'portal': {'SCALE': PRAYER_RITUAL_SCALE, 'OFFSET': (0, 0)},
                       'protect': {'SCALE': PRAYER_RITUAL_SCALE, 'OFFSET': (0, 0)}}
PIECE_IMAGE_MODIFY = {'king': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'queen': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'rook': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'bishop': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'knight': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'pawn': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'monk': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'duke': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'rogue_bishop': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'jester': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'pikeman': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'gold_general': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'silver_general': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'rogue_rook': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'elephant': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'elephant_cart': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'champion': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'rogue_pawn': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'rogue_knight': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'castle': {'SCALE': CASTLE_SCALE, 'OFFSET': CASTLE_OFFSET},
                      'fortress': {'SCALE': FORTRESS_SCALE, 'OFFSET': FORTRESS_OFFSET},
                      'wall': {'SCALE': FORTRESS_SCALE, 'OFFSET': WALL_OFFSET},
                      'monolith': {'SCALE': BARRACKS_SCALE, 'OFFSET': BARRACKS_OFFSET},
                      'prayer_stone': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'flag': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'barracks': {'SCALE': BARRACKS_SCALE, 'OFFSET': BARRACKS_OFFSET},
                      'war_tower': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'builder': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'unicorn': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'ram': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'stable': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'oxen': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'trader': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'doe': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'persuader': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'circus': {'SCALE': BARRACKS_SCALE, 'OFFSET': BARRACKS_OFFSET},
                      'trapper': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'trap': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'lion': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'fire_spinner': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'acrobat': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                      'magician': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},

                      }
IMAGES_IMAGE_MODIFY = {'icon': {'SCALE': DEFAULT_PIECE_SCALE, 'OFFSET': (0, 0)},
                       'pickaxe': {'SCALE': PICKAXE_SCALE, 'OFFSET': (0, 0)},
                       'w_game_name': {'SCALE': GAME_NAME_SCALE, 'OFFSET': (0, 0)},
                       'b_game_name': {'SCALE': GAME_NAME_SCALE, 'OFFSET': (0, 0)},
                       'prayer': {'SCALE': PICKAXE_SCALE, 'OFFSET': (0, 0)},
                       'gold_coin': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'give': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'receive': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'log': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'action': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'prayer_bar_end': {'SCALE': PRAYER_BAR_END_SCALE, 'OFFSET': (0, 0)},
                       'units': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'prayer_bar': {'SCALE': PRAYER_BAR_SCALE, 'OFFSET': (0, 0)},
                       'hour_glass': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'stone': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'w_boat': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'hammer': {'SCALE': PICKAXE_SCALE, 'OFFSET': (0, 0)},
                       'axe': {'SCALE': PICKAXE_SCALE, 'OFFSET': (0, 0)},
                       'b_boat': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                       'resources_button': {'SCALE': RESOURCES_BUTTON_SCALE, 'OFFSET': (0, 0)},
                       'b_no': {'SCALE': YES_NO_BUTTON_SCALE, 'OFFSET': (0, 0)},
                       'b_yes': {'SCALE': YES_NO_BUTTON_SCALE, 'OFFSET': (0, 0)},
                       'w_no': {'SCALE': YES_NO_BUTTON_SCALE, 'OFFSET': (0, 0)},
                       'w_yes': {'SCALE': YES_NO_BUTTON_SCALE, 'OFFSET': (0, 0)},
                       'w_protect': {'SCALE': PROTECT_SQUARE_SCALE, 'OFFSET': PROTECT_SQUARE_OFFSET},
                       'b_protect': {'SCALE': PROTECT_SQUARE_SCALE, 'OFFSET': PROTECT_SQUARE_OFFSET},
                       'w_decree': {'SCALE': DECREE_SCALE, 'OFFSET': (0, 0)},
                       'b_decree': {'SCALE': DECREE_SCALE, 'OFFSET': (0, 0)},
                       'w_decree_u': {'SCALE': DECREE_SCALE, 'OFFSET': (0, 0)},
                       'b_decree_u': {'SCALE': DECREE_SCALE, 'OFFSET': (0, 0)},
                       'persuade': {'SCALE': PICKAXE_SCALE, 'OFFSET': (0, 0)},
                       'w_block': {'SCALE': PROTECT_SQUARE_SCALE, 'OFFSET': PROTECT_SQUARE_OFFSET},
                       'b_block': {'SCALE': PROTECT_SQUARE_SCALE, 'OFFSET': PROTECT_SQUARE_OFFSET},
                       'w_portal': {'SCALE': PROTECT_SQUARE_SCALE, 'OFFSET': PROTECT_SQUARE_OFFSET},
                       'b_portal': {'SCALE': PROTECT_SQUARE_SCALE, 'OFFSET': PROTECT_SQUARE_OFFSET},
                       'steal': {'SCALE': PICKAXE_SCALE, 'OFFSET': (0, 0)}}
RESOURCES_IMAGE_MODIFY = {'gold_tile_1': {'SCALE': GOLD_SCALE, 'OFFSET': GOLD_OFFSET},
                          'tree_tile_1': {'SCALE': TREE_SCALE_1, 'OFFSET': TREE_OFFSET},
                          'tree_tile_2': {'SCALE': TREE_SCALE_2, 'OFFSET': TREE_OFFSET},
                          'tree_tile_3': {'SCALE': TREE_SCALE_3, 'OFFSET': TREE_OFFSET},
                          'tree_tile_4': {'SCALE': TREE_SCALE_4, 'OFFSET': TREE_OFFSET},
                          'quarry_1': {'SCALE': QUARRY_SCALE, 'OFFSET': (0, 0)},
                          'sunken_quarry_1': {'SCALE': QUARRY_SCALE, 'OFFSET': (0, 0)},
                          'depleted_quarry_1': {'SCALE': QUARRY_SCALE, 'OFFSET': (0, 0)}}
MENU_ICONS_IMAGE_MODIFY = {'gold_coin': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                           'log': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                           'stone': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)},
                           'prayer': {'SCALE': MENU_ICON_DEFAULT_SCALE, 'OFFSET': (0, 0)}}



