import os
import random
from typing import Dict, List, Callable
import typing

if typing.TYPE_CHECKING:
    from engine import Engine
    from player import Player
    from state import State

from unit import *


def get_decree_resource_sprite():
    resource = list(constant.DECREE_COST.keys())[-1]
    key = {"gold": "gold_coin", "wood": "log", "stone": "stone"}
    return constant.MENU_ICONS[key[resource]]


def get_initial_menu_position(row, col):
    return (
        col * constant.SQ_SIZE + constant.SQ_SIZE // 2,
        row * constant.SQ_SIZE + constant.SQ_SIZE // 2,
    )


class Menu:
    """
    Represents a menu in the game with various attributes and methods.
    """

    def __init__(self, win: pygame.Surface, engine: "Engine"):
        """
        Initializes a Menu object.

        :param win: The game window surface.
        :param engine: The game engine.
        """
        # Menu dimensions
        self._menu_width = None
        self._menu_height = None

        # Menu position
        self._menu_position_x = None
        self._menu_position_y = None

        # Default action_list
        self.action_list = []
        self.highlight_list = []

        # Screen surface and engine
        self.win: pygame.Surface = win
        self.engine: "Engine" = engine

        # Dictionary of pieces and buildings for each color
        self.pieces: dict[str, dict] = {
            "w": constant.W_PIECES | constant.W_BUILDINGS,
            "b": constant.B_PIECES | constant.B_BUILDINGS,
        }

        # Buffer to prevent menu from clipping the screen edges
        self._menu_boundary_buffer: int = 0

    def draw(self):
        """
        Draws the menu on the game window.
        This method should be overridden in subclasses to implement specific behavior.
        """
        return self.menu_position_x, self.menu_position_y

    @property
    def menu_boundary_buffer(self) -> int:
        """
        Returns the menu boundary buffer.

        :return: The menu boundary buffer.
        """
        return self.menu_width // 2

    @property
    def menu_width(self) -> int:
        """
        Returns the menu width.

        :return: The menu width.
        """
        return self._menu_width

    @menu_width.setter
    def menu_width(self, value: int):
        """
        Sets the menu width.

        :param: value: The menu width.
        """
        self._menu_width = value

    @property
    def menu_height(self) -> int:
        """
        Returns the menu height.

        :return: The menu height.
        """
        return self._menu_height

    @menu_height.setter
    def menu_height(self, value: int):
        """
        Sets the menu height.

        :param: value: The menu width.
        """
        self._menu_height = value

    def correct_menu_boundary(self) -> tuple[int, int]:
        """
        Positions the menu near the mouse cursor while ensuring it stays within screen boundaries.

        :return: The corrected x and y positions for the menu.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Get the board dimensions
        board_width: int = constant.BOARD_WIDTH_PX
        board_height: int = constant.BOARD_HEIGHT_PX

        # Get the menu dimensions
        menu_width: int = self.menu_width
        menu_height: int = self.menu_height

        # Get the boundary buffer
        boundary_buffer: int = self.menu_boundary_buffer

        # Start at mouse position
        x: int = mouse_x
        y: int = mouse_y

        # Adjust X to keep menu within screen width
        if x + menu_width > board_width:
            x = board_width - menu_width - constant.SQ_SIZE // 2
        elif x < 0:
            x = boundary_buffer  # Prevent clipping on the left side

        # Adjust Y to keep menu within screen height
        if y + menu_height > board_height:
            y = board_height - menu_height - constant.SQ_SIZE // 2
        elif y < 0:
            y = boundary_buffer  # Prevent clipping on the top side

        return x, y

    @property
    def menu_position_x(self) -> int:
        """
        Returns the x-coordinate of the menu position.

        :return: The x-coordinate of the menu position.
        """
        return self._menu_position_x

    @menu_position_x.setter
    def menu_position_x(self, value: int):
        """
        Sets the x-coordinate of the menu position.

        :param: value: The x-coordinate of the menu position.
        """
        self._menu_position_x = value

    @property
    def menu_position_y(self) -> int:
        """
        Returns the y-coordinate of the menu position.

        :return: The y-coordinate of the menu position.
        """
        return self._menu_position_y

    @menu_position_y.setter
    def menu_position_y(self, value: int):
        """
        Sets the y-coordinate of the menu position.

        :param: value: The y-coordinate of the menu position.
        """
        self._menu_position_y = value

    def mouse_in_menu_bounds(self) -> bool:
        """
        Checks if the mouse is within the menu boundaries.

        :return: True if the mouse is within the menu boundaries, False otherwise.
        """
        # Get the current mouse position
        x, y = pygame.mouse.get_pos()

        # Check if the mouse is outside the board
        if (
            x <= 0
            or x >= constant.BOARD_WIDTH_PX - 1
            or y <= 0
            or y >= constant.BOARD_HEIGHT_PX - 1
        ):
            return False

        # Check if the mouse is outside the menu bounds
        if not (
            self.menu_position_x - self.menu_boundary_buffer
            <= x
            <= self.menu_position_x + self.menu_boundary_buffer + self.menu_width
            and self.menu_position_y - self.menu_boundary_buffer
            <= y
            <= self.menu_position_y + self.menu_boundary_buffer + self.menu_height
        ):
            return False

        return True

    def get_index_selected(
        self, pos: Tuple[int, int], options: List[str]
    ) -> Optional[int]:
        """
        Determines the index of the options list corresponding to the given mouse position.

        This method calculates which option is selected based on the mouse position
        within the menu boundaries. It iterates through the list of options and checks if
        the mouse's Y-coordinate falls within the vertical range of each option.

        :param pos: The current mouse position as a tuple (x, y).
        :param options: The list of ritual options.
        :return: The index of the ritual if the mouse position is within bounds, else None.
        """
        # Check if the mouse's X-coordinate is within the menu's width
        if pos[0] < self.menu_position_x + self.menu_width:
            # Get the number of options
            length = len(options)

            # Iterate through each option to determine if the mouse is within its vertical range
            for index in range(length):
                # Calculate the starting Y-coordinate for the current option
                start_y = (index / length) * self.menu_height + self.menu_position_y

                # Calculate the ending Y-coordinate for the current option
                end_y = ((index + 1) / length) * self.menu_height + self.menu_position_y

                # Check if the mouse's Y-coordinate is within the current option's range
                if start_y <= pos[1] < end_y:
                    return index

        # Return None if the mouse position is not within any option's range
        return None

    def get_option_selected(self, options: list[str]) -> Optional[str]:
        """
        Determines which option was clicked based on the mouse position.
        This is used in almost all menus with edge to edge highlighting.

        :return: The clicked option, or None if no ritual was clicked.
        """
        pos = pygame.mouse.get_pos()
        index = self.get_index_selected(pos, options)
        return options[index] if index is not None else None

    def close(self):
        """
        Closes the menu.
        """
        pass

    def mouse_move(self):
        """
        Handles mouse movement to highlight items in the action list
        based on the mouse's vertical position within the menu.

        The method checks if the mouse is within the bounds of the menu,
        and highlights the corresponding item in the resource list if so.

        This default implementation will work for any menu class with the attributes
        self.action_list list[str] and self.highlight_list list[bool].
        """
        # Get the current mouse position
        mouse_x: int
        mouse_y: int
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # If the mouse is outside the menu bounds, remove highlights and set cursor to arrow
        if mouse_x >= self.menu_position_x + self.menu_width:
            # Reset all highlights
            self.highlight_list = [False] * len(self.highlight_list)
            # Set cursor to arrow
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return

        # Get the index of the item being hovered over
        highlighted_index: Optional[int]
        highlighted_index = self.get_index_selected(
            (mouse_x, mouse_y), self.action_list
        )

        # If no item is highlighted, reset all highlights and set cursor to arrow
        if highlighted_index is None:
            if any(self.highlight_list):
                # Reset all highlights
                self.highlight_list = [False] * len(self.highlight_list)
                # Set cursor to arrow
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return

        # Highlight the item at the current index if it is not already highlighted
        if not self.highlight_list[highlighted_index]:
            # Update the highlight list to highlight the current index
            self.highlight_list = [
                i == highlighted_index for i in range(len(self.highlight_list))
            ]
            # Set cursor to hand to indicate an interactive element
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def left_click(self) -> bool:
        """
        Handles the left-click action on the menu.
        This method should be overridden in subclasses to implement specific behavior.
        """
        return False

    def right_click(self):
        """
        Handles the right-click action on the menu.
        This method should be overridden in subclasses to implement specific behavior.
        """
        return False


class Notification(Menu):
    """
    Represents a notification menu in the game with various attributes and methods.
    """

    def __init__(
        self,
        row: int,
        col: int,
        win: pygame.Surface,
        engine: "Engine",
        message: str = "blank",
    ):
        """
        Initializes the notification menu at the given board position.

        :param row: The row position of the notification.
        :param col: The column position of the notification.
        :param win: The game window surface.
        :param engine: The game engine.
        :param message: The notification message.
        """
        # Initialize the parent Menu class
        super().__init__(win, engine)

        # Set the row and column positions
        self.row: int = row
        self.col: int = col

        # Set the color based on the current turn
        self.color: Tuple[int, int, int] = constant.turn_to_color[self.engine.turn]

        # Set the notification message
        self.message: List[str] = constant.NOTIFICATIONS[message]

        # Font setup
        self.font_size: int = round(constant.SQ_SIZE * 0.3)
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Menu dimensions
        self.menu_width: int = constant.SQ_SIZE * 3
        self.menu_height: int = constant.SQ_SIZE + len(self.message) * constant.SQ_SIZE
        self.y_buffer_between_messages: int = constant.SQ_SIZE

        # Menu boundary buffer
        self.menu_boundary_buffer_x: int = self.menu_width + self.menu_boundary_buffer
        self.menu_boundary_buffer_y: int = self.menu_height + self.menu_boundary_buffer

        # Positioning
        self.initial_menu_position: Tuple[int, int] = get_initial_menu_position(
            self.row, self.col
        )
        self.menu_position_x: int
        self.menu_position_y: int
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        # Create menu surface
        self.menu: pygame.Surface = pygame.Surface((self.menu_width, self.menu_height))

        # "OK" text rendering
        self.ok_text_surface: pygame.Surface = self.font.render("ok", True, self.color)
        self.ok_display_x: int = (
            self.menu_width - self.ok_text_surface.get_width()
        ) // 2
        self.ok_display_y: int = self.menu_height - self.ok_text_surface.get_height()

        # Message rendering
        self.message_text_surfaces: List[pygame.Surface] = [
            self.font.render(msg, True, self.color) for msg in self.message
        ]

        # Highlight area for interaction
        self.highlight_display_x: int = 0
        self.highlight_display_y: int = self.menu_height - constant.SQ_SIZE
        self.square: pygame.Surface = pygame.Surface(
            (self.menu_width, constant.SQ_SIZE)
        )
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.highlight: bool = False

    def draw(self):
        """
        Draws the notification menu on the game window.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Initialize the vertical buffer for message rendering
        y_buffer: int = 0

        # Render each message in the notification
        for message in self.message_text_surfaces:
            text_display_x: int = self.menu_width // 2 - message.get_width() // 2
            self.menu.blit(message, (text_display_x, y_buffer))
            y_buffer += self.y_buffer_between_messages

        # Highlight the "OK" button if needed
        if self.highlight:
            self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
            self.menu.blit(
                self.square, (self.highlight_display_x, self.highlight_display_y)
            )

        # Render the "OK" text
        self.menu.blit(self.ok_text_surface, (self.ok_display_x, self.ok_display_y))

        # Blit the menu onto the game window
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))

    def left_click(self) -> bool:
        """
        Handles the left-click action on the notification menu.

        :return: True if the click is within the "OK" button area, otherwise False.
        """
        # Calculate the vertical buffer above the "OK" button
        menu_above_ok_button: int = len(self.message) * round(constant.SQ_SIZE * 0.8)

        # Get the current mouse position
        pos: Tuple[int, int] = pygame.mouse.get_pos()

        # Check if the click is within the "OK" button area
        if self.menu_position_x < pos[0] < self.menu_position_x + self.menu_width:
            if (
                self.menu_position_y + menu_above_ok_button
                < pos[1]
                < self.menu_position_y + self.menu_height
            ):
                self.engine.close_menus()
                return True
        return False

    def right_click(self):
        """
        Handles the right-click action on the notification menu.
        """
        self.engine.close_menus()

    def mouse_move(self):
        """
        Handles mouse movement over the notification menu.
        """
        # Calculate the vertical buffer above the "OK" button
        menu_above_ok_button: int = len(self.message) * round(constant.SQ_SIZE * 0.8)

        # Get the current mouse position
        pos: Tuple[int, int] = pygame.mouse.get_pos()

        # Check if the mouse is within the "OK" button area
        if self.menu_position_x < pos[0] < self.menu_position_x + self.menu_width:
            if (
                self.menu_position_y + menu_above_ok_button
                < pos[1]
                < self.menu_position_y + self.menu_height
            ):
                self.highlight = True
                return

        # Reset the highlight state
        self.highlight = False


