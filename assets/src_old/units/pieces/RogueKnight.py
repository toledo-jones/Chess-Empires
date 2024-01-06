from . import *


class RogueKnight(Piece):
    def __repr__(self):
        return 'rogue_knight'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                    Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                    Constant.DOWN_LEFT)
        self.distance = 1
        self.is_rogue = True
        self.is_cavalry = True

    def stealing_squares(self, engine):
        squares = []

        for direction in self.stealing_directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

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
            if self.rogue_move_criteria(engine, r, c):
                squares.append((r, c))

        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_stealing_state(self.row, self.col)
