from GameEvent import *
from Menu import *


class State:
    def __init__(self, win, engine):
        self.win = win
        self.engine = engine
        self.side_bar = None
        self.dragging = False
        self.mouse_start_pos = None
        self.dragging_piece = None
        self.spawnTable = Constant.W_BUILDINGS | Constant.W_PIECES | Constant.B_BUILDINGS | Constant.B_PIECES

    def draw_piece_at_mouse_cursor(self, pos, piece):
        """
        Draws a piece at the mouse cursor position, centering it properly.
        """
        piece_image = self.spawnTable[(self.engine.turn + "_" + str(piece))]
        piece_rect = piece_image.get_rect(center=pos)
        self.win.blit(piece_image, piece_rect.topleft)

    def __repr__(self):
        raise NotImplementedError("Subclasses must implement __repr__ ")

    def reset_dragging_piece(self):
        try:
            self.dragging_piece.dragging = False
        except AttributeError as e:
            print(e)
        self.dragging_piece = None
        self.dragging = False

    def handle_input(self, event):
        """
        Handles input events including mouse clicks, dragging, and key presses.

        - Left click (MOUSEBUTTONDOWN with button 1) starts selection or dragging.
        - Mouse movement (MOUSEMOTION) updates dragging or handles hover effects.
        - Left click release (MOUSEBUTTONUP with button 1) determines if it was a click or a drag-and-drop action.
        - Right click (MOUSEBUTTONDOWN with button 3) triggers the right-click function.
        - Key presses (KEYDOWN) trigger specific functions.
        """

        CLICK_THRESHOLD = 5  # Movement threshold to differentiate click vs. drag

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.left_click():
                    print("Click")

                elif self.drag_piece(event.pos):
                    print("Dragging")
                    self.dragging = True

            elif event.button == 3:
                # Trigger right-click functionality
                self.right_click()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                # Otherwise, treat it as a drag-and-drop action
                print("Dropping")
                self.drop_piece(event.pos)
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            self.mouse_move()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.tab()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.enter()
            elif event.key == pygame.K_m:
                self.m()
            elif event.key == pygame.K_c:
                self.c()

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

    def can_inspect_piece(self, currently_selected):
        return currently_selected is not None

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
        """
        Reverts the engine to the 'playing' state, which is considered the default gameplay state.
        This method is typically used by various states to return to the default game state.

        It resets the engine flags, selected state, and closes any active menus before
        transitioning to the 'Playing' state.
        """

        # Reset any flags and selections that are active during other states
        self.engine.reset_flags()  # Resets any flags related to current actions
        self.engine.reset_selected()  # Clears any selected items or pieces
        self.engine.close_menus()  # Closes any open menus

        # Transition to the default 'Playing' state
        new_state = Playing(self.win, self.engine)
        self.engine.set_state(new_state)  # Sets the new state to 'Playing'
        return True

    def mouse_in_menu_bounds(self):
        """
        Checks if the mouse is within any active menu bounds.
        If the mouse is not in any menu bounds, it closes the menus and resets the game state.
        """
        # Only proceed if there are active menus
        if self.engine.menus:
            # Loop through each active menu
            for menu in self.engine.menus:
                # If mouse is not in the current menu bounds
                if not menu.mouse_in_menu_bounds():
                    # Close all menus and reset the selected state
                    self.engine.close_menus()
                    self.engine.reset_selected()

                    # Revert the game to the default 'playing' state
                    return self.revert_to_playing_state()

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
        self.revert_to_playing_state()
        player = self.engine.players[self.engine.turn]

        number_of_actions_if_player_has_done_nothing = (player.total_additional_actions_this_turn +
                                                        Constant.DEFAULT_ACTIONS_REMAINING)
        if number_of_actions_if_player_has_done_nothing > player.actions_remaining:
            self.engine.change_turn()

    def drag_piece(self, pos):
        pass

    def drop_piece(self, pos):
        pass

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

    def c(self):
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
    def __init__(self, win, engine, splash_screen):
        super().__init__(win, engine)
        self.main_menu_logo = splash_screen.logo_image
        self.logo_position = splash_screen.logo_position
        self.color = Constant.turn_to_color[splash_screen.logo_color]

        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.font_size = round(Constant.SQ_SIZE * 1)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)

        single_player_text = " "
        multiplayer_text = 'start'
        self.single_player_text_surf = self.font.render(single_player_text, True, self.color)
        self.multiplayer_text_surf = self.font.render(multiplayer_text, True, self.color)

        self.button_width = self.multiplayer_text_surf.get_width()
        self.button_height = self.multiplayer_text_surf.get_height()

        self.square = pygame.Surface((self.button_width, self.button_height))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.single_player_text_highlight = False
        self.multiplayer_text_highlight = False

        self.single_player_text_display_x = 0
        self.button_display_y = round(self.window_height * 3 / 4) - self.button_height // 2

        self.multiplayer_text_display_x = self.window_width // 2 - self.button_width // 2

        self.multiplayer_button_range_x = range(self.multiplayer_text_display_x,
                                                self.multiplayer_text_display_x + self.button_width)
        self.single_player_button_range_x = range(self.single_player_text_display_x,
                                                  self.single_player_text_display_x + self.button_width)
        self.button_range_y = range(self.button_display_y, self.button_display_y + self.button_height)

    def __repr__(self):
        return 'main menu'

    def set_splash(self, splash_screen):
        self.main_menu_logo = splash_screen.logo_image
        self.logo_position = splash_screen.logo_position
        self.color = Constant.turn_to_color[splash_screen.logo_color]

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
            # if pos[0] in self.single_player_button_range_x:
            #     pass
            #     # Constant.PLAY_AGAINST_AI = True
            #     # self.engine.set_state('starting')
            if pos[0] in self.multiplayer_button_range_x:
                self.engine.create_player('w')
                self.engine.create_player('b')
                Constant.PLAY_AGAINST_AI = False
                self.engine.set_state('starting')

    def enter(self):
        pass

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if pos[1] in self.button_range_y:
            # if pos[0] in self.single_player_button_range_x:
            #     # Disabled
            #     self.single_player_text_highlight = False
            if pos[0] in self.multiplayer_button_range_x:
                self.multiplayer_text_highlight = True
            else:
                self.single_player_text_highlight = False
                self.multiplayer_text_highlight = False
        else:
            self.single_player_text_highlight = False
            self.multiplayer_text_highlight = False


