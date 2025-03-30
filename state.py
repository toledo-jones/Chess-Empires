from __future__ import annotations

import typing

from pygame import BLEND_RGBA_MULT

if typing.TYPE_CHECKING:
    from engine import Engine
    from splash import SplashScreen
    from player import Player

from game_event import *
from menu import *
from sidebar import *
from encyclopedia import *


def exit_game():
    """
    Calls the Engine's exit_game function to properly terminate the game.
    """
    # Import at module level with a new name
    from engine import exit_game as engine_exit_game

    # Call the actual exit function from the engine
    engine_exit_game()


def _determine_special_move_type(
    acting_tile: Tile, action_tile: Tile, default_type: type
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


def type_of_capture(acting_tile: Tile, action_tile: Tile) -> type:
    """
    Determines the type of capture based on the presence of traps or portals.

    :param acting_tile: The tile from which the capture originates.
    :param action_tile: The tile on which the capture is performed.
    :return: The type of capture (TrapCapture, PortalCapture, or Capture).
    """
    return _determine_special_move_type(acting_tile, action_tile, Capture)


def type_of_spawn(acting_tile: Tile, action_tile: Tile, spawning: str = None) -> type:
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
    :return: (bool) if the piece is selected again.
    """
    # No piece selected
    if previously_selected is None:
        return False

    # Check if the positions match
    return previously_selected.get_position() == (row, col)


def type_of_move(acting_tile: Tile, action_tile: Tile) -> type:
    """
    Determines the type of move based on the presence of traps or portals.

    :param acting_tile: The tile from which the move originates.
    :param action_tile: The tile on which the move is performed.
    :return: The type of move (TrapMove, PortalMove, or Move).
    """
    return _determine_special_move_type(acting_tile, action_tile, Move)


class State:
    """
    Represents the game state, handling interactions, rendering, and game logic.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the State object with essential game components.

        :param win: The game window surface where everything is drawn.
        :param engine: The game engine managing game logic and events.
        """

        # The game window surface where all visuals are rendered
        self.win: pygame.Surface = win

        # Used by ritual child classes
        self.cost_type: Optional[str] = None

        # The game engine responsible for handling game logic and events
        self.engine: Engine = engine

        # Sidebar element, initially set to None
        self.side_bar: Optional[SideBar] = None

        # Boolean flag indicating whether an object is currently being dragged
        self.dragging: bool = False

        # Stores the initial mouse position when dragging starts
        self.mouse_start_pos: tuple[int, int] | None = None

        # Stores the game piece currently being dragged, initially None
        self.dragging_piece: Optional[Unit] = None

        # Dictionary of spawn-able objects, mapping string keys to their respective images
        self.spawn_table: dict[str, pygame.Surface] = (
            constant.W_BUILDINGS
            | constant.W_PIECES
            | constant.B_BUILDINGS
            | constant.B_PIECES
        )

        # Background paper texture used in the game interface
        self.paper_texture: pygame.Surface = constant.IMAGES["paper"]

    def get_window(self) -> pygame.Surface:
        """
        Return window surface of this state
        :return: pygame surface of window
        """
        return self.win

    def draw_piece_at_mouse_cursor(self, pos, piece):
        """
        Draws a piece at the mouse cursor position, centering it properly.
        """
        piece_image = self.spawn_table[(self.engine.turn + "_" + str(piece))]
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
        Scales the paper texture to match the size of the surface object.

        :param surface: The Pygame Surface object to be match the scale of.
        :return: a new pygame object which is the scaled version of paper image.
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
                # Attempt a left-click action, if successful, do nothing further
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

    def revert_to_playing_state(self) -> False:
        """
        Reverts the engine to the 'playing' state, which is considered the default gameplay state.
        This method is typically used by various states to return to the default game state.

        It resets the engine flags, selected state, and closes any active menus before
        transitioning to the 'Playing' state.
        """
        self.dragging = False

        # Resets any flags related to current actions
        self.engine.reset_flags()

        # Clears any selected items or pieces
        self.engine.reset_selected()

        # Closes any open menus
        self.engine.close_menus()

        # Transition to the default 'Playing' state
        new_state = Playing(self.win, self.engine)
        self.engine.set_state(new_state)  # Sets the new state to 'Playing'
        return False

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
        return False

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
        return False

    def draw(self):
        """
        Super method of draw, can be overridden by subclasses.
        Only clears the screen with the fill color and then draws the board. Override this method to add additional
        draw
        steps.
        """
        # Clear the frame with the menu color
        self.win.fill(constant.MENU_COLOR)

        # Draw the board from engine onto the window
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
            + constant.DEFAULT_ACTIONS_REMAINING
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
    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Pause state with buttons and UI elements.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        super().__init__(win, engine)  # Call parent class initializer

        # Scale paper texture to size of window
        self.paper_texture: pygame.Surface = self.scale_paper_texture(self.win)

        # Store font color
        self.color: str = constant.turn_to_color[self.engine.turn]

        # Store window dimensions
        self.window_width: int = self.win.get_width()
        self.window_height: int = self.win.get_height()

        # Set the font size based on a constant square size
        self.font_size: int = round(constant.SQ_SIZE * 1)

        # Load the font from the specified file
        self.font: pygame.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Define button labels
        buttons: list[str] = ["music:", "sounds:", "back"]

        # Define flags for buttons on and off
        flags: list[str] = ["off", "on"]

        # Create surfaces for each button text
        self.button_surfaces: list[pygame.Surface] = [
            self.font.render(button, True, self.color) for button in buttons
        ]

        # Create surfaces for each button text
        self.flag_surfaces: list[pygame.Surface] = [
            self.font.render(flag, True, self.color) for flag in flags
        ]

        # Get button dimensions (assuming all buttons have the same size)
        self.button_width: int = self.button_surfaces[1].get_width()
        self.button_height: int = self.button_surfaces[1].get_height()

        # Create a highlight rectangle (transparent overlay) for hovering effect
        self.square = pygame.Surface((self.button_width, self.button_height))
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Boolean list to track which button is currently highlighted
        self.button_highlighted: list[bool] = [False] * len(buttons)

        # List to store button positions for consistent layout
        self.button_positions: list[Tuple[int, int]] = []

        # List for which flags are on or off
        self.current_flags = [int(constant.MUSIC_ON), int(constant.SOUND_EFFECTS_ON)]

        # List to store flag positions for consistent layout
        self.flag_positions: list[Tuple[int, int]] = []

        # Compute initial button positions
        self.compute_button_positions()

        # Compute initial flag positions
        self.compute_flag_positions()

    def compute_flag_positions(self):
        """
        Computes and stores the positions for each flag next to the corresponding button.
        """
        # Set an offset to position the flag to the right of the button
        flag_offset: int = constant.SQ_SIZE

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
        total_height: int = (
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
        self.win.fill(constant.MENU_COLOR)

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
        cursor_over_button: bool = False

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
            constant.MUSIC_ON = not constant.MUSIC_ON
            self.current_flags[0] = int(constant.MUSIC_ON)
            constant.load_music(constant.MUSIC_ON)

        # If the "sounds" button was clicked
        elif button_index == 1:
            constant.SOUND_EFFECTS_ON = not constant.SOUND_EFFECTS_ON
            self.current_flags[1] = int(constant.SOUND_EFFECTS_ON)

        # If the "back" button was clicked
        elif button_index == 2:
            # Return to previous state
            self.esc()


class Pause(State):
    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Pause state with buttons and UI elements.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        super().__init__(win, engine)  # Call parent class initializer

        # Scale paper texture
        self.paper_texture: pygame.Surface = self.scale_paper_texture(self.win)

        # Store font color
        self.color: str = constant.turn_to_color[self.engine.turn]

        # Store window dimensions
        self.window_width: int = self.win.get_width()
        self.window_height: int = self.win.get_height()

        # Set the font size based on a constant square size
        self.font_size: int = round(constant.SQ_SIZE * 1)

        # Load the font from the specified file
        self.font: pygame.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Define button labels
        buttons: list[str] = [
            "return to game",
            "how to play",
            "reset board",
            "settings",
            "quit",
        ]

        # Create surfaces for each button text
        self.button_surfaces: list[pygame.Surface] = [
            self.font.render(button, True, self.color) for button in buttons
        ]

        # Get button dimensions (assuming all buttons have the same size)
        self.button_width: int = self.button_surfaces[0].get_width()
        self.button_height: int = self.button_surfaces[0].get_height()

        # Create a highlight rectangle (transparent overlay) for hovering effect
        self.square = pygame.Surface((self.button_width, self.button_height))
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Boolean list to track which button is currently highlighted
        self.button_highlighted: list[bool] = [False] * len(buttons)

        # List to store button positions for consistent layout
        self.button_positions: list[Tuple[int, int]] = []

        # Compute initial button positions
        self.compute_button_positions()

    def compute_button_positions(self):
        """
        Computes and stores the positions for each button to ensure consistent centering.
        """
        # Calculate total height occupied by all buttons (including spacing)
        total_height: int = (
            len(self.button_surfaces) * self.button_height
            + (len(self.button_surfaces) - 1) * 10
        )

        # Determine the starting y-position to center all buttons vertically
        start_y = (self.window_height - total_height) // 2

        # Compute positions for each button and store them
        self.button_positions: list[Tuple[int, int]] = [
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
        self.win.fill(constant.MENU_COLOR)

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
        cursor_over_button: bool = False

        # Iterate over all buttons and check if the mouse is hovering over any
        for i, (button_x, button_y) in enumerate(self.button_positions):
            # Create a rectangle representing the button's clickable area
            button_rect: pygame.Rect = pygame.Rect(
                button_x, button_y, self.button_width, self.button_height
            )

            # Update highlight status
            if button_rect.collidepoint(mouse_x, mouse_y):
                self.button_highlighted[i] = True

                # Set flag if mouse is over a button
                cursor_over_button: bool = True
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
        self.paper_texture: pygame.Surface = self.scale_paper_texture(self.win)

        # Menu logo and its position
        self.main_menu_logo: pygame.Surface = splash_screen.logo_image
        self.logo_position: Tuple[int, int] = splash_screen.logo_position
        self.color: str = constant.turn_to_color[splash_screen.logo_color]
        self.logo_position_y: Optional[int] = None
        self.button_display_y: Optional[int] = None

        # Window dimensions and font settings
        self.window_width: int = self.win.get_width()
        self.window_height: int = self.win.get_height()
        self.font_size: int = round(constant.SQ_SIZE * 1)
        self.font: pygame.font = pygame.font.Font(
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
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.MOVE_SQUARE_HIGHLIGHT_COLOR)

        # Boolean list to track which button is currently highlighted
        self.button_highlighted: list[bool] = [False] * len(buttons)

        # List to store button positions for consistent layout
        self.button_positions: list[Tuple[int, int]] = []

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
        self.color = constant.turn_to_color[splash_screen.logo_color]

    def compute_button_positions(self):
        """
        Calculate the position for each button and store it in the button_positions list.
        The buttons will be centered vertically and spaced evenly horizontally.
        """

        # Place logo at top of screen
        self.logo_position_y: int = self.window_height // 4

        # Place buttons on the bottom 2/3 of screen
        self.button_display_y: int = (
            2 * self.window_height
        ) // 3 - self.button_height // 2

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
        self.win.fill(constant.MENU_COLOR)

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
                    constant.PLAY_AGAINST_AI = False
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
    def __init__(self, win: pygame.Surface, engine: Engine):
        super().__init__(win, engine)

        # Scale paper texture
        self.paper_texture: pygame.Surface = self.scale_paper_texture(self.win)

        # Determine color for menu
        self.color: str = constant.turn_to_color[self.engine.turn]

        # Initialize variables for logo and button positions
        self.logo_position_y: Optional[int] = None
        self.button_display_y: Optional[int] = None

        # List of images to be shown
        self.images: dict[int, pygame.Surface] = constant.INSTRUCTIONS

        # Track the index of the current image being displayed
        self.current_image_index: int = 0

        # Obtain window height and width
        self.window_width: int = self.win.get_width()
        self.window_height: int = self.win.get_height()

        # Scale images
        self.scale_images()

        # Define the button text options
        buttons: list[str] = ["<---", "back", "--->"]

        # Set the font size based on a constant square size
        self.font_size: int = round(constant.SQ_SIZE * 0.8)

        # Load the font from the specified file
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Create surfaces for each button text
        self.button_surfaces: list[pygame.Surface] = [
            self.font.render(button, True, self.color) for button in buttons
        ]

        # Get button dimensions (assuming all buttons have the same size)
        self.button_width: int = self.button_surfaces[0].get_width()
        self.button_height: int = self.button_surfaces[0].get_height()

        # Create a highlight rectangle (transparent overlay) for hovering effect
        self.square: pygame.Surface = pygame.Surface(
            (self.button_width, self.button_height)
        )
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.MOVE_SQUARE_HIGHLIGHT_COLOR)

        # Boolean list to track which button is currently highlighted
        self.button_highlighted: list[bool] = [False] * len(buttons)

        # List to store button positions for consistent layout
        self.button_positions: list[Tuple[int, int]] = []

        # Compute initial button positions
        self.compute_button_positions()

    def compute_button_positions(self):
        """
        Calculate the position for each button and store it in the button_positions list.
        The buttons will be centered and spaced evenly under the image.
        """
        # Calculate the vertical starting position for the buttons at the bottom of the image
        self.logo_position_y = self.window_height // 4
        self.button_display_y = (
            self.window_height // 2
            + self.images[self.current_image_index].get_height() // 2
        )

        # Calculate the total width of all the buttons (including spacing)
        button_spacing = 20

        # Spacing between buttons
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
        self.win.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.draw_paper_texture(self.win)

        # Draw the current image at the center of the screen
        current_image = self.images[self.current_image_index]
        image_rect = current_image.get_rect(
            centerx=self.window_width // 2, top=constant.SQ_SIZE
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
        Scale each image to 2/3 of its original size while preserving the aspect ratio.
        """
        scaled_images = {}

        # Loop through each image in the dictionary
        for key, value in self.images.items():
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

    def __init__(self, win: pygame.Surface, engine: Engine, currently_selected: Unit):
        """
        Initializes the Inspector state.

        :param win: The game window surface.
        :param engine: The game engine handling state and logic.
        :param currently_selected: The piece that is currently being inspected.
        """

        # Initialize the base State class
        super().__init__(win, engine)

        # Store the currently selected piece
        self.currently_selected: Unit = currently_selected

        # Initialize the sidebar for displaying piece information
        self.side_bar: SideBar = PieceInspector(win, engine, currently_selected)

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
        self.engine.update_squares()

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
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Retrieve the piece at the specified board position
        selected_piece = self.engine.get_occupying(row, col)

        # If the selected piece is not already being inspected
        if selected_piece is not self.currently_selected:
            # Check if the piece can be inspected
            if selected_piece is not None:
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

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the 'Playing' state.

        :param win: The game window surface.
        :param engine: The game engine handling state and logic.
        """

        # Initialize the base State class
        super().__init__(win, engine)

        # Create the sidebar for this state
        self.side_bar: SideBar = Hud(win, engine)

        # Highlight surface to be drawn at mouse_position
        self.square = constant.create_highlight_surface(
            (constant.SQ_SIZE, constant.SQ_SIZE)
        )

        # Highlight x and y
        self.highlight_square_x: Optional[int] = None
        self.highlight_square_y: Optional[int] = None

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
            row, col = constant.convert_pos(pos)

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

        # Dragging did not occur
        return False

    def drop_piece(self, pos: Tuple[int, int]):
        """
        Handles the dropping of a dragged piece onto a new board position.

        :param pos: The position (x, y) where the piece is dropped.
        """

        # Prevent piece dropping if menus are open
        if not self.engine.menus:
            # Convert pixel position to board coordinates
            row, col = constant.convert_pos(pos)

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

    def can_move_to_square(
        self, previously_selected: Optional[Unit], row: int, col: int
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

    def can_select_piece(self, currently_selected: Optional[Unit]) -> bool:
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
            return False

        # Ensure the player can perform an action
        if not self.engine.player_can_do_action(self.engine.turn):
            return False

        # The move is valid
        return True

    def draw(self):
        """
        Draws the playing state, including the game board and sidebar.
        """

        # Draw the base state (such as the board)
        super().draw()

        # Draw the sidebar displaying game information
        self.side_bar.draw()

        # Draw menus if there are any
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()
            return

        # Draw the highlight square at the current mouse position
        if self.highlight_square_x is not None and self.highlight_square_y is not None:
            self.win.blit(
                self.square,
                (self.highlight_square_x, self.highlight_square_y),
                special_flags=BLEND_RGBA_MULT,
            )

        # Get the current mouse position
        pos = pygame.mouse.get_pos()

        # Draw the piece at the mouse cursor if dragging
        if self.dragging:
            try:
                self.draw_piece_at_mouse_cursor(pos, self.dragging_piece)
            except KeyError:
                pass

    def can_capture_piece(
        self,
        previously_selected: Optional[Unit],
        row: int,
        col: int,
        currently_selected: Optional[Unit],
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
        previously_selected: Unit,
        row: int,
        col: int,
        action_type: Callable[[Tile, Tile], type],
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

    def perform_move(self, previously_selected: Unit, row: int, col: int):
        """
        Performs the move action by creating an event and updating the game state.

        :param previously_selected: The piece being moved.
        :param row: The target row for the move.
        :param col: The target column for the move.
        """
        # Call the general perform action method with the appropriate action type (Move)
        self._perform_action(previously_selected, row, col, type_of_move)

    def perform_capture(self, previously_selected: Unit, row: int, col: int):
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
        self.engine.update_squares()

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
        Handles the inspection of a piece when a special action is performed (e.g., by pressing a key or
        right-clicking).
        """
        # Get the mouse position and convert it to board coordinates
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Get the piece under the mouse
        currently_selected = self.engine.get_occupying(row, col)

        # Check if the piece can be inspected
        if currently_selected is not None:
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
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Reset selected piece
        self.engine.reset_selected()

        # Get the piece under the mouse
        piece = self.engine.get_occupying(row, col)

        # Ensure the piece belongs to the current player
        if piece and piece.color == self.engine.turn:
            # Perform right-click action for the piece
            if not piece.right_click(self.engine):
                # Revert to the 'playing' state
                return self.revert_to_playing_state()
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

    def m(self):
        """
        Handles the inspection of a piece when triggered by a special action (e.g., pressing a key).
        It checks if the piece under the mouse can be inspected and switches to the Inspector state.
        """
        # Convert the current mouse position to board coordinates (row, col)
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Retrieve the piece that is currently occupying the specified position
        currently_selected = self.engine.get_occupying(row, col)

        # Check if the piece can be inspected (based on certain conditions)
        if currently_selected is not None:
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
            0 <= mouse_x < constant.BOARD_WIDTH_PX
            and 0 <= mouse_y < constant.BOARD_HEIGHT_PX
        ):
            # Update the cursor based on whether the mouse is hovering over a piece
            self.update_cursor()

        self.update_highlight_position()

    def update_highlight_position(self):
        """
        Updates the position of the highlight square based on the current mouse position.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if mouse_x > constant.BOARD_WIDTH_PX:
            self.highlight_square_x, self.highlight_square_y = None, None
            return

        # Convert pixel position to board coordinates
        row, col = constant.convert_pos((mouse_x, mouse_y))

        # Set the highlight square position
        self.highlight_square_x = col * constant.SQ_SIZE
        self.highlight_square_y = row * constant.SQ_SIZE

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


class Starting(State):
    """
    Represents the starting state of the game where players are initialized and resources are set up.
    """

    def __init__(
        self, win: pygame.Surface, engine: Engine, preserve_resources: bool = False
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
        self.side_bar: SideBar = Start(win, engine)

        # If resources should not be preserved
        if not preserve_resources:
            # If the board starts with resources, initialize them
            if constant.BOARD_STARTS_WITH_RESOURCES:
                self.engine.select_map()

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

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the SelectStartingPieces state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Initialize the base class
        super().__init__(win, engine)

        # Scale paper texture
        self.paper_texture: pygame.Surface = self.scale_paper_texture(self.win)

        # Set up initial attributes
        self.draw_map: bool = False
        self.pieces: dict[str, dict] = {
            "w": constant.W_PIECES | constant.W_BUILDINGS,
            "b": constant.B_PIECES | constant.B_BUILDINGS,
        }

        # Get window dimensions
        self.window_width: int = pygame.display.Info().current_w
        self.window_height: int = pygame.display.Info().current_h

        # Set font size and render description text
        self.font_size: int = round(constant.SQ_SIZE * 1)
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.description_text: str = "select your starting pieces:"
        self.text_surf: pygame.Surface = self.font.render(
            self.description_text, True, constant.turn_to_color[self.engine.turn]
        )

        # Set Y-buffer for spacing
        self.y_buffer: int = round(constant.SQ_SIZE * 0.55)

        # Calculate initial positions and spacing
        self.initial_x: int = round(2.5 * self.window_width) // len(
            constant.SELECTABLE_STARTING_PIECES
        )
        self.x_buffer: int = self.initial_x
        self.piece_spacing: int = round(constant.SQ_SIZE * 1.5)

        # Calculate total height of the grid and starting Y position
        total_height_of_grid: int = (
            self.y_buffer * 2 * constant.NUMBER_OF_STARTING_PIECES
        )
        self.initial_y: int = (self.window_height - total_height_of_grid) // 2

        # Define grid dimensions
        self.cols: int = len(constant.SELECTABLE_STARTING_PIECES)
        self.rows: int = (
            constant.NUMBER_OF_STARTING_PIECES + constant.NUMBER_OF_BONUS_PIECES
        )

        # Initialize the selection matrix (3D list to track piece status)
        self.selection_matrix: list[list[list[Union[str, int, bool]]]] = [
            [[0 for _ in range(3)] for _ in range(self.cols)] for _ in range(self.rows)
        ]

        # Set instruction text and surfaces
        self.instruction_text: list[str] = [
            " 'tab' to go back",
            " 'space bar' to confirm selection",
            " 'right click' to view the map",
            " 'right click' a piece for more information about it",
        ]
        self.instruction_text_surfaces: list[pygame.Surface] = []
        self.instruction_text_font_size: int = constant.SQ_SIZE // 2
        self.instruction_text_font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.instruction_text_font_size
        )
        for line in self.instruction_text:
            l: pygame.Surface = self.instruction_text_font.render(
                line, True, constant.turn_to_color[self.engine.turn]
            )
            self.instruction_text_surfaces.append(l)

        # Get the height of the instruction text for layout purposes
        self.instruction_text_height: int = self.instruction_text_surfaces[
            0
        ].get_height()

        # Assign pieces to the selection matrix
        for r in range(self.rows):
            for c in range(self.cols):
                # Check if we are in the bonus piece rows
                if r >= constant.NUMBER_OF_STARTING_PIECES:
                    # If it's a bonus piece, assign it
                    self.selection_matrix[r][c][0] = constant.BONUS_STARTING_PIECES[c]
                else:
                    # Otherwise, assign a selectable starting piece
                    self.selection_matrix[r][c][0] = (
                        constant.SELECTABLE_STARTING_PIECES[c]
                    )

                # Initialize the selection matrix states (highlight and selected status)
                self.selection_matrix[r][c][1] = False  # HIGHLIGHT
                self.selection_matrix[r][c][2] = False  # SELECTED

        # Create a surface for highlighting unused pieces
        self.square: pygame.Surface = pygame.Surface(
            (constant.SQ_SIZE, constant.SQ_SIZE)
        )
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

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

        # Display piece information if a piece is selected
        if not self.draw_map:
            try:
                row, col = piece_selected
            except TypeError:
                return
            piece = self.selection_matrix[row][col][0]
            menu: Menu = PieceDescription(self.win, self.engine, piece)
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
                    piece_position[0], piece_position[0] + constant.SQ_SIZE
                ):
                    if pos[1] in range(
                        piece_position[1], piece_position[1] + constant.SQ_SIZE
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
            self.update_drag_selection()

        # Loop through the selection matrix to highlight the piece under the cursor
        for r in range(self.rows):
            for c in range(self.cols):
                piece_position = (c * self.piece_spacing + self.initial_x, initial_y)
                if pos[0] in range(
                    piece_position[0], piece_position[0] + constant.SQ_SIZE
                ):
                    if pos[1] in range(
                        piece_position[1], piece_position[1] + constant.SQ_SIZE
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
            self.win.fill(constant.MENU_COLOR)

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
                constant.NUMBER_OF_STARTING_PIECES + constant.NUMBER_OF_BONUS_PIECES
            ):
                if x < constant.NUMBER_OF_STARTING_PIECES:
                    for p in constant.SELECTABLE_STARTING_PIECES:
                        piece = self.engine.turn + "_" + p
                        self.win.blit(
                            self.pieces[self.engine.turn][piece], (x_buffer, initial_y)
                        )
                        x_buffer += piece_spacing
                else:
                    for p in constant.BONUS_STARTING_PIECES:
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
        spawn_list = [constant.STARTING_PIECES[0]]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.selection_matrix[r][c][2]:
                    spawn_list.append(self.selection_matrix[r][c][0])
        spawn_list.append(constant.STARTING_PIECES[-1])
        if len(spawn_list) == (
            constant.NUMBER_OF_STARTING_PIECES
            + len(constant.STARTING_PIECES)
            + constant.NUMBER_OF_BONUS_PIECES
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

    def __init__(self, win: pygame.Surface, engine: Engine):
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

        self.engine.spawn_list = []

        self.engine.spawn_count = 0

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
        if constant.TURN_CHANGE_AFTER_START_SPAWN:
            self.engine.turn = constant.TURNS[self.engine.turn]

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
        if constant.pos_in_board(pos):
            row, col = constant.convert_pos(pos)

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
            acting_tile = self.engine.board[previously_selected.row][
                previously_selected.col
            ]
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
        self.engine.update_squares()

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

    def _handle_previously_selected_piece(
        self, previously_selected: Unit, row: int, col: int
    ):
        """
        Handles the logic when a piece was previously selected.

        :param previously_selected: The previously selected piece.
        :param row: The row index of the clicked position.
        :param col: The column index of the clicked position.
        """
        # Update the spawn squares for the previously selected piece
        previously_selected.update_squares(self.engine)

        # Check if the clicked position is in the spawn squares list
        if (row, col) in previously_selected.spawn_squares_list:
            self.create_spawn_event(row, col, False)

    def _handle_no_previously_selected_piece(self, row: int, col: int):
        """
        Handles the logic when no piece was previously selected.

        :param row: The row index of the clicked position.
        :param col: The column index of the clicked position.
        """
        # Check if the clicked position is a legal starting square
        if self.engine.is_legal_starting_square(row, col):
            self.create_spawn_event(row, col)

    def _update_spawn_squares(self):
        """
        Updates the spawn squares and handles the end of spawning.
        """
        try:
            # Set the current spawning piece
            self.engine.spawning = self.engine.spawn_list[self.engine.spawn_count]
            # Update the spawn squares
            self.engine.update_squares()
        except IndexError as e:
            print(e)
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
        displayPosX = pos[0] - constant.SQ_SIZE // 2
        displayPosY = pos[1] - constant.SQ_SIZE // 2

        # Check if the mouse position is within bounds
        if constant.pos_in_board(pos):
            try:
                # Draw the piece being dragged at the calculated position
                self.win.blit(
                    self.spawn_table[(self.engine.turn + "_" + self.engine.spawning)],
                    (displayPosX, displayPosY),
                )
            except TypeError:
                pass

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        # Handle menu input for mouse movement
        self.menu_input("mouse_move")

        # Check if the mouse is within menu bounds
        self.mouse_in_menu_bounds()

    def enter(self):
        """
        Handles the enter key press event.
        Override the default implementation here to prevent the state from changing.
        """
        pass

    def tab(self):
        """
        Handles the tab key press event by performing a right-click action.
        """
        self.right_click()


class DebugStart(StartingSpawn):
    """
    Represents the debug starting state where players begin spawning their pieces with debug settings.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the DebugStart state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with an empty state
        self.side_bar: SideBar = Empty(win, engine)

        # Set the first flag to True
        self.first: bool = True

        # Play the start game sound
        self.engine.sounds.play("start_game")

        # Set the spawn list to debug starting pieces
        self.spawn_list: list[str] = constant.DEBUG_STARTING_PIECES

        # Set the initial spawning piece
        self.engine.spawning = self.spawn_list[0]

        # Set engine spawn list to this spawn list
        self.engine.spawn_list = self.spawn_list

    def __repr__(self) -> str:
        """
        Returns a string representation of the DebugStart state.

        :return: A string representing the DebugStart state.
        """
        return "start spawn"

    def begin_next_player_start_spawn(self):
        """
        Begins the piece selection process for the next player.
        """
        # Create and complete a ChangeTurn event
        event = ChangeTurn(self.engine)
        event.complete()

        # Append the event to the engine's event list
        self.engine.events.append(event)

        # Reset spawn count and set final spawn flag to True
        self.engine.spawn_count = 0
        self.engine.final_spawn = True

        # Create a new DebugStart state and set it in the engine
        new_state = DebugStart(self.win, self.engine)
        self.engine.set_state(new_state)

    def end_start_spawning(self):
        """
        Ends the starting spawning phase and transitions to the playing state.
        """
        # Call the parent class's end_start_spawning method
        super().end_start_spawning()

        # Set debug resources for each player
        for p in self.engine.players:
            player = self.engine.players[p]
            player.wood = constant.DEBUG_STARTING_WOOD
            player.gold = constant.DEBUG_STARTING_GOLD
            player.stone = constant.DEBUG_STARTING_STONE
            player.prayer = constant.DEBUG_STARTING_PRAYER

        # Revert to the playing state
        super().revert_to_playing_state()

    def left_click(self):
        """
        Handles the left-click action to spawn a piece or interact with the menu.
        """
        # Get the valid position of the mouse click
        row, col = self.get_valid_position

        # Update the previously selected piece
        previously_selected = self.engine.update_previously_selected()

        # Handle spawning if a piece was previously selected
        if previously_selected is not None:
            previously_selected.update_squares(self.engine)
            if (row, col) in previously_selected.spawn_squares_list:
                self.create_spawn_event(row, col, False)
        else:
            # Handle spawning if no piece was previously selected
            if self.engine.is_legal_starting_square(row, col):
                self.create_spawn_event(row, col)

        # Update the spawning piece or end spawning if all pieces are placed
        try:
            self.engine.spawning = self.engine.spawn_list[self.engine.spawn_count]
        except IndexError:
            if self.engine.final_spawn:
                self.end_start_spawning()
            else:
                self.engine.create_player(constant.TURNS[self.engine.turn])
                self.begin_next_player_start_spawn()


