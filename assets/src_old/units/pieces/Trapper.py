from . import *


class Trapper(Piece):
    def __repr__(self):
        return 'trapper'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.trapping_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                    Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                    Constant.DOWN_LEFT)
        self.move_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN)
        self.capture_directions = (Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.move_distance = 3
        self.capture_distance = 1

    def capture_squares(self, engine):
        squares = []

        for direction in self.capture_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))
        return squares

    def base_spawn_criteria(self, engine, row, col):
        if Constant.tile_in_bounds(row, col):
            return not engine.has_trap(row, col) and not engine.board[row][col].is_protected_by_opposite_color(
                self.color)

    def spawn_squares(self, engine):
        squares = []
        if not self.can_spawn(engine):
            return squares

        for direction in self.trapping_directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.base_spawn_criteria(engine, r, c):
                if engine.can_be_occupied_by_gold_general(r, c):
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
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_building_state(self.row, self.col)
