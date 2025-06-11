import typing
from resource import DepletedQuarry
from typing import Optional, Tuple

if typing.TYPE_CHECKING:
    from engine import Engine

import pygame
import constant


class Unit:
    """
    Represents a unit in the game with various attributes and methods for drawing and highlighting.
    """

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Unit object.

        :param row: The row position of the unit.
        :param col: The column position of the unit.
        :param color: The color of the unit.
        """
        # Initialize position and color
        self.row: int = row
        self.col: int = col
        self.color: str = color
        self.unit_kind: Optional[str] = None

        # Initialize other attributes
        self.check: Optional[bool] = None
        self.offset: tuple[int, int] = self.get_sprite_offset()
        self.dragging: bool = False

        # This piece has not moved yet
        self.first_move: bool = True
        self.rect: pygame.Rect = pygame.Rect(
            col * constant.SQ_SIZE,
            row * constant.SQ_SIZE,
            constant.SQ_SIZE,
            constant.SQ_SIZE,
        )

        # Initialize sprites
        self.sprites: dict = (
            constant.W_PIECES
            | constant.W_BUILDINGS
            | constant.B_PIECES
            | constant.B_BUILDINGS
        )

        # Initialize state flags
        self.purchasing: bool = False
        self.performing_ritual: bool = False
        self.mining: bool = False
        self.selected: bool = False
        self.pre_selected: bool = False
        self.unused_piece_highlight: bool = False
        self.praying: bool = False
        self.casting: bool = False
        self.stealing: bool = False
        self.persuading: bool = False
        self.display_moves: bool = False

        # Initialize other attributes
        self.can_be_persuaded: bool = True
        self.intercepted: bool = False
        self.is_rogue: bool = False
        self.is_general: bool = False
        self.is_wall: bool = False
        self.is_cavalry: bool = False

        self.additional_actions: int = 0
        self.actions_remaining: int = 0
        self.population_value: int = constant.PIECE_POPULATION[str(self)]
        self.additional_piece_limit: int = constant.ADDITIONAL_PIECE_LIMIT[str(self)]

        # Initialize square lists
        self.praying_squares_list: list[Tuple[int, int]] = []
        self.spawn_squares_list: list[Tuple[int, int]] = []
        self.move_squares_list: list[Tuple[int, int]] = []
        self.mining_squares_list: list[Tuple[int, int]] = []
        self.interceptor_squares_list: list[Tuple[int, int]] = []
        self.stealing_squares_list: list[Tuple[int, int]] = []
        self.ritual_squares_list: list[Tuple[int, int]] = []
        self.capture_squares_list: list[Tuple[int, int]] = []
        self.persuader_squares_list: list[Tuple[int, int]] = []
        self.contextual_options: list[str] = []

        # Initialize drawing attributes
        self.square: pygame.Surface = pygame.Surface(
            (constant.SQ_SIZE, constant.SQ_SIZE), pygame.SRCALPHA
        )
        self.self_selected_square_color: tuple = constant.SELF_SQUARE_HIGHLIGHT_COLOR
        self.unused_square_color: tuple = constant.UNUSED_PIECE_HIGHLIGHT_COLOR
        self.move_square_color: tuple = constant.MOVE_SQUARE_HIGHLIGHT_COLOR
        self.check_color: tuple = constant.CHECK_SQUARE_HIGHLIGHT_COLOR
        self.is_effected_by_jester: bool = True
        self.square_list: dict[str, list] = {
            "spawn": self.spawn_squares_list,
            "stealing": self.stealing_squares_list,
            "praying": self.praying_squares_list,
            "mining": self.mining_squares_list,
            "move": self.move_squares_list,
            "ritual": self.ritual_squares_list,
            "capture": self.capture_squares_list,
            "persuader": self.persuader_squares_list,
            "interceptor": self.interceptor_squares_list,
        }
        self.flag_to_action = [
            ("purchasing", ["spawn"]),
            ("stealing", ["stealing"]),
            ("praying", ["praying"]),
            ("mining", ["mining"]),
            ("selected", ["move", "capture"]),
            ("pre_selected", []),
            ("performing_ritual", ["ritual"]),
            ("persuading", ["persuader"]),
            ("display_moves", ["move", "capture"]),
        ]

    def draw_highlights(self, win: pygame.Surface):
        """
        Draws the highlights on the game window based on the unit's state.

        :param win: The game window surface.
        """
        # Disable unused piece highlight if no actions remain
        if self.actions_remaining == 0:
            self.unused_piece_highlight = False

        # Highlight the unused piece if applicable
        if self.unused_piece_highlight:
            self.highlight_self_square_unused(win)

        # Highlight this piece because it is in check
        if self.check:
            self.highlight_self_square_check(win)

        # Highlight the casting square if applicable
        if self.casting:
            self.highlight_self_square(win)

        # Highlight squares based on active flags
        active_flags = [
            actions
            for flag_name, actions in self.flag_to_action
            if getattr(self, flag_name)
        ]

        # If there are any active flags, highlight the unit's square and draw highlights for each action
        if active_flags:
            self.highlight_self_square(win)
            for actions in active_flags:
                for action in actions:
                    self.draw_highlight(win, action)

    def draw(self, win: pygame.Surface):
        """
        Draws the unit on the game window.

        :param win: The game window surface.
        """
        # Check if the piece is not currently being dragged
        if not self.dragging:
            # Get the appropriate sprite based on the piece's color and type
            sprite = self.sprites[self.color + "_" + str(self)]
            if str(self) == "war_tower":
                if self.armed:
                    sprite = self.sprites[
                        f"{self.color}_war_tower_{self.explosion_timer}"
                    ]

            # Calculate the x position based on the column and offset
            x = (self.col * constant.SQ_SIZE) + self.offset[0]

            # Calculate the y position based on the row and offset
            y = (self.row * constant.SQ_SIZE) + self.offset[1]

            # Draw the piece sprite at the calculated position on the window
            win.blit(sprite, (x, y))

    def draw_self_highlight(self, win: pygame.Surface, color: tuple):
        """
        Draws a highlight on the unit's square.

        :param win: The game window surface.
        :param color: The color of the highlight.
        """
        # Fill the square with the specified color
        self.square_fill(color)
        win.blit(
            self.square, (self.col * constant.SQ_SIZE, self.row * constant.SQ_SIZE)
        )

    def draw_squares_in_list(
        self, win: pygame.Surface, square_list: list[Tuple[int, int]], color: tuple
    ):
        """
        Draws squares from a list on the game window.

        :param win: The game window surface.
        :param square_list: List of squares to draw.
        :param color: The color to fill the squares.
        """
        # Fill the square with the specified color
        self.square_fill(color)
        # Draw each square in the list
        for square in square_list:
            win.blit(
                self.square,
                (square[1] * constant.SQ_SIZE, square[0] * constant.SQ_SIZE),
            )

    def draw_highlight(self, win: pygame.Surface, square_type: str):
        """
        Draws highlights on the game window based on the square type.

        :param win: The game window surface.
        :param square_type: The type of squares to highlight.
        """
        # Check if the square type is in the highlight list
        if square_type in self.square_list:
            # Draw the squares of the specified type
            self.draw_squares_in_list(
                win,
                getattr(self, f"{square_type}_squares_list"),
                self.move_square_color,
            )

    def highlight_self_square_check(self, win: pygame.Surface):
        """
        Highlights the unit's square if it is in check.

        :param win: The game window surface.
        """
        # Draw the highlight for the check square
        self.draw_self_highlight(win, self.check_color)

    def square_fill(self, color: tuple):
        """
        Fills the unit's square with the specified color.

        :param color: The color to fill the square.
        """
        # Fill the square with the specified color
        self.square.fill(color)

    def highlight_self_square_unused(self, win: pygame.Surface):
        """
        Highlights the unit's square if it is unused.

        :param win: The game window surface.
        """
        # Draw the sparkle image on the unit's square
        win.blit(
            constant.IMAGES["sparkle"],
            (self.col * constant.SQ_SIZE, self.row * constant.SQ_SIZE),
        )

    def highlight_self_square(self, win: pygame.Surface):
        """
        Highlights the unit's square.

        :param win: The game window surface.
        """
        # Draw the highlight for the selected square
        self.draw_self_highlight(win, self.self_selected_square_color)

    def update_squares(self, engine: "Engine"):
        """
        Updates the squares lists based on the unit's state.

        :param engine: The game engine.
        """
        # Update each square list based on the unit's state
        for action, squares_list in self.square_list.items():
            try:
                # Attempt to get the method for the desired action. action_squares
                update_method = getattr(self, f"{action}_squares")

                # Update the squares list for the action using the attribute
                setattr(self, f"{action}_squares_list", update_method(engine))

            # Many pieces will not have a method for each action
            except AttributeError:
                continue

    def change_pos(self, row: int, col: int):
        """
        Changes the position of the unit.

        :param row: The new row position.
        :param col: The new column position.
        """
        # Update the row and column positions
        self.row = row
        self.col = col
        # Update the rectangle position
        self.rect.x = col * constant.SQ_SIZE
        self.rect.y = row * constant.SQ_SIZE

    def get_additional_piece_limit(self) -> int:
        """
        Gets the additional piece limit for the unit.

        :return: The additional piece limit.
        """
        # Return the additional piece limit
        return self.additional_piece_limit

    def get_additional_actions(self) -> int:
        """
        Gets the additional actions for the unit.

        :return: The additional actions.
        """
        # Return the additional actions
        return self.additional_actions

    def get_population_value(self) -> int:
        """
        Gets the population value for the unit.

        :return: The population value.
        """
        # Return the population value from the constant
        return constant.PIECE_POPULATION[str(self)]

    def get_sprite_offset(self) -> Tuple[int, int]:
        """
        Gets the sprite offset for the unit.

        :return: The sprite offset.
        """
        # Return the sprite offset from the constant
        return constant.PIECE_IMAGE_MODIFY[str(self)]["OFFSET"]

    def get_rect(self) -> pygame.Rect:
        """
        Gets the rectangle representing the unit's position and size.

        :return: The rectangle.
        """
        # Return the rectangle
        return self.rect

    def get_color(self) -> str:
        """
        Gets the color of the unit.

        :return: The color.
        """
        # Return the color
        return self.color

    def get_position(self) -> Tuple[int, int]:
        """
        Gets the position of the unit.

        :return: The row and column position.
        """
        # Return the row and column position
        return self.row, self.col

    def can_spawn(self, engine: "Engine") -> bool:
        """
        Checks if the unit can spawn.

        :param engine: The game engine.
        :return: True if the unit can spawn, False otherwise.
        """
        # Get the spawn list for the unit
        spawn_list = constant.SPAWN_LISTS[str(self)]
        legal_spawns = []

        # Check each spawn in the list
        for spawn in spawn_list:
            if engine.is_legal_spawn(spawn, spawner=self):
                legal_spawns.append(spawn)

        # Return True if there are legal spawns
        return bool(legal_spawns)

    def can_act(self) -> bool:
        """
        Checks if the unit can perform an action.

        :return: True if the unit can act, False otherwise.
        """
        # Return True if the unit has actions remaining
        return self.actions_remaining > 0

    def can_capture(self, r: int, c: int, engine: "Engine") -> bool:
        """
        Checks if the unit can capture a piece at the given position.

        :param r: The row position.
        :param c: The column position.
        :param engine: The game engine.
        :return: True if the unit can capture, False otherwise.
        """
        capture_piece = None
        # Check if the tile is within bounds
        if engine.tile_in_bounds(r, c):
            capture_piece = engine.board[r][c].get_occupying()

        # Check if the capture tile is a valid square
        valid_square = isinstance(capture_piece, Piece) or isinstance(
            capture_piece, Building
        )
        if not valid_square:
            return False

        # Check capture conditions based on unit type
        if self.is_rogue:
            return self.rogue_can_capture(r, c, engine, capture_piece)
        if self.is_cavalry:
            return self.cavalry_can_capture(r, c, engine, capture_piece)
        if self.is_general:
            return self.general_can_capture(r, c, engine, capture_piece)
        return self.default_can_capture(r, c, engine, capture_piece)

    def _can_capture(
        self,
        r: int,
        c: int,
        engine: "Engine",
        capture_piece: "Unit",
        check_rogue: bool = False,
    ) -> bool:
        """
        Checks if a unit can capture a piece at the given position.

        :param r: The row position.
        :param c: The column position.
        :param engine: The game engine.
        :param capture_piece: The piece to be captured.
        :param check_rogue: Whether to check for rogue-specific capture rules.
        :return: True if the unit can capture, False otherwise.
        """
        if check_rogue:
            if not engine.can_be_legally_occupied_by_rogue(r, c):
                return False
        else:
            if not engine.can_be_legally_occupied(r, c):
                return False

        if self.color != capture_piece.get_color():
            if not capture_piece.is_wall:
                if not engine.board[r][c].is_protected():
                    return True
                if not engine.board[r][c].is_protected_by_opposite_color(self.color):
                    return True
        return False

    def general_can_capture(
        self, r: int, c: int, engine: "Engine", capture_tile: "Unit"
    ) -> bool:
        return self._can_capture(r, c, engine, capture_tile, check_rogue=True)

    def cavalry_can_capture(
        self, r: int, c: int, engine: "Engine", capture_tile: "Unit"
    ) -> bool:
        return self._can_capture(r, c, engine, capture_tile)

    def rogue_can_capture(
        self, r: int, c: int, engine: "Engine", capture_tile: "Unit"
    ) -> bool:
        return self._can_capture(r, c, engine, capture_tile, check_rogue=True)

    def default_can_capture(
        self, r: int, c: int, engine: "Engine", capture_tile: "Unit"
    ) -> bool:
        return self._can_capture(r, c, engine, capture_tile)

    def right_click(self, engine: "Engine") -> True:
        """
        Handles the right-click action on the building.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Building(Unit):
    """
    Represents a building unit in the game with various attributes and methods.
    """

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Building object.

        :param row: The row position of the building.
        :param col: The column position of the building.
        :param color: The color of the building.
        """
        super().__init__(row, col, color)

        # Indicates if the building can be persuaded
        self.can_be_persuaded: bool = False

        # Indicates if the building is affected by the jester
        self.is_effected_by_jester: bool = False

        # Contextual options available for the building
        self.contextual_options: list[str] = ["build"]

        # Yield when the building is prayed
        self.yield_when_prayed: int = 0

        # Kind of the unit
        self.unit_kind: str = "building"

    def base_spawn_criteria(self, engine: "Engine", row: int, col: int) -> bool:
        """
        Determines if the building can spawn at the given position.

        :param engine: The game engine.
        :param row: The row position to check.
        :param col: The column position to check.
        :return: True if the building can spawn, False otherwise.
        """
        # Check if the tile is within bounds
        if engine.tile_in_bounds(row, col):
            # Check if the tile is not protected by the opposite color
            return not engine.board[row][col].is_protected_by_opposite_color(self.color)
        return False


class Piece(Unit):
    """
    Represents a piece unit in the game with various attributes and methods.
    """

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Piece object.

        :param row: The row position of the piece.
        :param col: The column position of the piece.
        :param color: The color of the piece.
        """
        super().__init__(row, col, color)
        self.unit_kind: str = "piece"

    def can_move(
        self, engine: "Engine", row: int, col: int, can_be_occupied_function
    ) -> bool:
        """
        Determines if the piece can move to the given position based on the provided criteria.

        :param engine: The game engine.
        :param row: The row position to check.
        :param col: The column position to check.
        :param can_be_occupied_function: Function to check if the tile can be occupied.
        :return: True if the piece can move, False otherwise.
        """
        # Check if the tile is within bounds
        if not engine.tile_in_bounds(row, col):
            return False

        # Check if the tile can be occupied using the provided function
        if not can_be_occupied_function(row, col):
            return False

        # Check if the tile is protected by the opposite color
        if engine.board[row][col].is_protected_by_opposite_color(self.color):
            return False

        return True

    def general_move_criteria(self, engine: "Engine", row: int, c: int) -> bool:
        """
        Determines if the piece can move to the given position based on general criteria.

        :param engine: The game engine.
        :param row: The row position to check.
        :param c: The column position to check.
        :return: True if the piece can move, False otherwise.
        """
        return self.can_move(engine, row, c, engine.can_be_occupied_by_gold_general)

    def rogue_move_criteria(self, engine: "Engine", row: int, col: int) -> bool:
        """
        Determines if the piece can move to the given position based on rogue criteria.

        :param engine: The game engine.
        :param row: The row position to check.
        :param col: The column position to check.
        :return: True if the piece can move, False otherwise.
        """
        return self.can_move(engine, row, col, engine.can_be_occupied_by_rogue)

    def base_move_criteria(self, engine: "Engine", row: int, col: int) -> bool:
        """
        Determines if the piece can move to the given position based on base criteria.

        :param engine: The game engine.
        :param row: The row position to check.
        :param col: The column position to check.
        :return: True if the piece can move, False otherwise.
        """
        return self.can_move(engine, row, col, engine.can_be_occupied)

    def right_click(self, engine: "Engine") -> True:
        """
        Handles the right-click action on the piece.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True

    def base_spawn_criteria(self, engine: "Engine", row: int, col: int) -> bool:
        """
        Determines if the builder can spawn at the given position based on base criteria.

        :param engine: The game engine.
        :param row: The row position to check.
        :param col: The column position to check.
        :return: True if the builder can spawn, False otherwise.
        """
        # Check if the tile is within bounds
        if engine.tile_in_bounds(row, col):
            return (
                not engine.has_occupying(row, col)
                and not engine.has_portal(row, col)
                and not engine.has_trap(row, col)
                and not engine.board[row][col].is_protected_by_opposite_color(
                    self.color
                )
            )
        return False


class King(Piece):
    """
    Represents a king piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the king piece.

        :return: The string "king".
        """
        return "king"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a King object.

        :param row: The row position of the king.
        :param col: The column position of the king.
        :param color: The color of the king.
        """
        super().__init__(row, col, color)

        # Indicates if the king is in check
        self.check: bool = False

        # Directions the king can move
        self.move_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Contextual options available for the king
        self.contextual_options: list[str] = ["king"]

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the king can capture.

        :param engine: The game engine.
        :return: A list of squares the king can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.move_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.can_capture(row, col, engine):
                squares.append((row, col))
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the king can move to.

        :param engine: The game engine.
        :return: A list of squares the king can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.move_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the king.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Queen(Piece):
    """
    Represents a queen piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the queen piece.

        :return: The string "queen".
        """
        return "queen"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Queen object.

        :param row: The row position of the queen.
        :param col: The column position of the queen.
        :param color: The color of the queen.
        """
        super().__init__(row, col, color)

        # Directions the queen can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the queen can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Contextual options available for the queen
        self.contextual_options: list[str] = ["queen"]

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the queen can capture.

        :param engine: The game engine.
        :return: A list of squares the queen can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance
                if not engine.tile_in_bounds(row, col):
                    break
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break
                if not self.base_move_criteria(engine, row, col):
                    break

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the queen can move to.

        :param engine: The game engine.
        :return: A list of squares the queen can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance
                if not engine.tile_in_bounds(row, col):
                    break
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the queen.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Duke(Piece):
    """
    Represents a duke piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the duke piece.

        :return: The string "duke".
        """
        return "duke"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Duke object.

        :param row: The row position of the duke.
        :param col: The column position of the duke.
        :param color: The color of the duke.
        """
        super().__init__(row, col, color)

        # Directions the duke can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the duke can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Contextual options available for the duke
        self.contextual_options: list[str] = ["pray"]

    def praying_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the duke can pray at.

        :param engine: The game engine.
        :return: A list of squares the duke can pray at.
        """
        moves: list[tuple[int, int]] = []

        # Check each direction for praying
        for direction in self.directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[0]
            if engine.has_pray_able_building(row, col):
                if engine.get_occupying(row, col).color is self.color:
                    moves.append((row, col))

        return moves

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the duke can capture.

        :param engine: The game engine.
        :return: A list of squares the duke can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance
                if not engine.tile_in_bounds(row, col):
                    break
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break
                if not self.base_move_criteria(engine, row, col):
                    break

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the duke can move to.

        :param engine: The game engine.
        :return: A list of squares the duke can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance
                if not engine.tile_in_bounds(row, col):
                    break
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))
        return squares

    def right_click(self, engine: "Engine") -> True:
        """
        Handles the right-click action on the duke.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class FireSpinner(Piece):
    """
    Represents a FireSpinner piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the FireSpinner piece.

        :return: The string "fire_spinner".
        """
        return "fire_spinner"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a FireSpinner object.

        :param row: The row position of the FireSpinner.
        :param col: The column position of the FireSpinner.
        :param color: The color of the FireSpinner.
        """
        super().__init__(row, col, color)

        # Directions the FireSpinner can move
        self.knight_directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_RIGHT_UP,
            constant.TWO_DOWN_RIGHT,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_UP_LEFT,
            constant.TWO_LEFT_UP,
            constant.TWO_DOWN_LEFT,
            constant.TWO_LEFT_DOWN,
        )

        # Depth of movement for the FireSpinner
        self.depth: int = 3

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the FireSpinner can move to.

        :param engine: The game engine.
        :return: A list of squares the FireSpinner can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.knight_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))
                for i in range(self.depth):
                    new_row: int = row + direction[0]
                    new_col: int = col + direction[1]
                    if self.base_move_criteria(engine, new_row, new_col):
                        if (new_row, new_col) not in squares:
                            squares.append((new_row, new_col))
                    else:
                        break

        return squares

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the FireSpinner can capture.

        :param engine: The game engine.
        :return: A list of squares the FireSpinner can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.knight_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.can_capture(row, col, engine):
                squares.append((row, col))
            elif self.base_move_criteria(engine, row, col):
                for i in range(self.depth):
                    new_row: int = row + direction[0]
                    new_col: int = col + direction[1]
                    if self.can_capture(new_row, new_col, engine):
                        if (new_row, new_col) not in squares:
                            squares.append((new_row, new_col))
                        break
                    elif not self.base_move_criteria(engine, new_row, new_col):
                        break

        return squares


class Lion(Piece):
    """
    Represents a Lion piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the Lion piece.

        :return: The string "lion".
        """
        return "lion"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Lion object.

        :param row: The row position of the Lion.
        :param col: The column position of the Lion.
        :param color: The color of the Lion.
        """
        super().__init__(row, col, color)

        # Directions the Lion can move
        self.directions: tuple = (
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
        )

        # Knight-like directions the Lion can move
        self.knight_directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_RIGHT_UP,
            constant.TWO_DOWN_RIGHT,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_UP_LEFT,
            constant.TWO_LEFT_UP,
            constant.TWO_DOWN_LEFT,
            constant.TWO_LEFT_DOWN,
        )

        # Maximum distance the Lion can move
        self.distance: int = constant.BOARD_WIDTH_SQ

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Lion can capture.

        :param engine: The game engine.
        :return: A list of squares the Lion can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each knight direction for capture
        for direction in self.knight_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        # Check each straight direction for capture
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance
                if not engine.tile_in_bounds(row, col):
                    break
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break
                if not self.base_move_criteria(engine, row, col):
                    break

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Lion can move to.

        :param engine: The game engine.
        :return: A list of squares the Lion can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each knight direction for movement
        for direction in self.knight_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))

        # Check each straight direction for movement
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance
                if not engine.tile_in_bounds(row, col):
                    break
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        return squares