class Mining(State):
    """
    Represents the mining state where players can mine resources on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Mining state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Update the previously selected piece
        self.previously_selected: Unit = engine.update_previously_selected()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Mining state.

        :return: A string representing the Mining state.
        """
        return "mining"

    def draw(self):
        """
        Draws the mining state, including the HUD and any active menus.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the HUD
        side_bar = Hud(self.win, self.engine)
        side_bar.draw()

        # Get the current mouse position
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - constant.SQ_SIZE // 2
        display_pos_y = pos[1] - constant.SQ_SIZE // 2

        # Check if the mouse position is within bounds
        if constant.pos_in_board(pos):
            row, col = constant.convert_pos(pos)

            # Check if the position is in the mining squares list
            if (row, col) in self.previously_selected.mining_squares_list:
                if (
                    self.engine.has_resource(row, col, Quarry)
                    or self.engine.has_resource(row, col, Gold)
                    or self.engine.has_resource(row, col, SunkenQuarry)
                    or self.engine.has_no_units_or_resources(row, col)
                ):
                    # Draw the pickaxe image
                    self.win.blit(
                        constant.IMAGES["pickaxe"], (display_pos_x, display_pos_y)
                    )
                elif self.engine.has_resource(row, col, Wood):
                    # Draw the axe image
                    self.win.blit(
                        constant.IMAGES["axe"], (display_pos_x, display_pos_y)
                    )

    def left_click(self) -> bool:
        """
        Handles the left-click action to select a mining square.

        :return: True if a square is successfully selected, otherwise False.
        """
        # Get the current mouse position
        pos = pygame.mouse.get_pos()
        row, col = constant.convert_pos(pos)

        # Select the square and handle the result
        if self.select(row, col):
            return True
        else:
            return self.revert_to_playing_state()

    def right_click(self):
        """
        Handles the right-click action to reset the selected piece and return to the playing state.
        """
        # Reset the selected piece and menus
        self.engine.reset_selected()
        self.engine.menus = []

        # Set the state to Playing
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        pass

    def select(self, row: int, col: int):
        """
        Selects a mining square and creates the appropriate event.

        :param row: The row index of the selected square.
        :param col: The column index of the selected square.
        """
        # Check if there is a previously selected piece
        if not self.previously_selected:
            return False

        # Check if the tile is within bounds
        if not self.engine.tile_in_bounds(row, col):
            return False

        mining_squares = self.previously_selected.mining_squares_list
        # Check if the selected square is in the mining squares list
        if (row, col) in mining_squares:
            acting_tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
            action_tile = self.engine.board[row][col]

            # Create the appropriate event based on the resource
            if action_tile.get_resource():
                # Action tile has a resource, so mine it.
                event = Mine(self.engine, acting_tile, action_tile)
            else:
                # Action tile does not have a resource, so spawn a quarry there.
                self.engine.spawning = "quarry_1"
                event = SpawnResource(self.engine, acting_tile, action_tile)

            # Add the event to the engine and reset the selected piece
            self.engine.add_event(event)
            print("added event")
            return self.revert_to_playing_state()

    def tab(self):
        """
        Handles the tab key press event to revert to the playing state.
        """
        self.revert_to_playing_state()


class Persuading(State):
    """
    Represents the persuading state where players can persuade other pieces on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Persuading state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Update the previously selected piece
        self.previously_selected: Unit = engine.update_previously_selected()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Persuading state.

        :return: A string representing the Persuading state.
        """
        return "persuading"

    def draw(self):
        """
        Draws the persuading state, including the HUD and any active menus.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the HUD
        side_bar = Hud(self.win, self.engine)
        side_bar.draw()

        # Get the current mouse position
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - constant.SQ_SIZE // 2
        display_pos_y = pos[1] - constant.SQ_SIZE // 2

        # Check if the mouse position is within bounds
        if constant.pos_in_board(pos):
            row, col = constant.convert_pos(pos)

            # Check if the position is in the persuader squares list
            if (row, col) in self.previously_selected.persuader_squares_list:
                self.win.blit(
                    constant.IMAGES["persuade"], (display_pos_x, display_pos_y)
                )

    def left_click(self) -> bool:
        """
        Handles the left-click action to select a persuading square.

        :return: True if a square is successfully selected, otherwise False.
        """
        # Get the current mouse position
        pos = pygame.mouse.get_pos()
        row, col = constant.convert_pos(pos)

        # Select the square and handle the result
        if self.select(row, col):
            return True
        else:
            self.revert_to_playing_state()
            return False

    def right_click(self):
        """
        Handles the right-click action to reset the selected piece and return to the playing state.
        """
        # Reset the selected piece and menus
        self.engine.reset_selected()
        self.engine.menus = []

        # Set the state to Playing
        state = Playing(self.win, self.engine)
        self.engine.set_state(state)

    def select(self, row: int, col: int) -> bool:
        """
        Selects a persuading square and creates the appropriate event.

        :param row: The row index of the selected square.
        :param col: The column index of the selected square.
        :return: True if the selection is successful, otherwise False.
        """
        # Check if there is a previously selected piece
        if self.previously_selected is not None:
            # Check if the tile is within bounds
            if self.engine.tile_in_bounds(row, col):
                persuader_squares = self.previously_selected.persuader_squares_list

                # Check if the selected square is in the persuader squares list
                if (row, col) in persuader_squares:

                    # The tile which the persuader is on
                    acting_tile = self.engine.board[self.previously_selected.row][
                        self.previously_selected.col
                    ]

                    # The tile containing the piece to be persuaded
                    action_tile = self.engine.board[row][col]

                    event = Persuade(self.engine, acting_tile, action_tile)
                    self.engine.add_event(event)

                    # Check if the enemy player's king does not exist
                    if self.engine.enemy_king_does_not_exist():
                        new_state = Winner(self.win, self.engine)
                        self.engine.set_state(new_state)
                        return True
        return False

    def tab(self):
        """
        Handles the tab key press event to revert to the playing state.
        """
        self.revert_to_playing_state()


