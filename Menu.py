import os
import random
from typing import Dict, List, Tuple, Optional
import typing

if typing.TYPE_CHECKING:
    from Engine import Engine
import pygame

from Tile import Tile
from Unit import *


def get_decree_resource_sprite():
    resource = list(Constant.DECREE_COST.keys())[-1]
    key = {"gold": "gold_coin", "wood": "log", "stone": "stone"}
    return Constant.MENU_ICONS[key[resource]]


def get_initial_menu_position(row, col):
    return (
        col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
        row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
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

        # Screen surface and engine
        self.win: pygame.Surface = win
        self.engine: "Engine" = engine

        # Dictionary of pieces and buildings for each color
        self.pieces: dict[str, set] = {
            "w": Constant.W_PIECES | Constant.W_BUILDINGS,
            "b": Constant.B_PIECES | Constant.B_BUILDINGS,
        }

        # Buffer to prevent menu from clipping the screen edges
        self._menu_boundary_buffer: int = 0

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
    def menu_width(self, value: int) -> None:
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
    def menu_height(self, value: int) -> None:
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
        board_width: int = Constant.BOARD_WIDTH_PX
        board_height: int = Constant.BOARD_HEIGHT_PX

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
            x = board_width - menu_width - Constant.SQ_SIZE // 2
        elif x < 0:
            x = boundary_buffer  # Prevent clipping on the left side

        # Adjust Y to keep menu within screen height
        if y + menu_height > board_height:
            y = board_height - menu_height - Constant.SQ_SIZE // 2
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
    def menu_position_x(self, value: int) -> None:
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
    def menu_position_y(self, value: int) -> None:
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
            or x >= Constant.BOARD_WIDTH_PX - 1
            or y <= 0
            or y >= Constant.BOARD_HEIGHT_PX - 1
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
        Determines the index of the ritual corresponding to the given mouse position.

        This method calculates which ritual option is selected based on the mouse position
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
        self.color: Tuple[int, int, int] = Constant.turn_to_color[self.engine.turn]

        # Set the notification message
        self.message: List[str] = Constant.NOTIFICATIONS[message]

        # Font setup
        self.font_size: int = round(Constant.SQ_SIZE * 0.3)
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Menu dimensions
        self.menu_width: int = Constant.SQ_SIZE * 3
        self.menu_height: int = Constant.SQ_SIZE + len(self.message) * Constant.SQ_SIZE
        self.y_buffer_between_messages: int = Constant.SQ_SIZE

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
        self.highlight_display_y: int = self.menu_height - Constant.SQ_SIZE
        self.square: pygame.Surface = pygame.Surface(
            (self.menu_width, Constant.SQ_SIZE)
        )
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.highlight: bool = False

    def draw(self):
        """
        Draws the notification menu on the game window.
        """
        # Fill the menu with the background color
        self.menu.fill(Constant.MENU_COLOR)

        # Initialize the vertical buffer for message rendering
        y_buffer: int = 0

        # Render each message in the notification
        for message in self.message_text_surfaces:
            text_display_x: int = self.menu_width // 2 - message.get_width() // 2
            self.menu.blit(message, (text_display_x, y_buffer))
            y_buffer += self.y_buffer_between_messages

        # Highlight the "OK" button if needed
        if self.highlight:
            self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
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
        menu_above_ok_button: int = len(self.message) * round(Constant.SQ_SIZE * 0.8)

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
        menu_above_ok_button: int = len(self.message) * round(Constant.SQ_SIZE * 0.8)

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
        self.ritual_list: list = ritual_list

        # Set the row and column positions
        self.row: int = row
        self.col: int = col

        # Initialize the parent Menu class
        super().__init__(win, engine)

        # Font setup
        self.font_size: int = round(Constant.SQ_SIZE / 2)
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Get the current player
        self.player = self.engine.players[self.engine.turn]

        # Initial menu position
        self.initial_menu_position: Tuple[int, int] = (
            self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
            self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
        )

        # Buffers for spacing
        self.vertical_buffer_between_pieces: int = Constant.SQ_SIZE // 6
        self.horizontal_buffer_between_costs: int = round(Constant.SQ_SIZE * 1.3)

        # Bar dimensions
        self.bar_width: int = Constant.IMAGES["prayer_bar"].get_width()
        self.bar_height: int = Constant.IMAGES["prayer_bar"].get_height()
        self.bar_end_width: int = Constant.IMAGES["prayer_bar_end"].get_width()

        # Ritual dimensions
        self.rituals = Constant.PRAYER_RITUALS
        self.ritual_width: int = self.rituals["w_gold_general"].get_width()
        self.ritual_height: int = self.rituals["w_gold_general"].get_height()

        # Gold icon setup
        self.gold_icon = Constant.MENU_ICONS["gold_coin"]
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
        self.ritual_highlight_list: List[bool] = []
        self.square: pygame.Surface = pygame.Surface(
            (self.menu_width, round(1 / len(self.ritual_list) * self.menu_height))
        )
        self.available_menu_space_for_prayer_bar: int = (
            self.menu_width - self.ritual_width
        )

        # Initialize ritual highlight list
        for _ in self.ritual_list:
            self.ritual_highlight_list.append(False)

    def full_length_of_prayer_bar(self, length_of_ritual: int) -> int:
        """
        Calculates the full length of the prayer bar for a given ritual length.

        :param length_of_ritual: The length of the ritual.
        :return: The full length of the prayer bar.
        """
        return self.bar_end_width * length_of_ritual + self.bar_width

    def mouse_move(self):
        """
        Handles mouse movement over the ritual menu. It highlights the rituals based on the mouse position.

        :return: None
        """
        pos = pygame.mouse.get_pos()
        index = self.get_index_selected(pos, self.ritual_list)

        if index is not None:
            # Highlight only the ritual at `index`
            self.ritual_highlight_list = [
                i == index for i in range(len(self.ritual_highlight_list))
            ]
        else:
            # Un-highlight all rituals
            self.ritual_highlight_list = [False] * len(self.ritual_highlight_list)

    def left_click(self) -> bool:
        """
        Handles the left-click action for selecting and casting a ritual.

        :return: True if the ritual is successfully cast, otherwise reverts to the playing state.
        """
        # Determine the ritual being clicked
        self.casting: Optional[str] = self.get_option_selected(self.ritual_list)

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
        self.menu.fill(Constant.MENU_COLOR)

        # Draw paper texture
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Highlight selected rituals
        highlight_indices: List[int] = [
            i for i, highlighted in enumerate(self.ritual_highlight_list) if highlighted
        ]
        for index in highlight_indices:
            start_y: float = (index / len(self.ritual_list)) * self.menu_height
            self.menu.blit(self.square, (0, start_y))

        # Set highlight properties once (instead of inside a loop)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Initialize buffers for drawing rituals and costs
        y_buffer_ritual: int = 0
        y_buffer_prayer: int = self.y_buffer

        # Cache values to avoid redundant dictionary lookups
        turn: int = self.engine.turn
        rituals: Dict[str, pygame.Surface] = self.rituals
        prayer_costs: Dict[str, Dict[str, int]] = Constant.PRAYER_COSTS
        cost_type: str = self.cost_type
        player_gold: int = self.player.gold

        for ritual in self.ritual_list:
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
                        Constant.IMAGES["prayer_bar"], (bar_edge, y_buffer_prayer)
                    )
                    for z in range(prayer_cost):
                        self.menu.blit(
                            Constant.IMAGES["prayer_bar_end"],
                            (bar_end_edge + self.bar_end_width * z, y_buffer_prayer),
                        )

                    y_buffer_prayer += self.y_buffer + self.ritual_height // 2

            elif cost_type == "gold" and cost_data["gold"] > 0:
                gold_cost: int = cost_data["gold"]
                gold_color: Tuple[int, int, int] = (
                    Constant.turn_to_color[turn]
                    if player_gold >= gold_cost
                    else Constant.RED
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
        self.resource_list: List[str] = resource_list
        super().__init__(win, engine)
        self.trade_arrow: pygame.Surface = trade_arrow
        self.amounts: Dict[str, int] = amounts
        self.player = self.engine.players[self.engine.turn]
        self.give_image: pygame.Surface = Constant.IMAGES["give"]
        self.selected: Optional[str] = None
        self.horizontal_buffer: int = Constant.SQ_SIZE // 2
        self.vertical_buffer_between_pieces: int = Constant.SQ_SIZE // 4
        self.font_size: int = round(Constant.SQ_SIZE / 2)
        self.font: pygame.font.Font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.font_color: Tuple[int, int, int] = Constant.turn_to_color[self.engine.turn]
        self.resource_height: int = Constant.IMAGES["gold_coin"].get_width()
        self.resource_width: int = Constant.IMAGES["gold_coin"].get_height()
        self.menu_width: int = (
            self.resource_width
            + self.horizontal_buffer
            + self.resource_width
            + Constant.SQ_SIZE
        )
        self.menu_height: int = len(self.resource_list) * (
            self.resource_height + self.vertical_buffer_between_pieces
        )
        self.menu: pygame.Surface = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture: pygame.Surface = (
            self.engine.get_current_state().scale_paper_texture(self.menu)
        )
        self.initial_menu_position: Tuple[int, int] = (
            self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
            self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
        )
        self.menu_position_x: int
        self.menu_position_y: int
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu_boundary_buffer_y: int = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x: int = self.menu_width + self.menu_boundary_buffer
        self.spawn_highlight_list: List[bool] = []
        self.square: pygame.Surface = pygame.Surface(
            (self.menu_width, round(1 / len(self.resource_list) * self.menu_height))
        )
        for _ in self.resource_list:
            self.spawn_highlight_list.append(False)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def mouse_move(self):
        """
        Handles mouse movement to highlight items in the resource list
        based on the mouse's vertical position within the menu.

        The method checks if the mouse is within the bounds of the menu,
        and highlights the corresponding item in the resource list if so.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is within the horizontal bounds of the menu
        if mouse_x + (self.menu_width // 3) < self.menu_position_x:
            # If the mouse is outside the bounds, reset all highlights and cursor
            if any(self.spawn_highlight_list):
                self.spawn_highlight_list = [False] * len(self.spawn_highlight_list)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return

        # Precompute the item height ratio to avoid repeated division
        item_height_ratio = 1 / len(self.resource_list) * self.menu_height

        # Track the index that should be highlighted
        highlighted_index = None

        # Iterate through the resource list to find which item is hovered over
        for index, _ in enumerate(self.resource_list):
            # Calculate the start and end Y-coordinates of the current menu item
            item_start_y = index * item_height_ratio + self.menu_position_y
            item_end_y = (index + 1) * item_height_ratio + self.menu_position_y

            # Check if the mouse's Y-coordinate falls within the current item's bounds
            if round(item_start_y) <= mouse_y <= round(item_end_y):
                highlighted_index = index
                break  # Stop checking once a highlight is found

        # Update highlighting only if necessary
        if highlighted_index is not None:
            # Only update if the item is not already highlighted
            if not self.spawn_highlight_list[highlighted_index]:
                self.spawn_highlight_list = [
                    i == highlighted_index
                    for i in range(len(self.spawn_highlight_list))
                ]
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            # Only reset if something was highlighted before
            if any(self.spawn_highlight_list):
                self.spawn_highlight_list = [False] * len(self.spawn_highlight_list)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self) -> Tuple[int, int]:
        """
        Draws the trader menu on the game window.

        :return: The x and y positions of the menu.
        """
        # Fill the menu with the background color
        self.menu.fill(Constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Highlight selected resources
        for index in range(len(self.resource_list)):
            start_y: float = (index / len(self.resource_list)) * self.menu_height
            if self.spawn_highlight_list[index]:
                self.menu.blit(self.square, (0, start_y))

        # Initialize buffer for drawing resources and amounts
        y_buffer: int = 0

        # Draw each resource and its amount
        for resource in self.resource_list:
            self.menu.blit(
                Constant.IMAGES[resource],
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

            y_buffer += self.menu_height // len(self.resource_list)

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
        self.trade_arrow: pygame.Surface = Constant.IMAGES["give"]

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
        self.selected: Optional[str] = self.get_index_selected(
            pygame.mouse.get_pos(), self.resource_list
        )

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
            row, col = Constant.convert_pos(pygame.mouse.get_pos())

            # Create and add a new ReceiveMenu
            menu = ReceiveMenu(
                row, col, self.win, self.engine, resource_list, amount_given
            )
            self.engine.menus.append(menu)

            return True

        return False


class ReceiveMenu(TraderMenu):
    """
    Represents a receive menu in the game with various attributes and methods.
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
        Initializes the receive menu at the given board position.

        :param row: The row position of the receive menu.
        :param col: The column position of the receive menu.
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
        self.trade_arrow: pygame.Surface = Constant.IMAGES["receive"]
        super().__init__(
            row, col, win, engine, resource_list, self.amounts, self.trade_arrow
        )

    def left_click(self) -> bool:
        """
        Handles the left-click action for selecting and receiving a resource.

        :return: True if a resource is successfully received, otherwise False.
        """
        # Determine the selected resource based on the mouse position
        self.selected: Optional[str] = self.get_index_selected(
            pygame.mouse.get_pos(), self.resource_list
        )

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
        row, col = Constant.convert_pos(pygame.mouse.get_pos())

        # Create and display a new trader menu
        self.engine.create_trader_menu(row, col, False)


class StealingMenu(Menu):
    """
    Represents the menu for stealing resources from a tile on the game board.

    This menu handles displaying the resources available for stealing and updating the game state.
    """

    def __init__(
        self, row: int, col: int, win: pygame.Surface, engine: "Engine"
    ) -> None:
        """
        Initializes the StealingMenu.

        :param row: The row position of the menu.
        :param col: The column position of the menu.
        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        self.row = row
        self.col = col
        self.action_list = ["log", "gold_coin", "stone"]
        self.key = {"log": "wood", "gold_coin": "gold", "stone": "stone"}

        # Initialize the type of entity being stolen from
        self.type_stolen_from = None

        # Call the parent class constructor
        super().__init__(win, engine)

        # Determine the type of entity occupying the tile
        piece = self.engine.get_occupying(row, col)

        # Create a mapping of classes to type strings
        entity_map = {
            Trader: "trader",  # Trader corresponds to "trader"
            Piece: "piece",  # Any Piece that isn't a Trader corresponds to "piece"
            Building: "building",  # Building corresponds to "building"
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
        self.horizontal_buffer = Constant.SQ_SIZE

        # Set the vertical buffer between pieces to one-fourth the size of a square
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 4

        # Set the font size as half of the square size, rounded for better visual appearance
        self.font_size = round(Constant.SQ_SIZE / 2)

        # Create the font object using the font file "font.ttf" and the calculated font size
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Set the font color based on the current player's turn using a predefined color mapping
        self.font_color = Constant.turn_to_color[self.engine.turn]

        # Set the resource height as the width of the gold coin image
        self.resource_height = Constant.IMAGES["gold_coin"].get_width()

        # Set the resource width as the height of the gold coin image
        self.resource_width = Constant.IMAGES["gold_coin"].get_height()

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
            self.col * Constant.SQ_SIZE
            + Constant.SQ_SIZE // 2,  # X position (centered within the column)
            self.row * Constant.SQ_SIZE
            + Constant.SQ_SIZE // 2,  # Y position (centered within the row)
        )

        # Correct the menu's position based on boundary conditions (e.g., screen edges or available space)
        # The returned position ensures that the menu stays within the boundaries
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        # Set the vertical boundary buffer, which is the height of the menu plus the menu boundary buffer
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer

        # Set the horizontal boundary buffer, which is the width of the menu plus the menu boundary buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer

        # Initialize highlight list for spawn items
        self.spawn_highlight_list = []
        self.square = pygame.Surface(
            (self.menu_width, round(1 / len(self.action_list) * self.menu_height))
        )
        for _ in self.action_list:
            self.spawn_highlight_list.append(False)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def draw(self) -> Tuple[int, int]:
        """
        Draws the stealing menu on the game window.

        :return: The x and y position of the menu.
        """
        self.menu.fill(Constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Highlight selected items
        for x in range(len(self.action_list)):
            a = x / len(self.action_list)
            b = a * self.menu_height
            if self.spawn_highlight_list[x]:
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
                Constant.IMAGES[p], (icon_x, y_buffer + self.menu_height // 16)
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
        stolen_resource: Optional[str] = self.get_index_selected(
            pygame.mouse.get_pos(), self.action_list
        )

        if stolen_resource:
            # Get the amount of the selected resource to steal
            amount: int = self.amounts[stolen_resource]

            # Clear the current menus
            self.engine.menus = []

            # Set the stealing state with the selected resource and amount
            self.engine.stealing = [self.key[stolen_resource], amount]

            return True
        else:
            # Reset the stealing state and revert to the playing state
            self.engine.stealing = None
            return self.engine.state[-1].revert_to_playing_state()

    def right_click(self):
        """
        Handles the right-click action to revert to the playing state.
        """
        # Revert to the playing state
        self.engine.get_current_state().revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement to highlight items in the resource list
        based on the mouse's vertical position within the menu.

        The method checks if the mouse is within the bounds of the menu,
        and highlights the corresponding item in the resource list if so.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is within the horizontal bounds of the menu
        if self.menu_position_x < mouse_x + (self.menu_width // 3):
            # Iterate through the resource list to find which item is being hovered over
            for index in range(len(self.action_list)):
                # Calculate the top and bottom y-coordinates of the current menu item
                item_start_y = (
                    index / len(self.action_list)
                ) * self.menu_height + self.menu_position_y
                item_end_y = (
                    (index + 1) / len(self.action_list)
                ) * self.menu_height + self.menu_position_y

                # Check if the mouse's y-coordinate is within the vertical bounds of the item
                if round(item_start_y) <= mouse_y <= round(item_end_y):
                    # Highlight the item at the current index
                    self.spawn_highlight_list[index] = True

                    # Set cursor to hand
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

                    # De-highlight other items in the list
                    for i in range(len(self.spawn_highlight_list)):
                        if i != index:
                            self.spawn_highlight_list[i] = False
        else:
            # If the mouse is outside the menu bounds, remove all highlights
            self.spawn_highlight_list = [False] * len(self.spawn_highlight_list)
            # Set cursor to hand
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


class ResourceMenu(Menu):

    def __init__(self, row, col, win, engine):
        self.row = row
        self.col = col
        rand = str(random.randint(1, 4))
        self.spawn_list = ["gold_tile_1", "quarry_1", "tree_tile_" + rand]
        super().__init__(win, engine)
        self.horizontal_buffer = Constant.SQ_SIZE
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 4
        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.resource_height = Constant.RESOURCES["gold_tile_1"].get_width()
        self.resource_width = Constant.RESOURCES["gold_tile_1"].get_height()
        self.menu_width = self.resource_width + self.horizontal_buffer
        self.menu_height = len(self.spawn_list) * (
            self.resource_height + self.vertical_buffer_between_pieces
        )
        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(
            self.menu
        )
        self.initial_menu_position = (
            self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
            self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
        )
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.spawn_highlight_list = []
        self.square = pygame.Surface(
            (self.menu_width, round(1 / len(self.spawn_list) * self.menu_height))
        )
        for _ in self.spawn_list:
            self.spawn_highlight_list.append(False)

    def resource_selected(self):
        pos = pygame.mouse.get_pos()
        mp = self.menu_position_y
        length = len(self.spawn_list)
        mh = self.menu_height

        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.spawn_list)):
                a = x / length
                b = a * mh
                c = b + mp
                d = (x + 1) / length
                e = d * mh
                f = e + mp
                r = range(round(c), round(f))
                if pos[1] in r:
                    return self.spawn_list[x]

    def left_click(self):
        self.engine.ritual_summon_resource = None
        self.spawning = self.resource_selected()
        if self.spawning is not None:
            self.engine.menus = []
            self.engine.ritual_summon_resource = self.spawning
            return True
        else:
            self.engine.ritual_summon_resource = None
            return self.engine.state[-1].revert_to_playing_state()

    def right_click(self):
        self.engine.ritual_summon_resource = None
        self.engine.state[-1].revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement to highlight items in the resource list
        based on the mouse's vertical position within the menu.

        The method checks if the mouse is within the bounds of the menu,
        and highlights the corresponding item in the resource list if so.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is within the horizontal bounds of the menu
        if self.menu_position_x < mouse_x + (self.menu_width // 3):
            # Iterate through the resource list to find which item is being hovered over
            for index in range(len(self.spawn_list)):
                # Calculate the top and bottom y-coordinates of the current menu item
                item_start_y = (
                    index / len(self.spawn_list)
                ) * self.menu_height + self.menu_position_y
                item_end_y = (
                    (index + 1) / len(self.spawn_list)
                ) * self.menu_height + self.menu_position_y

                # Check if the mouse's y-coordinate is within the vertical bounds of the item
                if round(item_start_y) <= mouse_y <= round(item_end_y):
                    # Highlight the item at the current index
                    self.spawn_highlight_list[index] = True

                    # Set cursor to hand
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

                    # De-highlight other items in the list
                    for i in range(len(self.spawn_highlight_list)):
                        if i != index:
                            self.spawn_highlight_list[i] = False
        else:
            # If the mouse is outside the menu bounds, remove all highlights
            self.spawn_highlight_list = [False] * len(self.spawn_highlight_list)
            # Set cursor to hand
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        for x in range(len(self.spawn_list)):
            a = x / len(self.spawn_list)
            b = a * self.menu_height
            if self.spawn_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        y_buffer = 0
        for p in self.spawn_list:
            self.menu.blit(
                Constant.RESOURCES[p], (self.horizontal_buffer // 2, y_buffer)
            )
            y_buffer += self.menu_height // len(self.spawn_list)

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class SpawningMenu(Menu):
    def __init__(self, row, col, win, engine, spawn_list, spawner):
        self.row = row
        self.col = col
        self.spawn_list = spawn_list
        self.spawner = spawner
        self.spawning = None

        super().__init__(win, engine)
        self.horizontal_buffer_between_costs = round(Constant.SQ_SIZE * 1.3)
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 4
        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.test_text = self.font.render("10", True, Constant.RED)
        self.menu_width = Constant.SQ_SIZE + (
            3 * self.horizontal_buffer_between_costs + self.test_text.get_width()
        )
        self.menu_height = len(spawn_list) * Constant.SPAWNING_MENU_HEIGHT_BUFFER + (
            self.vertical_buffer_between_pieces
        )
        self.initial_menu_position = (
            self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
            self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
        )
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(
            self.menu
        )
        self.piece_x = self.vertical_buffer_between_pieces
        self.log_x = self.piece_x + self.horizontal_buffer_between_costs
        self.gold_x = self.log_x + self.horizontal_buffer_between_costs
        self.stone_x = self.gold_x + self.horizontal_buffer_between_costs
        self.player = self.engine.players[self.engine.turn]
        self.spawn_highlight_list = []
        self.square = pygame.Surface(
            (self.menu_width, round(1 / len(self.spawn_list) * self.menu_height))
        )
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        for _ in self.spawn_list:
            self.spawn_highlight_list.append(False)

    def piece_spawned(self):
        pos = pygame.mouse.get_pos()
        mp = self.menu_position_y
        length = len(self.spawn_list)
        mh = self.menu_height

        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.spawn_list)):
                a = x / length
                b = a * mh
                c = b + mp
                d = (x + 1) / length
                e = d * mh
                f = e + mp
                r = range(round(c), round(f))
                if pos[1] in r:
                    return self.spawn_list[x]

    def left_click(self):
        self.engine.spawning = None
        self.spawning = self.piece_spawned()
        if not self.spawning or not self.engine.is_legal_spawn(
            self.spawning, self.spawner
        ):
            self.engine.spawning = None
            pos = pygame.mouse.get_pos()
            row, col = Constant.convert_pos(pos)
            self.engine.state[-1].revert_to_playing_state()
            self.engine.create_popup_menu(row, col)
            return True

        else:
            self.engine.menus = []
            self.engine.get_occupying(self.spawner.row, self.spawner.col).purchasing = (
                True
            )
            self.engine.get_occupying(
                self.spawner.row, self.spawner.col
            ).pre_selected = False
            return self.engine.transfer_to_spawning_state(self.spawning)

    def right_click(self):
        self.engine.spawning = None
        self.engine.state[-1].revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement to highlight items in the resource list
        based on the mouse's vertical position within the menu.

        The method checks if the mouse is within the bounds of the menu,
        and highlights the corresponding item in the resource list if so.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is within the horizontal bounds of the menu
        if self.menu_position_x < mouse_x + (self.menu_width // 3):
            # Iterate through the resource list to find which item is being hovered over
            for index in range(len(self.spawn_list)):
                # Calculate the top and bottom y-coordinates of the current menu item
                item_start_y = (
                    index / len(self.spawn_list)
                ) * self.menu_height + self.menu_position_y
                item_end_y = (
                    (index + 1) / len(self.spawn_list)
                ) * self.menu_height + self.menu_position_y

                # Check if the mouse's y-coordinate is within the vertical bounds of the item
                if round(item_start_y) <= mouse_y <= round(item_end_y):
                    # Highlight the item at the current index
                    self.spawn_highlight_list[index] = True

                    # Set cursor to hand
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

                    # De-highlight other items in the list
                    for i in range(len(self.spawn_highlight_list)):
                        if i != index:
                            self.spawn_highlight_list[i] = False
        else:
            # If the mouse is outside the menu bounds, remove all highlights
            self.spawn_highlight_list = [False] * len(self.spawn_highlight_list)
            # Set cursor to hand
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        y_buffer = self.vertical_buffer_between_pieces
        for x in range(len(self.spawn_list)):
            a = x / len(self.spawn_list)
            b = a * self.menu_height
            if self.spawn_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        for p in self.spawn_list:
            piece_cost = Constant.PIECE_COSTS[p]

            if p == "quarry_1":
                piece = "quarry_1"
            else:
                piece = self.engine.turn + "_" + p

            # Log Cost
            if piece_cost["log"] != 0:
                if self.player.wood >= piece_cost["log"]:
                    color = Constant.turn_to_color[self.engine.turn]
                else:
                    color = Constant.RED
                log_cost = self.font.render(str(piece_cost["log"]), True, color)
                self.menu.blit(
                    Constant.MENU_ICONS["log"],
                    (self.log_x, y_buffer + Constant.SQ_SIZE // 4),
                )
                self.menu.blit(
                    log_cost,
                    (
                        (self.log_x + (Constant.SQ_SIZE // 1.5)),
                        (y_buffer + (Constant.SQ_SIZE // 6)),
                    ),
                )

            # Gold Cost
            if piece_cost["gold"] != 0:
                if self.player.gold >= piece_cost["gold"]:
                    color = Constant.turn_to_color[self.engine.turn]
                else:
                    color = Constant.RED
                gold_cost = self.font.render(str(piece_cost["gold"]), True, color)
                self.menu.blit(
                    Constant.MENU_ICONS["gold_coin"],
                    (self.gold_x, y_buffer + Constant.SQ_SIZE // 4),
                )
                self.menu.blit(
                    gold_cost,
                    (
                        (self.gold_x + (Constant.SQ_SIZE // 1.5)),
                        (y_buffer + (Constant.SQ_SIZE // 6)),
                    ),
                )

            # Stone Cost
            if piece_cost["stone"] != 0:
                if self.player.stone >= piece_cost["stone"]:
                    color = Constant.turn_to_color[self.engine.turn]
                else:
                    color = Constant.RED
                stone_cost = self.font.render(str(piece_cost["stone"]), True, color)
                self.menu.blit(
                    Constant.MENU_ICONS["stone"],
                    (self.stone_x, y_buffer + Constant.SQ_SIZE // 4),
                )
                self.menu.blit(
                    stone_cost,
                    (
                        (self.stone_x + (Constant.SQ_SIZE // 1.5)),
                        (y_buffer + (Constant.SQ_SIZE // 6)),
                    ),
                )

            # Menu
            if p == "quarry_1":
                self.menu.blit(Constant.RESOURCES[p], (self.piece_x, y_buffer))
            else:
                self.menu.blit(
                    self.pieces[self.engine.turn][piece], (self.piece_x, y_buffer)
                )

            y_buffer += Constant.SPAWNING_MENU_HEIGHT_BUFFER

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class StableMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.STABLE_SPAWN_LIST
        self.spawner = spawner
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return "stable"


class FortressMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.FORTRESS_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return "fortress"


class BuilderMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.BUILDER_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return "builder"


class CastleMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.CASTLE_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return "castle"


class BarracksMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.BARRACKS_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return "barracks"


class CircusMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.CIRCUS_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return "circus"


class MonkMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.MONK_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return "monk"


class TrapperMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.TRAPPER_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return "trapper"


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
        self.small_font_size = round(Constant.SQ_SIZE * 0.5)
        self.large_font_size = round(Constant.SQ_SIZE * 1.6)

        # Initialize Fonts
        self.large_font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.large_font_size
        )
        self.small_font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.small_font_size
        )

        # Boiler Plate
        try:
            self.color = Constant.turn_to_color[self.engine.turn]
            self.player = self.engine.players[self.engine.turn]
        except KeyError:
            self.color = pygame.Color("black")
            self.player = None
        self.resources = {
            "wood": Constant.MENU_ICONS["log"],
            "gold": Constant.MENU_ICONS["gold_coin"],
            "stone": Constant.MENU_ICONS["stone"],
        }
        self.icons = (
            Constant.W_PIECES
            | Constant.W_BUILDINGS
            | Constant.B_PIECES
            | Constant.B_BUILDINGS
            | Constant.PRAYER_RITUALS
            | Constant.RESOURCES
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
            Constant.DARK_SQUARE_COLOR,
            Constant.LIGHT_SQUARE_COLOR,
        ]
        self.color_key: Dict[int, str] = {0: "dark", 1: "light"}

        # Create a copy of the engine's board state
        self.board_copy = self.engine.board

        # Define font size and load the font
        self.small_font_size: int = round(Constant.SQ_SIZE * (1 / 3))
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
            (self.cols * Constant.SQ_SIZE, self.rows * Constant.SQ_SIZE)
        )

        # Define board positioning on the window
        self.board_x: int = self.window_width // 40
        self.board_y: int = (self.window_height - self.board_surface.get_height()) // 2

        # Load description text
        self.description_text: List[str] = Constant.DESCRIPTIONS[str(self)]
        self.description_text_surfs: List[pygame.Surface] = []

        # Render description text as pygame surfaces
        for line in self.description_text:
            text_surf = self.small_font.render(line, True, self.color)
            self.description_text_surfs.append(text_surf)

        # Get dimensions of description text
        self.description_text_width: int = self.description_text_surfs[0].get_width()
        self.description_text_height: int = self.description_text_surfs[0].get_height()

        # Load images for prayer bar display
        self.prayer_bar_end: pygame.Surface = Constant.IMAGES["prayer_bar_end"]
        self.prayer_bar: pygame.Surface = Constant.IMAGES["prayer_bar"]
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
            self.cost = Constant.PRAYER_COSTS[self.selected]["prayer"]
            self.type = "ritual"
        except KeyError:
            self.cost = Constant.PIECE_COSTS[self.selected]
            self.type = "piece"

        # Adjust layout for piece selection
        self.move_offset: int = 0
        if self.type == "piece":
            self.move_offset = self.window_width // 8

        # Define layout calculations for cost display
        self.cost_display_y: int = (
            self.window_height // 2 - self.resources["wood"].get_height() // 2
        )
        self.x_buffer_between_costs: int = round(Constant.SQ_SIZE * 1.5)
        self.description_text_y: int = (
            self.cost_display_y + self.description_text_height
        )
        self.cost_display_x: int = 0

        # Determine cost display positioning based on type
        if self.type == "piece":
            count = sum(
                1
                for cost in Constant.PIECE_COSTS[self.selected]
                if Constant.PIECE_COSTS[self.selected][cost] != 0
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
        self.win.fill(Constant.MENU_COLOR)

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
        self.text_box.fill(Constant.MENU_COLOR)
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
        resource_tiles = [f"tree_tile_{i}" for i in range(1, 9)] + [
            "gold_tile_1",
            "quarry_1",
        ]
        contextual_options = {
            "pray": ["monolith, prayer_stone"],
            "mine": resource_tiles,
            "king": list(),
            "queen": list(),
            "trade": list(),
            "persuade": ["enemy"],
            "steal": ["enemy"],
            "build": list(),
            "ritual": list(),
        }
        row, col = 3, 3
        self.board[row][col].set_occupying(
            self.engine.PIECES[self.selected](row, col, color)
        )
        self.board[row][col].get_occupying().update_move_squares(self.engine)
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
                        getattr(self.player, Constant.RESOURCE_KEY[resource])
                        >= self.cost[resource]
                    ):
                        color = self.color
                    else:
                        color = Constant.RED
                except AttributeError:
                    color = self.color
                text_surf = self.small_font.render(
                    " " + str(self.cost[resource]), True, color
                )
                resource_position = (cost_x, self.cost_display_y)

                self.win.blit(
                    self.resources[Constant.RESOURCE_KEY[resource]], resource_position
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
                rect_size = (Constant.SQ_SIZE, Constant.SQ_SIZE)

                # Calculate position for the square, with the offset
                x = c * Constant.SQ_SIZE
                y = r * Constant.SQ_SIZE

                # Draw the square
                pygame.draw.rect(
                    self.board_surface,
                    color,
                    pygame.Rect(x, y, rect_size[0], rect_size[1]),
                )

                # Draw the tile using blend mode (avoid re-evaluating color calculation)
                tile_color = self.color_key[(r + c) % 2]
                self.board_surface.blit(
                    Constant.BOARD_TILES[tile_color][self.board[r][c].index],
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


class CostMenu(Encyclopedia):
    def __init__(self, win, engine, spawn_list):
        super().__init__(win, engine)

        self.board_copy = None
        self.spawn_list = spawn_list
        self.win = win
        self.engine = engine
        self.highlight_list = []
        self.column_list = []

        # Determine positions
        self.x_buffer_between_columns = Constant.SQ_SIZE // 3

        self.column_width = round(Constant.SQ_SIZE * 1.5)

        self.y_buffer_between_costs = Constant.SQ_SIZE // 2

        self.x_buffer_between_costs = self.x_buffer_between_columns // 3

        resource_height = self.resources[Constant.RESOURCE_KEY["stone"]].get_height()

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
        self.highlight.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.highlight.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

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
        self.win.fill(Constant.MENU_COLOR)
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
            cost = Constant.PIECE_COSTS[piece]
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
                resource_sprite = self.resources[Constant.RESOURCE_KEY[resource]]
                if cost[resource] != 0:
                    try:
                        if (
                            getattr(self.player, Constant.RESOURCE_KEY[resource])
                            >= cost[resource]
                        ):
                            color = self.color
                        else:
                            color = Constant.RED
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


class Master(CostMenu):
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


class BuilderCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.BUILDER_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "builder"


class CastleCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.CASTLE_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "castle"


class StableCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.STABLE_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "stable"


class CircusCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.CIRCUS_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "circus"


class MonkCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.MONK_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def left_click(self):
        piece_selected = self.piece_selected()
        if piece_selected is not None:
            menu = self.menu_key[piece_selected](self.win, self.engine)
            self.engine.menus.append(menu)
            return True

    def __repr__(self):
        return "monk"


class FortressCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.FORTRESS_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "fortress"


class BarracksCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.BARRACKS_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "barracks"


class RitualCosts(CostMenu):
    def __init__(self, win, engine, spawn_list):
        super().__init__(win, engine, spawn_list)
        self.rituals = Constant.PRAYER_RITUALS
        self.ritual_width = self.rituals["w_swap"].get_width()
        self.ritual_height = self.rituals["w_swap"].get_height()

        self.column_width = self.ritual_width

        total_height_of_cost_column = (
            self.y_buffer_between_costs * 3 + self.x_buffer_between_columns
        )
        self.highlight_width = self.ritual_width
        self.highlight_dimensions = (self.highlight_width, total_height_of_cost_column)

        self.square = pygame.Surface(self.highlight_dimensions)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.prayer_bar_end = Constant.IMAGES["prayer_bar_end"]
        self.prayer_bar = Constant.IMAGES["prayer_bar"]

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
        self.win.fill(Constant.MENU_COLOR)
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
            cost = Constant.PRAYER_COSTS[p]
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
        spawn_list = Constant.PRAYER_STONE_RITUALS
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "prayer_stone"


class MonolithCosts(RitualCosts):
    def __init__(self, win, engine):
        spawn_list = Constant.MONOLITH_RITUALS
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return "monolith"


class Contextual(Menu):
    def __init__(self, row, col, win, engine, menu_list):
        super().__init__(win, engine)
        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(
            self.win
        )
        self.menu_list = menu_list
        self.row = row
        self.col = col
        self.font_size = round(Constant.SQ_SIZE / 4)
        self.font = pygame.font.Font(
            os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.test_text = self.font.render("10", True, Constant.RED)
        self.sprite_list = list()
        self.piece = self.engine.get_occupying(self.row, self.col)
        self.color = Constant.turn_to_color[self.engine.turn]
        self.cost = self.engine.get_decree_cost()
        self.cost_text_surface = self.font.render(str(self.cost), True, self.color)
        self.engine.get_occupying(row, col).pre_selected = True
        self.contextual_options = {
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
        standard_requirements = (
            self.engine.players[self.engine.turn].can_act()
            and self.engine.get_occupying(self.row, self.col).can_act()
        )
        pray_requirements = standard_requirements and not self.engine.rituals_banned
        half_requirements = self.engine.get_occupying(self.row, self.col).can_act()
        no_requirements = True
        trade_requirements = half_requirements and self.engine.can_trade()
        queen_requirements = standard_requirements and self.engine.can_decree(
            self.row, self.col
        )
        self.requirements = {
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
        for item in menu_list:
            if item == "king":
                icon_key = f"{self.engine.turn}_flag"
            elif item == "queen":
                image_suffix = "_decree_u" if self.engine.rituals_banned else "_decree"
                icon_key = f"{self.engine.turn}{image_suffix}"
            elif item == "ritual":
                icon_key = f"{self.engine.turn}_{item}"
            else:
                icon_key = item
            self.sprite_list.append(Constant.CONTEXTUAL_MENU_ICONS[icon_key])

        self.menu_width = 2 * Constant.CONTEXTUAL_MENU_ICON_DEFAULT_SCALE[1]
        self.menu_height = (
            len(self.menu_list) * Constant.SQ_SIZE
        )  # **Exact height based on list length**

        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu = pygame.Surface((self.menu_width, self.menu_height))

        self.player = self.engine.players[self.engine.turn]
        self.item_highlight_list = [False] * len(self.menu_list)

        # Each highlightable section is now exactly SQ_SIZE tall
        self.square = pygame.Surface((self.menu_width, Constant.SQ_SIZE))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def handle_menu_selection(self, index, item):
        if not self.requirements[item]:
            return False
        try:
            self.engine.update_squares()
            squares = {
                "pray": self.piece.praying_squares_list,
                "mine": self.piece.mining_squares_list,
                "persuade": self.piece.persuader_squares_list,
                "steal": self.piece.stealing_squares_list,
            }
            if not squares[item]:
                return False
        except KeyError as e:
            pass
        except TypeError as e:
            pass

        return self.contextual_options[item](self.row, self.col)

    def left_click(self):
        pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = pos

        # Each section is now exactly one SQ_SIZE tall
        item_height = Constant.SQ_SIZE

        self.engine.get_occupying(self.row, self.col).pre_selected = False

        # Check if the click is inside the menu’s X boundaries
        if not (
            self.menu_position_x <= mouse_x <= self.menu_position_x + self.menu_width
        ):
            return  # Click is outside the menu

        # Check which highlight section the click is in
        for index in range(len(self.menu_list)):
            y_start = self.menu_position_y + (index * item_height)
            y_end = y_start + item_height

            if y_start <= mouse_y <= y_end:
                self.engine.close_menus()
                # Click is inside this highlight section
                # Perform action for the selected menu item
                if not self.handle_menu_selection(index, self.menu_list[index]):
                    self.engine.reset_selected()
                    self.engine.close_menus()
                    self.engine.state[-1].reset_dragging_piece()
                    return True
                else:
                    return True

    def right_click(self):
        self.engine.spawning = None
        self.engine.state[-1].revert_to_playing_state()

    def mouse_move(self):
        """
        Handles mouse movement over the menu area. It highlights the menu items based on the
        mouse position and updates the mouse cursor to a hand when hovering over an item.
        """
        # Get the current mouse position
        pos = pygame.mouse.get_pos()

        # Check if the mouse is within the menu area
        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            cursor_set = False  # Flag to track if cursor should be set to hand

            # Loop through each menu item
            for x in range(len(self.menu_list)):
                y_start = self.menu_position_y + (x * Constant.SQ_SIZE)
                y_end = y_start + Constant.SQ_SIZE

                # Check if the mouse is over this item
                if y_start <= pos[1] <= y_end:
                    self.item_highlight_list = [
                        i == x for i in range(len(self.menu_list))
                    ]  # Update highlights correctly
                    # Set the cursor to hand when hovering over a menu item
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    cursor_set = (
                        True  # Set flag to indicate cursor is already set to hand
                    )

            # If the cursor is not over any menu item, set it back to the default arrow
            if not cursor_set:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            # If the mouse is outside the menu area, reset all highlights and set cursor to arrow
            self.item_highlight_list = [False] * len(self.menu_list)  # Reset highlights
            pygame.mouse.set_cursor(
                pygame.SYSTEM_CURSOR_ARROW
            )  # Reset cursor to default

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        for index, item in enumerate(self.menu_list):
            y_position = index * Constant.SQ_SIZE  # No more adjusted length logic!

            # Draw highlight if the item is selected
            if self.item_highlight_list[index]:
                self.menu.blit(self.square, (0, y_position))

            # Draw the icon centered in its highlight section
            icon_surface = self.sprite_list[index]

            if item == "queen":
                resource = get_decree_resource_sprite()
                resource_x = self.menu_width // 6
                resource_y = (
                    self.menu.get_height() * 1 // 3
                )  # Center in the bottom third of the menu
                self.menu.blit(resource, (resource_x, resource_y))
                # Position the cost text to the right of the icon
                cost_x = resource_x + resource.get_width() * 3 // 4
                cost_y = (
                    resource_y
                    + (resource.get_height() - self.cost_text_surface.get_height())
                    * 3
                    // 4
                )  # Center vertically
                if not self.engine.can_decree(self.row, self.col):
                    color = Constant.RED
                else:
                    color = self.color
                self.cost_text_surface = self.font.render(str(self.cost), True, color)
                self.menu.blit(self.cost_text_surface, (cost_x, cost_y))

            icon_width, icon_height = icon_surface.get_size()
            icon_x = (self.menu_width - icon_width) // 2  # Center horizontally
            icon_y = (
                y_position + (Constant.SQ_SIZE - icon_height) // 2
            )  # Center vertically inside section

            self.menu.blit(icon_surface, (icon_x, icon_y))

        # Draw the menu onto the screen
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y
