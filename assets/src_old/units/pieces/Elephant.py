from . import *


class Elephant(Piece):
    def __repr__(self):
        return 'elephant'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)

        self.directions_to_extra_moves = {Constant.TWO_UP_RIGHT: Constant.UP,
                                          Constant.TWO_RIGHT_UP: Constant.RIGHT,
                                          Constant.TWO_DOWN_RIGHT: Constant.DOWN,
                                          Constant.TWO_RIGHT_DOWN: Constant.RIGHT,
                                          Constant.TWO_UP_LEFT: Constant.UP,
                                          Constant.TWO_LEFT_UP: Constant.LEFT,
                                          Constant.TWO_DOWN_LEFT: Constant.DOWN,
                                          Constant.TWO_LEFT_DOWN: Constant.LEFT}
        self.distance = 1
        self.is_cavalry = True

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))
            elif self.base_move_criteria(engine, r, c):
                extra_direction = self.directions_to_extra_moves[direction]
                r += extra_direction[0]
                c += extra_direction[1]
                if self.can_capture(r, c, engine):
                    squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))
                extra_direction = self.directions_to_extra_moves[direction]
                r += extra_direction[0]
                c += extra_direction[1]
                if self.base_move_criteria(engine, r, c):
                    squares.append((r, c))

        return squares