class Stealing(State):
    """
    Represents the stealing state in the game. This state handles user interactions
    related to stealing mechanics, including selecting valid tiles, processing menu interactions,
    and reverting to the playing state when needed.

    :param win: The game window where rendering occurs.
    :param engine: The game engine managing the state and logic.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        super().__init__(win, engine)

        # Updates the previously selected tile in the game
        self.previously_selected: Unit = engine.update_previously_selected()

        # HUD sidebar for displaying additional information
        self.side_bar: Hud = Hud(self.win, self.engine)

        # Coordinates of the tile being stolen from
        self.row: int | None = None
        self.col: int | None = None

    def __repr__(self) -> str:
        return "stealing"

    def draw(self):
        """
        Draws the game state, including menus, HUD, and steal icon if applicable.
        """
        super().draw()
        pos: tuple[int, int] = pygame.mouse.get_pos()
        display_pos_x: int = pos[0] - constant.SQ_SIZE // 2
        display_pos_y: int = pos[1] - constant.SQ_SIZE // 2

        self.side_bar.draw()

        # Draw menus if they exist
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()

        # Draw the steal icon if hovering over a valid square
        elif constant.pos_in_board(pos):
            row, col = constant.convert_pos(pos)
            if (row, col) in self.previously_selected.stealing_squares_list:
                self.win.blit(constant.IMAGES["steal"], (display_pos_x, display_pos_y))

    def left_click(self) -> bool:
        """
        Handles left-click interactions, checking for menu interactions,
        stealing mechanics, and valid square clicks.

        :return: True if an action was performed, otherwise False.
        """
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # If a menu is open, process menu clicks
        if self.engine.menus:
            return any(menu.left_click() for menu in self.engine.menus)

        # If stealing is in progress, execute the steal action
        if self.engine.stealing:
            self.engine.close_menus()
            action_tile: Tile = self.engine.board[self.row][self.col]
            acting_tile: Tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
            event: Steal = Steal(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)
            self.engine.stealing = None
            return self.revert_to_playing_state()

        # Check if the clicked square is a valid stealing target
        if self.click_valid_square(row, col):
            self.row, self.col = row, col
            self.engine.menus.append(StealingMenu(row, col, self.win, self.engine))
            return True

        # Default case: return to playing state if no action occurred
        return self.revert_to_playing_state()

    def click_valid_square(self, row: int, col: int) -> bool:
        """
        Checks whether the given row and column correspond to a valid square for stealing.

        :param row: The row index of the clicked square.
        :param col: The column index of the clicked square.
        :return: True if the square is valid for stealing, False otherwise.
        """
        return (row, col) in self.previously_selected.stealing_squares_list

    def right_click(self):
        """
        Handles right-click interactions, resetting selections and returning to the playing state.
        """
        self.engine.reset_selected()
        self.engine.menus.clear()
        self.engine.set_state(Playing(self.win, self.engine))

    def mouse_move(self):
        """
        Handles mouse movement, ensuring menus are properly updated and closing them
        if the mouse moves out of bounds.
        """
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()
                if not menu.mouse_in_menu_bounds():
                    self.revert_to_playing_state()

    def tab(self):
        """
        Handles the tab key press, returning to the playing state.
        """
        self.revert_to_playing_state()


class PreBuilding(State):
    """
    Represents the pre-building state where players can prepare to build structures on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the PreBuilding state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with a HUD
        self.side_bar = Hud(self.win, self.engine)

        # Update the previously selected piece
        self.previously_selected = self.engine.update_previously_selected()

        # Initialize menu queue and spawning piece
        self.menu_queue = None
        self.spawning_piece = None

    def __repr__(self) -> str:
        """
        Returns a string representation of the PreBuilding state.

        :return: A string representing the PreBuilding state.
        """
        return "building"

    def add_menu_to_menu_queue(self, menu: str):
        """
        Adds a menu to the menu queue and appends it to the engine's menus.

        :param menu: The menu to be added to the queue.
        """
        # Set the menu queue
        self.menu_queue = menu

        # Get the row and column of the previously selected piece
        row, col = (
            self.previously_selected.row,
            self.previously_selected.col,
        )

        # Append the menu to the engine's menus
        self.engine.menus.append(
            self.engine.MENUS[self.menu_queue](
                row, col, self.win, self.engine, self.previously_selected
            )
        )

    def can_select_piece(self, row: int, col: int) -> bool:
        """
        Checks if a piece can be selected based on its position.

        :param row: The row index of the piece.
        :param col: The column index of the piece.
        :return: True if the piece can be selected, otherwise False.
        """
        # Get the currently selected piece
        currently_selected = self.engine.get_occupying(row, col)

        try:
            # Check if the piece belongs to the current player and has remaining actions
            if self.engine.turn == currently_selected.color:
                if currently_selected.actions_remaining > 0:
                    if self.engine.player_can_do_action(self.engine.turn):
                        return True
        except AttributeError:
            pass

        return False

    def draw(self):
        """
        Draws the pre-building state, including the HUD and any active menus.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw each menu if any are open
        for menu in self.engine.menus:
            menu.draw()

        # Draw the sidebar
        self.side_bar.draw()

    def left_click(self) -> bool:
        """
        Handles the left-click action to interact with menus or select a piece.

        :return: True if an action is successfully performed, otherwise False.
        """
        # Handle menu input if applicable
        if self.engine.menus:
            for menu in self.engine.menus:
                return menu.left_click()
        return False

    def right_click(self):
        """
        Handles the right-click event to return to the playing state.
        """
        self.revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        # Handle menu input for mouse movement
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()
                if not menu.mouse_in_menu_bounds():
                    self.revert_to_playing_state()
                    break

    def click_square_in_spawn_squares(self, row: int, col: int) -> bool:
        """
        Checks if a square is within the spawn squares of the previously selected piece.

        :param row: The row index of the square.
        :param col: The column index of the square.
        :return: True if the square is within the spawn squares, otherwise False.
        """
        return (row, col) in self.previously_selected.spawn_squares(self.engine)

    def tab(self):
        """
        Handles the tab key press event to revert to the playing state.
        """
        self.revert_to_playing_state()


class Trading(State):
    """
    Represents the trading state where players can trade resources on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Trading state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with a HUD
        self.side_bar = Hud(self.win, self.engine)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Trading state.

        :return: A string representing the Trading state.
        """
        return "trading"

    def draw(self):
        """
        Draws the trading state, including the HUD and any active menus.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        self.side_bar.draw()

        # Draw each menu if any are open
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        # Handle menu input for mouse movement
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()
                if not menu.mouse_in_menu_bounds():
                    # Clear trading state and reset selected piece and menus
                    self.engine.trading = []
                    self.engine.reset_selected()
                    self.engine.menus = []

                    # Set the state to Playing
                    state = Playing(self.win, self.engine)
                    self.engine.set_state(state)

    def left_click(self) -> bool:
        """
        Handles the left-click action to interact with menus.

        :return: True if an action is successfully performed, otherwise False.
        """
        # Handle menu input for left click
        if self.engine.menus:
            for menu in self.engine.menus:
                return menu.left_click()
        return False

    def right_click(self):
        """
        Handles the right-click action to interact with menus.
        """
        # Handle menu input for right click
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.right_click()

    def tab(self):
        """
        Handles the tab key press event to revert to the playing state.
        """
        self.revert_to_playing_state()


