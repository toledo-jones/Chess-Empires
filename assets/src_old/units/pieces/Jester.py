from . import *


class Jester(Piece):
    def __repr__(self):
        return 'jester'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares

    def interceptor_squares(self, engine):
        squares = []
        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if engine.has_occupying(r, c):
                squares.append((r, c))

        return squares
