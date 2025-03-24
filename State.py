from __future__ import annotations

from typing import Callable

from GameEvent import *
from Menu import *


def can_inspect_piece(currently_selected: "Unit") -> bool:
    """
    Checks if a piece can be inspected based on the currently selected piece.
    :param currently_selected: The currently selected piece.
    :return: (bool) if the piece can be inspected.
    """
    return currently_selected is not None


def exit_game():
    """
    Calls the Engine's exit_game function to properly terminate the game.
    """
    # Import at module level with a new name
    from Engine import exit_game as engine_exit_game

    # Call the actual exit function from the engine
    engine_exit_game()


def _determine_special_move_type(
        acting_tile: "Tile", action_tile: "Tile", default_type: type
) -> type:
    """
    Determines whether a move involves a portal, a trap, or is a normal move.

    :param acting_tile: The tile from which the action originates.
    :param action_tile: The tile on which the action is performed.
    :param default_type: The default move type if no special condition applies.
    :return: The appropriate move type (portal, trap, or default).
    """

    # Retrieve the piece from the acting tile
    piece: Unit = acting_tile.get_occupying()

    # Check if the action tile contains a portal
    if action_tile.portal:
        return (
            PortalMove
            if default_type == Move
            else (PortalCapture if default_type == Capture else PortalSpawn)
        )

    # Check if the action tile contains a trap
    if action_tile.trap:
        # Determine if the trap is neutralized by a protective piece of the same color
        if not action_tile.is_protected_by_same_color(piece.color):
            return (
                TrapMove
                if default_type == Move
                else (TrapCapture if default_type == Capture else TrapSpawn)
            )

    # Return the default move type if no special conditions apply
    return default_type


def type_of_capture(acting_tile: "Tile", action_tile: "Tile") -> type:
    """
    Determines the type of capture based on the presence of traps or portals.

    :param acting_tile: The tile from which the capture originates.
    :param action_tile: The tile on which the capture is performed.
    :return: The type of capture (TrapCapture, PortalCapture, or Capture).
    """
    return _determine_special_move_type(acting_tile, action_tile, Capture)


def type_of_spawn(
        acting_tile: "Tile", action_tile: "Tile", spawning: str = None
) -> type:
    """
    Determines the type of spawn based on the presence of traps or portals.

    :param spawning: string of spawning piece
    :param acting_tile: The tile from which the spawn originates.
    :param action_tile: The tile on which the spawn is performed.
    :return: The type of spawn (SpawnTrap, TrapSpawn, PortalSpawn, or Spawn).
    """

    # If the engine is currently spawning a trap, return the corresponding spawn type
    if spawning == "trap":
        return SpawnTrap

    return _determine_special_move_type(acting_tile, action_tile, Spawn)


def same_piece_selected(previously_selected: Unit, row: int, col: int) -> bool:
    """
    Checks if the same piece is selected again.
    Returns True if the same piece is selected, False otherwise.
    :param: previously_selected: The piece that was previously selected.
    :param: row: The row index of the selected piece.
    :param: col: The column index of the selected piece.
    :return (bool) if the piece is selected again.
    """
    # No piece selected
    if previously_selected is None:
        return False

    # Check if the positions match
    return previously_selected.get_position() == (row, col)