class Praying(State):
    """
    Represents the praying state where players can perform prayer actions on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Praying state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Praying state.

        :return: A string representing the Praying state.
        """
        return "praying"

    def draw(self):
        """
        Draws the praying state, including the HUD and any active menus.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        side_bar = Hud(self.win, self.engine)
        side_bar.draw()

        # Get the current mouse position
        pos = pygame.mouse.get_pos()
        display_pos_x = pos[0] - constant.SQ_SIZE // 2
        display_pos_y = pos[1] - constant.SQ_SIZE // 2

        # Check if the mouse position is within bounds
        if constant.pos_in_board(pos):
            row, col = constant.convert_pos(pos)

            # Check if the position has a pray-able building
            if self.engine.has_pray_able_building(row, col):
                # Check if the building belongs to the current player
                if self.engine.get_occupying(row, col).color == self.engine.turn:
                    self.win.blit(
                        constant.IMAGES["prayer"], (display_pos_x, display_pos_y)
                    )

    def left_click(self) -> bool:
        """
        Handles the left-click action to select a praying square.

        :return: True if a square is successfully selected, otherwise False.
        """
        # Get the current mouse position
        pos = pygame.mouse.get_pos()
        row, col = constant.convert_pos(pos)

        # Select the square and handle the result
        if self.select(row, col):
            return True
        else:
            self.engine.reset_selected()
            new_state = Playing(self.win, self.engine)
            self.engine.set_state(new_state)
            return False

    def right_click(self):
        """
        Handles the right-click action to return to the playing state.
        """
        self.revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        pass

    def select(self, row: int, col: int):
        """
        Selects a praying square and creates the appropriate event.

        :param row: The row index of the selected square.
        :param col: The column index of the selected square.
        """
        # Update the previously selected piece
        previously_selected = self.engine.update_previously_selected()

        if previously_selected is not None:
            praying_squares = previously_selected.praying_squares_list

            # Check if the selected square is in the praying squares list
            if (row, col) in praying_squares:
                self.perform_pray(previously_selected, row, col)

    def perform_pray(self, previously_selected: Unit, row: int, col: int):
        """
        Performs the pray action by creating an event and updating the game state.

        :param previously_selected: The previously selected unit.
        :param row: The target row for the pray action.
        :param col: The target column for the pray action.
        """
        # Get the acting tile from the previously selected unit's position
        acting_tile = self.engine.board[previously_selected.row][
            previously_selected.col
        ]

        # Get the action tile from the target position
        action_tile = self.engine.board[row][col]

        # Create a Pray event with the acting and action tiles
        event = Pray(self.engine, acting_tile, action_tile)

        # Add the event to the engine's event list
        self.engine.add_event(event)

        # Revert to the playing state
        self.revert_to_playing_state()

    def tab(self):
        """
        Handles the tab key press event to revert to the playing state.
        """
        self.revert_to_playing_state()


class Spawning(State):
    """
    Represents the spawning state where players can spawn pieces on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Spawning state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with a HUD
        self.side_bar = Hud(win, engine)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Spawning state.

        :return: A string representing the Spawning state.
        """
        return "spawning"

    def draw(self):
        """
        Draws the spawning state, including the HUD and any active menus.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        self.side_bar.draw()

        # Get the current mouse position
        pos = pygame.mouse.get_pos()
        displayPosX = pos[0] - constant.SQ_SIZE // 2
        displayPosY = pos[1] - constant.SQ_SIZE // 2

        # Check if the mouse position is within bounds
        if constant.pos_in_board(pos):
            try:
                # Draw the appropriate image based on the spawning type
                if self.engine.spawning == "quarry_1":
                    self.win.blit(
                        constant.IMAGES["pickaxe"], (displayPosX, displayPosY)
                    )
                else:
                    self.win.blit(
                        self.spawn_table[
                            (self.engine.turn + "_" + self.engine.spawning)
                        ],
                        (displayPosX, displayPosY),
                    )
            except TypeError:
                pass
            return True

    def left_click(self) -> bool:
        """
        Handles the left-click action to spawn a piece.

        :return: True if a piece is successfully spawned, otherwise False.
        """
        # Get the current mouse position
        pos = pygame.mouse.get_pos()
        row, col = constant.convert_pos(pos)

        # Update the previously selected piece
        previously_selected = self.engine.update_previously_selected()

        # Check if the clicked position is in the spawn squares list
        if (row, col) in previously_selected.spawn_squares_list:
            # Perform the spawn action
            self.perform_spawn(previously_selected, row, col)

            # Return true and return to playing state
            return not self.revert_to_playing_state()
        return self.revert_to_playing_state()

    def perform_spawn(self, previously_selected, row, col):
        # Get the acting and action tiles
        acting_tile = self.engine.board[previously_selected.row][
            previously_selected.col
        ]
        action_tile = self.engine.board[row][col]

        # Create and add the spawn event
        spawn = type_of_spawn(acting_tile, action_tile, self.engine.spawning)
        event = spawn(self.engine, acting_tile, action_tile)
        self.engine.add_event(event)

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        self.revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        pass

    def tab(self):
        """
        Handles the tab key press event to revert to the playing state.
        """
        self.revert_to_playing_state()


