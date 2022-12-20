from GameEvent import *
from Menu import *
from Tile import *
from Building import *

#
#   Change each state class to have cleaner code.
#   Change all direct references to changing engine variables to helper methods
#   Use nested methods for reused logic
#


class State:

    def __init__(self, win, engine):
        self.win = win
        self.engine = engine

    def reset_state(self):
        self.engine.spawning = None
        self.engine.reset_selected()
        self.engine.close_menus()
        new_state = Playing(self.win, self.engine)
        self.engine.set_state(new_state)

    def draw(self):
        self.win.fill(Constant.MENU_COLOR)
        self.engine.draw(self.win)

    def enter(self):
        player = self.engine.players[self.engine.turn]
        number_of_actions_if_player_has_done_nothing = player.total_additional_actions_this_turn + Constant.DEFAULT_ACTIONS_REMAINING
        if number_of_actions_if_player_has_done_nothing > player.actions_remaining:
            self.engine.change_turn()


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

    def can_select_piece(self, currently_selected):
        try:
            if self.engine.turn == currently_selected.color:
                if currently_selected.actions_remaining > 0:
                    if self.engine.player_can_do_action(self.engine.turn):
                        return True
        except AttributeError:
            print("Attribute Error")
            print("Line 68, State.py")

    def can_capture_piece(self, previously_selected, row, col, currently_selected):
        if previously_selected is not None:
            if previously_selected.actions_remaining > 0:
                if self.engine.player_can_do_action(self.engine.turn):
                    if (row, col) in previously_selected.move_squares_list:
                        if currently_selected is not None:
                            if currently_selected.get_color != previously_selected.get_color():
                                return True

    def same_piece_selected(self, previously_selected, row, col):
        if previously_selected is not None:
            if previously_selected.get_position() == (row, col):
                return True

    def select(self, row, col):
        #
        #   Determine context of our select function
        #   Returns a piece object to previousP if the piece is mining, purchasing, selected
        #   or pre-selected
        #
        previously_selected = self.engine.update_previously_selected()

        #
        #   Determine the piece which we are currently selecting on this call of the select function
        #
        currently_selected = self.engine.get_occupying(row, col)

        #
        #   Move previously selected piece to empty square
        #
        if self.can_move_to_square(previously_selected, row, col):
            #
            #   Store the position of previously selected piece
            #
            prev_position = previously_selected.get_position()

            #
            #   Create move event using all data related to move
            #
            moveEvent = Move(previously_selected, prev_position, (row, col))

            #
            #   Complete move event a change the board accordingly
            #
            moveEvent.complete(self.engine)

            #
            #   Add the event to the engine list of all GameEvents
            #
            self.engine.events.append(moveEvent)

            #
            #   Reset selected piece and previously selected piece
            #
            self.engine.reset_selected()

            #
            #   Return True
            #
            return True

        elif self.same_piece_selected(previously_selected, row, col):
            self.engine.reset_selected()
            return True
        #
        #   Select Player piece for moving
        #
        elif self.can_select_piece(currently_selected):
            #
            #   Update all pieces moves
            #
            self.engine.update_moves()

            #
            #   Reset all selected pieces
            #
            self.engine.reset_selected()

            #
            #   Set currently selected to True
            #
            currently_selected.selected = True
            return True
        #
        #   Select enemy piece to be captured
        #
        elif self.can_capture_piece(previously_selected, row, col, currently_selected):
            #
            #   Store position of previously selected piece
            #
            prev_position = previously_selected.get_position()

            #
            #   Create Capture Event, passing in all relevant data
            #
            capture_event = Capture(previously_selected, prev_position, (row, col), currently_selected)

            #
            #   Complete Event
            #
            capture_event.complete(self.engine)

            #
            #   Add event to engine list of GameEvents
            #
            self.engine.events.append(capture_event)

            #
            #   Remove all selections
            #
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
                    self.engine.reset_selected()
            except IndexError as e:
                print(e)

        if self.engine.enemy_player_king_does_not_exist():
            new_state = Winner(self.win, self.engine)
            self.engine.set_state(new_state)

    def tab(self):
        prev = self.engine.update_previously_selected()
        if prev is not None:
            self.engine.reset_selected()
        else:
            try:
                self.engine.events[-1].undo(self.engine)
                del self.engine.events[-1]
            except IndexError:
                print("failed to undo")

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
                        self.reset_state()

    def mouse_move(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()
                if not menu.mouse_in_menu_bounds():
                    self.reset_state()

        if self.side_bar:
            self.side_bar.mouse_move()

    def draw(self):
        super().draw()
        for menu in self.engine.menus:
            menu.draw(self.win)
        self.side_bar.draw()


class Starting(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = StartMenu(win, engine)

    def __repr__(self):
        return 'starting'

    def select(self, row, col):
        pass

    def right_click(self):
        self.engine.events = []
        self.engine.board = [[0 for y in range(self.engine.cols)] for x in range(self.engine.rows)]
        for c in range(self.engine.cols):
            for r in range(self.engine.rows):
                self.engine.board[r][c] = Tile(r, c)
        new_state = Starting(self.win, self.engine)
        self.engine.set_state(new_state)

    def left_click(self):
        self.side_bar.left_click()

    def mouse_move(self):
        self.side_bar.mouse_move()

    def draw(self):
        super().draw()
        self.side_bar.draw()

    def enter(self):
        pass

    def tab(self):
        self.right_click()

    def re_initialize(self):
        self.engine.reset_all_engine_variables()


class SelectStartingPieces(State):

    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.pieces = {'w': Constant.W_PIECES, 'b': Constant.B_PIECES}
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.font_size = round(Constant.SQ_SIZE * 1.5)
        self.font = pygame.font.Font(os.path.join("resources/fonts", "font.ttf"), self.font_size)
        self.description_text = "Select your Starting Pieces:"
        self.text_surf = self.font.render(self.description_text, True, Constant.turn_to_color[self.engine.turn])
        self.y_buffer = Constant.SQ_SIZE
        self.initial_x = 2 * self.window_width // len(Constant.SELECTABLE_STARTING_PIECES)
        self.x_buffer = self.initial_x
        self.piece_spacing = Constant.SQ_SIZE * 2
        self.initial_y = self.window_height // Constant.NUMBER_OF_STARTING_PIECES - self.y_buffer
        self.cols = len(Constant.SELECTABLE_STARTING_PIECES)
        self.rows = Constant.NUMBER_OF_STARTING_PIECES

        self.selection_matrix = [[0 for y in range(self.cols)] for x in range(self.rows)]

        for c in range(self.cols):
            for r in range(self.rows):
                self.selection_matrix[r][c] = Constant.SELECTABLE_STARTING_PIECES[c]

        self.selections = []

    def __repr__(self):
        return 'select starting pieces'

    def left_click(self):
        row, col = self.convert_pos(pygame.mouse.get_pos())
        print(row, " ", col)

    def right_click(self):
        pass

    def mouse_move(self):
        pass

    def convert_pos(self, pos):
        print(pos)
        row = pos[1] // self.piece_spacing - self.y_buffer
        col = pos[0] // (self.piece_spacing + self.initial_x)
        return row, col

    def draw(self):
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
                rectangle = pygame.Rect(c * self.piece_spacing + self.initial_x, initial_y,
                                        Constant.SQ_SIZE, Constant.SQ_SIZE)
                pygame.draw.rect(self.win, Constant.BLACK, rectangle, 2)
            initial_y += y_buffer * 2

        self.win.blit(self.text_surf, (20, 0))

    def enter(self):
        pass

    def tab(self):
        pass


class StartingSpawn(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Empty(win, engine)
        self.first = True
        self.play_random_sound_effect()

    def __repr__(self):
        return 'start spawn'

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.start_game) - 1)
        Constant.START_GAME_SOUNDS[i].set_volume(.1)
        Constant.START_GAME_SOUNDS[i].play()

    def left_click(self):
        def get_valid_position():
            row, col = -1, -1
            pos = pygame.mouse.get_pos()
            if Constant.pos_in_bounds(pos):
                row, col = Constant.convert_pos(pos)
            return row, col

        def is_legal_starting_square(row, col):
            #
            #   Is the square empty
            #
            player_is_too_close = False
            if self.engine.can_be_occupied(row, col):
                #
                #   Is there another player on the board already
                #
                if self.engine.players:
                    #
                    #   Check 3x3 area around the Castle
                    #
                    for r in range(row - 3, row + 4):
                        for c in range(col - 3, col + 4):
                            #
                            #   If there is a Castle in any of those squares
                            #
                            if self.engine.has_castle(r, c):
                                #
                                #   Set the flag to true
                                #
                                player_is_too_close = True

                    #
                    #   If player is too close, return False.
                    #   Because the square is not a legal starting square.
                    #
                    return not player_is_too_close

                #
                #   If there is not another player, return True after we determine the square is empty.
                #
                else:
                    return True

            #
            #   The square is not empty, so return false. Not a legal starting square under any condition
            #
            else:
                return False

        #
        #   If the position of the mouse is in the bounds of the board
        #
        row, col = get_valid_position()
        #
        #   Determine if a piece has already been selected.
        #   This method is run recursively so we need to determine if this is the first click or the second
        #   after a piece has been previously selected
        #
        previousP = self.engine.update_previously_selected()

        #
        #   If board position is valid
        #
        #
        #   When previously selected is (None) it means that no Castle has been spawned yet this turn.
        #   First we will handle this by creating the Castle
        #
        if previousP is None:
            #
            #   Determine if the Square selected is valid for spawning a Castle
            #
            if is_legal_starting_square(row, col):
                #
                #   If the list of players contains another player
                #
                # create spawn event
                spawn_event = StartSpawn(self.engine.turn, self.engine.spawning, (row, col), self.engine.spawn_count,
                                         self.engine.final_spawn, self.engine.update_previously_selected())
                spawn_event.complete(self.engine)
                self.engine.reset_selected()
                self.engine.update_spawn_squares()
                self.engine.events.append(spawn_event)

                #
                #   Set the spawned castle purchasing to True
                #
                castle_row, castle_col = self.engine.find_player_castle()
                self.engine.set_purchasing(castle_row, castle_col, True)

                # iterate our index
                self.engine.spawn_count += 1

        #
        #   Now we run the logic for selecting the squares where we spawn the pieces around the Castle
        #
        else:
            #
            #
            #
            previousP.update_spawn_squares(self.engine)

            #
            #
            #
            if (row, col) in previousP.spawn_squares_list:
                spawn_event = StartSpawn(self.engine.turn, self.engine.spawning, (row, col), self.engine.spawn_count,
                                         self.engine.final_spawn, self.engine.update_previously_selected())
                spawn_event.complete(self.engine)
                self.engine.reset_selected()
                self.engine.update_spawn_squares()
                self.engine.events.append(spawn_event)
                castle_row, castle_col = self.engine.find_player_castle()
                self.engine.set_purchasing(castle_row, castle_col, True)
                self.first = False
                # iterate our index
                self.engine.spawn_count += 1

                if previousP.spawn_squares_list == []:
                    # no squares available to spawn
                    pass
            else:
                pass
        try:
            self.engine.spawning = Constant.STARTING_PIECES[self.engine.spawn_count]
        except IndexError:
            if self.engine.final_spawn:
                self.engine.reset_selected()
                self.engine.reset_piece_actions_remaining()
                self.engine.spawn_success = False
                unused_pieces = self.engine.count_unused_pieces()
                for piece in unused_pieces:
                    piece.unused_piece_highlight = True
                self.engine.reset_player_actions_remaining(self.engine.turn)
                self.engine.update_additional_actions()
                self.engine.update_piece_limit()
                super().reset_state()
            else:
                turn_change = ChangeTurn(self.engine)
                turn_change.complete(self.engine)
                self.engine.events.append(turn_change)
                new_state = StartingSpawn(self.win, self.engine)
                self.engine.set_state(new_state)
                self.engine.spawning = Constant.STARTING_PIECES[0]
                self.engine.spawn_count = 0
                self.engine.final_spawn = True

    def right_click(self):
        try:
            if isinstance(self.engine.events[-1], ChangeTurn):
                for x in range(2):
                    self.engine.events[-1].undo(self.engine)
                    del self.engine.events[-1]
            else:
                self.engine.events[-1].undo(self.engine)
                del self.engine.events[-1]
        except IndexError:
            if self.engine.turn_count_display == .5:
                new_state = Starting(self.win, self.engine)
                self.engine.spawning = None
                self.engine.set_state(new_state)
            else:
                self.engine.reset_board()
                new_state = Starting(self.win, self.engine)
                self.engine.spawning = None
                self.engine.first = True
                self.engine.set_state(new_state)

    def draw(self):
        super().draw()
        self.side_bar.draw()
        pos = pygame.mouse.get_pos()
        spawnTable = Constant.W_BUILDINGS | Constant.W_PIECES | Constant.B_BUILDINGS | Constant.B_PIECES
        displayPosX = pos[0] - Constant.SQ_SIZE // 2
        displayPosY = pos[1] - Constant.SQ_SIZE // 2
        if Constant.pos_in_bounds(pos):
            self.win.blit(spawnTable[(self.engine.turn + "_" + self.engine.spawning)], (displayPosX, displayPosY))
            return True

    def mouse_move(self):
        pass

    def enter(self):
        pass

    def tab(self):
        self.right_click()


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
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        self.side_bar.draw()
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw(self.win)
        elif Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
            if (row, col) in self.previously_selected.stealing_squares_list:
                self.win.blit(Constant.IMAGES['steal'], (display_pos_x, display_pos_y))

    def draw(self):
        super().draw()
        self.side_bar.draw()
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - Constant.SQ_SIZE // 2
        display_pos_y = pos[1] - Constant.SQ_SIZE // 2
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw(self.win)
        elif Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)
            if self.in_mining_squares(row, col):
                if self.engine.has_quarry(row, col) or self.engine.has_gold(row, col) or self.engine.has_sunken_quarry(
                        row, col):
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
                sel = self.engine.board[row][col].get_resource()
                mining_event = Mine(sel, self.previously_selected)
                mining_event.complete(self.engine)
                self.engine.events.append(mining_event)
                new_state = Playing(self.win, self.engine)
                self.engine.reset_selected()
                self.engine.set_state(new_state)
            else:
                self.reset_state()
        if self.engine.stealing:
            self.engine.close_menus()
            stolen_from = self.engine.get_occupying(self.row, self.col)
            thief = self.previously_selected
            resource_stolen = self.engine.stealing[0]
            amount = self.engine.stealing[1]
            event = Steal(stolen_from, thief, resource_stolen, amount)
            event.complete(self.engine)
            self.engine.events.append(event)
            self.engine.stealing = None
            self.reset_state()

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
                    self.reset_state()

    def tab(self):
        try:
            self.engine.events[-1].undo(self.engine)
            del self.engine.events[-1]
        except IndexError:
            print("IndexError")
            print("Line 567, State.py")


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
                        row, col):
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
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def mouse_move(self):
        pass

    def select(self, row, col):
        # try:
        if self.prev is not None:
            if Constant.tile_in_bounds(row, col):
                sel = self.engine.board[row][col].get_resource()
                mining_squares = self.prev.mining_squares_list
                if (row, col) in mining_squares:
                    mining_event = Mine(sel, self.prev)
                    mining_event.complete(self.engine)
                    self.engine.events.append(mining_event)
                    new_state = Playing(self.win, self.engine)
                    self.engine.reset_selected()
                    self.engine.set_state(new_state)

        # except AttributeError:
        #     print("attribute error lined 448")
        #     self.engine.reset_selected()
        #     new_state = Playing(self.win, self.engine)
        #     self.engine.set_state(new_state)

    def tab(self):
        try:
            self.engine.events[-1].undo(self.engine)
            del self.engine.events[-1]
        except IndexError:
            print("IndexError")
            print("Line 567, State.py")


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
                menu.draw(self.win)
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
                self.reset_state()

        if self.engine.stealing:
            self.engine.close_menus()
            stolen_from = self.engine.get_occupying(self.row, self.col)
            thief = self.previously_selected
            resource_stolen = self.engine.stealing[0]
            amount = self.engine.stealing[1]
            event = Steal(stolen_from, thief, resource_stolen, amount)
            event.complete(self.engine)
            self.engine.events.append(event)
            self.engine.stealing = None
            self.reset_state()

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
                    self.reset_state()

    def tab(self):
        try:
            self.engine.events[-1].undo(self.engine)
            del self.engine.events[-1]
        except IndexError:
            print("IndexError")
            print("Line 567, State.py")


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
            menu.draw(self.win)
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
        try:
            self.engine.events[-1].undo(self.engine)
            del self.engine.events[-1]

        except IndexError:
            print("failed to undo")


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
                prayer_event = Pray(prev, sel)
                prayer_event.complete(self.engine)
                self.engine.events.append(prayer_event)
                new_state = Playing(self.win, self.engine)
                self.engine.reset_selected()
                self.engine.set_state(new_state)

        # except AttributeError:
        #     print("attribute error lined 448")
        #     self.engine.reset_selected()
        #     new_state = Playing(self.win, self.engine)
        #     self.engine.set_state(new_state)

    def tab(self):
        try:
            self.engine.events[-1].undo(self.engine)
            del self.engine.events[-1]

        except IndexError:
            print("failed to undo")


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
        if self.engine.spawning == 'quarry_1':
            previousP.spawn_squares_list = previousP.spawn_squares_for_quarry(self.engine)
        piece_cost = Constant.PIECE_COSTS[self.engine.spawning]
        if (row, col) in previousP.spawn_squares_list:
            if self.engine.spawning == 'quarry_1':
                spawn_event = SpawnResource(self.engine.turn, self.engine.spawning, (row, col), previousP)
            else:
                spawn_event = Spawn(self.engine.turn, self.engine.spawning, (row, col), previousP)
            spawn_event.complete(self.engine)
            self.engine.events.append(spawn_event)
            self.engine.players[self.engine.turn].purchase(piece_cost)
            state = Playing(self.win, self.engine)
            self.engine.set_state(state)
        else:
            state = Playing(self.win, self.engine)
            self.engine.menus = []
            self.engine.reset_selected()
            self.engine.set_state(state)

    def right_click(self):
        super().reset_state()

    def mouse_move(self):
        pass

    def tab(self):
        pass


