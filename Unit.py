import pygame
import Constant
import random


class Unit:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.offset = self.get_sprite_offset()

        self.sprites = Constant.W_PIECES | Constant.W_BUILDINGS | Constant.B_PIECES | Constant.B_BUILDINGS

        self.purchasing = False
        self.mining = False
        self.selected = False
        self.pre_selected = False
        self.unused_piece_highlight = False
        self.praying = False
        self.casting = False
        self.stealing = False
        self.mining_stealing = False
        self.persuading = False
        self.praying_building = False

        self.can_be_persuaded = True
        self.intercepted = False
        self.is_rogue = False
        self.is_general = False
        self.is_wall = False
        self.is_cavalry = False

        self.additional_actions = 0
        self.actions_remaining = 0
        self.population_value = Constant.PIECE_POPULATION[str(self)]
        self.additional_piece_limit = Constant.ADDITIONAL_PIECE_LIMIT[str(self)]

        self.praying_squares_list = []
        self.spawn_squares_list = []
        self.move_squares_list = []
        self.mining_squares_list = []
        self.interceptor_squares_list = []
        self.stealing_squares_list = []
        self.ritual_squares_list = []
        self.capture_squares_list = []
        self.persuader_squares_list = []

        self.square = pygame.Surface((Constant.SQ_SIZE, Constant.SQ_SIZE))
        self.self_selected_square_color = Constant.SELF_SQUARE_HIGHLIGHT_COLOR
        self.unused_square_color = Constant.UNUSED_PIECE_HIGHLIGHT_COLOR
        self.move_square_color = Constant.MOVE_SQUARE_HIGHLIGHT_COLOR
        self.is_effected_by_jester = True

    def update_praying_squares(self, engine):
        self.praying_squares_list = self.praying_squares(engine)

    def update_stealing_squares(self, engine):
        self.stealing_squares_list = self.stealing_squares(engine)

    def update_interceptor_squares(self, engine):
        self.interceptor_squares_list = self.interceptor_squares(engine)

    def update_persuader_squares(self, engine):
        self.persuader_squares_list = self.persuader_squares(engine)

    def update_mining_squares(self, engine):
        self.mining_squares_list = self.mining_squares(engine)

    def update_move_squares(self, engine):
        self.move_squares_list = self.move_squares(engine)

    def update_capture_squares(self, engine):
        self.capture_squares_list = self.capture_squares(engine)

    def update_spawn_squares(self, engine):
        self.spawn_squares_list = self.spawn_squares(engine)

    def update_ritual_squares(self, engine):
        self.ritual_squares_list = self.ritual_squares(engine)

    def possible_moves(self):
        return {'spawn': self.spawn_squares_list, 'move': self.move_squares_list, 'mine': self.mining_squares_list,
                'steal': self.stealing_squares_list, 'pray': self.praying_squares_list,
                'capture': self.capture_squares_list, 'ritual': self.ritual_squares_list,
                'persuade': self.persuader_squares_list}

    def can_capture(self, r, c, engine):
        capture_tile = None
        if Constant.tile_in_bounds(r, c):
            capture_tile = engine.board[r][c].get_occupying()
        valid_square = isinstance(capture_tile, Piece) or isinstance(capture_tile, Building)
        if not valid_square:
            return False
        if self.is_rogue:
            return self.rogue_can_capture(r, c, engine, capture_tile)
        if self.is_cavalry:
            return self.cavalry_can_capture(r, c, engine, capture_tile)
        if self.is_general:
            return self.general_can_capture(r, c, engine, capture_tile)
        return self.default_can_capture(r, c, engine, capture_tile)

    def general_can_capture(self, r, c, engine, capture_tile):
        if engine.can_be_legally_occupied_by_rogue(r, c):
            if self.color != capture_tile.get_color():
                if not engine.board[r][c].is_protected():
                    return True
                else:
                    if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                        return True

    def cavalry_can_capture(self, r, c, engine, capture_tile):
        if engine.can_be_legally_occupied(r, c):
            if self.color != capture_tile.get_color():
                if not engine.board[r][c].is_protected():
                    return True
                else:
                    if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                        return True

    def rogue_can_capture(self, r, c, engine, capture_tile):
        if engine.can_be_legally_occupied_by_rogue(r, c):
            if self.color != capture_tile.get_color():
                if not capture_tile.is_wall:
                    if not engine.board[r][c].is_protected():
                        return True
                    else:
                        if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                            return True

    def default_can_capture(self, r, c, engine, capture_tile):
        if engine.can_be_legally_occupied(r, c):
            if self.color != capture_tile.get_color():
                if not capture_tile.is_wall:
                    if not engine.board[r][c].is_protected():
                        return True
                    else:
                        if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                            return True

    def persuader_squares(self, engine):
        return []

    def mining_squares(self, engine):
        return []

    def interceptor_squares(self, engine):
        return []

    def capture_squares(self, engine):
        return []

    def stealing_squares(self, engine):
        return []

    def praying_squares(self, engine):
        return []

    def move_squares(self, engine):
        return []

    def spawn_squares(self, engine):
        return []

    def ritual_squares(self, engine):
        return []

    def get_position(self):
        return self.row, self.col

    def change_pos(self, row, col):
        self.row = row
        self.col = col

    def draw_highlights(self, win):
        if self.purchasing:
            self.highlight_self_square(win)
            self.highlight_spawn_squares(win)
        if self.selected:
            self.highlight_self_square(win)
            self.highlight_move_squares(win)
            self.highlight_capture_squares(win)
        if self.pre_selected:
            self.highlight_self_square(win)
            self.highlight_spawn_squares(win)
        if self.unused_piece_highlight:
            self.highlight_self_square_unused(win)
        if self.mining:
            self.highlight_self_square(win)
            self.highlight_mining_squares(win)
        if self.praying:
            self.highlight_self_square(win)
            self.highlight_praying_squares(win)
        if self.casting:
            self.highlight_self_square(win)
        if self.mining_stealing:
            self.highlight_self_square(win)
            self.highlight_stealing_squares(win)
            self.highlight_mining_squares(win)
        if self.praying_building:
            self.highlight_self_square(win)
            self.highlight_spawn_squares(win)
            self.highlight_praying_squares(win)
        if self.stealing:
            self.highlight_self_square(win)
            self.highlight_stealing_squares(win)
        if self.persuading:
            self.highlight_self_square(win)
            self.highlight_persuader_squares(win)
        if self.actions_remaining == 0:
            self.unused_piece_highlight = False

    def draw(self, win):
        sprite = self.sprites[self.color + "_" + str(self)]
        x = (self.col * Constant.SQ_SIZE) + self.offset[0]
        y = (self.row * Constant.SQ_SIZE) + self.offset[1]
        win.blit(sprite, (x, y))

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

    def highlight_spawn_squares(self, win):
        self.draw_squares_in_list(win, self.spawn_squares_list, self.move_square_color)

    def highlight_stealing_squares(self, win):
        self.draw_squares_in_list(win, self.stealing_squares_list, self.move_square_color)

    def highlight_praying_squares(self, win):
        self.draw_squares_in_list(win, self.praying_squares_list, self.move_square_color)

    def highlight_mining_squares(self, win):
        self.draw_squares_in_list(win, self.mining_squares_list, self.move_square_color)

    def highlight_move_squares(self, win):
        self.draw_squares_in_list(win, self.move_squares_list, self.move_square_color)

    def highlight_ritual_squares(self, win):
        self.draw_squares_in_list(win, self.ritual_squares_list, self.move_square_color)

    def highlight_capture_squares(self, win):
        self.draw_squares_in_list(win, self.capture_squares_list, self.move_square_color)

    def highlight_persuader_squares(self, win):
        self.draw_squares_in_list(win, self.persuader_squares_list, self.move_square_color)

    def get_additional_piece_limit(self):
        return self.additional_piece_limit

    def get_additional_actions(self):
        return self.additional_actions

    def get_population_value(self):
        return Constant.PIECE_POPULATION[str(self)]

    def get_sprite_offset(self):
        # if random.randint(1, 2) > 1:
        #     r = random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
        #     z = random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
        #     return r, z
        # else:
        return Constant.PIECE_IMAGE_MODIFY[str(self)]['OFFSET']

    def get_color(self):
        return self.color

    def can_spawn(self, engine):
        spawn_list = Constant.SPAWN_LISTS[str(self)]
        legal_spawns = []
        for spawn in spawn_list:
            if engine.is_legal_spawn(spawn):
                legal_spawns.append(spawn)
        if legal_spawns:
            return True


