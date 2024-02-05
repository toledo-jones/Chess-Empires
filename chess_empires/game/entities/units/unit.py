from abc import ABC

from chess_empires.game.entities.piece import Piece


class Unit(Piece, ABC):
    def __init__(self, column, row, color):
        super().__init__(column, row, color)

    def path(self):
        return f"assets/sprites/entities/units/{self.color}/{str(self)}.png"