class State:
    """
    Represents the game state, handling interactions, rendering, and game logic.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the State object with essential game components.

        :param win: The game window surface where everything is drawn.
        :param engine: The game engine managing game logic and events.
        """

        # The game window surface where all visuals are rendered
        self.win: pygame.Surface = win

        # The game engine responsible for handling game logic and events
        self.engine: "Engine" = engine

        # Sidebar element, initially set to None
        self.side_bar: "Optional[SideMenu]" = None

        # Boolean flag indicating whether an object is currently being dragged
        self.dragging: bool = False

        # Stores the initial mouse position when dragging starts
        self.mouse_start_pos: tuple[int, int] | None = None

        # Stores the game piece currently being dragged, initially None
        self.dragging_piece: "Optional[Unit]" = None

        # Dictionary of spawn-able objects, mapping string keys to their respective images
        self.spawnTable: dict[str, pygame.Surface] = (
                Constant.W_BUILDINGS
                | Constant.W_PIECES
                | Constant.B_BUILDINGS
                | Constant.B_PIECES
        )

        # Background paper texture used in the game interface
        self.paper_texture: pygame.Surface = Constant.IMAGES["paper"]

    def draw_piece_at_mouse_cursor(self, pos, piece):
        """
        Draws a piece at the mouse cursor position, centering it properly.
        """
        piece_image = self.spawnTable[(self.engine.turn + "_" + str(piece))]
        piece_rect = piece_image.get_rect(center=pos)
        self.win.blit(piece_image, piece_rect.topleft)

    def __repr__(self):
        raise NotImplementedError("Subclasses must implement __repr__ ")

    def draw_paper_texture(self, surface: pygame.Surface) -> None:
        """
        Draws a texture onto the provided Pygame Surface at coordinates (0, 0),
        using alpha blending with multiplication mode.

        :param surface: The Pygame Surface object to draw onto.
        """
        surface.blit(self.paper_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def scale_paper_texture(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Scales a given surface to match the size of self.paper_texture.

        :param surface: The Pygame Surface object to be scaled.
        :return: A new Pygame Surface object that is a scaled version of the input.
        """
        width = surface.get_width()
        height = surface.get_height()

        # Scale the surface
        scaled_image = pygame.transform.scale(self.paper_texture, (width, height))

        # Convert to proper alpha format if needed
        return scaled_image

    def reset_dragging_piece(self) -> bool:
        """
        Resets the dragging piece to its original position if it was being dragged.
        :return: (bool) True if the dragging piece was reset, False otherwise.
        """
        # Attempt to set dragging piece dragging bool to false.
        try:
            self.dragging_piece.dragging = False
        except AttributeError:
            return False

        # Reset the dragging piece.
        self.dragging_piece = None
        self.dragging = False
        return True

    def handle_input(self, event: pygame.event.Event):
        """
        Processes input events including mouse clicks, dragging, and key presses.

        :param event: The pygame event object containing input details.
        """
        # Handle mouse button press events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the left mouse button (button 1) is pressed
            if event.button == 1:
                # Attempt left-click action, if successful, do nothing further
                if self.left_click():
                    pass
                # Otherwise, attempt to start dragging a piece
                elif self.drag_piece(event.pos):
                    self.dragging = True

            # Check if the right mouse button (button 3) is pressed
            elif event.button == 3:
                # Trigger right-click functionality
                self.right_click()

        # Handle mouse button release events
        elif event.type == pygame.MOUSEBUTTONUP:
            # Check if the left mouse button (button 1) is released
            if event.button == 1 and self.dragging:
                # Perform drop action for dragged piece
                self.drop_piece(event.pos)
                # Reset dragging state
                self.dragging = False

        # Handle mouse movement events
        elif event.type == pygame.MOUSEMOTION:
            # Update the game based on mouse movement (e.g., hover effects)
            self.mouse_move()

        # Handle key press events
        elif event.type == pygame.KEYDOWN:
            # Check if the Tab key is pressed
            if event.key == pygame.K_TAB:
                self.tab()
            # Check if the Enter or Space key is pressed
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.enter()
            # Check if the 'M' key is pressed
            elif event.key == pygame.K_m:
                self.m()
            # Check if the 'C' key is pressed
            elif event.key == pygame.K_c:
                self.c()
            # Check if the Escape key is pressed
            elif event.key == pygame.K_ESCAPE:
                self.esc()

    def type_of_move(self, acting_tile: "Tile", action_tile: "Tile") -> type:
        """
        Determines the type of move based on the presence of traps or portals.

        :param acting_tile: The tile from which the move originates.
        :param action_tile: The tile on which the move is performed.
        :return: The type of move (TrapMove, PortalMove, or Move).
        """
        return _determine_special_move_type(acting_tile, action_tile, Move)

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

    def side_bar_input(self, input_type: str) -> bool:
        """
        Processes input events for the sidebar, if it is active.
        :param input_type: (str) The type of input event to process.
        :return: (bool) True if the input was processed, False otherwise.
        """
        # Check if the sidebar exists
        if self.side_bar:
            # Get the function to call based on the input type
            function = getattr(self.side_bar, input_type)
            # Call the function and return the result
            return function()

    def menu_input(self, input_type: str) -> bool:
        """
        Processes input events for the active menu, if one is open.
        :param input_type: (str) The type of input event to process.
        :return: (bool) True if the input was processed, False otherwise.
        """
        # Check if there are active menus
        if self.engine.menus:
            # Loop through each active menu
            for menu in self.engine.menus:
                # Get the function to call based on the input type
                function: callable = getattr(menu, input_type)
                # Call the function and return the result
                return function()

    def draw(self):
        """
        Super method of draw, can be overridden by subclasses.
        Draws the board by default
        """
        self.win.fill(Constant.MENU_COLOR)
        self.engine.draw(self.win)

    def enter(self):
        """
        Super method of enter, can be overridden by subclasses.
        By default, sets state to playing and attempts to change the turn
        """
        # Set state to playing
        self.revert_to_playing_state()
        # Get player object
        player = self.engine.players[self.engine.turn]
        # Check if the player has any actions remaining
        number_of_actions_if_player_has_done_nothing = (
                player.total_additional_actions_this_turn
                + Constant.DEFAULT_ACTIONS_REMAINING
        )
        # Force the player to use their actions if they have any before changing turn
        if number_of_actions_if_player_has_done_nothing > player.actions_remaining:
            self.engine.change_turn()
            return True

    def drag_piece(self, pos: Tuple[int, int]):
        """
        Super method of drag piece, can be overridden by subclasses.
        By default, do nothing.
        :param pos: mouse position at current drag frame
        """
        pass

    def drop_piece(self, pos: Tuple[int, int]):
        """
        Super method of drop piece, can be overridden by subclasses.
        By default, do nothing.
        :param pos: mouse position at drop frame
        """
        pass

    def right_click(self):
        """
        Super method of right click, can be overridden by subclasses.
        By default, do nothing.
        """
        pass

    def tab(self) -> bool:
        """
        Super method of tab, can be overridden by subclasses.
        By default, attempt to undo the last move.
        :return: (bool) True if the undo was successful, False otherwise.
        """

        # Get the previously selected piece.
        prev = self.engine.update_previously_selected()
        # If prev exists, reset selected and revert to playing state.
        if prev is not None:
            self.engine.reset_selected()
            self.revert_to_playing_state()

        # Attempt to undo the last move.
        try:
            return self.engine.undo_last_event()
        except IndexError:
            return False

    def m(self):
        """
        Super method of 'm' key press, can be overridden by subclasses.
        By default, do nothing.
        """
        pass

    def c(self):
        """
        Super method of 'c' key press, can be overridden by subclasses.
        By default, do nothing.
        """
        pass

    def esc(self):
        self.engine.pause()

    def mouse_move(self):
        """
        Super method of mouse move, can be overridden by subclasses.
        By default, do nothing.
        """
        pass

    def left_click(self):
        """
        Super method of left click, can be overridden by subclasses.
        By default, do nothing.
        """
        pass

    def revert_to_starting_state(self, first: bool = False):
        """
        Revert game state to Starting state, before a player has chosen their color.
        :param first: Flag to indicate if it is the first turn of the game. This is used in StartingSpawn.
        """
        # Create new state object
        new_state = Starting(self.win, self.engine, True)

        # Reset spawning flag
        self.engine.spawning = None

        # If first is True, set the engine's first flag to True
        if first:
            self.engine.first = first

        # Set engine state to new state
        self.engine.set_state(new_state)

    def remove_top_state(self):
        """
        Remove the top state from the engine's state stack.
        """
        del self.engine.state[-1]


class Settings(State):
    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the Pause state with buttons and UI elements.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        super().__init__(win, engine)  # Call parent class initializer

        # Scale paper texture to size of window
        self.paper_texture = self.scale_paper_texture(self.win)

        # Store font color
        self.color = Constant.turn_to_color[self.engine.turn]

        # Store window dimensions
        self.window_width = self.win.get_width()
        self.window_height = self.win.get_height()

        # Set the font size based on a constant square size
        self.font_size = round(Constant.SQ_SIZE * 1)

        # Load the font from the specified file
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Define button labels
        buttons = ["music:", "sounds:", "back"]

        # Define flags for buttons on and off
        flags = ["off", "on"]

        # Create surfaces for each button text
        self.button_surfaces = [
            self.font.render(button, True, self.color) for button in buttons
        ]

        # Create surfaces for each button text
        self.flag_surfaces = [
            self.font.render(flag, True, self.color) for flag in flags
        ]

        # Get button dimensions (assuming all buttons have the same size)
        self.button_width = self.button_surfaces[1].get_width()
        self.button_height = self.button_surfaces[1].get_height()

        # Create a highlight rectangle (transparent overlay) for hovering effect
        self.square = pygame.Surface((self.button_width, self.button_height))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Boolean list to track which button is currently highlighted
        self.button_highlighted = [False] * len(buttons)

        # List to store button positions for consistent layout
        self.button_positions = []

        # List for which flags are on or off
        self.current_flags = [int(Constant.MUSIC_ON), int(Constant.SOUND_EFFECTS_ON)]

        # List to store flag positions for consistent layout
        self.flag_positions = []

        # Compute initial button positions
        self.compute_button_positions()

        # Compute initial flag positions
        self.compute_flag_positions()

    def compute_flag_positions(self):
        """
        Computes and stores the positions for each flag next to the corresponding button.
        """
        # Set an offset to position the flag to the right of the button
        flag_offset = Constant.SQ_SIZE

        # Compute positions for music and sound flags
        for i in range(2):  # Only for 'music:' and 'sounds:' buttons
            button_x, button_y = self.button_positions[i]  # Get button position
            flag_x = (
                    button_x + self.button_width + flag_offset
            )  # Position flag to the right
            flag_y = (
                    button_y
                    + (self.button_height - self.flag_surfaces[0].get_height()) // 2
            )  # Align vertically
            self.flag_positions.append((flag_x, flag_y))

    def compute_button_positions(self):
        """
        Computes and stores the positions for each button to ensure consistent centering.
        """
        # Calculate total height occupied by all buttons (including spacing)
        total_height = (
                len(self.button_surfaces) * self.button_height
                + (len(self.button_surfaces) - 1) * 10
        )

        # Determine the starting y-position to center all buttons vertically
        start_y = (self.window_height - total_height) // 2

        # Compute positions for each button and store them
        self.button_positions = [
            (
                (self.window_width - self.button_width) // 2,
                start_y + i * (self.button_height + 10),
            )
            for i in range(len(self.button_surfaces))
        ]

    def draw(self):
        """
        Draws the settings menu, including buttons, highlights, and flags.
        """
        # Fill the background with the menu color
        self.win.fill(Constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.draw_paper_texture(self.win)

        # Iterate over each button and draw it at its computed position
        for i, (button_x, button_y) in enumerate(self.button_positions):
            # If the button is highlighted, draw the highlight rectangle first
            if self.button_highlighted[i]:
                self.win.blit(self.square, (button_x, button_y))

            # Draw the button text
            self.win.blit(self.button_surfaces[i], (button_x, button_y))

        # Draw flags next to music and sounds buttons
        for i in range(2):  # Only for 'music:' and 'sounds:' buttons
            self.win.blit(
                self.flag_surfaces[self.current_flags[i]], self.flag_positions[i]
            )

    def mouse_move(self):
        """
        Tracks mouse movement, updates button highlight states, and changes the mouse cursor
        when hovering over a button.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Flag to track if the cursor is over any button
        cursor_over_button = False

        # Iterate over all buttons and check if the mouse is hovering over any
        for i, (button_x, button_y) in enumerate(self.button_positions):
            # Create a rectangle representing the button's clickable area
            button_rect = pygame.Rect(
                button_x, button_y, self.button_width, self.button_height
            )

            # Update highlight status
            if button_rect.collidepoint(mouse_x, mouse_y):
                self.button_highlighted[i] = True
                cursor_over_button = True  # Set flag if mouse is over a button
            else:
                self.button_highlighted[i] = False

        # Change cursor based on whether it is over a button
        if cursor_over_button:
            pygame.mouse.set_cursor(
                pygame.SYSTEM_CURSOR_HAND
            )  # Hand cursor for interaction
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Default cursor

    def __repr__(self) -> str:
        """
        Return a string representation of the class.
        :return: A string representing the class.
        """
        return "settings"

    def enter(self):
        """
        Override default enter method to do nothing.
        """
        pass

    def tab(self):
        """
        Simulate the 'tab' key action.
        """
        self.remove_top_state()

    def right_click(self):
        """
        Simulate a right-click action.
        """
        self.remove_top_state()

    def esc(self):
        """
        Simulate the 'esc' key action.
        """
        self.remove_top_state()

    def left_click(self):
        """
        Handles left mouse clicks. If a button is clicked, calls button_selected().
        """
        # Get current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Iterate through all buttons to check if one was clicked
        for i, (button_x, button_y) in enumerate(self.button_positions):
            # Create a rectangle representing the button's clickable area
            button_rect = pygame.Rect(
                button_x, button_y, self.button_width, self.button_height
            )

            # Check if mouse is inside button
            if button_rect.collidepoint(mouse_x, mouse_y):
                # Call button_selected with the clicked button index
                self.button_selected(i)
                # Stop checking once we find a clicked button
                break

    def button_selected(self, button_index: int):
        """
        Handles actions when a button is clicked.

        :param button_index: The index of the clicked button.
        """
        # If the "music" button was clicked
        if button_index == 0:
            Constant.MUSIC_ON = not Constant.MUSIC_ON
            self.current_flags[0] = int(Constant.MUSIC_ON)
            Constant.load_music(Constant.MUSIC_ON)

        # If the "sounds" button was clicked
        elif button_index == 1:
            Constant.SOUND_EFFECTS_ON = not Constant.SOUND_EFFECTS_ON
            self.current_flags[1] = int(Constant.SOUND_EFFECTS_ON)

        # If the "back" button was clicked
        elif button_index == 2:
            # Return to previous state
            self.esc()


class Pause(State):
    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the Pause state with buttons and UI elements.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        super().__init__(win, engine)  # Call parent class initializer

        # Scale paper texture
        self.paper_texture = self.scale_paper_texture(self.win)

        # Store font color
        self.color = Constant.turn_to_color[self.engine.turn]

        # Store window dimensions
        self.window_width = self.win.get_width()
        self.window_height = self.win.get_height()

        # Set the font size based on a constant square size
        self.font_size = round(Constant.SQ_SIZE * 1)

        # Load the font from the specified file
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Define button labels
        buttons = ["return to game", "how to play", "reset board", "settings", "quit"]

        # Create surfaces for each button text
        self.button_surfaces = [
            self.font.render(button, True, self.color) for button in buttons
        ]

        # Get button dimensions (assuming all buttons have the same size)
        self.button_width = self.button_surfaces[0].get_width()
        self.button_height = self.button_surfaces[0].get_height()

        # Create a highlight rectangle (transparent overlay) for hovering effect
        self.square = pygame.Surface((self.button_width, self.button_height))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Boolean list to track which button is currently highlighted
        self.button_highlighted = [False] * len(buttons)

        # List to store button positions for consistent layout
        self.button_positions = []

        # Compute initial button positions
        self.compute_button_positions()

    def compute_button_positions(self):
        """
        Computes and stores the positions for each button to ensure consistent centering.
        """
        # Calculate total height occupied by all buttons (including spacing)
        total_height = (
                len(self.button_surfaces) * self.button_height
                + (len(self.button_surfaces) - 1) * 10
        )

        # Determine the starting y-position to center all buttons vertically
        start_y = (self.window_height - total_height) // 2

        # Compute positions for each button and store them
        self.button_positions = [
            (
                (self.window_width - self.button_width) // 2,
                start_y + i * (self.button_height + 10),
            )
            for i in range(len(self.button_surfaces))
        ]

    def draw(self):
        """
        Draws the pause menu, including buttons and their highlights.
        """
        # Fill the background with the menu color
        self.win.fill(Constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.draw_paper_texture(self.win)

        # Iterate over each button and draw it at its computed position
        for i, (button_x, button_y) in enumerate(self.button_positions):
            # If the button is highlighted, draw the highlight rectangle first
            if self.button_highlighted[i]:
                self.win.blit(self.square, (button_x, button_y))

            # Draw the button text on top of the highlight (or directly if not highlighted)
            self.win.blit(self.button_surfaces[i], (button_x, button_y))

    def mouse_move(self):
        """
        Tracks mouse movement, updates button highlight states, and changes the mouse cursor
        when hovering over a button.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Flag to track if the cursor is over any button
        cursor_over_button = False

        # Iterate over all buttons and check if the mouse is hovering over any
        for i, (button_x, button_y) in enumerate(self.button_positions):
            # Create a rectangle representing the button's clickable area
            button_rect = pygame.Rect(
                button_x, button_y, self.button_width, self.button_height
            )

            # Update highlight status
            if button_rect.collidepoint(mouse_x, mouse_y):
                self.button_highlighted[i] = True
                cursor_over_button = True  # Set flag if mouse is over a button
            else:
                self.button_highlighted[i] = False

        # Change cursor based on whether it is over a button
        if cursor_over_button:
            pygame.mouse.set_cursor(
                pygame.SYSTEM_CURSOR_HAND
            )  # Hand cursor for interaction
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Default cursor

    def __repr__(self) -> str:
        """
        Return a string representation of the class.
        :return: A string representing the class.
        """
        return "pause"

    def enter(self):
        """
        Override default enter method to do nothing.
        """
        pass

    def tab(self):
        """
        Simulate the 'tab' key action.
        """
        self.remove_top_state()

    def right_click(self):
        """
        Simulate a right-click action.
        """
        self.remove_top_state()

    def esc(self):
        """
        Simulate the 'esc' key action.
        """
        self.remove_top_state()

    def left_click(self):
        """
        Handles left mouse clicks. If a button is clicked, calls button_selected().
        """
        # Get current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Iterate through all buttons to check if one was clicked
        for i, (button_x, button_y) in enumerate(self.button_positions):
            # Create a rectangle representing the button's clickable area
            button_rect = pygame.Rect(
                button_x, button_y, self.button_width, self.button_height
            )

            # Check if mouse is inside button
            if button_rect.collidepoint(mouse_x, mouse_y):
                # Call button_selected with the clicked button index
                self.button_selected(i)
                # Stop checking once we find a clicked button
                break

    def button_selected(self, button_index: int):
        """
        Handles actions when a button is clicked.

        :param button_index: The index of the clicked button.
        """
        # If the "return to game" button was clicked
        if button_index == 0:
            # Return to previous state
            self.esc()

        # If the "How to Play" button was clicked
        if button_index == 1:
            # Change the game state to "instructions"
            self.engine.state.append(Instructions(self.win, self.engine))

        # If the "Reset Board" button was clicked
        elif button_index == 2:
            # Reset the game board
            self.engine.reset_board()
            self.engine.set_state("starting")

        # If the "Settings" button was clicked
        elif button_index == 3:
            # Change the game state to "settings"
            self.engine.state.append(Settings(self.win, self.engine))

        # If the "Quit" button was clicked
        elif button_index == 4:
            exit_game()


class MainMenu(State):
    def __init__(self, win, engine, splash_screen):
        super().__init__(win, engine)
        # Paper texture
        self.paper_texture = self.scale_paper_texture(self.win)

        # Menu logo and its position
        self.main_menu_logo = splash_screen.logo_image
        self.logo_position = splash_screen.logo_position
        self.color = Constant.turn_to_color[splash_screen.logo_color]
        self.logo_position_y = None
        self.button_display_y = None

        # Window dimensions and font settings
        self.window_width = self.win.get_width()
        self.window_height = self.win.get_height()
        self.font_size = round(Constant.SQ_SIZE * 1)
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Button text options
        buttons = ["play", "how to play", "settings", "quit"]

        # Create surfaces for each button text
        self.button_surfaces = [
            self.font.render(button, True, self.color) for button in buttons
        ]

        # Get button dimensions (assuming all buttons have the same size)
        self.button_width = self.button_surfaces[1].get_width()
        self.button_height = self.button_surfaces[1].get_height()

        # Create a highlight rectangle (transparent overlay) for hovering effect
        self.square = pygame.Surface((self.button_width, self.button_height))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.MOVE_SQUARE_HIGHLIGHT_COLOR)

        # Boolean list to track which button is currently highlighted
        self.button_highlighted = [False] * len(buttons)

        # List to store button positions for consistent layout
        self.button_positions = []

        # Compute initial button positions
        self.compute_button_positions()

    def __repr__(self) -> str:
        """
        Returns a string representation of the state.

        :return: The name of the state as a string.
        """

        # The string representation of this state, indicating it's the main menu
        return "main menu"

    def esc(self):
        """
        Handles the escape key press.
        This method is currently unimplemented but can be overridden in subclasses.
        """
        pass

    def enter(self):
        """
        Handles the enter key press.
        This method is currently unimplemented but can be overridden in subclasses.
        """
        pass

    def set_splash(self, splash_screen: "SplashScreen"):
        """
        Sets the splash screen properties, including the logo image, position, and color.

        :param splash_screen: The splash screen containing logo details.
        """

        # Assign the splash screen's logo image to the main menu logo
        self.main_menu_logo = splash_screen.logo_image

        # Set the logo position based on the splash screen settings
        self.logo_position = splash_screen.logo_position

        # Convert the splash screen's logo color to the appropriate in-game color
        self.color = Constant.turn_to_color[splash_screen.logo_color]

    def compute_button_positions(self):
        """
        Calculate the position for each button and store it in the button_positions list.
        The buttons will be centered vertically and spaced evenly horizontally.
        """

        # Place logo at top of screen
        self.logo_position_y = self.window_height // 4

        # Place buttons on the bottom 2/3 of screen
        self.button_display_y = (2 * self.window_height) // 3 - self.button_height // 2

        # Calculate the total width needed for all buttons
        total_buttons_width = len(self.button_surfaces) * self.button_width

        # Calculate the starting X position to center buttons horizontally
        start_x = (self.window_width - total_buttons_width) // 2

        # Calculate each button's position (centered vertically, spaced evenly horizontally)
        for i, button_surface in enumerate(self.button_surfaces):
            button_x = start_x + i * self.button_width
            # Horizontal spacing between buttons
            button_y = self.button_display_y
            # Keep buttons vertically centered
            self.button_positions.append((button_x, button_y))

    def draw(self):
        """
        Draw the main menu with the logo at the top and buttons below it, highlighting
        the active button based on the current mouse position.
        """

        # Fill the background color for the menu
        self.win.fill(Constant.MENU_COLOR)

        # Draw paper texture
        self.draw_paper_texture(self.win)

        # Draw the menu logo at the top center
        self.win.blit(self.main_menu_logo, self.logo_position)

        # Draw each button and apply highlight if active
        for i, (button_x, button_y) in enumerate(self.button_positions):

            # Highlight the button if it's active
            if self.button_highlighted[i]:
                self.win.blit(self.square, (button_x, button_y))

            # Calculate the position to center the text on the button
            text_x = (
                    button_x
                    + (self.button_width - self.button_surfaces[i].get_width()) // 2
            )
            text_y = (
                    button_y
                    + (self.button_height - self.button_surfaces[i].get_height()) // 2
            )

            # Draw the button text centered on the button
            self.win.blit(self.button_surfaces[i], (text_x, text_y))

    def mouse_move(self):
        """
        Detect mouse movement to highlight the button under the cursor and update the mouse cursor.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Track if cursor is set to hand
        cursor_set = False

        # Check each button and update its highlight state
        for i, (button_x, button_y) in enumerate(self.button_positions):
            if (
                    button_x <= mouse_x <= button_x + self.button_width
                    and button_y <= mouse_y <= button_y + self.button_height
            ):
                self.button_highlighted[i] = True
                if not cursor_set:
                    # Set cursor to hand if not already set
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    cursor_set = True
            else:
                self.button_highlighted[i] = False

        if not cursor_set:
            # If no button is highlighted, reset to arrow
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def left_click(self):
        """
        Handle left mouse clicks to select buttons.
        This method checks which button the user clicked and takes appropriate action.
        """

        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Iterate over each button's position and check if the mouse click is within its range
        for i, (button_x, button_y) in enumerate(self.button_positions):

            # Check if the mouse click is within the button's clickable range
            if (
                    button_x <= mouse_x <= button_x + self.button_width
                    and button_y <= mouse_y <= button_y + self.button_height
            ):

                # Perform action based on which button was clicked
                if i == 0:
                    Constant.PLAY_AGAINST_AI = False
                    self.engine.set_state("starting")
                elif i == 1:
                    # How to Play button
                    self.engine.state.append(Instructions(self.win, self.engine))
                elif i == 2:
                    # Settings button
                    self.engine.state.append(Settings(self.win, self.engine))
                elif i == 3:
                    exit_game()


class Instructions(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)

        # Scale paper texture
        self.paper_texture = self.scale_paper_texture(self.win)

        # Determine color for menu
        self.color = Constant.turn_to_color[self.engine.turn]

        # Initialize variables for logo and button positions
        self.logo_position_y = None
        self.button_display_y = None

        # List of images to be shown
        self.images = Constant.INSTRUCTIONS
        self.current_image_index = 0  # Track the current image

        # Obtain window height and width
        self.window_width = self.win.get_width()
        self.window_height = self.win.get_height()

        # Scale images
        self.scale_images()

        # Define the button text options
        buttons = ["<---", "back", "--->"]

        # Set the font size based on a constant square size
        self.font_size = round(Constant.SQ_SIZE * 0.8)

        # Load the font from the specified file
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Create surfaces for each button text
        self.button_surfaces = [
            self.font.render(button, True, self.color) for button in buttons
        ]

        # Get button dimensions (assuming all buttons have the same size)
        self.button_width = self.button_surfaces[0].get_width()
        self.button_height = self.button_surfaces[0].get_height()

        # Create a highlight rectangle (transparent overlay) for hovering effect
        self.square = pygame.Surface((self.button_width, self.button_height))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.MOVE_SQUARE_HIGHLIGHT_COLOR)

        # Boolean list to track which button is currently highlighted
        self.button_highlighted = [False] * len(buttons)

        # List to store button positions for consistent layout
        self.button_positions = []

        # Compute initial button positions
        self.compute_button_positions()

    def compute_button_positions(self):
        """
        Calculate the position for each button and store it in the button_positions list.
        The buttons will be centered and spaced evenly under the image.
        """
        # Calculate the vertical starting position for the buttons
        self.logo_position_y = self.window_height // 4  # Position the logo at the top
        self.button_display_y = (
                self.window_height // 2
                + self.images[self.current_image_index].get_height() // 2
        )

        # Calculate the total width of all the buttons (including spacing)
        button_spacing = 20  # Spacing between buttons
        total_buttons_width = (
                len(self.button_surfaces) * self.button_width
                + (len(self.button_surfaces) - 1) * button_spacing
        )

        # Calculate the starting X position to center the buttons horizontally
        starting_x = (self.window_width - total_buttons_width) // 2

        # Calculate the position of each button and store in button_positions
        for i in range(len(self.button_surfaces)):
            button_x = starting_x + i * (self.button_width + button_spacing)
            self.button_positions.append((button_x, self.button_display_y))

    def mouse_move(self):
        """
        Handle mouse movement and highlight the button under the cursor, changing the cursor accordingly.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cursor_set = False  # Track if cursor is set to hand

        for i, (button_x, button_y) in enumerate(self.button_positions):
            button_rect = pygame.Rect(
                button_x, button_y, self.button_width, self.button_height
            )

            # Highlight the button if the mouse is over it
            if button_rect.collidepoint(mouse_x, mouse_y):
                self.button_highlighted[i] = True
                if not cursor_set:  # Set cursor to hand if not already set
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    cursor_set = True
            else:
                self.button_highlighted[i] = False

        if not cursor_set:  # If no button is highlighted, reset to arrow
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def __repr__(self) -> str:
        """
        Return a string representation of the class.
        :return: A string representing the class.
        """
        return "instructions"

    def enter(self):
        """
        Override default enter method to do nothing.
        """
        pass

    def tab(self):
        """
        Simulate the 'tab' key action.
        """
        self.remove_top_state()

    def right_click(self):
        """
        Simulate a right-click action.
        """
        self.remove_top_state()

    def esc(self):
        """
        Simulate the 'esc' key action.
        """
        self.remove_top_state()

    def draw(self):
        """
        Draw the How to Play screen with the image and buttons, applying the highlight effect for buttons.
        """
        # Fill the background color
        self.win.fill(Constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.draw_paper_texture(self.win)

        # Draw the current image at the center of the screen
        current_image = self.images[self.current_image_index]
        image_rect = current_image.get_rect(
            centerx=self.window_width // 2, top=Constant.SQ_SIZE
        )
        self.win.blit(current_image, image_rect)

        # Draw each button and apply highlight if active
        for i, (button_x, button_y) in enumerate(self.button_positions):
            # Draw highlight if the button is active
            if self.button_highlighted[i]:
                self.win.blit(self.square, (button_x, button_y))

            # Draw the button text
            self.win.blit(self.button_surfaces[i], (button_x, button_y))

    def left_click(self):
        """
        Handle the left click for navigating through images and the back button.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if any button is clicked
        for i, (button_x, button_y) in enumerate(self.button_positions):
            button_rect = pygame.Rect(
                button_x, button_y, self.button_width, self.button_height
            )

            if button_rect.collidepoint(mouse_x, mouse_y):
                if i == 0:  # Left arrow
                    self.current_image_index = (self.current_image_index - 1) % len(
                        self.images
                    )
                elif i == 1:  # Back button
                    self.esc()
                elif i == 2:  # Right arrow
                    self.current_image_index = (self.current_image_index + 1) % len(
                        self.images
                    )

    def scale_images(self):
        """
        Scale each image in self.images to 2/3 of its original size while preserving the aspect ratio.
        """
        scaled_images = {}

        # Loop through each image in the dictionary
        for key, value in self.images.items():
            # Get the original dimensions of the image
            original_width, original_height = value.get_size()

            # Calculate the new dimensions (2/3 of the original size)
            new_width = self.window_width * 3 // 4
            new_height = self.window_height * 3 // 4

            # Scale the image while preserving the aspect ratio
            scaled_image = pygame.transform.scale(value, (new_width, new_height))

            # Store the scaled image
            scaled_images[key] = scaled_image

        # Update self.images to be the scaled images
        self.images = scaled_images


class Inspector(State):
    """
    Represents the Inspector state, which allows players to inspect pieces on the board.

    This state enables selecting a piece, viewing its possible moves, and switching back to
    the main game state when necessary.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine", currently_selected: Unit):
        """
        Initializes the Inspector state.

        :param win: The game window surface.
        :param engine: The game engine handling state and logic.
        :param currently_selected: The piece that is currently being inspected.
        """

        # Initialize the base State class
        super().__init__(win, engine)

        # Store the currently selected piece
        self.currently_selected = currently_selected

        # Initialize the sidebar for displaying piece information
        self.side_bar = PieceInspector(win, engine, currently_selected)

    def __repr__(self) -> str:
        """
        Returns a string representation of this state.

        :return: The name of this state as a string.
        """

        # Identifies this state as the "inspector" state
        return "inspector"

    def draw(self):
        """
        Draws the inspector state, including the main game and sidebar elements.
        """

        # Draw the base state (such as the board)
        super().draw()

        # Draw the sidebar displaying information about the inspected piece
        self.side_bar.draw()

    def left_click(self):
        """
        Handles left-click input by reverting to the playing state.

        :return: The result of reverting to the playing state.
        """

        # Exit the inspector state and return to normal gameplay
        return self.revert_to_playing_state()

    def select(self, row: int, col: int):
        """
        Selects a new piece to inspect.

        :param row: The row index of the selected piece.
        :param col: The column index of the selected piece.
        """

        # Retrieve the piece at the specified board position
        self.currently_selected = self.engine.get_occupying(row, col)

        # Update available moves for the new selection
        self.engine.update_moves()

        # Enable move display for the currently selected piece
        self.currently_selected.display_moves = True

    def tab(self):
        """
        Handles the Tab key press by reverting to the playing state.
        """

        # Exit the inspector state and return to normal gameplay
        self.revert_to_playing_state()

    def right_click(self):
        """
        Handles right-click input by reverting to the playing state.
        """

        # Exit the inspector state and return to normal gameplay
        self.revert_to_playing_state()

    def get_piece_inspected(self) -> Unit:
        """
        Retrieves the currently inspected piece.

        :return: The piece currently being inspected.
        """

        # Return the piece currently selected in the inspector
        return self.currently_selected

    def m(self):
        """
        Handles the 'M' key press, allowing the player to switch to another piece for inspection.

        If the player clicks on a different piece, the inspector updates. If the same piece is
        selected, or if an un-inspect-able area is clicked, the game reverts to the playing state.
        """

        # Get the row and column based on the current mouse position
        row, col = Constant.convert_pos(pygame.mouse.get_pos())

        # Retrieve the piece at the specified board position
        selected_piece = self.engine.get_occupying(row, col)

        # If the selected piece is not already being inspected
        if selected_piece is not self.currently_selected:
            # Check if the piece can be inspected
            if can_inspect_piece(selected_piece):
                # Reset the currently selected piece in the engine
                self.engine.reset_selected()

                # Update the sidebar with the new piece's information
                self.side_bar = PieceInspector(self.win, self.engine, selected_piece)

                # Update the currently selected piece
                self.select(row, col)
            else:
                # If the piece is not inspect-able, revert to normal gameplay
                self.revert_to_playing_state()
        else:
            # If the player selects the same piece again, revert to normal gameplay
            self.revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement within the inspector state.
        This method is currently unimplemented but can be overridden in subclasses.
        """
        pass


class Playing(State):
    """
    Represents the main game-playing state where players can move pieces, interact with the board,
    and access in-game menus.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the 'Playing' state.

        :param win: The game window surface.
        :param engine: The game engine handling state and logic.
        """

        # Initialize the base State class
        super().__init__(win, engine)

        # Create the HUD (side bar) for this state
        self.side_bar = Hud(win, engine)

        # Store contextual menu information if applicable
        self.contextual = None

    def __repr__(self) -> str:
        """
        Returns a string representation of this state.

        :return: The name of this state as a string.
        """

        # Identifies this state as the "playing" state
        return "playing"

    def drag_piece(self, pos: Tuple[int, int]) -> bool:
        """
        Initiates the dragging of a game piece if conditions are met.

        :param pos: The position (x, y) of the mouse click.
        :return: True if a piece is successfully selected for dragging, False otherwise.
        """

        # Prevent piece movement if menus are open
        if not self.engine.menus:
            # Convert pixel position to board coordinates
            row, col = Constant.convert_pos(pos)

            # Retrieve the piece at the selected board position
            currently_selected = self.engine.get_occupying(row, col)

            # Check if the piece can be selected for dragging
            if self.can_select_piece(currently_selected):
                # Store the piece being dragged
                self.dragging_piece = currently_selected

                # Set the piece to dragging mode
                currently_selected.dragging = True

                # Change the mouse cursor to indicate dragging
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)

                # Select the piece and return success
                return self.select_piece(currently_selected)

            else:
                # If the piece cannot be selected, reset dragging state
                self.reset_dragging_piece()

        return False  # Dragging did not occur

    def drop_piece(self, pos: Tuple[int, int]):
        """
        Handles the dropping of a dragged piece onto a new board position.

        :param pos: The position (x, y) where the piece is dropped.
        """

        # Prevent piece dropping if menus are open
        if not self.engine.menus:
            # Convert pixel position to board coordinates
            row, col = Constant.convert_pos(pos)

            # Ensure a piece was being dragged
            if self.dragging:
                # Attempt to select the new position
                if not self.select(row, col):
                    # If no valid selection, reset the selected piece
                    self.engine.reset_selected()

            # Reset dragging state
            self.reset_dragging_piece()

            # Restore the mouse cursor to default
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def can_swap_to_square(
            self, previously_selected: Optional["Piece"], row: int, col: int
    ) -> bool:
        """
        Checks if the previously selected piece can swap to the target square.

        :param previously_selected: The piece that was previously selected.
        :param row: The target row to move to.
        :param col: The target column to move to.
        :return: True if the piece can swap to the target square, False otherwise.
        """

        # If no piece is selected or the piece cannot act, the move is invalid
        if not previously_selected or not previously_selected.can_act():
            return False

        # If the player cannot perform an action, the move is invalid
        if not self.engine.player_can_do_action(self.engine.turn):
            return False

        # If the target square is not in the swap list of the selected piece, return False
        if (row, col) not in previously_selected.swap_squares_list:
            return False

        # The piece can swap to the target square
        return True

    def can_move_to_square(
            self, previously_selected: Optional["Piece"], row: int, col: int
    ) -> bool:
        """
        Checks if the previously selected piece can move to the specified square.

        :param previously_selected: The piece that was previously selected.
        :param row: The target row to move to.
        :param col: The target column to move to.
        :return: True if the move is valid, False otherwise.
        """

        # If no piece is selected or the piece has no actions left, the move is invalid
        if not previously_selected or previously_selected.actions_remaining == 0:
            return False

        # If the player cannot perform an action, the move is invalid
        if not self.engine.player_can_do_action(self.engine.turn):
            return False

        # If the target square is not in the piece's move list, the move is invalid
        if (row, col) not in previously_selected.move_squares_list:
            return False

        # If the square is already occupied, the move is invalid
        if self.engine.get_occupying(row, col) is not None:
            return False

        # The move is valid
        return True

    def can_select_piece(self, currently_selected: Optional["Piece"]) -> bool:
        """
        Checks if a piece can be selected based on its properties and the current game state.

        :param currently_selected: The piece being considered for selection.
        :return: True if the piece can be selected, False otherwise.
        """

        # If dragging is in progress, pieces cannot be selected
        if self.dragging:
            return False

        # Ensure that the selected object is indeed a piece
        if not isinstance(currently_selected, Piece):
            return False

        # Ensure the piece belongs to the current player
        if self.engine.turn != currently_selected.color:
            return False

        # Ensure the piece can still act (i.e., has actions remaining)
        if not currently_selected.can_act():
            self.engine.set_popup_reason("piece_action")
            return False

        # Ensure the player can perform an action
        if not self.engine.player_can_do_action(self.engine.turn):
            return False

        # The move is valid
        return True

    def can_capture_piece(
            self,
            previously_selected: Optional["Piece"],
            row: int,
            col: int,
            currently_selected: Optional["Piece"],
    ) -> bool:
        """
        Checks if the previously selected piece can capture the piece on the target square.

        :param previously_selected: The piece that was previously selected for capturing.
        :param row: The target row to capture a piece from.
        :param col: The target column to capture a piece from.
        :param currently_selected: The piece currently occupying the target square.
        :return: True if the capture is valid, False otherwise.
        """

        # If no piece is selected or the piece has no actions left, the capture is invalid
        if not previously_selected or previously_selected.actions_remaining == 0:
            return False

        # If the player cannot perform an action, the capture is invalid
        if not self.engine.player_can_do_action(self.engine.turn):
            return False

        # If the target square is not in the piece's capture list, the capture is invalid
        if (row, col) not in previously_selected.capture_squares_list:
            return False

        # If no piece is present or the piece is of the same color, the capture is invalid
        if (
                currently_selected is None
                or currently_selected.get_color() == previously_selected.get_color()
        ):
            return False

        # The capture is valid
        return True

    def select(self, row: int, col: int) -> bool:
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
            return True

        if self.can_swap_to_square(previously_selected, row, col):
            self.perform_swap(previously_selected, row, col)
            return True

        # Check if the same piece is selected again (deselect it)
        if same_piece_selected(previously_selected, row, col):
            self.engine.reset_selected()
            return True

        # Check if a new piece can be selected
        if self.can_select_piece(currently_selected):
            self.select_piece(currently_selected)
            return True

        # Check if the piece can capture another piece
        if self.can_capture_piece(previously_selected, row, col, currently_selected):
            self.perform_capture(previously_selected, row, col)
            return True

        return False

    def _perform_action(
            self,
            previously_selected: "Piece",
            row: int,
            col: int,
            action_type: Callable[["Tile", "Tile"], type],
    ):
        """
        General method to perform an action (move, swap, capture) by creating an event and updating the game state.

        :param previously_selected: The piece being moved, swapped, or captured.
        :param row: The target row to perform the action on.
        :param col: The target column to perform the action on.
        :param action_type: The type of action (Move, Swap, Capture).
        """
        # Get the previous position of the selected piece
        prev_position = previously_selected.get_position()

        # Get the acting tile based on the piece's previous position
        acting_tile = self.engine.board[prev_position[0]][prev_position[1]]

        # Get the action tile at the specified row and column
        action_tile = self.engine.board[row][col]

        # Determine the action type (Move, Swap, Capture)
        action_class = action_type(acting_tile, action_tile)

        # Create the event based on the action type
        event = action_class(self.engine, acting_tile, action_tile)

        # Add the created event to the engine to update the game state
        self.engine.add_event(event)

        # Reset the selected piece after the action is performed
        self.engine.reset_selected()

    def perform_move(self, previously_selected: "Piece", row: int, col: int):
        """
        Performs the move action by creating an event and updating the game state.

        :param previously_selected: The piece being moved.
        :param row: The target row for the move.
        :param col: The target column for the move.
        """
        # Call the general perform action method with the appropriate action type (Move)
        self._perform_action(previously_selected, row, col, self.type_of_move)

    def perform_capture(self, previously_selected: "Piece", row: int, col: int):
        """
        Performs the capture action by creating an event and updating the game state.

        :param previously_selected: The piece performing the capture.
        :param row: The target row for the capture.
        :param col: The target column for the capture.
        """
        # Call the general perform action method with the appropriate action type (Capture)
        self._perform_action(previously_selected, row, col, type_of_capture)

    def select_piece(self, currently_selected: Unit) -> bool:
        """
        Selects a new piece to move or interact with.
        :param currently_selected: Unit which will be set to selected
        :return: (bool) True if the piece is successfully selected, False otherwise.
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

        :return: True if any left click action returns True, otherwise False.
        """
        # Initialize results list to store the outcomes of left click actions
        results = []

        # Handle left click action for the sidebar if it exists
        if self.side_bar:
            results.append(self.side_bar.left_click())

        # Handle left click action for each menu if menus exist
        if self.engine.menus:
            for menu in self.engine.menus:
                results.append(menu.left_click())

        # Return True if any element in results is True
        return any(results)

    def inspect_piece(self):
        """
        Handles the inspection of a piece when a special action is performed (e.g., by pressing a key or right-clicking).
        """
        # Get the mouse position and convert it to board coordinates
        row, col = Constant.convert_pos(pygame.mouse.get_pos())

        # Get the piece under the mouse
        currently_selected = self.engine.get_occupying(row, col)

        # Check if the piece can be inspected
        if can_inspect_piece(currently_selected):
            # Create and switch to the Inspector state
            new_state = Inspector(self.win, self.engine, currently_selected)
            # Select the piece in the Inspector state
            new_state.select(row, col)
            # Switch to the new state
            self.engine.set_state(new_state)

    def right_click(self):
        """
        Handles the right-click action, including interacting with menus and pieces.
        """
        # Handle right-click action for each menu if menus exist
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.right_click()
            return

        # Reset dragging piece and selected piece if dragging
        if self.dragging:
            self.reset_dragging_piece()
            self.engine.reset_selected()
            return

        # Get the mouse position and convert it to board coordinates
        row, col = Constant.convert_pos(pygame.mouse.get_pos())

        # Reset selected piece
        self.engine.reset_selected()

        # Get the piece under the mouse
        piece = self.engine.get_occupying(row, col)

        # Ensure the piece belongs to the current player
        if piece and piece.color == self.engine.turn:
            # Perform right-click action for the piece
            if not piece.right_click(self.engine):
                # If the right-click doesn't result in an action, show a popup menu
                self.engine.create_popup_menu(row, col, self.engine.popup_reason)
                # Revert to the 'playing' state
                self.revert_to_playing_state()
            else:
                try:
                    # Create ability menu for pieces with more than 1 ability
                    self.engine.create_contextual_menu(
                        row, col, self.win, piece.contextual_options
                    )

                    # Immediately click into the menu if there is only one option
                    if len(piece.contextual_options) == 1 and str(piece) not in [
                        "queen",
                        "king",
                    ]:
                        self.engine.menus[-1].left_click()
                except AttributeError:
                    pass

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
        if can_inspect_piece(currently_selected):
            # Create a new Inspector state and pass the piece to inspect
            new_state = Inspector(self.win, self.engine, currently_selected)

            # Select the piece in the new Inspector state (this may trigger further actions like showing details)
            new_state.select(row, col)

            # Switch to the Inspector state to inspect the piece
            self.engine.set_state(new_state)

    def mouse_move(self):
        """
        Handles mouse movement. It processes game board input, checks if the mouse is within
        the bounds of any clickable pieces, and updates the cursor accordingly.
        """

        # Process menu input (if any)
        self.menu_input("mouse_move")

        # Check if mouse is inside any active menu or bounds (if applicable)
        self.mouse_in_menu_bounds()

        # Process sidebar input (if any)
        self.side_bar_input("mouse_move")

        # Get current mouse x and y coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is within the board boundaries
        if (
                0 <= mouse_x < Constant.BOARD_WIDTH_PX
                and 0 <= mouse_y < Constant.BOARD_HEIGHT_PX
        ):
            # Update the cursor based on whether the mouse is hovering over a piece
            self.update_cursor()

    def update_cursor(self):
        """
        Updates the system cursor based on whether the mouse is hovering over a game piece or not.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Initialize flag to track if a clickable piece is hovered
        clickable_piece_hovered = False

        # Loop through all the pieces on the game board
        for piece in self.engine.players[self.engine.turn].pieces:
            # Get the piece's bounding rectangle
            piece_rect = piece.get_rect()

            # Check if the piece can act
            if piece.can_act():
                # Check if the mouse is over the piece
                if piece_rect.collidepoint(mouse_x, mouse_y):
                    clickable_piece_hovered = True
                    break  # No need to check further if we found a hovered piece

        # Update the cursor based on whether a piece is hovered
        if not self.dragging and not self.engine.menus:
            if clickable_piece_hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self):
        """
        Draws the game board, menus, and the sidebar on the window.
        """
        # Call the parent class's draw method (draw the base game state)
        super().draw()

        # Draw each menu if any are open
        for menu in self.engine.menus:
            menu.draw()

        # Draw the sidebar
        self.side_bar.draw()

        # Get the current mouse position
        pos = pygame.mouse.get_pos()

        # Draw the piece at the mouse cursor if dragging
        if self.dragging:
            try:
                self.draw_piece_at_mouse_cursor(pos, self.dragging_piece)
            except KeyError:
                pass


class Starting(State):
    """
    Represents the starting state of the game where players are initialized and resources are set up.
    """

    def __init__(
            self, win: pygame.Surface, engine: "Engine", preserve_resources: bool = False
    ):
        """
        Initializes the Starting state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        :param preserve_resources: Flag to indicate if resources should be preserved.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Set the final spawn flag to False
        self.engine.final_spawn = False

        # Initialize the players dictionary
        self.engine.players = {}

        # Create the white player
        self.engine.create_player("w")

        # Create the black player
        self.engine.create_player("b")

        # Initialize the sidebar with the StartMenu
        self.side_bar = StartMenu(win, engine)

        # If resources should not be preserved
        if not preserve_resources:
            # If the board starts with resources, initialize them
            if Constant.BOARD_STARTS_WITH_RESOURCES:
                self.engine.starting_resources()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Starting state.

        :return: A string representing the Starting state.
        """
        return "starting"

    def left_click(self):
        """
        Handles the left-click action.

        :return: The result of the sidebar's left-click action.
        """
        # Delegate the left-click action to the sidebar
        return self.side_bar.left_click()

    def c(self):
        """
        Handles the 'c' key press action.
        """
        # Transfer to the piece cost screen
        self.engine.transfer_to_piece_cost_screen()

    def mouse_move(self):
        """
        Handles the mouse move action.
        """
        # Delegate the mouse move action to the sidebar
        self.side_bar.mouse_move()

    def tab(self):
        """
        Handles the 'tab' key press action.
        """
        # Reset the game board
        self.engine.reset_board()

        # Set the state to the main menu
        self.engine.set_state("main menu")

    def draw(self):
        """
        Draws the game state.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        self.side_bar.draw()

    def enter(self):
        """
        Handles the enter action.
        """
        pass


class SelectStartingPieces(State):
    """
    Represents the state where players select their starting pieces.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the SelectStartingPieces state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Initialize the base class
        super().__init__(win, engine)

        # Scale paper texture
        self.paper_texture = self.scale_paper_texture(self.win)

        # Set up initial attributes
        self.draw_map = False
        self.pieces = {
            "w": Constant.W_PIECES | Constant.W_BUILDINGS,
            "b": Constant.B_PIECES | Constant.B_BUILDINGS,
        }

        # Get window dimensions
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h

        # Set font size and render description text
        self.font_size = round(Constant.SQ_SIZE * 1)
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.description_text = "select your starting pieces:"
        self.text_surf = self.font.render(
            self.description_text, True, Constant.turn_to_color[self.engine.turn]
        )

        # Set Y-buffer for spacing
        self.y_buffer = round(Constant.SQ_SIZE * 0.55)

        # Calculate initial positions and spacing
        self.initial_x = round(2.5 * self.window_width) // len(
            Constant.SELECTABLE_STARTING_PIECES
        )
        self.x_buffer = self.initial_x
        self.piece_spacing = round(Constant.SQ_SIZE * 1.5)

        # Calculate total height of the grid and starting Y position
        total_height_of_grid = self.y_buffer * 2 * Constant.NUMBER_OF_STARTING_PIECES
        self.initial_y = (self.window_height - total_height_of_grid) // 2

        # Define grid dimensions
        self.cols = len(Constant.SELECTABLE_STARTING_PIECES)
        self.rows = Constant.NUMBER_OF_STARTING_PIECES + Constant.NUMBER_OF_BONUS_PIECES

        # Initialize the selection matrix (3D list to track piece status)
        self.selection_matrix = [
            [[0 for _ in range(3)] for _ in range(self.cols)] for _ in range(self.rows)
        ]

        # Set instruction text and surfaces
        self.instruction_text = [
            " 'tab' to go back",
            " 'space bar' to confirm selection",
            " 'right click' to view the map",
            " 'right click' a piece for more information about it",
        ]
        self.instruction_text_surfaces = []
        self.instruction_text_font_size = Constant.SQ_SIZE // 2
        self.instruction_text_font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.instruction_text_font_size
        )
        for line in self.instruction_text:
            l = self.instruction_text_font.render(
                line, True, Constant.turn_to_color[self.engine.turn]
            )
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
                    self.selection_matrix[r][c][0] = (
                        Constant.SELECTABLE_STARTING_PIECES[c]
                    )

                # Initialize the selection matrix states (highlight and selected status)
                self.selection_matrix[r][c][1] = False  # HIGHLIGHT
                self.selection_matrix[r][c][2] = False  # SELECTED

        # Create a surface for highlighting unused pieces
        self.square = pygame.Surface((Constant.SQ_SIZE, Constant.SQ_SIZE))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def __repr__(self) -> str:
        """
        Returns a string representation of the SelectStartingPieces state.

        :return: A string representing the SelectStartingPieces state.
        """
        return "select starting pieces"

    def drag_piece(self, pos: Tuple[int, int]) -> bool:
        """
        Initiates the dragging of a game piece if conditions are met.

        :param pos: The position (x, y) of the mouse click.
        :return: True if a piece is successfully selected for dragging, False otherwise.
        """
        return True

    def start_drag_selection(self):
        """
        Starts the drag selection process.
        """
        self.dragging = True

    def update_drag_selection(self):
        """
        Updates the selection during the drag process.
        """
        if self.dragging:
            piece_selected = self.piece_selected()
            if piece_selected:
                self.select_piece(piece_selected)

    def end_drag_selection(self):
        """
        Ends the drag selection process.
        """
        self.dragging = False

    def select_piece(self, piece_selected: Tuple[int, int]):
        """
        Selects a piece from the selection matrix.

        :param piece_selected: A tuple containing the row and column of the selected piece.
        """
        # Extract row and column from the selected piece
        r, c = piece_selected[0], piece_selected[1]

        # Deselect any previously selected piece in the same row
        for col in range(self.cols):
            if self.selection_matrix[r][col][2]:
                self.selection_matrix[r][col][2] = False

        # Mark the new piece as selected
        self.selection_matrix[r][c][2] = True

    def left_click(self) -> bool:
        """
        Handles the left-click action to select a piece.

        :return: True if a piece is successfully selected, otherwise False.
        """
        # Get the selected piece based on the current mouse position
        piece_selected = self.piece_selected()

        # If a piece is selected, mark it as selected
        if piece_selected:
            self.select_piece(piece_selected)
            return False

        return False

    def right_click(self):
        """
        Handles the right-click action to view the map or piece information.
        """
        # Close any open menus if they exist
        if self.engine.menus:
            self.engine.close_menus()
            return

        # Get the selected piece based on the current mouse position
        piece_selected = self.piece_selected()

        # Toggle map drawing if no piece is selected or the map is already being drawn
        if not piece_selected or self.draw_map:
            self.draw_map = self.flip_draw_map()
            self.side_bar = Empty(self.win, self.engine)
            return

        # Show piece information if a piece is selected
        if not self.draw_map:
            try:
                row, col = piece_selected
            except TypeError:
                return
            piece = self.selection_matrix[row][col][0]
            menu = PieceDescription(self.win, self.engine, piece)
            self.engine.menus.append(menu)

    def piece_selected(self) -> Optional[Tuple[int, int]]:
        """
        Determines which piece is selected based on the current mouse position.

        :return: A tuple containing the row and column of the selected piece, or None if no piece is selected.
        """
        piece_selected = None
        pos = pygame.mouse.get_pos()
        y_buffer = self.y_buffer
        initial_y = self.initial_y

        # Loop through the selection matrix to find the selected piece
        for r in range(self.rows):
            for c in range(self.cols):
                piece_position = (c * self.piece_spacing + self.initial_x, initial_y)
                if pos[0] in range(
                        piece_position[0], piece_position[0] + Constant.SQ_SIZE
                ):
                    if pos[1] in range(
                            piece_position[1], piece_position[1] + Constant.SQ_SIZE
                    ):
                        piece_selected = (r, c)
            initial_y += y_buffer * 2

        return piece_selected

    def mouse_move(self) -> Optional[Tuple[int, int]]:
        """
        Handles mouse movement to highlight pieces under the cursor.

        :return: A tuple containing the row and column of the highlighted piece, or None if no piece is highlighted.
        """
        piece_selected = None
        pos = pygame.mouse.get_pos()
        y_buffer = self.y_buffer
        initial_y = self.initial_y

        # if we are dragging update selection for drags
        if self.dragging:
            print("Updating drag selection")
            self.update_drag_selection()

        # Loop through the selection matrix to highlight the piece under the cursor
        for r in range(self.rows):
            for c in range(self.cols):
                piece_position = (c * self.piece_spacing + self.initial_x, initial_y)
                if pos[0] in range(
                        piece_position[0], piece_position[0] + Constant.SQ_SIZE
                ):
                    if pos[1] in range(
                            piece_position[1], piece_position[1] + Constant.SQ_SIZE
                    ):
                        self.selection_matrix[r][c][1] = True
                    else:
                        self.selection_matrix[r][c][1] = False
                else:
                    self.selection_matrix[r][c][1] = False
            initial_y += y_buffer * 2

        return piece_selected

    def convert_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Converts a screen position to a grid position.

        :param pos: A tuple containing the x and y coordinates of the screen position.
        :return: A tuple containing the row and column of the grid position.
        """
        row = pos[1] // self.piece_spacing - self.y_buffer
        col = pos[0] // (self.piece_spacing + self.initial_x)
        return row, col

    def draw(self):
        """
        Draws the selection screen for starting pieces or the map if toggled.

        If menus are open, it draws the menus. Otherwise, it draws the selection screen
        with the available pieces and highlights the selected ones.
        """
        if self.engine.menus:
            # Draw each open menu
            for menu in self.engine.menus:
                menu.draw()
            return

        if not self.draw_map:
            # Fill the window with the menu color
            self.win.fill(Constant.MENU_COLOR)

            # Draw paper texture blended with background
            self.draw_paper_texture(self.win)

            # Initialize spacing variables
            y_buffer = self.y_buffer
            initial_x = self.initial_x
            x_buffer = self.initial_x
            piece_spacing = self.piece_spacing
            initial_y = self.initial_y

            # Draw selectable and bonus pieces
            for x in range(
                    Constant.NUMBER_OF_STARTING_PIECES + Constant.NUMBER_OF_BONUS_PIECES
            ):
                if x < Constant.NUMBER_OF_STARTING_PIECES:
                    for p in Constant.SELECTABLE_STARTING_PIECES:
                        piece = self.engine.turn + "_" + p
                        self.win.blit(
                            self.pieces[self.engine.turn][piece], (x_buffer, initial_y)
                        )
                        x_buffer += piece_spacing
                else:
                    for p in Constant.BONUS_STARTING_PIECES:
                        piece = self.engine.turn + "_" + p
                        self.win.blit(
                            self.pieces[self.engine.turn][piece], (x_buffer, initial_y)
                        )
                        x_buffer += piece_spacing

                x_buffer = initial_x
                initial_y += y_buffer * 2

            # Reset initial_y for drawing selection matrix
            initial_y = self.initial_y

            # Draw selection matrix highlights
            for r in range(self.rows):
                for c in range(self.cols):
                    position = (c * self.piece_spacing + self.initial_x, initial_y)
                    if self.selection_matrix[r][c][1]:
                        self.win.blit(self.square, position)
                    if self.selection_matrix[r][c][2]:
                        self.win.blit(self.square, position)
                initial_y += y_buffer * 2

            # Draw instruction text
            self.win.blit(self.text_surf, (20, 0))
            y_buffer = self.initial_y
            for line in self.instruction_text_surfaces:
                description_text_x = 0
                self.win.blit(line, (description_text_x, y_buffer))
                y_buffer += self.instruction_text_height
        else:
            # Draw the map and sidebar
            super().draw()
            self.side_bar.draw()

    def enter(self):
        """
        Handles the enter action to confirm the selection of starting pieces.

        It collects the selected pieces and transfers to the starting spawn state if the selection is valid.
        """
        spawn_list = [Constant.STARTING_PIECES[0]]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.selection_matrix[r][c][2]:
                    spawn_list.append(self.selection_matrix[r][c][0])
        spawn_list.append(Constant.STARTING_PIECES[-1])
        if len(spawn_list) == (
                Constant.NUMBER_OF_STARTING_PIECES
                + len(Constant.STARTING_PIECES)
                + Constant.NUMBER_OF_BONUS_PIECES
        ):
            self.engine.transfer_to_starting_spawn(spawn_list)

    def flip_draw_map(self) -> bool:
        """
        Toggles the draw_map flag.

        :return: The new state of the draw_map flag.
        """
        return not self.draw_map

    def tab(self):
        """
        Handles the 'tab' key press action to revert to the previous state or close menus.

        If menus are open, it closes them. Otherwise, it reverts to the starting state or undoes the last events.
        """
        if self.engine.menus:
            self.engine.close_menus()
            return

        if not self.engine.final_spawn:
            self.engine.players = {}
            self.revert_to_starting_state(self.engine.first)
        else:
            for _ in range(2):
                self.engine.events[-1].undo()
                del self.engine.events[-1]


class StartingSpawn(State):
    """
    Represents the state where players begin spawning their pieces at the start of the game.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the StartingSpawn state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with an empty state
        self.side_bar = Empty(win, engine)

        # Set the first flag to True
        self.first = True

        # Play the start game sound
        self.engine.sounds.play("start_game")

    def __repr__(self) -> str:
        """
        Returns a string representation of the StartingSpawn state.

        :return: A string representing the StartingSpawn state.
        """
        return "start spawn"

    def begin_next_player_piece_select(self):
        """
        Begins the piece selection process for the next player.
        """
        # Create and complete a ChangeTurn event
        event = ChangeTurn(self.engine)
        event.complete()

        # Append the event to the engine's event list
        self.engine.events.append(event)

        # Create a new SelectStartingPieces state and set it in the engine
        new_state = SelectStartingPieces(self.win, self.engine)
        self.engine.set_state(new_state)

        # Reset spawn count and set final spawn flag to True
        self.engine.spawn_count = 0
        self.engine.final_spawn = True

    def end_start_spawning(self):
        """
        Ends the starting spawning phase and transitions to the playing state.
        """
        # Change turn if the constant flag is set
        if Constant.TURN_CHANGE_AFTER_START_SPAWN:
            self.engine.turn = Constant.TURNS[self.engine.turn]

        # Reset selected pieces and their actions
        self.engine.reset_selected()
        self.engine.reset_piece_actions_remaining()

        # Set spawn success to False
        self.engine.spawn_success = False

        # Highlight unused pieces
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Reset player actions and piece limits
        self.engine.reset_player_actions_remaining(self.engine.turn)
        self.engine.reset_piece_limit(self.engine.turn)

        # Update additional actions and piece limits
        self.engine.update_additional_actions()
        self.engine.update_piece_limit()

        # Revert to the playing state
        super().revert_to_playing_state()

    @property
    def get_valid_position(self) -> Tuple[int, int]:
        """
        Gets the valid position of the mouse cursor on the game board.

        :return: A tuple containing the row and column of the valid position.
        """
        # Initialize row and column to -1
        row, col = -1, -1

        # Get the current mouse position
        pos = pygame.mouse.get_pos()

        # Check if the position is within bounds
        if Constant.pos_in_bounds(pos):
            row, col = Constant.convert_pos(pos)

        return row, col

    def create_spawn_event(self, row: int, col: int, first: bool = True):
        """
        Creates a spawn event for a piece at the specified board position.

        :param row: The row index on the board.
        :param col: The column index on the board.
        :param first: A flag indicating if this is the first spawn event.
        """
        # Create a player if this is the first spawn event
        if first:
            self.engine.create_player(self.engine.turn)

        # Get the action tile from the board
        action_tile = self.engine.board[row][col]

        # Update the previously selected piece
        previously_selected = self.engine.update_previously_selected()

        # Determine the acting tile based on the previously selected piece
        if previously_selected:
            acting_tile = self.engine.board[previously_selected.row][previously_selected.col]
        else:
            acting_tile = None

        # Create and complete the spawn event
        event = StartSpawn(self.engine, acting_tile, action_tile)
        event.complete()

        # Reset the selected piece
        self.engine.reset_selected()

        # Append the event to the engine's event list
        self.engine.events.append(event)

        # Find the player's castle and set it for purchasing
        castle_row, castle_col = self.engine.find_player_castle()
        self.engine.set_purchasing(castle_row, castle_col, True)

        # Update the spawn squares
        self.engine.update_spawn_squares()

        # Set the first flag
        self.first = first

        # Increment the spawn count
        self.engine.spawn_count += 1

    def left_click(self):
        """
        Handles the left-click action to spawn a piece or interact with the menu.
        """
        # Get the valid position of the mouse click
        row, col = self.get_valid_position

        # Handle menu input if applicable
        if self.menu_input("left_click"):
            return

        # Update the previously selected piece
        previously_selected = self.engine.update_previously_selected()

        if previously_selected:
            self._handle_previously_selected_piece(previously_selected, row, col)
        else:
            self._handle_no_previously_selected_piece(row, col)

        # Handle spawning and update spawn squares
        self._update_spawn_squares()

    def _handle_previously_selected_piece(self, previously_selected: Unit, row: int, col: int):
        """
        Handles the logic when a piece was previously selected.

        :param previously_selected: The previously selected piece.
        :param row: The row index of the clicked position.
        :param col: The column index of the clicked position.
        """
        # Update the spawn squares for the previously selected piece
        previously_selected.update_spawn_squares(self.engine)

        # Check if the clicked position is in the spawn squares list
        if (row, col) in previously_selected.spawn_squares_list:
            self.create_spawn_event(row, col, False)
        else:
            self.engine.create_popup_menu(row, col, "invalid_start_spawn")

    def _handle_no_previously_selected_piece(self, row: int, col: int):
        """
        Handles the logic when no piece was previously selected.

        :param row: The row index of the clicked position.
        :param col: The column index of the clicked position.
        """
        # Check if the clicked position is a legal starting square
        if self.engine.is_legal_starting_square(row, col):
            self.create_spawn_event(row, col)
        else:
            self.engine.create_popup_menu(row, col, self.engine.popup_reason)

    def _update_spawn_squares(self):
        """
        Updates the spawn squares and handles the end of spawning.
        """
        try:
            # Set the current spawning piece
            self.engine.spawning = self.engine.spawn_list[self.engine.spawn_count]
            # Update the spawn squares
            self.engine.update_spawn_squares()
        except IndexError:
            # Handle the end of spawning
            if self.engine.final_spawn:
                self.end_start_spawning()
            else:
                self.begin_next_player_piece_select()

    def right_click(self):
        """
        Handles the right-click action to undo the last event or transfer to piece selection.
        """
        # Handle menu input if applicable
        if self.menu_input("right_click"):
            return

        # Try to undo the last event or transfer to piece selection
        try:
            # Check if the last event is a ChangeTurn event
            if isinstance(self.engine.events[-1], ChangeTurn):
                self.engine.transfer_to_piece_selection()
            else:
                # Undo the last event and remove it from the event list
                self.engine.events[-1].undo()
                del self.engine.events[-1]
        except IndexError:
            # Handle the case where the turn count display is 0.5
            if self.engine.turn_count_display == 0.5:
                self.engine.transfer_to_piece_selection()

    def draw(self):
        """
        Draws the current game state, including the sidebar and any active menus.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        self.side_bar.draw()

        # Handle menu input for drawing
        if self.menu_input("draw"):
            return

        # Get the current mouse position
        pos = pygame.mouse.get_pos()

        # Calculate the display position for the piece being dragged
        displayPosX = pos[0] - Constant.SQ_SIZE // 2
        displayPosY = pos[1] - Constant.SQ_SIZE // 2

        # Check if the mouse position is within bounds
        if Constant.pos_in_bounds(pos):
            try:
                # Draw the piece being dragged at the calculated position
                self.win.blit(
                    self.spawnTable[(self.engine.turn + "_" + self.engine.spawning)],
                    (displayPosX, displayPosY),
                )
            except TypeError:
                pass

    def mouse_move(self):
        """
        Handles mouse movement events.

        :return: None
        """
        # Handle menu input for mouse movement
        self.menu_input("mouse_move")

        # Check if the mouse is within menu bounds
        self.mouse_in_menu_bounds()

    def enter(self):
        """
        Handles the enter key press event.

        :return: None
        """
        pass

    def tab(self):
        """
        Handles the tab key press event by performing a right-click action.

        :return: None
        """
        self.right_click()


class DebugStart(StartingSpawn):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Empty(win, engine)
        self.first = True
        self.engine.sounds.play("start_game")
        self.spawn_list = Constant.DEBUG_STARTING_PIECES
        self.engine.spawn_list = Constant.DEBUG_STARTING_PIECES
        self.engine.spawning = self.spawn_list[0]

    def __repr__(self):
        return "start spawn"

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
        return "mining"

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
                if (
                        self.engine.has_quarry(row, col)
                        or self.engine.has_gold(row, col)
                        or self.engine.has_sunken_quarry(row, col)
                        or self.engine.is_empty(row, col)
                ):
                    self.win.blit(
                        Constant.IMAGES["pickaxe"], (display_pos_x, display_pos_y)
                    )
                elif self.engine.has_wood(row, col):
                    self.win.blit(
                        Constant.IMAGES["axe"], (display_pos_x, display_pos_y)
                    )

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
                        self.engine.spawning = "quarry_1"
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
        return "mining"

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
                self.win.blit(
                    Constant.IMAGES["persuade"], (display_pos_x, display_pos_y)
                )

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
        return "stealing"

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
                self.win.blit(Constant.IMAGES["steal"], (display_pos_x, display_pos_y))

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
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
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
                results.append(
                    self.revert_to_playing_state()
                )  # Return to playing state if stealing is ongoing
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
        return "pre-building"

    def add_menu_to_menu_queue(self, menu):
        self.menu_queue = menu
        row, col = (
            self.previously_selected_piece.row,
            self.previously_selected_piece.col,
        )
        self.engine.menus.append(
            self.engine.MENUS[self.menu_queue](
                row, col, self.win, self.engine, self.previously_selected_piece
            )
        )

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
                if (row, col) in self.previously_selected_piece.spawn_squares(
                        self.engine
                ):
                    self.win.blit(
                        Constant.IMAGES["hammer"], (display_pos_x, display_pos_y)
                    )

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

    def tab(self):
        self.revert_to_playing_state()


class Trading(State):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.side_bar = Hud(self.win, self.engine)

    def __repr__(self):
        return "trading"

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
        return "praying"

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
                    self.win.blit(
                        Constant.IMAGES["prayer"], (display_pos_x, display_pos_y)
                    )

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
        return "spawning"

    def draw(self):
        super().draw()
        self.side_bar.draw()
        pos = pygame.mouse.get_pos()
        displayPosX = pos[0] - Constant.SQ_SIZE // 2
        displayPosY = pos[1] - Constant.SQ_SIZE // 2
        if Constant.pos_in_bounds(pos):
            try:
                if self.engine.spawning == "quarry_1":
                    self.win.blit(
                        Constant.IMAGES["pickaxe"], (displayPosX, displayPosY)
                    )
                else:
                    self.win.blit(
                        self.spawnTable[
                            (self.engine.turn + "_" + self.engine.spawning)
                        ],
                        (displayPosX, displayPosY),
                    )
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
            spawn = type_of_spawn(acting_tile, action_tile, self.engine.spawning)
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
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.key = {"w": "White Won!", "b": "Black Won!"}
        self.text_surf = self.font.render(
            self.key[self.engine.turn], True, Constant.turn_to_color[self.engine.turn]
        )
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.display_x = self.window_width // 2 - self.text_surf.get_width() // 2
        self.display_y = self.window_height // 2 - self.text_surf.get_height() // 2

    def __repr__(self):
        return "winner"

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
        return "surrender"

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
        return "piece cost screen"

    def remove_top_menu(self):
        if len(self.engine.menus) == 1:
            self.engine.close_menus()
            if str(self.current_state) == "playing":
                self.revert_to_playing_state()
            else:
                self.revert_to_starting_state()

        else:
            self.engine.menus[-1].close()
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
        self.engine.reset_selected()
        self.previously_selected.performing_ritual = True
        self.cost_type = None
        self.turn = self.engine.turn
        self.player = self.engine.players[self.turn]
        self.ritual_image = Constant.PRAYER_RITUALS[self.turn + "_" + str(self)]
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
        self.previously_selected.ritual_squares_list = (
            self.previously_selected.gold_general_ritual_squares(self.engine)
        )

    def __repr__(self):
        return "gold_general"

    def draw(self):

        super().draw()
        self.side_bar.draw()
        self.draw_ritual_at_mouse_position()

    def click_valid_square(self, row, col):
        if Constant.tile_in_bounds(row, col):
            if (row, col) in self.previously_selected.ritual_squares_list:
                return True

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col):
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
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
        return "smite"

    def draw(self):
        super().draw()
        self.side_bar.draw()
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
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
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
        self.previously_selected.ritual_squares_list = (
            self.delete_resource_ritual_squares()
        )

    def __repr__(self):
        return "destroy_resource"

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
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
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
        self.previously_selected.ritual_squares_list = (
            self.create_resource_ritual_squares()
        )
        self.row = None
        self.col = None

    def __repr__(self):
        return "create_resource"

    def draw(self):
        super().draw()
        self.side_bar.draw()
        # Display Gold General at mouse position while mouse is on valid spawn square
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()
        else:
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
                    acting_tile = self.engine.board[self.previously_selected.row][
                        self.previously_selected.col
                    ]
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
        return "teleport"

    def draw(self):
        super().draw()
        self.side_bar.draw()
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
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
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
        if str(self.previously_selected) == "assassin":
            self.first_selected = self.previously_selected
            self.first_selected.casting = True
            self.previously_selected.ritual_squares_list = self.swap_ritual_squares()

    def __repr__(self):
        return "swap"

    def draw(self):
        super().draw()
        self.side_bar.draw()
        self.draw_ritual_at_mouse_position()
        if self.first_selected:
            if str(self.first_selected) == "assassin":
                return

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
            self.first_selected.casting = True
            self.previously_selected.ritual_squares_list = self.swap_ritual_squares()
        elif self.click_valid_square(row, col) and self.first_selected:
            self.second_selected = self.engine.get_occupying(row, col)
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
            action_tile = (
                (self.first_selected.row, self.first_selected.col),
                (row, col),
            )
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
        self.down = range(self.row + 1, Constant.BOARD_HEIGHT_SQ), range(
            self.col, self.col + 1
        )
        self.right = range(self.row, self.row + 1), range(
            self.col + 1, Constant.BOARD_WIDTH_SQ
        )
        self.left = range(self.row, self.row + 1), range(self.col - 1, -1, -1)

        self.selected_range = self.determine_active_line(mouse_row, mouse_col)
        self.previously_selected.ritual_squares_list = (
            self.active_line_destroy_ritual_squares(self.selected_range)
        )

    def __repr__(self):
        return "line_destroy"

    def draw(self):
        super().draw()
        self.side_bar.draw()
        self.draw_ritual_at_mouse_position()

    def determine_active_line(self, row, col):
        if self.engine.tile_in_bounds(row, col):
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
        self.previously_selected.ritual_squares_list = (
            self.active_line_destroy_ritual_squares(self.selected_range)
        )

    def active_line_destroy_ritual_squares(self, selected_range):
        active_line_squares = []
        if selected_range:
            for r in selected_range[0]:
                for c in selected_range[1]:
                    if self.engine.board[r][c].is_protected_by_opposite_color(
                            self.engine.turn
                    ):
                        break
                    else:
                        active_line_squares.append((r, c))
        return active_line_squares

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col):
            self.engine.line_destroy_selected_range = self.selected_range
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
            action_tile = self.engine.board[row][col]
            event = LineDestroy(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
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
        return "protect"

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
        self.draw_ritual_at_mouse_position()

    def left_click(self):
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        if self.click_valid_square(row, col):
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
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
        return "portal"

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
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
            action_tile = ((self.selected.row, self.selected.col), (row, col))
            event = Portal(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            return self.revert_to_playing_state()
        else:
            return self.revert_to_playing_state()
