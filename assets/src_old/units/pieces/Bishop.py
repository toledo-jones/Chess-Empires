from . import *


class Bishop(Piece):
    def __repr__(self):
        return 'bishop'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT, Constant.UP_RIGHT)
        self.praying_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def praying_squares(self, engine):
        moves = []

        for direction in range(len(self.praying_directions)):
            d = self.praying_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    moves.append((r, c))

        return moves

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
                if not self.base_move_criteria(engine, r, c):
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
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            if not engine.rituals_banned:
                return engine.transfer_to_praying_state(self.row, self.col)