class Winner(State):
    """
    Represents the winner state where the game displays the winning message.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Winner state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Set the font size based on the square size constant
        self.font_size = round(constant.SQ_SIZE * 2)

        # Load the font with the specified size
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Define the winning messages for each player
        self.key = {"w": "White Won!", "b": "Black Won!"}

        # Render the winning message based on the current turn
        self.text_surf = self.font.render(
            self.key[self.engine.turn], True, constant.turn_to_color[self.engine.turn]
        )

        # Initialize the sidebar with an empty state
        self.side_bar = Empty(self.win, self.engine)

        # Create a surface for the text box
        self.text_box = pygame.Surface(
            (self.text_surf.get_width(), self.text_surf.get_height())
        )

        # Get the window dimensions
        window_width = self.win.get_width()
        window_height = self.win.get_height()

        # Scale the paper texture for the text box
        self.text_box_ = self.scale_paper_texture(self.text_box)

        # Calculate the position for the text box
        self.text_box_x = constant.BOARD_WIDTH_PX // 2 - self.text_box.get_width() // 2
        self.text_box_y = (
            constant.BOARD_HEIGHT_PX // 2 - self.text_box.get_height() // 2
        )

        # Calculate the display position for the text surface
        self.display_x = window_width // 2 - self.text_surf.get_width() // 2
        self.display_y = window_height // 2 - self.text_surf.get_height() // 2

    def __repr__(self) -> str:
        """
        Returns a string representation of the Winner state.

        :return: A string representing the Winner state.
        """
        return "winner"

    def left_click(self):
        """
        Handles the left-click action to revert to the playing state.
        """
        self.engine.reset()

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        self.engine.reset()

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        pass

    def draw(self):
        """
        Draws the winner state, including the sidebar and the winning message.
        """
        # Draw the sidebar
        self.side_bar.draw()

        # Fill the text box with the menu color
        self.text_box.fill(constant.MENU_COLOR)

        # Draw the paper texture on the text box
        self.draw_paper_texture(self.text_box)

        # Blit the text surface onto the text box
        self.text_box.blit(self.text_surf, (0, 0))

        # Blit the text box onto the window
        self.win.blit(self.text_box, (self.text_box_x, self.text_box_y))

    def enter(self):
        """
        Handles the enter key press event to revert to the playing state.
        """
        self.engine.reset()

    def tab(self):
        """
        Handles the tab key press event to revert to the playing state.
        """
        self.engine.reset()


class Surrender(State):
    """
    Represents the surrender state where players can choose to surrender the game.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Surrender state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with a SurrenderMenu
        self.side_bar = SurrenderMenu(win, engine)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Surrender state.

        :return: A string representing the Surrender state.
        """
        return "surrender"

    def left_click(self):
        """
        Handles the left-click action to process the surrender.

        If the player is surrendering, it transitions to the Winner state.
        """
        # Process the left-click action on the sidebar
        self.side_bar.left_click()

        # Check if the player is surrendering
        if self.engine.surrendering:
            # Transition to the Winner state
            new_state = Winner(self.win, self.engine)
            self.engine.set_state(new_state)

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        self.revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        # Process the mouse movement on the sidebar
        self.side_bar.mouse_move()

    def tab(self):
        """
        Handles the tab key press event to revert to the playing state.
        """
        self.revert_to_playing_state()

    def draw(self):
        """
        Draws the surrender state, including the sidebar.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        self.side_bar.draw()


class PieceCost(State):
    """
    Represents the piece cost screen state where players can view the cost of pieces.
    """

    def __init__(
        self, win: pygame.Surface, engine: Engine, current_state: State = None
    ):
        """
        Initializes the PieceCost state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        :param current_state: The current state before transitioning to the PieceCost state.
        """
        # Set the current state
        self.current_state = current_state

        # Call the parent class initializer
        super().__init__(win, engine)

        # Create and append the Master menu to the engine's menus
        menu = Master(self.win, self.engine, constant.MASTER_COST_LIST)
        self.engine.menus.append(menu)

    def __repr__(self) -> str:
        """
        Returns a string representation of the PieceCost state.

        :return: A string representing the PieceCost state.
        """
        return "piece cost screen"

    def remove_top_menu(self):
        """
        Removes the top menu from the engine's menus.

        If there is only one menu left, it closes all menus and reverts to the previous state.
        """
        # Check if there is only one menu left
        if len(self.engine.menus) == 1:
            # Close all menus
            self.engine.close_menus()

            # Revert to the appropriate state based on the current state
            if str(self.current_state) == "playing":
                self.revert_to_playing_state()
            else:
                self.revert_to_starting_state()
        else:
            # Close the top menu and remove it from the list
            self.engine.menus[-1].close()
            del self.engine.menus[-1]

    def right_click(self):
        """
        Handles the right-click action to remove the top menu.
        """
        self.remove_top_menu()

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        # Process the mouse movement on the top menu if any menus are open
        if self.engine.menus:
            self.engine.menus[-1].mouse_move()

    def draw(self):
        """
        Draw only the top menu, if it does not exist, draw nothing.
        """
        try:
            # Draw the top menu
            self.engine.menus[-1].draw()
        except IndexError:
            pass

    def left_click(self) -> bool:
        """
        Handles the left-click action to interact with the top menu.

        :return: True if an action is successfully performed, otherwise False.
        """
        return self.engine.menus[-1].left_click()

    def enter(self):
        """
        Handles the enter key press event.
        """
        pass

    def tab(self):
        """
        Handles the tab key press event to remove the top menu.
        """
        self.remove_top_menu()