class Building(Unit):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.can_be_persuaded = False
        self.is_effected_by_jester = False

    def base_spawn_criteria(self, engine, row, col):
        if Constant.tile_in_bounds(row, col):
            return not engine.board[row][col].is_protected_by_opposite_color(self.color)

    def get_unit_kind(self):
        return 'building'

    def right_click(self, engine):
        if self.actions_remaining > 0 and engine.players[engine.turn].actions_remaining > 0:
            return True


class Piece(Unit):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

    def get_unit_kind(self):
        return 'piece'

    def general_move_criteria(self, engine, r, c):
        if engine.can_be_legally_occupied_by_gold_general(r, c):
            if engine.board[r][c].is_protected_by_opposite_color(self.color):
                return False
            return True

    def rogue_move_criteria(self, engine, r, c):
        if engine.can_be_occupied_by_rogue(r, c):
            if engine.board[r][c].is_protected_by_opposite_color(self.color):
                return False
            return True

    def base_move_criteria(self, engine, r, c):
        if engine.can_be_occupied(r, c):
            if engine.board[r][c].is_protected_by_opposite_color(self.color):
                return False
            return True

    def right_click(self, engine):
        if self.actions_remaining > 0:
            return True


class King(Piece):
    def __repr__(self):
        return 'king'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.move_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                Constant.DOWN_LEFT)

    def capture_squares(self, engine):
        squares = []
        for direction in self.move_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))
        return squares

    def move_squares(self, engine):
        squares = []
        for direction in self.move_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))
        return squares

    def right_click(self, engine):
        return engine.create_king_menu(self.row, self.col)


