from __future__ import annotations

import typing
import constant
import pygame
import os
import random
from typing import Dict, List

if typing.TYPE_CHECKING:
    from unit import Unit
    from engine import Engine


class SideBar:
    def __init__(self, win, engine):
        self.win = win
        self.engine = engine
        self.menu_height = constant.SIDE_MENU_HEIGHT
        self.menu_width = constant.SIDE_MENU_WIDTH
        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        # Scale paper texture
        self.paper_texture = self.engine.get_current_state().scale_paper_texture(
                self.menu
        )

    def draw(self):
        pass

    def mouse_move(self):
        pass

    def left_click(self):
        pass

    def right_click(self):
        pass


class Empty(SideBar):
    def __init__(self, win, engine):
        super().__init__(win, engine)

    def draw(self):
        self.menu.fill(constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)
        self.win.blit(self.menu, (constant.BOARD_WIDTH_SQ * constant.SQ_SIZE, 0))


class PieceInspector(SideBar):
    def __init__(
            self, win: pygame.Surface, engine: "Engine", currently_selected: "Unit"
    ) -> None:
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
        self.player = self.engine.players[self.engine.turn]

        # Set buffer space size
        self.buffer: int = constant.SQ_SIZE // 2

        # Dictionary mapping resource names to their corresponding menu icons
        self.RESOURCES: Dict[str, pygame.Surface] = {
            "wood" : constant.MENU_ICONS["log"],
            "gold" : constant.MENU_ICONS["gold_coin"],
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

    def draw(self) -> None:
        """Draws the piece details onto the menu screen."""
        self.menu.fill(constant.MENU_COLOR)

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
        cost = constant.PIECE_COSTS[str(self.piece)]
        y_buffer = self.buffer + name_surface.get_height() + self.sprite.get_height()
        for resource in cost:
            if cost[resource] != 0:
                color = (
                    self.color
                    if getattr(self.player, constant.RESOURCE_KEY[resource])
                       >= cost[resource]
                    else constant.RED
                )
                text_surf = self.font.render(str(cost[resource]), True, color)
                resource_icon = self.RESOURCES[constant.RESOURCE_KEY[resource]]
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
        self.win.blit(self.menu, (constant.BOARD_WIDTH_SQ * constant.SQ_SIZE, 0))

    def make_name_more_readable(self):
        name = str(self.piece)

        if name == "prayer_stone":
            name = "floating stone"

        name = name.replace("_", " ")
        return name


class Start(SideBar):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        # Select a random color for the logo and intro text
        # Used by main menu to vary the wording
        self.faction_name = self.reselect_faction_name()
        self.color = self.reselect_menu_color()

        self.font_size = round(constant.SQ_SIZE / 3)
        self.font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.small_font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size // 2
        )

        self.ver_text = constant.VERSION + " " + constant.NUMBER
        self.version_text_surf = self.font.render(self.ver_text, True, self.color)
        self.version_text_display_x = (
                self.menu_width // 2 - self.version_text_surf.get_width() // 2
        )
        self.reset_map_image = constant.RESOURCES[random.choice(constant.resources)]
        self.map_image_height = self.reset_map_image.get_height()
        self.map_image_width = self.reset_map_image.get_width()

        self.introduction = [self.ver_text, " ", "select", "your", "_"]

        self.w_boat = constant.IMAGES["w_boat"]
        self.b_boat = constant.IMAGES["b_boat"]
        self.boat_display_x = self.menu_width // 2 - self.b_boat.get_width() // 2
        a = self.menu_height * 1 / 5
        self.r = round((self.menu_height - a))
        self.display_y = constant.SQ_SIZE * 6

        self.w_piece_highlight = False
        self.b_piece_highlight = False
        self.randomize_resources_highlight = False
        self.scale = constant.IMAGES_IMAGE_MODIFY["w_boat"]["SCALE"]
        self.buffer = self.scale[0]
        self.square = pygame.Surface(self.scale)
        self.square_highlight_buffer = constant.SQ_SIZE // 5

        self.resources_square = pygame.Surface((self.menu_width, round(a)))
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        self.resources_square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.resources_square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.resource_highlight_height = round(constant.BOARD_HEIGHT_PX * 4 / 5)
        self.reset_map_display_x = (
                self.menu_width // 2 - self.reset_map_image.get_width() // 2
        )
        self.reset_map_display_y = (
                constant.BOARD_HEIGHT_PX
                - self.resources_square.get_height() // 2
                - self.map_image_height // 2
        )

    def draw(self):
        self.menu.fill(constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)

        y_buffer = constant.SQ_SIZE // 2
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

        self.win.blit(self.menu, (constant.BOARD_WIDTH_PX, 0))

    def left_click(self):
        starting = False
        pos = pygame.mouse.get_pos()
        if pos[0] > constant.BOARD_WIDTH_PX:
            menu_mouse_x_position = pos[0] - constant.BOARD_WIDTH_PX
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
                    if not constant.DEBUG_START:
                        new_state = "select starting pieces"
                        self.engine.set_state(new_state)
                    else:
                        new_state = "debug"
                        self.engine.set_state(new_state)
            if pos[1] in range(self.r, self.menu_height):
                self.engine.reset_board()
                self.engine.generate_resources()
                self.reset_map_image = constant.RESOURCES[
                    random.choice(constant.resources)
                ]
                self.reset_map_display_x = (
                        self.menu_width // 2 - self.reset_map_image.get_width() // 2
                )
                self.reset_map_display_y = (
                        constant.BOARD_HEIGHT_PX
                        - self.resources_square.get_height() // 2
                        - self.map_image_height // 2
                )
                self.faction_name = self.reselect_faction_name()

    def reselect_faction_name(self):
        rand = random.randint(0, len(constant.FACTION_NAMES) - 1)
        return constant.FACTION_NAMES[rand]

    def reselect_menu_color(self):
        rand = random.randint(0, 2)
        if rand == 0:
            return constant.WHITE
        else:
            return constant.BLACK

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
        if mouse_x > constant.BOARD_WIDTH_PX:
            # Calculate the mouse's position relative to the menu
            menu_mouse_x_position = mouse_x - constant.BOARD_WIDTH_PX

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


