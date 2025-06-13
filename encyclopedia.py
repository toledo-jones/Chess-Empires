from __future__ import annotations

import os
import typing
from typing import List, Tuple, Dict, Optional, Union

import pygame

import constant
from menu import Menu
from tile import Tile

if typing.TYPE_CHECKING:
    from player import Player
    from engine import Engine


class Encyclopedia(Menu):
    """
    Represents the Encyclopedia menu in the game, displaying various information and resources.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the Encyclopedia menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        super().__init__(win, engine)

        # Scale paper texture
        self.paper_texture: pygame.Surface = (
            self.engine.get_current_state().scale_paper_texture(self.win)
        )
        self.description: bool = False

        # Window Variables
        self.window_width: int = pygame.display.Info().current_w
        self.window_height: int = pygame.display.Info().current_h

        # Font Sizes
        self.small_font_size: int = round(constant.SQ_SIZE * 0.5)
        self.large_font_size: int = round(constant.SQ_SIZE * 1.6)

        # Initialize Fonts
        self.large_font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.large_font_size
        )
        self.small_font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.small_font_size
        )

        # Boiler Plate
        try:
            self.color: pygame.Color = constant.turn_to_color[self.engine.turn]
            self.player: Optional["Player"] = self.engine.players[self.engine.turn]
        except KeyError:
            self.color = pygame.Color("black")
            self.player = None

        self.resources: Dict[str, pygame.Surface] = {
            "wood": constant.MENU_ICONS["log"],
            "gold": constant.MENU_ICONS["gold_coin"],
            "stone": constant.MENU_ICONS["stone"],
        }
        self.icons: Dict[str, pygame.Surface] = (
            constant.W_PIECES
            | constant.W_BUILDINGS
            | constant.B_PIECES
            | constant.B_BUILDINGS
            | constant.PRAYER_RITUALS
            | constant.RESOURCES
        )
        self.title_text_format_key: Dict[str, str] = {"prayer_stone": "floating stone"}
        self.menu_logo: Optional[pygame.Surface] = self.get_menu_logo(str(self))
        self.title_text: str = self.format_title_text(str(self))
        if self.title_text.endswith(" 0"):
            self.title_text = self.title_text[:-2]  # Remove trailing "_0" if present
        self.text_surf: pygame.Surface = self.large_font.render(
            self.title_text, True, self.color
        )
        self.title_text_width: int = self.text_surf.get_width()
        self.title_text_height: int = self.text_surf.get_height()
        self.menu_key: Dict[str, type] = self.engine.COST_MENUS

        # Graphics Math
        self.title_text_display_x: int = (
            self.window_width // 2 - self.title_text_width // 2
        )
        self.title_text_display_y: int = (
            round(self.window_height * 1 / 6) - self.title_text_height // 2
        )
        self.menu_logo_display_x, self.menu_logo_display_y = (
            self.get_menu_logo_position()
        )

    def get_menu_logo_position(self) -> Tuple[int, int]:
        """
        Calculates the position for the menu logo.

        :return: A tuple containing the x and y coordinates for the menu logo.
        """
        if self.menu_logo:
            x: int = self.window_width // 2 - self.menu_logo.get_width() // 2
            y: int = self.title_text_display_y + self.title_text_height
            return x, y
        return 0, 0

    def get_menu_logo(self, piece: str) -> Optional[pygame.Surface]:
        """
        Retrieves the menu logo for the given piece.

        :param piece: The piece identifier.
        :return: The menu logo surface.
        """
        menu_logo: Optional[pygame.Surface] = None
        if piece != "costs":
            try:
                piece = self.engine.turn + "_" + str(self)
            except TypeError:
                piece = f"w_{str(self)}"
            menu_logo = self.icons.get(piece)
        return menu_logo

    def format_title_text(self, piece: str) -> str:
        """
        Formats the title text for the given piece.

        :param piece: The piece identifier.
        :return: The formatted title text.
        """
        if piece in self.title_text_format_key:
            return self.title_text_format_key[piece]
        return piece.replace("_", " ")


def justify_text(font, text, max_width, color):
    """Formats and displays text within a given width using a pygame font.
    - Starts a new line after a period.
    - Wraps words normally when reaching the edge.
    - Ensures readability and proper formatting.
    """

    # Split the text into sentences based on periods
    sentences = text.split(". ")

    # List to store lines of formatted text
    lines = []

    for sentence in sentences:
        words = sentence.split()
        current_line = []
        current_width = 0

        for word in words:
            # Get the width of the word including a space
            word_width, _ = font.size(word + " ")

            # If adding this word exceeds max_width and current_line is not empty
            if current_width + word_width > max_width and current_line:
                lines.append(current_line)
                current_line = []
                current_width = 0

            # Add the word to the current line
            current_line.append(word)
            current_width += word_width

        # Append the sentence as a separate line
        if current_line:
            lines.append(current_line)

    # List to store rendered lines as pygame surfaces
    rendered_lines = []

    for line in lines:
        # Render the line with normal spacing (no justification spreading)
        text_surface = font.render(" ".join(line), True, color)
        rendered_lines.append(text_surface)

    return rendered_lines


class PieceDescription(Encyclopedia):
    """
    Represents the description and visualization of a game piece or ritual,
    including its board representation, cost, and description text.
    """

    def __init__(self, win: pygame.Surface, engine: Engine, selected: str):
        """
        Initializes the PieceDescription class.

        :param win: The game window surface.
        :param engine: The game engine containing board state and logic.
        :param selected: The selected piece or ritual identifier.
        """
        # Store selected item
        self.selected: str = selected

        # Call superclass initializer
        super().__init__(win, engine)

        # Define alternating square colors for the board
        self.colors: List[Tuple[int, int, int]] = [
            constant.DARK_SQUARE_COLOR,
            constant.LIGHT_SQUARE_COLOR,
        ]
        self.color_key: Dict[int, str] = {0: "dark", 1: "light"}

        # Create a copy of the engine's board state
        self.board_copy: List[List[Tile]] = self.engine.board

        # Define font size and load the font
        self.small_font_size: int = round(constant.SQ_SIZE * (1 / 3))
        self.small_font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.small_font_size
        )

        # Define board dimensions
        self.cols: int = 7
        self.rows: int = 7

        # Initialize the board with Tile objects
        self.board: List[List[Tile]] = [
            [Tile(row, col) for col in range(self.cols)] for row in range(self.rows)
        ]
        self.engine.board = self.board

        # Create the board surface
        self.board_surface: pygame.Surface = pygame.Surface(
            (self.cols * constant.SQ_SIZE, self.rows * constant.SQ_SIZE)
        )

        # Define board positioning on the window
        self.board_x: int = self.window_width // 40
        self.board_y: int = (self.window_height - self.board_surface.get_height()) // 2

        # Load description text
        self.description_text: List[str] = constant.DESCRIPTIONS[str(self)]
        self.description_text_surfs: List[pygame.Surface] = []

        # Render description text as pygame surfaces
        for line in self.description_text:
            text_surf: pygame.Surface = self.small_font.render(line, True, self.color)
            self.description_text_surfs.append(text_surf)

        # Get dimensions of description text
        self.description_text_width: int = self.description_text_surfs[0].get_width()
        self.description_text_height: int = self.description_text_surfs[0].get_height()

        # Load images for prayer bar display
        self.prayer_bar_end: pygame.Surface = constant.IMAGES["prayer_bar_end"]
        self.prayer_bar: pygame.Surface = constant.IMAGES["prayer_bar"]
        self.bar_end_width: int = self.prayer_bar_end.get_width()
        self.bar_width: int = self.prayer_bar.get_width()

        # Initialize cost and type variables
        self.cost: Optional[Union[dict[str, int], int]] = None
        self.type: Optional[str] = None

        # Define text box positioning
        self.text_box_x: int = self.board_surface.get_width() + self.board_x * 2
        self.text_box_width: int = self.window_width - (
            self.board_surface.get_width() + self.board_x * 3
        )
        self.text_box: pygame.Surface = pygame.Surface(
            (self.text_box_width, self.window_height // 2.2)
        )

        # Scale Paper surface to text box
        self.paper_surface_text_box: pygame.Surface = (
            self.engine.get_current_state().scale_paper_texture(self.text_box)
        )

        # Determine cost and type based on selection
        try:
            self.cost = constant.PRAYER_COSTS[self.selected]["prayer"]
            self.type = "ritual"
        except KeyError:
            self.cost = self.engine.PIECE_COSTS[self.selected]
            self.type = "piece"

        # Adjust layout for piece selection
        self.move_offset: int = 0
        if self.type == "piece":
            self.move_offset = self.window_width // 8

        # Define layout calculations for cost display
        self.cost_display_y: int = (
            self.window_height // 2 - self.resources["wood"].get_height() // 2
        )
        self.x_buffer_between_costs: int = round(constant.SQ_SIZE * 1.5)
        self.description_text_y: int = (
            self.cost_display_y + self.description_text_height
        )
        self.cost_display_x: int = 0

        # Determine cost display positioning based on type
        if self.type == "piece":
            count: int = sum(
                1
                for cost in self.engine.PIECE_COSTS[self.selected]
                if self.engine.PIECE_COSTS[self.selected][cost] != 0
            )
            full_length: int = (
                self.resources["wood"].get_width() * count
                + (self.x_buffer_between_costs // 2) * count
            )
            self.cost_display_x = (
                self.window_width // 2
                - full_length // 2
                + self.board_x // 2
                + self.board_surface.get_width() // 2
            )
            self.title_text_display_x: int = (
                self.window_width // 2
                - self.title_text_width // 2
                + self.board_x // 2
                + self.board_surface.get_width() // 2
            )
            self.menu_logo_display_x: int = (
                self.window_width // 2
                - self.menu_logo.get_width() // 2
                + self.board_x // 2
                + self.board_surface.get_width() // 2
            )
            self.set_up_demonstration_board()

        elif self.type == "ritual":
            length_of_this_prayer_bar: int = self.full_length_of_prayer_bar(self.cost)
            self.cost_display_x = (
                self.window_width // 2 - length_of_this_prayer_bar // 2
            )
            self.text_box_x = (self.window_width - self.text_box_width) // 2

    def __repr__(self) -> str:
        """
        Returns a string representation of the selected piece or ritual.

        :return: The selected piece or ritual identifier.
        """
        return self.selected

    def draw(self):
        """
        Renders the piece description screen, including board, costs, and text.
        """
        # Fill background with menu color
        self.win.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.win)

        # Draw cost display based on type
        if self.type == "ritual":
            self.draw_ritual_cost()
        elif self.type == "piece":
            self.draw_piece_cost()
            self.draw_board()
            self.win.blit(self.board_surface, (self.board_x, self.board_y))

        # Render title and menu logo
        self.win.blit(
            self.text_surf, (self.title_text_display_x, self.title_text_display_y)
        )
        self.win.blit(
            self.menu_logo, (self.menu_logo_display_x, self.menu_logo_display_y)
        )

        # Set initial position for description text rendering
        y_buffer: int = 0
        max_width: int = self.text_box.get_width()
        self.text_box.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.text_box)

        # Render and justify description text
        for line_surface in justify_text(
            self.small_font, " ".join(self.description_text), max_width, self.color
        ):
            x_position: int = (max_width - line_surface.get_width()) // 2
            self.text_box.blit(line_surface, (x_position, y_buffer))
            y_buffer += self.description_text_height

        # Blit the text box to the screen
        self.win.blit(self.text_box, (self.text_box_x, self.description_text_y))

    def set_up_demonstration_board(self):
        """
        Sets up the demonstration board with the selected piece.

        :return: None
        """
        # Get the current player's color
        color: str = self.engine.turn
        if not color:
            color = "w"

        # Set the piece at the center of the board
        row, col = 3, 3
        self.board[row][col].set_occupying(
            self.engine.PIECES[self.selected](row, col, color)
        )

        # Update the squares and display moves for the piece
        occupying_piece = self.board[row][col].get_occupying()
        occupying_piece.update_squares(self.engine)
        occupying_piece.display_moves = True

    def draw_piece_cost(self):
        """
        Draws the cost of the selected piece on the screen.
        """
        cost_x: int = self.cost_display_x

        for resource, amount in self.cost.items():
            if amount == 0:
                continue

            # Determine the color based on the player's resources
            try:
                player_resource = getattr(self.player, constant.RESOURCE_KEY[resource])
                color = self.color if player_resource >= amount else constant.RED
            except AttributeError:
                color = self.color

            # Render the cost text
            text_surf: pygame.Surface = self.small_font.render(
                f" {amount}", True, color
            )
            resource_position: Tuple[int, int] = (cost_x, self.cost_display_y)

            # Blit the resource icon and cost text onto the window
            resource_icon = self.resources[constant.RESOURCE_KEY[resource]]
            self.win.blit(resource_icon, resource_position)

            cost_text_position: Tuple[int, int] = (
                cost_x + self.resources["wood"].get_width(),
                self.cost_display_y - self.resources["wood"].get_height() // 3,
            )
            self.win.blit(text_surf, cost_text_position)

            cost_x += self.x_buffer_between_costs

    def close(self):
        """
        Restores the original board state.
        """
        # Restore the original board state
        self.engine.board = self.board_copy

    def draw_ritual_cost(self):
        """
        Draws the cost of the selected ritual on the screen.
        """
        # Calculate the starting edge for the prayer bar
        bar_end_edge: int = self.cost_display_x

        # Draw the prayer bar
        self.win.blit(
            self.prayer_bar, (bar_end_edge - self.bar_width, self.cost_display_y)
        )

        # Draw each segment of the prayer bar
        for index in range(self.cost):
            new_edge: int = bar_end_edge + self.bar_end_width * index
            self.win.blit(self.prayer_bar_end, (new_edge, self.cost_display_y))

    def draw_board(self):
        """
        Draws the board with squares and pieces.
        """
        # Draw the board squares and tiles
        for row in range(self.rows):
            for col in range(self.cols):
                # Calculate the color for the current square
                color = self.colors[(row + col) % 2]

                # Determine the rectangle size for the current square
                rect_size = (constant.SQ_SIZE, constant.SQ_SIZE)

                # Calculate position for the square, with the offset
                x = col * constant.SQ_SIZE
                y = row * constant.SQ_SIZE

                # Draw the square
                pygame.draw.rect(
                    self.board_surface,
                    color,
                    pygame.Rect(x, y, rect_size[0], rect_size[1]),
                )

                # Draw the tile using blend mode (avoid re-evaluating color calculation)
                tile_color = self.color_key[(row + col) % 2]
                self.board_surface.blit(
                    constant.BOARD_TILES[tile_color][self.board[row][col].index],
                    (x, y),
                    special_flags=pygame.BLEND_RGBA_MULT,
                )

        # Draw the board pieces
        for row in range(self.rows):
            for col in range(self.cols):
                self.board[row][col].draw_highlights(self.board_surface)

        # Draw the board pieces
        for row in range(self.rows):
            for col in range(self.cols):
                self.board[row][col].draw(self.board_surface)

    def full_length_of_prayer_bar(self, cost: int) -> int:
        """
        Calculates the full length of the prayer bar based on the cost.

        :param cost: The cost of the prayer.
        :return: The full length of the prayer bar.
        """
        return self.bar_end_width * cost + self.bar_width

    def mouse_move(self):
        """
        Handles mouse movement events.
        """
        pass

    def right_click(self):
        """
        Handles right-click events.
        """
        pass

    def left_click(self):
        """
        Handles left-click events.
        """
        pass


class Cost(Encyclopedia):
    """
    Represents the cost menu in the game, displaying various costs for spawning items.
    """

    def __init__(self, win: pygame.Surface, engine: Engine, spawn_list: List[str]):
        """
        Initializes the Cost menu with the given window, engine, and spawn list.

        :param win: The game window surface.
        :param engine: The game engine.
        :param spawn_list: The list of items to spawn.
        """
        super().__init__(win, engine)

        # Initialize board copy
        self.board_copy: Optional[List[List[Tile]]] = None

        # Store the spawn list
        self.spawn_list: List[str] = spawn_list

        # Store the game window surface
        self.win: pygame.Surface = win

        # Store the game engine
        self.engine: Engine = engine

        # Initialize highlight list
        self.highlight_list: List[bool] = []

        # Initialize column list
        self.column_list: List[pygame.Surface] = []

        # Determine the buffer between columns
        self.x_buffer_between_columns: int = constant.SQ_SIZE // 3

        # Determine the column width
        self.column_width: int = round(constant.SQ_SIZE * 1.5)

        # Determine the buffer between costs
        self.y_buffer_between_costs: int = constant.SQ_SIZE // 2

        # Determine the buffer between costs in the x direction
        self.x_buffer_between_costs: int = self.x_buffer_between_columns // 3

        # Get the height of the resource icon
        resource_height: int = self.resources[
            constant.RESOURCE_KEY["stone"]
        ].get_height()

        # Calculate the column height
        self.column_height: int = (self.y_buffer_between_costs * 3) + (
            resource_height * 3
        )

        # Calculate the x position for displaying the text
        self.text_display_x: int = self.window_width // 2 - self.title_text_width // 2

        # Calculate the y position for displaying the text
        self.text_display_y: int = (
            round(self.window_height * 1 / 6) - self.title_text_height // 2
        )

        # Calculate the total width of all columns and buffers
        self.width_of_of_all_columns_and_buffers: int = (
            self.column_width + self.x_buffer_between_columns
        ) * len(self.spawn_list)

        # Calculate the y position for displaying the columns
        self.column_display_y: int = round(self.window_height * 1 / 2)

        # Initialize columns and highlights
        for _ in self.spawn_list:
            self.highlight_list.append(False)
            column: pygame.Surface = pygame.Surface(
                [self.column_width, self.column_height], pygame.SRCALPHA, 32
            )
            column = column.convert_alpha()
            self.column_list.append(column)

        # Create the highlight surface
        self.highlight: pygame.Surface = constant.create_highlight_surface(
            (self.column_width, self.column_height)
        )

    def mouse_move(self):
        """
        Handles mouse movement over the menu. It checks if the mouse is over any of the columns
        and highlights the appropriate column. It also changes the mouse cursor to a hand when hovering
        over a column and resets it to the default arrow cursor when outside any column area.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate the initial position for displaying the columns
        column_display_x = (
            self.window_width // 2 - self.width_of_of_all_columns_and_buffers // 2
        )

        # Flag to check if the cursor is over any column
        cursor_over_column = False

        # Iterate over each column to check if the mouse is hovering over it
        for index, column in enumerate(self.column_list):
            # Check if the mouse is within the vertical bounds of the column
            is_within_column_y = (
                self.column_display_y
                <= mouse_y
                <= self.column_display_y + self.column_height
            )

            # Check if the mouse is within the horizontal bounds of the column
            is_within_column_x = (
                column_display_x <= mouse_x <= column_display_x + self.column_width
            )

            if is_within_column_x and is_within_column_y:
                # Highlight the column and set the cursor to a hand
                self.highlight_list[index] = True
                cursor_over_column = True
            else:
                # Remove highlight
                self.highlight_list[index] = False

            # Move the starting position for the next column
            column_display_x += self.column_width + self.x_buffer_between_columns

        # Set the cursor to a hand if it is over any column, otherwise reset to the default arrow
        if cursor_over_column:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def left_click(self):
        """
        Handles left-click events. If a piece is selected, it creates a PieceDescription menu
        and appends it to the engine's menu list.

        :return: True if a piece is selected and a menu is created.
        """
        # Get the selected piece
        selected: Optional[str] = self.piece_selected()

        # If a piece is selected, create a PieceDescription menu and append it to the engine's menus
        if selected is not None:
            menu: PieceDescription = PieceDescription(self.win, self.engine, selected)
            self.engine.menus.append(menu)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return True

    def draw(self):
        """
        Draws the cost menu on the screen, including the background, text, and columns with pieces and their costs.
        """
        # Fill the window with the menu color
        self.win.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.win)

        # Draw the title text
        self.win.blit(self.text_surf, (self.text_display_x, self.text_display_y))

        # Draw the menu logo if it exists
        if self.menu_logo:
            self.win.blit(
                self.menu_logo, (self.menu_logo_display_x, self.menu_logo_display_y)
            )

        # Calculate the initial position for displaying the columns
        column_display_x: int = (
            self.window_width // 2 - self.width_of_of_all_columns_and_buffers // 2
        )

        # Iterate over each column to draw the pieces and their costs
        for column in self.column_list:
            index: int = self.column_list.index(column)

            # Highlight the column if it is selected
            if self.highlight_list[index]:
                self.win.blit(self.highlight, (column_display_x, self.column_display_y))

            # Get the piece and its cost
            piece: str = self.spawn_list[index]
            cost: Dict[str, int] = self.engine.PIECE_COSTS[piece]

            # Determine the piece identifier based on the engine's turn
            try:
                piece = self.engine.turn + "_" + piece
            except TypeError:
                piece = f"w_{piece}"

            # Calculate the position for displaying the piece
            piece_display_x: int = (
                self.column_width // 2 - self.icons[piece].get_width() // 2
            )

            # Draw the piece icon
            column.blit(self.icons[piece], (piece_display_x, 0))

            # Initialize the y-buffer for displaying the cost
            y_buffer: int = self.icons[piece].get_height()

            # Iterate over each resource in the cost to draw the resource icon and amount
            for resource, amount in cost.items():
                resource_sprite: pygame.Surface = self.resources[
                    constant.RESOURCE_KEY[resource]
                ]

                # Skip if the cost amount is zero
                if amount != 0:
                    # Determine the color based on the player's resources
                    try:
                        if (
                            getattr(self.player, constant.RESOURCE_KEY[resource])
                            >= amount
                        ):
                            color: pygame.Color = self.color
                        else:
                            color = constant.RED
                    except AttributeError:
                        color = self.color

                    # Render the cost text
                    text_surface: pygame.Surface = self.small_font.render(
                        str(amount), True, color
                    )

                    # Calculate the position for displaying the resource icon and cost text
                    resource_position: Tuple[int, int] = (
                        self.column_width // 4 - resource_sprite.get_width() // 2,
                        y_buffer + resource_sprite.get_height() // 8,
                    )
                    cost_text_position: Tuple[int, int] = (
                        self.column_width * 2 // 3,
                        y_buffer - text_surface.get_height() // 8,
                    )

                    # Draw the resource icon and cost text
                    column.blit(resource_sprite, resource_position)
                    column.blit(text_surface, cost_text_position)

                    # Update the y-buffer for the next resource
                    y_buffer += self.y_buffer_between_costs

            # Draw the column on the window
            self.win.blit(column, (column_display_x, self.column_display_y))

            # Update the x position for the next column
            column_display_x += self.column_width + self.x_buffer_between_columns

    def piece_selected(self) -> Optional[str]:
        """
        Determines which piece is selected based on the current mouse position.

        :return: The identifier of the selected piece if one is selected, otherwise None.
        """
        # Get the current mouse position
        pos: Tuple[int, int] = pygame.mouse.get_pos()

        # Calculate the initial position for displaying the columns
        column_display_x: int = (
            self.window_width // 2 - self.width_of_of_all_columns_and_buffers // 2
        )

        # Check if the mouse is within the vertical bounds of the columns
        if not (
            self.column_display_y <= pos[1] < self.column_display_y + self.column_height
        ):
            return None

        # Iterate over each column to check if the mouse is hovering over it
        for index, column in enumerate(self.column_list):
            # Check if the mouse is within the horizontal bounds of the column
            if column_display_x <= pos[0] < column_display_x + self.column_width:
                # Return the identifier of the selected piece
                return self.spawn_list[index]

            # Move the starting position for the next column
            column_display_x += self.column_width + self.x_buffer_between_columns

        # Return None if no piece is selected
        return None