class Rook(Piece):
    """
    Represents a rook piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the rook piece.

        :return: The string "rook".
        """
        return "rook"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Rook object.

        :param row: The row position of the rook.
        :param col: The column position of the rook.
        :param color: The color of the rook.
        """
        super().__init__(row, col, color)

        # Directions the rook can move
        self.directions: tuple = (
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
        )

        # Directions the rook can pray
        self.praying_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the rook can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Contextual options available for the rook
        self.contextual_options: list[str] = ["pray"]

    def praying_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rook can pray at.

        :param engine: The game engine.
        :return: A list of squares the rook can pray at.
        """
        moves: list[tuple[int, int]] = []

        # Check each direction for praying
        for direction in range(len(self.praying_directions)):
            direction_tuple: tuple[int, int] = self.praying_directions[direction]
            row: int = self.row - direction_tuple[0]
            col: int = self.col - direction_tuple[1]
            if engine.has_pray_able_building(row, col):
                if engine.get_occupying(row, col).color == self.color:
                    moves.append((row, col))

        return moves

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rook can capture.

        :param engine: The game engine.
        :return: A list of squares the rook can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance
                if not engine.tile_in_bounds(row, col):
                    break
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break
                if not self.base_move_criteria(engine, row, col):
                    break

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rook can move to.

        :param engine: The game engine.
        :return: A list of squares the rook can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance
                if not engine.tile_in_bounds(row, col):
                    break
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the rook.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class WarTower(Piece):
    """
    Represents a war tower piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the war tower piece.

        :return: The string "war_tower".
        """
        return "war_tower"

    def arm(self):
        """
        Arms the war tower, when true the timer will tick down each time a turn ends.
        """
        self.armed = True

    def tick_timer(self):
        """
        Ticks up the explosion timer if the war tower is armed.
        """
        if self.armed:
            if self.explosion_timer < 3:
                self.explosion_timer += 1

    def un_tick_timer(self):
        """
        Ticks down the explosion timer if the war tower is armed.
        """
        if self.armed:
            self.explosion_timer -= 1

    def disarm(self):
        """
        Dis-arms the war tower, when false the timer will not tick down.
        """
        self.armed = False

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a war tower object.

        :param row: The row position of the rook.
        :param col: The column position of the rook.
        :param color: The color of the rook.
        """
        # Bool to track if the timer should tick each turn
        self.armed = False

        super().__init__(row, col, color)

        # Indicates how many turns left until the war tower detonates
        self.explosion_timer: int = 0

        # Distance out that will be destroyed by explosion
        self.radius: int = 1

        # Directions the war tower can move
        self.directions: tuple = (
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
        )

        # Maximum distance the war tower can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Contextual options available for the war tower
        self.contextual_options: list[str] = ["arm"]

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the war tower can move to.

        :param engine: The game engine.
        :return: A list of squares the war tower can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance
                if not engine.tile_in_bounds(row, col):
                    break
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the war tower.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Acrobat(Piece):
    """
    Represents an Acrobat piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the Acrobat piece.

        :return: The string "acrobat".
        """
        return "acrobat"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes an Acrobat object.

        :param row: The row position of the Acrobat.
        :param col: The column position of the Acrobat.
        :param color: The color of the Acrobat.
        """
        super().__init__(row, col, color)

        # Directions the Acrobat can move
        self.directions: tuple = (
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
            constant.UP_RIGHT,
        )

        # Maximum distance the Acrobat can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # The square the Acrobat has leaped over
        self.leaped_square: Optional[tuple[int, int]] = None

    def move_criteria(self, engine: "Engine", row: int, col: int) -> bool:
        """
        Determines if the Acrobat can move to the given position based on specific criteria.

        :param engine: The game engine.
        :param row: The row position to check.
        :param col: The column position to check.
        :return: True if the Acrobat can move, False otherwise.
        """
        # Check if the tile can be legally occupied
        if engine.can_be_legally_occupied(row, col):
            # Check if the tile is protected by an opposite color piece
            try:
                if engine.board[row][col].is_protected_by_opposite_color(self.color):
                    return False
                return True
            except IndexError:
                return False
        return False

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Acrobat can capture.

        :param engine: The game engine.
        :return: A list of squares the Acrobat can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.directions:
            # Reset the leaped_square to None for each new direction
            self.leaped_square = None

            # Iterate over the possible distances in the current direction
            for distance in range(1, self.distance):
                # Calculate the new row position based on the current direction and distance
                row: int = self.row + direction[0] * distance

                # Calculate the new column position based on the current direction and distance
                col: int = self.col + direction[1] * distance

                # If no square has been leaped over yet
                if not self.leaped_square:
                    # Check if the move criteria are not met for the current position
                    if not self.move_criteria(engine, row, col):
                        # Break out of the loop if the move criteria are not met
                        break

                    # Check if there is a piece occupying the current position
                    if engine.get_occupying(row, col):
                        # If the piece can be captured, add the position to the capture squares list
                        if self.can_capture(row, col, engine):
                            squares.append((row, col))

                        # Set the leaped_square to the current position
                        self.leaped_square = (row, col)
                else:
                    # If a square has been leaped over, check if the piece can be captured
                    if self.can_capture(row, col, engine):
                        # Add the position to the capture squares list
                        squares.append((row, col))

                        # Break out of the loop after capturing
                        break

                    # If the base move criteria are not met for the current position
                    elif not self.base_move_criteria(engine, row, col):
                        # Break out of the loop if the base move criteria are not met
                        break

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Acrobat can move to.

        :param engine: The game engine.
        :return: A list of squares the Acrobat can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            # Reset the leaped_square to None for each new direction
            self.leaped_square = None

            # Iterate over the possible distances in the current direction
            for distance in range(1, self.distance):
                # Calculate the new row position based on the current direction and distance
                row: int = self.row + direction[0] * distance

                # Calculate the new column position based on the current direction and distance
                col: int = self.col + direction[1] * distance

                # If no square has been leaped over yet
                if not self.leaped_square:
                    # Check if the move criteria are not met for the current position
                    if not self.move_criteria(engine, row, col):
                        # Break out of the loop if the move criteria are not met
                        break
                    else:
                        # Check if there is a piece occupying the current position
                        if engine.get_occupying(row, col):
                            # Set the leaped_square to the current position
                            self.leaped_square = (row, col)
                        else:
                            # Add the position to the move squares list
                            squares.append((row, col))
                else:
                    # If a square has been leaped over, check if the base move criteria are met
                    if not self.base_move_criteria(engine, row, col):
                        # Break out of the loop if the base move criteria are not met
                        break
                    else:
                        # Add the position to the move squares list
                        squares.append((row, col))

        return squares