class Inspector(State):
    def __init__(self, win, engine, currently_selected):
        super().__init__(win, engine)
        self.currently_selected = currently_selected
        self.side_bar = PieceInspector(win, engine, currently_selected)

    def __repr__(self):
        return 'inspector'

    def draw(self):
        super().draw()
        self.side_bar.draw()

    def left_click(self):
        return self.revert_to_playing_state()

    def select(self, row, col):
        self.currently_selected = self.engine.get_occupying(row, col)
        self.engine.update_moves()
        self.currently_selected.display_moves = True

    def tab(self):
        self.revert_to_playing_state()

    def right_click(self):
        self.revert_to_playing_state()

    def get_piece_inspected(self):
        return self.currently_selected

    def m(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.engine.get_occupying(row, col) is not self.currently_selected:
            if self.can_inspect_piece(self.engine.get_occupying(row, col)):
                self.engine.reset_selected()
                self.side_bar = PieceInspector(self.win, self.engine, self.engine.get_occupying(row, col))
                self.select(row, col)
            else:
                self.revert_to_playing_state()
        else:
            self.revert_to_playing_state()

    def mouse_move(self):
        pass


class Playing(State):
    def __init__(self, win, engine):
        # Initialize the 'Playing' state with the given window and engine.
        super().__init__(win, engine)
        self.side_bar = Hud(win, engine)  # Create the HUD (side bar) for this states
        self.contextual = None

    def __repr__(self):
        # Representation of the 'Playing' state, useful for debugging.
        return 'playing'

    def drag_piece(self, pos):
        if not self.engine.menus:
            row, col = Constant.convert_pos(pos)
            currently_selected = self.engine.get_occupying(row, col)
            if self.can_select_piece(currently_selected):
                self.dragging_piece = currently_selected
                currently_selected.dragging = True
                return self.select_piece(currently_selected)
            else:
                self.reset_dragging_piece()

    def drop_piece(self, pos):
        if not self.engine.menus:
            row, col = Constant.convert_pos(pos)
            if self.dragging:
                if not self.select(row, col):
                    print("Nothing valid selected")
                    # If nothing valid is selected, show a popup menu
                    self.engine.reset_selected()  # Reset selected piece
            self.reset_dragging_piece()

    def can_swap_to_square(self, previously_selected, row, col):
        if previously_selected is None:
            return False
        if not previously_selected.can_act():
            return False
        if not self.engine.player_can_do_action(self.engine.turn):
            return False
        if (row, col) not in previously_selected.swap_squares_list:
            return False
        return True

    def can_move_to_square(self, previously_selected, row, col):
        """
        Checks if the previously selected piece can move to the specified square.
        Returns True if the move is valid, False otherwise.
        """
        if previously_selected is None:  # No piece selected, can't move
            return False
        if previously_selected.actions_remaining == 0:  # No actions left to move
            return False
        if not self.engine.player_can_do_action(self.engine.turn):  # Check if the player can perform an action
            return False
        if (row, col) not in previously_selected.move_squares_list:  # Target square not in move list
            self.engine.set_popup_reason('invalid_move')  # Set error message for invalid move
            return False
        if self.engine.get_occupying(row, col) is not None:  # Square already occupied
            return False
        return True  # All checks passed, the move is valid

    def can_select_piece(self, currently_selected):
        """
        Checks if a piece can be selected based on its properties and the current game state.
        Returns True if the piece can be selected, False otherwise.
        """
        if self.dragging:
            return False
        if not isinstance(currently_selected, Piece):  # The selected object is not a piece
            return False
        if self.engine.turn != currently_selected.color:  # The piece does not belong to the current player
            return False
        if not currently_selected.can_act():  # No actions left for the piece
            self.engine.set_popup_reason('piece_action')  # Set reason for piece not being able to be selected
            return False
        if not self.engine.player_can_do_action(self.engine.turn):  # Player can't perform actions
            return False
        return True  # The piece can be selected

    def can_capture_piece(self, previously_selected, row, col, currently_selected):
        """
        Checks if the previously selected piece can capture the piece on the target square.
        Returns True if the capture is valid, False otherwise.
        """
        if previously_selected is None:  # No piece selected to capture with
            return False
        if previously_selected.actions_remaining == 0:  # No actions left to capture
            return False
        if not self.engine.player_can_do_action(self.engine.turn):  # Check if the player can perform an action
            return False
        if (row, col) not in previously_selected.capture_squares_list:  # Target square not in capture list
            return False
        if currently_selected is None or currently_selected.get_color() == previously_selected.get_color():
            # No piece to capture or the piece is of the same color
            return False
        return True  # The capture is valid

    def same_piece_selected(self, previously_selected, row, col):
        """
        Checks if the same piece is selected again.
        Returns True if the same piece is selected, False otherwise.
        """
        if previously_selected is None:  # No piece selected
            return False
        return previously_selected.get_position() == (row, col)  # Check if the positions match

    def select(
            self,
            row: int,
            col: int
    ) -> bool:
        """
        Handles the logic for selecting a piece or moving a piece to a new square.
        Returns True if the selection/move is successful, False otherwise.
        """
        # Get the currently selected piece and previously selected piece
        previously_selected = self.engine.update_previously_selected()
        currently_selected = self.engine.get_occupying(row, col)

        # Check if the piece can move to the new square
        if self.can_move_to_square(previously_selected, row, col):
            self.perform_move(previously_selected, row, col)
            return True  # Move successful

        if self.can_swap_to_square(previously_selected, row, col):
            self.perform_swap(previously_selected, row, col)
            return True

        # Check if the same piece is selected again (deselect it)
        if self.same_piece_selected(previously_selected, row, col):
            self.engine.reset_selected()
            return True  # Deselect the piece

        # Check if a new piece can be selected
        if self.can_select_piece(currently_selected):
            self.select_piece(currently_selected)
            return True  # Piece selected

        # Check if the piece can capture another piece
        if self.can_capture_piece(previously_selected, row, col, currently_selected):
            self.perform_capture(previously_selected, row, col)
            return True  # Capture successful

        return False  # No valid action

    def perform_move(self, previously_selected, row, col):
        """
        Performs the move action by creating an event and updating the game state.
        """
        prev_position = previously_selected.get_position()
        acting_tile = self.engine.board[prev_position[0]][prev_position[1]]
        action_tile = self.engine.board[row][col]
        move = self.type_of_move(acting_tile, action_tile)  # Get the type of move
        event = move(self.engine, acting_tile, action_tile)  # Create the move event
        self.engine.add_event(event)  # Add event to engine
        self.engine.reset_selected()  # Reset selected piece

    def perform_swap(self, previously_selected, row, col):
        """
        Performs the move action by creating an event and updating the game state.
        """
        prev_position = previously_selected.get_position()
        acting_tile = self.engine.board[prev_position[0]][prev_position[1]]
        action_tile = self.engine.board[row][col]
        event = Swap(self.engine, acting_tile, action_tile)  # Create the move event
        self.engine.add_event(event)  # Add event to engine
        self.engine.reset_selected()  # Reset selected piece

    def perform_capture(self, previously_selected, row, col):
        """
        Performs the capture action by creating an event and updating the game state.
        """
        prev_row, prev_col = previously_selected.get_position()
        acting_tile = self.engine.board[prev_row][prev_col]
        action_tile = self.engine.board[row][col]
        capture = self.type_of_capture(acting_tile, action_tile)  # Get the type of capture
        event = capture(self.engine, acting_tile, action_tile)  # Create the capture event
        self.engine.add_event(event)  # Add event to engine
        self.engine.reset_selected()  # Reset selected piece

    def select_piece(self, currently_selected):
        """
        Selects the piece and updates the game state.
        """
        # Update the available moves for the piece
        self.engine.update_moves()

        # Reset any previously selected piece
        self.engine.reset_selected()
        # Mark the piece as selected
        currently_selected.selected = True
        return True

    def left_click(self):
        """
        Handles the left click action, including selecting pieces and interacting with menus.
        Executes all left click actions and returns True if any return True.
        """
        results = []

        if self.side_bar:
            results.append(self.side_bar.left_click())

        if self.engine.menus:
            print(self.engine.menus)
            for menu in self.engine.menus:
                print("clicking into menu")
                results.append(menu.left_click())

        return any(results)  # Returns True if any element in results is True

    def inspect_piece(self):
        """
        Handles the inspection of a piece when a special action is performed (e.g., by pressing a key or
        right-clicking).
        """
        row, col = Constant.convert_pos(pygame.mouse.get_pos())  # Get mouse position
        currently_selected = self.engine.get_occupying(row, col)  # Get the piece under the mouse
        if self.can_inspect_piece(currently_selected):  # Check if the piece can be inspected
            # Create and switch to the Inspector state
            new_state = Inspector(self.win, self.engine, currently_selected)
            new_state.select(row, col)  # Select the piece in the Inspector state
            self.engine.set_state(new_state)  # Switch to the new state

    def right_click(self):
        """
        Handles the right-click action, including interacting with menus and pieces.
        """
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.right_click()  # Handle menu interaction
        else:
            if self.dragging:
                self.reset_dragging_piece()
                self.engine.reset_selected()
            else:
                row, col = Constant.convert_pos(pygame.mouse.get_pos())  # Get mouse position
                self.engine.reset_selected()  # Reset selected piece
                piece = self.engine.get_occupying(row, col)  # Get the piece under the mouse
                if piece and piece.color == self.engine.turn:  # Ensure the piece belongs to the current player
                    if not piece.right_click(self.engine):  # Perform right-click action for the piece
                        # If the right-click doesn't result in an action, show a popup menu
                        self.engine.create_popup_menu(row, col, self.engine.popup_reason)
                        self.revert_to_playing_state()  # Revert to the 'playing' state
                    else:
                        try:
                            # Create ability menu for pieces with more than 1 ability
                            self.engine.create_contextual_menu(row, col, self.win, piece.contextual_options)

                            # Immediately click into the menu if there is only one option
                            if len(piece.contextual_options) == 1:
                                if str(piece) not in ['queen', 'king']:
                                    self.engine.menus[-1].left_click()

                        except AttributeError as e:
                            print(f"{e} State.py, Line 615")

    def m(self):
        """
        Handles the inspection of a piece when triggered by a special action (e.g., pressing a key).
        It checks if the piece under the mouse can be inspected and switches to the Inspector state.
        """
        # Convert the current mouse position to board coordinates (row, col)
        row, col = Constant.convert_pos(pygame.mouse.get_pos())

        # Retrieve the piece that is currently occupying the specified position
        currently_selected = self.engine.get_occupying(row, col)

        # Check if the piece can be inspected (based on certain conditions)
        if self.can_inspect_piece(currently_selected):
            # Create a new Inspector state and pass the piece to inspect
            new_state = Inspector(self.win, self.engine, currently_selected)

            # Select the piece in the new Inspector state (this may trigger further actions like showing details)
            new_state.select(row, col)

            # Switch to the Inspector state to inspect the piece
            self.engine.set_state(new_state)

    def mouse_move(self):
        """
        Handles mouse movement. It processes menu input, checks if the mouse is within
        the bounds of any active menus, and handles sidebar input.
        """

        self.menu_input('mouse_move')  # Process menu input based on mouse movement
        self.mouse_in_menu_bounds()  # Check if mouse is inside any active menu
        self.side_bar_input('mouse_move')  # Process sidebar input based on mouse movement

    def draw(self):
        """
        Draws the game board, menus, and the sidebar on the window.
        """
        super().draw()  # Call the parent class's draw method (draw the base game state)
        for menu in self.engine.menus:
            menu.draw()  # Draw each menu if any are open
        self.side_bar.draw()  # Draw the sidebar

        pos = pygame.mouse.get_pos()
        if self.dragging:
            try:
                self.draw_piece_at_mouse_cursor(pos, self.dragging_piece)
            except KeyError:
                pass


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
        return self.side_bar.left_click()

    def c(self):
        self.engine.transfer_to_piece_cost_screen()

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
        # Initialize the base class
        super().__init__(win, engine)

        # Set up initial attributes
        self.draw_map = False
        self.pieces = {'w': Constant.W_PIECES | Constant.W_BUILDINGS, 'b': Constant.B_PIECES | Constant.B_BUILDINGS}

        # Window dimensions
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h

        # Font size and rendering
        self.font_size = round(Constant.SQ_SIZE * 1)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.description_text = "Select your starting pieces:"
        self.text_surf = self.font.render(self.description_text, True, Constant.turn_to_color[self.engine.turn])

        # Y-buffer for spacing
        self.y_buffer = round(Constant.SQ_SIZE * .55)

        # Calculate initial positions and spacing
        self.initial_x = round(2.5 * self.window_width) // len(Constant.SELECTABLE_STARTING_PIECES)
        self.x_buffer = self.initial_x
        self.piece_spacing = round(Constant.SQ_SIZE * 1.5)

        # Calculate total height of the grid and starting Y position
        total_height_of_grid = self.y_buffer * 2 * Constant.NUMBER_OF_STARTING_PIECES
        self.initial_y = (self.window_height - total_height_of_grid) // 2

        # Define grid dimensions
        self.cols = len(Constant.SELECTABLE_STARTING_PIECES)
        self.rows = Constant.NUMBER_OF_STARTING_PIECES + Constant.NUMBER_OF_BONUS_PIECES

        # Initialize the selection matrix (3D list to track piece status)
        self.selection_matrix = [[[0 for y in range(3)] for x in range(self.cols)] for _ in range(self.rows)]

        # Instruction text and surfaces
        self.instruction_text = [
            ' \'tab\' to go back',
            ' \'space bar\' to confirm selection',
            ' \'right click\' to view the map'
        ]
        self.instruction_text_surfaces = []
        self.instruction_text_font_size = Constant.SQ_SIZE // 2
        self.instruction_text_font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"),
                                                      self.instruction_text_font_size)
        for line in self.instruction_text:
            l = self.instruction_text_font.render(line, True, Constant.turn_to_color[self.engine.turn])
            self.instruction_text_surfaces.append(l)

        # Get the height of the instruction text for layout purposes
        self.instruction_text_height = self.instruction_text_surfaces[0].get_height()

        # Assign pieces to the selection matrix
        for r in range(self.rows):
            for c in range(self.cols):
                # Check if we are in the bonus piece rows
                if r >= Constant.NUMBER_OF_STARTING_PIECES:
                    # If it's a bonus piece, assign it
                    self.selection_matrix[r][c][0] = Constant.BONUS_STARTING_PIECES[c]
                else:
                    # Otherwise, assign a selectable starting piece
                    self.selection_matrix[r][c][0] = Constant.SELECTABLE_STARTING_PIECES[c]

                # Initialize the selection matrix states (highlight and selected status)
                self.selection_matrix[r][c][1] = False  # HIGHLIGHT
                self.selection_matrix[r][c][2] = False  # SELECTED

        # Create a surface for highlighting unused pieces
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
            return True

    def right_click(self):
        if self.engine.menus:
            self.engine.close_menus()
            return
        piece_selected = self.piece_selected()

        if not piece_selected or self.draw_map:
            self.draw_map = self.flip_draw_map()
            return

        if not self.draw_map:
            try:
                row, col = piece_selected
            except TypeError:
                return
            piece = self.selection_matrix[row][col][0]
            menu = PieceDescription(self.win, self.engine, piece)
            self.engine.menus.append(menu)



    def piece_selected(self):
        piece_selected = None
        pos = pygame.mouse.get_pos()
        y_buffer = self.y_buffer
        initial_y = self.initial_y
        for r in range(self.rows):
            for c in range(self.cols):
                piece_position = (c * self.piece_spacing + self.initial_x, initial_y)
                if pos[0] in range(piece_position[0], piece_position[0] + Constant.SQ_SIZE):
                    if pos[1] in range(piece_position[1], piece_position[1] + Constant.SQ_SIZE):
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
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()
                return
        if not self.draw_map:
            self.win.fill(Constant.MENU_COLOR)

            y_buffer = self.y_buffer
            initial_x = self.initial_x
            x_buffer = self.initial_x
            piece_spacing = self.piece_spacing
            initial_y = self.initial_y

            for x in range(Constant.NUMBER_OF_STARTING_PIECES + Constant.NUMBER_OF_BONUS_PIECES):
                if x < Constant.NUMBER_OF_STARTING_PIECES:
                    for p in Constant.SELECTABLE_STARTING_PIECES:
                        piece = self.engine.turn + "_" + p
                        self.win.blit(self.pieces[self.engine.turn][piece], (x_buffer, initial_y))
                        x_buffer += piece_spacing
                else:
                    for p in Constant.BONUS_STARTING_PIECES:
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
        if len(spawn_list) == (
                Constant.NUMBER_OF_STARTING_PIECES + len(Constant.STARTING_PIECES) + Constant.NUMBER_OF_BONUS_PIECES):
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
            try:
                self.win.blit(spawnTable[(self.engine.turn + "_" + self.engine.spawning)], (displayPosX, displayPosY))
            except TypeError:
                pass

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
            return True
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)
            return False

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
            return True
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)
            return False

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
        results = list()

        # First, check if there are any menus
        if self.engine.menus:
            for menu in self.engine.menus:
                results.append(menu.left_click())

        # If no menus, check if stealing is in progress
        if self.engine.stealing:
            self.engine.close_menus()
            action_tile = self.engine.board[self.row][self.col]
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            event = Steal(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.engine.stealing = None
            results.append(self.revert_to_playing_state())

        # If no menus and no stealing, check if the click is on a valid square
        if self.click_valid_square(row, col):
            if not self.engine.stealing:
                self.row = row
                self.col = col
                menu = StealingMenu(row, col, self.win, self.engine)
                self.engine.menus.append(menu)
                results.append(True)  # Return true if a valid square is clicked
            else:
                results.append(self.revert_to_playing_state())  # Return to playing state if stealing is ongoing
        return any(results)

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
        return 'pre-building'

    def add_menu_to_menu_queue(self, menu):
        self.menu_queue = menu
        row, col = self.previously_selected_piece.row, self.previously_selected_piece.col
        self.engine.menus.append(
                self.engine.MENUS[
                    self.menu_queue](row, col, self.win, self.engine, self.previously_selected_piece))

    def can_select_piece(self, row, col):
        currently_selected = self.engine.get_occupying(row, col)
        try:
            if self.engine.turn == currently_selected.color:
                if currently_selected.actions_remaining > 0:
                    if self.engine.player_can_do_action(self.engine.turn):
                        return True
        except AttributeError:
            pass

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
                return menu.left_click()

            if self.engine.spawning is not None:
                new_state = Spawning(self.win, self.engine)
                self.engine.set_state(new_state)
                return True
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)
            return False

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
        return True
        # if self.click_square_in_spawn_squares(row, col):
        #     self.engine.menus.append(
        #             self.engine.MENUS[self.menu_queue](row, col, self.win, self.engine, self.spawning_piece))
        #     self.spawning_piece.spawn_squares_list = [(row, col)]
        #     return True

    def tab(self):
        self.revert_to_playing_state()