class Queen(Piece):
    def __repr__(self):
        return 'queen'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
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
        if super().right_click(engine) and engine.players[self.color].actions_remaining > 0:
            return engine.create_queen_menu(self.row, self.col)


class Duke(Piece):
    def __repr__(self):
        return 'duke'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def praying_squares(self, engine):
        moves = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[0]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    moves.append((r, c))

        return moves

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
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
            if not engine.rituals_banned:
                return engine.transfer_to_praying_state(self.row, self.col)


class Lion(Piece):
    def __repr__(self):
        return 'lion'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT)
        self.praying_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def praying_squares(self, engine):
        moves = []

        for direction in range(len(self.praying_directions)):
            d = self.praying_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    moves.append((r, c))

        return moves

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares


class Rook(Piece):
    def __repr__(self):
        return 'rook'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT)
        self.praying_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def praying_squares(self, engine):
        moves = []

        for direction in range(len(self.praying_directions)):
            d = self.praying_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    moves.append((r, c))

        return moves

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
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
            if not engine.rituals_banned:
                return engine.transfer_to_praying_state(self.row, self.col)


class Acrobat(Piece):
    def __repr__(self):
        return 'bishop'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT, Constant.UP_RIGHT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares


class Bishop(Piece):
    def __repr__(self):
        return 'bishop'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT, Constant.UP_RIGHT)
        self.praying_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def praying_squares(self, engine):
        moves = []

        for direction in range(len(self.praying_directions)):
            d = self.praying_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    moves.append((r, c))

        return moves

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
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
            if not engine.rituals_banned:
                return engine.transfer_to_praying_state(self.row, self.col)