class Bishop(Piece):
    """
    Represents a bishop piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the bishop piece.

        :return: The string "bishop".
        """
        return "bishop"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Bishop object.

        :param row: The row position of the bishop.
        :param col: The column position of the bishop.
        :param color: The color of the bishop.
        """
        super().__init__(row, col, color)

        # Directions the bishop can move
        self.directions: tuple = (
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
            constant.UP_RIGHT,
        )

        # Directions the bishop can pray
        self.praying_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the bishop can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Contextual options available for the bishop
        self.contextual_options: list[str] = ["pray"]

    def praying_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the bishop can pray at.

        :param engine: The game engine.
        :return: A list of squares the bishop can pray at.
        """
        moves: list[tuple[int, int]] = []

        # Check each direction for praying
        for direction in range(len(self.praying_directions)):
            direction_tuple: tuple[int, int] = self.praying_directions[direction]
            row: int = self.row - direction_tuple[0]
            col: int = self.col - direction_tuple[1]

            # Check if the building at the position can be prayed at
            if engine.has_pray_able_building(row, col):
                # Check if the occupying piece is of the same color
                if engine.get_occupying(row, col).color is self.color:
                    moves.append((row, col))

        return moves

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the bishop can capture.

        :param engine: The game engine.
        :return: A list of squares the bishop can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the bishop can capture at the position
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break

                # Check if the base move criteria are not met
                if not self.base_move_criteria(engine, row, col):
                    break

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the bishop can move to.

        :param engine: The game engine.
        :return: A list of squares the bishop can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the base move criteria are not met
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        return squares