class Surrender(SideBar):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.fontSize = round(constant.SQ_SIZE // 3)
        self.font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.fontSize
        )
        self.surrender_text = "Surrender?"
        self.yes_text = "yes"
        self.no_text = "no"
        self.surrender_text_surface = self.font.render(
                self.surrender_text, True, constant.turn_to_color[self.engine.turn]
        )
        self.yes_button_address = self.engine.turn + "_" + self.yes_text
        self.no_button_address = self.engine.turn + "_" + self.no_text
        self.yes_button_image = constant.IMAGES[self.yes_button_address]
        self.no_button_image = constant.IMAGES[self.no_button_address]
        self.question_display_y = (
                self.menu_height // 2 - self.surrender_text_surface.get_height() // 2
        )
        self.question_display_x = (
                self.menu_width // 2 - self.surrender_text_surface.get_width() // 2
        )
        self.buffer = constant.SQ_SIZE // 2
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
        self.square = pygame.Surface(constant.YES_NO_BUTTON_SCALE)
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
        if mouse_x > constant.BOARD_WIDTH_PX:
            # Calculate the mouse's position relative to the menu
            menu_x = mouse_x - constant.BOARD_WIDTH_PX

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
        if pos[0] > constant.BOARD_WIDTH_PX:
            menu_x = pos[0] - constant.BOARD_WIDTH_PX
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
        self.menu.fill(constant.MENU_COLOR)
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
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.win.blit(self.menu, (constant.BOARD_WIDTH_SQ * constant.SQ_SIZE, 0))