def full_spawn_list(spawn_list: dict[int, list[str]]) -> list[str]:
    """
    Composes a full list of pieces from the given spawn list.
    :param spawn_list: dictionary of spawn lists, where keys are ranks (integers) and values are lists of strings.
    :return: list of strings representing all pieces in all ranks in the spawn list
    """
    # Initialize an empty list to hold all pieces
    _full_spawn_list: list[str] = []
    # Iterate through the spawn list and append each piece to the full list
    for key, value in spawn_list.items():
        # Iterate over each piece in the value list.
        for piece in value:
            # Append piece to full spawn list
            _full_spawn_list.append(piece)
    return _full_spawn_list


class Master(Cost):
    """
    Represents the Master cost menu in the game, displaying various costs for spawning items.
    """

    def __init__(self, win: pygame.Surface, engine: Engine, spawn_list: List[str]):
        """
        Initializes the Master cost menu with the given window, engine, and spawn list.

        :param win: The game window surface.
        :param engine: The game engine.
        :param spawn_list: The list of items to spawn.
        """
        super().__init__(win, engine, spawn_list)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Master cost menu.

        :return: The string "costs".
        """
        return "costs"

    def left_click(self) -> Optional[bool]:
        """
        Handles left-click events. If a piece is selected, it creates a Menu and appends it to the engine's menu list.

        :return: True if a piece is selected and a menu is created.
        """
        # Get the selected piece
        piece_selected: Optional[str] = self.piece_selected()

        # If a piece is selected, create a Menu and append it to the engine's menus
        if piece_selected is not None:
            menu: Menu = self.menu_key[piece_selected](self.win, self.engine)
            self.engine.menus.append(menu)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return True


class BuilderCosts(Cost):
    """
    Represents the Builder cost menu in the game, displaying various costs for spawning builder items.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Builder cost menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        spawn_list: List[str] = constant.BUILDER_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Builder cost menu.

        :return: The string "builder".
        """
        return "builder"


class CastleCosts(Cost):
    """
    Represents the Castle cost menu in the game, displaying various costs for spawning castle items.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Castle cost menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        spawn_list: List[str] = full_spawn_list(constant.CASTLE_SPAWN_LIST)
        super().__init__(win, engine, spawn_list)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Castle cost menu.

        :return: The string "castle".
        """
        return "castle_0"


class StableCosts(Cost):
    """
    Represents the Stable cost menu in the game, displaying various costs for spawning stable items.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Stable cost menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        spawn_list: List[str] = full_spawn_list(constant.STABLE_SPAWN_LIST)
        super().__init__(win, engine, spawn_list)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Stable cost menu.

        :return: The string "stable".
        """
        return "stable_0"


class CircusCosts(Cost):
    """
    Represents the Circus cost menu in the game, displaying various costs for spawning circus items.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Circus cost menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        spawn_list: List[str] = full_spawn_list(constant.CIRCUS_SPAWN_LIST)
        super().__init__(win, engine, spawn_list)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Circus cost menu.

        :return: The string "circus".
        """
        return "circus_0"


class MonkCosts(Cost):
    """
    Represents the Monk cost menu in the game, displaying various costs for spawning monk items.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Monk cost menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        spawn_list: List[str] = constant.MONK_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def left_click(self) -> Optional[bool]:
        """
        Handles left-click events. If a piece is selected, it creates a Menu and appends it to the engine's menu list.

        :return: True if a piece is selected and a menu is created.
        """
        # Get the selected piece
        piece_selected: Optional[str] = self.piece_selected()

        # If a piece is selected, create a Menu and append it to the engine's menus
        if piece_selected is not None:
            menu: Menu = self.menu_key[piece_selected](self.win, self.engine)
            self.engine.menus.append(menu)
            return True

    def __repr__(self) -> str:
        """
        Returns a string representation of the Monk cost menu.

        :return: The string "monk".
        """
        return "monk"