class Knight(Piece):
    """
    Represents a knight piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the knight piece.

        :return: The string "knight".
        """
        return "knight"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Knight object.

        :param row: The row position of the knight.
        :param col: The column position of the knight.
        :param color: The color of the knight.
        """
        super().__init__(row, col, color)

        # Directions the knight can move
        self.directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_RIGHT_UP,
            constant.TWO_DOWN_RIGHT,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_UP_LEFT,
            constant.TWO_LEFT_UP,
            constant.TWO_DOWN_LEFT,
            constant.TWO_LEFT_DOWN,
        )

        # Maximum distance the knight can move
        self.distance: int = 1

        # Indicates if the knight is cavalry
        self.is_cavalry: bool = True

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the knight can capture.

        :param engine: The game engine.
        :return: A list of squares the knight can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the knight can capture at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the knight can move to.

        :param engine: The game engine.
        :return: A list of squares the knight can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the base move criteria are met
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))

        return squares


class Pawn(Piece):
    """
    Represents a pawn piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the pawn piece.

        :return: The string "pawn".
        """
        return "pawn"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Pawn object.

        :param row: The row position of the pawn.
        :param col: The column position of the pawn.
        :param color: The color of the pawn.
        """
        super().__init__(row, col, color)

        # Directions the pawn can mine
        self.mining_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Directions the pawn can move
        self.move_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
        )

        # Directions the pawn can capture
        self.capture_directions: tuple = (
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the pawn can move
        self.move_distance: int = 3

        # Maximum distance the pawn can capture
        self.capture_distance: int = 1

        # Contextual options available for the pawn
        self.contextual_options: list[str] = ["mine"]

    def mining_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the pawn can mine.

        :param engine: The game engine.
        :return: A list of squares the pawn can mine.
        """
        # Initialize an empty list to store the mining squares
        mining_squares = []

        # Iterate over each direction in the mining directions
        for direction in self.mining_directions:
            # Calculate the new row and column based on the current direction
            row, col = self.row - direction[0], self.col - direction[1]

            # Get the piece occupying the calculated position
            occupying_piece = engine.get_occupying(row, col)

            # Check if the tile has a mine-able resource
            if engine.has_mine_able_resource(row, col):
                # If there is an occupying piece, check its color
                if occupying_piece:
                    # If the occupying piece is of the same color, add the position to mining squares
                    if engine.get_occupying_color(row, col) is self.color:
                        mining_squares.append((row, col))
                else:
                    # If there is no occupying piece, add the position to mining squares
                    mining_squares.append((row, col))
            # Check if the tile can contain a quarry and is empty
            elif engine.can_contain_quarry(
                row, col
            ) and engine.has_no_units_or_resources(row, col):
                # Add the position to mining squares
                mining_squares.append((row, col))

        # Return the list of mining squares
        return mining_squares

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the pawn can capture.

        :param engine: The game engine.
        :return: A list of squares the pawn can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.capture_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the pawn can capture at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the pawn can move to.

        :param engine: The game engine.
        :return: A list of squares the pawn can move to.
        """
        squares: list[tuple[int, int]] = []

        # Adjust move distance based on whether it's the first move
        if not self.first_move:
            self.move_distance = 2
        else:
            self.move_distance = 3

        # Check each direction for movement
        for direction in self.move_directions:
            for distance in range(1, self.move_distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the base move criteria are not met
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        return squares

    def right_click(self, engine: "Engine"):
        """
        Handles the right-click action on the pawn.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class RogueRook(Piece):
    """
    Represents a rogue rook piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the rogue rook piece.

        :return: The string "rogue_rook".
        """
        return "rogue_rook"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a RogueRook object.

        :param row: The row position of the rogue rook.
        :param col: The column position of the rogue rook.
        :param color: The color of the rogue rook.
        """
        super().__init__(row, col, color)

        # Directions the rogue rook can move
        self.directions: tuple = (
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
        )

        # Maximum distance the rogue rook can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Directions the rogue rook can steal
        self.stealing_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Indicates if the rogue rook is a rogue
        self.is_rogue: bool = True

        # Contextual options available for the rogue rook
        self.contextual_options: list[str] = ["steal"]

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue rook can capture.

        :param engine: The game engine.
        :return: A list of squares the rogue rook can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the rogue rook can capture at the position
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break

                # Check if the rogue move criteria are not met
                if not self.rogue_move_criteria(engine, row, col):
                    break

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue rook can move to.

        :param engine: The game engine.
        :return: A list of squares the rogue rook can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the rogue move criteria are not met
                if not self.rogue_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        return squares

    def stealing_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue rook can steal from.

        :param engine: The game engine.
        :return: A list of squares the rogue rook can steal from.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for stealing
        for direction in self.stealing_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the rogue rook can capture at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        return squares

    def right_click(self, engine: "Engine"):
        """
        Handles the right-click action on the rogue rook.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class RogueBishop(Piece):
    """
    Represents a rogue bishop piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the rogue bishop piece.

        :return: The string "rogue_bishop".
        """
        return "rogue_bishop"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a RogueBishop object.

        :param row: The row position of the rogue bishop.
        :param col: The column position of the rogue bishop.
        :param color: The color of the rogue bishop.
        """
        super().__init__(row, col, color)

        # Directions the rogue bishop can steal
        self.stealing_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Directions the rogue bishop can move
        self.directions: tuple = (
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
            constant.UP_RIGHT,
        )

        # Maximum distance the rogue bishop can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Indicates if the rogue bishop is a rogue
        self.is_rogue: bool = True

        # Contextual options available for the rogue bishop
        self.contextual_options: list[str] = ["steal"]

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue bishop can capture.

        :param engine: The game engine.
        :return: A list of squares the rogue bishop can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the rogue bishop can capture at the position
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break

                # Check if the rogue move criteria are not met
                if not self.rogue_move_criteria(engine, row, col):
                    break

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue bishop can move to.

        :param engine: The game engine.
        :return: A list of squares the rogue bishop can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the rogue move criteria are not met
                if not self.rogue_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        return squares

    def stealing_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue bishop can steal from.

        :param engine: The game engine.
        :return: A list of squares the rogue bishop can steal from.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for stealing
        for direction in self.stealing_directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the rogue bishop can capture at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        return squares

    def right_click(self, engine: "Engine"):
        """
        Handles the right-click action on the rogue bishop.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class RogueKnight(Piece):
    """
    Represents a rogue knight piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the rogue knight piece.

        :return: The string "rogue_knight".
        """
        return "rogue_knight"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a RogueKnight object.

        :param row: The row position of the rogue knight.
        :param col: The column position of the rogue knight.
        :param color: The color of the rogue knight.
        """
        super().__init__(row, col, color)

        # Directions the rogue knight can move
        self.directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_RIGHT_UP,
            constant.TWO_DOWN_RIGHT,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_UP_LEFT,
            constant.TWO_LEFT_UP,
            constant.TWO_DOWN_LEFT,
            constant.TWO_LEFT_DOWN,
        )

        # Directions the rogue knight can steal
        self.stealing_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the rogue knight can move
        self.distance: int = 1

        # Indicates if the rogue knight is a rogue
        self.is_rogue: bool = True

        # Indicates if the rogue knight is cavalry
        self.is_cavalry: bool = True

        # Contextual options available for the rogue knight
        self.contextual_options: list[str] = ["steal"]

    def stealing_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue knight can steal from.

        :param engine: The game engine.
        :return: A list of squares the rogue knight can steal from.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for stealing
        for direction in self.stealing_directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the rogue knight can capture at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        return squares

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue knight can capture.

        :param engine: The game engine.
        :return: A list of squares the rogue knight can capture.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for capture
        for direction in self.directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the rogue knight can capture at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue knight can move to.

        :param engine: The game engine.
        :return: A list of squares the rogue knight can move to.
        """
        squares: list[tuple[int, int]] = []

        # Check each direction for movement
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the rogue move criteria are met
            if self.rogue_move_criteria(engine, row, col):
                squares.append((row, col))

        return squares

    def right_click(self, engine: "Engine"):
        """
        Handles the right-click action on the rogue knight.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class RoguePawn(Piece):
    """
    Represents a rogue pawn piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the rogue pawn piece.

        :return: The string "rogue_pawn".
        """
        return "rogue_pawn"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a RoguePawn object.

        :param row: The row position of the rogue pawn.
        :param col: The column position of the rogue pawn.
        :param color: The color of the rogue pawn.
        """
        super().__init__(row, col, color)

        # Directions the rogue pawn can mine
        self.mining_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Directions the rogue pawn can move
        self.move_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
        )

        # Directions the rogue pawn can capture
        self.capture_directions: tuple = (
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Directions the rogue pawn can steal
        self.stealing_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the rogue pawn can move
        self.move_distance: int = 3

        # Maximum distance the rogue pawn can capture
        self.capture_distance: int = 1

        # Contextual options available for the rogue pawn
        self.contextual_options: list[str] = ["mine", "steal"]

        # Indicates if the rogue pawn is a rogue
        self.is_rogue: bool = True

    def mining_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue pawn can mine.

        :param engine: The game engine.
        :return: A list of squares the rogue pawn can mine.
        """
        # Initialize an empty list to store the mining squares
        mining_squares = []

        # Iterate over each direction in the mining directions
        for direction in self.mining_directions:
            # Calculate the new row and column based on the current direction
            row, col = self.row - direction[0], self.col - direction[1]

            # Get the piece occupying the calculated position
            occupying_piece = engine.get_occupying(row, col)

            # Check if the tile has mine-able resources
            if engine.has_mine_able_resource(row, col):
                # If there is no occupying piece or the occupying piece is of the same color
                if (
                    not occupying_piece
                    or engine.get_occupying_color(row, col) is self.color
                ):
                    # Add the position to the mining squares list
                    mining_squares.append((row, col))
            # Check if the tile can contain a quarry and is empty
            elif engine.can_contain_quarry(
                row, col
            ) and engine.has_no_units_or_resources(row, col):
                # Add the position to the mining squares list
                mining_squares.append((row, col))

        # Return the list of mining squares
        return mining_squares

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue pawn can capture.

        :param engine: The game engine.
        :return: A list of squares the rogue pawn can capture.
        """
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.capture_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the rogue pawn can capture at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue pawn can move to.

        :param engine: The game engine.
        :return: A list of squares the rogue pawn can move to.
        """
        squares: list[tuple[int, int]] = []

        # Adjust move distance based on whether it's the first move
        if not self.first_move:
            self.move_distance = 2
        else:
            self.move_distance = 3

        # Iterate over each direction in the move directions
        for direction in self.move_directions:
            for distance in range(1, self.move_distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the rogue move criteria are met
                if not self.rogue_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        return squares

    def stealing_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the rogue pawn can steal from.

        :param engine: The game engine.
        :return: A list of squares the rogue pawn can steal from.
        """
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the stealing directions
        for direction in self.stealing_directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the rogue pawn can capture at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        return squares

    def right_click(self, engine: "Engine"):
        """
        Handles the right-click action on the rogue pawn.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Magician(Piece):
    """
    Represents a magician piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the magician piece.

        :return: The string "magician".
        """
        return "magician"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Magician object.

        :param row: The row position of the magician.
        :param col: The column position of the magician.
        :param color: The color of the magician.
        """
        super().__init__(row, col, color)

        # Directions the magician can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the magician can move
        self.distance: int = 1

        # Contextual options available for the magician
        self.contextual_options: list[str] = ["ritual"]

    def right_click(self, engine: "Engine"):
        """
        Handles the right-click action on the magician.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the magician can move to.

        :param engine: The game engine.
        :return: A list of squares the magician can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            # Calculate the new row and column based on the current direction
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the move criteria are met
            if self.base_move_criteria(engine, row, col):
                # Add the position to the move squares list
                squares.append((row, col))

        # Return the list of move squares
        return squares


class Monk(Piece):
    """
    Represents a monk piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the monk piece.

        :return: The string "monk".
        """
        return "monk"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Monk object.

        :param row: The row position of the monk.
        :param col: The column position of the monk.
        :param color: The color of the monk.
        """
        super().__init__(row, col, color)

        # Directions the monk can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the monk can move
        self.distance: int = 1

        # Contextual options available for the monk
        self.contextual_options: list[str] = ["build", "pray"]

    def right_click(self, engine: "Engine"):
        """
        Handles the right-click action on the monk.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the monk can move to.

        :param engine: The game engine.
        :return: A list of squares the monk can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            # Calculate the new row and column based on the current direction
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the move criteria are met
            if self.base_move_criteria(engine, row, col):
                # Add the position to the move squares list
                squares.append((row, col))

        # Return the list of move squares
        return squares

    def spawn_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the monk can spawn at.

        :param engine: The game engine.
        :return: A list of squares the monk can spawn at.
        """
        # Initialize an empty list to store the spawn squares
        spawn_squares: list[tuple[int, int]] = []

        # Check if the monk can spawn
        if not self.can_spawn(engine):
            return spawn_squares

        # Iterate over each direction in the spawn directions
        for direction in self.directions:
            # Calculate the new row and column based on the current direction
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the spawn criteria are met
            if self.base_spawn_criteria(engine, row, col):
                # Check if the tile has no resource or has a depleted quarry
                if not engine.has_resource(row, col) or engine.has_resource(
                    row, col, DepletedQuarry
                ):
                    # Add the position to the spawn squares list
                    spawn_squares.append((row, col))

        # Return the list of spawn squares
        return spawn_squares

    def praying_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the monk can pray at.

        :param engine: The game engine.
        :return: A list of squares the monk can pray at.
        """
        # Initialize an empty list to store the praying squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the praying directions
        for direction in self.directions:
            # Calculate the new row and column based on the current direction
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the tile has a pray-able building
            if engine.has_pray_able_building(row, col):
                # Check if the occupying piece is of the same color
                if engine.get_occupying(row, col).color is self.color:
                    # Add the position to the praying squares list
                    squares.append((row, col))

        # Return the list of praying squares
        return squares


class Ram(Piece):
    """
    Represents a ram piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the ram piece.

        :return: The string "ram".
        """
        return "ram"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Ram object.

        :param row: The row position of the ram.
        :param col: The column position of the ram.
        :param color: The color of the ram.
        """
        super().__init__(row, col, color)

        # Directions the ram can move
        self.directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_UP_LEFT,
            constant.TWO_RIGHT_UP,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_LEFT_UP,
            constant.TWO_LEFT_DOWN,
            constant.TWO_DOWN_LEFT,
            constant.TWO_DOWN_RIGHT,
        )

        # Indicates if the ram is cavalry
        self.is_cavalry: bool = True

        # Extra move directions for the ram
        self.extra_move_directions: dict = {
            constant.TWO_UP_RIGHT: constant.UP_RIGHT,
            constant.TWO_UP_LEFT: constant.UP_LEFT,
            constant.TWO_RIGHT_UP: constant.UP_RIGHT,
            constant.TWO_RIGHT_DOWN: constant.DOWN_RIGHT,
            constant.TWO_LEFT_UP: constant.UP_LEFT,
            constant.TWO_LEFT_DOWN: constant.DOWN_LEFT,
            constant.TWO_DOWN_LEFT: constant.DOWN_LEFT,
            constant.TWO_DOWN_RIGHT: constant.DOWN_RIGHT,
        }

        # Maximum distance the ram can move
        self.distance: int = constant.BOARD_WIDTH_SQ

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the ram can capture.

        :param engine: The game engine.
        :return: A list of squares the ram can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.directions:
            for distance in range(0, constant.BOARD_WIDTH_SQ):
                # Calculate the new row and column based on the current direction and distance
                extra_direction: tuple[int, int] = self.extra_move_directions[direction]
                row: int = self.row + direction[0] + extra_direction[0] * distance
                col: int = self.col + direction[1] + extra_direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the ram can capture at the calculated position
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break

                # Check if the base move criteria are not met
                if not self.base_move_criteria(engine, row, col):
                    break

        # Return the list of capture squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the ram can move to.

        :param engine: The game engine.
        :return: A list of squares the ram can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            for distance in range(0, constant.BOARD_WIDTH_SQ):
                # Calculate the new row and column based on the current direction and distance
                extra_direction: tuple[int, int] = self.extra_move_directions[direction]
                row: int = self.row + direction[0] + extra_direction[0] * distance
                col: int = self.col + direction[1] + extra_direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the base move criteria are not met
                if not self.base_move_criteria(engine, row, col):
                    break

                # Add the position to the move squares list
                squares.append((row, col))

        # Return the list of move squares
        return squares


class Elephant(Piece):
    """
    Represents an elephant piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the elephant piece.

        :return: The string "elephant".
        """
        return "elephant"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes an Elephant object.

        :param row: The row position of the elephant.
        :param col: The column position of the elephant.
        :param color: The color of the elephant.
        """
        super().__init__(row, col, color)

        # Directions the elephant can move
        self.directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_RIGHT_UP,
            constant.TWO_DOWN_RIGHT,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_UP_LEFT,
            constant.TWO_LEFT_UP,
            constant.TWO_DOWN_LEFT,
            constant.TWO_LEFT_DOWN,
        )

        # Extra move directions for the elephant
        self.directions_to_extra_moves: dict = {
            constant.TWO_UP_RIGHT: constant.UP,
            constant.TWO_RIGHT_UP: constant.RIGHT,
            constant.TWO_DOWN_RIGHT: constant.DOWN,
            constant.TWO_RIGHT_DOWN: constant.RIGHT,
            constant.TWO_UP_LEFT: constant.UP,
            constant.TWO_LEFT_UP: constant.LEFT,
            constant.TWO_DOWN_LEFT: constant.DOWN,
            constant.TWO_LEFT_DOWN: constant.LEFT,
        }

        # Maximum distance the elephant can move
        self.distance: int = 1

        # Indicates if the elephant is cavalry
        self.is_cavalry: bool = True

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the elephant can capture.

        :param engine: The game engine.
        :return: A list of squares the elephant can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.directions:
            # Calculate the new row and column based on the current direction
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the elephant can capture at the calculated position
            if self.can_capture(row, col, engine):
                squares.append((row, col))
            # Check if the base move criteria are met
            elif self.base_move_criteria(engine, row, col):
                # Calculate the extra move direction
                extra_direction: tuple[int, int] = self.directions_to_extra_moves[
                    direction
                ]
                row += extra_direction[0]
                col += extra_direction[1]

                # Check if the elephant can capture at the new position
                if self.can_capture(row, col, engine):
                    squares.append((row, col))

        # Return the list of capture squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the elephant can move to.

        :param engine: The game engine.
        :return: A list of squares the elephant can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            # Calculate the new row and column based on the current direction
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the base move criteria are met
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))

                # Calculate the extra move direction
                extra_direction: tuple[int, int] = self.directions_to_extra_moves[
                    direction
                ]
                row += extra_direction[0]
                col += extra_direction[1]

                # Check if the base move criteria are met for the new position
                if self.base_move_criteria(engine, row, col):
                    squares.append((row, col))

        # Return the list of move squares
        return squares


