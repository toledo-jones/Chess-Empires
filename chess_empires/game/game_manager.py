from chess_empires.utilities.singleton import Singleton
from chess_empires.game.entities.board import Board
from chess_empires.utilities.factories.piece_factory import PieceFactory
from chess_empires.game.entities.piece import Piece


class GameManager(Singleton):
    def __init__(self, event_manager, scene_manager, state_manager, client, engine):
        self.event_manager = event_manager
        self.scene_manager = scene_manager
        self.state_manager = state_manager
        self.engine = engine
        self.client = client
        self.board = Board(self.event_manager)
        self.create_piece('acrobat', 0, 0, 'white')

        self.engine.board = self.board

    def render(self):
        self.engine.render()
        self.scene_manager.render()
        self.state_manager.render()

        # After all other images are rendered output the logical screen to the main screen
        self.engine.render_game_window()

    def is_player_data(self, data):
        return self.client.get_player_id() == data['player_id']

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

        # Add piece to player
        # Add piece to game board
        # Send information to server and to other connected clients

    def start_game(self):
        self.scene_manager.set_scene('GameScene')
        self.state_manager.set_state('TestState')

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
