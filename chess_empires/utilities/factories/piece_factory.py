from chess_empires.utilities.factories.base_factory import BaseFactory, auto_register, DefaultClass
from chess_empires.game.entities.piece import Piece


class PieceFactory(BaseFactory):
    _default_class = DefaultClass


# Automatically discover and register scene classes
auto_register(PieceFactory, "game.entities", Piece)
