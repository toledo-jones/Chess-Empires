from . import *


class PrayerStone(Building):
    def __repr__(self):
        return 'prayer_stone'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = ()
        self.distance = 0
        self.remaining = 0
        self.yield_when_prayed = Constant.PRAYER_STONE_YIELD
        self.is_effected_by_jester = False
        self.additional_actions = Constant.PRAYER_STONE_ADDITIONAL_ACTIONS

    def right_click(self, engine):
        if super().right_click(engine):
            if not engine.rituals_banned:
                self.casting = True
                return engine.create_ritual_menu(self.row, self.col,
                                                 engine.prayer_stone_rituals[engine.turn_count_actual])