class Knight(Piece):
    def __repr__(self):
        return 'knight'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.distance = 1
        self.is_cavalry = True

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        return squares


class Pawn(Piece):
    def __repr__(self):
        return 'pawn'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.mining_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                  Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                  Constant.DOWN_LEFT)
        self.move_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN)
        self.capture_directions = (Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.move_distance = 3
        self.capture_distance = 1

    def mining_squares(self, engine):
        mining_squares = []
        for direction in self.mining_directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if engine.has_mineable_resource(r, c):
                if engine.get_occupying(r, c):
                    if engine.get_occupying_color(r, c) is not self.color:
                        pass
                    elif engine.get_occupying_color(r, c) is self.color:
                        mining_squares.append((r, c))
                elif engine.has_none_occupying(r, c):
                    mining_squares.append((r, c))
            elif engine.can_contain_quarry(r, c) and engine.is_empty(r, c):
                mining_squares.append((r, c))

        return mining_squares

    def capture_squares(self, engine):
        squares = []

        for direction in self.capture_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
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
            return engine.transfer_to_mining_state(self.row, self.col)


class RogueRook(Piece):
    def __repr__(self):
        return 'rogue_rook'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                    Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                    Constant.DOWN_LEFT)
        self.is_rogue = True

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.rogue_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.rogue_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares

    def stealing_squares(self, engine):
        squares = []

        for direction in self.stealing_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_stealing_state(self.row, self.col)


class RogueBishop(Piece):
    def __repr__(self):
        return 'rogue_bishop'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                    Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                    Constant.DOWN_LEFT)
        self.directions = (Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT, Constant.UP_RIGHT)

        self.distance = Constant.BOARD_WIDTH_SQ
        self.is_rogue = True

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.rogue_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.rogue_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares

    def stealing_squares(self, engine):
        squares = []

        for direction in range(len(self.stealing_directions)):
            d = self.stealing_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_stealing_state(self.row, self.col)


class RogueKnight(Piece):
    def __repr__(self):
        return 'rogue_knight'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                    Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                    Constant.DOWN_LEFT)
        self.distance = 1
        self.is_rogue = True

    def stealing_squares(self, engine):
        squares = []

        for direction in self.stealing_directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.rogue_move_criteria(engine, r, c):
                squares.append((r, c))

        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_stealing_state(self.row, self.col)


class RoguePawn(Piece):
    def __repr__(self):
        return 'rogue_pawn'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.mining_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                  Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                  Constant.DOWN_LEFT)
        self.move_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN)
        self.capture_directions = (Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                    Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                    Constant.DOWN_LEFT)
        self.move_distance = 3
        self.capture_distance = 1

        self.is_rogue = True

    def mining_squares(self, engine):
        mining_squares = []
        for direction in self.mining_directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if engine.has_mineable_resource(r, c):
                if engine.get_occupying(r, c):
                    if engine.get_occupying_color(r, c) is not self.color:
                        pass
                    elif engine.get_occupying_color(r, c) is self.color:
                        mining_squares.append((r, c))
                elif engine.has_none_occupying(r, c):
                    mining_squares.append((r, c))
            elif engine.can_contain_quarry(r, c) and engine.is_empty(r, c):
                mining_squares.append((r, c))

        return mining_squares

    def capture_squares(self, engine):
        squares = []

        for direction in self.capture_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
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
                if not self.rogue_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares

    def stealing_squares(self, engine):
        squares = []

        for direction in range(len(self.stealing_directions)):
            d = self.stealing_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_stealing_mining_state(self.row, self.col)


class Monk(Piece):
    def __repr__(self):
        return 'monk'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = 1

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

    def right_click(self, engine):
        if self.actions_remaining > 0 and engine.players[engine.turn].actions_remaining > 0:
            if not engine.rituals_banned:
                return engine.transfer_to_praying_building_state(self.row, self.col)


