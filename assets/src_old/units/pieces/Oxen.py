from . import *


class Oxen(Piece):
    def __repr__(self):
        return 'oxen'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.is_cavalry = True

        self.extra_move_directions = {Constant.TWO_UP_RIGHT: Constant.UP,
                                      Constant.TWO_RIGHT_UP: Constant.RIGHT,
                                      Constant.TWO_DOWN_RIGHT: Constant.DOWN,
                                      Constant.TWO_RIGHT_DOWN: Constant.RIGHT,
                                      Constant.TWO_UP_LEFT: Constant.UP,
                                      Constant.TWO_LEFT_UP: Constant.LEFT,
                                      Constant.TWO_DOWN_LEFT: Constant.DOWN,
                                      Constant.TWO_LEFT_DOWN: Constant.LEFT}

        self.distance = Constant.BOARD_WIDTH_SQ

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            extra_direction = self.extra_move_directions[direction]
            for distance in range(0, self.distance):
                r = self.row + direction[0] + extra_direction[0] * distance
                c = self.col + direction[1] + extra_direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    if (r, c) not in squares:
                        squares.append((r, c))
                        break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            extra_direction = self.extra_move_directions[direction]
            for distance in range(0, self.distance):
                r = self.row + direction[0] + extra_direction[0] * distance
                c = self.col + direction[1] + extra_direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    if (r, c) not in squares:
                        squares.append((r, c))

        return squares
