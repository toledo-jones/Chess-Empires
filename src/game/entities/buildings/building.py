from abc import ABC

from src.game.entities.piece import Piece


class Building(Piece, ABC):
    def __init__(self, column, row, color):
        super().__init__(column, row, color)

    def path(self):
        return f"assets/sprites/entities/buildings/{self.color}/{str(self)}.png"
