from . import *


class Unicorn(Piece):
    def __repr__(self):
        return 'unicorn'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.is_cavalry = True
        self.knight_directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)

        self.cardinal_directions = (Constant.THREE_RIGHT, Constant.THREE_DOWN, Constant.THREE_UP, Constant.THREE_LEFT)
        self.knight_directions_to_extra_moves = {Constant.TWO_UP_RIGHT: Constant.TWO_RIGHT_UP,
                                                 Constant.TWO_RIGHT_UP: Constant.TWO_UP_RIGHT,
                                                 Constant.TWO_DOWN_RIGHT: Constant.TWO_RIGHT_DOWN,
                                                 Constant.TWO_RIGHT_DOWN: Constant.TWO_DOWN_RIGHT,
                                                 Constant.TWO_UP_LEFT: Constant.TWO_LEFT_UP,
                                                 Constant.TWO_LEFT_UP: Constant.TWO_UP_LEFT,
                                                 Constant.TWO_DOWN_LEFT: Constant.TWO_LEFT_DOWN,
                                                 Constant.TWO_LEFT_DOWN: Constant.TWO_DOWN_LEFT}
        self.distance = 1

    def capture_squares(self, engine):
        squares = []

        for direction in self.cardinal_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

            elif engine.can_be_occupied(r, c):
                extra_move_direction = self.knight_directions_to_extra_moves[direction]
                r += extra_move_direction[0]
                c += extra_move_direction[1]
                if self.can_capture(r, c, engine):
                    squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.cardinal_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))
                extra_move_direction = self.knight_directions_to_extra_moves[direction]
                r += extra_move_direction[0]
                c += extra_move_direction[1]
                if self.base_move_criteria(engine, r, c):
                    if (r, c) not in squares:
                        squares.append((r, c))

        return squares
