from . import *


class King(Piece):
    def __repr__(self):
        return 'king'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.move_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                Constant.DOWN_LEFT)

    def capture_squares(self, engine):
        squares = []
        for direction in self.move_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))
        return squares

    def move_squares(self, engine):
        squares = []
        for direction in self.move_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))
        return squares

    def right_click(self, engine):
        return engine.create_king_menu(self.row, self.col)