class Hud(SideBar):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.title_icon_width = constant.IMAGES["w_game_name"].get_width()
        self.title_icon_height = constant.IMAGES["w_game_name"].get_height()
        self.title_icon_display_x = self.menu_width // 2 - self.title_icon_width // 2
        self.title_icon_display_y = self.menu_height // 8 - self.title_icon_height // 2
        self.font_size = constant.SQ_SIZE // 2
        self.small_font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size // 2
        )

        self.font = pygame.font.Font(
                os.path.join("files/fonts", "font.ttf"), self.font_size
        )
        self.counter_icon_display_x = constant.BOARD_WIDTH_PX + 10
        self.coin_icon_display_y = round(self.menu_height * (8 / 10))
        self.icon_y_offset = constant.SQ_SIZE // 1.2
        self.stone_icon_display_y = self.coin_icon_display_y + self.icon_y_offset
        self.log_icon_display_y = self.coin_icon_display_y - self.icon_y_offset
        self.prayer_icon_display_y = self.log_icon_display_y - self.icon_y_offset
        self.action_icon_display_y = self.prayer_icon_display_y - self.icon_y_offset
        self.units_icon_display_y = self.action_icon_display_y - self.icon_y_offset
        self.turn_icon_display_y = self.units_icon_display_y - self.icon_y_offset
        self.bar_end_width = constant.IMAGES["prayer_bar_end"].get_width()
        self.bar_width = constant.IMAGES["prayer_bar"].get_width()
        self.bar_height = constant.IMAGES["prayer_bar"].get_height()
        self.counter_text_buffer = constant.SQ_SIZE // 2
        self.prayer_bar_height = (
                self.prayer_icon_display_y
                + round(constant.MENU_ICONS["prayer"].get_height() // 2)
                - round(self.bar_height // 2)
        )
        self.prayer_bar_edge = self.counter_icon_display_x + self.counter_text_buffer
        self.prayer_bar_end_edge = self.prayer_bar_edge + self.bar_width
        self.empty_text_surface = self.font.render("0", True, constant.WHITE)
        self.text_vertical_offset = (
                self.empty_text_surface.get_height() // 2
                - constant.MENU_ICONS["log"].get_height() // 2
        )
        self.square = pygame.Surface(
                (constant.SIDE_MENU_WIDTH, round(constant.SIDE_MENU_HEIGHT * 0.25))
        )
        self.title_bar_highlight = False
        self.square.set_alpha(constant.HIGHLIGHT_ALPHA)
        self.square.fill(constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def draw(self):
        self.menu.fill(constant.MENU_COLOR)
        # Draw paper texture blended with background
        self.engine.get_current_state().draw_paper_texture(self.menu)
        if constant.DISPLAY_STATE_IN_HUD:
            state_text_surf = self.small_font.render(
                    str(self.engine.state[-1]),
                    True,
                    constant.turn_to_color[self.engine.turn],
            )
            selected = self.small_font.render(
                    str(self.engine.update_previously_selected()),
                    True,
                    constant.turn_to_color[self.engine.turn],
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
                constant.IMAGES[self.engine.turn + "_game_name"],
                (self.title_icon_display_x, self.title_icon_display_y),
        )
        self.win.blit(self.menu, (constant.BOARD_WIDTH_PX, 0))

        # Gold Counter
        if not self.engine.players[self.engine.turn].gold == 0:
            self.win.blit(
                    constant.IMAGES["gold_coin"],
                    (self.counter_icon_display_x, self.coin_icon_display_y),
            )
            white_coin_text = self.font.render(
                    str(self.engine.players[self.engine.turn].gold),
                    True,
                    constant.turn_to_color[self.engine.turn],
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
                    constant.IMAGES["log"],
                    (self.counter_icon_display_x, self.log_icon_display_y),
            )
            white_log_text = self.font.render(
                    str(self.engine.players[self.engine.turn].wood),
                    True,
                    constant.turn_to_color[self.engine.turn],
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
                    constant.IMAGES["stone"],
                    (self.counter_icon_display_x, self.stone_icon_display_y),
            )
            white_log_text = self.font.render(
                    str(self.engine.players[self.engine.turn].stone),
                    True,
                    constant.turn_to_color[self.engine.turn],
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
                    constant.MENU_ICONS["prayer"],
                    (self.counter_icon_display_x, self.prayer_icon_display_y),
            )
            self.win.blit(
                    constant.IMAGES["prayer_bar"],
                    (self.prayer_bar_edge, self.prayer_bar_height),
            )
            for x in range(self.engine.players[self.engine.turn].prayer):
                new_edge = self.prayer_bar_end_edge + self.bar_end_width * (x)
                self.win.blit(
                        constant.IMAGES["prayer_bar_end"],
                        (new_edge, self.prayer_bar_height),
                )

        # Actions Remaining Counter
        self.win.blit(
                constant.IMAGES["action"],
                (self.counter_icon_display_x, self.action_icon_display_y),
        )
        actions_remaining_text = self.font.render(
                str(self.engine.players[self.engine.turn].get_actions_remaining()),
                True,
                constant.turn_to_color[self.engine.turn],
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
                constant.IMAGES["units"],
                (self.counter_icon_display_x, self.units_icon_display_y),
        )
        t = (
                str(self.engine.players[self.engine.turn].get_current_population())
                + "/"
                + str(self.engine.players[self.engine.turn].get_piece_limit())
        )
        units_text = self.font.render(t, True, constant.turn_to_color[self.engine.turn])
        self.win.blit(
                units_text,
                (
                    (self.counter_icon_display_x + self.counter_text_buffer),
                    self.units_icon_display_y - self.text_vertical_offset,
                ),
        )

        # Turn Counter
        self.win.blit(
                constant.IMAGES["hour_glass"],
                (self.counter_icon_display_x, self.turn_icon_display_y),
        )
        turn_number_text = str(self.engine.turn_count_display)
        text_surf = self.font.render(
                turn_number_text, True, constant.turn_to_color[self.engine.turn]
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
        if pos[0] > constant.BOARD_WIDTH_PX:
            # Check if the mouse is over the title bar area (top 25% of the screen)
            if 0 < pos[1] < constant.BOARD_HEIGHT_PX * 0.25:
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
        if pos[0] > constant.BOARD_WIDTH_PX:
            if 0 < pos[1] < constant.BOARD_HEIGHT_PX * 0.25:
                return self.engine.transfer_to_piece_cost_screen()