class Winner(State):

    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.font_size = round(Constant.SQ_SIZE * 1.5)
        self.font = pygame.font.Font(os.path.join("resources/fonts", "font.ttf"), self.font_size)
        self.key = {'w': 'White Won!', 'b': 'Black Won!'}
        self.text_surf = self.font.render(self.key[self.engine.turn], True, Constant.turn_to_color[self.engine.turn])
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.display_x = self.window_width // 2 - self.text_surf.get_width() // 2
        self.display_y = self.window_height // 2 - self.text_surf.get_height() // 2

    def __repr__(self):
        return 'winner'

    def left_click(self):
        pass

    def right_click(self):
        pass

    def mouse_move(self):
        pass

    def draw(self):
        self.win.fill(Constant.MENU_COLOR)
        self.win.blit(self.text_surf, (self.display_x, self.display_y))

    def enter(self):
        pass

    def tab(self):
        new_state = Starting(self.win, self.engine)
        new_state.re_initialize()
        self.engine.set_state(new_state)


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
        self.reset_state()

    def mouse_move(self):
        self.side_bar.mouse_move()

    def tab(self):
        self.reset_state()

    def draw(self):
        super().draw()
        self.side_bar.draw()


class PieceCost(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.pieces = {'w': Constant.W_PIECES | Constant.W_BUILDINGS, 'b': Constant.B_PIECES | Constant.B_BUILDINGS}
        self.font_size = round(Constant.SQ_SIZE * 1.5)
        self.font = pygame.font.Font(os.path.join("resources/fonts", "font.ttf"), self.font_size)
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.test_text = self.font.render("10", True, Constant.RED)
        self.menu = self.win
        self.color = Constant.turn_to_color[self.engine.turn]
        self.horizontal_buffer_between_costs = round(Constant.SQ_SIZE * 1.3)
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE
        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(os.path.join("resources/fonts", "font.ttf"), self.font_size)
        self.test_text = self.font.render("10", True, Constant.RED)
        self.spawning = None
        self.player = self.engine.players[self.engine.turn]

    def __repr__(self):
        return 'piece cost screen'

    def left_click(self):
        pass

    def right_click(self):
        self.tab()

    def mouse_move(self):
        pass

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        y_buffer = 0
        x_buffer = 0

        for p in Constant.PIECE_COSTS:
            p_piece_cost = Constant.PIECE_COSTS[p]
            if p == 'quarry_1':
                piece = 'quarry_1'
            else:
                piece = self.engine.turn + "_" + p
            log_x = x_buffer + self.horizontal_buffer_between_costs
            gold_x = log_x + self.horizontal_buffer_between_costs
            stone_x = gold_x + self.horizontal_buffer_between_costs

            # Log Cost
            if p_piece_cost['log'] != 0:
                if self.player.wood >= p_piece_cost['gold']:
                    color = Constant.turn_to_color[self.engine.turn]
                else:
                    color = Constant.RED
                log_cost = self.font.render(str(p_piece_cost['log']), True, color)
                self.menu.blit(Constant.MENU_ICONS['log'], (log_x, y_buffer + Constant.SQ_SIZE // 4))
                self.menu.blit(log_cost,
                               ((log_x + (Constant.SQ_SIZE // 1.5)), (y_buffer + (Constant.SQ_SIZE // 6))))

            # Gold Cost
            if p_piece_cost['gold'] != 0:
                if self.player.gold >= p_piece_cost['gold']:
                    color = Constant.turn_to_color[self.engine.turn]
                else:
                    color = Constant.RED
                gold_cost = self.font.render(str(p_piece_cost['gold']), True, color)
                self.menu.blit(Constant.MENU_ICONS['gold_coin'], (gold_x, y_buffer + Constant.SQ_SIZE // 4))
                self.menu.blit(gold_cost,
                               ((gold_x + (Constant.SQ_SIZE // 1.5)), (y_buffer + (Constant.SQ_SIZE // 6))))

            # Stone Cost
            if p_piece_cost['stone'] != 0:
                if self.player.stone >= p_piece_cost['stone']:
                    color = Constant.turn_to_color[self.engine.turn]
                else:
                    color = Constant.RED
                stone_cost = self.font.render(str(p_piece_cost['stone']), True, color)
                self.menu.blit(Constant.MENU_ICONS['stone'], (stone_x, y_buffer + Constant.SQ_SIZE // 4))
                self.menu.blit(stone_cost,
                               ((stone_x + (Constant.SQ_SIZE // 1.5)), (y_buffer + (Constant.SQ_SIZE // 6))))

            # Menu
            if p == 'quarry_1':
                self.menu.blit(Constant.RESOURCES[piece], (x_buffer, y_buffer))
            else:
                self.menu.blit(self.pieces[self.engine.turn][piece], (x_buffer, y_buffer))

            y_buffer += self.vertical_buffer_between_pieces
            if y_buffer >= Constant.BOARD_HEIGHT_PX:
                y_buffer = 0
                x_buffer += self.window_width / 3

    def enter(self):
        pass

    def tab(self):
        new_state = Playing(self.win, self.engine)
        self.engine.set_state(new_state)


class Ritual(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.previously_selected = engine.update_previously_selected()
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
        self.reset_state()

    def mouse_move(self):
        pass

    def enter(self):
        pass

    def tab(self):
        self.reset_state()


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
            event = GoldGeneralEvent(self.engine,self.previously_selected, row, col)
            event.complete()
            self.engine.events.append(event)
            self.reset_state()
        else:
            self.reset_state()

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
                list_of_enemy_pieces.append((row, col))
        return list_of_enemy_pieces

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col):
            event = Smite(self.engine,self.previously_selected, row, col)
            event.complete()
            self.engine.events.append(event)
            self.reset_state()
        else:
            self.reset_state()


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
            event = DestroyResource(self.engine,self.previously_selected, row, col)
            event.complete()
            self.engine.events.append(event)
            self.reset_state()
        else:
            self.reset_state()


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
                menu.draw(self.win)
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
                self.reset_state()

        if self.engine.ritual_summon_resource:
            self.engine.close_menus()
            event = CreateResource(self.engine,self.previously_selected, self.row, self.col, self.engine.ritual_summon_resource)
            event.complete()
            self.engine.events.append(event)
            self.engine.ritual_summon_resource = None
            self.reset_state()


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
            event = Teleport(self.engine,self.previously_selected, self.selected.row, self.selected.col, row, col)
            event.complete()
            self.engine.events.append(event)
            self.reset_state()
        else:
            self.reset_state()


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

    def swap_ritual_squares(self):
        list_of_all_pieces = []
        for player in self.engine.players:
            for piece in self.engine.players[player].pieces:
                if piece is not self.first_selected:
                    if not isinstance(piece, Building):
                        if not isinstance(piece, King):
                            list_of_all_pieces.append((piece.row, piece.col))
        return list_of_all_pieces

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col) and self.first_selected is None:
            self.first_selected = self.engine.get_occupying(row, col)
            self.previously_selected.ritual_squares_list = self.swap_ritual_squares()
        elif self.click_valid_square(row, col) and self.first_selected:
            self.second_selected = self.engine.get_occupying(row, col)
            event = Swap(self.engine,self.previously_selected, self.first_selected.row, self.first_selected.col, self.second_selected.row, self.second_selected.col)
            event.complete()
            self.engine.events.append(event)
            self.reset_state()
        else:
            self.reset_state()


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
                    active_line_squares.append((r, c))
        return active_line_squares

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col):
            event = LineDestroy(self.engine,self.previously_selected, row, col, self.selected_range)
            event.complete()
            self.engine.events.append(event)
            if self.engine.enemy_player_king_does_not_exist():
                new_state = Winner(self.win, self.engine)
                self.engine.set_state(new_state)
            else:
                self.reset_state()
        else:
            self.reset_state()


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
            event = Protect(self.engine,self.previously_selected, row, col)
            event.complete()
            self.engine.events.append(event)
            self.reset_state()
        else:
            self.reset_state()