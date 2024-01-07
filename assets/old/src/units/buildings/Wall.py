from . import *


class Wall(Building):
    def __repr__(self):
        return 'wall'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.is_wall = True

    def highlight_self_square_unused(self, win):
        pass
