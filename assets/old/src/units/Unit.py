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
        self.display_moves = False

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
        if self.display_moves:
            self.highlight_self_square(win)
            self.highlight_move_squares(win)
            self.highlight_capture_squares(win)

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
        return 'buildings'

    def right_click(self, engine):
        if self.actions_remaining > 0:
            if engine.players[engine.turn].actions_remaining > 0:
                return True
            else:
                engine.set_popup_reason('player_action')
        else:
            engine.set_popup_reason('piece_action')


class Piece(Unit):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

    def get_unit_kind(self):
        return 'pieces'

    def general_move_criteria(self, engine, r, c):
        if engine.can_be_occupied_by_gold_general(r, c):
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
        else:
            engine.set_popup_reason('piece_action')
