import os
import random
from typing import Dict, List, Tuple, Optional

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
    def __init__(self, win, engine):
        self.win = win
        self.engine = engine
        self.pieces = {
            "w": Constant.W_PIECES | Constant.W_BUILDINGS,
            "b": Constant.B_PIECES | Constant.B_BUILDINGS,
        }
        self._menu_boundary_buffer = 0

    @property
    def menu_boundary_buffer(self):
        return self.menu_width // 2

    def correct_menu_boundary(self):
        """Positions the menu near the mouse cursor while ensuring it stays within screen boundaries."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        board_width = Constant.BOARD_WIDTH_PX
        board_height = Constant.BOARD_HEIGHT_PX
        menu_width = self.menu_width
        menu_height = self.menu_height
        boundary_buffer = (
            self.menu_boundary_buffer
        )  # Optional buffer to prevent edge clipping

        # Start at mouse position
        x, y = mouse_x, mouse_y

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

    def mouse_in_menu_bounds(self):
        """Checks if the mouse is within the menu boundaries."""

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

    def close(self):
        pass


class Notification(Menu):
    def __init__(self, row, col, win, engine, message="blank"):
        """Initializes the notification menu at the given board position."""
        super().__init__(win, engine)
        self.row = row
        self.col = col
        self.color = Constant.turn_to_color[self.engine.turn]
        self.message = Constant.NOTIFICATIONS[message]

        # Font setup
        self.font_size = round(Constant.SQ_SIZE * 0.3)
        self.font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size
        )

        # Menu dimensions
        self.menu_width = Constant.SQ_SIZE * 3
        self.menu_height = Constant.SQ_SIZE + len(self.message) * Constant.SQ_SIZE
        self.y_buffer_between_messages = Constant.SQ_SIZE

        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer

        # Positioning
        self.initial_menu_position = get_initial_menu_position(self.row, self.col)
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        # Create menu surface
        self.menu = pygame.Surface((self.menu_width, self.menu_height))

        # "OK" text rendering
        self.ok_text_surface = self.font.render("ok", True, self.color)
        self.ok_display_x = (self.menu_width - self.ok_text_surface.get_width()) // 2
        self.ok_display_y = self.menu_height - self.ok_text_surface.get_height()

        # Message rendering
        self.message_text_surfaces = [
            self.font.render(msg, True, self.color) for msg in self.message
        ]

        # Highlight area for interaction
        self.highlight_display_x = 0
        self.highlight_display_y = self.menu_height - Constant.SQ_SIZE
        self.square = pygame.Surface((self.menu_width, Constant.SQ_SIZE))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.highlight = False

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        y_buffer = 0
        for message in self.message_text_surfaces:
            text_display_x = self.menu_width // 2 - message.get_width() // 2
            self.menu.blit(message, (text_display_x, y_buffer))
            y_buffer += self.y_buffer_between_messages
        if self.highlight:
            self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
            self.menu.blit(
                    self.square, (self.highlight_display_x, self.highlight_display_y)
            )
        self.menu.blit(self.ok_text_surface, (self.ok_display_x, self.ok_display_y))
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))

    def left_click(self):
        menu_above_ok_button = len(self.message) * round(Constant.SQ_SIZE * 0.8)
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] < self.menu_position_x + self.menu_width:
            if (
                    self.menu_position_y + menu_above_ok_button
                    < pos[1]
                    < self.menu_position_y + self.menu_height
            ):
                self.engine.close_menus()
                return True

    def right_click(self):
        self.engine.close_menus()

    def mouse_move(self):
        menu_above_ok_button = len(self.message) * round(Constant.SQ_SIZE * 0.8)
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] < self.menu_position_x + self.menu_width:
            if (
                    self.menu_position_y + menu_above_ok_button
                    < pos[1]
                    < self.menu_position_y + self.menu_height
            ):
                self.highlight = True
                return

        self.highlight = False


class RitualMenu(Menu):
    def __init__(self, row, col, win, engine, ritual_list, cost_type):
        self.cost_type = cost_type
        self.ritual_list = ritual_list
        self.row = row
        self.col = col
        super().__init__(win, engine)

        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.player = self.engine.players[self.engine.turn]
        self.initial_menu_position = (
            self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
            self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
        )
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 6
        self.horizontal_buffer_between_costs = round(Constant.SQ_SIZE * 1.3)
        self.bar_width = Constant.IMAGES["prayer_bar"].get_width()
        self.bar_height = Constant.IMAGES["prayer_bar"].get_height()
        self.bar_end_width = Constant.IMAGES["prayer_bar_end"].get_width()
        self.rituals = Constant.PRAYER_RITUALS
        self.ritual_width = self.rituals["w_gold_general"].get_width()
        self.ritual_height = self.rituals["w_gold_general"].get_height()
        self.gold_icon = Constant.MENU_ICONS["gold_coin"]
        self.gold_icon_display_x = (
                self.ritual_width + self.vertical_buffer_between_pieces
        )
        self.gold_cost_text_display_x = (
                self.ritual_width + self.vertical_buffer_between_pieces * 2
        )
        if not self.cost_type == "gold":
            self.menu_width = (
                    self.ritual_width
                    + self.vertical_buffer_between_pieces
                    + self.bar_end_width * 16
                    + self.bar_width
            )
        else:
            self.menu_width = (
                    self.ritual_width
                    + self.vertical_buffer_between_pieces
                    + self.gold_icon.get_width() * 2
            )

        self.menu_height = len(ritual_list) * self.ritual_height

        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(self.menu)

        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.casting = None

        self.prayer_bar_edge = self.vertical_buffer_between_pieces + self.ritual_width
        self.prayer_bar_end_edge = self.prayer_bar_edge + self.bar_width
        self.y_buffer = (
                self.vertical_buffer_between_pieces // 2
                + self.ritual_height // 2
                - self.bar_height // 2
        )
        self.ritual_highlight_list = []
        self.square = pygame.Surface(
                (self.menu_width, round(1 / len(self.ritual_list) * self.menu_height))
        )
        self.available_menu_space_for_prayer_bar = self.menu_width - self.ritual_width

        for _ in self.ritual_list:
            self.ritual_highlight_list.append(False)


    def full_length_of_prayer_bar(self, length_of_ritual):
        return self.bar_end_width * length_of_ritual + self.bar_width

    def ritual_clicked(self):
        pos = pygame.mouse.get_pos()
        mp = self.menu_position_y
        length = len(self.ritual_list)
        mh = self.menu_height

        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.ritual_list)):
                a = x / length
                b = a * mh
                c = b + mp
                d = (x + 1) / length
                e = d * mh
                f = e + mp
                r = range(round(c), round(f))
                if pos[1] in r:
                    return self.ritual_list[x]

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.ritual_list)):
                a = x / len(self.ritual_list)
                b = a * self.menu_height
                c = b + self.menu_position_y
                d = (x + 1) / len(self.ritual_list)
                e = d * self.menu_height
                f = e + self.menu_position_y
                r = range(round(c), round(f))
                if pos[1] in r:
                    self.ritual_highlight_list[x] = True
                    for z in range(len(self.ritual_highlight_list)):
                        if z is not x:
                            self.ritual_highlight_list[z] = False
        else:
            for _ in self.ritual_highlight_list:
                _ = False

    def left_click(self):
        self.casting = self.ritual_clicked()
        if self.casting is None or not self.engine.is_legal_ritual(
                self.casting, self.cost_type
        ) or self.engine.get_occupying(self.row, self.col).intercepted:
            return self.engine.state[-1].revert_to_playing_state()
        else:
            self.engine.menus = []
            return self.engine.transfer_to_ritual_state(self.casting, self.cost_type)

    def right_click(self):
        self.engine.state[-1].revert_to_playing_state()

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        for x in range(len(self.ritual_list)):
            a = x / len(self.ritual_list)
            b = a * self.menu_height
            if self.ritual_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Prayer Counter
        y_buffer_ritual = 0
        y_buffer_prayer = self.y_buffer
        for ritual in self.ritual_list:
            if self.cost_type == "prayer":
                length_of_this_prayer_bar = self.full_length_of_prayer_bar(
                        Constant.PRAYER_COSTS[ritual]["prayer"]
                )
                bar_end_edge = (
                        self.ritual_width
                        + self.available_menu_space_for_prayer_bar // 2
                        - length_of_this_prayer_bar // 2
                )
                bar_edge = bar_end_edge - self.bar_width
                self.menu.blit(
                        Constant.IMAGES["prayer_bar"], (bar_edge, y_buffer_prayer)
                )
                for z in range(Constant.PRAYER_COSTS[ritual]["prayer"]):
                    new_edge = bar_end_edge + self.bar_end_width * (z)
                    self.menu.blit(
                            Constant.IMAGES["prayer_bar_end"], (new_edge, y_buffer_prayer)
                    )
                y_buffer_prayer += self.y_buffer + self.ritual_height // 2
            elif self.cost_type == "gold":
                if Constant.PRAYER_COSTS[ritual]["gold"] != 0:
                    cost = Constant.PRAYER_COSTS[ritual]["gold"]
                    if self.player.gold >= cost:
                        color = Constant.turn_to_color[self.engine.turn]
                    else:
                        color = Constant.RED
                    gold_cost = self.font.render(str(cost), True, color)
                    gold_icon_display_y = (
                            y_buffer_ritual + self.gold_icon.get_height() // 2
                    )
                    gold_text_display_y = y_buffer_ritual + gold_cost.get_height() // 2
                    self.menu.blit(
                            self.gold_icon, (self.gold_icon_display_x, gold_icon_display_y)
                    )
                    self.menu.blit(
                            gold_cost, (self.gold_cost_text_display_x, gold_text_display_y)
                    )

            self.menu.blit(
                    self.rituals[self.engine.turn + "_" + ritual], (0, y_buffer_ritual)
            )
            y_buffer_ritual += self.ritual_height

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))


class TraderMenu(Menu):
    def __init__(self, row, col, win, engine, resource_list, amounts, trade_arrow):
        self.row = row
        self.col = col
        self.key = {"log": "wood", "gold_coin": "gold", "stone": "stone"}
        self.resource_list = resource_list
        super().__init__(win, engine)
        self.trade_arrow = trade_arrow
        self.amounts = amounts
        self.player = self.engine.players[self.engine.turn]
        self.give_image = Constant.IMAGES["give"]
        self.selected = None
        self.horizontal_buffer = Constant.SQ_SIZE // 2
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 4
        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.font_color = Constant.turn_to_color[self.engine.turn]
        self.resource_height = Constant.IMAGES["gold_coin"].get_width()
        self.resource_width = Constant.IMAGES["gold_coin"].get_height()
        self.menu_width = (
                self.resource_width
                + self.horizontal_buffer
                + self.resource_width
                + Constant.SQ_SIZE
        )
        self.menu_height = len(self.resource_list) * (
                self.resource_height + self.vertical_buffer_between_pieces
        )
        self.menu = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(self.menu)
        self.initial_menu_position = (
            self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
            self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,
        )
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.spawn_highlight_list = []
        self.square = pygame.Surface(
                (self.menu_width, round(1 / len(self.resource_list) * self.menu_height))
        )
        for _ in self.resource_list:
            self.spawn_highlight_list.append(False)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def resource_selected(self):
        pos = pygame.mouse.get_pos()
        mp = self.menu_position_y
        length = len(self.resource_list)
        mh = self.menu_height

        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.resource_list)):
                a = x / length
                b = a * mh
                c = b + mp
                d = (x + 1) / length
                e = d * mh
                f = e + mp
                r = range(round(c), round(f))
                if pos[1] in r:
                    return self.resource_list[x]

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
            for index in range(len(self.resource_list)):
                # Calculate the top and bottom y-coordinates of the current menu item
                item_start_y = (
                                       index / len(self.resource_list)
                               ) * self.menu_height + self.menu_position_y
                item_end_y = (
                                     (index + 1) / len(self.resource_list)
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
        for x in range(len(self.resource_list)):
            a = x / len(self.resource_list)
            b = a * self.menu_height
            if self.spawn_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        y_buffer = 0
        for p in self.resource_list:
            self.menu.blit(
                    Constant.IMAGES[p],
                    (self.horizontal_buffer // 2, y_buffer + self.menu_height // 16),
            )

            amount_text_surface = self.font.render(
                    ": " + str(self.amounts[p]), True, self.font_color
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

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class GiveMenu(TraderMenu):
    def __init__(self, row, col, win, engine, resource_list):
        self.player = engine.players[engine.turn]
        self.amounts = {
            "log"      : engine.trade_handler.get_give_conversion("wood", self.player),
            "gold_coin": engine.trade_handler.get_give_conversion("gold", self.player),
            "stone"    : engine.trade_handler.get_give_conversion("stone", self.player),
        }
        self.trade_arrow = Constant.IMAGES["give"]
        super().__init__(
                row, col, win, engine, resource_list, self.amounts, self.trade_arrow
        )

    def right_click(self):
        self.engine.piece_trading = None
        self.engine.state[-1].revert_to_playing_state()

    def left_click(self):
        self.selected = self.resource_selected()
        if self.selected is not None:
            amount_given = self.amounts[self.selected]
            self.engine.trading.append((self.selected, amount_given))
            self.engine.close_menus()
            resource_list = []
            resources = ["log", "gold_coin", "stone"]
            for resource in resources:
                if resource is not self.selected:
                    resource_list.append(resource)
            row, col = Constant.convert_pos(pygame.mouse.get_pos())
            menu = ReceiveMenu(
                    row, col, self.win, self.engine, resource_list, amount_given
            )
            self.engine.menus.append(menu)
            return True


class ReceiveMenu(TraderMenu):
    def __init__(self, row, col, win, engine, resource_list, amount_given):
        self.amount_given = amount_given
        self.amounts = {
            "log"      : engine.trade_handler.get_receive_conversion(
                    self.amount_given, "wood"
            ),
            "gold_coin": engine.trade_handler.get_receive_conversion(
                    self.amount_given, "gold"
            ),
            "stone"    : engine.trade_handler.get_receive_conversion(
                    self.amount_given, "stone"
            ),
        }
        self.trade_arrow = Constant.IMAGES["receive"]
        super().__init__(
                row, col, win, engine, resource_list, self.amounts, self.trade_arrow
        )

    def left_click(self):
        self.selected = self.resource_selected()
        if self.selected is not None:
            amount = self.engine.trade_handler.get_receive_conversion(
                    self.amount_given, self.key[self.selected]
            )
            self.engine.menus = []
            self.engine.trading.append((self.selected, amount))
            self.engine.trade()
            return True

    def right_click(self):
        self.engine.close_menus()
        self.engine.trading = []
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        self.engine.create_trader_menu(row, col, False)


class StealingMenu(Menu):
    """
    Represents the menu for stealing resources from a tile on the game board.

    This menu handles displaying the resources available for stealing and updating the game state.
    """

    def __init__(self, row: int, col: int, win: pygame.Surface, engine: "Engine") -> None:
        """
        Initializes the StealingMenu.

        :param row: The row position of the menu.
        :param col: The column position of the menu.
        :param win: The game window surface.
        :param engine: The game engine instance.
        """
        self.row = row
        self.col = col
        self.spawn_list = ["log", "gold_coin", "stone"]
        self.key = {"log": "wood", "gold_coin": "gold", "stone": "stone"}

        # Initialize the type of entity being stolen from
        self.type_stolen_from = None

        # Call the parent class constructor
        super().__init__(win, engine)

        # Determine the type of entity occupying the tile
        piece = self.engine.get_occupying(row, col)

        # Create a mapping of classes to type strings
        entity_map = {
            Trader  : "trader",  # Trader corresponds to "trader"
            Piece   : "piece",  # Any Piece that isn't a Trader corresponds to "piece"
            Building: "building"  # Building corresponds to "building"
        }

        # Check the type of the piece and set the appropriate type
        for entity_class, entity_type in entity_map.items():
            if isinstance(piece, entity_class):
                self.type_stolen_from = entity_type
                break

        # Get the amounts of each resource available for stealing
        self.amounts = {
            "log"      : self.engine.stealing_values("wood", self.type_stolen_from),
            "gold_coin": self.engine.stealing_values("gold", self.type_stolen_from),
            "stone"    : self.engine.stealing_values("stone", self.type_stolen_from),
        }
        for resource in self.spawn_list:
            if self.amounts[resource] == 0:
                self.spawn_list.remove(resource)

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
        self.menu_height = len(self.spawn_list) * (
                self.resource_height + self.vertical_buffer_between_pieces
        )

        # Create a pygame surface for the menu with the calculated width and height
        self.menu = pygame.Surface((self.menu_width, self.menu_height))

        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(self.menu)

        # Set initial menu position based on the column and row
        # Position the menu at the center of the grid square
        self.initial_menu_position = (
            self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,  # X position (centered within the column)
            self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2,  # Y position (centered within the row)
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
                (self.menu_width, round(1 / len(self.spawn_list) * self.menu_height))
        )
        for _ in self.spawn_list:
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
        for x in range(len(self.spawn_list)):
            a = x / len(self.spawn_list)
            b = a * self.menu_height
            if self.spawn_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        # Set the vertical buffer to 0 to start drawing at the top of the menu
        y_buffer = 0

        # Iterate through the spawn list to draw the resources and amounts
        for p in self.spawn_list:
            # Center the resource image icon horizontally within the menu width
            # Align the icon at 1/3 of the menu width, centered within its section
            icon_x = self.menu_width // 3 - self.resource_width // 2

            # Draw the resource image at the calculated position
            self.menu.blit(Constant.IMAGES[p], (icon_x, y_buffer+self.menu_height // 16))

            # Center the amount text surface horizontally within the remaining 2/3 of the menu width
            amount_text_surface = self.font.render(
                    ": " + str(self.amounts[p]), True, self.font_color
            )

            # Align the text at the center of the right side of the menu
            text_x = ((self.menu_width * 2 // 3) - amount_text_surface.get_width() // 2)

            # Draw the amount text below the resource image (adding a vertical offset for spacing)
            self.menu.blit(
                    amount_text_surface,
                    (text_x, y_buffer),
            )

            # Increment the y_buffer by the total height of the resource image + vertical spacing
            y_buffer += self.resource_height + self.vertical_buffer_between_pieces

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y

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
        self.engine.stealing = None
        stolen_resource = self.resource_selected()
        if stolen_resource:
            amount = self.amounts[stolen_resource]
            self.engine.menus = []
            self.engine.stealing = [self.key[stolen_resource], amount]
            return True
        else:
            self.engine.stealing = None
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
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(self.menu)
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
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(self.menu)
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
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(self.win)
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
            "wood" : Constant.MENU_ICONS["log"],
            "gold" : Constant.MENU_ICONS["gold_coin"],
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
        self.paper_surface_text_box = self.engine.get_current_state().scale_paper_texture(self.text_box)
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
            "pray"    : ["monolith, prayer_stone"],
            "mine"    : resource_tiles,
            "king"    : list(),
            "queen"   : list(),
            "trade"   : list(),
            "persuade": ["enemy"],
            "steal"   : ["enemy"],
            "build"   : list(),
            "ritual"  : list(),
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


class SideMenu:
    def __init__(self, win, engine):
        self.win = win
        self.engine = engine
        self.menu_height = Constant.SIDE_MENU_HEIGHT
        self.menu_width = Constant.SIDE_MENU_WIDTH
        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(self.menu)

    def mouse_move(self):
        pass

    def left_click(self):
        pass

    def right_click(self):
        pass


class Empty(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)
        self.win.blit(self.menu, (Constant.BOARD_WIDTH_SQ * Constant.SQ_SIZE, 0))


class PieceInspector(SideMenu):
    def __init__(
            self, win: pygame.Surface, engine: "Engine", currently_selected: "Unit"
    ) -> None:
        # Initialize the parent class with window and engine
        super().__init__(win, engine)

        # Dictionary mapping player colors to their respective pieces and buildings
        self.PIECES: Dict[str, Dict[str, pygame.Surface]] = {
            "w": Constant.W_PIECES | Constant.W_BUILDINGS,
            "b": Constant.B_PIECES | Constant.B_BUILDINGS,
        }

        # Define font sizes based on the square size constant
        self.font_size: int = round(Constant.SQ_SIZE / 3.5)
        self.small_font_size: int = round(Constant.SQ_SIZE / 4)

        # Load fonts from the specified file path
        self.font: pygame.font.Font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.small_font: pygame.font.Font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.small_font_size
        )

        # Get the current player based on engine's turn
        self.player = self.engine.players[self.engine.turn]

        # Set buffer space size
        self.buffer: int = Constant.SQ_SIZE // 2

        # Dictionary mapping resource names to their corresponding menu icons
        self.RESOURCES: Dict[str, pygame.Surface] = {
            "wood" : Constant.MENU_ICONS["log"],
            "gold" : Constant.MENU_ICONS["gold_coin"],
            "stone": Constant.MENU_ICONS["stone"],
        }

        # Render a space character to be used for spacing
        self.space: pygame.Surface = self.small_font.render(" ", True, Constant.WHITE)

        # Store the currently selected piece
        self.piece: Unit = currently_selected

        # Determine the piece's color based on turn mapping
        self.color: tuple = Constant.turn_to_color[self.piece.color]

        # Retrieve the description text for the selected piece
        self.description_text: List[str] = Constant.DESCRIPTIONS[str(self.piece)]

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

    def draw(self) -> None:
        """Draws the piece details onto the menu screen."""
        self.menu.fill(Constant.MENU_COLOR)

        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        # Display sprite
        self.menu.blit(
                self.sprite,
                (self.menu_width // 2 - self.sprite.get_width() // 2, self.buffer),
        )

        # Display name
        name = self.make_name_more_readable()
        name_surface = self.font.render(name, True, self.color)
        self.menu.blit(
                name_surface,
                (
                    self.menu_width // 2 - name_surface.get_width() // 2,
                    self.buffer + self.sprite.get_height(),
                ),
        )

        # Display cost
        cost = Constant.PIECE_COSTS[str(self.piece)]
        y_buffer = self.buffer + name_surface.get_height() + self.sprite.get_height()
        for resource in cost:
            if cost[resource] != 0:
                color = (
                    self.color
                    if getattr(self.player, Constant.RESOURCE_KEY[resource])
                       >= cost[resource]
                    else Constant.RED
                )
                text_surf = self.font.render(str(cost[resource]), True, color)
                resource_icon = self.RESOURCES[Constant.RESOURCE_KEY[resource]]
                resource_x = self.menu_width // 2 - (
                        text_surf.get_width() // 2 + resource_icon.get_width() // 2
                )
                self.menu.blit(resource_icon, (resource_x, y_buffer))
                self.menu.blit(
                        text_surf,
                        (
                            resource_x + resource_icon.get_width(),
                            y_buffer - text_surf.get_height() // 8,
                        ),
                )
            y_buffer += name_surface.get_height()

        # Display piece description with line breaks
        if self.description_text_surfaces:
            original_x = self.menu_width // 16
            x = original_x
            for line in self.description_text_surfaces:
                y_buffer += (
                    self.description_text_height
                )  # Move to the next line for each description entry
                x = original_x
                for word in line:
                    if x + word.get_width() + self.space.get_width() >= self.menu_width:
                        y_buffer += self.description_text_height
                        x = original_x
                    self.menu.blit(word, (x, y_buffer))
                    x += word.get_width()
                    self.menu.blit(self.space, (x, y_buffer))
                    x += self.space.get_width()

        # Render the menu onto the game window
        self.win.blit(self.menu, (Constant.BOARD_WIDTH_SQ * Constant.SQ_SIZE, 0))

    def make_name_more_readable(self):
        name = str(self.piece)

        if name == "prayer_stone":
            name = "floating stone"

        name = name.replace("_", " ")
        return name


class StartMenu(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        # Select a random color for the logo and intro text
        # Used by main menu to vary the wording
        self.faction_name = self.reselect_faction_name()
        self.color = self.reselect_menu_color()

        self.font_size = round(Constant.SQ_SIZE / 3)
        self.font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.small_font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size // 2
        )

        self.ver_text = Constant.VERSION + " " + Constant.NUMBER
        self.version_text_surf = self.font.render(self.ver_text, True, self.color)
        self.version_text_display_x = (
                self.menu_width // 2 - self.version_text_surf.get_width() // 2
        )
        self.reset_map_image = Constant.RESOURCES[random.choice(Constant.resources)]
        self.map_image_height = self.reset_map_image.get_height()
        self.map_image_width = self.reset_map_image.get_width()

        self.introduction = [self.ver_text, " ", "select", "your", "_"]

        self.w_boat = Constant.IMAGES["w_boat"]
        self.b_boat = Constant.IMAGES["b_boat"]
        self.boat_display_x = self.menu_width // 2 - self.b_boat.get_width() // 2
        a = self.menu_height * 1 / 5
        self.r = round((self.menu_height - a))
        self.display_y = Constant.SQ_SIZE * 6

        self.w_piece_highlight = False
        self.b_piece_highlight = False
        self.randomize_resources_highlight = False
        self.scale = Constant.IMAGES_IMAGE_MODIFY["w_boat"]["SCALE"]
        self.buffer = self.scale[0]
        self.square = pygame.Surface(self.scale)
        self.square_highlight_buffer = Constant.SQ_SIZE // 5

        self.resources_square = pygame.Surface((self.menu_width, round(a)))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        self.resources_square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.resources_square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.resource_highlight_height = round(Constant.BOARD_HEIGHT_PX * 4 / 5)
        self.reset_map_display_x = (
                self.menu_width // 2 - self.reset_map_image.get_width() // 2
        )
        self.reset_map_display_y = (
                Constant.BOARD_HEIGHT_PX
                - self.resources_square.get_height() // 2
                - self.map_image_height // 2
        )

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        y_buffer = Constant.SQ_SIZE // 2
        for line in self.introduction:
            if line == "_":
                line = self.faction_name
            if line == self.introduction[0]:
                surface = self.small_font.render(line, True, self.color)
            else:
                surface = self.font.render(line, True, self.color)
            text_x = self.menu_width // 2 - surface.get_width() // 2
            self.menu.blit(surface, (text_x, y_buffer))
            y_buffer += surface.get_height()

        self.w_display_y = self.menu_height // 2 - self.b_boat.get_height() // 2
        self.b_display_y = self.w_display_y + self.buffer + self.b_boat.get_height()
        self.menu.blit(self.w_boat, (self.boat_display_x, self.w_display_y))
        self.menu.blit(self.b_boat, (self.boat_display_x, self.b_display_y))
        if self.b_piece_highlight:
            self.menu.blit(self.square, (self.boat_display_x, self.b_display_y))
        elif self.w_piece_highlight:
            self.menu.blit(self.square, (self.boat_display_x, self.w_display_y))
        elif self.randomize_resources_highlight:
            self.menu.blit(self.resources_square, (0, self.resource_highlight_height))
        self.menu.blit(
                self.reset_map_image, (self.reset_map_display_x, self.reset_map_display_y)
        )

        self.win.blit(self.menu, (Constant.BOARD_WIDTH_PX, 0))

    def left_click(self):
        starting = False
        pos = pygame.mouse.get_pos()
        if pos[0] > Constant.BOARD_WIDTH_PX:
            menu_mouse_x_position = pos[0] - Constant.BOARD_WIDTH_PX
            if menu_mouse_x_position in range(
                    self.boat_display_x, self.boat_display_x + self.w_boat.get_width()
            ):
                if pos[1] in range(
                        self.w_display_y, self.w_display_y + self.w_boat.get_height()
                ):
                    self.engine.turn = "w"
                    starting = True
                elif pos[1] in range(
                        self.b_display_y, self.b_display_y + self.w_boat.get_height()
                ):
                    self.engine.turn = "b"
                    starting = True
                if starting:
                    if not Constant.DEBUG_START:
                        new_state = "select starting pieces"
                        self.engine.set_state(new_state)
                    else:
                        new_state = "debug"
                        self.engine.set_state(new_state)
            if pos[1] in range(self.r, self.menu_height):
                self.engine.reset_board()
                self.engine.starting_resources()
                self.reset_map_image = Constant.RESOURCES[
                    random.choice(Constant.resources)
                ]
                self.reset_map_display_x = (
                        self.menu_width // 2 - self.reset_map_image.get_width() // 2
                )
                self.reset_map_display_y = (
                        Constant.BOARD_HEIGHT_PX
                        - self.resources_square.get_height() // 2
                        - self.map_image_height // 2
                )
                self.faction_name = self.reselect_faction_name()

    def reselect_faction_name(self):
        rand = random.randint(0, len(Constant.FACTION_NAMES) - 1)
        return Constant.FACTION_NAMES[rand]

    def reselect_menu_color(self):
        rand = random.randint(0, 2)
        if rand == 0:
            return Constant.WHITE
        else:
            return Constant.BLACK

    def mouse_move(self):
        """
        Handles mouse movement over the board and the menu area. It highlights the pieces
        and shows the appropriate cursor when hovering over specific areas of the board or menu.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Initialize cursor to default
        cursor_set = False

        # Check if the mouse is within the bounds of the menu (right of the board)
        if mouse_x > Constant.BOARD_WIDTH_PX:
            # Calculate the mouse's position relative to the menu
            menu_mouse_x_position = mouse_x - Constant.BOARD_WIDTH_PX

            # Check if the mouse is over the white piece area
            if menu_mouse_x_position in range(
                    self.boat_display_x, self.boat_display_x + self.w_boat.get_width()
            ):
                if mouse_y in range(
                        self.w_display_y, self.w_display_y + self.w_boat.get_height()
                ):
                    # Highlight white piece if hovering
                    self.w_piece_highlight = True
                    if not cursor_set:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        cursor_set = True
                else:
                    self.w_piece_highlight = False

                # Check if the mouse is over the black piece area
                if mouse_y in range(
                        self.b_display_y, self.b_display_y + self.w_boat.get_height()
                ):
                    # Highlight black piece if hovering
                    self.b_piece_highlight = True
                    if not cursor_set:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        cursor_set = True
                else:
                    self.b_piece_highlight = False

            else:
                self.w_piece_highlight = False
                self.b_piece_highlight = False

            # Check if the mouse is within the range for the randomize resources button
            if mouse_y in range(self.r, self.menu_height):
                self.randomize_resources_highlight = True
                if not cursor_set:
                    # Set cursor to hand when hovering over randomize button
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    cursor_set = True
            else:
                self.randomize_resources_highlight = False

        else:
            # Reset highlights when the mouse is not in the menu area
            self.w_piece_highlight = False
            self.b_piece_highlight = False
            self.randomize_resources_highlight = False

        # If no other condition has set the cursor, set it back to default arrow
        if not cursor_set:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


