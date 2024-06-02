from __future__ import annotations
import typing
from chess_empires.game.game_event import GameEvent

if typing.TYPE_CHECKING:
    from chess_empires.game.game_manager import GameManager
    from chess_empires.game.entities.piece import Piece


class Spawn(GameEvent):
    def __init__(self,
                 game_manager: GameManager,
                 piece: Piece,
                 column: int,
                 row: int,
                 color: str):
        """
        Initialize a Spawn event.

        :param game_manager: The game manager instance.
        :param piece: The Piece object being spawned.
        :param column: The column where the piece is spawned.
        :param row: The row where the piece is spawned.
        :param color: The color of the spawned piece.
        """
        super().__init__(game_manager)
        self.piece = piece
        self.column = column
        self.row = row
        self.color = color
        self.player = self.game_manager.players[self.color]

    def complete(self) -> bool:
        # Set piece of board to the new piece
        self.game_manager.board[self.column][self.row].set_occupying(self.piece)

        # apply costs

        # add it to lists
        self.game_manager.add_piece(self.piece, self.player)

        # etc
        return True

    def undo(self):
        pass

    @property
    def piece(self) -> Piece:
        """
        Get the Piece object being spawned.

        :return: The Piece object being spawned.
        """
        return self._piece

    @piece.setter
    def piece(self, piece: Piece):
        """
        Set the Piece object being spawned.

        :param piece: The new Piece object being spawned.
        """
        self._piece = piece

    @property
    def column(self) -> int:
        """
        Get the column where the piece is spawned.

        :return: The column where the piece is spawned.
        """
        return self._column

    @column.setter
    def column(self, column: int):
        """
        Set the column where the piece is spawned.

        :param column: The new column where the piece is spawned.
        """
        self._column = column

    @property
    def row(self) -> int:
        """
        Get the row where the piece is spawned.

        :return: The row where the piece is spawned.
        """
        return self._row

    @row.setter
    def row(self, row: int):
        """
        Set the row where the piece is spawned.

        :param row: The new row where the piece is spawned.
        """
        self._row = row

    @property
    def color(self) -> str:
        """
        Get the color of the spawned piece.

        :return: The color of the spawned piece.
        """
        return self._color

    @color.setter
    def color(self, color: str):
        """
        Set the color of the spawned piece.

        :param color: The new color of the spawned piece.
        """
        self._color = color