class Ram(Piece):
    def __repr__(self):
        return 'ram'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.TWO_UP_RIGHT, Constant.TWO_UP_LEFT, Constant.TWO_RIGHT_UP,
                           Constant.TWO_RIGHT_DOWN, Constant.TWO_LEFT_UP, Constant.TWO_LEFT_DOWN,
                           Constant.TWO_DOWN_LEFT, Constant.TWO_DOWN_RIGHT)
        self.is_cavalry = True
        self.extra_move_directions = {Constant.TWO_UP_RIGHT: Constant.UP_RIGHT,
                                      Constant.TWO_UP_LEFT: Constant.UP_LEFT,
                                      Constant.TWO_RIGHT_UP: Constant.UP_RIGHT,
                                      Constant.TWO_RIGHT_DOWN: Constant.DOWN_RIGHT,
                                      Constant.TWO_LEFT_UP: Constant.UP_LEFT,
                                      Constant.TWO_LEFT_DOWN: Constant.DOWN_LEFT,
                                      Constant.TWO_DOWN_LEFT: Constant.DOWN_LEFT,
                                      Constant.TWO_DOWN_RIGHT: Constant.DOWN_RIGHT, }

        self.distance = Constant.BOARD_WIDTH_SQ

    def capture_squares(self, engine):
        squares = []
        for direction in self.directions:
            for distance in range(0, Constant.BOARD_WIDTH_SQ):
                d = self.extra_move_directions[direction]
                r = self.row + direction[0] + d[0] * distance
                c = self.col + direction[1] + d[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []
        for direction in self.directions:
            for distance in range(0, Constant.BOARD_WIDTH_SQ):
                d = self.extra_move_directions[direction]
                r = self.row + direction[0] + d[0] * distance
                c = self.col + direction[1] + d[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))

        return squares


class Elephant(Piece):
    def __repr__(self):
        return 'elephant'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN,
            Constant.THREE_UP_RIGHT, Constant.THREE_RIGHT_UP, Constant.THREE_DOWN_RIGHT, Constant.THREE_RIGHT_DOWN,
            Constant.THREE_UP_LEFT, Constant.THREE_LEFT_UP, Constant.THREE_DOWN_LEFT, Constant.THREE_LEFT_DOWN)
        self.distance = 1
        self.is_cavalry = True

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        return squares


class Jester(Piece):
    def __repr__(self):
        return 'jester'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares

    def interceptor_squares(self, engine):
        squares = []
        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if engine.has_occupying(r, c):

                squares.append((r, c))

        return squares


class Doe(Piece):
    def __repr__(self):
        return 'doe'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.knight_directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.bishop_directions = (Constant.UP_LEFT, Constant.UP_RIGHT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ
        self.is_cavalry = True

    def capture_squares(self, engine):
        squares = []

        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        for direction in self.bishop_directions:
            for i in range(1, self.distance):
                r = self.row + direction[0] * i
                c = self.col + direction[1] * i
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        for direction in self.bishop_directions:
            for i in range(1, self.distance):
                r = self.row + direction[0] * i
                c = self.col + direction[1] * i
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))

        return squares


class Pikeman(Piece):
    def __repr__(self):
        return 'pikeman'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.is_cavalry = True
        self.distance = 1

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        return squares


class Builder(Piece):
    def __repr__(self):
        return 'builder'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)

        self.distance = 1

    def move_squares(self, engine):
        moves = []
        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.base_move_criteria(engine, r, c):
                moves.append((r, c))
        return moves

    def base_spawn_criteria(self, engine, row, col):
        if Constant.tile_in_bounds(row, col):
            return engine.has_none_occupying(row, col) and not engine.has_portal(row, col) and not engine.has_trap(row, col)

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

    def right_click(self, engine):
        if super().right_click(engine):
            if engine.players[engine.turn].actions_remaining > 0:
                return engine.transfer_to_building_state(self.row, self.col)


