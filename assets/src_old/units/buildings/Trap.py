from . import *


class Trap(Building):
    def __repr__(self):
        return 'trap'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)

    def highlight_self_square_unused(self, win):
        pass
