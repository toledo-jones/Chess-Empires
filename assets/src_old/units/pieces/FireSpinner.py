from . import *


class FireSpinner(Piece):
    def __repr__(self):
        return 'fire_spinner'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.knight_directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.depth = 3

    def move_squares(self, engine):
        squares = []
        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))
                for i in range(self.depth):
                    new_r = r + direction[0]
                    new_c = c + direction[1]
                    if self.base_move_criteria(engine, new_r, new_c):
                        if (new_r, new_c) not in squares:
                            squares.append((new_r, new_c))
                    else:
                        break

        return squares

    def capture_squares(self, engine):
        squares = []
        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))
            elif self.base_move_criteria(engine, r, c):
                for i in range(self.depth):
                    new_r = r + direction[0]
                    new_c = c + direction[1]
                    if self.can_capture(new_r, new_c, engine):
                        if (new_r, new_c) not in squares:
                            squares.append((new_r, new_c))
                        break
                    elif not self.base_move_criteria(engine, new_r, new_c):
                        break

        return squares
