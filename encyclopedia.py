from __future__ import annotations

import os
import typing
from typing import List, Tuple, Dict, Optional

import pygame

import constant
from menu import Menu
from tile import Tile

if typing.TYPE_CHECKING:
    pass


class Encyclopedia(Menu):
    def __init__(self, win, engine):
        self.win = win
        self.engine = engine
        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(
            self.win
        )
        self.description = False

        # Window Variables
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h

        # Font Sizes
        self.small_font_size = round(constant.SQ_SIZE * 0.5)
        self.large_font_size = round(constant.SQ_SIZE * 1.6)

        # Initialize Fonts
        self.large_font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.large_font_size
        )
        self.small_font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.small_font_size
        )

        # Boiler Plate
        try:
            self.color = constant.turn_to_color[self.engine.turn]
            self.player = self.engine.players[self.engine.turn]
        except KeyError:
            self.color = pygame.Color("black")
            self.player = None
        self.resources = {
            "wood": constant.MENU_ICONS["log"],
            "gold": constant.MENU_ICONS["gold_coin"],
            "stone": constant.MENU_ICONS["stone"],
        }
        self.icons = (
            constant.W_PIECES
            | constant.W_BUILDINGS
            | constant.B_PIECES
            | constant.B_BUILDINGS
            | constant.PRAYER_RITUALS
            | constant.RESOURCES
        )
        self.title_text_format_key = {"prayer_stone": "floating stone"}
        self.menu_logo = self.get_menu_logo(str(self))
        self.title_text = self.format_title_text(str(self))
        self.text_surf = self.large_font.render(self.title_text, True, self.color)
        self.title_text_width = self.text_surf.get_width()
        self.title_text_height = self.text_surf.get_height()
        self.menu_key = self.engine.COST_MENUS

        # Graphics Math
        self.title_text_display_x = self.window_width // 2 - self.title_text_width // 2
        self.title_text_display_y = (
            round(self.window_height * 1 / 6) - self.title_text_height // 2
        )
        self.menu_logo_display_x, self.menu_logo_display_y = (
            self.get_menu_logo_position()
        )

    def get_menu_logo_position(self):
        if self.menu_logo:
            x = self.window_width // 2 - self.menu_logo.get_width() // 2
            y = self.title_text_display_y + self.title_text_height
            return x, y
        return 0, 0

    def get_menu_logo(self, piece):
        menu_logo = None
        if piece != "costs":
            try:
                piece = self.engine.turn + "_" + str(self)
            except TypeError:
                piece = f"w_{str(self)}"
            menu_logo = self.icons[piece]
        return menu_logo

    def format_title_text(self, piece):
        if piece in self.title_text_format_key.keys():
            return self.title_text_format_key[piece]
        return piece.replace("_", " ")


