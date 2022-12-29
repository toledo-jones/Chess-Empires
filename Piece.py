from Building import *
import random

class Piece:
    def __repr__(self):
        return 'none'

    def __init__(self, r, c, color='none'):
        self.row = r
        self.col = c
        self.color = color
        self.offset = self.get_piece_offset()

        self.purchasing = False
        self.mining = False
        self.selected = False
        self.pre_selected = False
        self.unused_piece_highlight = False
        self.praying = False
        self.casting = False
        self.stealing = False
        self.mining_stealing = False

        self.intercepted = False
        self.is_rogue = False
        self.is_general = False

        self.additional_actions = 0
        self.actions_remaining = 0

        self.praying_squares_list = []
        self.spawn_squares_list = []
        self.move_squares_list = []
        self.mining_squares_list = []
        self.interceptor_squares_list = []
        self.stealing_squares_list = []
        self.ritual_squares_list = []
        self.capture_squares_list = []

        self.population_value = 1
        self.additional_piece_limit = 0

        self.square = pygame.Surface((Constant.SQ_SIZE, Constant.SQ_SIZE))
        self.self_selected_square_color = Constant.SELF_SQUARE_HIGHLIGHT_COLOR
        self.unused_square_color = Constant.UNUSED_PIECE_HIGHLIGHT_COLOR
        self.move_square_color = Constant.MOVE_SQUARE_HIGHLIGHT_COLOR
        self.is_effected_by_jester = True

    def possible_moves(self):
        return {'spawn': self.spawn_squares_list, 'move': self.move_squares_list, 'mine': self.mining_squares_list,
                'steal': self.stealing_squares_list, 'pray': self.praying_squares_list}

    def can_capture(self, r, c, engine):
        capture_tile = None
        if Constant.tile_in_bounds(r, c):
            capture_tile = engine.board[r][c].get_occupying()
        valid_square = isinstance(capture_tile, Piece) or isinstance(capture_tile, Building)
        if valid_square:
            if engine.can_be_legally_occupied(r, c):
                if self.color != capture_tile.get_color():
                    if not engine.board[r][c].is_protected():
                        return True
                    else:
                        if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                            return True

    def mining_squares(self, engine):
        return []

    def interceptor_squares(self, engine):
        return []

    def draw_highlights(self, win):
        if self.purchasing:
            self.highlight_self_square(win)
            self.highlight_spawn_squares(win)
        if self.selected:
            self.highlight_self_square(win)
            self.highlight_move_squares(win)
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
        if self.stealing:
            self.highlight_self_square(win)
            self.highlight_stealing_squares(win)
        if self.actions_remaining == 0:
            self.unused_piece_highlight = False

    def draw(self, win):
        if self.color == "w":
            draw_this = Constant.W_PIECES['w_' + str(self)]
        elif self.color == "b":
            draw_this = Constant.B_PIECES['b_' + str(self)]
        x = (self.col * Constant.SQ_SIZE) + self.offset[0]
        y = (self.row * Constant.SQ_SIZE) + self.offset[1]
        win.blit(draw_this, (x, y))

    def get_position(self):
        return self.row, self.col

    def change_pos(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        return self.color

    def update_mining_squares(self, engine):
        self.mining_squares_list = self.mining_squares(engine)

    def update_move_squares(self, engine):
        self.move_squares_list = self.valid_moves(engine)

    def update_spawn_squares(self, engine):
        self.spawn_squares_list = self.spawn_squares(engine)

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

    def spawn_squares(self, engine):
        return []

    def get_additional_piece_limit(self):
        return self.additional_piece_limit

    def get_additional_actions(self):
        return self.additional_actions

    def get_population_value(self):
        return Constant.PIECE_POPULATION[str(self)]

    def update_praying_squares(self, engine):
        self.praying_squares_list = self.praying_squares(engine)

    def update_stealing_squares(self, engine):
        self.stealing_squares_list = self.stealing_squares(engine)

    def stealing_squares(self, engine):
        return []

    def update_interceptor_squares(self, engine):
        self.interceptor_squares_list = self.interceptor_squares(engine)

    def praying_squares(self, engine):
        return []

    def get_piece_offset(self):
        if random.randint(1, 2) > 1:
            r = random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
            z = random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
            return r, z
        else:
            return Constant.PIECE_IMAGE_MODIFY[str(self)]['OFFSET']

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

        self.spawn_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN)

        self.distance = 1

    def valid_moves(self, engine):
        moves = []

        for direction in range(len(self.move_directions)):
            d = self.move_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied(r, c) or self.can_capture(r, c, engine):
                moves.append((r, c))

        return moves

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
        self.distance = -1

    def valid_moves(self, engine):
        c = self.col
        r = self.row
        moves = []
        # UP DIAGONALS
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1

        # DOWN DIAGONALS
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1
        # UP
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break

        # DOWN
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ, 1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break

        # LEFT
        for c2 in range(c - 1, -1, -1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break

        # RIGHT
        for c2 in range(c + 1, Constant.BOARD_WIDTH_SQ, 1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break

        return moves


class Duke(Piece):
    def __repr__(self):
        return 'duke'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = -1

    def praying_squares(self, engine):
        moves = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    moves.append((r, c))

        return moves

    def valid_moves(self, engine):
        c = self.col
        r = self.row
        moves = []
        # UP DIAGONALS
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1

        # DOWN DIAGONALS
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1
        # UP
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break

        # DOWN
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ, 1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break

        # LEFT
        for c2 in range(c - 1, -1, -1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break

        # RIGHT
        for c2 in range(c + 1, Constant.BOARD_WIDTH_SQ, 1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break

        return moves

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_praying_state(self.row, self.col)


class Rook(Piece):
    def __repr__(self):
        return 'rook'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT)
        self.praying_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = -1

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

    def valid_moves(self, engine):
        c = self.col
        r = self.row
        moves = []

        # UP
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break

        # DOWN
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ, 1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break
        # LEFT
        for c2 in range(c - 1, -1, -1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break

        # RIGHT
        for c2 in range(c + 1, Constant.BOARD_WIDTH_SQ, 1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break
        return moves

    def right_click(self, engine):
        super().right_click(engine)
        return engine.transfer_to_praying_state(self.row, self.col)


class Bishop(Piece):
    def __repr__(self):
        return 'bishop'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT, Constant.UP_RIGHT)
        self.praying_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = -1

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

    def valid_moves(self, engine):
        r = self.row
        c = self.col
        moves = []

        # UP
        c3 = c - 1
        c2 = c + 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1

        # DOWN
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1

        return moves

    def right_click(self, engine):
        if super().right_click(engine):
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

    def valid_moves(self, engine):
        moves = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied(r, c) or self.can_capture(r, c, engine):
                moves.append((r, c))

        return moves


class Pawn(Piece):
    def __repr__(self):
        return 'pawn'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.mining_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                  Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                  Constant.DOWN_LEFT)
        self.distance = 1

    def mining_squares(self, engine):
        mining_squares = []
        for direction in range(len(self.mining_directions)):
            d = self.mining_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_mineable_resource(r, c):
                if engine.get_occupying(r, c):
                    if engine.get_occupying_color(r, c) is not self.color:
                        pass
                    elif engine.get_occupying_color(r, c) is self.color:
                        mining_squares.append((r, c))
                elif engine.has_none_occupying(r, c):
                    mining_squares.append((r, c))

        return mining_squares

    def valid_moves(self, engine):
        c = self.col
        r = self.row

        moves = []
        # UP
        for r2 in range(r - 1, r - 3, -1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            else:
                break

        # DOWN
        for r2 in range(r + 1, r + 3, 1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            else:
                break

        # LEFT
        for c2 in range(c - 1, c - 3, -1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            else:
                break

        # RIGHT
        for c2 in range(c + 1, c + 3, 1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            else:
                break

        # UP RIGHT
        c2 = c + 1
        r2 = r + 1
        if Constant.tile_in_bounds(r2, c2):
            if self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
        # UP LEFT
        c2 = c - 1
        r2 = r - 1
        if Constant.tile_in_bounds(r2, c2):
            if self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
        # DOWN LEFT
        c2 = c + 1
        r2 = r - 1
        if Constant.tile_in_bounds(r2, c2):
            if self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
        # DOWN RIGHT
        c2 = c - 1
        r2 = r + 1
        if Constant.tile_in_bounds(r2, c2):
            if self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
        return moves

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_mining_state(self.row, self.col)


class RogueRook(Piece):
    def __repr__(self):
        return 'rogue_rook'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = ()
        self.distance = 0
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.is_rogue = True

    def valid_moves(self, engine):
        c = self.col
        r = self.row
        moves = []

        # UP
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied_by_rogue(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break

        # DOWN
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ, 1):
            if engine.can_be_occupied_by_rogue(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break
        # LEFT
        for c2 in range(c - 1, -1, -1):
            if engine.can_be_occupied_by_rogue(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break

        # RIGHT
        for c2 in range(c + 1, Constant.BOARD_WIDTH_SQ, 1):
            if engine.can_be_occupied_by_rogue(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break
        return moves

    def can_capture(self, r, c, engine):
        capture_tile = None
        if Constant.tile_in_bounds(r, c):
            capture_tile = engine.board[r][c].get_occupying()
        valid_square = isinstance(capture_tile, Piece) or isinstance(capture_tile, Building)
        if valid_square:
            if engine.can_be_legally_occupied_by_rogue(r, c):
                if self.color != capture_tile.get_color():
                    if not engine.board[r][c].is_protected():
                        return True
                    else:
                        if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                            return True

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


class RogueBishop(Piece):
    def __repr__(self):
        return 'rogue_bishop'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.distance = 0
        self.is_rogue = True

    def valid_moves(self, engine):
        r = self.row
        c = self.col
        moves = []

        # UP
        c3 = c - 1
        c2 = c + 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied_by_rogue(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied_by_rogue(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1

        # DOWN
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied_by_rogue(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied_by_rogue(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1

        return moves

    def can_capture(self, r, c, engine):
        capture_tile = None
        if Constant.tile_in_bounds(r, c):
            capture_tile = engine.board[r][c].get_occupying()
        valid_square = isinstance(capture_tile, Piece) or isinstance(capture_tile, Building)
        if valid_square:
            if engine.can_be_legally_occupied_by_rogue(r, c):
                if self.color != capture_tile.get_color():
                    if not engine.board[r][c].is_protected():
                        return True
                    else:
                        if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                            return True

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

        for direction in range(len(self.stealing_directions)):
            d = self.stealing_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if self.can_capture(r, c, engine):
                squares.append((r, c))

        return squares

    def valid_moves(self, engine):
        moves = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied_by_rogue(r, c) or self.can_capture(r, c, engine):
                moves.append((r, c))

        return moves

    def can_capture(self, r, c, engine):
        capture_tile = None
        if Constant.tile_in_bounds(r, c):
            capture_tile = engine.board[r][c].get_occupying()
        valid_square = isinstance(capture_tile, Piece) or isinstance(capture_tile, Building)
        if valid_square:
            if engine.can_be_legally_occupied_by_rogue(r, c):
                if self.color != capture_tile.get_color():
                    if not engine.board[r][c].is_protected():
                        return True
                    else:
                        if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                            return True

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
        self.stealing_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)
        self.distance = 0
        self.is_rogue = True

    def mining_squares(self, engine):
        mining_squares = []
        for direction in range(len(self.mining_directions)):
            d = self.mining_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_mineable_resource(r, c):
                if engine.get_occupying(r, c):
                    if engine.get_occupying_color(r, c) is not self.color:
                        pass
                    elif engine.get_occupying_color(r, c) is self.color:
                        mining_squares.append((r, c))
                elif engine.has_none_occupying(r, c):
                    mining_squares.append((r, c))

        return mining_squares

    def valid_moves(self, engine):
        c = self.col
        r = self.row

        moves = []
        # UP
        for r2 in range(r - 1, r - 3, -1):
            if engine.can_be_occupied_by_rogue(r2, c):
                moves.append((r2, c))
            else:
                break

        # DOWN
        for r2 in range(r + 1, r + 3, 1):
            if engine.can_be_occupied_by_rogue(r2, c):
                moves.append((r2, c))
            else:
                break

        # LEFT
        for c2 in range(c - 1, c - 3, -1):
            if engine.can_be_occupied_by_rogue(r, c2):
                moves.append((r, c2))
            else:
                break

        # RIGHT
        for c2 in range(c + 1, c + 3, 1):
            if engine.can_be_occupied_by_rogue(r, c2):
                moves.append((r, c2))
            else:
                break

        # UP RIGHT
        c2 = c + 1
        r2 = r + 1
        if Constant.tile_in_bounds(r2, c2):
            if self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
        # UP LEFT
        c2 = c - 1
        r2 = r - 1
        if Constant.tile_in_bounds(r2, c2):
            if self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
        # DOWN LEFT
        c2 = c + 1
        r2 = r - 1
        if Constant.tile_in_bounds(r2, c2):
            if self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
        # DOWN RIGHT
        c2 = c - 1
        r2 = r + 1
        if Constant.tile_in_bounds(r2, c2):
            if self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
        return moves

    def can_capture(self, r, c, engine):
        capture_tile = None
        if Constant.tile_in_bounds(r, c):
            capture_tile = engine.board[r][c].get_occupying()
        valid_square = isinstance(capture_tile, Piece) or isinstance(capture_tile, Building)
        if valid_square:
            if engine.can_be_legally_occupied_by_rogue(r, c):
                if self.color != capture_tile.get_color():
                    if not engine.board[r][c].is_protected():
                        return True
                    else:
                        if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                            return True

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

    def valid_moves(self, engine):
        moves = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied(r, c):
                moves.append((r, c))

        return moves

    def praying_squares(self, engine):
        moves = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    moves.append((r, c))

        return moves

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_praying_state(self.row, self.col)


class Ram(Piece):
    def __repr__(self):
        return 'ram'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.TWO_UP_RIGHT, Constant.TWO_UP_LEFT, Constant.TWO_RIGHT_UP,
                           Constant.TWO_RIGHT_DOWN, Constant.TWO_LEFT_UP, Constant.TWO_LEFT_DOWN,
                           Constant.TWO_DOWN_LEFT, Constant.TWO_DOWN_RIGHT,)
        self.distance = -1

    def valid_moves(self, engine):
        moves = []
        for d in self.directions:
            r = self.row
            c = self.col
            r += d[0]
            c += d[1]
            c2 = c
            if r > self.row and c < self.col:
                # down left
                for r2 in range(r, Constant.BOARD_HEIGHT_SQ):
                    if engine.can_be_occupied(r2, c2):
                        moves.append((r2, c2))
                    elif self.can_capture(r2, c2, engine):
                        moves.append((r2, c2))
                        break
                    else:
                        break
                    c2 -= 1
            elif r > self.row and c > self.col:
                # down right
                for r2 in range(r, Constant.BOARD_HEIGHT_SQ):
                    if engine.can_be_occupied(r2, c2):
                        moves.append((r2, c2))
                    elif self.can_capture(r2, c2, engine):
                        moves.append((r2, c2))
                        break
                    else:
                        break
                    c2 += 1
            elif r < self.row and c > self.col:
                # up right
                for r2 in range(r, -1, -1):
                    if engine.can_be_occupied(r2, c2):
                        moves.append((r2, c2))
                    elif self.can_capture(r2, c2, engine):
                        moves.append((r2, c2))
                        break
                    else:
                        break
                    c2 += 1
            elif r < self.row and c < self.col:
                # up left
                for r2 in range(r, -1, -1):
                    if engine.can_be_occupied(r2, c2):
                        moves.append((r2, c2))
                    elif self.can_capture(r2, c2, engine):
                        moves.append((r2, c2))
                        break
                    else:
                        break
                    c2 -= 1
        return moves


class Champion(Piece):
    def __repr__(self):
        return 'champion'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = ()
        self.distance = -1

    def valid_moves(self, engine):
        r = self.row
        c = self.col

        return []


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

    def valid_moves(self, engine):
        moves = []

        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied(r, c) or self.can_capture(r, c, engine):
                moves.append((r, c))

        return moves


class Jester(Piece):
    def __repr__(self):
        return 'jester'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = ()
        self.distance = 0

    def valid_moves(self, engine):
        c = self.col
        r = self.row
        moves = []
        # UP DIAGONALS
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                break
            else:
                break
            c2 += 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                break
            else:
                break
            c3 -= 1

        # DOWN DIAGONALS
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                break
            else:
                break
            c2 += 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                break
            else:
                break
            c3 -= 1
        # UP
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                break
            else:
                break

        # DOWN
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ, 1):
            if engine.can_be_occupied(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                break
            else:
                break

        # LEFT
        for c2 in range(c - 1, -1, -1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                break
            else:
                break

        # RIGHT
        for c2 in range(c + 1, Constant.BOARD_WIDTH_SQ, 1):
            if engine.can_be_occupied(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                break
            else:
                break

        return moves

    def interceptor_squares(self, engine):
        r = self.row
        c = self.col

        moves = []

        RIGHT = (r, c + 1)
        LEFT = (r, c - 1)
        UP = (r - 1, c)
        DOWN = (r + 1, c)
        UP_RIGHT = (r - 1, c + 1)
        UP_LEFT = (r - 1, c - 1)
        DOWN_RIGHT = (r + 1, c + 1)
        DOWN_LEFT = (r + 1, c - 1)

        valid_moves = [RIGHT, LEFT, UP, DOWN, UP_RIGHT, UP_LEFT, DOWN_RIGHT, DOWN_LEFT]

        for move in valid_moves:
            if engine.has_occupying(move[0], move[1]):
                moves.append((move[0], move[1]))

        return moves


class Pikeman(Piece):
    def __repr__(self):
        return 'pikeman'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        self.move_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                Constant.DOWN_LEFT)

        self.spawn_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN)

        self.distance = 1

    def valid_moves(self, engine):
        moves = []

        for direction in range(len(self.move_directions)):
            d = self.move_directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied(r, c) or self.can_capture(r, c, engine):
                moves.append((r, c))

        return moves


class Builder(Piece):
    def __repr__(self):
        return 'builder'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                Constant.DOWN_LEFT)



        self.distance = 1

    def valid_moves(self, engine):
        moves = []
        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.can_be_occupied(r, c):
                moves.append((r, c))
        return moves

    def spawn_squares_for_quarry(self, engine):
        spawn_squares = []
        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_no_resource(r, c) and engine.has_none_occupying(r, c):
                spawn_squares.append((r, c))
        return spawn_squares

    def spawn_squares(self, engine):

        spawn_squares = []
        for direction in range(len(self.directions)):
            d = self.directions[direction]
            r = self.row - d[0]
            c = self.col - d[1]
            if engine.has_no_resource(r, c) and engine.has_none_occupying(r, c):
                spawn_squares.append((r, c))
            elif engine.has_depleted_quarry(r, c) and engine.has_none_occupying(r, c):
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

    def valid_moves(self, engine):
        moves = []

        for direction in self.cardinal_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if engine.can_be_occupied(r, c) or self.can_capture(r, c, engine):
                moves.append((r, c))

        for direction in self.knight_directions:
            r = self.row + direction[0]
            c = self.col + direction[1]
            if engine.can_be_occupied(r, c):
                moves.append((r, c))
                extra_move_direction = self.knight_directions_to_extra_moves[direction]
                r += extra_move_direction[0]
                c += extra_move_direction[1]
                if engine.can_be_occupied(r, c) or self.can_capture(r, c, engine):
                    moves.append((r, c))
            elif self.can_capture(r, c, engine):
                moves.append((r, c))
        return moves


class GoldGeneral(Piece):
    def __repr__(self):
        return 'gold_general'

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                           Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                           Constant.DOWN_LEFT)
        self.distance = -1
        self.knight_directions = (
            Constant.TWO_UP_RIGHT, Constant.TWO_RIGHT_UP, Constant.TWO_DOWN_RIGHT, Constant.TWO_RIGHT_DOWN,
            Constant.TWO_UP_LEFT, Constant.TWO_LEFT_UP, Constant.TWO_DOWN_LEFT, Constant.TWO_LEFT_DOWN)
        self.praying_directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT)
        self.is_general = True

    def praying_squares(self, engine):
        squares = []

        for d in self.praying_directions:
            r = self.row + d[0]
            c = self.col + d[1]
            if engine.has_prayable_building(r, c):
                if engine.get_occupying(r, c).color is self.color:
                    squares.append((r, c))
        return squares

    def valid_moves(self, engine):
        moves = []
        r = self.row
        c = self.col
        # UP DIAGONALS
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied_by_gold_general(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied_by_gold_general(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1

        # DOWN DIAGONALS
        c2 = c + 1
        c3 = c - 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied_by_gold_general(r2, c2):
                moves.append((r2, c2))
            elif self.can_capture(r2, c2, engine):
                moves.append((r2, c2))
                break
            else:
                break
            c2 += 1
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ):
            if engine.can_be_occupied_by_gold_general(r2, c3):
                moves.append((r2, c3))
            elif self.can_capture(r2, c3, engine):
                moves.append((r2, c3))
                break
            else:
                break
            c3 -= 1
        # UP
        for r2 in range(r - 1, -1, -1):
            if engine.can_be_occupied_by_gold_general(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break

        # DOWN
        for r2 in range(r + 1, Constant.BOARD_HEIGHT_SQ, 1):
            if engine.can_be_occupied_by_gold_general(r2, c):
                moves.append((r2, c))
            elif self.can_capture(r2, c, engine):
                moves.append((r2, c))
                break
            else:
                break

        # LEFT
        for c2 in range(c - 1, -1, -1):
            if engine.can_be_occupied_by_gold_general(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break

        # RIGHT
        for c2 in range(c + 1, Constant.BOARD_WIDTH_SQ, 1):
            if engine.can_be_occupied_by_gold_general(r, c2):
                moves.append((r, c2))
            elif self.can_capture(r, c2, engine):
                moves.append((r, c2))
                break
            else:
                break
        return moves

    def can_capture(self, r, c, engine):
        capture_tile = None
        if Constant.tile_in_bounds(r, c):
            capture_tile = engine.board[r][c].get_occupying()
        valid_square = isinstance(capture_tile, Piece) or isinstance(capture_tile, Building)
        if valid_square:
            if engine.can_be_legally_occupied_by_gold_general(r, c):
                if self.color != capture_tile.get_color():
                    if not engine.board[r][c].is_protected():
                        return True
                    else:
                        if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                            return True

    def right_click(self, engine):
        if super().right_click(engine):
            return engine.transfer_to_building_state(self.row, self.col)

class Blank(Piece):
    def __repr__(self):
        return ''

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.directions = ()
        self.distance = 0
