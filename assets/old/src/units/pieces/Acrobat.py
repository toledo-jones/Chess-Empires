from . import Piece


class Acrobat(Piece):
    def __repr__(self):
        return 'acrobat'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT, Constant.UP_RIGHT)
        self.distance = Constant.BOARD_WIDTH_SQ
        self.leaped_square = None

    def move_criteria(self, engine, r, c):
        if engine.can_be_legally_occupied(r, c):
            if engine.board[r][c].is_protected_by_opposite_color(self.color):
                return False
            return True

    def capture_squares(self, engine):
        squares = []
        for direction in self.directions:
            self.leaped_square = None
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not self.leaped_square:
                    if not self.move_criteria(engine, r, c):
                        break
                    if engine.get_occupying(r, c):
                        if self.can_capture(r, c, engine):
                            squares.append((r, c))
                        self.leaped_square = (r, c)
                else:
                    if self.can_capture(r, c, engine):
                        squares.append((r, c))
                        break
                    elif not self.base_move_criteria(engine, r, c):
                        break

        return squares

    def move_squares(self, engine):
        squares = []
        for direction in self.directions:
            self.leaped_square = None
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not self.leaped_square:
                    if not self.move_criteria(engine, r, c):
                        break
                    else:
                        if engine.get_occupying(r, c):
                            self.leaped_square = (r, c)
                        else:
                            squares.append((r, c))
                else:
                    if not self.base_move_criteria(engine, r, c):
                        break
                    else:
                        squares.append((r, c))
        return squares