class Ritual(State):
    """
    Represents the ritual state where players can perform rituals on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Ritual state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Update the previously selected piece
        self.previously_selected: Unit = engine.update_previously_selected()

        # Reset the selected piece in the engine
        self.engine.reset_selected()

        # Set the performing_ritual flag to True for the previously selected piece
        self.previously_selected.performing_ritual = True

        # Initialize the cost type to None
        self.cost_type: Optional[str] = None

        # Get the current turn
        self.turn: str = self.engine.turn

        # Get the current player
        self.player: Player = self.engine.players[self.turn]

        # Load the ritual image based on the current turn and state
        self.ritual_image: pygame.Surface = constant.PRAYER_RITUALS[
            self.turn + "_" + str(self)
        ]

        # Close all menus in the engine
        self.engine.close_menus()

        # Set the pieces constant
        self.PIECES = constant.B_PIECES | constant.W_PIECES

    def click_valid_square(self, row: int, col: int) -> bool:
        """
        Checks if the clicked square is valid for performing the ritual.

        :param row: The row index of the clicked square.
        :param col: The column index of the clicked square.
        :return: True if the square is valid, otherwise False.
        """
        return (row, col) in self.previously_selected.ritual_squares_list

    def draw_ritual_at_mouse_position(self):
        """
        Draws the ritual image at the current mouse position.
        """
        # Get the current mouse position
        pos = pygame.mouse.get_pos()

        # Calculate the display position for the ritual image
        display_pos_x = pos[0] - constant.SQ_SIZE // 2
        display_pos_y = pos[1] - constant.SQ_SIZE // 2

        # Blit the ritual image onto the window
        self.win.blit(self.ritual_image, (display_pos_x, display_pos_y))

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        self.revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        pass

    def enter(self):
        """
        Handles the enter key press event.
        """
        pass

    def tab(self):
        """
        Handles the tab key press event to revert to the playing state.
        """
        self.revert_to_playing_state()


class SummonGoldGeneral(Ritual):
    """
    Represents the state where players can summon a Gold General on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the SummonGoldGeneral state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with a HUD
        self.side_bar: SideBar = Hud(self.win, self.engine)

        # Set the ritual squares list for the previously selected piece
        self.previously_selected.ritual_squares_list = (
            self.previously_selected.gold_general_ritual_squares(self.engine)
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the SummonGoldGeneral state.

        :return: A string representing the SummonGoldGeneral state.
        """
        return "gold_general"

    def draw(self):
        """
        Draws the SummonGoldGeneral state, including the sidebar and the ritual image.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        self.side_bar.draw()

        # Draw the ritual image at the mouse position
        self.draw_ritual_at_mouse_position()

    def click_valid_square(self, row: int, col: int) -> bool:
        """
        Checks if the clicked square is valid for summoning the Gold General.

        :param row: The row index of the clicked square.
        :param col: The column index of the clicked square.
        :return: True if the square is valid, otherwise False.
        """
        # Check if the tile is within bounds
        if self.engine.tile_in_bounds(row, col):
            # Check if the square is in the ritual squares list
            return (row, col) in self.previously_selected.ritual_squares_list
        return False

    def left_click(self) -> bool:
        """
        Handles the left-click action to summon the Gold General.

        :return: True if the action is successfully performed, otherwise False.
        """
        # Get the row and column of the clicked position
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Check if the clicked square is valid
        if self.click_valid_square(row, col):
            # Get the acting and action tiles
            acting_tile: Tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
            action_tile: Tile = self.engine.board[row][col]

            # Create and add the GoldGeneralEvent
            event: GoldGeneralEvent = GoldGeneralEvent(
                self.engine, acting_tile, action_tile
            )
            self.engine.add_event(event)

            # Revert to the playing state
            return self.revert_to_playing_state()
        else:
            # Revert to the playing state if the square is not valid
            return self.revert_to_playing_state()


class PerformSmite(Ritual):
    """
    Represents the state where players can perform a smite ritual on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the PerformSmite state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with a HUD
        self.side_bar: SideBar = Hud(self.win, self.engine)

        # Close all menus in the engine
        self.engine.close_menus()

        # Set the ritual squares list for the previously selected piece
        self.previously_selected.ritual_squares_list = self.smite_ritual_squares()

    def __repr__(self) -> str:
        """
        Returns a string representation of the PerformSmite state.

        :return: A string representing the PerformSmite state.
        """
        return "smite"

    def draw(self):
        """
        Draws the PerformSmite state, including the sidebar and the ritual image.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        self.side_bar.draw()

        # Draw the ritual image at the mouse position
        self.draw_ritual_at_mouse_position()

    def smite_ritual_squares(self) -> list[tuple[int, int]]:
        """
        Determines the valid squares for performing the smite ritual.

        :return: A list of tuples representing the valid squares.
        """
        list_of_enemy_pieces: list[tuple[int, int]] = []

        # Iterate over the pieces of the current player
        for piece in self.engine.players[constant.TURNS[self.engine.turn]].pieces:
            row, col = piece.row, piece.col

            # Check if the piece is not a King and is not protected
            if not isinstance(piece, King):
                if not self.engine.board[row][col].is_protected():
                    list_of_enemy_pieces.append((row, col))

        return list_of_enemy_pieces

    def left_click(self) -> bool:
        """
        Handles the left-click action to perform the smite ritual.

        :return: True if the action is successfully performed, otherwise False.
        """
        # Get the row and column of the clicked position
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Check if the clicked square is valid
        if self.click_valid_square(row, col):
            # Get the acting and action tiles
            acting_tile: Tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
            action_tile: Tile = self.engine.board[row][col]

            # Create and add the Smite event
            event: Smite = Smite(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)

            # Revert to the playing state
            return self.revert_to_playing_state()
        else:
            # Revert to the playing state if the square is not valid
            return self.revert_to_playing_state()


class PerformDestroyResource(Ritual):
    """
    Represents the state where players can perform a destroy resource ritual on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the PerformDestroyResource state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with a HUD
        self.side_bar: SideBar = Hud(self.win, self.engine)

        # Close all menus in the engine
        self.engine.close_menus()

        # Set the ritual squares list for the previously selected piece
        self.previously_selected.ritual_squares_list = (
            self.delete_resource_ritual_squares()
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the PerformDestroyResource state.

        :return: A string representing the PerformDestroyResource state.
        """
        return "destroy_resource"

    def draw(self):
        """
        Draws the PerformDestroyResource state, including the sidebar and the ritual image.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        self.side_bar.draw()

        # Draw the ritual image at the mouse position
        self.draw_ritual_at_mouse_position()

    def delete_resource_ritual_squares(self) -> list[tuple[int, int]]:
        """
        Determines the valid squares for performing the destroy resource ritual.

        :return: A list of tuples representing the valid squares.
        """
        list_of_all_resources: list[tuple[int, int]] = []

        # Iterate over all rows and columns on the board
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                # Check if the tile has a resource
                if self.engine.has_resource(row, col):
                    list_of_all_resources.append((row, col))

        return list_of_all_resources

    def left_click(self) -> bool:
        """
        Handles the left-click action to perform the destroy resource ritual.

        :return: True if the action is successfully performed, otherwise False.
        """
        # Get the row and column of the clicked position
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Check if the clicked square is valid
        if self.click_valid_square(row, col):
            # Get the acting and action tiles
            acting_tile: Tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]
            action_tile: Tile = self.engine.board[row][col]

            # Create and add the DestroyResource event
            event: DestroyResource = DestroyResource(
                self.engine, acting_tile, action_tile
            )
            self.engine.add_event(event)

            # Revert to the playing state
            return self.revert_to_playing_state()
        else:
            # Revert to the playing state if the square is not valid
            return self.revert_to_playing_state()


class PerformCreateResource(Ritual):
    """
    Represents the state where players can perform the ritual which creates a resource on the board.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the PerformCreateResource state.

        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        # Call the parent class initializer
        super().__init__(win, engine)

        # Initialize the sidebar with a HUD
        self.side_bar: SideBar = Hud(self.win, self.engine)

        # Close all menus in the engine
        self.engine.close_menus()

        # Set the ritual squares list for the previously selected piece
        self.previously_selected.ritual_squares_list = (
            self.create_resource_ritual_squares()
        )

        # Initialize row and col to None
        self.row: Optional[int] = None
        self.col: Optional[int] = None

    def __repr__(self) -> str:
        """
        Returns a string representation of the PerformCreateResource state.

        :return: A string representing the PerformCreateResource state.
        """
        return "create_resource"

    def draw(self):
        """
        Draws the PerformCreateResource state, including the sidebar and the ritual image.
        """
        # Call the parent class's draw method
        super().draw()

        # Draw the sidebar
        self.side_bar.draw()

        # Display Gold General at mouse position while mouse is on valid spawn square
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.draw()
        else:
            self.draw_ritual_at_mouse_position()

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        # Handle menu input for mouse movement
        if self.engine.menus:
            for menu in self.engine.menus:
                menu.mouse_move()

    def create_resource_ritual_squares(self) -> list[tuple[int, int]]:
        """
        Determines the valid squares for performing the resource creation ritual.

        :return: A list of tuples representing the valid squares.
        """
        list_of_all_empty_squares: list[tuple[int, int]] = []

        # Iterate over all rows and columns on the board
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                # Check if the tile is empty
                if self.engine.has_no_units_or_resources(row, col):
                    list_of_all_empty_squares.append((row, col))

        return list_of_all_empty_squares

    def left_click(self) -> bool:
        """
        Handles the left-click action to perform the resource creation ritual.

        :return: True if the action is successfully performed, otherwise False.
        """

        # Get the row and column of the clicked position based on the mouse coordinates
        row: int
        col: int
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Handle menu input
        if self.handle_menu_click():
            return True

        # Handle board click
        return self.handle_board_click(row, col)

    def handle_menu_click(self) -> bool:
        """
        Handles left-click interactions with open menus.

        :return: True if a menu was clicked and handled, otherwise False.
        """

        # Return early if there are no open menus
        if not self.engine.menus:
            return False

        # Iterate through all open menus and process left-click events
        for menu in self.engine.menus:
            menu_clicked: bool = menu.left_click()

            # If a menu click triggers a ritual summon, complete the ritual
            if menu_clicked and self.engine.ritual_summon_resource:
                self.complete_ritual_summon()
                return True

        return False

    def complete_ritual_summon(self):
        """
        Completes the ritual summoning of a resource by closing menus, creating an event,
        and reverting to the playing state.
        """

        # Close all open menus after selecting a resource to summon
        self.engine.close_menus()

        # Retrieve the tile where the spawn originates
        acting_tile: Tile = self.engine.board[self.previously_selected.row][
            self.previously_selected.col
        ]

        # Retrieve the target tile where the resource will be summoned
        action_tile: Tile = self.engine.board[self.row][self.col]

        # Create a new resource event using the acting and target tiles
        event: CreateResource = CreateResource(self.engine, acting_tile, action_tile)

        # Add the new event to the event manager
        self.engine.add_event(event)

        # Reset the ritual summon state
        self.engine.ritual_summon_resource = None

        # Revert to the playing state
        self.revert_to_playing_state()

    def handle_board_click(self, row: int, col: int) -> bool:
        """
        Handles left-click interactions with the board, allowing resource menu creation.

        :param row: The row index of the clicked position on the board.
        :param col: The column index of the clicked position on the board.
        :return: True if a valid square was clicked and handled, otherwise False.
        """

        # Check if the clicked position is a valid square and no ritual summoning is in progress
        if self.click_valid_square(row, col) and not self.engine.ritual_summon_resource:
            # Store the clicked position
            self.row = row
            self.col = col

            # Create a new resource menu at the clicked position
            menu: ResourceMenu = ResourceMenu(row, col, self.win, self.engine)

            # Add the resource menu to the engine's menu list
            self.engine.menus.append(menu)

            return True

        # If the clicked position is invalid, revert to the playing state
        self.revert_to_playing_state()
        return False


class PerformTeleport(Ritual):
    """
    Represents the teleportation ritual, allowing a player to move a piece to a valid square.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the PerformTeleport ritual.

        :param win: The game window surface.
        :param engine: The game engine managing the state.
        """

        # Initialize the parent class (Ritual)
        super().__init__(win, engine)

        # Create the sidebar HUD for displaying information
        self.side_bar: Hud = Hud(self.win, self.engine)

        # Close any open menus before performing the teleportation ritual
        self.engine.close_menus()

        # Store valid squares for teleportation based on ritual rules
        self.previously_selected.ritual_squares_list = self.get_teleport_able_pieces()

        # Store the selected piece for teleportation
        self.selected: Optional[Piece] = None

    def __repr__(self) -> str:
        """
        Returns the string representation of this ritual.

        :return: A string representing the ritual type.
        """
        return "teleport"

    def draw(self):
        """
        Draws the ritual state, including the sidebar and highlighted squares.
        """

        # Draw common ritual elements
        super().draw()

        # Draw the sidebar HUD
        self.side_bar.draw()

        # Draw the ritual effect at the mouse position
        self.draw_ritual_at_mouse_position()

        # Highlight the selected piece if one is chosen
        if self.selected:
            self.selected.highlight_self_square(self.win)

    def get_teleport_able_pieces(self) -> list[tuple[int, int]]:
        """
        Retrieves a list of pieces that can be teleported.

        :return: A list of (row, col) tuples representing teleport-able piece positions.
        """
        teleport_able_pieces: list[tuple[int, int]] = []

        # Add all player-controlled pieces that are not Buildings or Kings
        for piece in self.player.pieces:
            if not isinstance(piece, (Building, King)):
                teleport_able_pieces.append((piece.row, piece.col))

        # Add all opponent-controlled pieces that are not Buildings or Kings
        opponent_pieces: list[Unit] = self.engine.players[
            constant.TURNS[self.turn]
        ].pieces
        for piece in opponent_pieces:
            if not isinstance(piece, (King, Building)):
                teleport_able_pieces.append((piece.row, piece.col))

        return teleport_able_pieces

    def get_valid_teleport_squares(self) -> list[tuple[int, int]]:
        """
        Determines the valid squares where the selected piece can teleport.

        :return: A list of (row, col) tuples representing valid teleportation destinations.
        """
        valid_squares: list[tuple[int, int]] = []

        # Iterate over all board positions
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):

                # Check if the square is empty
                if self.engine.has_no_units_or_resources(row, col):
                    valid_squares.append((row, col))
                    continue

                # Check if the selected piece has special movement rules
                if self.selected:
                    if self.selected.is_rogue and self.engine.can_be_occupied_by_rogue(
                        row, col
                    ):
                        valid_squares.append((row, col))
                    elif (
                        self.selected.is_general
                        and self.engine.can_be_occupied_by_gold_general(row, col)
                    ):
                        valid_squares.append((row, col))

        return valid_squares

    def left_click(self) -> bool:
        """
        Handles the left-click action during the teleportation ritual.

        :return: True if the click is handled successfully, otherwise False.
        """

        # Get the row and column of the clicked position
        row: int
        col: int
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Handle selecting a piece to teleport
        if self.is_valid_selection(row, col):
            return True

        # Handle selecting a destination for teleportation
        if self.is_valid_destination(row, col):
            return self.perform_teleport(row, col)

        # If the click was invalid, return to the playing state
        return self.revert_to_playing_state()

    def is_valid_selection(self, row: int, col: int) -> bool:
        """
        Determines if the clicked square is a valid piece selection for teleportation.

        :param row: The row index of the clicked square.
        :param col: The column index of the clicked square.
        :return: True if a piece was successfully selected, otherwise False.
        """

        # Ensure the square is valid and no piece has been selected yet
        if self.click_valid_square(row, col) and self.selected is None:
            # Select the piece occupying the clicked square
            self.selected: Optional[Unit] = self.engine.get_occupying(row, col)

            # Update the list of valid teleportation squares
            self.previously_selected.ritual_squares_list = (
                self.get_valid_teleport_squares()
            )

            return True

        return False

    def is_valid_destination(self, row: int, col: int) -> bool:
        """
        Determines if the clicked square is a valid teleportation destination.

        :param row: The row index of the clicked square.
        :param col: The column index of the clicked square.
        :return: True if the clicked square is a valid teleport destination, otherwise False.
        """
        return self.click_valid_square(row, col) and self.selected is not None

    def perform_teleport(self, row: int, col: int) -> bool:
        """
        Performs the teleportation ritual by creating a teleport event.

        :param row: The target row index for teleportation.
        :param col: The target column index for teleportation.
        :return: Always returns True to indicate that teleportation was performed.
        """

        # Get the acting tile where the teleport initiates
        acting_tile: Tile = self.engine.board[self.previously_selected.row][
            self.previously_selected.col
        ]

        # Define the teleportation action from the current position to the new position
        action_tile: tuple[tuple[int, int], tuple[int, int]] = (
            (self.selected.row, self.selected.col),
            (row, col),
        )

        # Create and register a new teleport event
        event: Teleport = Teleport(self.engine, acting_tile, action_tile)
        self.engine.add_event(event)

        # Return to the playing state
        return self.revert_to_playing_state()


