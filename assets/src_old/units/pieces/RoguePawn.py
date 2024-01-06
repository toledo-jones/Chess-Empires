from . import *


class RoguePawn(Piece):
    def __repr__(self):
        return 'rogue_pawn'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.mining_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                  Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                  Constant.DOWN_LEFT)
        self.move_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN)
        self.capture_directions = (Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                    Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                    Constant.DOWN_LEFT)
        self.move_distance = 3
        self.capture_distance = 1

        self.is_rogue = True

    def mining_squares(self, engine):
        mining_squares = []
        for direction in self.mining_directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if engine.has_mineable_resource(r, c):
                if engine.get_occupying(r, c):
                    if engine.get_occupying_color(r, c) is not self.color:
                        pass
                    elif engine.get_occupying_color(r, c) is self.color:
                        mining_squares.append((r, c))
                elif engine.has_none_occupying(r, c):
                    mining_squares.append((r, c))
            elif engine.can_contain_quarry(r, c) and engine.is_empty(r, c):
                mining_squares.append((r, c))

        return mining_squares

    def capture_squares(self, engine):
        squares = []

        for direction in self.capture_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.move_directions:
            for distance in range(1, self.move_distance):
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

        for direction in range(len(self.stealing_directions)):
            d = self.stealing_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_stealing_mining_state(self.row, self.col)
