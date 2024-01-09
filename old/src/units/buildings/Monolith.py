from . import *


class Monolith(Building):
    def __repr__(self):
        return 'monolith'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP, Constant.RIGHT, Constant.LEFT, Constant.DOWN,
                           Constant.UP_LEFT, Constant.DOWN_LEFT, Constant.DOWN_RIGHT, Constant.UP_RIGHT)
        self.distance = 2
        self.remaining = 0
        self.yield_when_prayed = Constant.MONOLITH_YIELD
        self.is_effected_by_jester = False
        self.additional_actions = Constant.MONOLITH_ADDITIONAL_ACTIONS

    def gold_general_ritual_squares(self, engine):
        ritual_squares = []
        for direction in self.directions:
            for i in range(self.distance):
                r = self.row + direction[0] * i
                c = self.col + direction[1] * i
                if self.base_spawn_criteria(engine, r, c):
                    if engine.can_be_occupied_by_gold_general(r, c):
                        ritual_squares.append((r, c))

        return ritual_squares

    def right_click(self, engine):
        if super().right_click(engine):
            if not engine.rituals_banned:
                self.casting = True
                return engine.create_ritual_menu(self.row, self.col, engine.monolith_rituals[engine.turn_count_actual])