class Trading(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)

    def __repr__(self):
        return 'trading'

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
                    self.engine.trading = []
                    self.engine.reset_selected()
                    self.engine.menus = []
                    state = Playing(self.win, self.engine)
                    self.engine.set_state(state)

    def left_click(self):
        if self.engine.menus:
            for menu in self.engine.menus:
                return menu.left_click()

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
            return True
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)
            return False

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

    def tab(self):
        self.revert_to_playing_state()


class Spawning(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(win, engine)

    def __repr__(self):
        return 'spawning'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        pos = pygame.mouse.get_pos()
        displayPosX = pos[0] - Constant.SQ_SIZE // 2
        displayPosY = pos[1] - Constant.SQ_SIZE // 2
        if Constant.pos_in_bounds(pos):
            try:
                if self.engine.spawning == 'quarry_1':
                    self.win.blit(Constant.IMAGES['pickaxe'], (displayPosX, displayPosY))
                else:
                    self.win.blit(self.spawnTable[(self.engine.turn + "_" + self.engine.spawning)],
                                  (displayPosX, displayPosY))
            except TypeError:
                pass
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
            return True
        else:
            state = Playing(self.win, self.engine)
            self.engine.menus = []
            self.engine.reset_selected()
            self.engine.set_state(state)
            return False

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
    def __init__(self, win, engine, current_state=None):
        self.current_state = current_state
        super().__init__(win, engine)
        menu = Master(self.win, self.engine, Constant.MASTER_COST_LIST)
        self.engine.menus.append(menu)

    def __repr__(self):
        return 'piece cost screen'

    def remove_top_menu(self):
        if len(self.engine.menus) == 1:
            self.engine.close_menus()
            if str(self.current_state) == 'playing':
                self.revert_to_playing_state()
            else:
                self.revert_to_starting_state()

        else:
            del self.engine.menus[-1]

    def right_click(self):
        self.remove_top_menu()

    def mouse_move(self):
        if self.engine.menus:
            self.engine.menus[-1].mouse_move()

    def draw(self):
        try:
            self.engine.menus[-1].draw()
        except IndexError:
            pass

    def left_click(self):
        return self.engine.menus[-1].left_click()

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
            return self.revert_to_playing_state()
        else:
            return self.revert_to_playing_state()

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
            return self.revert_to_playing_state()
        else:
            return self.revert_to_playing_state()


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
            return self.revert_to_playing_state()
        else:
            return self.revert_to_playing_state()


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
        flag = False
        if self.engine.menus:
            for menu in self.engine.menus:
                flag = menu.left_click()
                if self.engine.ritual_summon_resource:
                    self.engine.close_menus()
                    acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
                    action_tile = self.engine.board[self.row][self.col]
                    event = CreateResource(self.engine, acting_tile, action_tile)
                    self.engine.add_event(event)
                    self.engine.ritual_summon_resource = None
                    return self.revert_to_playing_state()
        if self.click_valid_square(row, col) and not self.engine.ritual_summon_resource:
            self.row = row
            self.col = col
            menu = ResourceMenu(row, col, self.win, self.engine)
            self.engine.menus.append(menu)
            flag = True
        else:
            return self.revert_to_playing_state()


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
            return True
        elif self.click_valid_square(row, col) and self.selected:
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = ((self.selected.row, self.selected.col), (row, col))
            event = Teleport(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            return self.revert_to_playing_state()
        else:
            return self.revert_to_playing_state()


class PerformSwap(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.engine.close_menus()
        self.first_selected = None
        self.second_selected = None
        self.previously_selected.ritual_squares_list = self.swap_ritual_squares()
        if str(self.previously_selected) == 'assassin':
            self.first_selected = self.previously_selected
            self.previously_selected.ritual_squares_list = self.swap_ritual_squares()


    def __repr__(self):
        return 'swap'

    def draw(self):
        super().draw()
        self.side_bar.draw()
        self.previously_selected.highlight_ritual_squares(self.win)
        self.draw_ritual_at_mouse_position()
        if self.first_selected:
            if str(self.first_selected) == 'assassin':
                return
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
            return self.revert_to_playing_state()
        else:
            return self.revert_to_playing_state()


class PerformLineDestroy(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)
        self.engine.close_menus()
        self.directions = (Constant.UP, Constant.RIGHT, Constant.LEFT, Constant.DOWN)
        self.row = self.previously_selected.row
        self.col = self.previously_selected.col
        mouse_row, mouse_col = Constant.convert_pos(pygame.mouse.get_pos())
        self.up = range(self.row - 1, -1, -1), range(self.col, self.col + 1)
        self.down = range(self.row + 1, Constant.BOARD_HEIGHT_SQ), range(self.col, self.col + 1)
        self.right = range(self.row, self.row + 1), range(self.col + 1, Constant.BOARD_WIDTH_SQ)
        self.left = range(self.row, self.row + 1), range(self.col - 1, -1, -1)

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
            return True
            if self.engine.enemy_player_king_does_not_exist():
                new_state = Winner(self.win, self.engine)
                self.engine.set_state(new_state)
                return True
            else:
                return self.revert_to_playing_state()
        else:
            return self.revert_to_playing_state()


class PerformProtect(Ritual):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(win, engine)
        self.engine.close_menus()
        self.previously_selected.ritual_squares_list = self.protectable_ritual_squares()

    def __repr__(self):
        return 'protect'

    def protectable_ritual_squares(self):
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
            return self.revert_to_playing_state()
        else:
            return self.revert_to_playing_state()


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
            self.selected.portal_image = Constant.IMAGES[self.turn + "_portal"]
            self.previously_selected.ritual_squares_list = self.valid_portal_squares()
            return True
        elif self.click_valid_square(row, col) and self.selected:
            acting_tile = self.engine.board[self.previously_selected.row][self.previously_selected.col]
            action_tile = ((self.selected.row, self.selected.col), (row, col))
            event = Portal(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            return self.revert_to_playing_state()
        else:
            return self.revert_to_playing_state()
