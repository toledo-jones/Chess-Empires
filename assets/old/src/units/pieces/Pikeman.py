from . import *


class Pikeman(Piece):
    def __repr__(self):
        return 'pikeman'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = 1

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        return squares