class Assassin(Piece):
    """
    Represents an assassin piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the assassin piece.

        :return: The string "assassin".
        """
        return "assassin"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes an Assassin object.

        :param row: The row position of the assassin.
        :param col: The column position of the assassin.
        :param color: The color of the assassin.
        """
        super().__init__(row, col, color)

        # Directions the assassin can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the assassin can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Contextual options available for the assassin
        self.contextual_options: list[str] = ["ritual"]

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the assassin can capture.

        :param engine: The game engine.
        :return: A list of squares the assassin can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.directions:
            # Calculate the new row and column based on the current direction
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the assassin can capture at the calculated position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        # Return the list of capture squares
        return squares


class Jester(Piece):
    """
    Represents a jester piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the jester piece.

        :return: The string "jester".
        """
        return "jester"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Jester object.

        :param row: The row position of the jester.
        :param col: The column position of the jester.
        :param color: The color of the jester.
        """
        super().__init__(row, col, color)

        # Directions the jester can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the jester can move
        self.distance: int = constant.BOARD_WIDTH_SQ

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the jester can move to.

        :param engine: The game engine.
        :return: A list of squares the jester can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            for dist in range(1, self.distance):
                # Calculate the new row and column based on the current direction and distance
                row: int = self.row + direction[0] * dist
                col: int = self.col + direction[1] * dist

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the jester can move to the calculated position
                if not self.base_move_criteria(engine, row, col):
                    break

                # Add the position to the move squares list
                squares.append((row, col))

        # Return the list of move squares
        return squares

    def interceptor_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the jester can intercept.

        :param engine: The game engine.
        :return: A list of squares the jester can intercept.
        """
        # Initialize an empty list to store the interceptor squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the interceptor directions
        for direction in self.directions:
            # Calculate the new row and column based on the current direction
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if there is an occupying piece at the calculated position
            if engine.has_occupying(row, col):
                # Add the position to the interceptor squares list
                squares.append((row, col))

        # Return the list of interceptor squares
        return squares


class Doe(Piece):
    """
    Represents a doe piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the doe piece.

        :return: The string "doe".
        """
        return "doe"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Doe object.

        :param row: The row position of the doe.
        :param col: The column position of the doe.
        :param color: The color of the doe.
        """
        super().__init__(row, col, color)

        # Directions the doe can move like a knight
        self.knight_directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_RIGHT_UP,
            constant.TWO_DOWN_RIGHT,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_UP_LEFT,
            constant.TWO_LEFT_UP,
            constant.TWO_DOWN_LEFT,
            constant.TWO_LEFT_DOWN,
        )

        # Directions the doe can move like a bishop
        self.bishop_directions: tuple = (
            constant.UP_LEFT,
            constant.UP_RIGHT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the doe can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Indicates if the doe is cavalry
        self.is_cavalry: bool = True

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the doe can capture.

        :param engine: The game engine.
        :return: A list of squares the doe can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each knight direction for capture
        for direction in self.knight_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        # Iterate over each bishop direction for capture
        for direction in self.bishop_directions:
            for i in range(1, self.distance):
                row: int = self.row + direction[0] * i
                col: int = self.col + direction[1] * i
                if not engine.tile_in_bounds(row, col):
                    break
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break
                if not self.base_move_criteria(engine, row, col):
                    break

        # Return the list of capture squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the doe can move to.

        :param engine: The game engine.
        :return: A list of squares the doe can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each knight direction for movement
        for direction in self.knight_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))

        # Iterate over each bishop direction for movement
        for direction in self.bishop_directions:
            for i in range(1, self.distance):
                row: int = self.row + direction[0] * i
                col: int = self.col + direction[1] * i
                if not engine.tile_in_bounds(row, col):
                    break
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        # Return the list of move squares
        return squares


