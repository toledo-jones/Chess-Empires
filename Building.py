import random

import pygame

import Constant


class Building:
    def __repr__(self):
        return 'none'

    def __init__(self, row, col, color):
        self.offset = self.get_piece_offset()

        self.row = row
        self.col = col
        self.color = color

        self.purchasing = False
        self.mining = False
        self.selected = False
        self.pre_selected = False
        self.praying = False
        self.casting = False
        self.stealing = False
        self.mining_stealing = False

        self.intercepted = False
        self.unused_piece_highlight = False

        self.is_rogue = False
        self.is_general = False

        self.actions_remaining = 0

        self.spawn_squares_list = []
        self.move_squares_list = []
        self.interceptor_squares_list = []
        self.stealing_squares_list = []

        self.additional_actions = 0
        self.additional_piece_limit = 0
        self.population_value = 0

        self.ritual_squares_list = []
        self.is_effected_by_jester = True

        self.square = pygame.Surface((Constant.SQ_SIZE, Constant.SQ_SIZE))
        self.self_selected_square_color = Constant.SELF_SQUARE_HIGHLIGHT_COLOR
        self.unused_square_color = Constant.UNUSED_PIECE_HIGHLIGHT_COLOR
        self.move_square_color = Constant.MOVE_SQUARE_HIGHLIGHT_COLOR

    def get_piece_offset(self):
        if random.randint(1, 2) > 1:
            r = random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
            z = random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
            return r, z
        else:
            return Constant.PIECE_IMAGE_MODIFY[str(self)]['OFFSET']

    def get_position(self):
        return self.row, self.col

    def change_pos(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        return self.color

    def draw_highlights(self, win):
        if self.purchasing:
            self.highlight_self_square(win)
            self.highlight_spawn_squares(win)
        if self.pre_selected:
            self.highlight_self_square(win)
            self.highlight_spawn_squares(win)
        if self.unused_piece_highlight:
            self.highlight_self_square_unused(win)
        if self.casting:
            self.highlight_self_square(win)

        if self.actions_remaining == 0:
            self.unused_piece_highlight = False

    def draw(self, win):
        if self.color == 'w':
            draw_this = Constant.W_BUILDINGS['w_' + str(self)]
        elif self.color == 'b':
            draw_this = Constant.B_BUILDINGS['b_' + str(self)]

        x = (self.col * Constant.SQ_SIZE) + self.offset[0]
        y = (self.row * Constant.SQ_SIZE) + self.offset[1]
        win.blit(draw_this, (x, y))

    def square_fill(self, color):
        self.square.fill(color)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)

    def draw_squares_in_list(self, win, square_list, color):
        self.square_fill(color)
        for square in square_list:
            win.blit(self.square, (square[1] * Constant.SQ_SIZE, square[0] * Constant.SQ_SIZE))

    def draw_self_highlight(self, win, color):
        self.square_fill(color)
        win.blit(self.square, (self.col * Constant.SQ_SIZE, self.row * Constant.SQ_SIZE))

    def highlight_self_square_unused(self, win):
        self.draw_self_highlight(win, self.unused_square_color)

    def highlight_self_square(self, win):
        self.draw_self_highlight(win, self.self_selected_square_color)

    def stealing_squares(self, engine):
        return []

    def highlight_ritual_squares(self, win):
        self.draw_squares_in_list(win, self.ritual_squares_list, self.move_square_color)

    def highlight_spawn_squares(self, win):
        self.draw_squares_in_list(win, self.spawn_squares_list, self.move_square_color)

    def update_spawn_squares(self, engine):
        self.spawn_squares_list = self.spawn_squares(engine)

    def update_stealing_squares(self, engine):
        self.stealing_squares_list = self.stealing_squares(engine)

    def update_move_squares(self, engine):
        return []

    def update_mining_squares(self, engine):
        return []

    def get_additional_actions(self):
        return self.additional_actions

    def get_additional_piece_limit(self):
        return self.additional_piece_limit

    def get_population_value(self):
        return self.population_value

    def update_praying_squares(self, engine):
        self.praying_squares_list = self.praying_squares(engine)

    def update_interceptor_squares(self, engine):
        self.interceptor_squares_list = self.interceptor_squares(engine)

    def interceptor_squares(self, engine):
        return []

    def praying_squares(self, engine):
        return []

    def spawn_squares(self, engine):
        return []

    def right_click(self, engine):
        if self.actions_remaining > 0 and engine.players[engine.turn].actions_remaining > 0:
            return True


class Stable(Building):
    def __repr__(self):
        return 'stable'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                  Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                  Constant.DOWN_LEFT)
        self.distance = 1
        self.additional_actions = Constant.STABLE_ADDITIONAL_ACTIONS
        self.additional_piece_limit = Constant.ADDITIONAL_PIECE_LIMIT[str(self)]

    def spawn_squares(self, engine):
        spawn_squares = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied(r, c):
                spawn_squares.append((r, c))
        return spawn_squares

    def right_click(self, engine):
        if super().right_click(engine):
            if engine.transfer_to_building_state(self.row, self.col):
                return True


class Barracks(Building):
    def __repr__(self):
        return 'barracks'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                  Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                  Constant.DOWN_LEFT)
        self.distance = 1
        self.additional_actions = Constant.BARRACKS_ADDITIONAL_ACTIONS
        self.additional_piece_limit = Constant.ADDITIONAL_PIECE_LIMIT[str(self)]

    def spawn_squares(self, engine):
        spawn_squares = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied(r, c):
                spawn_squares.append((r, c))
        return spawn_squares

    def right_click(self, engine):
        if super().right_click(engine):
            if engine.transfer_to_building_state(self.row, self.col):
                return True


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
        self.additional_piece_limit = Constant.ADDITIONAL_PIECE_LIMIT[str(self)]

    def spawn_squares(self, engine):
        spawn_squares = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied(r, c):
                spawn_squares.append((r, c))
        return spawn_squares

    def right_click(self, engine):
        if super().right_click(engine):
            if engine.transfer_to_building_state(self.row, self.col):
                return True


class Fortress(Building):
    def __repr__(self):
        return 'fortress'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                  Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                  Constant.DOWN_LEFT)
        self.distance = 1
        self.additional_actions = Constant.FORTRESS_ADDITIONAL_ACTIONS
        self.additional_piece_limit = Constant.ADDITIONAL_PIECE_LIMIT[str(self)]

    def spawn_squares(self, engine):
        spawn_squares = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied_by_rogue(r, c):
                spawn_squares.append((r, c))

        return spawn_squares

    def right_click(self, engine):
        if super().right_click(engine):
            if engine.transfer_to_building_state(self.row, self.col):
                return True


class Flag(Building):
    def __repr__(self):
        return 'flag'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = ()
        self.distance = 0
        self.remaining = 0


class Wall(Building):
    def __repr__(self):
        return 'wall'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = ()
        self.distance = 0
        self.remaining = 0


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
            self.casting = True
            return engine.create_ritual_menu(self.row, self.col, engine.prayer_stone_rituals[engine.turn_count_actual])


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
                if engine.can_be_occupied_by_gold_general(r, c):
                    ritual_squares.append((r, c))

        return ritual_squares

    def right_click(self, engine):
        if super().right_click(engine):
            self.casting = True
            return engine.create_ritual_menu(self.row, self.col, engine.monolith_rituals[engine.turn_count_actual])


