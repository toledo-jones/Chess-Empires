from . import *


class RogueRook(Piece):
    def __repr__(self):
        return 'rogue_rook'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                    Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                    Constant.DOWN_LEFT)
        self.is_rogue = True

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.rogue_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.rogue_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares

    def stealing_squares(self, engine):
        squares = []

        for direction in self.stealing_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_stealing_state(self.row, self.col)

