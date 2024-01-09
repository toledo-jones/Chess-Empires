from . import *


class Castle(Building):
    def __repr__(self):
        return 'castle'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = 1
        self.additional_actions = Constant.CASTLE_ADDITIONAL_ACTIONS

    def spawn_squares(self, engine):
        spawn_squares = []

        if not str(engine.state[-1]) == 'start spawn':
            if not self.can_spawn(engine):
                return spawn_squares

        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if engine.spawning == 'rogue_pawn':
                if engine.can_be_occupied_by_rogue(r, c):
                    spawn_squares.append((r, c))
            elif self.base_spawn_criteria(engine, r, c):
                if engine.can_be_occupied(r, c):
                    spawn_squares.append((r, c))
        return spawn_squares

    def right_click(self, engine):
        if super().right_click(engine):
            if engine.transfer_to_building_state(self.row, self.col):
                return True