class PieceDescription(Encyclopedia):
    """
    Represents the description and visualization of a game piece or ritual,
    including its board representation, cost, and description text.
    """

    def __init__(self, win: pygame.Surface, engine, selected: str) -> None:
        """
        Initializes the PieceDescription class.

        Args:
            win (pygame.Surface): The game window surface.
            engine: The game engine containing board state and logic.
            selected (str): The selected piece or ritual identifier.
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
        self.board_copy = self.engine.board

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
            [Tile(x, y) for y in range(self.cols)] for x in range(self.rows)
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
            text_surf = self.small_font.render(line, True, self.color)
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
        self.cost: Optional[int] = None
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
        self.paper_surface_text_box = (
            self.engine.get_current_state().scale_paper_texture(self.text_box)
        )
        # Determine cost and type based on selection
        try:
            self.cost = constant.PRAYER_COSTS[self.selected]["prayer"]
            self.type = "ritual"
        except KeyError:
            self.cost = constant.PIECE_COSTS[self.selected]
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
            count = sum(
                1
                for cost in constant.PIECE_COSTS[self.selected]
                if constant.PIECE_COSTS[self.selected][cost] != 0
            )
            full_length = (
                self.resources["wood"].get_width() * count
                + (self.x_buffer_between_costs // 2) * count
            )
            self.cost_display_x = (
                self.window_width // 2
                - full_length // 2
                + self.board_x // 2
                + self.board_surface.get_width() // 2
            )
            self.title_text_display_x = (
                self.window_width // 2
                - self.title_text_width // 2
                + self.board_x // 2
                + self.board_surface.get_width() // 2
            )
            self.menu_logo_display_x = (
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

    def draw(self) -> None:
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
        for line_surface in self.justify_text(
            self.small_font, " ".join(self.description_text), max_width, self.color
        ):
            x_position: int = (max_width - line_surface.get_width()) // 2
            self.text_box.blit(line_surface, (x_position, y_buffer))
            y_buffer += self.description_text_height

        # Blit the text box to the screen
        self.win.blit(self.text_box, (self.text_box_x, self.description_text_y))

    def __repr__(self):
        return self.selected

    def close(self):
        self.engine.board = self.board_copy

    def set_up_demonstration_board(self):
        color = self.engine.turn
        if not color:
            color = "w"
        # resource_tiles = [f"tree_tile_{i}" for i in range(1, 9)] + [
        #     "gold_tile_1",
        #     "quarry_1",
        # ]
        # contextual_options = {
        #     "pray"    : ["monolith, prayer_stone"],
        #     "mine"    : resource_tiles,
        #     "king"    : list(),
        #     "queen"   : list(),
        #     "trade"   : list(),
        #     "persuade": ["enemy"],
        #     "steal"   : ["enemy"],
        #     "build"   : list(),
        #     "ritual"  : list(),
        # }
        row, col = 3, 3
        self.board[row][col].set_occupying(
            self.engine.PIECES[self.selected](row, col, color)
        )
        self.board[row][col].get_occupying().update_squares(self.engine)
        self.board[row][col].get_occupying().display_moves = True

    def justify_text(self, font, text, max_width, color):
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

    def draw_piece_cost(self):
        cost_x = self.cost_display_x
        for resource in self.cost:
            if self.cost[resource] != 0:

                try:
                    if (
                        getattr(self.player, constant.RESOURCE_KEY[resource])
                        >= self.cost[resource]
                    ):
                        color = self.color
                    else:
                        color = constant.RED
                except AttributeError:
                    color = self.color
                text_surf = self.small_font.render(
                    " " + str(self.cost[resource]), True, color
                )
                resource_position = (cost_x, self.cost_display_y)

                self.win.blit(
                    self.resources[constant.RESOURCE_KEY[resource]], resource_position
                )

                cost_text_position = (
                    cost_x + self.resources["wood"].get_width(),
                    self.cost_display_y - self.resources["wood"].get_height() // 3,
                )

                self.win.blit(text_surf, cost_text_position)
                cost_x += self.x_buffer_between_costs

    def draw_ritual_cost(self):
        bar_end_edge = self.cost_display_x
        self.win.blit(
            self.prayer_bar, (bar_end_edge - self.bar_width, self.cost_display_y)
        )
        for z in range(self.cost):
            new_edge = bar_end_edge + self.bar_end_width * z
            self.win.blit(self.prayer_bar_end, (new_edge, self.cost_display_y))

    def draw_board(self):
        # Draw the board squares and tiles
        for r in range(self.rows):
            for c in range(self.cols):
                # Calculate the color for the current square
                color = self.colors[(r + c) % 2]

                # Determine the rectangle size for the current square
                rect_size = (constant.SQ_SIZE, constant.SQ_SIZE)

                # Calculate position for the square, with the offset
                x = c * constant.SQ_SIZE
                y = r * constant.SQ_SIZE

                # Draw the square
                pygame.draw.rect(
                    self.board_surface,
                    color,
                    pygame.Rect(x, y, rect_size[0], rect_size[1]),
                )

                # Draw the tile using blend mode (avoid re-evaluating color calculation)
                tile_color = self.color_key[(r + c) % 2]
                self.board_surface.blit(
                    constant.BOARD_TILES[tile_color][self.board[r][c].index],
                    (x, y),
                    special_flags=pygame.BLEND_RGBA_MULT,
                )
        # Draw the board pieces
        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c].draw_highlights(self.board_surface)

        # Draw the board pieces
        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c].draw(self.board_surface)

    def full_length_of_prayer_bar(self, cost):
        return self.bar_end_width * cost + self.bar_width

    def mouse_move(self):
        pass

    def right_click(self):
        pass

    def left_click(self):
        pass


class Cost(Encyclopedia):
    def __init__(self, win, engine, spawn_list):
        super().__init__(win, engine)

        self.board_copy = None
        self.spawn_list = spawn_list
        self.win = win
        self.engine = engine
        self.highlight_list = []
        self.column_list = []

        # Determine positions
        self.x_buffer_between_columns = constant.SQ_SIZE // 3

        self.column_width = round(constant.SQ_SIZE * 1.5)

        self.y_buffer_between_costs = constant.SQ_SIZE // 2

        self.x_buffer_between_costs = self.x_buffer_between_columns // 3

        resource_height = self.resources[constant.RESOURCE_KEY["stone"]].get_height()

        self.column_height = (self.y_buffer_between_costs * 3) + (resource_height * 3)

        self.text_display_x = self.window_width // 2 - self.title_text_width // 2

        self.text_display_y = (
            round(self.window_height * 1 / 6) - self.title_text_height // 2
        )

        self.width_of_of_all_columns_and_buffers = (
            self.column_width + self.x_buffer_between_columns
        ) * len(self.spawn_list)

        self.column_display_y = round(self.window_height * 1 / 2)

        for _ in self.spawn_list:
            self.highlight_list.append(False)
            column = pygame.Surface(
                [self.column_width, self.column_height], pygame.SRCALPHA, 32
            )
            column = column.convert_alpha()
            self.column_list.append(column)
        self.highlight = pygame.Surface((self.column_width, self.column_height))
        self.highlight.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.highlight.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

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
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                # Remove highlight and reset cursor to the default arrow
                self.highlight_list[index] = False
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            # Move the starting position for the next column
            column_display_x += self.column_width + self.x_buffer_between_columns

    def left_click(self):
        selected = self.piece_selected()
        if selected is not None:
            menu = PieceDescription(self.win, self.engine, selected)
            self.engine.menus.append(menu)
            return True

    def draw(self):
        self.win.fill(constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.win)

        self.win.blit(self.text_surf, (self.text_display_x, self.text_display_y))
        if self.menu_logo:
            self.win.blit(
                self.menu_logo, (self.menu_logo_display_x, self.menu_logo_display_y)
            )

        column_display_x = (
            self.window_width // 2 - self.width_of_of_all_columns_and_buffers // 2
        )
        for column in self.column_list:
            index = self.column_list.index(column)
            if self.highlight_list[index]:
                self.win.blit(self.highlight, (column_display_x, self.column_display_y))

            # Boiler Plate
            piece = self.spawn_list[index]
            cost = constant.PIECE_COSTS[piece]
            try:
                piece = self.engine.turn + "_" + piece
            except TypeError:
                piece = f"w_{piece}"

            # Graphics Math
            piece_display_x = (
                self.column_width // 2 - self.icons[piece].get_width() // 2
            )

            column.blit(self.icons[piece], (piece_display_x, 0))
            y_buffer = self.icons[piece].get_height()
            for resource in cost:
                resource_sprite = self.resources[constant.RESOURCE_KEY[resource]]
                if cost[resource] != 0:
                    try:
                        if (
                            getattr(self.player, constant.RESOURCE_KEY[resource])
                            >= cost[resource]
                        ):
                            color = self.color
                        else:
                            color = constant.RED
                    except AttributeError:
                        color = self.color
                    text_surface = self.small_font.render(
                        str(cost[resource]), True, color
                    )
                    resource_position = (
                        self.column_width // 4 - resource_sprite.get_width() // 2,
                        y_buffer + resource_sprite.get_height() // 8,
                    )
                    column.blit(resource_sprite, resource_position)
                    cost_text_position = (
                        self.column_width // (3 / 2),
                        y_buffer - text_surface.get_height() // 8,
                    )
                    column.blit(text_surface, cost_text_position)
                    y_buffer += self.y_buffer_between_costs

            self.win.blit(column, (column_display_x, self.column_display_y))
            column_display_x += self.column_width + self.x_buffer_between_columns

    def piece_selected(self):
        pos = pygame.mouse.get_pos()
        column_display_x = (
            self.window_width // 2 - self.width_of_of_all_columns_and_buffers // 2
        )
        for column in self.column_list:
            index = self.column_list.index(column)
            if pos[1] in range(
                self.column_display_y, self.column_display_y + self.column_height
            ):
                if pos[0] in range(
                    column_display_x, column_display_x + self.column_width
                ):
                    return self.spawn_list[index]
            column_display_x += self.column_width + self.x_buffer_between_columns


class Master(Cost):
    def __init__(self, win, engine, spawn_list):
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "costs"

    def left_click(self):
        piece_selected = self.piece_selected()
        if piece_selected is not None:
            menu = self.menu_key[piece_selected](self.win, self.engine)
            self.engine.menus.append(menu)
            return True


class BuilderCosts(Cost):
    def __init__(self, win, engine):
        spawn_list = constant.BUILDER_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "builder"


class CastleCosts(Cost):
    def __init__(self, win, engine):
        spawn_list = constant.CASTLE_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "castle"


class StableCosts(Cost):
    def __init__(self, win, engine):
        spawn_list = constant.STABLE_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "stable"


class CircusCosts(Cost):
    def __init__(self, win, engine):
        spawn_list = constant.CIRCUS_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "circus"


class MonkCosts(Cost):
    def __init__(self, win, engine):
        spawn_list = constant.MONK_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def left_click(self):
        piece_selected = self.piece_selected()
        if piece_selected is not None:
            menu = self.menu_key[piece_selected](self.win, self.engine)
            self.engine.menus.append(menu)
            return True

    def __repr__(self):
        return "monk"


class FortressCosts(Cost):
    def __init__(self, win, engine):
        spawn_list = constant.FORTRESS_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "fortress"


class BarracksCosts(Cost):
    def __init__(self, win, engine):
        spawn_list = constant.BARRACKS_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "barracks"


class RitualCosts(Cost):
    def __init__(self, win, engine, spawn_list):
        super().__init__(win, engine, spawn_list)
        self.rituals = constant.PRAYER_RITUALS
        self.ritual_width = self.rituals["w_swap"].get_width()
        self.ritual_height = self.rituals["w_swap"].get_height()

        self.column_width = self.ritual_width

        total_height_of_cost_column = (
            self.y_buffer_between_costs * 3 + self.x_buffer_between_columns
        )
        self.highlight_width = self.ritual_width
        self.highlight_dimensions = (self.highlight_width, total_height_of_cost_column)

        self.square = pygame.Surface(self.highlight_dimensions)
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.prayer_bar_end = constant.IMAGES["prayer_bar_end"]
        self.prayer_bar = constant.IMAGES["prayer_bar"]

        self.bar_end_width = self.prayer_bar_end.get_width()
        self.bar_width = self.prayer_bar.get_width()

        self.piece_display_x = (
            (self.win.get_width() // 2)
            - self.column_width // 2
            - (self.ritual_width // 2) * len(self.highlight_list)
        )
        self.piece_display_y = self.win.get_height() // 2

        self.bar_display_y = self.piece_display_y + self.y_buffer_between_costs * 3

    def full_length_of_prayer_bar(self, cost):
        return self.bar_end_width * cost + self.bar_width

    def draw(self):
        self.win.fill(constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.win)

        self.win.blit(self.text_surf, (self.text_display_x, self.text_display_y))
        if self.menu_logo:
            self.win.blit(
                self.menu_logo, (self.menu_logo_display_x, self.menu_logo_display_y)
            )
        piece_display_x = self.piece_display_x
        for i in range(len(self.spawn_list)):
            p = self.spawn_list[i]
            cost = constant.PRAYER_COSTS[p]
            try:
                ritual = self.engine.turn + "_" + p
            except TypeError:
                ritual = f"w_{p}"
            if self.highlight_list[i]:
                self.win.blit(self.square, (piece_display_x, self.piece_display_y))
            self.win.blit(self.rituals[ritual], (piece_display_x, self.piece_display_y))

            length_of_this_prayer_bar = self.full_length_of_prayer_bar(cost["prayer"])

            bar_end_edge = (
                piece_display_x
                + self.ritual_width // 2
                - length_of_this_prayer_bar // 2
            )

            self.win.blit(
                self.prayer_bar, (bar_end_edge - self.bar_width, self.bar_display_y)
            )

            for z in range(cost["prayer"]):
                new_edge = bar_end_edge + self.bar_end_width * (z)
                self.win.blit(self.prayer_bar_end, (new_edge, self.bar_display_y))

            piece_display_x += self.column_width + self.x_buffer_between_columns


class PrayerStoneCosts(RitualCosts):
    def __init__(self, win, engine):
        spawn_list = constant.PRAYER_STONE_RITUALS
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "prayer_stone"


class MonolithCosts(RitualCosts):
    def __init__(self, win, engine):
        spawn_list = constant.MONOLITH_RITUALS
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "monolith"
