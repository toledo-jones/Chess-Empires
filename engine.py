import sys

from map import *
from sound import *
from state import *
from trades import *
from player import Player

if typing.TYPE_CHECKING:
    from client import GameClient


def exit_game():
    """
    Exits the game.
    """
    # Save settings to file
    constant.save_settings()
    # Quit the game
    pygame.quit()
    # Exit the program
    sys.exit()


def initialize_maps() -> list[type]:
    """
    Returns a list of available maps.

    :return: A list of map classes.
    """
    # Return a list of map classes
    return [
        Default,
        Minimal,
        VTrees,
        TriangleTrees,
        UltraBalanced,
        LeftRight,
        OnlyStoneAndGold,
        FourCorners,
        CenterCircleA,
        CenterCircleB,
        EnclosedForest,
        GoldCornersA,
        GoldCornersB,
        Islands,
        WoodlandQuarries,
        GoldForest,
        LeftRightModified,
        TopBottomModified,
        IslandsModified,
        Full,
        ATrees,
        AngleTrees,
        HyperBalanced,
        OctoBalanced,
        FirstClass,
        Perfect,
    ]


def initialize_resources() -> dict[str, type]:
    """
    Returns a dictionary of resource types.

    :return: A dictionary mapping resource names to their classes.
    """
    # Return a dictionary of resource types
    return {
        "tree_tile_1": Wood,
        "gold_tile_1": Gold,
        "quarry_1": Quarry,
        "tree_tile_2": Wood,
        "tree_tile_3": Wood,
        "tree_tile_4": Wood,
        "sunken_quarry_1": SunkenQuarry,
        "depleted_quarry_1": DepletedQuarry,
    }


def initialize_menus() -> dict[str, type]:
    """
    Returns a dictionary of building menus.

    :return: A dictionary mapping menu names to their classes.
    """
    # Return a dictionary of building menus
    return {
        "stable": StableMenu,
        "fortress": FortressMenu,
        "barracks": BarracksMenu,
        "builder": BuilderMenu,
        "castle": CastleMenu,
        "circus": CircusMenu,
        "trapper": TrapperMenu,
        "monk": MonkMenu,
    }


def initialize_cost_menus() -> dict[str, type]:
    """
    Returns a dictionary of cost menus.

    :return: A dictionary mapping cost menu names to their classes.
    """
    # Return a dictionary of cost menus
    return {
        "builder": BuilderCosts,
        "castle": CastleCosts,
        "stable": StableCosts,
        "fortress": FortressCosts,
        "prayer_stone": PrayerStoneCosts,
        "monolith": MonolithCosts,
        "barracks": BarracksCosts,
        "circus": CircusCosts,
        "monk": MonkCosts,
    }


def initialize_states() -> dict[str, type]:
    """
    Returns a dictionary of game states.

    :return: A dictionary mapping state names to their classes.
    """
    # Return a dictionary of game states
    return {
        "playing": Playing,
        "mining": Mining,
        "spawning": Spawning,
        "starting": Starting,
        "start spawn": StartingSpawn,
        "piece cost screen": PieceCost,
        "building": PreBuilding,
        "winner": Winner,
        "surrender": SurrenderMenu,
        "gold_general": SummonGoldGeneral,
        "smite": PerformSmite,
        "select starting pieces": SelectStartingPieces,
        "destroy_resource": PerformDestroyResource,
        "create_resource": PerformCreateResource,
        "portal": PerformPortal,
        "teleport": PerformTeleport,
        "swap": PerformSwap,
        "line_destroy": PerformLineDestroy,
        "protect": PerformProtect,
        "main menu": MainMenu,
        "debug": DebugStart,
        "inspector": Inspector,
        "instructions": Instructions,
        "pause": Pause,
        "play select": PlaySelect,
    }


def initialize_events() -> dict[str, type]:
    """
    Returns a dictionary of game events.

    :return: A dictionary mapping event names to their classes.
    """
    # Return a dictionary of game events
    return {
        "pray": Pray,
        "steal": Steal,
        "mine": Mine,
        "spawn": Spawn,
        "move": Move,
        "capture": Capture,
    }


def initialize_pieces() -> dict[str, type]:
    """
    Returns a dictionary of game pieces.

    :return: A dictionary mapping piece names to their classes.
    """
    # Return a dictionary of game pieces
    return {
        "king": King,
        "queen": Queen,
        "rook": Rook,
        "bishop": Bishop,
        "knight": Knight,
        "pawn": Pawn,
        "castle": Castle,
        "monk": Monk,
        "fortress": Fortress,
        "ram": Ram,
        "elephant": Elephant,
        "barracks": Barracks,
        "jester": Jester,
        "champion": Champion,
        "prayer_stone": PrayerStone,
        "monolith": Monolith,
        "pikeman": Pikeman,
        "rogue_rook": RogueRook,
        "rogue_bishop": RogueBishop,
        "rogue_knight": RogueKnight,
        "rogue_pawn": RoguePawn,
        "builder": Builder,
        "unicorn": Unicorn,
        "stable": Stable,
        "gold_general": GoldGeneral,
        "duke": Duke,
        "oxen": Oxen,
        "wall": Wall,
        "doe": Doe,
        "persuader": Persuader,
        "trader": Trader,
        "circus": Circus,
        "trapper": Trapper,
        "trap": Trap,
        "lion": Lion,
        "fire_spinner": FireSpinner,
        "acrobat": Acrobat,
        "magician": Magician,
        "cavalry": Cavalry,
        "ferz": Ferz,
        "assassin": Assassin,
    }


def generate_available_rituals(potential_rituals: list[str], limit: int) -> list[str]:
    """
    Generates a list of available rituals based on the given potential rituals and limit.

    :param potential_rituals: A list of potential ritual classes.
    :param limit: The maximum number of rituals to generate.
    :return: A list of available ritual classes.
    """
    # Determine the length of the new ritual list, randomly between 1 and the limit
    length_of_new_ritual_list: int = random.randint(1, limit)
    # Initialize the list of available rituals
    available_rituals: list[str] = []
    # Shuffle the list of potential rituals
    random.shuffle(potential_rituals)

    # Append the selected number of rituals to the available rituals list
    for i in range(length_of_new_ritual_list):
        available_rituals.append(potential_rituals[i])

    return available_rituals


def initialize_rituals() -> list[list[str]]:
    """
    Initializes rituals based on debug mode.

    :return: A tuple containing lists of monolith, prayer stone, and magician rituals.
    """
    # Check if debug mode is enabled for rituals
    if constant.DEBUG_RITUALS:
        # Return predefined rituals for debug mode
        return [
            [constant.MONOLITH_RITUALS],
            [constant.PRAYER_STONE_RITUALS],
            [constant.MAGICIAN_RITUALS],
        ]

    # Generate available rituals based on game constants
    return [
        generate_available_rituals(
            constant.MONOLITH_RITUALS, constant.MAX_MONOLITH_RITUALS_PER_TURN
        ),
        generate_available_rituals(
            constant.PRAYER_STONE_RITUALS,
            constant.MAX_PRAYER_STONE_RITUALS_PER_TURN,
        ),
        generate_available_rituals(
            constant.MAGICIAN_RITUALS, constant.MAX_MAGICIAN_RITUALS_PER_TURN
        ),
    ]


def generate_stealing_offsets(
    stealing_key: dict[str, dict[str, tuple[int, int]]],
) -> list[int]:
    """
    Generates a list of stealing offsets based on the given stealing key.

    :param stealing_key: A dictionary containing variance ranges for resources.
    :return: A list of stealing offsets.
    """
    # Extract variance ranges for wood, gold, and stone
    variance_list: list[tuple[int, int]] = [
        stealing_key["wood"]["variance"],
        stealing_key["gold"]["variance"],
        stealing_key["stone"]["variance"],
    ]

    # Initialize the list of stealing offsets
    stealing_offsets: list[int] = []

    # Generate a random offset for each variance range and append to the list
    for variance in variance_list:
        rand: int = random.randint(variance[0], variance[1])
        stealing_offsets.append(rand)

    return stealing_offsets


def initialize_stealing_offsets() -> list[list[int]]:
    """
    Initializes stealing offsets for pieces, buildings, and traders.

    :return: A list containing lists of stealing offsets for pieces, buildings, and traders.
    """
    # Generate stealing offsets for pieces, buildings, and traders
    return [
        generate_stealing_offsets(constant.STEALING_KEY["piece"]),
        generate_stealing_offsets(constant.STEALING_KEY["building"]),
        generate_stealing_offsets(constant.STEALING_KEY["trader"]),
    ]


def piece_is_selected(piece: Unit) -> bool:
    """
    Checks if a piece is selected or performing any action.

    :param piece: The piece to check.
    :return: True if the piece is selected or performing any action, False otherwise.
    """
    # List of attributes indicating the piece is selected or performing an action
    selected_list: list[bool] = [
        piece.selected,
        piece.mining,
        piece.pre_selected,
        piece.purchasing,
        piece.praying,
        piece.casting,
        piece.stealing,
        piece.persuading,
    ]
    # Return True if any attribute in the list is True
    return any(selected_list)