class RitualMenu(Menu):
    """
    Represents a ritual menu in the game with various attributes and methods.
    """

    def __init__(
        self,
        row: int,
        col: int,
        win: pygame.Surface,
        engine: "Engine",
        ritual_list: list[str],
        cost_type: str,
    ):
        """
        Initializes the ritual menu at the given board position.

        :param row: The row position of the ritual menu.
        :param col: The column position of the ritual menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param ritual_list: The list of rituals.
        :param cost_type: The type of cost for the rituals.
        """
        # Set the cost type and ritual list
        self.cost_type: str = cost_type

        # Set the row and column positions
        self.row: int = row
        self.col: int = col

        # Initialize the parent Menu class
        super().__init__(win, engine)

        # Set list of actions for this menu
        self.action_list: list = ritual_list

        # Font setup
        self.font_size: int = round(constant.SQ_SIZE / 2)
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Get the current player
        self.player = self.engine.players[self.engine.turn]

        # Initial menu position
        self.initial_menu_position: Tuple[int, int] = (
            self.col * constant.SQ_SIZE + constant.SQ_SIZE // 2,
            self.row * constant.SQ_SIZE + constant.SQ_SIZE // 2,
        )

        # Buffers for spacing
        self.vertical_buffer_between_pieces: int = constant.SQ_SIZE // 6
        self.horizontal_buffer_between_costs: int = round(constant.SQ_SIZE * 1.3)

        # Bar dimensions
        self.bar_width: int = constant.IMAGES["prayer_bar"].get_width()
        self.bar_height: int = constant.IMAGES["prayer_bar"].get_height()
        self.bar_end_width: int = constant.IMAGES["prayer_bar_end"].get_width()

        # Ritual dimensions
        self.rituals = constant.PRAYER_RITUALS
        self.ritual_width: int = self.rituals["w_gold_general"].get_width()
        self.ritual_height: int = self.rituals["w_gold_general"].get_height()

        # Gold icon setup
        self.gold_icon = constant.MENU_ICONS["gold_coin"]
        self.gold_icon_display_x: int = (
            self.ritual_width + self.vertical_buffer_between_pieces
        )
        self.gold_cost_text_display_x: int = (
            self.ritual_width + self.vertical_buffer_between_pieces * 2
        )

        # Menu dimensions
        if not self.cost_type == "gold":
            self.menu_width: int = (
                self.ritual_width
                + self.vertical_buffer_between_pieces
                + self.bar_end_width * 16
                + self.bar_width
            )
        else:
            self.menu_width: int = (
                self.ritual_width
                + self.vertical_buffer_between_pieces
                + self.gold_icon.get_width() * 2
            )

        self.menu_height: int = len(ritual_list) * self.ritual_height

        # Correct menu boundary
        self.menu_position_x: int
        self.menu_position_y: int
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        # Create menu surface
        self.menu: pygame.Surface = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(
            self.menu
        )

        # Menu boundary buffer
        self.menu_boundary_buffer_y: int = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x: int = self.menu_width + self.menu_boundary_buffer

        # Casting state
        self.casting = None

        # Prayer bar edges
        self.prayer_bar_edge: int = (
            self.vertical_buffer_between_pieces + self.ritual_width
        )
        self.prayer_bar_end_edge: int = self.prayer_bar_edge + self.bar_width

        # Vertical buffer for prayer bar
        self.y_buffer: int = (
            self.vertical_buffer_between_pieces // 2
            + self.ritual_height // 2
            - self.bar_height // 2
        )

        # Ritual highlight list
        self.highlight_list: List[bool] = []
        self.square: pygame.Surface = pygame.Surface(
            (self.menu_width, round(1 / len(self.action_list) * self.menu_height))
        )
        self.available_menu_space_for_prayer_bar: int = (
            self.menu_width - self.ritual_width
        )

        # Initialize ritual highlight list
        for _ in self.action_list:
            self.highlight_list.append(False)

    def full_length_of_prayer_bar(self, length_of_ritual: int) -> int:
        """
        Calculates the full length of the prayer bar for a given ritual length.

        :param length_of_ritual: The length of the ritual.
        :return: The full length of the prayer bar.
        """
        return self.bar_end_width * length_of_ritual + self.bar_width

    def left_click(self) -> bool:
        """
        Handles the left-click action for selecting and casting a ritual.

        :return: True if the ritual is successfully cast, otherwise reverts to the playing state.
        """
        # Determine the ritual being clicked
        self.casting: Optional[str] = self.get_option_selected(self.action_list)

        # Check if the ritual is valid and not intercepted
        if (
            self.casting is None
            or not self.engine.is_legal_ritual(self.casting, self.cost_type)
            or self.engine.get_occupying(self.row, self.col).intercepted
        ):
            return self.engine.state[-1].revert_to_playing_state()

        # Clear menus and transfer to the ritual state
        self.engine.menus = []
        return self.engine.transfer_to_ritual_state(self.casting, self.cost_type)

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        self.engine.state[-1].revert_to_playing_state()

    def draw(self):
        """
        Draws the ritual menu on the game window.
        """
        # Fill menu background
        self.menu.fill(constant.MENU_COLOR)

        # Draw paper texture
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Highlight selected rituals
        highlight_indices: List[int] = [
            i for i, highlighted in enumerate(self.highlight_list) if highlighted
        ]
        for index in highlight_indices:
            start_y: float = (index / len(self.action_list)) * self.menu_height
            self.menu.blit(self.square, (0, start_y))

        # Set highlight properties once (instead of inside a loop)
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Initialize buffers for drawing rituals and costs
        y_buffer_ritual: int = 0
        y_buffer_prayer: int = self.y_buffer

        # Cache values to avoid redundant dictionary lookups
        turn: str = self.engine.turn
        rituals: Dict[str, pygame.Surface] = self.rituals
        prayer_costs: Dict[str, Dict[str, int]] = constant.PRAYER_COSTS
        cost_type: str = self.cost_type
        player_gold: int = self.player.gold

        for ritual in self.action_list:
            cost_data: Dict[str, int] = prayer_costs[ritual]

            if cost_type == "prayer":
                prayer_cost: int = cost_data["prayer"]
                if prayer_cost > 0:
                    # Calculate the prayer bar position
                    bar_length: int = self.full_length_of_prayer_bar(prayer_cost)
                    bar_end_edge: int = (
                        self.ritual_width
                        + self.available_menu_space_for_prayer_bar // 2
                        - bar_length // 2
                    )
                    bar_edge: int = bar_end_edge - self.bar_width

                    # Draw prayer bars
                    self.menu.blit(
                        constant.IMAGES["prayer_bar"], (bar_edge, y_buffer_prayer)
                    )
                    for z in range(prayer_cost):
                        self.menu.blit(
                            constant.IMAGES["prayer_bar_end"],
                            (bar_end_edge + self.bar_end_width * z, y_buffer_prayer),
                        )

                    y_buffer_prayer += self.y_buffer + self.ritual_height // 2

            elif cost_type == "gold" and cost_data["gold"] > 0:
                gold_cost: int = cost_data["gold"]
                gold_color: Tuple[int, int, int] = (
                    constant.turn_to_color[turn]
                    if player_gold >= gold_cost
                    else constant.RED
                )
                gold_surface: pygame.Surface = self.font.render(
                    str(gold_cost), True, gold_color
                )

                # Compute Y positions for gold icon and cost text
                gold_icon_y: int = y_buffer_ritual + self.gold_icon.get_height() // 2
                gold_text_y: int = y_buffer_ritual + gold_surface.get_height() // 2

                self.menu.blit(self.gold_icon, (self.gold_icon_display_x, gold_icon_y))
                self.menu.blit(
                    gold_surface, (self.gold_cost_text_display_x, gold_text_y)
                )

            # Draw the ritual icon
            ritual_key: str = f"{turn}_{ritual}"
            self.menu.blit(rituals[ritual_key], (0, y_buffer_ritual))
            y_buffer_ritual += self.ritual_height

        # Draw menu onto the game window
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))


