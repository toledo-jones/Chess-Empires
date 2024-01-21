import random
import pygame

import settings
from src.utilities.singleton import Singleton
from utilities.factories.sprite_factory import SpriteFactory
from src.utilities.helpers import convert_from_world_position, convert_sprite_alphas


class GameEngine(Singleton):
    def __init__(self, window, input_handler, event_system, scene_manager, state_manager):
        # Initialize all relevant attributes
        self.input_handler = input_handler
        self.event_system = event_system
        self.scene_manager = scene_manager
        self.state_manager = state_manager

        # Initial window is set to an arbitrary size
        self.window = window

        # Convert all sprites for performance.
        ungrouped_sprites = convert_sprite_alphas(SpriteFactory.loaded_images)
        self.sprites = self.delineate_sprite_dictionary(ungrouped_sprites)

        # Logical coordinates will all be rendered within
        self.logical_screen_dimensions = settings.LOGICAL_GAME_WINDOW
        self.aspect_ratio = (16 / 9)
        self.game_window = pygame.Surface(self.logical_screen_dimensions)

        # These are calculated after handling the initial window "resize" below.
        self.scale_factor = (None, None)

        # Scale game window to match initial starting window size.
        self.handle_window_resize(self.window.get_size())

        # Here the engine will subscribe to relevant events.
        # TODO: event system event restructuring. Should I use objects?`
        self.event_system.subscribe("draw sprite", self.render_sprite)
        self.event_system.subscribe("draw board", self.render_board)
        self.event_system.subscribe("test", self.render_sprite)

        # Board attribute is set by the set_board method and passed in from the game_manager as an argument
        self.board = None

        # Debug
        self.debug_sprite_path = random.choice(list(ungrouped_sprites.keys()))

    def get_sprite_from_path(self, path):
        keys = path.split("/")
        current_dict = self.sprites

        for key in keys[:-1]:
            current_dict = current_dict.get(key, {})

        # Use the last key to access the surface
        last_key = keys[-1]
        surface = current_dict.get(last_key)

        print(surface)
        return surface

    def delineate_sprite_dictionary(self, ungrouped_sprites):
        grouped_sprites = {}

        for path, surface in ungrouped_sprites.items():
            directory_structure = path.split("/")
            self.add_to_grouped_sprites(grouped_sprites, directory_structure, surface)

        # Now grouped_sprites contains the nested dictionary structure
        print(grouped_sprites)
        return grouped_sprites

    def add_to_grouped_sprites(self, nested_dict, keys, value):
        if len(keys) == 1:
            nested_dict[keys[0]] = value
        else:
            key = keys[0]
            if key not in nested_dict:
                nested_dict[key] = {}
            self.add_to_grouped_sprites(nested_dict[key], keys[1:], value)

    def calculate_scale_factor(self):
        """ Scale factor for scaling the Logical Screen to the Game Window """
        # To convert the Game Window to the Logical Screen DIVIDE. Game_Window / Scale Factor
        # To convert the Logical Screen to the Game Window MULTIPLY: Logical Screen * Scale Factor
        scale_factor_x = (self.game_window.get_width() / self.logical_screen_dimensions[0])
        scale_factor_y = (self.game_window.get_height() / self.logical_screen_dimensions[1])
        return scale_factor_x, scale_factor_y

    def scale_game_window(self, new_size):
        # Define the aspect ratio
        aspect_ratio = 16 / 9

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

    def get_game_window_offset(self):
        """ This returns a single offset on each axis. To calculate the full difference, multiply each offset by 2"""

        # Get the current screen size
        window_width, window_height = self.window.get_size()

        # Calculate the offset for the logical screen
        offset_x = (window_width - self.game_window.get_width()) // 2
        offset_y = (window_height - self.game_window.get_height()) // 2

        return offset_x, offset_y

    def handle_window_resize(self, new_size):
        # Handle window resize
        self.window = pygame.display.set_mode(new_size, pygame.RESIZABLE)

        # Scale down logical screen if needed
        self.scale_game_window(new_size)

        # Emit the window offsets, window size, game window size, and scale factor
        data = {'scale factor': self.scale_factor, 'game window': self.game_window.get_size(), 'offset': self.get_game_window_offset(), 'window': self.window.get_size()}
        self.event_system.emit('window resize', data)

    def render_surface(self, surface, position, **kwargs):
        x, y = position

        scaled_dimensions = self.scale_by_scale_factor(surface.get_size())

        screen_position = convert_from_world_position((x, y), self.scale_factor, self.get_game_window_offset())

        scaled_sprite = pygame.transform.scale(surface, (int(scaled_dimensions[0]), int(scaled_dimensions[1])))

        centered_position = screen_position[0] - scaled_dimensions[0] // 2, screen_position[1] - scaled_dimensions[1] // 2

        # Draw the scaled sprite to the screen
        self.game_window.blit(scaled_sprite, centered_position, **kwargs)

    def scale_by_scale_factor(self, size):
        return size[0] * self.scale_factor[0], size[1] * self.scale_factor[0]

    def render_sprite(self, data, **kwargs):
        # Convert data to surface and position
        position = data.get('x'), data.get('y')
        sprite_path = data.get('sprite')
        surface = self.get_sprite_from_path(sprite_path)
        self.render_surface(surface, position, **kwargs)

    def draw_test_building(self):
        sprite_path = self.debug_sprite_path
        position = self.center_of_game_window()
        data = {"sprite": sprite_path, 'type': 'test', "x": position[0], "y": position[1], 'origin': str(self)}
        self.event_system.emit('test', data)

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
        royal_purple = (72, 61, 139)
        self.window.fill((0, 0, 0))
        self.game_window.fill(royal_purple)
        self.render_menu_texture()

    def render(self):
        # self.draw_test_grid()
        pass

    def draw_test_grid(self):
        screen_width = self.game_window.get_width()
        screen_height = self.game_window.get_height()
        grid_size = screen_width // 16
        grid_color = (0, 0, 0)

        for x in range(-screen_width // 2, screen_width // 2, grid_size):
            pygame.draw.line(self.game_window, grid_color, (x + screen_width // 2, 0), (x + screen_width // 2, screen_height), 1)

        for y in range(-screen_height // 2, screen_height // 2, grid_size):
            pygame.draw.line(self.game_window, grid_color, (0, y + screen_height // 2), (screen_width, y + screen_height // 2), 1)

    def render_game_window(self):
        offset = self.get_game_window_offset()
        self.window.blit(self.game_window, offset)

    def update(self):
        # Scene manager will call state_manager.update()
        # TODO: centralize manager calls
        self.scene_manager.update()

    def render_board(self, data):
        x, y = self.center_of_game_window()
        # Initial color fill
        print(f"rendering board at {x} {y}")
        print(f"board is {self.board.width} by {self.board.height}")
        light_color = pygame.Color((238, 232, 170, 255))
        dark_color = pygame.Color((222, 184, 135, 255))
        self.board.render_tiles(light_color, dark_color, self)
        self.render_surface(self.board.surface, (x, y))

    def set_board(self, board):
        self.board = board
        self.board.set_tile_pattern(tree_tile_sprites=self.sprites['board'])
