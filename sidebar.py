from __future__ import annotations

import os
import random
import typing
from typing import Dict, List, Union

import pygame

import constant

if typing.TYPE_CHECKING:
    from unit import Unit
    from engine import Engine
    from player import Player


class SideBar:
    """
    Represents a sidebar in the game with various attributes and methods.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the sidebar with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        # Set the game window surface
        self.win: pygame.Surface = win

        # Default sidebar has no icon
        self.icon = None

        # Set the game engine
        self.engine: "Engine" = engine

        # Set the menu dimensions
        self.menu_height: int = constant.SIDE_MENU_HEIGHT
        self.menu_width: int = constant.SIDE_MENU_WIDTH

        # Create the menu surface
        self.menu: pygame.Surface = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture: pygame.Surface = (
            self.engine.get_current_state().scale_paper_texture(self.menu)
        )

    def update_icon(self):
        icon = f"{self.engine.turn}_game_name" if self.engine.turn else "w_game_name"
        self.icon = constant.IMAGES[icon]

    def draw(self):
        """
        Draws the sidebar on the game window.
        Does nothing by default, child classes can override this method.
        """
        pass

    def mouse_move(self):
        """
        Handles mouse movement over the sidebar.
        Does nothing by default, child classes can override this method.
        """
        pass

    def left_click(self):
        """
        Handles the left-click action on the sidebar.
        Does nothing by default, child classes can override this method.
        """
        pass

    def right_click(self):
        """
        Handles the right-click action on the sidebar.
        Does nothing by default, child classes can override this method.
        """
        pass


class Empty(SideBar):
    """
    Represents an empty sidebar in the game with various attributes and methods.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the empty sidebar with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        # Initialize the parent SideBar class
        super().__init__(win, engine)

    def draw(self):
        """
        Draws the empty sidebar on the game window.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Blit the menu surface onto the game window
        self.win.blit(self.menu, (constant.BOARD_WIDTH_SQ * constant.SQ_SIZE, 0))


class PieceInspector(SideBar):
    """
    Represents a piece inspector in the game with various attributes and methods.
    """

    def __init__(
        self, win: pygame.Surface, engine: "Engine", currently_selected: "Unit"
    ):
        """
        Initializes the piece inspector with the given window, engine, and currently selected piece.

        :param win: The game window surface.
        :param engine: The game engine.
        :param currently_selected: The currently selected unit.
        """
        # Initialize the parent class with window and engine
        super().__init__(win, engine)

        # Dictionary mapping player colors to their respective pieces and buildings
        self.PIECES: Dict[str, Dict[str, pygame.Surface]] = {
            "w": constant.W_PIECES | constant.W_BUILDINGS,
            "b": constant.B_PIECES | constant.B_BUILDINGS,
        }

        # Define font sizes based on the square size constant
        self.font_size: int = round(constant.SQ_SIZE / 3.5)
        self.small_font_size: int = round(constant.SQ_SIZE / 4)

        # Load fonts from the specified file path
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.small_font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.small_font_size
        )

        # Get the current player based on engine's turn
        self.player: "Player" = self.engine.players[self.engine.turn]

        # Set buffer space size
        self.buffer: int = constant.SQ_SIZE // 2

        # Dictionary mapping resource names to their corresponding menu icons
        self.RESOURCES: Dict[str, pygame.Surface] = {
            "wood": constant.MENU_ICONS["log"],
            "gold": constant.MENU_ICONS["gold_coin"],
            "stone": constant.MENU_ICONS["stone"],
        }

        # Render a space character to be used for spacing
        self.space: pygame.Surface = self.small_font.render(" ", True, constant.WHITE)

        # Store the currently selected piece
        self.piece: Unit = currently_selected

        # Determine the piece's color based on turn mapping
        self.color: tuple = constant.turn_to_color[self.piece.color]

        # Retrieve the description text for the selected piece
        self.description_text: List[str] = constant.DESCRIPTIONS[str(self.piece)]

        # List to store rendered description text surfaces
        self.description_text_surfaces: List[List[pygame.Surface]] = []

        # Process description text and ensure each new string starts on a new line
        for line in self.description_text:
            if line[0] == "?":
                line = " "
            words = line.split()
            line_surfaces = [
                self.small_font.render(word, True, self.color) for word in words
            ]
            self.description_text_surfaces.append(line_surfaces)

        # Store the width and height of the first rendered word if description is not empty
        if self.description_text_surfaces and self.description_text_surfaces[0]:
            self.description_text_width: int = self.description_text_surfaces[0][
                0
            ].get_width()
            self.description_text_height: int = self.description_text_surfaces[0][
                0
            ].get_height()

        # Construct the piece identifier string
        self.piece_identifier: str = self.piece.color + "_" + str(self.piece)

        # Retrieve the sprite for the selected piece based on its identifier
        self.sprite: pygame.Surface = self.PIECES[self.piece.color][
            self.piece_identifier
        ]

    def draw(self):
        """
        Draws the piece details onto the menu screen.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Get the current state and draw the paper texture
        state = self.engine.get_current_state()
        state.draw_paper_texture(self.menu)

        # Center the sprite on the menu
        sprite_x = (self.menu_width - self.sprite.get_width()) // 2
        self.menu.blit(self.sprite, (sprite_x, self.buffer))

        # Render and display the piece name
        name_surface = self.font.render(
            self.make_name_more_readable(), True, self.color
        )
        name_x = (self.menu_width - name_surface.get_width()) // 2
        y_buffer = self.buffer + self.sprite.get_height()
        self.menu.blit(name_surface, (name_x, y_buffer))

        # Display the cost of the piece
        y_buffer += name_surface.get_height()
        cost = self.engine.PIECE_COSTS[str(self.piece)]

        for resource, amount in cost.items():
            if amount == 0:
                continue

            player_has_enough = (
                getattr(self.player, constant.RESOURCE_KEY[resource]) >= amount
            )
            color = self.color if player_has_enough else constant.RED
            text_surf = self.font.render(str(amount), True, color)
            resource_icon = self.RESOURCES[constant.RESOURCE_KEY[resource]]

            # Center the resource icon and text together
            combined_width = resource_icon.get_width() + text_surf.get_width()
            resource_x = (self.menu_width - combined_width) // 2
            text_x = resource_x + resource_icon.get_width()

            self.menu.blit(resource_icon, (resource_x, y_buffer))
            self.menu.blit(text_surf, (text_x, y_buffer - text_surf.get_height() // 8))

            y_buffer += name_surface.get_height()

        # Display the piece description with line breaks
        if self.description_text_surfaces:
            # Set the starting x position for the text
            x_start = self.menu_width // 16

            # Iterate over each line of description text surfaces
            for line in self.description_text_surfaces:
                # Move to the next line by increasing the y buffer
                y_buffer += self.description_text_height
                # Reset x position for the new line
                x = x_start

                # Iterate over each word in the line
                for word in line:
                    # Check if the word exceeds the menu width
                    if x + word.get_width() >= self.menu_width:
                        # Move to the next line if the word exceeds the width
                        y_buffer += self.description_text_height
                        # Reset x position for the new line
                        x = x_start

                    # Blit the word surface onto the menu at the current x and y buffer positions
                    self.menu.blit(word, (x, y_buffer))
                    # Move the x position to the right by the width of the word and the space width
                    x += word.get_width() + self.space.get_width()
        # Render the menu onto the game window
        self.win.blit(self.menu, (constant.BOARD_WIDTH_SQ * constant.SQ_SIZE, 0))

    def make_name_more_readable(self) -> str:
        """
        Converts the piece name to a more readable format by replacing underscores with spaces
        and handling special cases.

        :return: The more readable name of the piece.
        """
        # Convert the piece to a string
        name: str = str(self.piece)

        # Replace underscores with spaces
        name = name.replace("_", " ")

        return name


def reselect_menu_color():
    return random.choice([constant.WHITE, constant.BLACK])


def reselect_faction_name():
    return random.choice(constant.FACTION_NAMES)


class Start(SideBar):
    """
    Represents the start sidebar in the game with various attributes and methods.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the start sidebar with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        # Initialize the parent SideBar class
        super().__init__(win, engine)

        # Randomized faction name and color for menu
        self.faction_name: str = reselect_faction_name()
        self.color: tuple = reselect_menu_color()

        # Font settings
        self.font_size: int = round(constant.SQ_SIZE / 3)
        font_path: str = os.path.join("files/fonts", "font.ttf")
        self.font: pygame.font.Font = pygame.font.Font(font_path, self.font_size)
        self.small_font: pygame.font.Font = pygame.font.Font(
            font_path, self.font_size // 2
        )

        # Version text display
        self.ver_text: str = f"{constant.VERSION} {constant.NUMBER}"
        self.version_text_surf: pygame.Surface = self.font.render(
            self.ver_text, True, self.color
        )
        self.version_text_display_x: int = (
            self.menu_width - self.version_text_surf.get_width()
        ) // 2

        # Map Image Selection
        self.reset_map_image: pygame.Surface = constant.RESOURCES[
            random.choice(constant.resources)
        ]
        self.map_image_height: int = self.reset_map_image.get_height()

        # Introduction Text
        self.introduction: list[str] = [self.ver_text, " ", "select", "your", "_"]

        # Boat Images
        self.w_boat: pygame.Surface = constant.IMAGES["w_boat"]
        self.b_boat: pygame.Surface = constant.IMAGES["b_boat"]
        self.boat_display_x: int = (self.menu_width - self.b_boat.get_width()) // 2

        # Positioning and Sizing
        section_height: float = self.menu_height * 1 / 5
        self.r: int = round(self.menu_height - section_height)
        self.display_y: int = constant.SQ_SIZE * 6

        # Highlighting States
        self.w_piece_highlight: bool = False
        self.b_piece_highlight: bool = False
        self.randomize_resources_highlight: bool = False

        # Scaling & Highlight Buffers
        self.scale: tuple = constant.IMAGES_IMAGE_MODIFY["w_boat"]["SCALE"]
        self.buffer: int = self.scale[0]
        self.square_highlight_buffer: int = constant.SQ_SIZE // 5

        # Create Highlight Squares
        self.square: pygame.Surface = constant.create_highlight_surface(self.scale)
        self.resources_square: pygame.Surface = constant.create_highlight_surface(
            (self.menu_width, round(section_height))
        )

        # Resource Highlight Height
        self.resource_highlight_height: int = round(constant.BOARD_HEIGHT_PX * 4 / 5)

        # Map Display Position
        self.reset_map_display_x: int = (
            self.menu_width - self.reset_map_image.get_width()
        ) // 2
        self.reset_map_display_y: int = (
            constant.BOARD_HEIGHT_PX
            - self.resources_square.get_height() // 2
            - self.map_image_height // 2
        )

        # Menu Display Position
        self.w_display_y: int = self.menu_height // 2 - self.b_boat.get_height() // 2
        self.b_display_y: int = (
            self.w_display_y + self.buffer + self.b_boat.get_height()
        )

    def draw(self):
        """
        Draws the start sidebar on the game window, including the introduction text, boats, highlights,
        and reset map image.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Precompute menu center to avoid repeated calculations
        menu_center_x: int = self.menu_width // 2
        y_buffer: int = constant.SQ_SIZE // 2

        # Render and display introduction text
        for line in self.introduction:
            # Determine the text to render
            text: str = self.faction_name if line == "_" else line
            # Choose the appropriate font
            font_to_use: pygame.font.Font = (
                self.small_font if line == self.introduction[0] else self.font
            )
            # Render the text surface
            surface: pygame.Surface = font_to_use.render(text, True, self.color)
            # Calculate the x position to center the text
            text_x: int = menu_center_x - surface.get_width() // 2
            # Blit the text surface onto the menu
            self.menu.blit(surface, (text_x, y_buffer))
            # Update the y buffer for the next line
            y_buffer += surface.get_height()

        # Display boats
        self.menu.blit(self.w_boat, (self.boat_display_x, self.w_display_y))
        self.menu.blit(self.b_boat, (self.boat_display_x, self.b_display_y))

        # Display highlights efficiently
        if self.b_piece_highlight:
            self.menu.blit(self.square, (self.boat_display_x, self.b_display_y))
        elif self.w_piece_highlight:
            self.menu.blit(self.square, (self.boat_display_x, self.w_display_y))
        elif self.randomize_resources_highlight:
            self.menu.blit(self.resources_square, (0, self.resource_highlight_height))

        # Display reset map image
        self.menu.blit(
            self.reset_map_image, (self.reset_map_display_x, self.reset_map_display_y)
        )

        # Render the menu onto the game window
        self.win.blit(self.menu, (constant.BOARD_WIDTH_PX, 0))

    def left_click(self):
        """
        Handles left-click interactions on the menu.
        """
        # Get the current mouse position
        pos: tuple[int, int] = pygame.mouse.get_pos()

        # Check if the click is on the menu (outside the board)
        if pos[0] <= constant.BOARD_WIDTH_PX:
            return

        # Calculate the mouse's position relative to the menu
        menu_mouse_x_position: int = pos[0] - constant.BOARD_WIDTH_PX

        # Check for boat selection
        if self.is_within_boat_area(menu_mouse_x_position, pos[1]):
            self.start_game()
            return

        # Check for reset action
        if self.is_within_reset_area(pos[1]):
            self.generate_new_resources()

    def is_within_boat_area(self, x: int, y: int) -> bool:
        """
        Checks if the click is within the boat selection area.

        :param x: The x-coordinate of the mouse position.
        :param y: The y-coordinate of the mouse position.
        :return: True if the click is within the boat selection area, otherwise False.
        """
        # Get the width of the boat image
        boat_width: int = self.w_boat.get_width()

        # Check if the click is within the bounds of the boat selection area
        return self.boat_display_x <= x <= self.boat_display_x + boat_width and (
            self.w_display_y <= y <= self.w_display_y + self.w_boat.get_height()
            or self.b_display_y <= y <= self.b_display_y + self.w_boat.get_height()
        )

    def start_game(self):
        """
        Starts the game with the selected turn color.
        """
        # Determine the turn color based on the mouse's y-coordinate
        self.engine.turn = "w" if pygame.mouse.get_pos()[1] < self.b_display_y else "b"

        # Set the new state of the game
        new_state: str = (
            "select starting pieces" if not constant.DEBUG_START else "debug"
        )
        self.engine.set_state(new_state)

    def is_within_reset_area(self, y: int) -> bool:
        """
        Checks if the click is within the reset button area.

        :param y: The y-coordinate of the mouse position.
        :return: True if the click is within the reset button area, otherwise False.
        """
        # Check if the y-coordinate is within the reset button area
        return self.menu_height * 4 // 5 <= y <= self.menu_height

    def generate_new_resources(self):
        """
        Resets the tiles of the board and randomizes resources.
        """
        # Reset the game board
        self.engine.reset_board()

        # Generate new resources
        self.engine.select_map()

        # Randomize the displayed reset map image
        self.reset_map_image: pygame.Surface = random.choice(
            list(constant.RESOURCES.values())
        )
        self.reset_map_display_x: int = (
            self.menu_width - self.reset_map_image.get_width()
        ) // 2
        self.reset_map_display_y: int = (
            constant.BOARD_HEIGHT_PX
            - self.resources_square.get_height() // 2
            - self.map_image_height // 2
        )

        # Reselect the faction name
        self.faction_name: str = reselect_faction_name()

    def mouse_move(self):
        """
        Handles mouse movement to update highlights and cursor appearance.
        """
        # Get the current mouse position
        mouse_x: int
        mouse_y: int
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Reset all highlights initially
        self.w_piece_highlight = False
        self.b_piece_highlight = False
        self.randomize_resources_highlight = False

        # Set default cursor to arrow
        cursor: int = pygame.SYSTEM_CURSOR_ARROW

        # Exit early if the mouse is not in the menu area
        if mouse_x <= constant.BOARD_WIDTH_PX:
            pygame.mouse.set_cursor(cursor)
            return

        # Calculate relative menu position
        menu_mouse_x_position: int = mouse_x - constant.BOARD_WIDTH_PX

        # Check if hovering over the white piece
        if (
            self.boat_display_x
            <= menu_mouse_x_position
            < self.boat_display_x + self.w_boat.get_width()
            and self.w_display_y
            <= mouse_y
            < self.w_display_y + self.w_boat.get_height()
        ):
            self.w_piece_highlight = True
            cursor = pygame.SYSTEM_CURSOR_HAND

        # Check if hovering over the black piece
        elif (
            self.boat_display_x
            <= menu_mouse_x_position
            < self.boat_display_x + self.w_boat.get_width()
            and self.b_display_y
            <= mouse_y
            < self.b_display_y + self.w_boat.get_height()
        ):
            self.b_piece_highlight = True
            cursor = pygame.SYSTEM_CURSOR_HAND

        # Check if hovering over the randomize resources button
        elif self.r <= mouse_y < self.menu_height:
            self.randomize_resources_highlight = True
            cursor = pygame.SYSTEM_CURSOR_HAND

        # Apply the final cursor setting
        pygame.mouse.set_cursor(cursor)


class SurrenderMenu(SideBar):
    """
    Represents the surrender sidebar in the game with various attributes and methods.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the surrender sidebar with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        super().__init__(win, engine)

        # Font settings
        self.font_size: int = round(constant.SQ_SIZE // 3)
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Text settings
        self.surrender_text: str = "Surrender?"
        self.surrender_text_surface: pygame.Surface = self.font.render(
            self.surrender_text, True, constant.turn_to_color[self.engine.turn]
        )

        # Button settings
        self.yes_button_address: str = self.engine.turn + "_yes"
        self.no_button_address: str = self.engine.turn + "_no"
        self.yes_button_image: pygame.Surface = constant.IMAGES[self.yes_button_address]
        self.no_button_image: pygame.Surface = constant.IMAGES[self.no_button_address]

        # Answer surface size
        self.answer_surface_width: int = self.yes_button_image.get_width()
        self.answer_surface_height: int = self.yes_button_image.get_height()

        # Highlight states
        self.yes_highlight: bool = False
        self.no_highlight: bool = False

        # Highlight squares
        self.square: pygame.Surface = constant.create_highlight_surface(
            (constant.SQ_SIZE * 2 // 3, constant.SQ_SIZE * 2 // 3)
        )

        # Positioning calculations
        self.buffer: int = constant.SQ_SIZE // 2

        self.question_display_x: int = (
            self.menu_width // 2 - self.surrender_text_surface.get_width() // 2
        )
        self.question_display_y: int = (
            self.menu_height // 2 - self.surrender_text_surface.get_height() // 2
        )
        self.yes_display_x: int = (
            self.menu_width // 2 - self.yes_button_image.get_width() // 2
        )
        self.yes_display_y: int = self.question_display_y + 2 * self.buffer

        self.no_display_x: int = (
            self.menu_width // 2 - self.no_button_image.get_width() // 2
        )
        self.no_display_y: int = (
            self.yes_display_y + self.yes_button_image.get_height() + self.buffer
        )
        self.yes_square_display_x: int = (
            self.yes_display_x
            + self.answer_surface_width // 2
            - self.square.get_width() // 2
        )
        self.no_square_display_x: int = (
            self.no_display_x
            + self.answer_surface_width // 2
            - self.square.get_width() // 2
        )
        self.yes_square_display_y: int = (
            self.yes_display_y
            + self.answer_surface_height // 2
            - self.square.get_height() // 2
        )
        self.no_square_display_y: int = (
            self.no_display_y
            + self.answer_surface_height // 2
            - self.square.get_height() // 2
        )

    def mouse_move(self):
        """
        Handles mouse movement over the menu area, highlighting buttons and changing cursor.
        """
        # Get the current mouse position
        mouse_x: int
        mouse_y: int
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Set the default cursor to arrow
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Reset highlights for 'Yes' and 'No' buttons
        self.yes_highlight = False
        self.no_highlight = False

        # Exit early if the mouse is not in the menu area
        if mouse_x <= constant.BOARD_WIDTH_PX:
            return

        # Calculate the mouse's position relative to the menu
        menu_x: int = mouse_x - constant.BOARD_WIDTH_PX

        # Check if hovering over 'Yes' button
        if (
            self.yes_display_y
            <= mouse_y
            < self.yes_display_y + self.answer_surface_height
            and self.yes_display_x
            <= menu_x
            < self.yes_display_x + self.answer_surface_width
        ):
            self.yes_highlight = True
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return

        # Check if hovering over 'No' button
        if (
            self.no_display_y
            <= mouse_y
            < self.no_display_y + self.answer_surface_height
            and self.no_display_x
            <= menu_x
            < self.no_display_x + self.answer_surface_width
        ):
            self.no_highlight = True
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def left_click(self) -> bool:
        """
        Handles the left-click action on the surrender menu.
        :return: True if the "Yes" button was clicked, otherwise None.
        """
        # Get the current mouse position
        pos: tuple[int, int] = pygame.mouse.get_pos()

        # Exit early if the click is not in the menu area
        if pos[0] <= constant.BOARD_WIDTH_PX:
            return False

        # Calculate the mouse's position relative to the menu
        menu_x: int = pos[0] - constant.BOARD_WIDTH_PX
        menu_y: int = pos[1]

        # Check if "Yes" was clicked
        if (
            self.yes_display_y
            <= menu_y
            < self.yes_display_y + self.answer_surface_height
            and self.yes_display_x
            <= menu_x
            < self.yes_display_x + self.answer_surface_width
        ):
            self.engine.change_turn()
            self.engine.surrendering = True
            return True

        # Check if "No" was clicked
        if (
            self.no_display_y <= menu_y < self.no_display_y + self.answer_surface_height
            and self.no_display_x
            <= menu_x
            < self.no_display_x + self.answer_surface_width
        ):
            return self.engine.state[-1].revert_to_playing_state()
        return False

    def draw(self):
        """
        Draws the surrender sidebar on the game window, including the surrender text, buttons, and highlights.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Blit the surrender text surface onto the menu
        self.menu.blit(
            self.surrender_text_surface,
            (self.question_display_x, self.question_display_y),
        )

        # Display highlights for the 'Yes' and 'No' buttons
        if self.yes_highlight:
            self.menu.blit(
                self.square, (self.yes_square_display_x, self.yes_square_display_y)
            )
        elif self.no_highlight:
            self.menu.blit(
                self.square, (self.no_square_display_x, self.no_square_display_y)
            )

        # Blit the 'Yes' and 'No' button images onto the menu
        self.menu.blit(self.yes_button_image, (self.yes_display_x, self.yes_display_y))
        self.menu.blit(self.no_button_image, (self.no_display_x, self.no_display_y))

        # Render the menu onto the game window
        self.win.blit(self.menu, (constant.BOARD_WIDTH_SQ * constant.SQ_SIZE, 0))


class Hud(SideBar):
    """
    Represents the HUD (Heads-Up Display) sidebar in the game with various attributes and methods.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the HUD sidebar with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        super().__init__(win, engine)

        # Get the width and height of the title icon
        self.title_icon_width: int = constant.IMAGES["w_game_name"].get_width()
        self.title_icon_height: int = constant.IMAGES["w_game_name"].get_height()

        # Update the icon
        self.update_icon()

        # Calculate the display position for the title icon
        self.title_icon_display_x: int = (
            self.menu_width // 2 - self.title_icon_width // 2
        )
        self.title_icon_display_y: int = (
            self.menu_height // 8 - self.title_icon_height // 2
        )

        # Set font sizes and load fonts
        self.font_size: int = constant.SQ_SIZE // 2
        self.small_font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size // 2
        )
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Set display positions for various icons
        self.counter_icon_display_x: int = constant.BOARD_WIDTH_PX + 10
        self.coin_icon_display_y: int = round(self.menu_height * (8 / 10))
        self.icon_y_offset: int = constant.SQ_SIZE // 1.2
        self.stone_icon_display_y: int = self.coin_icon_display_y + self.icon_y_offset
        self.log_icon_display_y: int = self.coin_icon_display_y - self.icon_y_offset
        self.prayer_icon_display_y: int = self.log_icon_display_y - self.icon_y_offset
        self.action_icon_display_y: int = (
            self.prayer_icon_display_y - self.icon_y_offset
        )
        self.units_icon_display_y: int = self.action_icon_display_y - self.icon_y_offset
        self.turn_icon_display_y: int = self.units_icon_display_y - self.icon_y_offset

        # Resource Counters
        self.resources: dict[str, tuple[str, int]] = {
            "gold_coin": ("gold", self.coin_icon_display_y),
            "log": ("wood", self.log_icon_display_y),
            "stone": ("stone", self.stone_icon_display_y),
        }

        # Get the width and height of the prayer bar
        self.bar_end_width: int = constant.IMAGES["prayer_bar_end"].get_width()
        self.bar_width: int = constant.IMAGES["prayer_bar"].get_width()
        self.bar_height: int = constant.IMAGES["prayer_bar"].get_height()

        # Set buffer for counter text
        self.counter_text_buffer: int = constant.SQ_SIZE // 2

        # Calculate the height and edges for the prayer bar
        self.prayer_bar_height: int = (
            self.prayer_icon_display_y
            + round(constant.MENU_ICONS["prayer"].get_height() // 2)
            - round(self.bar_height // 2)
        )
        self.prayer_bar_edge: int = (
            self.counter_icon_display_x + self.counter_text_buffer
        )
        self.prayer_bar_end_edge: int = self.prayer_bar_edge + self.bar_width

        # Create an empty text surface
        self.empty_text_surface: pygame.Surface = self.font.render(
            "0", True, constant.WHITE
        )

        # Calculate the vertical offset for text
        self.text_vertical_offset: int = (
            self.empty_text_surface.get_height() // 2
            - constant.MENU_ICONS["log"].get_height() // 2
        )

        # Create a highlight square surface
        self.square: pygame.Surface = pygame.Surface(
            (constant.SIDE_MENU_WIDTH, round(constant.SIDE_MENU_HEIGHT * 0.25))
        )
        self.title_bar_highlight: bool = False
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def draw(self):
        """
        Draws the menu, HUD elements, and various counters.

        :param self: The instance of the class.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Display State in HUD
        if constant.DISPLAY_STATE_IN_HUD:
            self._draw_hud_text()

        # Highlight Title Bar
        if self.title_bar_highlight:
            self.menu.blit(self.square, (0, 0))

        # Draw Title Icon
        self.menu.blit(
            self.icon, (self.title_icon_display_x, self.title_icon_display_y)
        )

        # Render the menu onto the game window
        self.win.blit(self.menu, (constant.BOARD_WIDTH_PX, 0))

        # Draw resource counters
        for img_key, (resource, y_pos) in self.resources.items():
            value: int = getattr(self.engine.players[self.engine.turn], resource)
            if value:
                self._draw_resource_counter(img_key, value, y_pos)

        # Draw prayer counter
        self._draw_prayer_counter()

        # Draw actions remaining counter
        actions_remaining: int = self.engine.players[
            self.engine.turn
        ].get_actions_remaining()
        self._draw_basic_counter(
            "action", self.action_icon_display_y, actions_remaining
        )

        # Draw unit limit counter
        current_population: int = self.engine.players[
            self.engine.turn
        ].get_current_population()
        piece_limit: int = self.engine.players[self.engine.turn].get_piece_limit()
        self._draw_basic_counter(
            "units", self.units_icon_display_y, f"{current_population}/{piece_limit}"
        )

        # Draw turn counter
        turn_count_display: float = self.engine.turn_count_display
        self._draw_basic_counter(
            "hour_glass", self.turn_icon_display_y, turn_count_display
        )

    def _draw_hud_text(self):
        """
        Draws state and selected text in the HUD.

        :param self: The instance of the class.
        """
        # Render the current state text
        state_text: pygame.Surface = self.small_font.render(
            str(self.engine.state[-1]), True, constant.turn_to_color[self.engine.turn]
        )

        # Render map text
        map_text: pygame.Surface = self.small_font.render(
            str(self.engine.map), True, constant.turn_to_color[self.engine.turn]
        )

        # Render the previously selected text
        selected_text: pygame.Surface = self.small_font.render(
            str(self.engine.update_previously_selected()),
            True,
            constant.turn_to_color[self.engine.turn],
        )

        # Blit the state and selected text onto the menu
        for i, text in enumerate([state_text, selected_text, map_text], start=1):
            self.menu.blit(
                text,
                (
                    self.menu_width // 2 - text.get_width() // 2,
                    self.square.get_height() * i,
                ),
            )

    def _draw_resource_counter(self, img_key: str, value: int, y_pos: int):
        """
        Draws a single resource counter.

        :param self: The instance of the class.
        :param img_key: The key for the resource image.
        :param value: The value of the resource.
        :param y_pos: The y-coordinate position to draw the counter.
        """
        # Blit the resource image onto the window
        self.win.blit(constant.IMAGES[img_key], (self.counter_icon_display_x, y_pos))

        # Render the resource value text
        text_surf: pygame.Surface = self.font.render(
            str(value), True, constant.turn_to_color[self.engine.turn]
        )

        # Blit the resource value text onto the window
        self.win.blit(
            text_surf,
            (
                self.counter_icon_display_x + self.counter_text_buffer,
                y_pos - self.text_vertical_offset,
            ),
        )

    def _draw_basic_counter(
        self, img_key: str, y_pos: int, value: Union[float, int, str]
    ):
        """
        Draws a basic counter (actions, units, turn).

        :param self: The instance of the class.
        :param img_key: The key for the counter image.
        :param y_pos: The y-coordinate position to draw the counter.
        :param value: The value of the counter.
        """
        # Blit the counter image onto the window
        self.win.blit(constant.IMAGES[img_key], (self.counter_icon_display_x, y_pos))

        # Render the counter value text
        text_surf: pygame.Surface = self.font.render(
            str(value), True, constant.turn_to_color[self.engine.turn]
        )

        # Blit the counter value text onto the window
        self.win.blit(
            text_surf,
            (
                self.counter_icon_display_x + self.counter_text_buffer,
                y_pos - self.text_vertical_offset,
            ),
        )

    def _draw_prayer_counter(self):
        """
        Draws the prayer counter and progress bar.

        :param self: The instance of the class.
        """
        # Get the current player
        player: Player = self.engine.players[self.engine.turn]

        # Check if the player has prayer points
        if player.prayer:
            # Blit the prayer icon onto the window
            self.win.blit(
                constant.MENU_ICONS["prayer"],
                (self.counter_icon_display_x, self.prayer_icon_display_y),
            )

            # Blit the prayer bar onto the window
            self.win.blit(
                constant.IMAGES["prayer_bar"],
                (self.prayer_bar_edge, self.prayer_bar_height),
            )

            # Blit the prayer bar end images based on the player's prayer points
            for x in range(player.prayer):
                self.win.blit(
                    constant.IMAGES["prayer_bar_end"],
                    (
                        self.prayer_bar_end_edge + self.bar_end_width * x,
                        self.prayer_bar_height,
                    ),
                )

    def mouse_move(self):
        """
        Handles mouse movement over the title bar area. It highlights the title bar based on the
        mouse position and updates the mouse cursor to a hand when hovering over the title bar.
        """
        # Get the current mouse position
        pos = pygame.mouse.get_pos()

        # Check if the mouse is within the board area (right of the board)
        if pos[0] < constant.BOARD_WIDTH_PX:
            return False

        # Check if the mouse is over the title bar area (top 25% of the screen)
        if 0 < pos[1] < constant.BOARD_HEIGHT_PX * 0.25:
            # Set highlight and cursor if the mouse is in the title bar area
            self.title_bar_highlight = True
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return True

        # Reset title bar highlight and cursor if not in the menu area
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.title_bar_highlight = False
        return False

    def left_click(self) -> bool:
        """
        Handles the left-click action on the HUD.
        :return: True if the click is within the title bar area and the screen is transferred, otherwise None.
        """
        # Get the current mouse position
        pos: tuple[int, int] = pygame.mouse.get_pos()

        # Check if the click is within the menu area (right of the board)
        if pos[0] < constant.BOARD_WIDTH_PX:
            return False

        # Check if the click is within the title bar area (top 25% of the screen)
        if 0 < pos[1] < constant.BOARD_HEIGHT_PX * 0.25:
            # Transfer to the piece cost screen
            return self.engine.transfer_to_piece_cost_screen()

        return False