class Pikeman(Piece):
    """
    Represents a pikeman piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the pikeman piece.

        :return: The string "pikeman".
        """
        return "pikeman"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Pikeman object.

        :param row: The row position of the pikeman.
        :param col: The column position of the pikeman.
        :param color: The color of the pikeman.
        """
        super().__init__(row, col, color)

        # Directions the pikeman can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the pikeman can move
        self.distance: int = 1

        # Indicates if the pikeman is cavalry
        self.is_cavalry: bool = True

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the pikeman can capture.

        :param engine: The game engine.
        :return: A list of squares the pikeman can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        # Return the list of capture squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the pikeman can move to.

        :param engine: The game engine.
        :return: A list of squares the pikeman can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))

        # Return the list of move squares
        return squares


class Builder(Piece):
    """
    Represents a builder piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the builder piece.

        :return: The string "builder".
        """
        return "builder"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Builder object.

        :param row: The row position of the builder.
        :param col: The column position of the builder.
        :param color: The color of the builder.
        """
        super().__init__(row, col, color)

        # Directions the builder can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Directions the builder can mine
        self.mining_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the builder can move
        self.distance: int = 1

        # Contextual options available for the builder
        self.contextual_options: list[str] = ["build", "mine"]

    def mining_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the builder can mine.

        :param engine: The game engine.
        :return: A list of squares the builder can mine.
        """
        # Initialize an empty list to store the mining squares
        mining_squares: list[tuple[int, int]] = []

        # Iterate over each direction in the mining directions
        for direction in self.mining_directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the tile has a mine-able resource
            if engine.has_mine_able_resource(row, col):
                if engine.get_occupying(row, col):
                    if engine.get_occupying_color(row, col) is not self.color:
                        pass
                    elif engine.get_occupying_color(row, col) is self.color:
                        mining_squares.append((row, col))
                elif not engine.has_occupying(row, col):
                    mining_squares.append((row, col))
            elif engine.can_contain_quarry(
                row, col
            ) and engine.has_no_units_or_resources(row, col):
                mining_squares.append((row, col))

        # Return the list of mining squares
        return mining_squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the builder can move to.

        :param engine: The game engine.
        :return: A list of squares the builder can move to.
        """
        # Initialize an empty list to store the move squares
        moves: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the move criteria are met
            if self.base_move_criteria(engine, row, col):
                moves.append((row, col))

        # Return the list of move squares
        return moves

    def spawn_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the builder can spawn at.

        :param engine: The game engine.
        :return: A list of squares the builder can spawn at.
        """
        # Initialize an empty list to store the spawn squares
        spawn_squares: list[tuple[int, int]] = []

        # Check if the builder can spawn
        if not self.can_spawn(engine):
            return spawn_squares

        # Iterate over each direction in the spawn directions
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the base spawn criteria are met
            if self.base_spawn_criteria(engine, row, col):
                if not engine.has_resource(row, col) or engine.has_resource(
                    row, col, DepletedQuarry
                ):
                    spawn_squares.append((row, col))

        # Return the list of spawn squares
        return spawn_squares

    def right_click(self, engine: "Engine"):
        """
        Handles the right-click action on the builder.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Unicorn(Piece):
    """
    Represents a unicorn piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the unicorn piece.

        :return: The string "unicorn".
        """
        return "unicorn"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Unicorn object.

        :param row: The row position of the unicorn.
        :param col: The column position of the unicorn.
        :param color: The color of the unicorn.
        """
        super().__init__(row, col, color)

        # Indicates if the unicorn is cavalry
        self.is_cavalry: bool = True

        # Directions the unicorn can move like a knight
        self.knight_directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_RIGHT_UP,
            constant.TWO_DOWN_RIGHT,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_UP_LEFT,
            constant.TWO_LEFT_UP,
            constant.TWO_DOWN_LEFT,
            constant.TWO_LEFT_DOWN,
        )

        # Directions the unicorn can move in cardinal directions
        self.cardinal_directions: tuple = (
            constant.THREE_RIGHT,
            constant.THREE_DOWN,
            constant.THREE_UP,
            constant.THREE_LEFT,
        )

        # Mapping of knight directions to extra moves
        self.knight_directions_to_extra_moves: dict = {
            constant.TWO_UP_RIGHT: constant.TWO_RIGHT_UP,
            constant.TWO_RIGHT_UP: constant.TWO_UP_RIGHT,
            constant.TWO_DOWN_RIGHT: constant.TWO_RIGHT_DOWN,
            constant.TWO_RIGHT_DOWN: constant.TWO_DOWN_RIGHT,
            constant.TWO_UP_LEFT: constant.TWO_LEFT_UP,
            constant.TWO_LEFT_UP: constant.TWO_UP_LEFT,
            constant.TWO_DOWN_LEFT: constant.TWO_LEFT_DOWN,
            constant.TWO_LEFT_DOWN: constant.TWO_DOWN_LEFT,
        }

        # Maximum distance the unicorn can move
        self.distance: int = 1

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the unicorn can capture.

        :param engine: The game engine.
        :return: A list of squares the unicorn can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each cardinal direction for capture
        for direction in self.cardinal_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        # Iterate over each knight direction for capture
        for direction in self.knight_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.can_capture(row, col, engine):
                squares.append((row, col))
            elif engine.can_be_occupied(row, col):
                extra_move_direction = self.knight_directions_to_extra_moves[direction]
                row += extra_move_direction[0]
                col += extra_move_direction[1]
                if self.can_capture(row, col, engine):
                    squares.append((row, col))

        # Return the list of capture squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the unicorn can move to.

        :param engine: The game engine.
        :return: A list of squares the unicorn can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each cardinal direction for movement
        for direction in self.cardinal_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))

        # Iterate over each knight direction for movement
        for direction in self.knight_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))
                extra_move_direction = self.knight_directions_to_extra_moves[direction]
                row += extra_move_direction[0]
                col += extra_move_direction[1]
                if self.base_move_criteria(engine, row, col):
                    if (row, col) not in squares:
                        squares.append((row, col))

        # Return the list of move squares
        return squares


class Champion(Piece):
    """
    Represents a champion piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the champion piece.

        :return: The string "champion".
        """
        return "champion"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Champion object.

        :param row: The row position of the champion.
        :param col: The column position of the champion.
        :param color: The color of the champion.
        """
        super().__init__(row, col, color)

        # Directions the champion can move
        self.directions: tuple = (
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Directions the champion can pray
        self.praying_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Extra move directions for the champion
        self.extra_move_directions: dict = {
            constant.UP_RIGHT: (constant.UP, constant.RIGHT),
            constant.UP_LEFT: (constant.UP, constant.LEFT),
            constant.DOWN_RIGHT: (constant.DOWN, constant.RIGHT),
            constant.DOWN_LEFT: (constant.DOWN, constant.LEFT),
        }

        # Contextual options available for the champion
        self.contextual_options: list[str] = ["pray"]

        # Maximum distance the champion can move
        self.distance: int = constant.BOARD_WIDTH_SQ

    def praying_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the champion can pray at.

        :param engine: The game engine.
        :return: A list of squares the champion can pray at.
        """
        # Initialize an empty list to store the praying squares
        moves: list[tuple[int, int]] = []

        # Iterate over each direction in the praying directions
        for direction in range(len(self.praying_directions)):
            direction_tuple: tuple[int, int] = self.praying_directions[direction]
            row: int = self.row - direction_tuple[0]
            col: int = self.col - direction_tuple[1]

            # Check if the tile has a pray-able building
            if engine.has_pray_able_building(row, col):
                if engine.get_occupying(row, col).color is self.color:
                    moves.append((row, col))

        # Return the list of praying squares
        return moves

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the champion can capture.

        :param engine: The game engine.
        :return: A list of squares the champion can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.directions:
            extra_directions: dict[Tuple[int, int]] = self.extra_move_directions[
                direction
            ]
            for extra_direction in extra_directions:
                for distance in range(0, self.distance):
                    row: int = self.row + direction[0] + extra_direction[0] * distance
                    col: int = self.col + direction[1] + extra_direction[1] * distance

                    # Check if the tile is within bounds
                    if not engine.tile_in_bounds(row, col):
                        break

                    # Check if the champion can capture the piece at the position
                    if self.can_capture(row, col, engine):
                        if (row, col) not in squares:
                            squares.append((row, col))
                            break

                    # Check if the base move criteria are met
                    if not self.base_move_criteria(engine, row, col):
                        break

        # Return the list of capture squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the champion can move to.

        :param engine: The game engine.
        :return: A list of squares the champion can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            extra_directions: dict[tuple[int, int]] = self.extra_move_directions[
                direction
            ]
            for extra_direction in extra_directions:
                for distance in range(0, self.distance):
                    row: int = self.row + direction[0] + extra_direction[0] * distance
                    col: int = self.col + direction[1] + extra_direction[1] * distance

                    # Check if the tile is within bounds
                    if not engine.tile_in_bounds(row, col):
                        break

                    # Check if the base move criteria are met
                    if not self.base_move_criteria(engine, row, col):
                        break
                    else:
                        if (row, col) not in squares:
                            squares.append((row, col))

        # Return the list of move squares
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the champion.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Oxen(Piece):
    """
    Represents an oxen piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the oxen piece.

        :return: The string "oxen".
        """
        return "oxen"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes an Oxen object.

        :param row: The row position of the oxen.
        :param col: The column position of the oxen.
        :param color: The color of the oxen.
        """
        super().__init__(row, col, color)

        # Directions the oxen can move
        self.directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_RIGHT_UP,
            constant.TWO_DOWN_RIGHT,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_UP_LEFT,
            constant.TWO_LEFT_UP,
            constant.TWO_DOWN_LEFT,
            constant.TWO_LEFT_DOWN,
        )

        # Indicates if the oxen is cavalry
        self.is_cavalry: bool = True

        # Extra move directions for the oxen
        self.extra_move_directions: dict = {
            constant.TWO_UP_RIGHT: constant.UP,
            constant.TWO_RIGHT_UP: constant.RIGHT,
            constant.TWO_DOWN_RIGHT: constant.DOWN,
            constant.TWO_RIGHT_DOWN: constant.RIGHT,
            constant.TWO_UP_LEFT: constant.UP,
            constant.TWO_LEFT_UP: constant.LEFT,
            constant.TWO_DOWN_LEFT: constant.DOWN,
            constant.TWO_LEFT_DOWN: constant.LEFT,
        }

        # Maximum distance the oxen can move
        self.distance: int = constant.BOARD_WIDTH_SQ

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the oxen can capture.

        :param engine: The game engine.
        :return: A list of squares the oxen can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.directions:
            extra_direction: tuple[int, int] = self.extra_move_directions[direction]
            for distance in range(0, self.distance):
                row: int = self.row + direction[0] + extra_direction[0] * distance
                col: int = self.col + direction[1] + extra_direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the oxen can capture the piece at the position
                if self.can_capture(row, col, engine):
                    if (row, col) not in squares:
                        squares.append((row, col))
                        break

                # Check if the base move criteria are met
                if not self.base_move_criteria(engine, row, col):
                    break

        # Return the list of capture squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the oxen can move to.

        :param engine: The game engine.
        :return: A list of squares the oxen can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            extra_direction: tuple[int, int] = self.extra_move_directions[direction]
            for distance in range(0, self.distance):
                row: int = self.row + direction[0] + extra_direction[0] * distance
                col: int = self.col + direction[1] + extra_direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the base move criteria are met
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    if (row, col) not in squares:
                        squares.append((row, col))

        # Return the list of move squares
        return squares


