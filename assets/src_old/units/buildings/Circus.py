from . import *


class Circus(Building):
    def __repr__(self):
        return 'circus'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = 1
        self.additional_actions = Constant.CIRCUS_ADDITIONAL_ACTIONS

    def spawn_squares(self, engine):
        spawn_squares = []

        if not self.can_spawn(engine):
            return spawn_squares

        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.base_spawn_criteria(engine, r, c):
                if engine.can_be_occupied(r, c):
                    spawn_squares.append((r, c))
        return spawn_squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_building_state(self.row, self.col)
