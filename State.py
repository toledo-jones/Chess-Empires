from GameEvent import *
from Menu import *


class State:
    def __init__(self, win, engine):
        self.win = win
        self.engine = engine
        self.side_bar = None

    def type_of_move(self, acting_tile, action_tile):
        piece = acting_tile.get_occupying()
        has_portal = False
        if action_tile.portal:
            has_portal = True
        has_trap = False
        if action_tile.trap:
            has_trap = True
            if action_tile.is_protected_by_same_color(piece.color):
                has_trap = False
        if has_trap:
            if action_tile.trap.color != piece.color:
                return TrapMove
        if has_portal:
            return PortalMove

        return Move

    def type_of_capture(self, acting_tile, action_tile):
        piece = acting_tile.get_occupying()
        has_portal = False
        if action_tile.portal:
            has_portal = True
        has_trap = False
        if action_tile.trap:
            has_trap = True
            if action_tile.is_protected_by_same_color(piece.color):
                has_trap = False
        if has_trap:
            if action_tile.trap.color != piece.color:
                return TrapCapture
        if has_portal:
            return PortalCapture
        return Capture

    def type_of_spawn(self, acting_tile, action_tile):
        piece = acting_tile.get_occupying()
        has_portal = False
        if action_tile.portal:
            has_portal = True
        has_trap = False

        if action_tile.trap:
            has_trap = True
            if action_tile.is_protected_by_same_color(piece.color):
                has_trap = False
        if self.engine.spawning == 'trap':
            return SpawnTrap
        if has_trap:
            if action_tile.trap.color != piece.color:
                return TrapSpawn
        if has_portal:
            return PortalSpawn

        return Spawn

    def revert_to_playing_state(self):
        #
        #   used by many states to return to the 'playing' state, or default state
        #
        self.engine.reset_flags()
        self.engine.reset_selected()
        self.engine.close_menus()
        new_state = Playing(self.win, self.engine)
        self.engine.set_state(new_state)

    def mouse_in_menu_bounds(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                if not menu.mouse_in_menu_bounds():
                    self.engine.close_menus()
                    self.engine.reset_selected()
                    self.revert_to_playing_state()

    def side_bar_input(self, input_type):
        if self.side_bar:
            function = getattr(self.side_bar, input_type)
            function()
            return True

    def menu_input(self, input_type):
        if self.engine.menus:
            for menu in self.engine.menus:
                function = getattr(menu, input_type)
                function()
            return True

    def draw(self):
        #
        #   Default: draw the engine and fill the window background
        #
        self.win.fill(Constant.MENU_COLOR)
        self.engine.draw(self.win)

    def enter(self):
        #
        #   By default enter will change turn if the player has performed an action that turn.
        #
        player = self.engine.players[self.engine.turn]
        number_of_actions_if_player_has_done_nothing = player.total_additional_actions_this_turn + Constant.DEFAULT_ACTIONS_REMAINING
        if number_of_actions_if_player_has_done_nothing > player.actions_remaining:
            self.engine.change_turn()

    def right_click(self):
        #
        #   Implement a right click function in a state to change the default functionality
        #
        pass

    def tab(self):
        prev = self.engine.update_previously_selected()
        if prev is not None:
            self.engine.reset_selected()
            self.revert_to_playing_state()
        try:
            if isinstance(self.engine.events[-1], AITurn):
                for _ in range(2):
                    self.engine.events[-1].undo()
                    del self.engine.events[-1]
            else:
                self.engine.close_menus()
                self.engine.events[-1].undo()
                del self.engine.events[-1]
        except IndexError as e:
            print(e)

    def m(self):
        pass

    def mouse_move(self):
        pass

    def left_click(self):
        pass

    def revert_to_starting_state(self, first=False):
        new_state = Starting(self.win, self.engine, True)
        self.engine.spawning = None
        if first:
            self.engine.first = first
        self.engine.set_state(new_state)


class MainMenu(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.main_menu_logo = Constant.MAIN_MENU_LOGO
        self.logo_position = Constant.LOGO_POSITION
        self.color = Constant.turn_to_color[Constant.LOGO_COLOR]

        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.font_size = round(Constant.SQ_SIZE * 1)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)

        single_player_text = "single player"
        multiplayer_text = 'pass n\' play'
        self.single_player_text_surf = self.font.render(single_player_text, True, self.color)
        self.multiplayer_text_surf = self.font.render(multiplayer_text, True, self.color)

        self.button_width = self.single_player_text_surf.get_width()
        self.button_height = self.multiplayer_text_surf.get_height()

        self.square = pygame.Surface((self.button_width, self.button_height))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.single_player_text_highlight = False
        self.multiplayer_text_highlight = False

        self.single_player_text_display_x = self.window_width // 3 - self.button_width // 2
        self.button_display_y = round(self.window_height * 3/4) - self.button_height // 2

        self.multiplayer_text_display_x = round(self.window_width * 2/3) - self.button_width // 2

        self.multiplayer_button_range_x = range(self.multiplayer_text_display_x, self.multiplayer_text_display_x + self.button_width)
        self.single_player_button_range_x = range(self.single_player_text_display_x, self.single_player_text_display_x + self.button_width)
        self.button_range_y = range(self.button_display_y, self.button_display_y + self.button_height)

    def draw(self):
        self.win.fill(Constant.MENU_COLOR)
        self.win.blit(self.main_menu_logo, self.logo_position)
        if self.single_player_text_highlight:
            self.win.blit(self.square, (self.single_player_text_display_x, self.button_display_y))
        elif self.multiplayer_text_highlight:
            self.win.blit(self.square, (self.multiplayer_text_display_x, self.button_display_y))
        self.win.blit(self.single_player_text_surf, (self.single_player_text_display_x, self.button_display_y))
        self.win.blit(self.multiplayer_text_surf, (self.multiplayer_text_display_x, self.button_display_y))

    def left_click(self):
        pos = pygame.mouse.get_pos()
        if pos[1] in self.button_range_y:
            if pos[0] in self.single_player_button_range_x:
                Constant.PLAY_AGAINST_AI = True
                self.engine.set_state('starting')
            elif pos[0] in self.multiplayer_button_range_x:
                self.engine.create_player('w')
                self.engine.create_player('b')
                Constant.PLAY_AGAINST_AI = False
                self.engine.set_state('starting')

    def enter(self):
        pass

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if pos[1] in self.button_range_y:
            if pos[0] in self.single_player_button_range_x:
                self.single_player_text_highlight = True
            elif pos[0] in self.multiplayer_button_range_x:
                self.multiplayer_text_highlight = True
            else:
                self.single_player_text_highlight = False
                self.multiplayer_text_highlight = False
        else:
            self.single_player_text_highlight = False
            self.multiplayer_text_highlight = False


class DisplayMoves(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)

    def draw(self):
        super().draw()

    def left_click(self):
        self.revert_to_playing_state()

    def select(self, row, col):
        currently_selected = self.engine.get_occupying(row, col)
        self.engine.update_moves()
        currently_selected.display_moves = True

    def tab(self):
        self.revert_to_playing_state()

    def right_click(self):
        self.revert_to_playing_state()

    def m(self):
        self.revert_to_playing_state()

    def mouse_move(self):
        pass


class Playing(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(win, engine)

    def __repr__(self):
        return 'playing'

    def can_move_to_square(self, previously_selected, row, col):
        if previously_selected is not None:
            if previously_selected.actions_remaining > 0:
                if self.engine.player_can_do_action(self.engine.turn):
                    if (row, col) in previously_selected.move_squares_list:
                        if self.engine.get_occupying(row, col) is None:
                            return True
                    else:
                        self.engine.set_popup_reason('invalid_move')

    def can_display_piece_moves(self, currently_selected):
        if not isinstance(currently_selected, Piece):
            return False
        return True

    def can_select_piece(self, currently_selected):
        if not isinstance(currently_selected, Piece):
            return False
        if self.engine.turn == currently_selected.color:
            if currently_selected.actions_remaining > 0:
                if self.engine.player_can_do_action(self.engine.turn):
                    return True
            else:
                self.engine.set_popup_reason('piece_action')

    def can_capture_piece(self, previously_selected, row, col, currently_selected):
        if previously_selected is not None:
            if previously_selected.actions_remaining > 0:
                if self.engine.player_can_do_action(self.engine.turn):
                    if (row, col) in previously_selected.capture_squares_list:
                        if currently_selected is not None:
                            if currently_selected.get_color != previously_selected.get_color():
                                return True

    def same_piece_selected(self, previously_selected, row, col):
        if previously_selected is not None:
            if previously_selected.get_position() == (row, col):
                return True

    def select(self, row, col):
        previously_selected = self.engine.update_previously_selected()
        currently_selected = self.engine.get_occupying(row, col)
        if self.can_move_to_square(previously_selected, row, col):
            prev_position = previously_selected.get_position()
            acting_tile = self.engine.board[prev_position[0]][prev_position[1]]
            action_tile = self.engine.board[row][col]
            move = self.type_of_move(acting_tile, action_tile)
            event = move(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.engine.reset_selected()
            return True

        elif self.same_piece_selected(previously_selected, row, col):
            self.engine.reset_selected()
            return True

        elif self.can_select_piece(currently_selected):
            self.engine.update_moves()
            self.engine.reset_selected()
            currently_selected.selected = True
            return True

        elif self.can_capture_piece(previously_selected, row, col, currently_selected):
            prev_row, prev_col = previously_selected.get_position()
            acting_tile = self.engine.board[prev_row][prev_col]
            action_tile = self.engine.board[row][col]
            capture = self.type_of_capture(acting_tile, action_tile)
            event = capture(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.engine.reset_selected()
            return True

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.side_bar:
            self.side_bar.left_click()

        if self.engine.menus:
            for menu in self.engine.menus:
                menu.left_click()
        else:
            try:
                if not self.select(row, col):
                    self.engine.create_popup_menu(row, col, self.engine.popup_reason)
                    self.engine.reset_selected()
            except IndexError as e:
                print(e)

    def m(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        currently_selected = self.engine.get_occupying(row, col)

        if self.can_display_piece_moves(currently_selected):
            new_state = DisplayMoves(self.win, self.engine)
            self.engine.set_state(new_state)
            self.engine.state[-1].select(row, col)

    def right_click(self):  # STATE, PLAYING
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.right_click()
        else:
            row, col = Constant.convert_pos(pygame.mouse.get_pos())
            self.engine.reset_selected()
            piece = self.engine.get_occupying(row, col)
            if piece:
                if piece.color is self.engine.turn:
                    if not piece.right_click(self.engine):
                        self.engine.create_popup_menu(row, col, self.engine.popup_reason)
                        self.revert_to_playing_state()

    def mouse_move(self):
        self.menu_input('mouse_move')
        self.mouse_in_menu_bounds()
        self.side_bar_input('mouse_move')

    def draw(self):
        super().draw()
        for menu in self.engine.menus:
            menu.draw()
        self.side_bar.draw()


class Starting(State):
    def __init__(self, win, engine, preserve_resources=False):
        super().__init__(win, engine)
        self.side_bar = StartMenu(win, engine)
        if not preserve_resources:
            if Constant.BOARD_STARTS_WITH_RESOURCES:
                self.engine.starting_resources()

    def __repr__(self):
        return 'starting'

    def left_click(self):
        self.side_bar.left_click()

    def mouse_move(self):
        self.side_bar.mouse_move()

    def tab(self):
        self.engine.reset_board()
        self.engine.set_state('main menu')

    def draw(self):
        super().draw()
        self.side_bar.draw()

    def enter(self):
        pass


class SelectStartingPieces(State):

    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.draw_map = False
        self.pieces = {'w': Constant.W_PIECES | Constant.W_BUILDINGS, 'b': Constant.B_PIECES | Constant.B_BUILDINGS}
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.font_size = round(Constant.SQ_SIZE * 1)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.description_text = "Select your Starting Pieces:"
        self.text_surf = self.font.render(self.description_text, True, Constant.turn_to_color[self.engine.turn])
        self.y_buffer = round(Constant.SQ_SIZE * .55)
        self.initial_x = round(2.5 * self.window_width) // len(Constant.SELECTABLE_STARTING_PIECES)
        self.x_buffer = self.initial_x
        self.piece_spacing = round(Constant.SQ_SIZE * 1.5)
        total_height_of_grid = self.y_buffer * 2 * Constant.NUMBER_OF_STARTING_PIECES
        self.initial_y = (self.window_height - total_height_of_grid) // 2
        self.cols = len(Constant.SELECTABLE_STARTING_PIECES)
        self.rows = Constant.NUMBER_OF_STARTING_PIECES
        self.selection_matrix = [[[0 for y in range(3)] for x in range(self.cols)] for _ in range(self.rows)]
        self.instruction_text = [' \'tab\' to go back', ' \'space bar\' to confirm selection',
                                 ' \'right click\' to view the map']
        self.instruction_text_surfaces = []
        self.instruction_text_font_size = Constant.SQ_SIZE // 2
        self.instruction_text_font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.instruction_text_font_size)
        for line in self.instruction_text:
            l = self.instruction_text_font.render(line, True, Constant.turn_to_color[self.engine.turn])
            self.instruction_text_surfaces.append(l)

        self.instruction_text_height = self.instruction_text_surfaces[0].get_height()
        for c in range(self.cols):
            for r in range(self.rows):
                self.selection_matrix[r][c][0] = Constant.SELECTABLE_STARTING_PIECES[c]
                self.selection_matrix[r][c][1] = False  # HIGHLIGHT
                self.selection_matrix[r][c][2] = False  # SELECTED

        self.square = pygame.Surface((Constant.SQ_SIZE, Constant.SQ_SIZE))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def __repr__(self):
        return 'select starting pieces'

    def select_piece(self, piece_selected):
        r, c = piece_selected[0], piece_selected[1]
        for col in range(self.cols):
            if self.selection_matrix[r][col][2]:
                self.selection_matrix[r][col][2] = False
        self.selection_matrix[r][c][2] = True

    def left_click(self):
        piece_selected = self.piece_selected()
        if piece_selected:
            self.select_piece(piece_selected)

    def right_click(self):
        self.draw_map = self.flip_draw_map()

    def piece_selected(self):
        piece_selected = None
        pos = pygame.mouse.get_pos()
        y_buffer = self.y_buffer
        initial_y = self.initial_y
        for r in range(self.rows):
            for c in range(self.cols):
                piece_position = (c * self.piece_spacing + self.initial_x, initial_y)
                if pos[0] in range(piece_position[0], piece_position[0]+Constant.SQ_SIZE):
                    if pos[1] in range(piece_position[1], piece_position[1]+Constant.SQ_SIZE):
                        piece_selected = (r, c)
            initial_y += y_buffer * 2

        return piece_selected

    def mouse_move(self):
        piece_selected = None
        pos = pygame.mouse.get_pos()
        y_buffer = self.y_buffer
        initial_y = self.initial_y
        for r in range(self.rows):
            for c in range(self.cols):
                piece_position = (c * self.piece_spacing + self.initial_x, initial_y)
                if pos[0] in range(piece_position[0], piece_position[0] + Constant.SQ_SIZE):
                    if pos[1] in range(piece_position[1], piece_position[1] + Constant.SQ_SIZE):
                        self.selection_matrix[r][c][1] = True
                    else:
                        self.selection_matrix[r][c][1] = False
                else:
                    self.selection_matrix[r][c][1] = False
            initial_y += y_buffer * 2

        return piece_selected

    def convert_pos(self, pos):
        row = pos[1] // self.piece_spacing - self.y_buffer
        col = pos[0] // (self.piece_spacing + self.initial_x)
        return row, col

    def draw(self):
        if not self.draw_map:
            self.win.fill(Constant.MENU_COLOR)

            y_buffer = self.y_buffer
            initial_x = self.initial_x
            x_buffer = self.initial_x
            piece_spacing = self.piece_spacing
            initial_y = self.initial_y

            for x in range(Constant.NUMBER_OF_STARTING_PIECES):
                for p in Constant.SELECTABLE_STARTING_PIECES:
                    piece = self.engine.turn + "_" + p
                    self.win.blit(self.pieces[self.engine.turn][piece], (x_buffer, initial_y))
                    x_buffer += piece_spacing
                x_buffer = initial_x
                initial_y += y_buffer * 2

            initial_y = self.initial_y
            for r in range(self.rows):
                for c in range(self.cols):
                    position = (c * self.piece_spacing + self.initial_x, initial_y)
                    if self.selection_matrix[r][c][1]:
                        self.win.blit(self.square, position)
                    if self.selection_matrix[r][c][2]:
                        self.win.blit(self.square, position)

                initial_y += y_buffer * 2

            self.win.blit(self.text_surf, (20, 0))
            y_buffer = self.initial_y
            for line in self.instruction_text_surfaces:
                description_text_x = 0
                self.win.blit(line, (description_text_x, y_buffer))
                y_buffer += self.instruction_text_height
        else:
            super().draw()

    def enter(self):
        spawn_list = []
        spawn_list.append(Constant.STARTING_PIECES[0])
        for r in range(self.rows):
            for c in range(self.cols):
                if self.selection_matrix[r][c][2]:
                    spawn_list.append(self.selection_matrix[r][c][0])
        spawn_list.append(Constant.STARTING_PIECES[-1])
        if len(spawn_list) == (Constant.NUMBER_OF_STARTING_PIECES + len(Constant.STARTING_PIECES)):
            self.engine.transfer_to_starting_spawn(spawn_list)

    def flip_draw_map(self):
        return not self.draw_map

    def tab(self):
        if not self.engine.final_spawn:
            self.revert_to_starting_state(self.engine.first)
        else:
            for x in range(2):
                self.engine.events[-1].undo()
                del self.engine.events[-1]


class AIPlaying(State):
    def __init__(self, win, engine, turn_events=None):
        super().__init__(win, engine)
        if turn_events is None:
            self.turn_events = []
        else:
            self.turn_events = turn_events
        self.ai = self.engine.players[self.engine.turn]

    def __repr__(self):
        return 'ai playing'

    def complete_turn(self):
        if not self.act():
            self.change_turn()
            event = AITurn(self.engine, self.turn_events)
            self.engine.add_event(event)
            self.revert_to_playing_state()

    def change_turn(self):
        event = ChangeTurn(self.engine)
        self.engine.add_event(event)
        self.engine.players[self.engine.turn].begin_turn(self)

    def make_move(self, event):
        self.turn_events.append(event)
        event.complete()

    def act(self):
        desired_action = self.ai.get_desired_action(self.engine)
        print(desired_action)
        event = self.ai.fulfill_move_parameters(self.engine, desired_action[0])
        if event is not None:
            self.make_move(event)

        if self.ai.actions_remaining == 0:
            return False

        self.act()


class AIStartingSpawn(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Empty(win, engine)
        self.first = True
        self.engine.sounds.play('start_game')
        self.turn_events = []
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                                   Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                                   Constant.DOWN_LEFT)

    def __repr__(self):
        return 'start spawn'

    def create_ai_player(self):
        if not Constant.TURNS[self.engine.turn] in self.engine.players:
            self.engine.create_ai(Constant.TURNS[self.engine.turn])

        turn_change_event = ChangeTurn(self.engine)
        turn_change_event.complete()
        self.turn_events.append(turn_change_event)

        self.engine.spawn_count = 0
        self.engine.final_spawn = True

        ai = self.engine.players[self.engine.turn]
        choice = ai.behavior.select_starting_square(self.engine)

        self.engine.spawn_list = ai.behavior.select_starting_pieces()
        self.engine.spawning = 'castle'
        self.create_ai_spawn_event(choice[0], choice[1], False)
        self.engine.spawn_count = 0
        self.engine.update_spawn_squares()
        spawn_squares_list = self.engine.get_occupying(choice[0], choice[1]).spawn_squares_list
        placements = ai.behavior.starting_piece_placements(self.engine.spawn_list, spawn_squares_list)
        self.engine.update_spawn_squares()
        for _ in self.engine.spawn_list:
            self.engine.spawning = self.engine.spawn_list[self.engine.spawn_count]
            row, col = placements[self.engine.spawn_count][0], placements[self.engine.spawn_count][1]
            self.create_ai_spawn_event(row, col)
        self.end_start_spawning()

    def end_start_spawning(self):
        self.engine.reset_selected()
        self.engine.reset_piece_actions_remaining()
        self.engine.spawn_success = False
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.reset_player_actions_remaining(self.engine.turn)
        self.engine.update_additional_actions()
        self.engine.update_piece_limit()
        self.engine.spawn_count = 0
        new_state = AIPlaying(self.win, self.engine, self.turn_events)
        self.engine.set_state(new_state)
        new_state.complete_turn()

    def create_ai_spawn_event(self, row, col, first=True):
        action_tile = self.engine.board[row][col]
        acting_tile = self.engine.update_previously_selected()
        event = StartSpawn(self.engine, acting_tile, action_tile)
        event.complete()
        self.turn_events.append(event)
        self.engine.update_spawn_squares()
        self.first = first
        self.engine.spawn_count += 1


class StartingSpawn(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Empty(win, engine)
        self.first = True
        self.engine.sounds.play('start_game')

    def __repr__(self):
        return 'start spawn'

    def begin_ai_starting_spawn(self):
        new_state = AIStartingSpawn(self.win, self.engine)
        self.engine.set_state(new_state)
        new_state.create_ai_player()

    def begin_next_player_piece_select(self):
        event = ChangeTurn(self.engine)
        event.complete()
        self.engine.events.append(event)
        new_state = SelectStartingPieces(self.win, self.engine)
        self.engine.set_state(new_state)
        self.engine.spawn_count = 0
        self.engine.final_spawn = True

    def end_start_spawning(self):
        if Constant.TURN_CHANGE_AFTER_START_SPAWN:
            self.engine.turn = Constant.TURNS[self.engine.turn]
        self.engine.reset_selected()
        self.engine.reset_piece_actions_remaining()
        self.engine.spawn_success = False
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        self.engine.reset_player_actions_remaining(self.engine.turn)
        self.engine.reset_piece_limit(self.engine.turn)
        self.engine.update_additional_actions()

        self.engine.update_piece_limit()
        super().revert_to_playing_state()

    @property
    def get_valid_position(self):
        row, col = -1, -1
        pos = pygame.mouse.get_pos()
        if Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
        return row, col

    def create_spawn_event(self, row, col, first=True):
        if first:
            self.engine.create_player(self.engine.turn)
        action_tile = self.engine.board[row][col]
        previously_selected = self.engine.update_previously_selected()
        if previously_selected:
            acting_tile = self.engine.board[previously_selected.row][previously_selected.col]
        else:
            acting_tile = None
        event = StartSpawn(self.engine, acting_tile, action_tile)
        event.complete()
        self.engine.reset_selected()
        self.engine.events.append(event)
        castle_row, castle_col = self.engine.find_player_castle()
        self.engine.set_purchasing(castle_row, castle_col, True)
        self.engine.update_spawn_squares()
        self.first = first

        self.engine.spawn_count += 1

    def left_click(self):
        row, col = self.get_valid_position
        if self.menu_input('left_click'):
            return
        previously_selected = self.engine.update_previously_selected()
        if previously_selected is not None:
            previously_selected.update_spawn_squares(self.engine)
            if (row, col) in previously_selected.spawn_squares_list:
                self.create_spawn_event(row, col, False)
            else:
                self.engine.create_popup_menu(row, col, 'invalid_start_spawn')
        else:
            if self.engine.is_legal_starting_square(row, col):
                self.create_spawn_event(row, col)
            else:
                self.engine.create_popup_menu(row, col, self.engine.popup_reason)
        try:
            self.engine.spawning = self.engine.spawn_list[self.engine.spawn_count]
            self.engine.update_spawn_squares()
        except IndexError:
            if Constant.PLAY_AGAINST_AI:
                self.begin_ai_starting_spawn()
            elif self.engine.final_spawn:
                self.end_start_spawning()
            else:
                self.begin_next_player_piece_select()

    def right_click(self):
        if self.menu_input('right_click'):
            return
        try:
            if isinstance(self.engine.events[-1], ChangeTurn):
                self.engine.transfer_to_piece_selection()
            else:
                self.engine.events[-1].undo()
                del self.engine.events[-1]
        except IndexError:
            if self.engine.turn_count_display == .5:
                self.engine.transfer_to_piece_selection()

    def revert_to_starting_state(self, first=False):
        new_state = Starting(self.win, self.engine, True)
        self.engine.spawning = None
        self.engine.first = first
        self.engine.set_state(new_state)

    def mouse_in_menu_bounds(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                if not menu.mouse_in_menu_bounds():
                    self.engine.close_menus()

    def draw(self):
        super().draw()
        self.side_bar.draw()
        if self.menu_input('draw'):
            return
        pos = pygame.mouse.get_pos()
        spawnTable = Constant.W_BUILDINGS | Constant.W_PIECES | Constant.B_BUILDINGS | Constant.B_PIECES
        displayPosX = pos[0] - Constant.SQ_SIZE // 2
        displayPosY = pos[1] - Constant.SQ_SIZE // 2
        if Constant.pos_in_bounds(pos):
            self.win.blit(spawnTable[(self.engine.turn + "_" + self.engine.spawning)], (displayPosX, displayPosY))

    def mouse_move(self):
        self.menu_input('mouse_move')
        self.mouse_in_menu_bounds()

    def enter(self):
        pass

    def tab(self):
        self.right_click()


class DebugStart(StartingSpawn):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Empty(win, engine)
        self.first = True
        self.engine.sounds.play('start_game')
        self.spawn_list = Constant.DEBUG_STARTING_PIECES
        self.engine.spawn_list = Constant.DEBUG_STARTING_PIECES
        self.engine.spawning = self.spawn_list[0]

    def __repr__(self):
        return 'start spawn'

    def begin_next_player_start_spawn(self):
        event = ChangeTurn(self.engine)
        event.complete()
        self.engine.events.append(event)
        self.engine.spawn_count = 0
        self.engine.final_spawn = True
        new_state = DebugStart(self.win, self.engine)
        self.engine.set_state(new_state)

    def end_start_spawning(self):
        super().end_start_spawning()
        for p in self.engine.players:
            player = self.engine.players[p]
            player.wood = Constant.DEBUG_STARTING_WOOD
            player.gold = Constant.DEBUG_STARTING_GOLD
            player.stone = Constant.DEBUG_STARTING_STONE
            player.prayer = Constant.DEBUG_STARTING_PRAYER
        super().revert_to_playing_state()

    def left_click(self):
        row, col = self.get_valid_position
        previously_selected = self.engine.update_previously_selected()
        if previously_selected is not None:
            previously_selected.update_spawn_squares(self.engine)
            if (row, col) in previously_selected.spawn_squares_list:
                self.create_spawn_event(row, col, False)
        else:
            if self.engine.is_legal_starting_square(row, col):
                self.create_spawn_event(row, col)
        try:
            self.engine.spawning = self.engine.spawn_list[self.engine.spawn_count]
        except IndexError:
            if self.engine.final_spawn:
                self.end_start_spawning()
            else:
                self.engine.create_player(Constant.TURNS[self.engine.turn])
                self.begin_next_player_start_spawn()


class PrayingBuilding(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.previously_selected = self.engine.update_previously_selected()
        self.menu_queue = None
        self.spawning_piece = None

    def __repr__(self):
        return 'praying building'

    def add_menu_to_menu_queue(self, menu):
        self.menu_queue = menu

    def can_select_piece(self, row, col):
        currently_selected = self.engine.get_occupying(row, col)
        try:
            if self.engine.turn == currently_selected.color:
                if currently_selected.actions_remaining > 0:
                    if self.engine.player_can_do_action(self.engine.turn):
                        return True
        except AttributeError:
            print("Attribute Error")
            print("Line 68, State.py")

    def draw(self):
        super().draw()
        self.side_bar.draw()
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()
        elif Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
            if self.in_praying_squares(row, col):
                self.win.blit(Constant.IMAGES['prayer'], (display_pos_x, display_pos_y))
            elif self.click_square_in_spawn_squares(row, col):
                self.win.blit(Constant.IMAGES['hammer'], (display_pos_x, display_pos_y))

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.left_click()
            if self.engine.spawning is not None:
                new_state = Spawning(self.win, self.engine)
                self.engine.set_state(new_state)
        elif self.select(row, col):
            pass
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)

    def right_click(self):
        self.engine.reset_selected()
        self.engine.menus = []
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def mouse_move(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()
                if not menu.mouse_in_menu_bounds():
                    self.engine.reset_selected()
                    self.engine.menus = []
                    state = Playing(self.win, self.engine)
                    self.engine.set_state(state)

    def click_square_in_spawn_squares(self, row, col):
        if (row, col) in self.previously_selected.spawn_squares(self.engine):
            return True

    def in_praying_squares(self, row, col):
        if (row, col) in self.previously_selected.praying_squares_list:
            return True

    def select(self, row, col):
        if self.click_square_in_spawn_squares(row, col):
            self.engine.menus.append(
                self.engine.MENUS[self.menu_queue](row, col, self.win, self.engine, self.spawning_piece))
            self.spawning_piece.spawn_squares_list = [(row, col)]
            return True
        elif self.in_praying_squares(row, col):
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = self.engine.board[row][col]
            event = Pray(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            new_state = Playing(self.win, self.engine)
            self.engine.reset_selected()
            self.engine.set_state(new_state)
            return True

    def tab(self):
        self.revert_to_playing_state()

class MiningStealing(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)

        self.previously_selected = engine.update_previously_selected()
        self.side_bar = Hud(self.win, self.engine)
        # Row, Col of Stolen FROM piece
        self.row = None
        self.col = None

    def __repr__(self):
        return 'mining stealing'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()
        elif Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
            if self.in_mining_squares(row, col):
                if self.engine.has_quarry(row, col) or self.engine.has_gold(row, col) or self.engine.has_sunken_quarry(
                        row, col) or self.engine.is_empty(row, col):
                    self.win.blit(Constant.IMAGES['pickaxe'], (display_pos_x, display_pos_y))
                elif self.engine.has_wood(row, col):
                    self.win.blit(Constant.IMAGES['axe'], (display_pos_x, display_pos_y))
            elif self.in_stealing_squares(row, col):
                self.win.blit(Constant.IMAGES['steal'], (display_pos_x, display_pos_y))

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.left_click()
        else:
            if self.in_stealing_squares(row, col) and not self.engine.stealing:
                self.row = row
                self.col = col
                menu = StealingMenu(row, col, self.win, self.engine)
                self.engine.menus.append(menu)
            elif self.in_mining_squares(row, col):
                acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
                action_tile = self.engine.board[row][col]
                if action_tile.get_resource():
                    event = Mine(self.engine, acting_tile, action_tile)
                else:
                    self.engine.spawning = 'quarry_1'
                    event = SpawnResource(self.engine, acting_tile, action_tile)
                self.engine.add_event(event)
                new_state = Playing(self.win, self.engine)
                self.engine.reset_selected()
                self.engine.set_state(new_state)
            else:
                self.revert_to_playing_state()
        if self.engine.stealing:
            self.engine.close_menus()
            action_tile = self.engine.board[self.row][self.col]
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            event = Steal(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.engine.stealing = None
            self.revert_to_playing_state()

    def in_mining_squares(self, row, col):
        if (row, col) in self.previously_selected.mining_squares_list:
            return True

    def in_stealing_squares(self, row, col):
        if (row, col) in self.previously_selected.stealing_squares_list:
            return True

    def right_click(self):
        self.engine.reset_selected()
        self.engine.menus = []
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def mouse_move(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()
                if not menu.mouse_in_menu_bounds():
                    self.revert_to_playing_state()

    def tab(self):
        self.revert_to_playing_state()


class Mining(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.prev = engine.update_previously_selected()

    def __repr__(self):
        return 'mining'

    def draw(self):
        super().draw()
        side_bar = Hud(self.win, self.engine)
        side_bar.draw()
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        if Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
            if (row, col) in self.prev.mining_squares_list:
                if self.engine.has_quarry(row, col) or self.engine.has_gold(row, col) or self.engine.has_sunken_quarry(
                        row, col) or self.engine.is_empty(row, col):
                    self.win.blit(Constant.IMAGES['pickaxe'], (display_pos_x, display_pos_y))
                elif self.engine.has_wood(row, col):
                    self.win.blit(Constant.IMAGES['axe'], (display_pos_x, display_pos_y))

    def left_click(self):
        pos = pygame.mouse.get_pos()
        row, col = Constant.convert_pos(pos)
        # try:
        if self.select(row, col):
            pass
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)
        # except IndexError:
        #     print("Index Error")
        #     print(" -- Line 423, State.py")

    def right_click(self):
        self.engine.reset_selected()
        self.engine.menus = []
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def mouse_move(self):
        pass

    def select(self, row, col):
        # try:
        if self.prev is not None:
            if Constant.tile_in_bounds(row, col):
                mining_squares = self.prev.mining_squares_list
                if (row, col) in mining_squares:
                    acting_tile = self.engine.board[self.prev.row][self.prev.col]
                    action_tile = self.engine.board[row][col]
                    if action_tile.get_resource():
                        event = Mine(self.engine, acting_tile, action_tile)
                    else:
                        self.engine.spawning = 'quarry_1'
                        event = SpawnResource(self.engine, acting_tile, action_tile)
                    self.engine.add_event(event)
                    new_state = Playing(self.win, self.engine)
                    self.engine.reset_selected()
                    self.engine.set_state(new_state)

        # except AttributeError:
        #     print("attribute error lined 448")
        #     self.engine.reset_selected()
        #     new_state = Playing(self.win, self.engine)
        #     self.engine.set_state(new_state)

    def tab(self):
        self.revert_to_playing_state()


class Persuading(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.prev = engine.update_previously_selected()

    def __repr__(self):
        return 'mining'

    def draw(self):
        super().draw()
        side_bar = Hud(self.win, self.engine)
        side_bar.draw()
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        if Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
            if (row, col) in self.prev.persuader_squares_list:
                self.win.blit(Constant.IMAGES['persuade'], (display_pos_x, display_pos_y))

    def left_click(self):
        pos = pygame.mouse.get_pos()
        row, col = Constant.convert_pos(pos)
        # try:
        if self.select(row, col):
            pass
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)
        # except IndexError:
        #     print("Index Error")
        #     print(" -- Line 423, State.py")

    def right_click(self):
        self.engine.reset_selected()
        self.engine.menus = []
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def select(self, row, col):
        if self.prev is not None:
            if Constant.tile_in_bounds(row, col):
                persuader_squares = self.prev.persuader_squares_list
                if (row, col) in persuader_squares:
                    acting_tile = self.engine.board[self.prev.row][self.prev.col]
                    action_tile = self.engine.board[row][col]
                    event = Persuade(self.engine, acting_tile, action_tile)
                    self.engine.add_event(event)
                    if self.engine.enemy_player_king_does_not_exist():
                        new_state = Winner(self.win, self.engine)
                        self.engine.set_state(new_state)
                        return True

    def tab(self):
        self.revert_to_playing_state()


class Stealing(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.previously_selected = engine.update_previously_selected()
        self.side_bar = Hud(self.win, self.engine)
        # Row, Col of Stolen FROM piece
        self.row = None
        self.col = None

    def __repr__(self):
        return 'stealing'

    def draw(self):
        super().draw()
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        self.side_bar.draw()
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()
        elif Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
            if (row, col) in self.previously_selected.stealing_squares_list:
                self.win.blit(Constant.IMAGES['steal'], (display_pos_x, display_pos_y))

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.left_click()
        else:
            if self.click_valid_square(row, col) and not self.engine.stealing:
                self.row = row
                self.col = col
                menu = StealingMenu(row, col, self.win, self.engine)
                self.engine.menus.append(menu)
            else:
                self.revert_to_playing_state()

        if self.engine.stealing:
            self.engine.close_menus()
            action_tile = self.engine.board[self.row][self.col]
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            event = Steal(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.engine.stealing = None
            self.revert_to_playing_state()

    def click_valid_square(self, row, col):
        if (row, col) in self.previously_selected.stealing_squares_list:
            return True

    def right_click(self):
        self.engine.reset_selected()
        self.engine.menus = []
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def mouse_move(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()
                if not menu.mouse_in_menu_bounds():
                    self.revert_to_playing_state()

    def tab(self):
        self.revert_to_playing_state()


class PreBuilding(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.previously_selected_piece = self.engine.update_previously_selected()
        self.menu_queue = None
        self.spawning_piece = None

    def __repr__(self):
        return 'building'

    def add_menu_to_menu_queue(self, menu):
        self.menu_queue = menu

    def can_select_piece(self, row, col):
        currently_selected = self.engine.get_occupying(row, col)
        try:
            if self.engine.turn == currently_selected.color:
                if currently_selected.actions_remaining > 0:
                    if self.engine.player_can_do_action(self.engine.turn):
                        return True
        except AttributeError:
            print("Attribute Error")
            print("Line 68, State.py")

    def draw(self):
        super().draw()
        for menu in self.engine.menus:
            menu.draw()
        self.side_bar.draw()
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        if Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
            if not self.engine.menus:
                if (row, col) in self.previously_selected_piece.spawn_squares(self.engine):
                    self.win.blit(Constant.IMAGES['hammer'], (display_pos_x, display_pos_y))

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.left_click()
            if self.engine.spawning is not None:
                new_state = Spawning(self.win, self.engine)
                self.engine.set_state(new_state)
        elif self.select(row, col):
            pass
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)

    def right_click(self):
        self.engine.reset_selected()
        self.engine.menus = []
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def mouse_move(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()
                if not menu.mouse_in_menu_bounds():
                    self.engine.reset_selected()
                    self.engine.menus = []
                    state = Playing(self.win, self.engine)
                    self.engine.set_state(state)

    def click_square_in_spawn_squares(self, row, col):
        if (row, col) in self.previously_selected_piece.spawn_squares(self.engine):
            return True

    def select(self, row, col):
        if self.click_square_in_spawn_squares(row, col):
            self.engine.menus.append(
                self.engine.MENUS[self.menu_queue](row, col, self.win, self.engine, self.spawning_piece))
            self.spawning_piece.spawn_squares_list = [(row, col)]
            return True

    def tab(self):
        self.revert_to_playing_state()


class Trading(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)

    def __repr__(self):
        return 'praying'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()

    def mouse_move(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()
                if not menu.mouse_in_menu_bounds():
                    self.engine.reset_selected()
                    self.engine.menus = []
                    state = Playing(self.win, self.engine)
                    self.engine.set_state(state)

    def left_click(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.left_click()

    def right_click(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.right_click()

    def tab(self):
        self.revert_to_playing_state()


class Praying(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)

    def __repr__(self):
        return 'praying'

    def draw(self):
        super().draw()
        side_bar = Hud(self.win, self.engine)
        side_bar.draw()
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        if Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
            if self.engine.has_prayable_building(row, col):
                if self.engine.get_occupying(row, col).color == self.engine.turn:
                    self.win.blit(Constant.IMAGES['prayer'], (display_pos_x, display_pos_y))

    def left_click(self):
        pos = pygame.mouse.get_pos()
        row, col = Constant.convert_pos(pos)
        # try:
        if self.select(row, col):
            pass
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)
        # except IndexError:
        #     print("Index Error")
        #     print(" -- Line 423, State.py")

    def right_click(self):
        self.engine.reset_selected()
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def mouse_move(self):
        pass

    def select(self, row, col):
        # try:
        prev = self.engine.update_previously_selected()
        if prev is not None:
            sel = self.engine.board[row][col].get_occupying()
            praying_squares = prev.praying_squares_list
            if (row, col) in praying_squares:
                acting_tile = self.engine.board[prev.row][prev.col]
                action_tile = self.engine.board[row][col]
                event = Pray(self.engine, acting_tile, action_tile)
                self.engine.add_event(event)
                new_state = Playing(self.win, self.engine)
                self.engine.reset_selected()
                self.engine.set_state(new_state)

        # except AttributeError:
        #     print("attribute error lined 448")
        #     self.engine.reset_selected()
        #     new_state = Playing(self.win, self.engine)
        #     self.engine.set_state(new_state)

    def tab(self):
        self.revert_to_playing_state()


class Spawning(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(win, engine)
        self.spawnTable = Constant.W_BUILDINGS | Constant.W_PIECES | Constant.B_BUILDINGS | Constant.B_PIECES

    def __repr__(self):
        return 'spawning'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        pos = pygame.mouse.get_pos()
        displayPosX = pos[0] - Constant.SQ_SIZE // 2
        displayPosY = pos[1] - Constant.SQ_SIZE // 2
        if Constant.pos_in_bounds(pos):
            if self.engine.spawning == 'quarry_1':
                self.win.blit(Constant.IMAGES['pickaxe'], (displayPosX, displayPosY))
            else:
                self.win.blit(self.spawnTable[(self.engine.turn + "_" + self.engine.spawning)],
                              (displayPosX, displayPosY))
            return True

    def left_click(self):
        pos = pygame.mouse.get_pos()
        row, col = Constant.convert_pos(pos)
        previousP = self.engine.update_previously_selected()
        if (row, col) in previousP.spawn_squares_list:
            acting_tile = self.engine.board[previousP.row][previousP.col]
            action_tile = self.engine.board[row][col]
            spawn = self.type_of_spawn(acting_tile, action_tile)
            event = spawn(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            state = Playing(self.win, self.engine)
            self.engine.set_state(state)
        else:
            state = Playing(self.win, self.engine)
            self.engine.menus = []
            self.engine.reset_selected()
            self.engine.set_state(state)

    def right_click(self):
        self.revert_to_playing_state()

    def mouse_move(self):
        pass

    def tab(self):
        self.revert_to_playing_state()

class Winner(State):

    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.font_size = round(Constant.SQ_SIZE * 2)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.key = {'w': 'White Won!', 'b': 'Black Won!'}
        self.text_surf = self.font.render(self.key[self.engine.turn], True, Constant.turn_to_color[self.engine.turn])
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.display_x = self.window_width // 2 - self.text_surf.get_width() // 2
        self.display_y = self.window_height // 2 - self.text_surf.get_height() // 2

    def __repr__(self):
        return 'winner'

    def left_click(self):
        self.engine.reset()

    def right_click(self):
        self.engine.reset()

    def mouse_move(self):
        pass

    def draw(self):
        self.win.fill(Constant.MENU_COLOR)
        self.win.blit(self.text_surf, (self.display_x, self.display_y))

    def enter(self):
        self.engine.reset()

    def tab(self):
        self.engine.reset()


class Surrender(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = SurrenderMenu(win, engine)

    def __repr__(self):
        return 'surrender'

    def left_click(self):
        self.side_bar.left_click()
        if self.engine.surrendering:
            new_state = Winner(self.win, self.engine)
            self.engine.set_state(new_state)

    def right_click(self):
        self.revert_to_playing_state()

    def mouse_move(self):
        self.side_bar.mouse_move()

    def tab(self):
        self.revert_to_playing_state()

    def draw(self):
        super().draw()
        self.side_bar.draw()


class PieceCost(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        menu = Master(self.win, self.engine, Constant.MASTER_COST_LIST)
        self.engine.menus.append(menu)

    def __repr__(self):
        return 'piece cost screen'

    def remove_top_menu(self):
        if len(self.engine.menus) == 1:
            self.engine.close_menus()
            self.revert_to_playing_state()
        else:
            del self.engine.menus[-1]

    def right_click(self):
        self.remove_top_menu()

    def mouse_move(self):
        self.engine.menus[-1].mouse_move()

    def draw(self):
        self.engine.menus[-1].draw()

    def left_click(self):
        self.engine.menus[-1].left_click()

    def enter(self):
        pass

    def tab(self):
        self.remove_top_menu()


class Ritual(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.previously_selected = engine.update_previously_selected()
        self.cost_type = None
        self.turn = self.engine.turn
        self.player = self.engine.players[self.turn]
        self.ritual_image = Constant.PRAYER_RITUALS[self.turn + '_' + str(self)]
        self.engine.close_menus()
        self.PIECES = Constant.B_PIECES | Constant.W_PIECES

    def click_valid_square(self, row, col):
        if (row, col) in self.previously_selected.ritual_squares_list:
            return True

    def draw_ritual_at_mouse_position(self):
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        self.win.blit(self.ritual_image, (display_pos_x, display_pos_y))

    def right_click(self):
        self.revert_to_playing_state()

    def mouse_move(self):
        pass

    def enter(self):
        pass

    def tab(self):
        self.revert_to_playing_state()


class SummonGoldGeneral(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.previously_selected.ritual_squares_list = self.previously_selected.gold_general_ritual_squares(self.engine)

    def __repr__(self):
        return 'gold_general'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        # Display Gold General at mouse position while mouse is on valid spawn square
        self.previously_selected.highlight_ritual_squares(self.win)
        self.draw_ritual_at_mouse_position()

    def click_valid_square(self, row, col):
        if Constant.tile_in_bounds(row, col):
            if (row, col) in self.previously_selected.ritual_squares_list:
                return True

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col):
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = self.engine.board[row][col]
            event = GoldGeneralEvent(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.revert_to_playing_state()
        else:
            self.revert_to_playing_state()

        # Spend prayer after the square is clicked


class PerformSmite(Ritual):

    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.engine.close_menus()
        self.previously_selected.ritual_squares_list = self.smite_ritual_squares()

    def __repr__(self):
        return 'smite'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        # Display Gold General at mouse position while mouse is on valid spawn square
        self.previously_selected.highlight_ritual_squares(self.win)
        self.draw_ritual_at_mouse_position()

    def smite_ritual_squares(self):
        list_of_enemy_pieces = []
        for piece in self.engine.players[Constant.TURNS[self.engine.turn]].pieces:
            row, col = piece.row, piece.col
            if not isinstance(piece, King):
                if not self.engine.board[row][col].is_protected():
                    list_of_enemy_pieces.append((row, col))
        return list_of_enemy_pieces

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col):
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = self.engine.board[row][col]
            event = Smite(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.revert_to_playing_state()
        else:
            self.revert_to_playing_state()


class PerformDestroyResource(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.engine.close_menus()
        self.previously_selected.ritual_squares_list = self.delete_resource_ritual_squares()

    def __repr__(self):
        return 'destroy_resource'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        # Display Gold General at mouse position while mouse is on valid spawn square
        self.previously_selected.highlight_ritual_squares(self.win)
        self.draw_ritual_at_mouse_position()

    def delete_resource_ritual_squares(self):
        list_of_all_resources = []
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                if self.engine.has_resource(row, col):
                    list_of_all_resources.append((row, col))
        return list_of_all_resources

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())

        if self.click_valid_square(row, col):
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = self.engine.board[row][col]
            event = DestroyResource(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.revert_to_playing_state()
        else:
            self.revert_to_playing_state()


class PerformCreateResource(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.engine.close_menus()
        self.previously_selected.ritual_squares_list = self.create_resource_ritual_squares()
        self.row = None
        self.col = None

    def __repr__(self):
        return 'create_resource'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        # Display Gold General at mouse position while mouse is on valid spawn square
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()
        else:
            self.previously_selected.highlight_ritual_squares(self.win)
            self.draw_ritual_at_mouse_position()

    def mouse_move(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()

    def create_resource_ritual_squares(self):
        list_of_all_empty_squares = []
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                if self.engine.is_empty(row, col):
                    list_of_all_empty_squares.append((row, col))

        return list_of_all_empty_squares

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.left_click()
        else:
            if self.click_valid_square(row, col) and not self.engine.ritual_summon_resource:
                self.row = row
                self.col = col
                menu = ResourceMenu(row, col, self.win, self.engine)
                self.engine.menus.append(menu)
            else:
                self.revert_to_playing_state()

        if self.engine.ritual_summon_resource:
            self.engine.close_menus()
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = self.engine.board[self.row][self.col]
            event = CreateResource(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.engine.ritual_summon_resource = None
            self.revert_to_playing_state()


class PerformTeleport(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.engine.close_menus()
        self.previously_selected.ritual_squares_list = self.teleport_ritual_squares()
        self.selected = None

    def __repr__(self):
        return 'teleport'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        self.previously_selected.highlight_ritual_squares(self.win)
        self.draw_ritual_at_mouse_position()
        if self.selected:
            self.selected.highlight_self_square(self.win)

    def teleport_ritual_squares(self):
        list_of_all_pieces = []
        for piece in self.player.pieces:
            if not isinstance(piece, Building):
                if not isinstance(piece, King):
                    list_of_all_pieces.append((piece.row, piece.col))

        for piece in self.engine.players[Constant.TURNS[self.turn]].pieces:
            if not isinstance(piece, King):
                if not isinstance(piece, Building):
                    list_of_all_pieces.append((piece.row, piece.col))
        return list_of_all_pieces

    def valid_teleport_squares(self):
        valid_squares = []
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                if self.engine.is_empty(row, col):
                    valid_squares.append((row, col))
                elif self.selected.is_rogue:
                    if self.engine.can_be_occupied_by_rogue(row, col):
                        valid_squares.append((row, col))
                elif self.selected.is_general:
                    if self.engine.can_be_occupied_by_gold_general(row, col):
                        valid_squares.append((row, col))

        return valid_squares

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col) and self.selected is None:
            self.selected = self.engine.get_occupying(row, col)
            self.previously_selected.ritual_squares_list = self.valid_teleport_squares()
        elif self.click_valid_square(row, col) and self.selected:
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = ((self.selected.row, self.selected.col), (row, col))
            event = Teleport(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.revert_to_playing_state()
        else:
            self.revert_to_playing_state()


class PerformSwap(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.engine.close_menus()
        self.first_selected = None
        self.second_selected = None
        self.previously_selected.ritual_squares_list = self.swap_ritual_squares()

    def __repr__(self):
        return 'swap'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        self.previously_selected.highlight_ritual_squares(self.win)
        self.draw_ritual_at_mouse_position()
        if self.first_selected:
            self.first_selected.highlight_self_square(self.win)

    def swap_criteria(self, piece):
        if not isinstance(piece, King):
            return not isinstance(piece, Building)

    def swap_ritual_squares(self):
        valid_pieces = []
        # find first selected:
        if not self.first_selected:
            for piece in self.engine.players[self.turn].pieces:
                if self.swap_criteria(piece):
                    valid_pieces.append((piece.row, piece.col))
            return valid_pieces
        # find second selected:
        for piece in self.engine.players[Constant.TURNS[self.turn]].pieces:
            if self.swap_criteria(piece):
                valid_pieces.append((piece.row, piece.col))
        return valid_pieces

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col) and self.first_selected is None:
            self.first_selected = self.engine.get_occupying(row, col)
            self.previously_selected.ritual_squares_list = self.swap_ritual_squares()
        elif self.click_valid_square(row, col) and self.first_selected:
            self.second_selected = self.engine.get_occupying(row, col)
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = ((self.first_selected.row, self.first_selected.col), (row, col))
            event = Swap(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.revert_to_playing_state()
        else:
            self.revert_to_playing_state()


class PerformLineDestroy(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.engine.close_menus()
        self.directions = (Constant.UP, Constant.RIGHT, Constant.LEFT, Constant.DOWN)
        self.row = self.previously_selected.row
        self.col = self.previously_selected.col
        mouse_row, mouse_col = Constant.convert_pos(pygame.mouse.get_pos())
        self.up = range(self.row - 1, -1, -1), range(self.col, self.col+1)
        self.down = range(self.row + 1, Constant.BOARD_HEIGHT_SQ), range(self.col, self.col + 1)
        self.right = range(self.row, self.row+1), range(self.col + 1, Constant.BOARD_WIDTH_SQ)
        self.left = range(self.row, self.row+1), range(self.col - 1, -1, -1)

        self.selected_range = self.determine_active_line(mouse_row, mouse_col)

        self.previously_selected.ritual_squares_list = self.active_line_destroy_ritual_squares(self.selected_range)

    def __repr__(self):
        return 'line_destroy'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        self.previously_selected.highlight_ritual_squares(self.win)
        self.draw_ritual_at_mouse_position()

    def determine_active_line(self, row, col):
        if Constant.tile_in_bounds(row, col):
            if row in self.up[0] and col == self.col:
                return self.up
            if row in self.down[0] and col == self.col:
                return self.down
            if col in self.right[1] and row == self.row:
                return self.right
            if col in self.left[1] and row == self.row:
                return self.left

    def mouse_move(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        self.selected_range = self.determine_active_line(row, col)
        self.previously_selected.ritual_squares_list = self.active_line_destroy_ritual_squares(self.selected_range)

    def active_line_destroy_ritual_squares(self, selected_range):
        active_line_squares = []
        if selected_range:
            for r in selected_range[0]:
                for c in selected_range[1]:
                    if self.engine.board[r][c].is_protected_by_opposite_color(self.engine.turn):
                        break
                    else:
                        active_line_squares.append((r, c))
        return active_line_squares

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col):
            self.engine.line_destroy_selected_range = self.selected_range
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = self.engine.board[row][col]
            event = LineDestroy(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            if self.engine.enemy_player_king_does_not_exist():
                new_state = Winner(self.win, self.engine)
                self.engine.set_state(new_state)
            else:
                self.revert_to_playing_state()
        else:
            self.revert_to_playing_state()


class PerformProtect(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(win, engine)
        self.engine.close_menus()
        self.previously_selected.ritual_squares_list = self.protectable_ritual_squares()

    def __repr__(self):
        return 'protect'

    def protectable_ritual_squares(self):
        # empty
        #
        # resource
        ritual_squares = []
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                if self.engine.is_empty(row, col):
                    ritual_squares.append((row, col))
                elif self.engine.get_occupying(row, col):
                    piece = self.engine.get_occupying(row, col)
                    if not isinstance(piece, King):
                        ritual_squares.append((row, col))
                elif self.engine.get_resource(row, col):
                    ritual_squares.append((row, col))
        return ritual_squares

    def draw(self):
        super().draw()
        self.side_bar.draw()
        self.previously_selected.highlight_ritual_squares(self.win)
        self.draw_ritual_at_mouse_position()

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col):
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = self.engine.board[row][col]
            event = Protect(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.revert_to_playing_state()
        else:
            self.revert_to_playing_state()


class PerformPortal(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(win, engine)
        self.engine.close_menus()
        self.selected = None
        self.previously_selected.ritual_squares_list = self.valid_portal_squares()

    def __repr__(self):
        return 'portal'

    def valid_portal_squares(self):
        ritual_squares = []
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                if self.engine.is_empty(row, col):
                    ritual_squares.append((row, col))
                elif self.engine.get_occupying(row, col):
                    piece = self.engine.get_occupying(row, col)
                    if not isinstance(piece, Piece) and not isinstance(piece, Building):
                        ritual_squares.append((row, col))
                elif self.engine.get_resource(row, col):
                    ritual_squares.append((row, col))
        if self.selected:
            if (self.selected.row, self.selected.col) in ritual_squares:
                ritual_squares.remove((self.selected.row, self.selected.col))
        return ritual_squares

    def draw(self):
        super().draw()
        self.side_bar.draw()
        self.previously_selected.highlight_ritual_squares(self.win)
        self.draw_ritual_at_mouse_position()
        if self.selected:
            self.selected.draw_portal_image(self.win)

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col) and self.selected is None:
            self.selected = self.engine.board[row][col]
            self.selected.portal_image = Constant.IMAGES[self.turn+"_portal"]
            self.previously_selected.ritual_squares_list = self.valid_portal_squares()
        elif self.click_valid_square(row, col) and self.selected:
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = ((self.selected.row, self.selected.col), (row, col))
            event = Portal(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.revert_to_playing_state()
        else:
            self.revert_to_playing_state()