class TraderMenu(Menu):
    """
    Represents a trader menu in the game with various attributes and methods.
    """

    def __init__(
        self,
        row: int,
        col: int,
        win: pygame.Surface,
        engine: "Engine",
        resource_list: List[str],
        amounts: Dict[str, int],
        trade_arrow: pygame.Surface,
    ):
        """
        Initializes the trader menu at the given board position.

        :param row: The row position of the trader menu.
        :param col: The column position of the trader menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param resource_list: The list of resources.
        :param amounts: The amounts of each resource.
        :param trade_arrow: The trade arrow image.
        """
        self.row: int = row
        self.col: int = col
        self.key: Dict[str, str] = {
            "log": "wood",
            "gold_coin": "gold",
            "stone": "stone",
        }
        super().__init__(win, engine)
        self.action_list: List[str] = resource_list
        self.trade_arrow: pygame.Surface = trade_arrow
        self.amounts: Dict[str, int] = amounts
        self.player = self.engine.players[self.engine.turn]
        self.give_image: pygame.Surface = constant.IMAGES["give"]
        self.selected: Optional[str] = None
        self.horizontal_buffer: int = constant.SQ_SIZE // 2
        self.vertical_buffer_between_pieces: int = constant.SQ_SIZE // 4
        self.font_size: int = round(constant.SQ_SIZE / 2)
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.font_color: Tuple[int, int, int] = constant.turn_to_color[self.engine.turn]
        self.resource_height: int = constant.IMAGES["gold_coin"].get_width()
        self.resource_width: int = constant.IMAGES["gold_coin"].get_height()
        self.menu_width: int = (
            self.resource_width
            + self.horizontal_buffer
            + self.resource_width
            + constant.SQ_SIZE
        )
        self.menu_height: int = len(self.action_list) * (
            self.resource_height + self.vertical_buffer_between_pieces
        )
        self.menu: pygame.Surface = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture: pygame.Surface = (
            self.engine.get_current_state().scale_paper_texture(self.menu)
        )
        self.initial_menu_position: Tuple[int, int] = (
            self.col * constant.SQ_SIZE + constant.SQ_SIZE // 2,
            self.row * constant.SQ_SIZE + constant.SQ_SIZE // 2,
        )
        self.menu_position_x: int
        self.menu_position_y: int
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu_boundary_buffer_y: int = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x: int = self.menu_width + self.menu_boundary_buffer
        self.highlight_list: List[bool] = []
        self.square: pygame.Surface = pygame.Surface(
            (self.menu_width, round(1 / len(self.action_list) * self.menu_height))
        )
        for _ in self.action_list:
            self.highlight_list.append(False)
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    # def mouse_move(self):
    #     """
    #     Handles mouse movement to highlight items in the resource list
    #     based on the mouse's vertical position within the menu.
    #
    #     The method checks if the mouse is within the bounds of the menu,
    #     and highlights the corresponding item in the resource list if so.
    #     """
    #     # Get the current mouse position
    #     mouse_x, mouse_y = pygame.mouse.get_pos()
    #
    #     # Check if the mouse is within the horizontal bounds of the menu
    #     if mouse_x + (self.menu_width // 3) < self.menu_position_x:
    #         # If the mouse is outside the bounds, reset all highlights and cursor
    #         if any(self.highlight_list):
    #             self.highlight_list = [False] * len(self.highlight_list)
    #             pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    #         return
    #
    #     # Precompute the item height ratio to avoid repeated division
    #     item_height_ratio = 1 / len(self.resource_list) * self.menu_height
    #
    #     # Track the index that should be highlighted
    #     highlighted_index = None
    #
    #     # Iterate through the resource list to find which item is hovered over
    #     for index, _ in enumerate(self.resource_list):
    #         # Calculate the start and end Y-coordinates of the current menu item
    #         item_start_y = index * item_height_ratio + self.menu_position_y
    #         item_end_y = (index + 1) * item_height_ratio + self.menu_position_y
    #
    #         # Check if the mouse's Y-coordinate falls within the current item's bounds
    #         if round(item_start_y) <= mouse_y <= round(item_end_y):
    #             highlighted_index = index
    #             break  # Stop checking once a highlight is found
    #
    #     # Update highlighting only if necessary
    #     if highlighted_index is not None:
    #         # Only update if the item is not already highlighted
    #         if not self.highlight_list[highlighted_index]:
    #             self.highlight_list = [
    #                 i == highlighted_index
    #                 for i in range(len(self.highlight_list))
    #             ]
    #             pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    #     else:
    #         # Only reset if something was highlighted before
    #         if any(self.highlight_list):
    #             self.highlight_list = [False] * len(self.highlight_list)
    #             pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self) -> Tuple[int, int]:
        """
        Draws the trader menu on the game window.

        :return: The x and y positions of the menu.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Highlight selected resources
        for index in range(len(self.action_list)):
            start_y: float = (index / len(self.action_list)) * self.menu_height
            if self.highlight_list[index]:
                self.menu.blit(self.square, (0, start_y))

        # Initialize buffer for drawing resources and amounts
        y_buffer: int = 0

        # Draw each resource and its amount
        for resource in self.action_list:
            self.menu.blit(
                constant.IMAGES[resource],
                (self.horizontal_buffer // 2, y_buffer + self.menu_height // 16),
            )

            amount_text_surface: pygame.Surface = self.font.render(
                ": " + str(self.amounts[resource]), True, self.font_color
            )

            self.menu.blit(
                self.trade_arrow,
                (
                    self.menu_width - self.trade_arrow.get_width(),
                    y_buffer + self.menu_height // 16,
                ),
            )

            self.menu.blit(
                amount_text_surface,
                (self.resource_width + self.horizontal_buffer, y_buffer),
            )

            y_buffer += self.menu_height // len(self.action_list)

        # Blit the menu onto the game window
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class GiveMenu(TraderMenu):
    """
    Represents a give menu in the game with various attributes and methods.
    """

    def __init__(
        self,
        row: int,
        col: int,
        win: pygame.Surface,
        engine: "Engine",
        resource_list: List[str],
    ):
        """
        Initializes the give menu at the given board position.

        :param row: The row position of the give menu.
        :param col: The column position of the give menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param resource_list: The list of resources.
        """
        # Get the current player
        self.player = engine.players[engine.turn]

        # Get the amounts of each resource to give
        self.amounts: Dict[str, int] = {
            "log": engine.trade_handler.get_give_conversion("wood", self.player),
            "gold_coin": engine.trade_handler.get_give_conversion("gold", self.player),
            "stone": engine.trade_handler.get_give_conversion("stone", self.player),
        }

        # Set the trade arrow image
        self.trade_arrow: pygame.Surface = constant.IMAGES["give"]

        # Initialize the parent TraderMenu class
        super().__init__(
            row, col, win, engine, resource_list, self.amounts, self.trade_arrow
        )

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        # Reset piece trading state
        self.engine.piece_trading = None

        # Revert to the playing state
        self.engine.state[-1].revert_to_playing_state()

    def left_click(self) -> bool:
        """
        Handles the left-click action for selecting and giving a resource.

        :return: True if a resource is successfully given, otherwise False.
        """
        # Determine the selected resource based on the mouse position
        self.selected = self.get_option_selected(self.action_list)

        if self.selected is not None:
            # Get the amount of the selected resource to give
            amount_given: int = self.amounts[self.selected]

            # Add the selected resource and amount to the trading list
            self.engine.trading.append((self.selected, amount_given))

            # Close the current menus
            self.engine.close_menus()

            # Create a new resource list excluding the selected resource
            resource_list: List[str] = [
                resource
                for resource in ["log", "gold_coin", "stone"]
                if resource != self.selected
            ]

            # Get the row and column of the mouse position
            row: int
            col: int
            row, col = constant.convert_pos(pygame.mouse.get_pos())

            # Create and add a new ReceiveMenu
            menu = ReceiveMenu(
                row, col, self.win, self.engine, resource_list, amount_given
            )
            self.engine.menus.append(menu)

            return True

        return False


class ReceiveMenu(TraderMenu):
    """
    Represents a receiving menu in the game with various attributes and methods.
    """

    def __init__(
        self,
        row: int,
        col: int,
        win: pygame.Surface,
        engine: "Engine",
        resource_list: List[str],
        amount_given: int,
    ):
        """
        Initializes the receiving menu at the given board position.

        :param row: The row position of the receiving menu.
        :param col: The column position of the receiving menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param resource_list: The list of resources.
        :param amount_given: The amount of resource given.
        """
        self.amount_given: int = amount_given
        self.amounts: Dict[str, int] = {
            "log": engine.trade_handler.get_receive_conversion(
                self.amount_given, "wood"
            ),
            "gold_coin": engine.trade_handler.get_receive_conversion(
                self.amount_given, "gold"
            ),
            "stone": engine.trade_handler.get_receive_conversion(
                self.amount_given, "stone"
            ),
        }
        self.trade_arrow: pygame.Surface = constant.IMAGES["receive"]
        super().__init__(
            row, col, win, engine, resource_list, self.amounts, self.trade_arrow
        )

    def left_click(self) -> bool:
        """
        Handles the left-click action for selecting and receiving a resource.

        :return: True if a resource is successfully received, otherwise False.
        """
        # Determine the selected resource based on the mouse position
        self.selected: Optional[str] = self.get_option_selected(self.action_list)

        if self.selected is not None:
            # Get the amount of the selected resource to receive
            amount: int = self.engine.trade_handler.get_receive_conversion(
                self.amount_given, self.key[self.selected]
            )

            # Clear the current menus
            self.engine.menus = []

            # Add the selected resource and amount to the trading list
            self.engine.trading.append((self.selected, amount))

            # Execute the trade
            self.engine.trade()

            return True

        return False

    def right_click(self):
        """
        Handles the right-click action to revert to the previous trader menu.
        """
        # Close the current menus
        self.engine.close_menus()

        # Clear the trading list
        self.engine.trading = []

        # Get the row and column of the mouse position
        row: int
        col: int
        row, col = constant.convert_pos(pygame.mouse.get_pos())

        # Create and display a new trader menu
        self.engine.create_trader_menu(row, col, False)


class StealingMenu(Menu):
    """
    Represents the menu for stealing resources from a tile on the game board.

    This menu handles displaying the resources available for stealing and updating the game state.
    """

    def __init__(self, row: int, col: int, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the StealingMenu.

        :param row: The row position of the menu.
        :param col: The column position of the menu.
        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        self.row = row
        self.col = col

        # Initialize the type of entity being stolen from
        self.type_stolen_from = None

        # Call the parent class constructor
        super().__init__(win, engine)

        # Set action list and type of entity stolen from
        self.action_list = ["log", "gold_coin", "stone"]

        # The key maps resource name to corresponding currency
        self.key = {"log": "wood", "gold_coin": "gold", "stone": "stone"}

        # Determine the type of entity occupying the tile
        piece = self.engine.get_occupying(row, col)

        # Create a mapping of classes to type strings
        entity_map = {
            Trader: "trader",
            Piece: "piece",
            Building: "building",
        }

        # Check the type of the piece and set the appropriate type
        for entity_class, entity_type in entity_map.items():
            if isinstance(piece, entity_class):
                self.type_stolen_from = entity_type
                break

        # Get the amounts of each resource available for stealing
        self.amounts = {
            "log": self.engine.stealing_values("wood", self.type_stolen_from),
            "gold_coin": self.engine.stealing_values("gold", self.type_stolen_from),
            "stone": self.engine.stealing_values("stone", self.type_stolen_from),
        }
        for resource in self.action_list:
            if self.amounts[resource] == 0:
                self.action_list.remove(resource)

        # Set up menu dimensions and appearance

        # Set the horizontal buffer between elements to the size of a square
        self.horizontal_buffer = constant.SQ_SIZE

        # Set the vertical buffer between pieces to one-fourth the size of a square
        self.vertical_buffer_between_pieces = constant.SQ_SIZE // 4

        # Set the font size as half of the square size, rounded for better visual appearance
        self.font_size = round(constant.SQ_SIZE / 2)

        # Create the font object using the font file "font.ttf" and the calculated font size
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Set the font color based on the current player's turn using a predefined color mapping
        self.font_color = constant.turn_to_color[self.engine.turn]

        # Set the resource height as the width of the gold coin image
        self.resource_height = constant.IMAGES["gold_coin"].get_width()

        # Set the resource width as the height of the gold coin image
        self.resource_width = constant.IMAGES["gold_coin"].get_height()

        # Calculate the menu width as the sum of two resource widths and the horizontal buffer
        self.menu_width = (
            self.resource_width + self.horizontal_buffer + self.resource_width
        )

        # Calculate the menu height based on the number of items in the spawn list
        # Each item will take up space equivalent to the resource height plus vertical buffer
        self.menu_height = len(self.action_list) * (
            self.resource_height + self.vertical_buffer_between_pieces
        )

        # Create a pygame surface for the menu with the calculated width and height
        self.menu = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(
            self.menu
        )

        # Set initial menu position based on the column and row
        # Position the menu at the center of the grid square
        self.initial_menu_position = (
            self.col * constant.SQ_SIZE
            + constant.SQ_SIZE // 2,  # X position (centered within the column)
            self.row * constant.SQ_SIZE
            + constant.SQ_SIZE // 2,  # Y position (centered within the row)
        )

        # Correct the menu's position based on boundary conditions (e.g., screen edges or available space)
        # The returned position ensures that the menu stays within the boundaries
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        # Set the vertical boundary buffer, which is the height of the menu plus the menu boundary buffer
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer

        # Set the horizontal boundary buffer, which is the width of the menu plus the menu boundary buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer

        # Initialize highlight list for spawn items
        self.highlight_list = []
        self.square = pygame.Surface(
            (self.menu_width, round(1 / len(self.action_list) * self.menu_height))
        )
        for _ in self.action_list:
            self.highlight_list.append(False)
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def draw(self) -> Tuple[int, int]:
        """
        Draws the stealing menu on the game window.

        :return: The x and y position of the menu.
        """
        self.menu.fill(constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Highlight selected items
        for x in range(len(self.action_list)):
            a = x / len(self.action_list)
            b = a * self.menu_height
            if self.highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        # Set the vertical buffer to 0 to start drawing at the top of the menu
        y_buffer = 0

        # Iterate through the spawn list to draw the resources and amounts
        for p in self.action_list:
            # Center the resource image icon horizontally within the menu width
            # Align the icon at 1/3 of the menu width, centered within its section
            icon_x = self.menu_width // 3 - self.resource_width // 2

            # Draw the resource image at the calculated position
            self.menu.blit(
                constant.IMAGES[p], (icon_x, y_buffer + self.menu_height // 16)
            )

            # Center the amount text surface horizontally within the remaining 2/3 of the menu width
            amount_text_surface = self.font.render(
                ": " + str(self.amounts[p]), True, self.font_color
            )

            # Align the text at the center of the right side of the menu
            text_x = (self.menu_width * 2 // 3) - amount_text_surface.get_width() // 2

            # Draw the amount text below the resource image (adding a vertical offset for spacing)
            self.menu.blit(
                amount_text_surface,
                (text_x, y_buffer),
            )

            # Increment the y_buffer by the total height of the resource image + vertical spacing
            y_buffer += self.resource_height + self.vertical_buffer_between_pieces

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y

    def left_click(self) -> bool:
        """
        Handles the left-click action for selecting and stealing a resource.

        :return: True if a resource is successfully stolen, otherwise reverts to the playing state.
        """
        # Reset the stealing state
        self.engine.stealing = None

        # Determine the selected resource based on the mouse position
        stolen_resource: Optional[str] = self.get_option_selected(self.action_list)

        if stolen_resource:
            # Get the amount of the selected resource to steal
            amount: int = self.amounts[stolen_resource]

            # Clear the current menus
            self.engine.menus = []

            # Set the stealing state with the selected resource and amount
            self.engine.stealing = [self.key[stolen_resource], amount]

            return True

        # Reset the stealing state and revert to the playing state
        self.engine.stealing = None
        return self.engine.state[-1].revert_to_playing_state()

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        # Revert to the playing state
        self.engine.get_current_state().revert_to_playing_state()


class ResourceMenu(Menu):
    """
    Represents a resource menu in the game with various attributes and methods.
    """

    def __init__(self, row: int, col: int, win: pygame.Surface, engine: "Engine"):
        """
        Initializes the resource menu at the given board position.

        :param row: The row position of the resource menu.
        :param col: The column position of the resource menu.
        :param win: The game window surface.
        :param engine: The game engine.
        """
        # Set the row and column positions
        self.row: int = row
        self.col: int = col

        # Generate a random number between 1 and 4 for tree tile selection
        rand: str = str(random.randint(1, 4))

        # Initialize the parent Menu class
        super().__init__(win, engine)

        # Set list of actions for this menu
        self.action_list: list[str] = ["gold_tile_1", "quarry_1", "tree_tile_" + rand]

        # Initialize spawning state
        self.spawning: Optional[str] = None

        # Set horizontal buffer between elements
        self.horizontal_buffer: int = constant.SQ_SIZE

        # Set vertical buffer between pieces
        self.vertical_buffer_between_pieces: int = constant.SQ_SIZE // 4

        # Set font size
        self.font_size: int = round(constant.SQ_SIZE / 2)

        # Create font object
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Set resource dimensions
        self.resource_height: int = constant.RESOURCES["gold_tile_1"].get_width()
        self.resource_width: int = constant.RESOURCES["gold_tile_1"].get_height()

        # Calculate menu dimensions
        self.menu_width: int = self.resource_width + self.horizontal_buffer
        self.menu_height: int = len(self.action_list) * (
            self.resource_height + self.vertical_buffer_between_pieces
        )

        # Create menu surface
        self.menu: pygame.Surface = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture: pygame.Surface = (
            self.engine.get_current_state().scale_paper_texture(self.menu)
        )

        # Set initial menu position
        self.initial_menu_position: Tuple[int, int] = (
            self.col * constant.SQ_SIZE + constant.SQ_SIZE // 2,
            self.row * constant.SQ_SIZE + constant.SQ_SIZE // 2,
        )

        # Correct menu boundary
        self.menu_position_x: int
        self.menu_position_y: int
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        # Set menu boundary buffers
        self.menu_boundary_buffer_y: int = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x: int = self.menu_width + self.menu_boundary_buffer

        # Initialize highlight list for spawn items
        self.spawn_highlight_list: list[bool] = []
        self.square: pygame.Surface = pygame.Surface(
            (self.menu_width, round(1 / len(self.action_list) * self.menu_height))
        )
        for _ in self.action_list:
            self.spawn_highlight_list.append(False)

    def left_click(self) -> bool:
        """
        Handles the left-click action for selecting and spawning a resource.

        :return: True if a resource is successfully selected, otherwise reverts to the playing state.
        """
        # Reset ritual summon resource state
        self.engine.ritual_summon_resource = None

        # Determine the selected resource based on the mouse position
        self.spawning: Optional[str] = self.get_option_selected(self.action_list)

        if self.spawning is not None:
            # Clear current menus and set the ritual summon resource
            self.engine.menus = []
            self.engine.ritual_summon_resource = self.spawning
            return True

        # Reset ritual summon resource state and revert to the playing state
        self.engine.ritual_summon_resource = None
        return self.engine.state[-1].revert_to_playing_state()

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        # Reset ritual summon resource state
        self.engine.ritual_summon_resource = None

        # Revert to the playing state
        self.engine.state[-1].revert_to_playing_state()

    def draw(self) -> Tuple[int, int]:
        """
        Draws the resource menu on the game window.

        :return: The x and y positions of the menu.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Highlight selected items
        for index in range(len(self.action_list)):
            start_y: float = (index / len(self.action_list)) * self.menu_height
            if self.spawn_highlight_list[index]:
                self.menu.blit(self.square, (0, start_y))

        # Set highlight properties once (instead of inside a loop)
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Initialize buffer for drawing resources
        y_buffer: int = 0

        # Draw each resource
        for resource in self.action_list:
            self.menu.blit(
                constant.RESOURCES[resource], (self.horizontal_buffer // 2, y_buffer)
            )
            y_buffer += self.menu_height // len(self.action_list)

        # Blit the menu onto the game window
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class SpawningMenu(Menu):
    """
    Represents a spawning menu in the game with various attributes and methods.
    """

    def __init__(
        self,
        row: int,
        col: int,
        win: pygame.Surface,
        engine: "Engine",
        spawn_list: list[str],
        spawner: "Unit",
    ):
        """
        Initializes the spawning menu at the given board position.

        :param row: The row position of the spawning menu.
        :param col: The column position of the spawning menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param spawn_list: The list of items that can be spawned.
        :param spawner: The spawner object.
        """
        # Set the row and column positions
        self.row: int = row
        self.col: int = col

        # Set the spawner object
        self.spawner: "Unit" = spawner

        # Initialize spawning state
        self.spawning: Optional[str] = None

        # Initialize the parent Menu class
        super().__init__(win, engine)

        # Set list of actions for this menu
        self.action_list: list[str] = spawn_list

        # Set vertical buffer between pieces
        self.vertical_buffer_between_pieces: int = constant.SQ_SIZE // 4

        # Set font size
        self.font_size: int = round(constant.SQ_SIZE / 2)

        # Create font object
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Render test text to calculate menu width
        self.test_text: pygame.Surface = self.font.render("10", True, constant.RED)

        # Calculate menu dimensions
        self.menu_width: int = constant.SQ_SIZE * 5
        self.menu_height: int = (
            len(spawn_list) * constant.SPAWNING_MENU_HEIGHT_BUFFER
            + self.vertical_buffer_between_pieces
        )

        # Set initial menu position
        self.initial_menu_position: Tuple[int, int] = (
            self.col * constant.SQ_SIZE + constant.SQ_SIZE // 2,
            self.row * constant.SQ_SIZE + constant.SQ_SIZE // 2,
        )

        # Correct menu boundary
        self.menu_position_x: int
        self.menu_position_y: int
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        # Create menu surface
        self.menu: pygame.Surface = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture: pygame.Surface = (
            self.engine.get_current_state().scale_paper_texture(self.menu)
        )

        # Define spacing for costs dynamically
        first_third = self.menu_width // 3
        cost_section_width = (self.menu_width - first_third) // 3

        # Set positions for cost icons & text
        self.log_x = first_third
        self.gold_x = self.log_x + cost_section_width
        self.stone_x = self.gold_x + cost_section_width

        self.row_height = (
            self.menu_height // len(self.action_list)
            if len(self.action_list) > 0
            else 0
        )

        # Padding
        self.sq_size_div_6: int = constant.SQ_SIZE // 6
        self.sq_size_div_1_5: int = constant.SQ_SIZE // 1.5
        self.sq_size_div_4: int = constant.SQ_SIZE // 4

        # Get the current player
        self.player: "Player" = self.engine.players[self.engine.turn]

        # Initialize highlight list for spawn items
        self.highlight_list: list[bool] = []
        self.square: pygame.Surface = pygame.Surface(
            (self.menu_width, round(1 / len(self.action_list) * self.menu_height))
        )
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        for _ in self.action_list:
            self.highlight_list.append(False)

    def left_click(self) -> bool:
        """
        Handles the left-click action for selecting and spawning a resource.

        :return: True if a resource is successfully selected, otherwise reverts to the playing state.
        """
        # Reset spawning state
        self.engine.spawning = None

        # Determine the selected resource based on the mouse position
        self.spawning: Optional[str] = self.get_option_selected(self.action_list)

        if not self.spawning or not self.engine.is_legal_spawn(
            self.spawning, self.spawner
        ):
            # Reset spawning state and revert to the playing state
            self.engine.spawning = None
            self.engine.state[-1].revert_to_playing_state()
            return True

        # Clear current menus and set the spawning state
        self.engine.menus = []
        self.engine.get_occupying(self.spawner.row, self.spawner.col).purchasing = True
        self.engine.get_occupying(self.spawner.row, self.spawner.col).pre_selected = (
            False
        )
        return self.engine.transfer_to_spawning_state(self.spawning)

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        # Reset spawning state
        self.engine.spawning = None

        # Revert to the playing state
        self.engine.state[-1].revert_to_playing_state()

    def draw_cost(
        self,
        resource_type: str,
        x_pos: int,
        cost: int,
        player_amount: int,
        y_buffer: int,
    ):
        """
        Draws the cost of a resource on the menu, centering it within its allocated section.

        :param resource_type: The type of resource (e.g., "log", "gold", "stone").
        :param x_pos: The x-coordinate position to draw the resource cost.
        :param cost: The cost of the resource.
        :param player_amount: The amount of the resource the player currently has.
        :param y_buffer: The y-coordinate buffer for drawing the resource cost.
        """
        if cost == 0:
            return  # No need to draw anything if the cost is zero

        # Determine color based on player resources
        color: pygame.Color = (
            constant.turn_to_color[self.engine.turn]
            if player_amount >= cost
            else constant.RED
        )

        # Render cost text
        cost_surface: pygame.Surface = self.font.render(str(cost), True, color)

        # Get icon and text heights
        icon_surface = constant.MENU_ICONS[resource_type]
        icon_height = icon_surface.get_height()
        text_height = cost_surface.get_height()

        # Compute centered y-positions
        icon_y = y_buffer + (self.row_height - icon_height) // 2
        text_y = y_buffer + (self.row_height - text_height) // 2

        # Draw icon
        self.menu.blit(icon_surface, (x_pos, icon_y))

        # Draw cost text
        self.menu.blit(cost_surface, (x_pos + icon_surface.get_width() + 5, text_y))

    def draw(self) -> Tuple[int, int]:
        """
        Draws the spawning menu on the game window.

        :return: The x and y positions of the menu.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Highlight selected items
        for index, highlighted in enumerate(self.highlight_list):
            if highlighted:
                start_y = (index / len(self.action_list)) * self.menu_height
                self.menu.blit(self.square, (0, start_y))

        num_items = len(self.action_list)
        menu_height = self.menu.get_height()

        # Calculate dynamic row height
        row_height = menu_height // num_items if num_items > 0 else 0

        # Start y_buffer at the top of the menu
        y_buffer = 0

        # Draw each resource and its costs
        for piece in self.action_list:
            piece_cost = constant.PIECE_COSTS[piece]
            piece = "quarry_1" if piece == "quarry_1" else f"{self.engine.turn}_{piece}"

            # Draw costs
            self.draw_cost(
                "log", self.log_x, piece_cost["log"], self.player.wood, y_buffer
            )
            self.draw_cost(
                "gold_coin", self.gold_x, piece_cost["gold"], self.player.gold, y_buffer
            )
            self.draw_cost(
                "stone", self.stone_x, piece_cost["stone"], self.player.stone, y_buffer
            )

            piece_surface = self.pieces[self.engine.turn][piece]

            # Get menu's first third width
            third_width = self.menu.get_width() // 3

            # Get piece dimensions
            piece_width, piece_height = piece_surface.get_size()

            # Compute x position to center in the first third
            piece_x = (third_width - piece_width) // 2

            # Compute y position to center within the dynamically calculated row
            piece_y = y_buffer + (row_height - piece_height) // 2

            # Draw resource image centered in both x and y
            self.menu.blit(piece_surface, (piece_x, piece_y))

            y_buffer += row_height  # Move to next row dynamically

        # Blit the menu onto the game window
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class StableMenu(SpawningMenu):
    """
    Represents a spawning menu for the stable in the game with various attributes and methods.
    """

    def __init__(
        self, row: int, col: int, win: pygame.Surface, engine: "Engine", spawner: "Unit"
    ):
        """
        Initializes the stable spawning menu at the given board position.

        :param row: The row position of the spawning menu.
        :param col: The column position of the spawning menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param spawner: The spawner object.
        """
        # Set the list of items that can be spawned
        spawn_list: list[str] = constant.STABLE_SPAWN_LIST

        # Set the spawner object
        self.spawner: "Unit" = spawner

        # Initialize the parent SpawningMenu class
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self) -> str:
        """
        Returns a string representation of the stable menu.

        :return: The string representation of the stable menu.
        """
        return "stable"


class FortressMenu(SpawningMenu):
    """
    Represents a spawning menu for the fortress in the game with various attributes and methods.
    """

    def __init__(
        self, row: int, col: int, win: pygame.Surface, engine: "Engine", spawner: "Unit"
    ):
        """
        Initializes the fortress spawning menu at the given board position.

        :param row: The row position of the spawning menu.
        :param col: The column position of the spawning menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param spawner: The spawner object.
        """
        # Set the list of items that can be spawned
        spawn_list: list[str] = constant.FORTRESS_SPAWN_LIST

        # Set the spawner object
        self.spawner: "Unit" = spawner

        # Initialize the parent SpawningMenu class
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self) -> str:
        """
        Returns a string representation of the fortress menu.

        :return: The string representation of the fortress menu.
        """
        return "fortress"


class BuilderMenu(SpawningMenu):
    """
    Represents a spawning menu for the builder in the game with various attributes and methods.
    """

    def __init__(
        self, row: int, col: int, win: pygame.Surface, engine: "Engine", spawner: "Unit"
    ):
        """
        Initializes the builder spawning menu at the given board position.

        :param row: The row position of the spawning menu.
        :param col: The column position of the spawning menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param spawner: The spawner object.
        """
        # Set the list of items that can be spawned
        spawn_list: list[str] = constant.BUILDER_SPAWN_LIST

        # Set the spawner object
        self.spawner: "Unit" = spawner

        # Initialize the parent SpawningMenu class
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self) -> str:
        """
        Returns a string representation of the builder menu.

        :return: The string representation of the builder menu.
        """
        return "builder"


class CastleMenu(SpawningMenu):
    """
    Represents a spawning menu for the castle in the game with various attributes and methods.
    """

    def __init__(
        self, row: int, col: int, win: pygame.Surface, engine: "Engine", spawner: "Unit"
    ):
        """
        Initializes the castle spawning menu at the given board position.

        :param row: The row position of the spawning menu.
        :param col: The column position of the spawning menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param spawner: The spawner object.
        """
        # Set the list of items that can be spawned
        spawn_list: list[str] = constant.CASTLE_SPAWN_LIST

        # Set the spawner object
        self.spawner: "Unit" = spawner

        # Initialize the parent SpawningMenu class
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self) -> str:
        """
        Returns a string representation of the castle menu.

        :return: The string representation of the castle menu.
        """
        return "castle"


class BarracksMenu(SpawningMenu):
    """
    Represents a spawning menu for the barracks in the game with various attributes and methods.
    """

    def __init__(
        self, row: int, col: int, win: pygame.Surface, engine: "Engine", spawner: "Unit"
    ):
        """
        Initializes the barracks spawning menu at the given board position.

        :param row: The row position of the spawning menu.
        :param col: The column position of the spawning menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param spawner: The spawner object.
        """
        # Set the list of items that can be spawned
        spawn_list: list[str] = constant.BARRACKS_SPAWN_LIST

        # Set the spawner object
        self.spawner: "Unit" = spawner

        # Initialize the parent SpawningMenu class
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self) -> str:
        """
        Returns a string representation of the barracks menu.

        :return: The string representation of the barracks menu.
        """
        return "barracks"


class CircusMenu(SpawningMenu):
    """
    Represents a spawning menu for the circus in the game with various attributes and methods.
    """

    def __init__(
        self, row: int, col: int, win: pygame.Surface, engine: "Engine", spawner: "Unit"
    ):
        """
        Initializes the circus spawning menu at the given board position.

        :param row: The row position of the spawning menu.
        :param col: The column position of the spawning menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param spawner: The spawner object.
        """
        # Set the list of items that can be spawned
        spawn_list: list[str] = constant.CIRCUS_SPAWN_LIST

        # Set the spawner object
        self.spawner: "Unit" = spawner

        # Initialize the parent SpawningMenu class
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self) -> str:
        """
        Returns a string representation of the circus menu.

        :return: The string representation of the circus menu.
        """
        return "circus"


class MonkMenu(SpawningMenu):
    """
    Represents a spawning menu for the monk in the game with various attributes and methods.
    """

    def __init__(
        self, row: int, col: int, win: pygame.Surface, engine: "Engine", spawner: "Unit"
    ):
        """
        Initializes the monk spawning menu at the given board position.

        :param row: The row position of the spawning menu.
        :param col: The column position of the spawning menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param spawner: The spawner object.
        """
        # Set the list of items that can be spawned
        spawn_list: list[str] = constant.MONK_SPAWN_LIST

        # Set the spawner object
        self.spawner: "Unit" = spawner

        # Initialize the parent SpawningMenu class
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self) -> str:
        """
        Returns a string representation of the monk menu.

        :return: The string representation of the monk menu.
        """
        return "monk"


class TrapperMenu(SpawningMenu):
    """
    Represents a spawning menu for the trapper in the game with various attributes and methods.
    """

    def __init__(
        self, row: int, col: int, win: pygame.Surface, engine: "Engine", spawner: "Unit"
    ):
        """
        Initializes the trapper spawning menu at the given board position.

        :param row: The row position of the spawning menu.
        :param col: The column position of the spawning menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param spawner: The spawner object.
        """
        # Set the list of items that can be spawned
        spawn_list: list[str] = constant.TRAPPER_SPAWN_LIST

        # Set the spawner object
        self.spawner: "Unit" = spawner

        # Initialize the parent SpawningMenu class
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self) -> str:
        """
        Returns a string representation of the trapper menu.

        :return: The string representation of the trapper menu.
        """
        return "trapper"


class Contextual(Menu):
    """
    Represents a contextual menu in the game with various attributes and methods.
    """

    def __init__(
        self,
        row: int,
        col: int,
        win: pygame.Surface,
        engine: "Engine",
        menu_list: list[str],
    ):
        """
        Initializes the contextual menu at the given board position.

        :param row: The row position of the contextual menu.
        :param col: The column position of the contextual menu.
        :param win: The game window surface.
        :param engine: The game engine.
        :param menu_list: The list of menu actions.
        """
        super().__init__(win, engine)

        # Scale paper texture
        self.paper_texture: pygame.Surface = (
            self.engine.get_current_state().scale_paper_texture(self.win)
        )

        # Set the row and column positions
        self.row: int = row
        self.col: int = col

        # Set the list of actions for this menu
        self.action_list: list[str] = menu_list

        # Set font size and create font object
        self.font_size: int = round(constant.SQ_SIZE / 4)
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Render test text
        self.test_text: pygame.Surface = self.font.render("10", True, constant.RED)

        # Initialize sprite list
        self.sprite_list: list[pygame.Surface] = []

        # Get the piece occupying the current position
        self.piece: Optional["Unit"] = self.engine.get_occupying(self.row, self.col)

        # Set the color based on the current turn
        self.color: pygame.Color = constant.turn_to_color[self.engine.turn]

        # Get the decree cost
        self.cost: int = self.engine.get_decree_cost()

        # Get the current state of the engine
        self.current_state: "State" = self.engine.get_current_state()

        # Render the cost text surface
        self.cost_text_surface: pygame.Surface = self.font.render(
            str(self.cost), True, self.color
        )

        # Mark the piece as pre-selected
        self.engine.get_occupying(row, col).pre_selected = True

        # Define contextual options
        self.contextual_options: dict[str, Callable] = {
            "pray": self.engine.transfer_to_praying_state,
            "mine": self.engine.transfer_to_mining_state,
            "king": self.engine.transfer_to_surrender_state,
            "queen": self.engine.decree,
            "trade": self.engine.transfer_to_trading_state,
            "persuade": self.engine.transfer_to_persuading_state,
            "steal": self.engine.transfer_to_stealing_state,
            "build": self.engine.transfer_to_building_state,
            "ritual": self.engine.transfer_to_pre_ritual_state,
        }

        # Define requirements for each action
        standard_requirements: bool = (
            self.engine.players[self.engine.turn].can_act()
            and self.engine.get_occupying(self.row, self.col).can_act()
        )
        pray_requirements: bool = (
            standard_requirements and not self.engine.rituals_banned
        )
        half_requirements: bool = self.engine.get_occupying(
            self.row, self.col
        ).can_act()
        no_requirements: bool = True
        trade_requirements: bool = half_requirements and self.engine.can_trade()
        queen_requirements: bool = standard_requirements and self.engine.can_decree(
            self.row, self.col
        )

        self.requirements: dict[str, bool] = {
            "pray": pray_requirements,
            "mine": half_requirements,
            "king": no_requirements,
            "queen": queen_requirements,
            "trade": trade_requirements,
            "persuade": standard_requirements,
            "steal": half_requirements,
            "build": no_requirements,
            "ritual": no_requirements,
        }

        # Map icons to actions
        icon_map: dict[str, str] = {
            "king": f"{self.engine.turn}_flag",
            "queen": f"{self.engine.turn}{'_decree_u' if self.engine.rituals_banned else '_decree'}",
            "ritual": f"{self.engine.turn}_ritual",
        }
        self.sprite_list = [
            constant.CONTEXTUAL_MENU_ICONS.get(icon_map.get(item, item))
            for item in menu_list
        ]

        # Calculate menu dimensions
        self.menu_width: int = 2 * constant.CONTEXTUAL_MENU_ICON_DEFAULT_SCALE[1]
        self.menu_height: int = len(self.action_list) * constant.SQ_SIZE

        # Correct menu boundary
        self.menu_position_x: int
        self.menu_position_y: int
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        # Create menu surface
        self.menu: pygame.Surface = pygame.Surface((self.menu_width, self.menu_height))

        # Get the current player
        self.player: "Player" = self.engine.players[self.engine.turn]

        # Initialize highlight list for menu items
        self.highlight_list: list[bool] = [False] * len(self.action_list)

        # Create highlight square surface
        self.square: pygame.Surface = pygame.Surface(
            (self.menu_width, constant.SQ_SIZE)
        )
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def handle_menu_selection(self, item: str) -> bool:
        """
        Handles the selection of a menu item.

        :param item: The selected menu item.
        :return: True if the action is successfully handled, otherwise False.
        """
        if not self.requirements.get(item, False):
            return False

        self.engine.update_squares()
        squares: dict[str, list] = {
            "pray": self.piece.praying_squares_list,
            "mine": self.piece.mining_squares_list,
            "persuade": self.piece.persuader_squares_list,
            "steal": self.piece.stealing_squares_list,
        }

        # Only check squares if the action requires a square list
        if item in squares and not squares[item]:
            return False

        return self.contextual_options[item](self.row, self.col)

    def left_click(self) -> bool:
        """
        Handles the left-click action to select a menu item.

        :return: True if a menu item is successfully selected, otherwise False.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()

        self.piece.pre_selected = False

        # Return early if click is outside menu
        if not (
            self.menu_position_x <= mouse_x <= self.menu_position_x + self.menu_width
        ):
            self.current_state.revert_to_playing_state()
            return False

        # Find which menu item was clicked
        for index, y_start in enumerate(
            range(
                self.menu_position_y,
                self.menu_position_y + len(self.action_list) * constant.SQ_SIZE,
                constant.SQ_SIZE,
            )
        ):
            if y_start <= mouse_y < y_start + constant.SQ_SIZE:
                self.engine.close_menus()
                if not self.handle_menu_selection(self.action_list[index]):
                    self.current_state.revert_to_playing_state()
                return True
        return False

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        self.engine.spawning = None
        self.engine.state[-1].revert_to_playing_state()

    def draw(self) -> Tuple[int, int]:
        """
        Draws the contextual menu on the game window.

        :return: The x and y positions of the menu.
        """
        # Fill the menu with the background color
        self.menu.fill(constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.current_state.draw_paper_texture(self.menu)

        # Iterate over the action list and corresponding sprite list
        for index, (item, icon_surface) in enumerate(
            zip(self.action_list, self.sprite_list)
        ):
            # Calculate the y-position for the current item
            y_position: int = index * constant.SQ_SIZE

            # Highlight the item if it is selected
            if self.highlight_list[index]:
                self.menu.blit(self.square, (0, y_position))

            # Calculate the x and y positions to center the icon
            icon_x: int = (self.menu_width - icon_surface.get_width()) // 2
            icon_y: int = (
                y_position + (constant.SQ_SIZE - icon_surface.get_height()) // 2
            )

            # Draw the icon on the menu
            self.menu.blit(icon_surface, (icon_x, icon_y))

            # Special handling for the "queen" item
            if item == "queen":
                # Get the decree resource sprite
                resource: pygame.Surface = get_decree_resource_sprite()

                # Calculate the x and y positions for the resource sprite
                resource_x: int = self.menu_width // 6
                resource_y: int = self.menu.get_height() // 3

                # Draw the resource sprite on the menu
                self.menu.blit(resource, (resource_x, resource_y))

                # Calculate the x and y positions for the cost text
                cost_x: int = resource_x + resource.get_width() * 3 // 4
                cost_y: int = (
                    resource_y
                    + (resource.get_height() - self.cost_text_surface.get_height())
                    * 3
                    // 4
                )

                # Determine the color of the cost text based on whether the player can decree
                color: pygame.Color = (
                    constant.RED
                    if not self.engine.can_decree(self.row, self.col)
                    else self.color
                )

                # Draw the cost text on the menu
                self.menu.blit(
                    self.font.render(str(self.cost), True, color), (cost_x, cost_y)
                )

        # Draw the menu on the game window
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))

        # Return the x and y positions of the menu
        return self.menu_position_x, self.menu_position_y