class Unicorn(Piece):
    def __repr__(self):
        return 'unicorn'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.is_cavalry = True
        self.knight_directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)

        self.cardinal_directions = (Constant.THREE_RIGHT, Constant.THREE_DOWN, Constant.THREE_UP, Constant.THREE_LEFT)
        self.knight_directions_to_extra_moves = {Constant.TWO_UP_RIGHT: Constant.TWO_RIGHT_UP,
                                                 Constant.TWO_RIGHT_UP: Constant.TWO_UP_RIGHT,
                                                 Constant.TWO_DOWN_RIGHT: Constant.TWO_RIGHT_DOWN,
                                                 Constant.TWO_RIGHT_DOWN: Constant.TWO_DOWN_RIGHT,
                                                 Constant.TWO_UP_LEFT: Constant.TWO_LEFT_UP,
                                                 Constant.TWO_LEFT_UP: Constant.TWO_UP_LEFT,
                                                 Constant.TWO_DOWN_LEFT: Constant.TWO_LEFT_DOWN,
                                                 Constant.TWO_LEFT_DOWN: Constant.TWO_DOWN_LEFT}
        self.distance = 1

    def capture_squares(self, engine):
        squares = []

        for direction in self.cardinal_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

            elif engine.can_be_occupied(r, c):
                extra_move_direction = self.knight_directions_to_extra_moves[direction]
                r += extra_move_direction[0]
                c += extra_move_direction[1]
                if self.can_capture(r, c, engine):
                    squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.cardinal_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))
                extra_move_direction = self.knight_directions_to_extra_moves[direction]
                r += extra_move_direction[0]
                c += extra_move_direction[1]
                if self.base_move_criteria(engine, r, c):
                    if (r, c) not in squares:
                        squares.append((r, c))

        return squares


class Champion(Piece):
    def __repr__(self):
        return 'champion'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.praying_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.extra_move_directions = {Constant.UP_RIGHT: (Constant.UP, Constant.RIGHT),
                                      Constant.UP_LEFT: (Constant.UP, Constant.LEFT),
                                      Constant.DOWN_RIGHT: (Constant.DOWN, Constant.RIGHT),
                                      Constant.DOWN_LEFT: (Constant.DOWN, Constant.LEFT), }

        self.distance = Constant.BOARD_WIDTH_SQ

    def praying_squares(self, engine):
        moves = []

        for direction in range(len(self.praying_directions)):
            d = self.praying_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    moves.append((r, c))

        return moves

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            extra_directions = self.extra_move_directions[direction]
            for extra_direction in extra_directions:
                for distance in range(0, self.distance):
                    r = self.row + direction[0] + extra_direction[0] * distance
                    c = self.col + direction[1] + extra_direction[1] * distance
                    if not Constant.tile_in_bounds(r, c):
                        break
                    if self.can_capture(r, c, engine):
                        if (r, c) not in squares:
                            squares.append((r, c))
                            break
                    if not self.base_move_criteria(engine, r, c):
                        break
        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            extra_directions = self.extra_move_directions[direction]
            for extra_direction in extra_directions:
                for distance in range(0, self.distance):
                    r = self.row + direction[0] + extra_direction[0] * distance
                    c = self.col + direction[1] + extra_direction[1] * distance
                    if not Constant.tile_in_bounds(r, c):
                        break
                    if not self.base_move_criteria(engine, r, c):
                        break
                    else:
                        if (r, c) not in squares:
                            squares.append((r, c))
        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            if not engine.rituals_banned:
                return engine.transfer_to_praying_state(self.row, self.col)


