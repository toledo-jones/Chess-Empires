from . import *


class Ram(Piece):
    def __repr__(self):
        return 'ram'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.TWO_UP_RIGHT, Constant.TWO_UP_LEFT, Constant.TWO_RIGHT_UP,
                           Constant.TWO_RIGHT_DOWN, Constant.TWO_LEFT_UP, Constant.TWO_LEFT_DOWN,
                           Constant.TWO_DOWN_LEFT, Constant.TWO_DOWN_RIGHT)
        self.is_cavalry = True
        self.extra_move_directions = {Constant.TWO_UP_RIGHT: Constant.UP_RIGHT,
                                      Constant.TWO_UP_LEFT: Constant.UP_LEFT,
                                      Constant.TWO_RIGHT_UP: Constant.UP_RIGHT,
                                      Constant.TWO_RIGHT_DOWN: Constant.DOWN_RIGHT,
                                      Constant.TWO_LEFT_UP: Constant.UP_LEFT,
                                      Constant.TWO_LEFT_DOWN: Constant.DOWN_LEFT,
                                      Constant.TWO_DOWN_LEFT: Constant.DOWN_LEFT,
                                      Constant.TWO_DOWN_RIGHT: Constant.DOWN_RIGHT, }

        self.distance = Constant.BOARD_WIDTH_SQ

    def capture_squares(self, engine):
        squares = []
        for direction in self.directions:
            for distance in range(0, Constant.BOARD_WIDTH_SQ):
                d = self.extra_move_directions[direction]
                r = self.row + direction[0] + d[0] * distance
                c = self.col + direction[1] + d[1] * distance
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
        for direction in self.directions:
            for distance in range(0, Constant.BOARD_WIDTH_SQ):
                d = self.extra_move_directions[direction]
                r = self.row + direction[0] + d[0] * distance
                c = self.col + direction[1] + d[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))

        return squares
