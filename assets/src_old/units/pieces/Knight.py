from . import *


class Knight(Piece):
    def __repr__(self):
        return 'knight'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.distance = 1
        self.is_cavalry = True

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