class FortressCosts(Cost):
    """
    Represents the Fortress cost menu in the game, displaying various costs for spawning fortress items.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Fortress cost menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        spawn_list: List[str] = full_spawn_list(constant.FORTRESS_SPAWN_LIST)
        super().__init__(win, engine, spawn_list)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Fortress cost menu.

        :return: The string "fortress".
        """
        return "fortress_0"


class BarracksCosts(Cost):
    """
    Represents the Barracks cost menu in the game, displaying various costs for spawning barracks items.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Barracks cost menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        spawn_list: List[str] = full_spawn_list(constant.BARRACKS_SPAWN_LIST)
        super().__init__(win, engine, spawn_list)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Barracks cost menu.

        :return: The string "barracks".
        """
        return "barracks_0"


class RitualCosts(Cost):
    """
    Represents the Ritual cost menu in the game, displaying various costs for performing rituals.
    """

    def __init__(self, win: pygame.Surface, engine: Engine, spawn_list: List[str]):
        """
        Initializes the Ritual cost menu with the given window, engine, and spawn list.

        :param win: The game window surface.
        :param engine: The game engine.
        :param spawn_list: The list of items to spawn.
        """
        super().__init__(win, engine, spawn_list)

        # Store the rituals from constants
        self.rituals: Dict[str, pygame.Surface] = constant.PRAYER_RITUALS

        # Get the width and height of the ritual icon
        self.ritual_width: int = self.rituals["w_swap"].get_width()
        self.ritual_height: int = self.rituals["w_swap"].get_height()

        # Set the column width to the ritual width
        self.column_width: int = self.ritual_width

        # Calculate the total height of the cost column
        total_height_of_cost_column: int = (
            self.y_buffer_between_costs * 3 + self.x_buffer_between_columns
        )

        # Set the highlight width and dimensions
        self.highlight_width: int = self.ritual_width
        self.highlight_dimensions: Tuple[int, int] = (
            self.highlight_width,
            total_height_of_cost_column,
        )

        # Create the highlight square surface
        self.square: pygame.Surface = pygame.Surface(self.highlight_dimensions)
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Load the prayer bar images
        self.prayer_bar_end: pygame.Surface = constant.IMAGES["prayer_bar_end"]
        self.prayer_bar: pygame.Surface = constant.IMAGES["prayer_bar"]

        # Get the width of the prayer bar end and bar
        self.bar_end_width: int = self.prayer_bar_end.get_width()
        self.bar_width: int = self.prayer_bar.get_width()

        # Calculate the x position for displaying the piece
        self.piece_display_x: int = (
            (self.win.get_width() // 2)
            - self.column_width // 2
            - (self.ritual_width // 2) * len(self.highlight_list)
        )

        # Set the y position for displaying the piece
        self.piece_display_y: int = self.win.get_height() // 2

        # Set the y position for displaying the prayer bar
        self.bar_display_y: int = self.piece_display_y + self.y_buffer_between_costs * 3

    def full_length_of_prayer_bar(self, cost: int) -> int:
        """
        Calculates the full length of the prayer bar based on the cost.

        :param cost: The cost of the prayer.
        :return: The full length of the prayer bar.
        """
        return self.bar_end_width * cost + self.bar_width

    def draw(self):
        """
        Draws the ritual cost menu on the screen, including the background, text,
        and columns with rituals and their costs.
        """
        # Fill the window with the menu color
        self.win.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.win)

        # Draw the title text
        self.win.blit(self.text_surf, (self.text_display_x, self.text_display_y))

        # Draw the menu logo if it exists
        if self.menu_logo:
            self.win.blit(
                self.menu_logo, (self.menu_logo_display_x, self.menu_logo_display_y)
            )

        # Calculate the initial position for displaying the pieces
        piece_display_x: int = self.piece_display_x

        # Iterate over each piece to draw the rituals and their costs
        for i in range(len(self.spawn_list)):
            piece: str = self.spawn_list[i]
            cost: Dict[str, int] = constant.PRAYER_COSTS[piece]

            # Determine the ritual identifier based on the engine's turn
            try:
                ritual: str = self.engine.turn + "_" + piece
            except TypeError:
                ritual = f"w_{piece}"

            # Highlight the piece if it is selected
            if self.highlight_list[i]:
                self.win.blit(self.square, (piece_display_x, self.piece_display_y))

            # Draw the ritual icon
            self.win.blit(self.rituals[ritual], (piece_display_x, self.piece_display_y))

            # Calculate the length of the prayer bar
            length_of_this_prayer_bar: int = self.full_length_of_prayer_bar(
                cost["prayer"]
            )

            # Calculate the starting edge for the prayer bar
            bar_end_edge: int = (
                piece_display_x
                + self.ritual_width // 2
                - length_of_this_prayer_bar // 2
            )

            # Draw the prayer bar
            self.win.blit(
                self.prayer_bar, (bar_end_edge - self.bar_width, self.bar_display_y)
            )

            # Draw each segment of the prayer bar
            for z in range(cost["prayer"]):
                new_edge: int = bar_end_edge + self.bar_end_width * z
                self.win.blit(self.prayer_bar_end, (new_edge, self.bar_display_y))

            # Update the x position for the next piece
            piece_display_x += self.column_width + self.x_buffer_between_columns


class PrayerStoneCosts(RitualCosts):
    """
    Represents the Prayer Stone cost menu in the game, displaying various costs for performing prayer stone rituals.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Prayer Stone cost menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        # Get the list of prayer stone rituals from constants
        spawn_list: List[str] = constant.PRAYER_STONE_RITUALS
        super().__init__(win, engine, spawn_list)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Prayer Stone cost menu.

        :return: The string "prayer_stone".
        """
        return "prayer_stone"


class MonolithCosts(RitualCosts):
    """
    Represents the Monolith cost menu in the game, displaying various costs for performing monolith rituals.
    """

    def __init__(self, win: pygame.Surface, engine: Engine):
        """
        Initializes the Monolith cost menu with the given window and engine.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        # Get the list of monolith rituals from constants
        spawn_list: List[str] = constant.MONOLITH_RITUALS
        super().__init__(win, engine, spawn_list)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Monolith cost menu.

        :return: The string "monolith".
        """
        return "monolith"