def is_valid_swap_piece(piece: Unit) -> bool:
    """
    Determines if a given piece can be swapped.

    :param piece: The piece to check.
    :return: True if the piece is swap-eligible, otherwise False.
    """

    # A valid piece for swapping cannot be a King or a Building
    return not isinstance(piece, (King, Building))


class PerformSwap(Ritual):
    """
    Represents the swap ritual, allowing a player to swap positions of two valid pieces.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the PerformSwap ritual.

        :param win: The game window surface.
        :param engine: The game engine managing the state.
        """

        # Initialize the parent class (Ritual)
        super().__init__(win, engine)

        # Create the sidebar HUD for displaying information
        self.side_bar: Hud = Hud(self.win, self.engine)

        # Close any open menus before starting the ritual
        self.engine.close_menus()

        # Track the first and second selected pieces for swapping
        self.first_selected: Optional[Unit] = None
        self.second_selected: Optional[Unit] = None

        # Store valid swap squares based on ritual rules
        self.previously_selected.ritual_squares_list = self.get_swappable_pieces()

        # If the selected piece is an assassin, preselect it and mark it as casting
        if str(self.previously_selected) == "assassin":
            self.first_selected = self.previously_selected
            self.first_selected.casting = True
            self.previously_selected.ritual_squares_list = self.get_swappable_pieces()

    def __repr__(self) -> str:
        """
        Returns the string representation of this ritual.

        :return: A string representing the ritual type.
        """
        return "swap"

    def draw(self):
        """
        Draws the ritual state, including the sidebar and selected piece highlights.
        """

        # Draw common ritual elements
        super().draw()

        # Draw the sidebar HUD
        self.side_bar.draw()

        # Draw the ritual effect at the mouse position
        self.draw_ritual_at_mouse_position()

        # If the first selected piece is an assassin, no further drawing is needed
        if self.first_selected and str(self.first_selected) == "assassin":
            return

    def get_swappable_pieces(self) -> list[tuple[int, int]]:
        """
        Retrieves a list of valid pieces that can be swapped.

        :return: A list of (row, col) tuples representing swap-able piece positions.
        """
        valid_pieces: list[tuple[int, int]] = []

        # If no piece has been selected, find a valid first selection from the player's pieces
        if not self.first_selected:
            for piece in self.engine.players[self.turn].pieces:
                if is_valid_swap_piece(piece):
                    valid_pieces.append((piece.row, piece.col))
            return valid_pieces

        # If the first piece is already selected, find valid second selections from the opponent's pieces
        for piece in self.engine.players[constant.TURNS[self.turn]].pieces:
            if is_valid_swap_piece(piece):
                valid_pieces.append((piece.row, piece.col))

        return valid_pieces

    def left_click(self) -> bool:
        """
        Handles the left-click action during the swap ritual.

        :return: True if the click is handled successfully, otherwise False.
        """

        # Get the row and column of the clicked position
        row: int
        col: int
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Handle selecting the first piece to swap
        if self.is_valid_first_selection(row, col):
            return True

        # Handle selecting the second piece to swap
        if self.is_valid_second_selection(row, col):
            return self.perform_swap(row, col)

        # If the click was invalid, return to the playing state
        return self.revert_to_playing_state()

    def is_valid_first_selection(self, row: int, col: int) -> bool:
        """
        Determines if the clicked square is a valid first piece selection for swapping.

        :param row: The row index of the clicked square.
        :param col: The column index of the clicked square.
        :return: True if a piece was successfully selected, otherwise False.
        """

        # Ensure the square is valid and no piece has been selected yet
        if self.click_valid_square(row, col) and self.first_selected is None:
            # Select the piece occupying the clicked square
            self.first_selected: Optional[Unit] = self.engine.get_occupying(row, col)

            # Mark the piece as casting the ritual
            self.first_selected.casting = True

            # Update the list of valid swap targets
            self.previously_selected.ritual_squares_list = self.get_swappable_pieces()

            return True

        return False

    def is_valid_second_selection(self, row: int, col: int) -> bool:
        """
        Determines if the clicked square is a valid second piece selection for swapping.

        :param row: The row index of the clicked square.
        :param col: The column index of the clicked square.
        :return: True if the clicked square is a valid swap destination, otherwise False.
        """
        return self.click_valid_square(row, col) and self.first_selected is not None

    def perform_swap(self, row: int, col: int) -> bool:
        """
        Performs the swap ritual by creating a swap event.

        :param row: The target row index for swapping.
        :param col: The target column index for swapping.
        :return: Always returns True to indicate that swapping was performed.
        """

        # Get the second selected piece
        self.second_selected: Optional[Unit] = self.engine.get_occupying(row, col)

        # Get the acting tile where the swap initiates
        acting_tile: Tile = self.engine.board[self.previously_selected.row][
            self.previously_selected.col
        ]

        # Define the swap action from the first piece's position to the second piece's position
        action_tile: tuple[tuple[int, int], tuple[int, int]] = (
            (self.first_selected.row, self.first_selected.col),
            (row, col),
        )

        # Create and register a new swap event
        event: Swap = Swap(self.engine, acting_tile, action_tile)
        self.engine.add_event(event)

        # Return to the playing state
        return self.revert_to_playing_state()


