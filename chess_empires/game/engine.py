from __future__ import annotations

from chess_empires.game.entities.sprite import Sprite
import typing
import pygame
import settings
from chess_empires.utilities.singleton import Singleton
from utilities.sprite_paths import SpriteFactory
from pathlib import Path

if typing.TYPE_CHECKING:
    from chess_empires.game.event_manager import EventManager
    from chess_empires.game.scene_manager import SceneManager
    from chess_empires.game.state_manager import StateManager


def convert_sprite_alphas(loaded_images: dict[str, pygame.Surface]) -> dict[str, pygame.Surface]:
    """
    Converts all loaded pygame surfaces with convert_alpha() to increase performance
    :param loaded_images : dictionary of surfaces, keys look like: 'entities/units/black/acrobat.png'
    :return: converted dictionary of surfaces
    """
    for key in loaded_images.keys():
        loaded_images[key] = loaded_images[key].convert_alpha()
    return loaded_images


def convert_to_world_position(
        screen_position: tuple[int, int],
        scale_factor: tuple[float, float],
        game_window_offset: tuple[int, int]) -> tuple[float, float]:
    """
    Converts a screen position into a world position
    :param screen_position: typically given with pygame.mouse.Pos()
    :param scale_factor: the ratio between the logical screen and the actual game window
    :param game_window_offset: how far in the game_window is from the edge of the window
    :return: world_position: the position inside the internal logical window
    """

    # Unpack Screen Position
    x, y = screen_position[0], screen_position[1]

    # Adjust for game window offset
    adjusted_x = x - game_window_offset[0]
    adjusted_y = y - game_window_offset[1]

    # To convert the Game Window to the Logical Screen DIVIDE. Game_Window / Scale Factor
    world_x = adjusted_x / scale_factor[0]
    world_y = adjusted_y / scale_factor[1]

    return world_x, world_y


def convert_from_world_position(
        world_position: tuple[float, float],
        scale_factor: tuple[float, float]) -> tuple[float, float]:
    """
    Converts a logical world position into a game window position
    :param world_position: a world position given by convert_to_world_position()
    :param scale_factor: the ratio between the logical screen and the actual game window
    :return: game window position scaled to fit properly within the actual screen
    """

    # Unpack World Position
    x, y = world_position[0], world_position[1]

    # To convert the Logical Screen to the Game Window MULTIPLY: Logical Screen * Scale Factor
    game_window_x = x * scale_factor[0]
    game_window_y = y * scale_factor[1]

    return game_window_x, game_window_y


def center_position(
        position: tuple[float, float],
        dimensions: tuple[int, int]) -> tuple[int, int]:
    """
    Calculate the top-left coordinates of a bounding box to center it at the given position.

    This function takes the position (center) and dimensions (width and height) of a bounding box
    and calculates the top-left coordinates needed to center the box at the specified position.

    :param position: A tuple representing the center coordinates (x, y) of the bounding box.
    :param dimensions: A tuple representing the dimensions (width, height) of the bounding box.

    :return: A tuple containing the top-left coordinates (x, y) of the bounding box to center it.
    """
    return int(position[0] - round(dimensions[0] / 2)), int(position[1] - round(dimensions[1] / 2))


