from . import *


class Doe(Piece):
    def __repr__(self):
        return 'doe'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.knight_directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.bishop_directions = (Constant.UP_LEFT, Constant.UP_RIGHT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ
        self.is_cavalry = True

    def capture_squares(self, engine):
        squares = []

        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        for direction in self.bishop_directions:
            for i in range(1, self.distance):
                r = self.row + direction[0] * i
                c = self.col + direction[1] * i
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        for direction in self.bishop_directions:
            for i in range(1, self.distance):
                r = self.row + direction[0] * i
                c = self.col + direction[1] * i
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))

        return squares