class Oxen(Piece):
    def __repr__(self):
        return 'oxen'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.is_cavalry = True

        self.extra_move_directions = {Constant.TWO_UP_RIGHT: Constant.UP,
                                      Constant.TWO_RIGHT_UP: Constant.RIGHT,
                                      Constant.TWO_DOWN_RIGHT: Constant.DOWN,
                                      Constant.TWO_RIGHT_DOWN: Constant.RIGHT,
                                      Constant.TWO_UP_LEFT: Constant.UP,
                                      Constant.TWO_LEFT_UP: Constant.LEFT,
                                      Constant.TWO_DOWN_LEFT: Constant.DOWN,
                                      Constant.TWO_LEFT_DOWN: Constant.LEFT}

        self.distance = Constant.BOARD_WIDTH_SQ

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            extra_direction = self.extra_move_directions[direction]
            for distance in range(0, self.distance):
                r = self.row + direction[0] + extra_direction[0] * distance
                c = self.col + direction[1] + extra_direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    if (r, c) not in squares:
                        squares.append((r, c))
                        break
                if not self.base_move_criteria(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            extra_direction = self.extra_move_directions[direction]
            for distance in range(0, self.distance):
                r = self.row + direction[0] + extra_direction[0] * distance
                c = self.col + direction[1] + extra_direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.base_move_criteria(engine, r, c):
                    break
                else:
                    if (r, c) not in squares:
                        squares.append((r, c))

        return squares


class Persuader(Piece):
    def __repr__(self):
        return 'persuader'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ

    def persuader_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.can_capture(r, c, engine):
                if engine.get_occupying(r, c).can_be_persuaded:
                    squares.append((r, c))

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
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
            if engine.players[engine.turn].actions_remaining > 0:
                return engine.transfer_to_persuading_state(self.row, self.col)


class GoldGeneral(Piece):
    def __repr__(self):
        return 'gold_general'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = Constant.BOARD_WIDTH_SQ
        self.praying_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT)
        self.is_general = True
        self.can_be_persuaded = False

    def praying_squares(self, engine):
        squares = []

        for direction in self.praying_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    squares.append((r, c))
        return squares

    def capture_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if self.can_capture(r, c, engine):
                    squares.append((r, c))
                    break
                if not self.general_move_critera(engine, r, c):
                    break

        return squares

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            for distance in range(1, self.distance):
                r = self.row + direction[0] * distance
                c = self.col + direction[1] * distance
                if not Constant.tile_in_bounds(r, c):
                    break
                if not self.general_move_criteria(engine, r, c):
                    break
                else:
                    squares.append((r, c))
        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            if not engine.rituals_banned:
                return engine.transfer_to_building_state(self.row, self.col)


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
            return not engine.has_trap(row, col) and not engine.board[row][col].is_protected_by_opposite_color(self.color)

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


class Trader(Piece):
    def __repr__(self):
        return 'trader'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)

    def move_squares(self, engine):
        squares = []

        for direction in self.directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if self.base_move_criteria(engine, r, c):
                squares.append((r, c))

        return squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.create_trader_menu(self.row, self.col)


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

    def spawn_squares(self, engine):
        spawn_squares = []

        if not self.can_spawn(engine):
            return spawn_squares

        for direction in self.directions:
            r = self.row - direction[0]
            c = self.col - direction[1]
            if self.base_spawn_criteria(engine, r, c):
                if engine.can_be_occupied_by_rogue(r, c):
                    spawn_squares.append((r, c))
        return spawn_squares

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_building_state(self.row, self.col)


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
                if self.base_spawn_criteria(engine, r, c):
                    if engine.can_be_occupied_by_gold_general(r, c):
                        ritual_squares.append((r, c))

        return ritual_squares

    def right_click(self, engine):
        if super().right_click(engine):
            if not engine.rituals_banned:
                self.casting = True
                return engine.create_ritual_menu(self.row, self.col, engine.monolith_rituals[engine.turn_count_actual])


class Trap(Building):
    def __repr__(self):
        return 'trap'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)

    def highlight_self_square_unused(self, win):
        pass


class Wall(Building):
    def __repr__(self):
        return 'wall'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.is_wall = True

    def highlight_self_square_unused(self, win):
        pass