class Persuader(Piece):
    """
    Represents a persuader piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the persuader piece.

        :return: The string "persuader".
        """
        return "persuader"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Persuader object.

        :param row: The row position of the persuader.
        :param col: The column position of the persuader.
        :param color: The color of the persuader.
        """
        super().__init__(row, col, color)

        # Directions the persuader can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the persuader can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Contextual options available for the persuader
        self.contextual_options: list[str] = ["persuade"]

    def persuader_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the persuader can persuade.

        :param engine: The game engine.
        :return: A list of squares the persuader can persuade.
        """
        # Initialize an empty list to store the persuader squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the persuader directions
        for direction in self.directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the persuader can capture the piece at the position
            if self.can_capture(row, col, engine):
                if engine.get_occupying(row, col).can_be_persuaded:
                    squares.append((row, col))

        # Return the list of persuader squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the persuader can move to.

        :param engine: The game engine.
        :return: A list of squares the persuader can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the base move criteria are met
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        # Return the list of move squares
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the persuader.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class GoldGeneral(Piece):
    """
    Represents a gold general piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the gold general piece.

        :return: The string "gold_general".
        """
        return "gold_general"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a GoldGeneral object.

        :param row: The row position of the gold general.
        :param col: The column position of the gold general.
        :param color: The color of the gold general.
        """
        super().__init__(row, col, color)

        # Directions the gold general can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the gold general can move
        self.distance: int = constant.BOARD_WIDTH_SQ

        # Directions the gold general can pray
        self.praying_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Indicates if the gold general is a general
        self.is_general: bool = True

        # Indicates if the gold general can be persuaded
        self.can_be_persuaded: bool = False

    def praying_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the gold general can pray at.

        :param engine: The game engine.
        :return: A list of squares the gold general can pray at.
        """
        # Initialize an empty list to store the praying squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the praying directions
        for direction in self.praying_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the square has a pray-able building
            if engine.has_pray_able_building(row, col):
                if engine.get_occupying(row, col).color == self.color:
                    squares.append((row, col))

        # Return the list of praying squares
        return squares

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the gold general can capture.

        :param engine: The game engine.
        :return: A list of squares the gold general can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the gold general can capture the piece at the position
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
                    break

                # Check if the general move criteria are met
                if not self.general_move_criteria(engine, row, col):
                    break

        # Return the list of capture squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the gold general can move to.

        :param engine: The game engine.
        :return: A list of squares the gold general can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            for distance in range(1, self.distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the general move criteria are met
                if not self.general_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        # Return the list of move squares
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the gold general.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Trapper(Piece):
    """
    Represents a trapper piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the trapper piece.

        :return: The string "trapper".
        """
        return "trapper"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Trapper object.

        :param row: The row position of the trapper.
        :param col: The column position of the trapper.
        :param color: The color of the trapper.
        """
        super().__init__(row, col, color)

        # Directions the trapper can trap
        self.trapping_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Directions the trapper can move
        self.move_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
        )

        # Directions the trapper can capture
        self.capture_directions: tuple = (
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the trapper can move
        self.move_distance: int = 3

        # Maximum distance the trapper can capture
        self.capture_distance: int = 1

        # Indicates if the trapper is a rogue
        self.is_rogue: bool = True

        # Contextual options available for the trapper
        self.contextual_options: list[str] = ["build", "steal"]

        # Directions the trapper can steal
        self.stealing_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the trapper can capture.

        :param engine: The game engine.
        :return: A list of squares the trapper can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.capture_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the trapper can capture the piece at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        # Return the list of capture squares
        return squares

    def can_spawn(self, engine: "Engine") -> bool:
        """
        Determines if the trapper can spawn.

        :param engine: The game engine.
        :return: True if the trapper can spawn, False otherwise.
        """
        # Get the list of legal spawns for the trapper
        spawn_list: list = constant.SPAWN_LISTS[str(self)]
        legal_spawns: list = []

        # Iterate over each spawn in the spawn list
        for spawn in spawn_list:
            if engine.is_legal_spawn(spawn, spawner=self):
                legal_spawns.append(spawn)

        # Return True if there are legal spawns, False otherwise
        return bool(legal_spawns)

    def stealing_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the trapper can steal from.

        :param engine: The game engine.
        :return: A list of squares the trapper can steal from.
        """
        # Initialize an empty list to store the stealing squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the stealing directions
        for direction in self.stealing_directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the trapper can capture the piece at the position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        # Return the list of stealing squares
        return squares

    def base_spawn_criteria(self, engine: "Engine", row: int, col: int) -> bool:
        """
        Determines if the trapper can spawn at the given position based on base criteria.

        :param engine: The game engine.
        :param row: The row position to check.
        :param col: The column position to check.
        :return: True if the trapper can spawn, False otherwise.
        """
        # Check if the tile is within bounds
        if engine.tile_in_bounds(row, col):
            return not engine.has_trap(row, col) and not engine.board[row][
                col
            ].is_protected_by_opposite_color(self.color)
        return False

    def spawn_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the trapper can spawn at.

        :param engine: The game engine.
        :return: A list of squares the trapper can spawn at.
        """
        # Initialize an empty list to store the spawn squares
        squares: list[tuple[int, int]] = []

        # Check if the trapper can spawn
        if not self.can_spawn(engine):
            return squares

        # Iterate over each direction in the trapping directions
        for direction in self.trapping_directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the base spawn criteria are met
            if self.base_spawn_criteria(engine, row, col):
                if engine.can_be_occupied_by_rogue(row, col):
                    squares.append((row, col))

        # Return the list of spawn squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the trapper can move to.

        :param engine: The game engine.
        :return: A list of squares the trapper can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Set the move distance based on whether it is the first move
        self.move_distance = 2 if not self.first_move else 3

        # Iterate over each direction in the move directions
        for direction in self.move_directions:
            for distance in range(1, self.move_distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the rogue move criteria are met
                if not self.rogue_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        # Return the list of move squares
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the trapper.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Trader(Piece):
    """
    Represents a trader piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the trader piece.

        :return: The string "trader".
        """
        return "trader"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Trader object.

        :param row: The row position of the trader.
        :param col: The column position of the trader.
        :param color: The color of the trader.
        """
        super().__init__(row, col, color)

        # Directions the trader can move
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Contextual options available for the trader
        self.contextual_options: list[str] = ["trade"]

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the trader can move to.

        :param engine: The game engine.
        :return: A list of squares the trader can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the move directions
        for direction in self.directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the base move criteria are met
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))

        # Return the list of move squares
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the trader.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Stable(Building):
    """
    Represents a stable building in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the stable building.

        :return: The string "stable".
        """
        return "stable"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Stable object.

        :param row: The row position of the stable.
        :param col: The column position of the stable.
        :param color: The color of the stable.
        """
        super().__init__(row, col, color)

        # Directions the stable can spawn units
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the stable can spawn units
        self.distance: int = 1

        # Additional actions available for the stable
        self.additional_actions: list[str] = constant.STABLE_ADDITIONAL_ACTIONS

    def spawn_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the stable can spawn units at.

        :param engine: The game engine.
        :return: A list of squares the stable can spawn units at.
        """
        # Initialize an empty list to store the spawn squares
        spawn_squares: list[tuple[int, int]] = []

        # Check if the stable can spawn units
        if not self.can_spawn(engine):
            return spawn_squares

        # Iterate over each direction in the spawn directions
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the base spawn criteria are met
            if self.base_spawn_criteria(engine, row, col):
                if engine.can_be_occupied(row, col):
                    spawn_squares.append((row, col))

        # Return the list of spawn squares
        return spawn_squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the stable.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Barracks(Building):
    """
    Represents a barracks building in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the barracks building.

        :return: The string "barracks".
        """
        return "barracks"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Barracks object.

        :param row: The row position of the barracks.
        :param col: The column position of the barracks.
        :param color: The color of the barracks.
        """
        super().__init__(row, col, color)

        # Directions the barracks can spawn units
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the barracks can spawn units
        self.distance: int = 1

        # Additional actions available for the barracks
        self.additional_actions: list[str] = constant.BARRACKS_ADDITIONAL_ACTIONS

    def spawn_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the barracks can spawn units at.

        :param engine: The game engine.
        :return: A list of squares the barracks can spawn units at.
        """
        # Initialize an empty list to store the spawn squares
        spawn_squares: list[tuple[int, int]] = []

        # Check if the barracks can spawn units
        if not self.can_spawn(engine):
            return spawn_squares

        # Iterate over each direction in the spawn directions
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the base spawn criteria are met
            if self.base_spawn_criteria(engine, row, col):
                if engine.can_be_occupied(row, col):
                    spawn_squares.append((row, col))

        # Return the list of spawn squares
        return spawn_squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the barracks.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Castle(Building):
    """
    Represents a castle building in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the castle building.

        :return: The string "castle".
        """
        return "castle"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Castle object.

        :param row: The row position of the castle.
        :param col: The column position of the castle.
        :param color: The color of the castle.
        """
        super().__init__(row, col, color)

        # Directions the castle can spawn units
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the castle can spawn units
        self.distance: int = 1

        # Additional actions available for the castle
        self.additional_actions: list[str] = constant.CASTLE_ADDITIONAL_ACTIONS

    def spawn_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the castle can spawn units at.

        :param engine: The game engine.
        :return: A list of squares the castle can spawn units at.
        """
        # Initialize an empty list to store the spawn squares
        spawn_squares: list[tuple[int, int]] = []

        # Check if the castle can spawn units
        if not str(engine.get_current_state()) == "start spawn":
            if not self.can_spawn(engine):
                return spawn_squares

        # Iterate over each direction in the spawn directions
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the spawning unit is a rogue pawn or trapper
            if engine.spawning == "rogue_pawn" or engine.spawning == "trapper":
                if engine.can_be_occupied_by_rogue(row, col):
                    spawn_squares.append((row, col))
            # Check if the base spawn criteria are met
            elif self.base_spawn_criteria(engine, row, col):
                if engine.can_be_occupied(row, col):
                    spawn_squares.append((row, col))

        # Return the list of spawn squares
        return spawn_squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the castle.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Circus(Building):
    """
    Represents a circus building in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the circus building.

        :return: The string "circus".
        """
        return "circus"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Circus object.

        :param row: The row position of the circus.
        :param col: The column position of the circus.
        :param color: The color of the circus.
        """
        super().__init__(row, col, color)

        # Directions the circus can spawn units
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the circus can spawn units
        self.distance: int = 1

        # Additional actions available for the circus
        self.additional_actions: list[str] = constant.CIRCUS_ADDITIONAL_ACTIONS

    def spawn_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the circus can spawn units at.

        :param engine: The game engine.
        :return: A list of squares the circus can spawn units at.
        """
        # Initialize an empty list to store the spawn squares
        spawn_squares: list[tuple[int, int]] = []

        # Check if the circus can spawn units
        if not self.can_spawn(engine):
            return spawn_squares

        # Iterate over each direction in the spawn directions
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the base spawn criteria are met
            if self.base_spawn_criteria(engine, row, col):
                # Check if the square can be occupied
                if engine.can_be_occupied(row, col):
                    spawn_squares.append((row, col))

        # Return the list of spawn squares
        return spawn_squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the circus.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Fortress(Building):
    """
    Represents a fortress building in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the fortress building.

        :return: The string "fortress".
        """
        return "fortress"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Fortress object.

        :param row: The row position of the fortress.
        :param col: The column position of the fortress.
        :param color: The color of the fortress.
        """
        super().__init__(row, col, color)

        # Directions the fortress can spawn units
        self.directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the fortress can spawn units
        self.distance: int = 1

        # Additional actions available for the fortress
        self.additional_actions: list[str] = constant.FORTRESS_ADDITIONAL_ACTIONS

    def spawn_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the fortress can spawn units at.

        :param engine: The game engine.
        :return: A list of squares the fortress can spawn units at.
        """
        # Initialize an empty list to store the spawn squares
        spawn_squares: list[tuple[int, int]] = []

        # Check if the fortress can spawn units
        if not self.can_spawn(engine):
            return spawn_squares

        # Iterate over each direction in the spawn directions
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the base spawn criteria are met
            if self.base_spawn_criteria(engine, row, col):
                # Check if the square can be occupied by a rogue
                if engine.can_be_occupied_by_rogue(row, col):
                    spawn_squares.append((row, col))

        # Return the list of spawn squares
        return spawn_squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the fortress.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class PrayerStone(Building):
    """
    Represents a prayer stone building in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the prayer stone building.

        :return: The string "prayer_stone".
        """
        return "prayer_stone"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a PrayerStone object.

        :param row: The row position of the prayer stone.
        :param col: The column position of the prayer stone.
        :param color: The color of the prayer stone.
        """
        super().__init__(row, col, color)

        # Directions the prayer stone can spawn units
        self.directions: tuple = ()

        # Maximum distance the prayer stone can spawn units
        self.distance: int = 0

        # Remaining uses of the prayer stone
        self.remaining: int = 0

        # Yield when the prayer stone is prayed
        self.yield_when_prayed: int = constant.PRAYER_STONE_YIELD

        # Indicates if the prayer stone is affected by the jester
        self.is_effected_by_jester: bool = False

        # Additional actions available for the prayer stone
        self.additional_actions: list[str] = constant.PRAYER_STONE_ADDITIONAL_ACTIONS

        # Contextual options available for the prayer stone
        self.contextual_options: list[str] = ["ritual"]

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the prayer stone.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Monolith(Building):
    """
    Represents a monolith building in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the monolith building.

        :return: The string "monolith".
        """
        return "monolith"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Monolith object.

        :param row: The row position of the monolith.
        :param col: The column position of the monolith.
        :param color: The color of the monolith.
        """
        super().__init__(row, col, color)

        # Directions the monolith can spawn units
        self.directions: tuple = (
            constant.UP,
            constant.RIGHT,
            constant.LEFT,
            constant.DOWN,
            constant.UP_LEFT,
            constant.DOWN_LEFT,
            constant.DOWN_RIGHT,
            constant.UP_RIGHT,
        )

        # Maximum distance the monolith can spawn units
        self.distance: int = 2

        # Remaining uses of the monolith
        self.remaining: int = 0

        # Yield when the monolith is prayed
        self.yield_when_prayed: int = constant.MONOLITH_YIELD

        # Indicates if the monolith is affected by the jester
        self.is_effected_by_jester: bool = False

        # Additional actions available for the monolith
        self.additional_actions: list[str] = constant.MONOLITH_ADDITIONAL_ACTIONS

        # Contextual options available for the monolith
        self.contextual_options: list[str] = ["ritual"]

    def gold_general_ritual_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the gold general can perform rituals at.

        :param engine: The game engine.
        :return: A list of squares the gold general can perform rituals at.
        """
        # Initialize an empty list to store the ritual squares
        ritual_squares: list[tuple[int, int]] = []

        # Iterate over each direction in the spawn directions
        for direction in self.directions:
            for i in range(self.distance):
                row: int = self.row + direction[0] * i
                col: int = self.col + direction[1] * i

                # Check if the base spawn criteria are met
                if self.base_spawn_criteria(engine, row, col):
                    # Check if the square can be occupied by the gold general
                    if engine.can_be_occupied_by_gold_general(row, col):
                        ritual_squares.append((row, col))

        # Return the list of ritual squares
        return ritual_squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the monolith.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Ferz(Piece):
    """
    Represents a Ferz piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the Ferz piece.

        :return: The string "ferz".
        """
        return "ferz"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Ferz object.

        :param row: The row position of the Ferz.
        :param col: The column position of the Ferz.
        :param color: The color of the Ferz.
        """
        super().__init__(row, col, color)

        # Directions the Ferz can mine
        self.mining_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Directions the Ferz can capture
        self.capture_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
        )

        # Directions the Ferz can move
        self.move_directions: tuple = (
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Maximum distance the Ferz can move
        self.move_distance: int = 3

        # Maximum distance the Ferz can capture
        self.capture_distance: int = 1

        # Contextual options available for the Ferz
        self.contextual_options: list[str] = ["mine"]

    def mining_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Ferz can mine.

        :param engine: The game engine.
        :return: A list of squares the Ferz can mine.
        """
        # Initialize an empty list to store the mining squares
        mining_squares: list[tuple[int, int]] = []

        # Iterate over each direction in the mining directions
        for destination_row, destination_col in self.mining_directions:
            # Calculate the target row and column
            row: int = self.row - destination_row
            col: int = self.col - destination_col

            # Get the occupying unit on the target tile
            occupying_unit: Optional[Unit] = engine.get_occupying(row, col)

            # Check if the tile has a mine-able resource
            if engine.has_mine_able_resource(row, col):
                # Check if the tile is empty or occupied by a unit of the same color
                if (
                    not occupying_unit
                    or engine.get_occupying_color(row, col) == self.color
                ):
                    mining_squares.append((row, col))

            # Check if the tile can contain a quarry and has no units or resources
            elif engine.can_contain_quarry(
                row, col
            ) and engine.has_no_units_or_resources(row, col):
                mining_squares.append((row, col))

        print(mining_squares)
        return mining_squares

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Ferz can capture.

        :param engine: The game engine.
        :return: A list of squares the Ferz can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Iterate over each direction in the capture directions
        for direction in self.capture_directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]

            # Check if the Ferz can capture at the given position
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        # Return the list of capture squares
        return squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Ferz can move to.

        :param engine: The game engine.
        :return: A list of squares the Ferz can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Set the move distance based on whether it is the first move
        self.move_distance = 2 if not self.first_move else 3

        # Iterate over each direction in the move directions
        for direction in self.move_directions:
            for distance in range(1, self.move_distance):
                row: int = self.row + direction[0] * distance
                col: int = self.col + direction[1] * distance

                # Check if the tile is within bounds
                if not engine.tile_in_bounds(row, col):
                    break

                # Check if the base move criteria are met
                if not self.base_move_criteria(engine, row, col):
                    break
                else:
                    squares.append((row, col))

        # Return the list of move squares
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the Ferz.

        :param engine: The game engine.
        :return: Always returns True.
        """
        return True


class Cavalry(Piece):
    """
    Represents a Cavalry piece in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the Cavalry piece.

        :return: The string "cavalry".
        """
        return "cavalry"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Cavalry object.

        :param row: The row position of the Cavalry.
        :param col: The column position of the Cavalry.
        :param color: The color of the Cavalry.
        """
        super().__init__(row, col, color)

        # Directions the Cavalry can move in a knight-like pattern
        self.directions: tuple = (
            constant.TWO_UP_RIGHT,
            constant.TWO_RIGHT_UP,
            constant.TWO_DOWN_RIGHT,
            constant.TWO_RIGHT_DOWN,
            constant.TWO_UP_LEFT,
            constant.TWO_LEFT_UP,
            constant.TWO_DOWN_LEFT,
            constant.TWO_LEFT_DOWN,
        )

        # Directions the Cavalry can mine
        self.mining_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        )

        # Directions the Cavalry can move in a straight line
        self.move_directions: tuple = (
            constant.RIGHT,
            constant.LEFT,
            constant.UP,
            constant.DOWN,
        )

        # Directions the Cavalry can capture
        self.capture_directions: tuple = (
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_LEFT,
            constant.DOWN_RIGHT,
        )

        # Contextual options available for the Cavalry
        self.contextual_options: list[str] = ["mine"]

        # Maximum distance the Cavalry can move
        self.move_distance: int = 2

        # Maximum distance the Cavalry can capture
        self.distance: int = 1

    def capture_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Cavalry can capture.

        :param engine: The game engine.
        :return: A list of squares the Cavalry can capture.
        """
        # Initialize an empty list to store the capture squares
        squares: list[tuple[int, int]] = []

        # Pawn Capture
        if not self.first_move:
            for direction in self.capture_directions:
                row: int = self.row + direction[0]
                col: int = self.col + direction[1]
                if self.can_capture(row, col, engine):
                    squares.append((row, col))
            return squares

        # Knight Capture
        for direction in self.directions:
            row: int = self.row + direction[0]
            col: int = self.col + direction[1]
            if self.can_capture(row, col, engine):
                squares.append((row, col))

        # Return the list of capture squares
        return squares

    def right_click(self, engine: "Engine") -> bool:
        """
        Handles the right-click action on the Cavalry.

        :param engine: The game engine.
        :return: Returns False if it is not the first move, otherwise True.
        """
        if not self.first_move:
            return False

        return True

    def mining_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Cavalry can mine.

        :param engine: The game engine.
        :return: A list of squares the Cavalry can mine.
        """
        # Initialize an empty list to store the mining squares
        mining_squares: list[tuple[int, int]] = []

        # Iterate over each direction in the mining directions
        for direction in self.mining_directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]

            # Check if the square has mine-able resources
            if engine.has_mine_able_resource(row, col):
                if engine.get_occupying(row, col):
                    if engine.get_occupying_color(row, col) is not self.color:
                        pass
                    elif engine.get_occupying_color(row, col) is self.color:
                        mining_squares.append((row, col))
                elif not engine.has_occupying(row, col):
                    mining_squares.append((row, col))
            elif engine.can_contain_quarry(
                row, col
            ) and engine.has_no_units_or_resources(row, col):
                mining_squares.append((row, col))

        # Return the list of mining squares
        return mining_squares

    def move_squares(self, engine: "Engine") -> list[tuple[int, int]]:
        """
        Determines the squares the Cavalry can move to.

        :param engine: The game engine.
        :return: A list of squares the Cavalry can move to.
        """
        # Initialize an empty list to store the move squares
        squares: list[tuple[int, int]] = []

        # Pawn Moves
        if not self.first_move:
            for direction in self.move_directions:
                for distance in range(1, self.move_distance):
                    row: int = self.row + direction[0] * distance
                    col: int = self.col + direction[1] * distance
                    if not engine.tile_in_bounds(row, col):
                        break
                    if not self.base_move_criteria(engine, row, col):
                        break
                    else:
                        squares.append((row, col))
            return squares

        # Knight Moves
        for direction in self.directions:
            row: int = self.row - direction[0]
            col: int = self.col - direction[1]
            if self.base_move_criteria(engine, row, col):
                squares.append((row, col))

        # Return the list of move squares
        return squares


class Trap(Building):
    """
    Represents a trap building in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the trap building.

        :return: The string "trap".
        """
        return "trap"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Trap object.

        :param row: The row position of the trap.
        :param col: The column position of the trap.
        :param color: The color of the trap.
        """
        super().__init__(row, col, color)

    def highlight_self_square_unused(self, win: pygame.Surface):
        """
        Override default highlights so the square is not highlighted. This is not a 'usable' piece.

        :param win: The game window surface.
        """
        pass


class Wall(Building):
    """
    Represents a wall building in the game with various attributes and methods.
    """

    def __repr__(self) -> str:
        """
        Returns the string representation of the wall building.

        :return: The string "wall".
        """
        return "wall"

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Wall object.

        :param row: The row position of the wall.
        :param col: The column position of the wall.
        :param color: The color of the wall.
        """
        super().__init__(row, col, color)

        # Indicates that this building is a wall
        self.is_wall: bool = True

    def highlight_self_square_unused(self, win: pygame.Surface):
        """
        Override default highlights so the square is not highlighted. This is not a 'usable' piece.

        :param win: The game window surface.
        """
        pass