class Engine:
    def __init__(
        self, window: Optional[pygame.Surface] = None, board: Optional[list[list[Tile]]] = None
    ):
        """
        Initializes the game engine and sets up game attributes.

        :param window: The game window surface.
        :param board: The game board, optional.
        """
        # Set the running state to True
        self.running: bool = True
        # Set the game window
        self.window: pygame.Surface = window

        # Board Setup
        # Set the number of columns
        self.cols: int = constant.BOARD_WIDTH_SQ
        # Set the number of rows
        self.rows: int = constant.BOARD_HEIGHT_SQ

        # This flag is set true when the game is played over the network
        self.online = False

        # This will hold the client which will connect to the server
        self._client = None

        # Set the game board
        self.board = board

        if not board:
            # Initialize the game board with Tile objects
            self.board: list[list[Tile]] = [
                [Tile(x, y) for y in range(self.cols)] for x in range(self.rows)
            ]
            # Create a surface for the board
            self.board_surface: pygame.Surface = pygame.Surface(
                (self.cols * constant.SQ_SIZE, self.rows * constant.SQ_SIZE)
            )
            # Create a surface for the display
            self.display_surface: pygame.Surface = pygame.Surface(
                (self.window.get_width(), self.rows * constant.SQ_SIZE)
            )
            # Initialize the map to None
            self.map: Optional[Map] = None

        # Game State
        # Initialize the winner to None
        self.winner: Optional[str] = None
        # Initialize the popup reason to None
        self.popup_reason: Optional[str] = None
        # Initialize the turn to None
        self.turn: Optional[str] = None
        # Set the first turn flag to True
        self.first: bool = True
        # Set the first turn flag to True
        self.first_turn: bool = True
        # Set the turn count display
        self.turn_count_display: float = 0.5
        # Set the actual turn count
        self.turn_count_actual: int = -1
        # Initialize the state list
        self.state: list[State] = []
        # Initialize the players dictionary
        self.players: Optional[dict[str, Player]] = {}

        # Gameplay Mechanics
        # Initialize the spawn list
        self.spawn_list: list[str] = []
        # Initialize the spawn count
        self.spawn_count: int = 0
        # Initialize the spawn success flag
        self.spawn_success: bool = False
        # Initialize the spawning piece
        self.spawning: Optional[str] = None
        # Initialize the final spawn flag
        self.final_spawn: bool = False
        # Initialize the ritual
        self.ritual: Optional[Ritual] = None
        # Initialize the rituals banned flag
        self.rituals_banned: bool = False
        # Initialize the mining flag
        self.mining: bool = False
        # Initialize the praying flag
        self.praying: bool = False
        # Initialize the check flag
        self.check: bool = False
        # Initialize the surrendering flag
        self.surrendering: bool = False
        # Initialize the stealing piece
        self.stealing: Optional[Tuple[str, int]] = None
        # Initialize the piece trading
        self.piece_trading: Optional[Piece] = None
        # Initialize the trading list
        self.trading: list[Tuple[str, int]] = []

        # UI Elements
        # Initialize the menus list
        self.menus: list[Menu] = []
        # Initialize the piece cost screen flag
        self.piece_cost_screen: bool = False

        self.PIECE_COSTS = {
            "king": {"log": 0, "gold": 0, "stone": 0},
            "gold_general": {"log": 0, "gold": 0, "stone": 0},
            "pawn": {"log": 6, "gold": 0, "stone": 0},
            "builder": {"log": 6, "gold": 0, "stone": 0},
            "monk": {"log": 6, "gold": 0, "stone": 1},
            "pikeman": {"log": 0, "gold": 4, "stone": 4},
            "castle": {"log": 10, "gold": 0, "stone": 0},
            "stable": {"log": 10, "gold": 0, "stone": 10},
            "barracks": {"log": 4, "gold": 10, "stone": 0},
            "fortress": {"log": 0, "gold": 12, "stone": 12},
            "queen": {"log": 0, "gold": 12, "stone": 12},
            "rook": {"log": 0, "gold": 5, "stone": 5},
            "bishop": {"log": 5, "gold": 5, "stone": 0},
            "knight": {"log": 1, "gold": 0, "stone": 3},
            "jester": {"log": 0, "gold": 10, "stone": 0},
            "rogue_rook": {"log": 0, "gold": 10, "stone": 10},
            "rogue_bishop": {"log": 7, "gold": 7, "stone": 0},
            "rogue_knight": {"log": 5, "gold": 0, "stone": 5},
            "rogue_pawn": {"log": 6, "gold": 0, "stone": 0},
            "elephant": {"log": 8, "gold": 0, "stone": 8},
            "ram": {"log": 8, "gold": 0, "stone": 8},
            "unicorn": {"log": 12, "gold": 0, "stone": 12},
            "monolith": {"log": 0, "gold": 0, "stone": 16},
            "prayer_stone": {"log": 0, "gold": 0, "stone": 8},
            "duke": {"log": 6, "gold": 12, "stone": 13},
            "oxen": {"log": 12, "gold": 0, "stone": 12},
            "champion": {"log": 0, "gold": 7, "stone": 7},
            "wall": {"log": 0, "gold": 0, "stone": 3},
            "persuader": {"log": 0, "gold": 14, "stone": 0},
            "doe": {"log": 14, "gold": 0, "stone": 14},
            "trader": {"log": 6, "gold": 0, "stone": 0},
            "circus": {"log": 0, "gold": 10, "stone": 0},
            "trapper": {"log": 6, "gold": 0, "stone": 0},
            "trap": {"log": 0, "gold": 0, "stone": 1},
            "lion": {"log": 0, "gold": 20, "stone": 0},
            "fire_spinner": {"log": 0, "gold": 18, "stone": 0},
            "acrobat": {"log": 0, "gold": 18, "stone": 0},
            "magician": {"log": 0, "gold": 10, "stone": 0},
            "cavalry": {"log": 4, "gold": 1, "stone": 0},
            "ferz": {"log": 6, "gold": 0, "stone": 0},
            "assassin": {"log": 0, "gold": 10, "stone": 0},
        }

        # Game Modifiers
        # Initialize the protected tiles list
        self.protected_tiles: list[Tile] = []
        # Initialize the pieces checking list
        self.pieces_checking: list[Piece] = []
        # Initialize the used and intercepted pieces list
        self.used_and_intercepted_pieces: list[Unit] = []

        # Rituals & Stealing
        # Initialize the ritual summon resource
        self.ritual_summon_resource: Optional[str] = None
        # Initialize the rituals
        self.monolith_rituals, self.prayer_stone_rituals, self.magician_rituals = (
            initialize_rituals()
        )
        # Initialize the stealing offsets
        (
            self.piece_stealing_offsets,
            self.building_stealing_offsets,
            self.trader_stealing_offsets,
        ) = initialize_stealing_offsets()

        # Events
        # Initialize the events list
        self.events: list[GameEvent] = []
        # Initialize the decrees count
        self.decrees: int = 0

        # Constants & Mapping
        # Initialize the colors dictionary
        self.COLORS: dict[int, str] = {0: "dark", 1: "light"}
        # Initialize the pieces dictionary
        self.PIECES: dict[str, type] = initialize_pieces()
        # Initialize the states dictionary
        self.STATES: dict[str, type] = initialize_states()
        # Initialize the resources dictionary
        self.RESOURCES: dict[str, type] = initialize_resources()
        # Initialize the maps list
        self.MAPS: list[type] = initialize_maps()
        # Initialize the menus dictionary
        self.MENUS: dict[str, type] = initialize_menus()
        # Initialize the cost menus dictionary
        self.COST_MENUS: dict[str, type] = initialize_cost_menus()
        # Initialize the events dictionary
        self.EVENTS: dict[str, type] = initialize_events()
        # Initialize the stealing values dictionary
        self.STEALING_VALUES: dict[str, int] = {"wood": 0, "gold": 1, "stone": 2}
        # Initialize the kind to stealing list dictionary
        self.KIND_TO_STEALING_LIST: [dict[str, dict[str, int | tuple[int, int]]]] = {
            "piece": self.piece_stealing_offsets,
            "building": self.building_stealing_offsets,
            "trader": self.trader_stealing_offsets,
        }

        # Trade & Sounds
        # Initialize the trade handler
        self.trade_handler: Trades = Trades(self)
        # Initialize the trade conversions list
        self.trade_conversions: list[dict[str, tuple[float, float]]] = [
            self.trade_handler.get_conversions()
        ]
        # Initialize the sounds
        self.sounds: Sounds = Sounds()

    def reset(self):
        """
        Resets the engine's running state.
        """
        # Set the running state to False
        self.running: bool = False

    def pause(self):
        """
        Pauses the game by appending the Pause state.
        """
        # Append the Pause state to the state list
        self.state.append(Pause(self.display_surface, self))

    def draw_display_surface(self):
        """
        Draws the display surface centered on the window.
        """
        # Calculate the vertical offset to center the display surface
        offset_y: int = (
            self.window.get_height() // 2 - self.display_surface.get_height() // 2
        )
        # Blit the display surface onto the window at the calculated offset
        self.window.blit(self.display_surface, (0, offset_y))

    def tile_in_bounds(self, r, c):
        try:
            # Get the number of rows and columns in the board
            rows = len(self.board)
            cols = len(self.board[r]) if rows > 0 else 0  # Handle case for empty board

        # Check if the row and column are within bounds
        except IndexError:
            return False
        return 0 <= r < rows and 0 <= c < cols

    def reset_flags(self):
        """
        Resets various gameplay flags to their default state.
        """
        # Reset the spawning piece to None
        self.spawning: Optional[str] = None
        # Reset the stealing piece to None
        self.stealing: Optional[Piece] = None
        # Reset the piece trading to None
        self.piece_trading: Optional[Piece] = None
        # Reset the trading list
        self.trading: list[Tuple[str, int]] = []
        # Reset the mining flag to False
        self.mining: bool = False
        # Reset the praying flag to False
        self.praying: bool = False

    def get_decree_cost(self) -> int:
        """
        Calculates the cost of a decree based on the number of decrees already issued.

        :return: The cost of the next decree.
        """
        # Get the decree cost dictionary
        decree_cost: dict[str, int] = constant.DECREE_COST
        # Get the list of keys from the decree cost dictionary
        keys: list[str] = list(decree_cost.keys())
        # Calculate and return the cost of the next decree
        return decree_cost[keys[-1]] + (self.decrees * constant.DECREE_INCREMENT)

    def stealing_values(self, resource: str, kind: str) -> int:
        """
        Calculates the value of a resource to be stolen based on the current game state.

        :param resource: The type of resource to be stolen (e.g., "wood", "gold", "stone").
        :param kind: The kind of stealing action (e.g., "piece", "building", "trader").
        :return: The value of the resource to be stolen.
        """
        # Get the list of offsets for the specified kind
        offset_list: list[list[int]] = self.KIND_TO_STEALING_LIST[kind]
        # Get the offset for the specified resource
        offset: int = offset_list[self.turn_count_actual][
            self.STEALING_VALUES[resource]
        ]
        # Get the base value of the resource
        base_value: int = constant.STEALING_KEY[kind][resource]["value"]
        # Calculate the total value of the resource to be stolen
        value: int = base_value + offset
        # Get the enemy player
        enemy_player: Player = self.players[constant.TURNS[self.turn]]

        # Adjust the value if the enemy player does not have enough of the resource
        if resource == "wood":
            if enemy_player.wood - value < 0:
                value = enemy_player.wood
        elif resource == "gold":
            if enemy_player.gold - value < 0:
                value = enemy_player.gold
        elif resource == "stone":
            if enemy_player.stone - value < 0:
                value = enemy_player.stone

        return value

    @property
    def client(self) -> "GameClient":
        """
        Returns the client instance.
        """
        return self._client

    @client.setter
    def client(self, client: "GameClient"):
        """
        Sets the client instance.
        """
        # Connect the client to server
        client.connect()
        # Start listening thread
        client.start_listening_thread()
        # Set the online flag to True
        self.online = True
        # Set client instance to private variable
        self._client = client

    def select_map(self):
        """
        Selects a random map, generates resources, and sets piece values.
        """
        event = SelectMap(self, None, None)
        self.add_event(event, constrain_check=False, determine_winner=False)

    def set_piece_values(self):
        """
        Sets the values for the pieces based on the resource count.
        """
        # Count the resources on the map
        resource_count: dict[str, int] = self.count_resources()
        # Set the piece values based on the resource count
        self.map.set_piece_values(resource_count)

    def count_resources(self) -> dict[str, int]:
        """
        Counts the resources on the map.

        :return: A dictionary with the count of gold, wood, and quarry resources.
        """
        # Get the base yield weights for resources
        weights: dict[str, int] = constant.BASE_TOTAL_YIELD
        # Initialize the resource count dictionary
        resource_count: dict[str, int] = {"gold": 0, "wood": 0, "quarry": 0}

        # Iterate over each row on the board
        for row in range(self.rows):
            # Iterate over each column in the current row
            for col in range(self.cols):
                # Check if the current tile has gold
                if self.has_resource(row, col, Gold):
                    resource_count["gold"] += 1
                # Check if the current tile has wood
                elif self.has_resource(row, col, Wood):
                    resource_count["wood"] += 1
                # Check if the current tile can contain a quarry
                elif self.board[row][col].can_contain_quarry:
                    resource_count["quarry"] += 1

        # Multiply the resource counts by their respective weights
        for resource in resource_count:
            resource_count[resource] *= weights[resource]

        return resource_count

    def create_player(self, color: str):
        """
        Implements player profile which holds all current pieces the player has, has captured, gold, wood, etc.
        Pulls from this player profile all data which is needed by the engine with regard to the players.
        """
        # Create a new player with the specified color
        player: Player = Player(color)
        # Add the player to the players dictionary
        self.players[color] = player

    def set_state(self, state: Union[str, State]):
        """
        Sets the current state of the game engine.

        :param state: The new state to set, either as a string or a State object.
        """
        # Accepts State Object and adds it to State List
        if isinstance(state, State):
            self.state.append(state)
        else:
            # Accepts 'state' string and converts it to state Object. Then adds it to State List
            if state == "main menu" or state == "play select":
                from splash import SplashScreen

                # Get the current window from the state
                window: pygame.Surface = self.get_current_state().get_window()
                # Create a splash screen
                splash_screen: SplashScreen = SplashScreen(self.state[-1].win)
                # Create a new state object
                new_state: State = self.STATES[state](window, self, splash_screen)
            else:
                # Create a new state object
                new_state: State = self.STATES[state](self.state[-1].win, self)

            # Set the new state
            self.set_state(new_state)

        # Removes the first state in the list if the list reaches length of two
        if len(self.state) == 2:
            del self.state[0]

    def valid_ritual(self, cost: Optional[int], cost_type: str) -> bool:
        """
        Checks if a ritual can be performed based on the cost and cost type.

        :param cost: The cost of the ritual.
        :param cost_type: The type of cost (e.g., "prayer", "gold").
        :return: True if the ritual can be performed, False otherwise.
        """
        # Check if the current player can act
        if not self.players[self.turn].can_act():
            return False

        # Check if rituals are banned
        if self.rituals_banned:
            return False

        # If there is no cost, the ritual is valid
        if not cost:
            return True

        # Check if the player has enough prayer points
        if cost_type == "prayer":
            return self.players[self.turn].prayer - cost >= 0

        # Check if the player has enough gold
        elif cost_type == "gold":
            return self.players[self.turn].gold - cost >= 0

        return False

    def valid_purchase(self, cost: dict[str, int]) -> bool:
        """
        Checks if the current player can afford the cost of a piece being spawned.

        :param cost: A dictionary with the cost of the piece in terms of resources.
        :return: True if the player can afford the piece, False otherwise.
        """
        # Check if the player has enough wood
        valid_wood: bool = self.players[self.turn].wood - cost["log"] >= 0
        # Check if the player has enough gold
        valid_gold: bool = self.players[self.turn].gold - cost["gold"] >= 0
        # Check if the player has enough stone
        valid_stone: bool = self.players[self.turn].stone - cost["stone"] >= 0

        # Return True if the player has enough of all resources, otherwise return False
        return valid_wood and valid_gold and valid_stone

    def draw(self, win: pygame.Surface):
        """
        Draws the game board and pieces on the given window surface.

        :param win: The window surface to draw on.
        """
        try:
            # Define the alternating colors for the squares
            colors: list[str] = [
                constant.DARK_SQUARE_COLOR,
                constant.LIGHT_SQUARE_COLOR,
            ]

            # Calculate the total size of the board
            board_height: int = self.board_surface.get_height()

            # Calculate the offset to center the board on the window
            window_width: int
            window_height: int
            window_width, window_height = win.get_size()
            offset_y: int = (window_height - board_height) // 2

            # Draw the board squares and tiles
            for row in range(self.rows):
                for col in range(self.cols):
                    # Calculate the color for the current square
                    color: str = colors[(row + col) % 2]

                    # Determine the rectangle size for the current square
                    rect_size: tuple[int, int] = (constant.SQ_SIZE, constant.SQ_SIZE)

                    # Calculate position for the square, with the offset
                    x: int = col * constant.SQ_SIZE
                    y: int = row * constant.SQ_SIZE

                    # Check if the square can contain a quarry and set the color to red if true
                    if constant.SHOW_STONE and self.board[row][col].can_contain_quarry:
                        color = constant.RED

                    # Draw the square
                    pygame.draw.rect(
                        self.board_surface,
                        color,
                        pygame.Rect(x, y, rect_size[0], rect_size[1]),
                    )

                    # Draw the tile using blend mode (avoid re-evaluating color calculation)
                    tile_color: str = self.COLORS[(row + col) % 2]
                    self.board_surface.blit(
                        constant.BOARD_TILES[tile_color][self.board[row][col].index],
                        (x, y),
                        special_flags=pygame.BLEND_RGBA_MULT,
                    )

            # Draw the board pieces highlights
            for row in range(self.rows):
                for col in range(self.cols):
                    self.board[row][col].draw_highlights(self.board_surface)

            # Draw the board pieces
            for row in range(self.rows):
                for col in range(self.cols):
                    self.board[row][col].draw(self.board_surface)

            # Blit the board surface to the main window
            win.blit(self.board_surface, (0, offset_y))

        except IndexError:
            pass

    def get_player_king(self) -> Optional[King]:
        """
        Retrieves the King piece of the current player.

        :return: The King piece if found, otherwise None.
        """
        # Iterate over the pieces of the current player
        for piece in self.players[self.turn].pieces:
            # Check if the piece is an instance of King
            if isinstance(piece, King):
                return piece
        return None

    def set_highlight(
        self, squares_list: list[tuple[int, int]], boolean: bool, highlight_type: str
    ) -> bool:
        """
        Sets the highlight of a set of squares to on or off.
        (currently unused, planning to use for highlighting squares based in the Tile class instead of Unit class)

        :param squares_list: List of squares [(row, col), (row, col)...].
        :param boolean: Value to set the highlight of the squares to.
        :param highlight_type: Valid inputs are 'check', 'default', 'unused', 'self'.
        :return: True if the highlight was successfully set, False otherwise.
        """
        # Valid inputs for highlight types
        valid_types: list[str] = ["check", "default", "unused", "self"]

        # Check if the highlight type is valid
        if highlight_type not in valid_types:
            # Raise an error if the highlight type is invalid
            raise ValueError(
                f"Invalid highlight type: {highlight_type}. Valid inputs are: {', '.join(valid_types)}"
            )

        try:
            # Iterate over each square
            for row, col in squares_list:
                # Set the highlight attribute for the square
                setattr(self.board[row][col], f"highlight_{highlight_type}", boolean)
            return True

        # Handle IndexError for squares outside the current board
        except IndexError:
            return False

    def king_does_not_exist(self, player_key: str) -> bool:
        """
        Checks if the King piece does not exist for the specified player.

        :param player_key: The key of the player to check.
        :return: True if the King piece does not exist, False otherwise.
        """
        # Check if any piece of the player is an instance of King
        does_king_exist: bool = any(
            isinstance(piece, King) for piece in self.players[player_key].pieces
        )
        return not does_king_exist

    def player_king_does_not_exist(self) -> bool:
        """
        Checks if the King piece does not exist for the current player.

        :return: True if the King piece does not exist, False otherwise.
        """
        return self.king_does_not_exist(self.turn)

    def enemy_king_does_not_exist(self) -> bool:
        """
        Checks if the King piece does not exist for the enemy player.

        :return: True if the King piece does not exist, False otherwise.
        """
        return self.king_does_not_exist(constant.TURNS[self.turn])

    def update_squares(self):
        """
        Updates the squares for all pieces of all players.
        """
        # Iterate over each player
        for player in self.players:
            # Iterate over each piece of the player
            for piece in self.players[player].pieces:
                # Update the squares for the piece
                piece.update_squares(self)

    def update_previously_selected(self) -> Optional[Unit]:
        """
        Updates and returns the previously selected piece.

        :return: The previously selected piece if found, otherwise None.
        """
        # Initialize the previously selected piece to None
        previously_selected: Optional[Unit] = None
        # Iterate over each player
        for player in self.players:
            # Iterate over each piece of the player
            for piece in self.players[player].pieces:
                # Check if the piece is selected or performing any action
                if piece_is_selected(piece):
                    # Update the previously selected piece
                    previously_selected = piece
        return previously_selected

    def tick_protected_tiles(self, protected_tiles: list[Tile]):
        """
        Ticks the protect timer for each tile in the protected tiles list.

        :param protected_tiles: List of tiles to tick the protect timer for.
        """
        # Iterate over each tile in the protected tiles list
        for tile in protected_tiles:
            # Tick the protect timer for the tile
            tile.tick_protect_timer(self)

    def un_tick_protected_tiles(self, protected_tiles: list[Tile]):
        """
        Un-ticks the protect timer for each tile in the protected tiles list.
        A protect timer ticks once per change turn action. This function will be called when a change turn is un done.

        :param protected_tiles: List of tiles to un-tick the protect timer for.
        """
        # Iterate over each tile in the protected tiles list
        for tile in protected_tiles:
            # Un-tick the protect timer for the tile
            tile.un_tick_protect_timer(self, tile.protected_by)

    def set_actions_remaining(self, actions_remaining: int):
        """
        Sets the actions remaining for all pieces of all players.

        :param actions_remaining: The number of actions to set for each piece.
        """
        # Iterate over each player
        for player in self.players:
            # Iterate over each piece of the player
            for piece in self.players[player].pieces:
                # Set the actions remaining for the piece
                piece.actions_remaining = actions_remaining

    def update_piece_limit(self):
        """
        Updates the piece limit for the current player based on their pieces.
        """
        # Iterate over each piece of the current player
        for piece in self.players[self.turn].pieces:
            # Add the additional piece limit for the piece to the player's piece limit
            self.players[self.turn].add_additional_piece_limit(
                piece.get_additional_piece_limit()
            )

    def reset_selected(self):
        """
        Resets the selected state and various action flags for all pieces of all players.
        """
        # Iterate over each player
        for player in self.players:
            # Iterate over each piece of the player
            for piece in self.players[player].pieces:
                # Reset the selected state and various action flags for the piece
                piece.selected = False
                piece.pre_selected = False
                piece.mining = False
                piece.purchasing = False
                piece.praying = False
                piece.casting = False
                piece.stealing = False
                piece.mining_stealing = False
                piece.persuading = False
                piece.praying_building = False
                piece.display_moves = False
                piece.performing_ritual = False

    def reset_piece_limit(self, color: str):
        """
        Resets the piece limit for the specified player to the default value.

        :param color: The color key of the player.
        """
        # Set the piece limit to the default value
        self.players[color].piece_limit = constant.DEFAULT_PIECE_LIMIT

    def reset_player_actions_remaining(self, color: str):
        """
        Resets the actions remaining for all pieces of the specified player.

        :param color: The color key of the player.
        """
        # Reset the actions remaining for the player
        self.players[color].reset_actions_remaining()

    def reset_piece_actions_remaining(self):
        """
        Resets the actions remaining for all pieces of all players to 1.
        """
        # Iterate over each player
        for player in self.players:
            # Iterate over each piece of the player
            for piece in self.players[player].pieces:
                # Set the actions remaining for the piece to 1
                piece.actions_remaining = 1

    def reset_board(self):
        """
        Resets the game board by reinitializing all tiles.
        """
        event = ResetBoard(self, None, None)
        self.add_event(event, determine_winner=False)

    def has_enemy_occupying(self, color: str, row: int, col: int) -> bool:
        """
        Checks if the specified tile is occupied by an enemy piece.

        :param color: The color of the current player.
        :param row: The row of the tile to check.
        :param col: The column of the tile to check.
        :return: True if the tile is occupied by an enemy piece, False otherwise.
        """
        try:
            # Check if the tile is occupied
            if not self.has_occupying(row, col):
                return False
            # Check if the occupying piece is an enemy
            if self.get_occupying(row, col).color != color:
                return True
            return False
        except IndexError:
            return False

    def can_contain_quarry(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile can contain a quarry.

        :param row: The row of the tile to check.
        :param col: The column of the tile to check.
        :return: True if the tile can contain a quarry, False otherwise.
        """
        try:
            # Check if the tile can contain a quarry and is not a depleted quarry
            return self.board[row][col].can_contain_quarry and not self.has_resource(
                row, col, DepletedQuarry
            )
        except IndexError:
            return False

    def reset_unused_piece_highlight(self):
        """
        Resets the unused piece highlight for all pieces of all players.
        """
        # Iterate over each player
        for player in self.players:
            # Iterate over each piece of the player
            for piece in self.players[player].pieces:
                # Reset the unused piece highlight for the piece
                piece.unused_piece_highlight = False

    def un_trap(self, row: int, col: int):
        """
        Removes a trap from the specified tile and updates the player's pieces.

        :param row: The row of the tile.
        :param col: The column of the tile.
        """
        # Get the color of the trap
        color: str = self.board[row][col].trap.get_color()
        # Remove the trap from the player's pieces
        self.players[color].pieces.remove(self.board[row][col].trap)
        # Undo the trap on the tile
        self.board[row][col].undo_trap()

    def set_trap(self, row: int, col: int, trap: Trap):
        """
        Sets a trap on the specified tile and updates the player's pieces.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param trap: The trap to set on the tile.
        """
        # Set the trap on the tile
        self.board[row][col].set_trap(trap)
        # Add the trap to the player's pieces
        self.players[trap.get_color()].pieces.append(trap)

    def spawn(self, destination_row: int, destination_col: int, spawned: str) -> Union[Unit, bool]:
        """
        Spawns a piece at the specified destination.

        :param destination_row: The row of the destination tile.
        :param destination_col: The column of the destination tile.
        :param spawned: The type of piece to spawn.
        """
        # Do not spawn if a square is occupied
        if self.get_occupying(destination_row, destination_col):
            print(f"Did not spawn at {destination_row} {destination_col} because it is occupied.")
            return False

        # Create the spawned piece object at the destination
        spawned_piece: Unit = self.PIECES[spawned](
            destination_row, destination_col, self.turn
        )
        # Store the piece on the board at the destination address
        self.create_piece(destination_row, destination_col, spawned_piece)

        return spawned_piece

    def capture(
        self,
        moving_row: int,
        moving_col: int,
        destination_row: int,
        destination_col: int,
    ):
        """
        Captures a piece at the destination and moves the capturing piece.

        :param moving_row: The row of the moving piece.
        :param moving_col: The column of the moving piece.
        :param destination_row: The row of the destination tile.
        :param destination_col: The column of the destination tile.
        """
        # Remove the captured piece from the enemy player's pieces
        self.players[constant.TURNS[self.turn]].pieces.remove(
            self.board[destination_row][destination_col].get_occupying()
        )
        # Empty the captured square
        self.board[destination_row][destination_col].set_occupying(None)
        # Move the piece to the newly emptied square
        self.move(moving_row, moving_col, destination_row, destination_col)

    def swap(
        self,
        moving_row: int,
        moving_col: int,
        destination_row: int,
        destination_col: int,
    ):
        """
        Swaps the positions of two pieces on the board.

        :param moving_row: The row of the first piece to swap.
        :param moving_col: The column of the first piece to swap.
        :param destination_row: The row of the second piece to swap.
        :param destination_col: The column of the second piece to swap.
        """
        # Get the first piece to swap
        first_piece_to_swap: Optional[Piece] = self.get_occupying(
            moving_row, moving_col
        )
        # Get the second piece to swap
        second_piece_to_swap: Optional[Piece] = self.get_occupying(
            destination_row, destination_col
        )

        # Swap the positions of the pieces on the board
        self.board[moving_row][moving_col].set_occupying(second_piece_to_swap)
        self.board[destination_row][destination_col].set_occupying(first_piece_to_swap)

        # Update the positions of the pieces if they exist
        if first_piece_to_swap:
            first_piece_to_swap.change_pos(destination_row, destination_col)
        if second_piece_to_swap:
            second_piece_to_swap.change_pos(moving_row, moving_col)

    def move(
        self,
        moving_row: int,
        moving_col: int,
        destination_row: int,
        destination_col: int,
    ):
        """
        Moves a piece from one position to another on the board.

        :param moving_row: The row of the piece to move.
        :param moving_col: The column of the piece to move.
        :param destination_row: The row of the destination tile.
        :param destination_col: The column of the destination tile.
        """
        # Get the piece to move
        piece: Unit = self.board[moving_row][moving_col].get_occupying()
        # Set the piece at the destination position
        self.board[destination_row][destination_col].set_occupying(piece)
        # Update the position of the piece
        piece.change_pos(destination_row, destination_col)
        # Clear the original position
        self.board[moving_row][moving_col].set_occupying(None)

    def has_portal(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile has a portal.

        :param row: The row of the tile to check.
        :param col: The column of the tile to check.
        :return: True if the tile has a portal, False otherwise.
        """
        try:
            # Return whether the tile has a portal
            return self.board[row][col].portal
        except IndexError:
            return False

    def get_all_pray_able(self) -> list[Unit]:
        """
        Retrieves all monoliths and prayer stones from the players' units.

        :return: A list of monoliths and prayer stones.
        """
        monoliths: list[Unit] = []
        for player in self.players:
            for piece in self.players[player].pieces:
                if isinstance(piece, Monolith) or isinstance(piece, PrayerStone):
                    monoliths.append(piece)
        return monoliths

    def enable_monoliths(self) -> list[Unit]:
        """
        Enables monoliths and prayer stones by increasing their actions remaining.

        :return: A list of enabled monoliths and prayer stones.
        """
        monoliths = self.get_all_pray_able()
        for monolith in monoliths:
            monolith.actions_remaining += 1
        return monoliths

    def disable_monoliths(self) -> list[Unit]:
        """
        Disables monoliths and prayer stones by setting their actions remaining to zero and removing their highlight.

        :return: A list of disabled monoliths and prayer stones.
        """
        monoliths = self.get_all_pray_able()
        for monolith in monoliths:
            monolith.actions_remaining = 0
            monolith.unused_piece_highlight = False
        return monoliths

    def has_resource(
        self, row: int, col: int, resource_type: Optional[type] = None
    ) -> bool:
        """
        Checks if a square contains a resource. If resource_types are provided,
        checks if a resource of the given type(s) is present.

        :param row: The row of the square.
        :param col: The column of the square.
        :param resource_type: Optional resource type(s) to check for.
        :return: True if the square has any resource (if no types are provided) or a resource of the given type(s).
        """
        try:
            # Get the resource on the tile
            resource: Optional[Resource] = self.board[row][col].get_resource()
        except IndexError:
            # Row, col is out of bounds
            return False

        # Check if the tile is unoccupied
        if resource is None:
            return False

        # If no specific resource types are provided, return True if the tile has any resource
        if not resource_type:
            return True

        # Check if the resource is of the specified type(s)
        return isinstance(resource, resource_type)

    def has_occupying(self, row: int, col: int, unit_type: type = None) -> bool:
        """
        Checks if a square is occupied. If unit_types are provided, checks if a unit of the given type(s) is
        occupying the square.

        :param row: The row of the square.
        :param col: The column of the square.
        :param unit_type: Optional unit type(s) to check for.
        :return: True if the square is occupied by any unit (if no types are provided)
            or by a unit of the given type(s).
        """
        try:
            # Get the occupying unit on the tile
            occupant: Optional[Unit] = self.board[row][col].occupying
        except IndexError:
            # Row, col is out of bounds
            return False

        # Check if the tile is unoccupied
        if occupant is None:
            return False

        # If no specific unit types are provided, return True if the tile is occupied
        if not unit_type:
            return True

        # Check if the occupying unit is of the specified type(s)
        return isinstance(occupant, unit_type)

    def has_disqualifying_resource(
        self, row: int, col: int, disqualifying_resources: set[type]
    ) -> bool:
        """
        Checks if the tile has any resource that prevents occupation.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param disqualifying_resources: A set of resource types that disqualify the tile.
        :return: True if the tile has any disqualifying resource, False otherwise.
        """
        # Check if the tile has any disqualifying resource
        return any(
            self.has_resource(row, col, resource)
            for resource in disqualifying_resources
        )

    def is_occupyable_with_units(
        self, row: int, col: int, extra_resources: set[type]
    ) -> bool:
        """
        Checks if the tile can be occupied based on its contents, allowing occupation even if a unit is present.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param extra_resources: A set of additional resource types that allow occupation.
        :return: True if the tile can be occupied, False otherwise.
        """
        return (
            self.has_no_units_or_resources(row, col)
            or self.has_resource(row, col, Quarry)
            or self.has_resource(row, col, DepletedQuarry)
            or self.has_occupying(
                row, col
            )  # Allows occupation even if a unit is present
            or any(
                self.has_resource(row, col, resource) for resource in extra_resources
            )
        )

    def is_occupyable_without_units(
        self, row: int, col: int, allow_resources: set[type]
    ) -> bool:
        """
        Checks if the tile can be occupied based on its contents, but only if there is no occupying unit.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param allow_resources: A set of additional resource types that allow occupation.
        :return: True if the tile can be occupied without an occupying unit, False otherwise.
        """
        return (
            self.has_no_units_or_resources(row, col)
            or (
                not self.has_occupying(row, col) and self.has_resource(row, col, Quarry)
            )
            or (
                not self.has_occupying(row, col)
                and self.has_resource(row, col, DepletedQuarry)
            )
            or any(
                not self.has_occupying(row, col)
                and self.has_resource(row, col, resource)
                for resource in allow_resources
            )
        )

    def can_be_legally_occupied(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile can be legally occupied.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the tile can be legally occupied, False otherwise.
        """
        try:
            # Check if the tile has any disqualifying resource
            if self.has_disqualifying_resource(row, col, {Gold, Wood, SunkenQuarry}):
                return False
            # Check if the tile can be occupied
            return self.is_occupyable_with_units(row, col, set())
        except IndexError:
            return False

    def can_be_legally_occupied_by_rogue(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile can be legally occupied by a rogue.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the tile can be legally occupied by a rogue, False otherwise.
        """
        try:
            # Check if the tile has any disqualifying resource for a rogue
            if self.has_disqualifying_resource(row, col, {Gold, SunkenQuarry}):
                return False
            # Check if the tile can be occupied
            return self.is_occupyable_with_units(row, col, set())
        except IndexError:
            return False

    def can_be_legally_occupied_by_gold_general(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile can be legally occupied by a gold general.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the tile can be legally occupied by a gold general, False otherwise.
        """
        try:
            # Check if the tile can be occupied by a gold general
            return self.is_occupyable_with_units(row, col, {Gold, SunkenQuarry, Wood})
        except IndexError:
            return False

    def can_be_occupied_by_gold_general(self, row: int, col: int) -> bool:
        """Checks if the specified tile can be occupied by a gold general."""
        try:
            return self.is_occupyable_without_units(
                row, col, {Gold, Wood, SunkenQuarry}
            )
        except IndexError:
            return False

    def can_be_occupied(self, row: int, col: int) -> bool:
        """Checks if the specified tile can be occupied."""
        try:
            if self.has_resource(row, col, Wood) or self.has_resource(row, col, Gold):
                return False
            return self.is_occupyable_without_units(row, col, set())
        except IndexError:
            return False

    def can_be_occupied_by_rogue(self, row: int, col: int) -> bool:
        """Checks if the specified tile can be occupied by a rogue."""
        try:
            return self.is_occupyable_without_units(row, col, {Wood})
        except IndexError:
            return False

    def create_resource(self, row: int, col: int, resource: Resource) -> bool:
        """
        Creates a resource on the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param resource: The resource to create.
        :return: True if the resource was successfully created, False otherwise.
        """
        try:
            # Set the resource on the tile
            self.board[row][col].set_resource(resource)
            return True
        except IndexError:
            return False

    def delete_piece(self, row: int, col: int):
        """
        Deletes the piece on the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        """
        # Get the piece on the tile
        piece: Unit = self.board[row][col].get_occupying()
        # Get the list of pieces for the piece's color
        pieces: list[Unit] = self.players[piece.get_color()].pieces
        # Remove the piece from the list
        del pieces[pieces.index(piece)]
        # Set the occupying unit on the tile to None
        self.board[row][col].set_occupying(None)

    def create_piece(self, row: int, col: int, piece: Unit):
        """
        Creates a piece on the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param piece: The piece to create.
        """
        # Set the occupying unit on the tile
        self.board[row][col].set_occupying(piece)
        # Add the piece to the list of pieces for the piece's color
        self.players[piece.get_color()].pieces.append(piece)

    def delete_resource(self, row: int, col: int):
        """
        Deletes the resource on the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        """
        # Set the resource on the tile to None
        self.board[row][col].set_resource(None)

    def count_unused_pieces(self) -> list[Unit]:
        """
        Counts the unused pieces of the current player.

        :return: A list of unused pieces.
        """
        # Initialize the list of unused pieces
        unused_pieces: list[Unit] = []
        # Iterate over the pieces of the current player
        for piece in self.players[self.turn].pieces:
            # Check if the piece has one action remaining
            if piece.actions_remaining == 1:
                unused_pieces.append(piece)
        return unused_pieces

    def count_used_pieces(self) -> list[Unit]:
        """
        Counts the used pieces of the current player.

        :return: A list of used pieces.
        """
        # Initialize the list of used pieces
        used_pieces: list[Unit] = []
        # Iterate over the pieces of the current player
        for piece in self.players[self.turn].pieces:
            # Check if the piece has no actions remaining
            if piece.actions_remaining == 0:
                used_pieces.append(piece)
        return used_pieces

    def count_pieces(self, piece_type: type, color: str) -> int:
        """
        Counts the number of pieces of a specific type for a given player.

        :param piece_type: The type of piece to count.
        :param color: The color of the player.
        :return: The number of pieces of the specified type.
        """
        # Initialize the count of pieces
        count: int = 0
        # Iterate over the pieces of the specified player
        for piece in self.players[color].pieces:
            # Check if the piece is of the specified type
            if isinstance(piece, piece_type):
                count += 1
        return count

    def close_menus(self):
        """
        Closes all open menus.
        """
        # Check if there are any open menus
        if self.menus:
            # Close each menu
            for menu in self.menus:
                menu.close()
        # Clear the list of menus
        self.menus = []

    def set_winner(self):
        """
        Sets the current player as the winner.
        """
        # Determine if the game is over (king is captured)
        winner = None
        if self.player_king_does_not_exist():
            self.turn = constant.TURNS[self.turn]
            winner = self.turn

        elif self.enemy_king_does_not_exist():
            winner = self.turn

        self.winner = winner

    def undo_last_event(self) -> bool:
        """
        Undoes the last event and updates the game state.

        :return: True if the event was successfully undone, False otherwise.
        """
        # Close all open menus
        self.close_menus()
        # Get the last event
        event: GameEvent = self.events[-1]
        # Undo the last event
        event.undo()
        # Update the check status for the players
        event.set_player_in_check()
        event.set_enemy_in_check()
        # Remove the last event from the list
        del self.events[-1]
        return True

    def add_network_event(self, event: GameEvent):
        """
        Adds a new event to the game and updates the game state.
        This function is used for networked games to synchronize events across clients.

        :param event: The event to add.
        """
        event.engine = self
        # Complete the event.
        event.complete()
        # Append it to our list of game events.
        self.events.append(event)
        # Synchronize our game state with the event
        event.synchronize(self)

    def add_event(
        self,
        event: GameEvent,
        constrain_check: bool = True,
        determine_winner: bool = True,
    ):
        """
        Adds a new event to the game and updates the game state.

        :param event: The event to add.
        :param constrain_check: When this is true the event will be un done if the player is determined to be in
        check after the event is completed.
        :param determine_winner: Allow the game to end if a king is not discovered. Some events will take place before
        a king is spawned, so it is useful to be able to bypass this check.
        """
        # Complete the event
        event.complete()
        # Add the event to the list of events
        self.events.append(event)

        # # If we are online, synchronize elements of the event which require it:
        # if self.online:
        #     event.synchronize() # Do we do this from add_network_event()

        # Check if the event is not a change turn event
        if constrain_check:
            # Update the check status for the players
            event.constrain_check()
            event.set_enemy_in_check()

        if event in self.events:
            if self.online:
                event.engine = None
                self.client.send_object(event)

        if determine_winner:
            self.set_winner()

    def get_turn(self) -> str:
        """
        Returns the current player's turn.

        :return: The current player's turn.
        """
        return self.turn

    def change_turn(self):
        """
        Changes the turn to the next player.
        """
        # Create a change turn event
        event: ChangeTurn = ChangeTurn(self)
        # Add the event to the game
        self.add_event(event, constrain_check=False, determine_winner=False)
        # Begin the turn for the next player
        self.players[self.turn].begin_turn(self)

    def get_occupying_color(self, row: int, col: int) -> Optional[str]:
        """
        Returns the color of the piece occupying the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: The color of the occupying piece, or None if the tile is empty or out of bounds.
        """
        try:
            # Return the color of the occupying piece
            return self.board[row][col].occupying.get_color()
        except (IndexError, AttributeError):
            return None

    def set_purchasing(self, row: int, col: int, boolean: bool):
        """
        Sets the purchasing status of the unit occupying the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param boolean: The purchasing status to set.
        """
        # Set the purchasing status of the occupying unit
        self.board[row][col].occupying.purchasing = boolean

    def set_stealing(self, row: int, col: int, boolean: bool):
        """
        Sets the stealing status of the unit occupying the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param boolean: The stealing status to set.
        """
        # Set the stealing status of the occupying unit
        self.board[row][col].occupying.stealing = boolean

    def set_pre_selected(self, row: int, col: int, boolean: bool):
        """
        Sets the pre-selected status of the unit occupying the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param boolean: The pre-selected status to set.
        """
        # Set the pre-selected status of the occupying unit
        self.board[row][col].occupying.pre_selected = boolean

    def find_player_castle(self) -> Optional[tuple[int, int]]:
        """
        Finds the position of the current player's castle.

        :return: The position of the castle as a tuple (row, col), or None if not found.
        """
        # Iterate over the pieces of the current player
        for piece in self.players[self.turn].pieces:
            # Check if the piece is a Castle
            if isinstance(piece, Castle):
                # Return the position of the castle
                return piece.get_position()
        return None

    def player_can_do_action(self, color: str) -> bool:
        """
        Checks if the specified player can perform an action.

        :param color: The color of the player.
        :return: True if the player can perform an action, False otherwise.
        """
        # Check if the player can act
        return self.players[color].can_act()

    def update_additional_actions(self):
        """
        Updates the total additional actions for the current player.
        """
        # Initialize the tally of additional actions
        tally_additional_actions: int = 0
        # Iterate over the pieces of the current player
        for piece in self.players[self.turn].pieces:
            # Add the additional actions of the piece to the player's total
            self.players[self.turn].add_additional_actions(
                piece.get_additional_actions()
            )
            # Increment the tally of additional actions
            tally_additional_actions += piece.get_additional_actions()
        # Set the total additional actions for the current player
        self.players[self.turn].total_additional_actions_this_turn = (
            tally_additional_actions
        )

    def determine_winner(self):
        """
        Determines the winner of the game and sets the game state to 'winner' if a winner is found.
        """
        if self.winner is not None:
            self.set_state("winner")

    def update(self):
        """
        Updates the game state by determining the winner.
        """
        self.determine_winner()

    def is_legal_ritual(self, ritual: str, cost_type: Optional[str]) -> bool:
        """
        Checks if a ritual can be performed based on the cost and cost type.

        :param ritual: The name of the ritual.
        :param cost_type: The type of cost (e.g., 'prayer', 'gold').
        :return: True if the ritual can be performed, False otherwise.
        """
        if not cost_type:
            ritual_cost = None
        else:
            ritual_cost = constant.PRAYER_COSTS[ritual][cost_type]
        return self.valid_ritual(ritual_cost, cost_type)

    def player_has_gold_general(self, color: str) -> bool:
        """
        Checks if the specified player has a Gold General piece.

        :param color: The color of the player.
        :return: True if the player has a Gold General piece, False otherwise.
        """
        for piece in self.players[color].pieces:
            if isinstance(piece, GoldGeneral):
                return True
        return False

    def is_legal_spawn(self, spawning: str, spawner: Unit) -> bool:
        """
        Checks if a piece can be legally spawned by the spawner.

        :param spawning: The type of piece to spawn.
        :param spawner: The unit that is spawning the piece.
        :return: True if the piece can be legally spawned, False otherwise.
        """
        piece_cost = self.PIECE_COSTS[spawning]

        # Check if the spawner can act
        if not spawner.can_act():
            return False

        # Check if the piece can be purchased
        if not self.valid_purchase(piece_cost):
            return False

        # Check if the player can add the piece
        if not self.players[self.turn].can_add_piece(spawning):
            return False

        # Special check for 'trapper' piece
        if str(spawner) == "trapper":
            return True

        # Check if the player can act
        if not self.players[self.turn].can_act():
            return False

        # Check if the player has a Gold General for monk spawn
        if self.player_has_gold_general(self.turn) and spawning == "monk":
            return True

        return True

    def has_mine_able_resource(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile has a mine-able resource.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the tile has a mine-able resource, False otherwise.
        """
        try:
            resource = self.board[row][col].get_resource()
        except IndexError:
            return False
        if (
            isinstance(resource, Wood)
            or isinstance(resource, Quarry)
            or isinstance(resource, Gold)
            or isinstance(resource, SunkenQuarry)
        ):
            return True
        return False

    def has_trap(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile has a trap.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the tile has a trap, False otherwise.
        """
        try:
            # Return whether the tile has a trap
            return self.board[row][col].has_trap()
        except IndexError:
            return False

    def has_pray_able_building(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile has a pray-able building.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the tile has a pray-able building, False otherwise.
        """
        try:
            # Get the occupying unit on the tile
            building = self.board[row][col].get_occupying()
        except IndexError:
            return False

        # Protection works on pray-able buildings
        if self.board[row][col].is_protected_by_opposite_color(self.turn):
            return False

        # Check if rituals are not banned and the building is a PrayerStone or Monolith
        if not self.rituals_banned and (
            isinstance(building, PrayerStone) or isinstance(building, Monolith)
        ):
            return True
        return False

    def get_intercepted_pieces(self) -> list[Unit]:
        """
        Retrieves a list of intercepted pieces affected by a jester.

        :return: A list of intercepted pieces.
        """
        # Initialize the list of intercepted pieces
        intercepted_pieces: list[Unit] = []
        # Iterate over each player
        for player in self.players:
            # Iterate over each piece of the player
            for piece in self.players[player].pieces:
                # Check if the piece is intercepted and affected by a jester
                if piece.intercepted and piece.is_effected_by_jester:
                    intercepted_pieces.append(piece)
        return intercepted_pieces

    def find_interceptors(self) -> list[Unit]:
        """
        Finds all jester pieces that can intercept other pieces.

        :return: A list of jester pieces.
        """
        # Update the squares for all pieces
        self.update_squares()
        # Initialize the list of interceptors
        interceptors: list[Unit] = []
        # Iterate over each player
        for player in self.players:
            # Iterate over each piece of the player
            for piece in self.players[player].pieces:
                # Check if the piece is a jester
                if isinstance(piece, Jester):
                    interceptors.append(piece)
        return interceptors

    def intercept_pieces(self):
        """
        Intercepts pieces affected by jesters.
        """
        # Find all interceptors
        interceptors = self.find_interceptors()
        # Iterate over each interceptor
        for interceptor in interceptors:
            # Iterate over each square in the interceptor's range
            for square in interceptor.interceptor_squares_list:
                # Get the occupying piece on the square
                piece = self.board[square[0]][square[1]].get_occupying()
                # Check if the piece is affected by a jester and cannot act
                if piece and piece.is_effected_by_jester:
                    if not piece.can_act():
                        self.used_and_intercepted_pieces.append(piece)
                    piece.intercepted = True
                    piece.actions_remaining = 0

    def reset_intercepted(self):
        """
        Resets the intercepted status for all pieces.
        """
        # Iterate over each player
        for player in self.players:
            # Iterate over each piece of the player
            for piece in self.players[player].pieces:
                # Reset the intercepted status
                if piece.intercepted:
                    piece.intercepted = False

    def correct_interceptions(self):
        """
        Corrects the interceptions by resetting and re-intercepting pieces.
        """
        # Get the original list of intercepted pieces
        intercepted_pieces_original = self.get_intercepted_pieces()
        # Reset the intercepted status for all pieces
        self.reset_intercepted()
        # Re-intercept pieces
        self.intercept_pieces()
        # Get the new list of intercepted pieces
        intercepted_pieces_new = self.get_intercepted_pieces()
        # Iterate over the original intercepted pieces
        for piece in intercepted_pieces_original:
            # Check if the piece is no longer intercepted
            if piece not in intercepted_pieces_new:
                if piece not in self.used_and_intercepted_pieces:
                    piece.intercepted = False
                    # Highlight the piece if it belongs to the current player
                    if piece.get_color() == self.turn:
                        piece.unused_piece_highlight = True
                    piece.actions_remaining = 1
        # Clear the list of used and intercepted pieces
        self.used_and_intercepted_pieces = []

    def get_occupying(self, row: int, col: int) -> Optional[Unit]:
        """
        Returns the occupying unit of the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: The occupying unit, or None if the tile is out of bounds.
        """
        try:
            # Get the occupying unit of the tile
            unit: Optional[Unit] = self.board[row][col].get_occupying()
        except IndexError:
            # Return None if the tile is out of bounds
            unit = None
        return unit

    def transfer_to_stealing_state(self, row: int, col: int) -> bool:
        """
        Transfers the game state to the stealing state if the conditions are met.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Update the squares on the board
        self.update_squares()
        # Get the list of stealing squares for the occupying unit
        stealing_squares: list[tuple[int, int]] = (
            self.board[row][col].get_occupying().stealing_squares_list
        )
        # Initialize the allow_steal flag
        allow_steal: bool = False
        # Check if there are stealing squares
        if stealing_squares:
            allow_steal = True
        # If stealing is allowed, transfer to the stealing state
        if allow_steal:
            self.set_stealing(row, col, True)
            new_state: Stealing = Stealing(self.state[-1].win, self)
            self.menus = []
            self.set_state(new_state)
            return True
        return False

    def transfer_to_building_state(self, row: int, col: int) -> bool:
        """
        Transfers the game state to the building state.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Update the squares on the board
        self.update_squares()
        # Set the pre-selected state for the tile
        self.set_pre_selected(row, col, True)
        # Create a new PreBuilding state
        new_state: PreBuilding = PreBuilding(self.state[-1].win, self)
        self.menus = []
        self.set_state(new_state)
        # Add the menu to the queue and set the spawning piece
        new_state.add_menu_to_menu_queue(str(self.get_occupying(row, col)))
        new_state.spawning_piece = self.get_occupying(row, col)
        return True

    def transfer_to_piece_cost_screen(self) -> bool:
        """
        Transfers the game state to the piece cost screen.

        :return: True if the state was successfully transferred, False otherwise.
        """
        # Get the current state
        current_state: State = self.state[-1]
        # Create a new PieceCost state
        new_state: PieceCost = PieceCost(self.state[-1].win, self, current_state)
        self.set_state(new_state)
        return True

    def transfer_to_praying_state(self, row: int, col: int) -> bool:
        """
        Transfers the game state to the praying state if the conditions are met.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Update the squares on the board
        self.update_squares()
        # Get the list of praying squares for the occupying unit
        praying_squares: list[tuple[int, int]] = (
            self.board[row][col].get_occupying().praying_squares_list
        )
        # Initialize the allow_pray flag
        allow_pray: bool = False
        # Check if there are praying squares
        for square in praying_squares:
            if self.has_pray_able_building(square[0], square[1]):
                allow_pray = True
        # If praying is allowed, transfer to the praying state
        if allow_pray:
            self.board[row][col].get_occupying().praying = True
            new_state: Praying = Praying(self.state[-1].win, self)
            self.set_state(new_state)
            self.menus = []
            return True
        return False

    def transfer_to_persuading_state(self, row: int, col: int) -> bool:
        """
        Transfers the game state to the persuading state if the conditions are met.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Update the squares on the board
        self.update_squares()
        # Get the list of persuader squares for the occupying unit
        persuader_squares: list[tuple[int, int]] = (
            self.board[row][col].get_occupying().persuader_squares_list
        )
        # If there are persuader squares, transfer to the persuading state
        if persuader_squares:
            self.board[row][col].get_occupying().persuading = True
            new_state: Persuading = Persuading(self.state[-1].win, self)
            self.set_state(new_state)
            self.menus = []
            return True
        return False

    def transfer_to_mining_state(self, row: int, col: int) -> bool:
        """
        Transfers the game state to the mining state if the conditions are met.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Update the squares on the board
        self.update_squares()
        # Get the list of mining squares for the occupying unit
        mining_squares: list[tuple[int, int]] = (
            self.board[row][col].get_occupying().mining_squares_list
        )
        # Initialize the allow_mine flag
        allow_mine: bool = False
        # Check if there are mine-able resources or no units/resources on the squares
        for m in mining_squares:
            if self.has_mine_able_resource(
                m[0], m[1]
            ) or self.has_no_units_or_resources(m[0], m[1]):
                allow_mine = True
        # If mining is allowed, transfer to the mining state
        if allow_mine:
            self.board[row][col].get_occupying().mining = True
            new_state: Mining = Mining(self.state[-1].win, self)
            self.set_state(new_state)
            self.menus = []
            return True
        return False

    def transfer_to_surrender_state(self, row: int, col: int) -> bool:
        """
        Transfers the game state to the surrender state.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Create a new Surrender state
        new_state: Surrender = Surrender(self.state[-1].win, self)
        # Set the new state
        self.set_state(new_state)
        # Clear the menus
        self.menus = []
        return True

    def transfer_to_spawning_state(self, spawning: str) -> bool:
        """
        Transfers the game state to the spawning state.

        :param spawning: The type of piece to spawn.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Create a new Spawning state
        new_state: Spawning = Spawning(self.state[-1].win, self)
        # Set the spawning piece
        self.spawning = spawning
        # Set the new state
        self.set_state(new_state)
        return True

    def transfer_to_ritual_state(self, ritual: str, cost_type: str) -> bool:
        """
        Transfers the game state to the ritual state.

        :param ritual: The type of ritual to perform.
        :param cost_type: The type of cost for the ritual.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Create a new ritual state
        new_state: State = self.STATES[ritual](self.state[-1].win, self)
        # Set the cost type for the ritual
        new_state.cost_type = cost_type
        # Clear the menus
        self.menus = []
        # Set the new state
        self.set_state(new_state)
        return True

    def transfer_to_starting_spawn(self, spawn_list: list[str]) -> bool:
        """
        Transfers the game state to the starting spawn state.

        :param spawn_list: The list of pieces to spawn at the start.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Create a new StartingSpawn state
        state: StartingSpawn = StartingSpawn(self.state[-1].win, self)
        # Set the spawn list
        self.spawn_list = spawn_list
        # Set the first piece to spawn
        self.spawning = self.spawn_list[0]
        # Set the new state
        self.set_state(state)
        return True

    def transfer_to_piece_selection(self) -> bool:
        """
        Transfers the game state to the piece selection state.

        :return: True if the state was successfully transferred, False otherwise.
        """
        # Create a new SelectStartingPieces state
        state: SelectStartingPieces = SelectStartingPieces(self.state[-1].win, self)
        # Set the new state
        self.set_state(state)
        return True

    def transfer_to_pre_ritual_state(self, row: int, col: int) -> bool:
        """
        Transfers the game state to the pre-ritual state.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Define the ritual key mapping
        ritual_key: dict[str, tuple[Optional[str], list[str]]] = {
            "magician": ("gold", self.magician_rituals[self.turn_count_actual]),
            "prayer_stone": (
                "prayer",
                self.prayer_stone_rituals[self.turn_count_actual],
            ),
            "monolith": ("prayer", self.monolith_rituals[self.turn_count_actual]),
            "assassin": (None, constant.ASSASSIN_RITUALS),
        }
        # Get the cost type and ritual list for the occupying unit
        cost_type, ritual_list = ritual_key[str(self.get_occupying(row, col))]
        # Create the ritual menu
        return self.create_ritual_menu(row, col, ritual_list, cost_type)

    def create_ritual_menu(
        self, row: int, col: int, ritual_list: list[str], cost_type: str = "prayer"
    ) -> bool:
        """
        Creates a ritual menu for the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param ritual_list: The list of rituals to display in the menu.
        :param cost_type: The type of cost for the rituals.
        :return: True if the ritual menu was successfully created, False otherwise.
        """
        # Set the casting flag for the occupying unit
        self.get_occupying(row, col).casting = True
        # Create a new RitualMenu
        ritual_menu: RitualMenu = RitualMenu(
            row, col, self.state[-1].win, self, ritual_list, cost_type
        )
        # Add the ritual menu to the menus list
        self.menus.append(ritual_menu)
        return True

    def can_decree(self, row: int, col: int) -> bool:
        """
        Checks if the current player has enough gold to perform the decree action.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the player has enough resources, False otherwise.
        """
        # Get the cost of the decree action
        decree_cost: dict[str, int] = constant.DECREE_COST
        # Get the keys of the decree cost dictionary
        keys: list[str] = list(decree_cost.keys())
        # Get the current resource of the player
        current_resource: int = getattr(self.players[self.turn], keys[-1])
        # Check if the player has enough resources
        return current_resource >= self.get_decree_cost()

    def decree(self, row: int, col: int) -> None:
        """
        Performs the decree action on the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        """
        # Get the acting tile
        acting_tile: Tile = self.board[row][col]
        # Create a new Decree event
        event: Decree = Decree(self, acting_tile, None)
        # Add the event to the event list
        self.add_event(event)

    def get_current_state(self) -> Optional[State]:
        """
        Returns the current state of the game.

        :return: The current state.
        """
        if not self.state:
            return None
        return self.state[-1]

    def can_trade(self) -> bool:
        """
        Checks if the current player can trade.

        :return: True if the player can trade, False otherwise.
        """
        return self.players[self.turn].can_trade()

    def trade(self) -> None:
        """
        Performs the trade action.

        """
        # Get the acting tile
        acting_tile: Tile = self.board[self.piece_trading.row][self.piece_trading.col]
        # Create a new Trade event
        event: Trade = Trade(self, acting_tile, None)
        # Add the event to the event list
        self.add_event(event)
        # Revert to the playing state
        self.state[-1].revert_to_playing_state()

    def transfer_to_trading_state(self, row: int, col: int) -> bool:
        """
        Transfers the game state to the trading state.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the state was successfully transferred, False otherwise.
        """
        # Create a new Trading state
        new_state: Trading = Trading(self.state[-1].win, self)
        # Set the new state
        self.set_state(new_state)
        # Create the trader menu
        return self.create_trader_menu(row, col)

    def create_trader_menu(
        self, row: int, col: int, set_new_piece_trading: bool = True
    ) -> bool:
        """
        Creates a trader menu for the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param set_new_piece_trading: Flag to set a new piece for trading.
        :return: True if the trader menu was successfully created, False otherwise.
        """
        # Get the current player
        player: Player = self.players[self.turn]
        # Define the resources and their corresponding keys
        resources: list[str] = ["wood", "gold", "stone"]
        key: dict[str, str] = {"wood": "log", "gold": "gold_coin", "stone": "stone"}
        # Initialize the resource list
        resource_list: list[str] = []
        # Populate the resource list with available resources
        for resource in resources:
            if getattr(player, resource) != 0:
                resource_list.append(key[resource])
        # Check if there are resources to trade
        if resource_list:
            if set_new_piece_trading:
                self.piece_trading = self.get_occupying(row, col)
            # Create a new GiveMenu
            trader_menu: GiveMenu = GiveMenu(
                row, col, self.state[-1].win, self, resource_list
            )
            # Add the trader menu to the menus list
            self.menus.append(trader_menu)
            return True
        return False

    def create_contextual_menu(
        self, row: int, col: int, win: pygame.Surface, menu_list: list[str]
    ) -> bool:
        """
        Creates a contextual menu for the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :param win: The game window surface.
        :param menu_list: The list of menu options.
        :return: True if the contextual menu was successfully created, False otherwise.
        """
        # Create a new Contextual menu
        menu: Contextual = Contextual(row, col, win, self, menu_list)
        # Add the contextual menu to the menus list
        self.menus.append(menu)
        return True

    def starting_square_has_enough_open_spaces(self, row: int, col: int) -> bool:
        """
        Checks if the starting square has enough open spaces.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the starting square has enough open spaces, False otherwise.
        """
        # Initialize the open spaces and rogue spaces counters
        open_spaces: int = 0
        rogue_spaces: int = 0
        rogues: int = 0
        # Count the number of rogues in the spawn list
        for piece in self.spawn_list:
            if piece == "rogue_pawn" or piece == "trapper":
                rogues += 1
        # Calculate the number of open spaces needed
        open_spaces_needed: int = 7 - rogues
        # Check the surrounding tiles for open spaces
        for row_offset in range(row - 1, row + 2):
            for col_offset in range(col - 1, col + 2):
                if self.can_be_occupied(row_offset, col_offset):
                    open_spaces += 1
                elif self.can_be_occupied_by_rogue(row_offset, col_offset):
                    rogue_spaces += 1
        return open_spaces >= open_spaces_needed

    def is_legal_starting_square(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile is a legal starting square.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the tile is a legal starting square, False otherwise.
        """
        # Initialize the flags
        no_players_nearby: bool = True
        square_has_enough_spaces: bool = True

        # Check if the square can be occupied and does not have a quarry
        if not self.can_be_occupied(row, col) or self.has_resource(row, col, Quarry):
            return False

        # Check if the square has enough open spaces
        if not self.starting_square_has_enough_open_spaces(row, col):
            square_has_enough_spaces = False

        # Ensure we only check valid board positions
        for row_offset in range(max(0, row - 3), min(len(self.board), row + 4)):
            for col_offset in range(max(0, col - 3), min(len(self.board[0]), col + 4)):
                if self.has_occupying(row_offset, col_offset, Castle):
                    no_players_nearby = False

        return no_players_nearby and square_has_enough_spaces

    def has_no_units_or_resources(self, row: int, col: int) -> bool:
        """
        Checks if the specified tile has no units or resources.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: True if the tile has no units or resources, False otherwise.
        """
        try:
            # Check if the tile has no resource and no occupying unit
            if not self.has_resource(row, col) and not self.has_occupying(row, col):
                return True
        except IndexError:
            return False
        return False

    def get_resource(self, row: int, col: int) -> Optional[Resource]:
        """
        Returns the resource on the specified tile.

        :param row: The row of the tile.
        :param col: The column of the tile.
        :return: The resource on the tile, or False if an IndexError occurs.
        """
        try:
            # Get the resource on the tile
            return self.board[row][col].get_resource()
        except IndexError:
            return None
