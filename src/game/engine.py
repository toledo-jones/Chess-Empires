from __future__ import annotations

import random
import typing
import pygame
import settings
from src.utilities.singleton import Singleton
from src.utilities.factories.sprite_factory import SpriteFactory

if typing.TYPE_CHECKING:
    from src.game.event_manager import EventManager
    from src.game.scene_manager import SceneManager
    from src.game.state_manager import StateManager


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
        world_position: tuple[int, int],
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


def center_position(position, dimensions):
    return position[0] - round(dimensions[0] / 2), position[1] - round(dimensions[1] / 2)


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

        # Board object is passed in by game_manager
        self.board = None

        self.all_sprite_keys = list(SpriteFactory.loaded_images.keys())

        # Convert sprites for performance
        ungrouped_sprites = convert_sprite_alphas(SpriteFactory.loaded_images)

        # Sprites can be accessed directly using a nested dictionary structure:
        # self.sprites['entities']['units']['white']['acrobat.png']
        # Alternatively you can call get_sprite_from_path('entities/units/white/acrobat.png')
        self.sprites = self.delineate_sprite_dictionary(ungrouped_sprites)

        self.default_sizes = {}
        self.populate_default_sizes()

        # After calculation the game window is scaled to an appropriate size for whatever window it is contained within
        self.aspect_ratio = (16 / 9)
        self.logical_screen_dimensions = settings.LOGICAL_GAME_WINDOW
        self.game_window = pygame.Surface(self.logical_screen_dimensions)

        # The ratio between the scaled logical window and the internal logical window
        self.scale_factor = (1.0, 1.0)

        # Default scaling of sprites
        self.default_scale_factors = {
            'entities': (1.0, 1.0),
            'board': (1.0, 1.0),  # Adjust the default scale factor for the 'board' category
            # Add more categories as needed
        }

        # Scale game window to match initial starting window size.
        self.handle_window_resize(self.window.get_size())

        # TODO: event system event restructuring. Should I use objects?`
        self.event_manager.subscribe("draw sprite", self.render_sprite)
        self.event_manager.subscribe("draw board", self.render_board)
        self.event_manager.subscribe("test", self.render_sprite)



        # Debug
        self.debug_sprite_path = random.choice(self.all_sprite_keys)

    @property
    def all_sprite_keys(self) -> list[str]:
        """
        Get every key for the sprite dictionary in the form of a path. '/entities/units/white/acrobat.png'
        :return: list of keys
        """
        return self._all_sprite_keys

    @all_sprite_keys.setter
    def all_sprite_keys(self, keys: list[str]) -> None:
        """
        Set every key for the sprite dictionary. Expected structure is '/entities/units/black/acrobat.png'
        :param keys: list of keys
        :return: None
        """
        self._all_sprite_keys = keys

    def set_sprite_from_path(self, path: str, sprite_surface: pygame.Surface) -> None:
        """
        Sets the sprite at the specified path in the self.sprites dictionary.
        :param path: Path starting below assets directory 'entities/units/white/acrobat.png'
        :param sprite_surface: pygame.Surface to set at the specified path
        :return: None
        """
        keys = path.split("/")
        current_dict = self.sprites

        # Traverse the dictionary to the second-to-last level
        for key in keys[:-1]:
            if key not in current_dict:
                current_dict[key] = {}
            current_dict = current_dict[key]

        # Set the sprite at the last level
        current_dict[keys[-1]] = sprite_surface
        print(sprite_surface)

    def get_sprite_from_path(self, path: str) -> pygame.Surface:
        """
        Converts path into sprite surface
        :param path: starting below assets directory 'entities/units/white/acrobat.png'
        :return: sprite as a pygame.Surface
        """
        keys = path.split("/")
        current_dict = self.sprites

        for key in keys[:-1]:
            current_dict = current_dict.get(key, {})

        # Use the last key to access the surface
        last_key = keys[-1]
        surface = current_dict.get(last_key)

        return surface

    def delineate_sprite_dictionary(self, ungrouped_sprites: dict[str, pygame.Surface]) -> dict[str, dict]:
        """
        Changes the sprite dictionary structure to be referenced like:
        sprites['entities']['units']['white']['acrobat.png']
        :param ungrouped_sprites: Dictionary of paths to pygame surfaces
        :return: A nested dictionary structure organizing different groupings of sprites
        """
        grouped_sprites = {}

        # Iterate through ungrouped_sprites and build the nested dictionary structure
        for path, surface in ungrouped_sprites.items():
            directory_structure = path.split("/")
            self.add_to_grouped_sprites(grouped_sprites, directory_structure, surface)

        # Now grouped_sprites contains the nested dictionary structure
        return grouped_sprites

    def add_to_grouped_sprites(self,
                               nested_dict: dict[str, dict],
                               keys: list[str],
                               surface: any) -> None:
        """
        Recursively adds a surface to the nested dictionary structure based on the keys.
        :param nested_dict: The nested dictionary to which the surface is added
        :param keys: List of keys representing the hierarchy in the dictionary
        :param surface: The pygame.Surface associated with the given path
        :return: None
        """
        if len(keys) == 1:
            # If there is only one key left, assign the surface to that key
            nested_dict[keys[0]] = surface
        else:
            key = keys[0]
            if key not in nested_dict:
                # If the key is not present, create an empty dictionary for it
                nested_dict[key] = {}
            # Recursively call add_to_grouped_sprites with the next level of keys
            self.add_to_grouped_sprites(nested_dict[key], keys[1:], surface)

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

    def populate_default_sizes_recursive(self, sprites, path_prefix=''):
        """
        Recursively populate the default_sizes dictionary with the true default sizes of sprites.
        :param sprites: Nested dictionary containing sprites
        :param path_prefix: Prefix representing the current path in the nested structure
        :return: None
        """
        for key, value in sprites.items():
            path = f"{path_prefix}/{key}" if path_prefix else key

            if isinstance(value, dict):
                # If the value is a dictionary, recursively call the function for the next depth
                self.populate_default_sizes_recursive(value, path)
            else:
                # Get the true default size of the sprite
                true_default_size = value.get_size()

                # Store the true default size in the dictionary
                self.default_sizes[path] = true_default_size

    def populate_default_sizes(self):
        """
        Populate the default_sizes dictionary with the true default sizes of sprites.
        This should be called once during initialization.
        """
        self.populate_default_sizes_recursive(self.sprites)

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

    def calculate_default_scaled_size(self, original_size, category=None):
        """
        Calculate the default scaled size for a sprite based on its category.
        :param original_size: Tuple (width, height) of the original size
        :param category: Category of the sprite (optional)
        :return: Tuple (width, height) of the default scaled size
        """
        # Your logic to determine the default scale factor for each category
        # For example, you might have a predefined dictionary of default scale factors for different categories

        default_factor = self.default_scale_factors.get(category, (1.0, 1.0))

        return (
            int(original_size[0] * default_factor[0]),
            int(original_size[1] * default_factor[1])
        )

    def scale_sprites_recursive(self, sprites, category=None, depth=0):
        """
        Recursively scale sprites in a nested dictionary structure.
        :param sprites: Nested dictionary of sprites
        :param category: Category of the sprites (optional)
        :param depth: Current depth in the nested structure
        :return: None
        """
        if isinstance(sprites, dict):
            for key, value in sprites.items():
                if isinstance(value, dict):
                    # Recursive call for nested dictionaries
                    self.scale_sprites_recursive(value, category, depth + 1)
                elif isinstance(value, pygame.Surface):
                    # Scale the sprite surface
                    true_default_size = self.calculate_true_default_size(value, category)
                    default_scaled_size = self.calculate_default_scaled_size(true_default_size, category)
                    scaled_surface = pygame.transform.scale(value, default_scaled_size)
                    game_scale_surface = pygame.transform.scale(
                        scaled_surface,
                        self.scale_by_scale_factor(scaled_surface.get_size()))
                    sprites[key] = game_scale_surface

    def calculate_true_default_size(self, surface, category=None):
        """
        Calculate the true default size of a sprite based on its category.
        :param surface: Pygame Surface
        :param category: Category of the sprite (optional)
        :return: Tuple (width, height) of the true default size
        """
        # Your logic to determine the true default size for each category
        # For example, you might have a predefined dictionary of true default sizes for different categories

        true_default_size = self.default_sizes.get(category, surface.get_size())
        print(f"{true_default_size} is default size for {category}")

        return true_default_size

    def scale_sprites(self):
        """
        Scale all sprites in the self.sprites dictionary using the default scale factors.

        For each sprite category, retrieves the sprites, scales them based on the default scale factor,
        and updates the sprites in the dictionary.

        :return: None
        """
        for category, sprites in self.sprites.items():
            self.scale_sprites_recursive(sprites, category)

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
        self.scale_sprites()

        # # Scale Board to fit within the new game window
        if self.board:
            self.board.handle_resize_event(self.game_window.get_size())

    def render_surface(self, surface, position, **kwargs):
        x, y = position

        # scaled_dimensions = self.scale_by_scale_factor(surface.get_size())

        screen_position = convert_from_world_position((x, y), self.scale_factor)

        # TODO: Do not scale sprites every tick. This is destroying performance
        # surface = pygame.transform.scale(surface, (int(scaled_dimensions[0]), int(scaled_dimensions[1])))

        centered_position = center_position(screen_position, surface.get_size())
        # Draw the scaled sprite to the screen
        self.game_window.blit(surface, centered_position, **kwargs)

    def scale_by_scale_factor(self, size):
        return int(size[0] * self.scale_factor[0]), int(size[1] * self.scale_factor[1])

    def render_sprite(self, data, **kwargs):
        # Convert data to surface and position
        position = data.get('x'), data.get('y')
        sprite_path = data.get('sprite')
        surface = self.get_sprite_from_path(sprite_path)
        self.render_surface(surface, position, **kwargs)

    def render_board(self, data):
        x, y = self.center_of_game_window()
        # Initial color fill
        # print(f"rendering board at {x} {y}")
        # print(f"board is {self.board.width} by {self.board.height}")
        light_color = pygame.Color((255, 255, 255, 255))
        dark_color = pygame.Color((66.3, 33.6, 21.4, 255))
        self.board.render_tiles(light_color, dark_color, self)
        self.render_surface(self.board.surface, (x, y))

    def draw_test_building(self):
        sprite_path = self.debug_sprite_path
        position = self.center_of_game_window()
        data = {"sprite": sprite_path, 'type': 'test', "x": position[0], "y": position[1], 'origin': str(self)}
        self.event_manager.emit('test', data)

    def center_of_window(self):
        return self.window.get_width() // 2, self.window.get_height() // 2

    def center_of_game_window(self):
        return self.logical_screen_dimensions[0] // 2, self.logical_screen_dimensions[1] // 2

    def render_menu_texture(self):
        path = 'icons/menu/paper.png'
        x, y = self.center_of_game_window()
        data = {'sprite': path, 'x': x, 'y': y}
        self.render_sprite(data, special_flags=pygame.BLEND_RGBA_MULT)

    def clear_screens(self):
        background_color = (39.6, 51.7, 28.1)
        self.window.fill((0, 0, 0))
        self.game_window.fill(background_color)
        self.render_menu_texture()

    def render(self):
        self.draw_test_grid()

    def draw_test_grid(self):
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

    def render_game_window(self):
        offset = self.get_game_window_offset()
        self.window.blit(self.game_window, offset)

    def update(self):
        # Scene manager will call state_manager.update()
        # TODO: centralize manager calls
        self.scene_manager.update()


    def set_board(self, board):
        self.board = board
        self.board.set_tile_pattern(tree_tile_sprites=(self.sprites['board']['light'], self.sprites['board']['dark']))

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
    def sprites(self) -> dict[str: dict]:
        return self._sprites

    @sprites.setter
    def sprites(self, sprites: dict[str: dict]) -> None:
        """
        Set sprites attribute
        :param sprites: nested dictionary structure of sprites
        :return: None
        """
        self._sprites = sprites

    @state_manager.setter
    def state_manager(self, state_manager: StateManager):

        self._state_manager = state_manager