class GameEngine(Singleton):
    def __init__(self,
                 window: pygame.Surface,
                 player_id: int,
                 event_manager: EventManager,
                 scene_manager: SceneManager,
                 state_manager: StateManager):
        """ Handles all rendering to the screen, window resizing, inputs and graphics

        :param window: the actual application window to render graphics to

        :param player_id: player identifier

        :param event_manager: internal system for syncing events between classes

        :param scene_manager: holds the different scene objects, such as pause, playing, etc

        :param state_manager: holds the different state objects such as spawning, praying, etc
        """
        # All attributes use the @property decorator paradigm
        self.player_id = player_id
        self.event_manager = event_manager
        self.scene_manager = scene_manager
        self.state_manager = state_manager

        # Initial window is set to an arbitrary size
        self.window = window

        # Discover sprite paths from base path
        base_path = "assets/sprites"
        all_sprite_paths = SpriteFactory.discover_sprite_paths(base_path)
        if not all_sprite_paths:
            print("No sprite paths found.")
            self.sprite_paths = None
        else:
            # Group sprite paths to be accessed like this:
            # self.sprite_paths['entities']['units']['white']['acrobat.png'] = Path object
            ungrouped_paths = SpriteFactory.load_images(all_sprite_paths, Path(base_path))
            self.sprite_paths = SpriteFactory.delineate_sprite_dictionary(ungrouped_paths)

        # Board object is passed in by game_manager
        self.board = None

        # After calculation the game window is scaled to an appropriate size for whatever window it is contained within
        self.aspect_ratio = (16 / 9)
        self.logical_screen_dimensions = settings.LOGICAL_GAME_WINDOW
        self.game_window = pygame.Surface(self.logical_screen_dimensions)
        self.scale_factor = (1.0, 1.0)

        # Menu texture
        self.menu_texture = Sprite(self.sprite_paths['icons']['menu']['paper.png'])

        # Scale game window to match initial starting window size.
        self.handle_window_resize(self.window.get_size())

        # TODO: event system event restructuring. Should I use objects?`
        self.event_manager.subscribe("draw sprite", self.render_sprite)
        self.event_manager.subscribe("draw board", self.render_board)
        self.event_manager.subscribe("test", self.render_sprite)

    def handle_window_resize(self, new_size: tuple[int, int]) -> None:
        """
        Updates the pygame.display and scales the game window after a window resize event
        :param new_size: (x, y): new size of the application window
        :return: None
        """
        # Handle window resize
        self.window = pygame.display.set_mode(new_size, pygame.RESIZABLE)

        # Scale down logical screen if needed
        self.scale_game_window(new_size)

        # Scale sprites to fit within the new game window
        # self.scale_sprites()

        # # Scale Board to fit within the new game window
        if self.board:
            self.board.handle_resize_event(self.game_window.get_size())

    def render_surface(self, surface, position, **kwargs) -> None:
        x, y = position

        # scaled_dimensions = self.scale_by_scale_factor(surface.get_size())

        screen_position = convert_from_world_position((x, y), self.scale_factor)

        # TODO: Do not scale sprites every tick. This is destroying performance
        # surface = pygame.transform.scale(surface, (int(scaled_dimensions[0]), int(scaled_dimensions[1])))

        centered_position = center_position(screen_position, surface.get_size())
        # Draw the scaled sprite to the screen
        self.game_window.blit(surface, centered_position, **kwargs)

    def handle_input(self, pygame_event: pygame.event) -> None:
        """
        Routes pygame events to the custom EventManager
        :param pygame_event: event from pygame event queue
        """
        if pygame_event.type == pygame.MOUSEMOTION:
            screen_position = pygame_event.pos

            # Mouse data is converted to world position using the attributes
            x, y = convert_to_world_position(screen_position, self.scale_factor, self.get_game_window_offset())
            data = {"type": 'mouse move', 'player_id': self.player_id, "x": x, "y": y, 'me': True, 'origin': str(self)}
            self.event_manager.emit("mouse move", data)

    def calculate_scale_factor(self) -> tuple[float, float]:
        """
        Calculate the scale factor for scaling the Logical Dimensions to the actual Game Window.

        To convert the Game Window to the Logical Screen,

        DIVIDE: Game_Window / Scale Factor

        To convert the Logical Screen to the Game Window,

        MULTIPLY: Logical Screen * Scale Factor
        :return: A tuple containing the scale factors for X and Y dimensions
        """
        # Calculate the scale factor for X dimension
        scale_factor_x = self.game_window.get_width() / self.logical_screen_dimensions[0]

        # Calculate the scale factor for Y dimension
        scale_factor_y = self.game_window.get_height() / self.logical_screen_dimensions[1]

        # Return the tuple containing the scale factors
        return scale_factor_x, scale_factor_y

    def scale_game_window(self, new_size: tuple[int, int]) -> None:
        """
        Called after every window resize to adjust the game window size, position on screen, and update the scale factor
        :param new_size: the new size of the actual screen (x, y)
        :return: None
        """
        # Define the aspect ratio
        aspect_ratio = self.aspect_ratio

        # Calculate the maximum width and height that fits within the screen size
        max_width = new_size[0]
        max_height = int(max_width / aspect_ratio)

        if max_height > new_size[1]:
            # If the calculated height exceeds the screen height, recalculate based on the height
            max_height = new_size[1]
            max_width = int(max_height * aspect_ratio)

        # Check if the width needs adjustment to be a multiple of 16
        width_remainder = max_width % 16
        if width_remainder != 0:
            max_width -= width_remainder + 16

        # Check if the height needs adjustment to be a multiple of 9
        height_remainder = max_height % 9
        if height_remainder != 0:
            max_height -= height_remainder + 9

        # Scale the logical screen
        self.game_window = pygame.transform.scale(self.game_window, (max_width, max_height))

        # Update scale factors based on the new window size
        self.scale_factor = self.calculate_scale_factor()

        # scale menu texture
        self.menu_texture.reload_surface_and_scale(self.game_window.get_size())

        # Convert
        self.game_window.convert()

    def get_game_window_offset(self) -> tuple[int, int]:
        """
        Gives the offset of the game window from the window.

        Multiply each offset by 2 to calculate the full difference in size of the game window and the screen
        :return: (x, y): how far the game window is from the edge of the screen
        """
        # Get the current screen size
        window_width, window_height = self.window.get_size()

        # Calculate the offset for the logical screen
        offset_x = (window_width - self.game_window.get_width()) // 2
        offset_y = (window_height - self.game_window.get_height()) // 2

        return offset_x, offset_y

    def scale_by_scale_factor(self, size: tuple[int, int]) -> tuple[int, int]:
        """
        Scales the given size by the scale factor.

        :param size:  tuple representing the original size (width, height).
        :return: tuple representing the scaled size based on the scale factor.
        The result is a tuple of integers (scaled_width, scaled_height).
        """
        scaled_width = int(size[0] * self.scale_factor[0])
        scaled_height = int(size[1] * self.scale_factor[1])
        return scaled_width, scaled_height

    def render_sprite(self, data: dict, **kwargs) -> None:
        """
        Renders a sprite on the screen based on the provided data.

        :param data: Dictionary containing sprite rendering information.
                     It should have keys 'x', 'y', and 'sprite'.
                     'x': x-coordinate of the sprite position.
                     'y': y-coordinate of the sprite position.
                     'sprite': Path to the sprite image.
        :param kwargs: Additional keyword arguments to customize rendering (optional).

        The method converts the provided data to a surface and position,
        retrieves the sprite image, and renders the surface on the screen.
        """
        # Convert data to surface and position
        # position = data.get('x'), data.get('y')
        # sprite_path = data.get('sprite')
        # surface = self.get_sprite_from_path(sprite_path)
        # self.render_surface(surface, position, **kwargs)

    def render_board(self, data: dict) -> None:
        """
        Renders the game board on the screen based on the provided data.

        :param data: Dictionary containing information for rendering the board.
                     The method expects a properly initialized 'board' attribute in the class.
        """
        # Determine position of board
        x, y = self.center_of_game_window

        # Render board surface
        self.board.render_tiles()
        self.render_surface(self.board.surface, (x, y))

    def center_of_window(self) -> tuple[int, int]:
        """
        Calculate the center coordinates of the main window.

        :return: A tuple containing the x and y coordinates of the window center.
        """
        return self.window.get_width() // 2, self.window.get_height() // 2

    @property
    def center_of_game_window(self) -> tuple[int, int]:
        """
        Calculate the center coordinates of the game window.

        :return: A tuple containing the x and y coordinates of the game window center.
        """
        return self.logical_screen_dimensions[0] // 2, self.logical_screen_dimensions[1] // 2

    def render_menu_texture(self) -> None:
        """
        Render a menu texture on the game window.

        The menu texture is placed at the center of the game window.

        :return: None
        """
        self.render_surface(self.menu_texture.image, self.center_of_game_window, special_flags=pygame.BLEND_RGBA_MULT)

    def clear_screens(self) -> None:
        """
        Clear the main window, game window, and render a menu texture.

        The main window is filled with black color, the game window is filled with
        a specified background color, and a menu texture is rendered at the center
        of the game window.

        :return: None
        """
        background_color = (39.6, 51.7, 28.1)
        self.window.fill((0, 0, 0))
        self.game_window.fill(background_color)
        self.render_menu_texture()

    def draw_test_grid(self) -> None:
        """
        Draws a grid on the game window for testing purposes.

        The grid is drawn with a specified size, color, and spacing.
        """
        screen_width = self.game_window.get_width()
        screen_height = self.game_window.get_height()
        grid_size = screen_width // 16
        grid_color = (0, 0, 0)

        for x in range(-screen_width // 2, screen_width // 2, grid_size):
            pygame.draw.line(self.game_window, grid_color, (x + screen_width // 2, 0),
                             (x + screen_width // 2, screen_height), 1)

        for y in range(-screen_height // 2, screen_height // 2, grid_size):
            pygame.draw.line(self.game_window, grid_color, (0, y + screen_height // 2),
                             (screen_width, y + screen_height // 2), 1)

    def render_game_window(self) -> None:
        """
        Renders the game window on the main window.

        The game window is blitted onto the main window with an offset.
        """
        offset = self.get_game_window_offset()
        self.window.blit(self.game_window, offset)

    # engine.py
    def render(self) -> None:
        """
        Renders the game components.

        This method calls the draw_test_grid() method to draw a test grid and
        can be extended to include rendering of other game components.
        """
        # Could the game engine go through all sprite groups and blit them here?
        self.render_menu_texture()
        self.draw_test_grid()

    def update(self):
        # Scene manager will call state_manager.update()
        # TODO: centralize manager calls
        self.scene_manager.update()

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, board):
        self._board = board

    @property
    def player_id(self):
        return self._player_id

    @player_id.setter
    def player_id(self, player_id):
        self._player_id = player_id

    @property
    def game_window(self):
        return self._game_window

    @game_window.setter
    def game_window(self, game_window):
        self._game_window = game_window

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, window: pygame.Surface):
        self._window = window

    @property
    def event_manager(self):
        return self._event_manager

    @event_manager.setter
    def event_manager(self, event_manager):
        self._event_manager = event_manager

    @property
    def scene_manager(self):
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, scene_manager):
        self._scene_manager = scene_manager

    @property
    def state_manager(self):
        return self._state_manager

    @property
    def sprite_paths(self) -> dict[str: dict]:
        return self._sprite_paths

    @sprite_paths.setter
    def sprite_paths(self, sprite_paths: dict[str: dict]) -> None:
        """
        Set sprites attribute
        :param sprite_paths: nested dictionary structure of sprite paths
        :return: None
        """
        self._sprite_paths = sprite_paths

    @state_manager.setter
    def state_manager(self, state_manager: StateManager):

        self._state_manager = state_manager

    @property
    def menu_texture(self):
        return self._menu_texture

    @menu_texture.setter
    def menu_texture(self, menu_texture: Sprite):
        self._menu_texture = menu_texture
