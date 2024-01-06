from . import *


class Magician(Piece):
    def __repr__(self):
        return 'magician'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = 1

    def right_click(self, engine):
        if self.actions_remaining > 0 and engine.players[engine.turn].actions_remaining > 0:
            if not engine.rituals_banned:
                self.casting = True
                return engine.create_ritual_menu(self.row, self.col, engine.magician_rituals[engine.turn_count_actual], 'gold')

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        return squares
