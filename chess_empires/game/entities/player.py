from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from chess_empires.game.entities.piece import Piece


class Player:
    def __init__(self, color=None):
        """
        Initialize a Player object.

        :param color: A string representing the color of the player. Defaults to None.
        """
        self.color = color
        self.pieces = []

    def add_piece(self, piece):
        self.pieces.append(piece)

    @property
    def color(self) -> str:
        """
        Get the color of the player.

        :return: A string representing the color of the player.
        """
        return self._color

    @color.setter
    def color(self, color: str):
        """
        Set the color of the player.

        :param color: A string representing the new color of the player.
        """
        self._color = color

    @property
    def pieces(self):
        """
        Get the list of pieces owned by the player.

        :return: A list of Piece objects owned by the player.
        """
        return self._pieces

    @pieces.setter
    def pieces(self, pieces: list[Piece]):
        """
        Set the list of pieces owned by the player.

        :param pieces: A list of Piece objects representing the new pieces owned by the player.
        """
        self._pieces = pieces