class SurrenderMenu(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.fontSize = round(Constant.SQ_SIZE // 3)
        self.font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.fontSize
        )
        self.surrender_text = "Surrender?"
        self.yes_text = "yes"
        self.no_text = "no"
        self.surrender_text_surface = self.font.render(
                self.surrender_text, True, Constant.turn_to_color[self.engine.turn]
        )
        self.yes_button_address = self.engine.turn + "_" + self.yes_text
        self.no_button_address = self.engine.turn + "_" + self.no_text
        self.yes_button_image = Constant.IMAGES[self.yes_button_address]
        self.no_button_image = Constant.IMAGES[self.no_button_address]
        self.question_display_y = (
                self.menu_height // 2 - self.surrender_text_surface.get_height() // 2
        )
        self.question_display_x = (
                self.menu_width // 2 - self.surrender_text_surface.get_width() // 2
        )
        self.buffer = Constant.SQ_SIZE // 2
        self.yes_display_y = self.question_display_y + 2 * self.buffer
        self.no_display_y = (
                self.yes_display_y + self.yes_button_image.get_height() + self.buffer
        )
        self.answer_surface_height = self.yes_button_image.get_height()
        self.answer_surface_width = self.yes_button_image.get_width()
        self.yes_display_x = (
                self.menu_width // 2 - self.yes_button_image.get_width() // 2
        )
        self.no_display_x = self.menu_width // 2 - self.no_button_image.get_width() // 2

        self.yes_highlight = False
        self.no_highlight = False
        self.square = pygame.Surface(Constant.YES_NO_BUTTON_SCALE)
        self.yes_square_display_x = self.yes_display_x
        self.no_square_display_x = self.no_display_x

    def mouse_move(self):
        """
        Handles mouse movement over the menu area, highlighting the 'Yes' and 'No' buttons
        based on the mouse position and updating the highlight state accordingly.
        It also changes the mouse cursor when hovering over the buttons.
        """
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Initialize cursor state to the default arrow
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Check if the mouse is within the bounds of the menu (right of the board)
        if mouse_x > Constant.BOARD_WIDTH_PX:
            # Calculate the mouse's position relative to the menu
            menu_x = mouse_x - Constant.BOARD_WIDTH_PX

            # Check if the mouse is over the 'Yes' button
            if mouse_y in range(
                    self.yes_display_y, self.yes_display_y + self.answer_surface_height
            ):
                if menu_x in range(
                        self.yes_display_x, self.yes_display_x + self.answer_surface_width
                ):
                    # Highlight 'Yes' button if hovering
                    self.yes_highlight = True
                    # Set cursor to hand if hovering over 'Yes'
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    self.yes_highlight = False

            # Check if the mouse is over the 'No' button
            elif mouse_y in range(
                    self.no_display_y, self.no_display_y + self.answer_surface_height
            ):
                if menu_x in range(
                        self.no_display_x, self.no_display_x + self.answer_surface_width
                ):
                    # Highlight 'No' button if hovering
                    self.no_highlight = True
                    # Set cursor to hand if hovering over 'No'
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    self.no_highlight = False

            else:
                # Reset highlights if not hovering over either button
                self.yes_highlight = False
                self.no_highlight = False
        else:
            # Reset highlights when the mouse is not in the menu area
            self.yes_highlight = False
            self.no_highlight = False

    def left_click(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > Constant.BOARD_WIDTH_PX:
            menu_x = pos[0] - Constant.BOARD_WIDTH_PX
            if pos[1] in range(
                    self.yes_display_y, self.yes_display_y + self.answer_surface_height
            ):
                if menu_x in range(
                        self.yes_display_x, self.yes_display_x + self.answer_surface_width
                ):
                    self.engine.change_turn()
                    self.engine.surrendering = True
                    return True
            if pos[1] in range(
                    self.no_display_y, self.no_display_y + self.answer_surface_height
            ):
                if menu_x in range(
                        self.no_display_x, self.no_display_x + self.answer_surface_width
                ):
                    return self.engine.state[-1].revert_to_playing_state()

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)
        self.menu.blit(
                self.surrender_text_surface,
                (self.question_display_x, self.question_display_y),
        )
        if self.yes_highlight:
            self.menu.blit(self.square, (self.yes_square_display_x, self.yes_display_y))
        elif self.no_highlight:
            self.menu.blit(self.square, (self.no_square_display_x, self.no_display_y))
        self.menu.blit(self.yes_button_image, (self.yes_display_x, self.yes_display_y))
        self.menu.blit(self.no_button_image, (self.no_display_x, self.no_display_y))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.win.blit(self.menu, (Constant.BOARD_WIDTH_SQ * Constant.SQ_SIZE, 0))


class Hud(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.title_icon_width = Constant.IMAGES["w_game_name"].get_width()
        self.title_icon_height = Constant.IMAGES["w_game_name"].get_height()
        self.title_icon_display_x = self.menu_width // 2 - self.title_icon_width // 2
        self.title_icon_display_y = self.menu_height // 8 - self.title_icon_height // 2
        self.font_size = Constant.SQ_SIZE // 2
        self.small_font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size // 2
        )

        self.font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.counter_icon_display_x = Constant.BOARD_WIDTH_PX + 10
        self.coin_icon_display_y = round(self.menu_height * (8 / 10))
        self.icon_y_offset = Constant.SQ_SIZE // 1.2
        self.stone_icon_display_y = self.coin_icon_display_y + self.icon_y_offset
        self.log_icon_display_y = self.coin_icon_display_y - self.icon_y_offset
        self.prayer_icon_display_y = self.log_icon_display_y - self.icon_y_offset
        self.action_icon_display_y = self.prayer_icon_display_y - self.icon_y_offset
        self.units_icon_display_y = self.action_icon_display_y - self.icon_y_offset
        self.turn_icon_display_y = self.units_icon_display_y - self.icon_y_offset
        self.bar_end_width = Constant.IMAGES["prayer_bar_end"].get_width()
        self.bar_width = Constant.IMAGES["prayer_bar"].get_width()
        self.bar_height = Constant.IMAGES["prayer_bar"].get_height()
        self.counter_text_buffer = Constant.SQ_SIZE // 2
        self.prayer_bar_height = (
                self.prayer_icon_display_y
                + round(Constant.MENU_ICONS["prayer"].get_height() // 2)
                - round(self.bar_height // 2)
        )
        self.prayer_bar_edge = self.counter_icon_display_x + self.counter_text_buffer
        self.prayer_bar_end_edge = self.prayer_bar_edge + self.bar_width
        self.empty_text_surface = self.font.render("0", True, Constant.WHITE)
        self.text_vertical_offset = (
                self.empty_text_surface.get_height() // 2
                - Constant.MENU_ICONS["log"].get_height() // 2
        )
        self.square = pygame.Surface(
                (Constant.SIDE_MENU_WIDTH, round(Constant.SIDE_MENU_HEIGHT * 0.25))
        )
        self.title_bar_highlight = False
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)
        if Constant.DISPLAY_STATE_IN_HUD:
            state_text_surf = self.small_font.render(
                    str(self.engine.state[-1]),
                    True,
                    Constant.turn_to_color[self.engine.turn],
            )
            selected = self.small_font.render(
                    str(self.engine.update_previously_selected()),
                    True,
                    Constant.turn_to_color[self.engine.turn],
            )
            self.menu.blit(
                    state_text_surf,
                    (
                        self.menu_width // 2 - state_text_surf.get_width() // 2,
                        self.square.get_height(),
                    ),
            )
            self.menu.blit(
                    selected,
                    (
                        self.menu_width // 2 - selected.get_width() // 2,
                        self.square.get_height() * 2,
                    ),
            )
        if self.title_bar_highlight:
            self.menu.blit(self.square, (0, 0))
        self.menu.blit(
                Constant.IMAGES[self.engine.turn + "_game_name"],
                (self.title_icon_display_x, self.title_icon_display_y),
        )
        self.win.blit(self.menu, (Constant.BOARD_WIDTH_PX, 0))

        # Gold Counter
        if not self.engine.players[self.engine.turn].gold == 0:
            self.win.blit(
                    Constant.IMAGES["gold_coin"],
                    (self.counter_icon_display_x, self.coin_icon_display_y),
            )
            white_coin_text = self.font.render(
                    str(self.engine.players[self.engine.turn].gold),
                    True,
                    Constant.turn_to_color[self.engine.turn],
            )
            self.win.blit(
                    white_coin_text,
                    (
                        (self.counter_icon_display_x + self.counter_text_buffer),
                        self.coin_icon_display_y - self.text_vertical_offset,
                    ),
            )

        # Wood Counter
        if not self.engine.players[self.engine.turn].wood == 0:
            self.win.blit(
                    Constant.IMAGES["log"],
                    (self.counter_icon_display_x, self.log_icon_display_y),
            )
            white_log_text = self.font.render(
                    str(self.engine.players[self.engine.turn].wood),
                    True,
                    Constant.turn_to_color[self.engine.turn],
            )
            self.win.blit(
                    white_log_text,
                    (
                        (self.counter_icon_display_x + self.counter_text_buffer),
                        self.log_icon_display_y - self.text_vertical_offset,
                    ),
            )

        # Stone Counter
        if not self.engine.players[self.engine.turn].stone == 0:
            self.win.blit(
                    Constant.IMAGES["stone"],
                    (self.counter_icon_display_x, self.stone_icon_display_y),
            )
            white_log_text = self.font.render(
                    str(self.engine.players[self.engine.turn].stone),
                    True,
                    Constant.turn_to_color[self.engine.turn],
            )
            self.win.blit(
                    white_log_text,
                    (
                        (self.counter_icon_display_x + self.counter_text_buffer),
                        self.stone_icon_display_y - self.text_vertical_offset,
                    ),
            )

        # Prayer Counter
        if not self.engine.players[self.engine.turn].prayer == 0:
            self.win.blit(
                    Constant.MENU_ICONS["prayer"],
                    (self.counter_icon_display_x, self.prayer_icon_display_y),
            )
            self.win.blit(
                    Constant.IMAGES["prayer_bar"],
                    (self.prayer_bar_edge, self.prayer_bar_height),
            )
            for x in range(self.engine.players[self.engine.turn].prayer):
                new_edge = self.prayer_bar_end_edge + self.bar_end_width * (x)
                self.win.blit(
                        Constant.IMAGES["prayer_bar_end"],
                        (new_edge, self.prayer_bar_height),
                )

        # Actions Remaining Counter
        self.win.blit(
                Constant.IMAGES["action"],
                (self.counter_icon_display_x, self.action_icon_display_y),
        )
        actions_remaining_text = self.font.render(
                str(self.engine.players[self.engine.turn].get_actions_remaining()),
                True,
                Constant.turn_to_color[self.engine.turn],
        )
        self.win.blit(
                actions_remaining_text,
                (
                    (self.counter_icon_display_x + self.counter_text_buffer),
                    self.action_icon_display_y - self.text_vertical_offset,
                ),
        )

        # Unit Limit Counter
        self.win.blit(
                Constant.IMAGES["units"],
                (self.counter_icon_display_x, self.units_icon_display_y),
        )
        t = (
                str(self.engine.players[self.engine.turn].get_current_population())
                + "/"
                + str(self.engine.players[self.engine.turn].get_piece_limit())
        )
        units_text = self.font.render(t, True, Constant.turn_to_color[self.engine.turn])
        self.win.blit(
                units_text,
                (
                    (self.counter_icon_display_x + self.counter_text_buffer),
                    self.units_icon_display_y - self.text_vertical_offset,
                ),
        )

        # Turn Counter
        self.win.blit(
                Constant.IMAGES["hour_glass"],
                (self.counter_icon_display_x, self.turn_icon_display_y),
        )
        turn_number_text = str(self.engine.turn_count_display)
        text_surf = self.font.render(
                turn_number_text, True, Constant.turn_to_color[self.engine.turn]
        )
        self.win.blit(
                text_surf,
                (
                    self.counter_icon_display_x + self.counter_text_buffer,
                    self.turn_icon_display_y - self.text_vertical_offset,
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
        if pos[0] > Constant.BOARD_WIDTH_PX:
            # Check if the mouse is over the title bar area (top 25% of the screen)
            if 0 < pos[1] < Constant.BOARD_HEIGHT_PX * 0.25:
                self.title_bar_highlight = True
                pygame.mouse.set_cursor(
                        pygame.SYSTEM_CURSOR_HAND
                )  # Set cursor to hand when over title bar
            else:
                self.title_bar_highlight = False
                pygame.mouse.set_cursor(
                        pygame.SYSTEM_CURSOR_ARROW
                )  # Reset cursor to arrow when not over title bar
        else:
            # Reset title bar highlight and cursor if not in the menu area
            self.title_bar_highlight = False

    def left_click(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > Constant.BOARD_WIDTH_PX:
            if 0 < pos[1] < Constant.BOARD_HEIGHT_PX * 0.25:
                return self.engine.transfer_to_piece_cost_screen()


class Contextual(Menu):
    def __init__(self, row, col, win, engine, menu_list):
        super().__init__(win, engine)
        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(self.win)
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
            "pray"    : self.engine.transfer_to_praying_state,
            "mine"    : self.engine.transfer_to_mining_state,
            "king"    : self.engine.transfer_to_surrender_state,
            "queen"   : self.engine.decree,
            "trade"   : self.engine.transfer_to_trading_state,
            "persuade": self.engine.transfer_to_persuading_state,
            "steal"   : self.engine.transfer_to_stealing_state,
            "build"   : self.engine.transfer_to_building_state,
            "ritual"  : self.engine.transfer_to_pre_ritual_state,
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
            "pray"    : pray_requirements,
            "mine"    : half_requirements,
            "king"    : no_requirements,
            "queen"   : queen_requirements,
            "trade"   : trade_requirements,
            "persuade": standard_requirements,
            "steal"   : half_requirements,
            "build"   : no_requirements,
            "ritual"  : no_requirements,
        }
        self.updates = {
            "pray"    : self.engine.update_praying_squares,
            "mine"    : self.engine.update_mining_squares,
            "king"    : None,
            "queen"   : None,
            "trade"   : None,
            "persuade": self.engine.update_persuader_squares,
            "steal"   : self.engine.update_stealing_squares,
            "build"   : self.engine.update_spawn_squares,
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
            self.updates[item]()
            squares = {
                "pray"    : self.piece.praying_squares_list,
                "mine"    : self.piece.mining_squares_list,
                "persuade": self.piece.persuader_squares_list,
                "steal"   : self.piece.stealing_squares_list,
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
