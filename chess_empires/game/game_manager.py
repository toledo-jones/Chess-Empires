from __future__ import annotations

import typing

from chess_empires.utilities.singleton import Singleton
from chess_empires.game.entities.board import Board
from chess_empires.utilities.factories.piece_factory import PieceFactory
from chess_empires.game.entities.piece import Piece
from chess_empires.utilities.factories.event_factory import EventFactory
from game.db import EventTypes

if typing.TYPE_CHECKING:
    from chess_empires.game.game_event import GameEvent
    from chess_empires.game.scene_manager import SceneManager
    from chess_empires.game.state_manager import StateManager
    from chess_empires.game.engine import GameEngine
    from chess_empires.network.client import GameClient
    from chess_empires.game.event_manager import EventManager
    from chess_empires.game.entities.player import Player


class GameManager(Singleton):
    def __init__(self,
                 event_manager: EventManager,
                 scene_manager: SceneManager,
                 state_manager: StateManager,
                 client: GameClient,
                 engine: GameEngine):
        """
        Initialize the GameManager.

        This will control the board, players, execute events and handle all the game logic.

        :param event_manager: An instance of EventManager for subscribing and emitting game events.
        :param scene_manager: An instance of SceneManager for managing game scenes.
        :param state_manager: An instance of StateManager for managing game states.
        :param client: An instance of GameClient for interacting with the game server.
        :param engine: An instance of GameEngine for rendering the game.

        """

        # Class attributes
        self.event_manager = event_manager
        self.scene_manager = scene_manager
        self.state_manager = state_manager
        self.engine = engine
        self.client = client

        # Create the board
        self.board = Board(self.event_manager)

        # Players objects are stored here
        self.players = []

        # Game Events completed this turn are stored here.
        # The objects can be accessed and undone while they are in this list
        self.turn_events = []

        # Set the board in the engine
        self.engine.board = self.board

    def render(self):
        self.engine.render()
        self.scene_manager.render()
        self.state_manager.render()

        # After all other images are rendered output the logical screen to the main screen
        self.engine.render_game_window()

    def is_player_data(self, data):
        return self.client.get_player_id() == data['player_id']

    def add_piece(self,
                  piece: Piece,
                  player: Player) -> bool:
        """
        Adds a piece to a player's units list

        :param player: Player object to add piece to
        :param piece: Piece object to be added
        :return: True if the piece is successfully added, False if it cannot be added
        """
        self.engine.units.add(piece)
        return player.add_piece(piece)

    def create_player(self, color: str):
        pass

    def create_piece(self,
                     piece_name: str,
                     column: int,
                     row: int,
                     color: str,
                     **kwargs) -> bool:
        """
        Uses a class-discovering factory pattern to dynamically create a piece and add it to the board.

        :param piece_name: A string representing the name or type of the piece to be created.
        :param column: An integer specifying the column on the board where the piece will be placed.
        :param row: An integer specifying the row on the board where the piece will be placed.
        :param color: A string indicating the color of the piece.
        :param kwargs: Additional keyword arguments that may be required for specific piece types.

        :return: Returns True if the piece is successfully created and added to the board, False otherwise.
        """

        # Use the PieceFactory to dynamically create the piece
        piece = PieceFactory.create(piece_name, column, row, color, **kwargs)

        # Debug
        print(f"New {piece_name} is an instance of Piece: {isinstance(piece, Piece)}")

        # Failsafe to make sure the piece is of valid type
        if not isinstance(piece, Piece):
            print(f"Error: Unable to create piece '{piece_name}'.")
            return False

        # Send information to server and to other connected clients
        event = EventFactory.create("spawn", self, piece, column, row, color)

        self.event_manager.emit(EventTypes.GAME_EVENT, event)

    def execute_game_event(self, event: GameEvent) -> bool:
        """
        Execute a game event
        :param event: Game Event to be executed
        :return: returns True if the event was successfully completed
        """
        # attempt to complete the event
        if event.complete():
            # append the completed event object to the turn events list
            self.turn_events.append(event)

            # Event completed successfully
            return True

        # Event could not be completed
        print(f"{event} failed to complete")
        return False

    def start_game(self):
        self.scene_manager.set_scene('Title')

    def initialize_player(self):
        pass

    def update(self):
        self.engine.update()
        self.scene_manager.update()
        self.state_manager.update()

    @property
    def event_manager(self):
        """
        The event manager responsible for handling game events.

        :return: The event manager instance.
        """
        return self._event_manager

    @event_manager.setter
    def event_manager(self, event_manager):
        """
        Set the event manager instance.

        :param event_manager: The new event manager instance.
        """
        self._event_manager = event_manager

    @property
    def scene_manager(self):
        """
        The scene manager responsible for managing game scenes.

        :return: The scene manager instance.
        """
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, scene_manager):
        """
        Set the scene manager instance.

        :param scene_manager: The new scene manager instance.
        """
        self._scene_manager = scene_manager

    @property
    def state_manager(self):
        """
        The state manager responsible for managing game states.

        :return: The state manager instance.
        """
        return self._state_manager

    @state_manager.setter
    def state_manager(self, state_manager):
        """
        Set the state manager instance.

        :param state_manager: The new state manager instance.
        """
        self._state_manager = state_manager

    @property
    def engine(self):
        """
        The game engine responsible for game logic and rendering.

        :return: The game engine instance.
        """
        return self._engine

    @engine.setter
    def engine(self, engine):
        """
        Set the game engine instance.

        :param engine: The new game engine instance.
        """
        self._engine = engine

    @property
    def client(self):
        """
        The client object representing the game client.

        :return: The client instance.
        """
        return self._client

    @client.setter
    def client(self, client):
        """
        Set the client instance.

        :param client: The new client instance.
        """
        self._client = client

    @property
    def board(self):
        """
        The game board containing pieces and managing game state.

        :return: The board instance.
        """
        return self._board

    @board.setter
    def board(self, board):
        """
        Set the board instance.

        :param board: The new board instance.
        """
        self._board = board
