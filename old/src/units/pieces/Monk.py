from . import *


class Monk(Piece):
    def __repr__(self):
        return 'monk'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = 1

    def right_click(self, engine):
        if self.actions_remaining > 0:
            if not engine.rituals_banned:
                if not engine.players[engine.turn].actions_remaining > 0:
                    return engine.transfer_to_praying_state(self.row, self.col)
                return engine.transfer_to_praying_building_state(self.row, self.col)

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        return squares

    def base_spawn_criteria(self, engine, row, col):
        if Constant.tile_in_bounds(row, col):
            return engine.has_none_occupying(row, col) and not engine.has_portal(row, col) and not engine.has_trap(row,
                                                                                                                   col)

    def spawn_squares(self, engine):
        spawn_squares = []
        if not self.can_spawn(engine):
            return spawn_squares

        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.base_spawn_criteria(engine, r, c):
                if engine.has_no_resource(r, c, ) or engine.has_depleted_quarry(r, c):
                    spawn_squares.append((r, c))
        return spawn_squares

    def praying_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    squares.append((r, c))

        return squares