class PerformLineDestroy(Ritual):
    """
    Represents the line destroy ritual, allowing a player to destroy pieces in a straight line.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the PerformLineDestroy ritual.

        :param win: The game window surface.
        :param engine: The game engine managing the state.
        """

        # Initialize the parent class (Ritual)
        super().__init__(win, engine)

        # Create the sidebar HUD for displaying information
        self.side_bar: Hud = Hud(self.win, self.engine)

        # Close any open menus before starting the ritual
        self.engine.close_menus()

        # Define possible movement directions for the line destruction
        self.directions: tuple[str, str, str, str] = (
            constant.UP,
            constant.RIGHT,
            constant.LEFT,
            constant.DOWN,
        )

        # Store the position of the previously selected piece
        self.row: int = self.previously_selected.row
        self.col: int = self.previously_selected.col

        # Determine the current mouse position in board coordinates
        mouse_row: int
        mouse_col: int
        mouse_row, mouse_col = constant.convert_pos(pygame.mouse.get_pos())

        # Define movement ranges for each possible direction
        self.up: tuple[range, range] = (
            range(self.row - 1, -1, -1),
            range(self.col, self.col + 1),
        )
        self.down: tuple[range, range] = (
            range(self.row + 1, constant.BOARD_HEIGHT_SQ),
            range(self.col, self.col + 1),
        )
        self.right: tuple[range, range] = (
            range(self.row, self.row + 1),
            range(self.col + 1, constant.BOARD_WIDTH_SQ),
        )
        self.left: tuple[range, range] = (
            range(self.row, self.row + 1),
            range(self.col - 1, -1, -1),
        )

        # Determine the initial active destruction line based on mouse position
        self.selected_range: Optional[tuple[range, range]] = self.determine_active_line(
            mouse_row, mouse_col
        )

        # Store valid destruction squares based on the selected range
        self.previously_selected.ritual_squares_list = (
            self.active_line_destroy_ritual_squares(self.selected_range)
        )

    def __repr__(self) -> str:
        """
        Returns the string representation of this ritual.

        :return: A string representing the ritual type.
        """
        return "line_destroy"

    def draw(self):
        """
        Draws the ritual state, including the sidebar and visual effects.
        """

        # Draw common ritual elements
        super().draw()

        # Draw the sidebar HUD
        self.side_bar.draw()

        # Draw the ritual effect at the mouse position
        self.draw_ritual_at_mouse_position()

    def determine_active_line(
        self, row: int, col: int
    ) -> Optional[tuple[range, range]]:
        """
        Determines the active destruction line based on the given row and column.

        :param row: The row index of the target tile.
        :param col: The column index of the target tile.
        :return: A tuple containing the row and column ranges for the active destruction line.
        """

        # Ensure the target tile is within the board bounds
        if self.engine.tile_in_bounds(row, col):

            # Determine which directional range matches the target tile
            if row in self.up[0] and col == self.col:
                return self.up
            if row in self.down[0] and col == self.col:
                return self.down
            if col in self.right[1] and row == self.row:
                return self.right
            if col in self.left[1] and row == self.row:
                return self.left

        return None

    def mouse_move(self):
        """
        Updates the destruction line selection when the mouse moves.
        """

        # Get the row and column of the current mouse position
        row: int
        col: int
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Update the selected destruction line based on the mouse position
        self.selected_range = self.determine_active_line(row, col)

        # Update the list of affected squares for the ritual
        self.previously_selected.ritual_squares_list = (
            self.active_line_destroy_ritual_squares(self.selected_range)
        )

    def active_line_destroy_ritual_squares(
        self, selected_range: Optional[tuple[range, range]]
    ) -> list[tuple[int, int]]:
        """
        Determines which squares are affected by the line destruction.

        :param selected_range: The range of squares affected in a straight line.
        :return: A list of (row, col) tuples representing affected tiles.
        """

        active_line_squares: list[tuple[int, int]] = []

        # Ensure a valid range is selected before processing
        if selected_range:
            for r in selected_range[0]:
                for c in selected_range[1]:

                    # Stop if the tile is protected by the opposite player
                    if self.engine.board[r][c].is_protected_by_opposite_color(
                        self.engine.turn
                    ):
                        break

                    # Otherwise, add the tile to the affected list
                    active_line_squares.append((r, c))

        return active_line_squares

    def left_click(self) -> bool:
        """
        Handles the left-click action for executing the line destruction.

        :return: True if the ritual successfully executes, otherwise False.
        """

        # Get the row and column of the clicked position
        row: int
        col: int
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Ensure the clicked square is a valid target
        if not self.click_valid_square(row, col):
            return self.revert_to_playing_state()

        # Store the selected destruction range
        self.engine.line_destroy_selected_range = self.selected_range

        # Get the acting tile where the destruction originates
        acting_tile: Tile = self.engine.board[self.previously_selected.row][
            self.previously_selected.col
        ]

        # Get the action tile where the destruction is targeted
        action_tile: Tile = self.engine.board[row][col]

        # Create and register a new line destruction event
        event: LineDestroy = LineDestroy(self.engine, acting_tile, action_tile)
        self.engine.add_event(event)

        # If the enemy player's king is destroyed, transition to the Winner state
        if self.engine.enemy_king_does_not_exist():
            new_state: Winner = Winner(self.win, self.engine)
            self.engine.set_state(new_state)
            return True

        # Otherwise, return to the normal playing state
        return self.revert_to_playing_state()


class PerformProtect(Ritual):
    """
    Represents the protect ritual, allowing a player to protect an empty tile,
    a non-king piece, or a resource.

    :param win: The game window surface.
    :param engine: The game engine managing the state.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the PerformProtect ritual.

        :param win: The game window surface.
        :param engine: The game engine managing the state.
        """

        # Initialize the parent class (Ritual)
        super().__init__(win, engine)

        # Create the sidebar HUD for displaying information
        self.side_bar: Hud = Hud(win, engine)

        # Close any open menus before starting the ritual
        self.engine.close_menus()

        # Store the list of squares that can be protected
        self.previously_selected.ritual_squares_list = (
            self.protect_able_ritual_squares()
        )

    def __repr__(self) -> str:
        """
        Returns the string representation of this ritual.

        :return: A string representing the ritual type.
        """
        return "protect"

    def protect_able_ritual_squares(self) -> list[tuple[int, int]]:
        """
        Identifies which tiles are eligible for protection.

        :return: A list of (row, col) tuples representing protect-able tiles.
        """

        protect_able_squares: list[tuple[int, int]] = []

        # Iterate through each tile on the board
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):

                # If the tile is empty, it can be protected
                if self.engine.has_no_units_or_resources(row, col):
                    protect_able_squares.append((row, col))
                    continue

                # Check if a piece is occupying the tile
                piece: Optional[Piece] = self.engine.get_occupying(row, col)
                if piece and not isinstance(piece, King):
                    protect_able_squares.append((row, col))
                    continue

                # If the tile contains a resource, it can also be protected
                if self.engine.get_resource(row, col):
                    protect_able_squares.append((row, col))

        return protect_able_squares

    def draw(self):
        """
        Draws the ritual state, including the sidebar and visual effects.
        """

        # Draw common ritual elements
        super().draw()

        # Draw the sidebar HUD
        self.side_bar.draw()

        # Draw the ritual effect at the mouse position
        self.draw_ritual_at_mouse_position()

    def left_click(self) -> bool:
        """
        Handles the left-click action for executing the protect ritual.

        :return: True if the ritual successfully executes, otherwise False.
        """

        # Get the row and column of the clicked position
        row: int
        col: int
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Ensure the clicked square is a valid target
        if not self.click_valid_square(row, col):
            return self.revert_to_playing_state()

        # Get the acting tile where the protection originates
        acting_tile: Tile = self.engine.board[self.previously_selected.row][
            self.previously_selected.col
        ]

        # Get the action tile where the protection is applied
        action_tile: Tile = self.engine.board[row][col]

        # Create and register a new protection event
        event: Protect = Protect(self.engine, acting_tile, action_tile)
        self.engine.add_event(event)

        # Return to the normal playing state
        return self.revert_to_playing_state()


class PerformPortal(Ritual):
    """
    Represents the portal ritual, allowing a player to place a portal on a valid tile
    and then teleport a piece to a new location.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the PerformPortal ritual.

        :param win: The game window surface.
        :param engine: The game engine managing the state.
        """

        # Initialize the parent class (Ritual)
        super().__init__(win, engine)

        # Create the sidebar HUD for displaying information
        self.side_bar: Hud = Hud(win, engine)

        # Close any open menus before starting the ritual
        self.engine.close_menus()

        # Tracks the initially selected tile for the portal
        self.selected: Optional[Tile] = None

        # Store the list of valid squares where portals can be placed
        self.previously_selected.ritual_squares_list = self.valid_portal_squares()

    def __repr__(self) -> str:
        """
        Returns the string representation of this ritual.

        :return: A string representing the ritual type.
        """
        return "portal"

    def valid_portal_squares(self) -> list[tuple[int, int]]:
        """
        Identifies which tiles are eligible for portal placement.

        :return: A list of (row, col) tuples representing valid portal tiles.
        """

        valid_squares: list[tuple[int, int]] = []

        # Iterate through each tile on the board
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):

                # If the tile is empty, it can have a portal
                if self.engine.has_no_units_or_resources(row, col):
                    valid_squares.append((row, col))
                    continue

                # Check if a non-Piece and non-Building entity is occupying the tile
                piece: Optional[Piece] = self.engine.get_occupying(row, col)
                if piece and not isinstance(piece, (Piece, Building)):
                    valid_squares.append((row, col))
                    continue

                # If the tile contains a resource, it can also have a portal
                if self.engine.get_resource(row, col):
                    valid_squares.append((row, col))

        # Ensure the currently selected portal tile is not in the valid squares list
        if self.selected and (self.selected.row, self.selected.col) in valid_squares:
            valid_squares.remove((self.selected.row, self.selected.col))

        return valid_squares

    def draw(self):
        """
        Draws the ritual state, including the sidebar and portal effects.
        """

        # Draw common ritual elements
        super().draw()

        # Draw the sidebar HUD
        self.side_bar.draw()

        # Draw the ritual effect at the mouse position
        self.draw_ritual_at_mouse_position()

        # If a portal is selected, render its image at the appropriate location
        if self.selected:
            self.selected.draw_portal_image(self.win)

    def left_click(self) -> bool:
        """
        Handles the left-click action for executing the portal ritual.

        :return: True if the ritual successfully executes, otherwise False.
        """

        # Get the row and column of the clicked position
        row: int
        col: int
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # If no portal has been selected yet, set the first selected portal tile
        if self.click_valid_square(row, col) and self.selected is None:
            self.selected = self.engine.board[row][col]
            self.selected.portal_image = constant.IMAGES[self.turn + "_portal"]
            self.previously_selected.ritual_squares_list = self.valid_portal_squares()
            return True

        # If a portal has already been selected, finalize portal placement
        elif self.click_valid_square(row, col) and self.selected:

            # Get the acting tile where the portal was originally placed
            acting_tile: Tile = self.engine.board[self.previously_selected.row][
                self.previously_selected.col
            ]

            # Define the action tile as a movement from the original portal to the new location
            action_tile: tuple[tuple[int, int], tuple[int, int]] = (
                (self.selected.row, self.selected.col),
                (row, col),
            )

            # Create and register a new portal event
            event: Portal = Portal(self.engine, acting_tile, action_tile)
            self.engine.add_event(event)

            # Return to the normal playing state
            return self.revert_to_playing_state()

        # If the click is invalid, revert back to the playing state
        return self.revert_to_playing_state()
