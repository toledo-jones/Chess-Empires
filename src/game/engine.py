import random

from src.utilities.singleton import Singleton
from src.utilities.sprite_factory import SpriteFactory
import pygame


def convert_sprite_alphas():
    loaded_images = SpriteFactory.loaded_images
    for key in loaded_images.keys():
        loaded_images[key] = loaded_images[key].convert_alpha()
    return loaded_images


class GameEngine(Singleton):

    def __init__(self, window, input_handler, event_system, scene_manager, state_manager):
        # Initialize all relevant attributes
        self.input_handler = input_handler
        self.event_system = event_system
        self.scene_manager = scene_manager
        self.state_manager = state_manager

        # Initial window is set to an arbitrary size
        self.window = window
        self.sprites = convert_sprite_alphas()

        # Logical coordinates will all be rendered within
        logical_screen_dimensions = (1600, 900)
        self.aspect_ratio = (16 / 9)
        self.game_window = pygame.Surface(logical_screen_dimensions)

        # Calculate initial scale factors. These factors convert between the game window and the actual window
        self.scale_factor_x, self.scale_factor_y = self.calculate_scale_factor(self.game_window, self.window)

        # Scale game window to match initial starting window size.
        self.handle_window_resize(self.window.get_size())

        self.event_system.subscribe("draw sprite", self.draw_sprite)
        self.event_system.subscribe("test", self.draw_sprite)

        self.debug_sprite_path = random.choice(list(self.sprites.keys()))

    @staticmethod
    def calculate_scale_factor(game_window, window):
        scale_factor_x = game_window.get_width() / window.get_width()
        scale_factor_y = game_window.get_height() / window.get_height()
        return scale_factor_x, scale_factor_y

    def scale_game_window(self, new_size):
        # Get the dimensions of the logical screen
        game_window_width, game_window_height = self.game_window.get_size()

        # Calculate the new dimensions while preserving the aspect ratio
        new_width = int(min(new_size[0], new_size[1] * self.aspect_ratio))
        new_height = int(new_width / self.aspect_ratio)

        # Check if scaling down is necessary
        if new_size[0] < game_window_width or new_size[1] < game_window_height:
            # Scale down the logical screen
            self.game_window = pygame.transform.scale(self.game_window, (new_width, new_height))
        else:
            # Check if scaling up is possible
            if new_size[0] > game_window_width or new_size[1] > game_window_height:
                # Scale up the logical screen
                self.game_window = pygame.transform.scale(self.game_window, (new_width, new_height))

        # Update scale factors based on the new window size
        self.scale_factor_x, self.scale_factor_y = self.calculate_scale_factor(self.game_window, self.window)

        # Convert
        self.game_window.convert()

    def get_game_window_offset(self):
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

    def draw_sprite(self, data):
        print("Drawing...")
        # Assemble necessary data
        position = data.get('x'), data.get('y')
        sprite_path = data.get('sprite')
        sprite = self.sprites[sprite_path]
        dimensions = sprite.get_size()

        # # Change raw data to scaled/converted data
        offset_x, offset_y = self.get_game_window_offset()

        scaled_position = position[0] - offset_x, position[1] - offset_y
        scaled_dimensions = (50, 50)
        scaled_sprite = pygame.transform.scale(sprite, (int(scaled_dimensions[0]), int(scaled_dimensions[1])))
        centered_position = scaled_position[0] - scaled_dimensions[0] // 2, scaled_position[1] - scaled_dimensions[1] // 2

        # Draw the scaled sprite to the screen
        self.game_window.blit(scaled_sprite, centered_position)

        # DEBUG:
        print(f"Screen Size is: {self.window.get_size()}")
        print(f"Sprite image is: {sprite_path}")
        print(f"Draw function called by: {data.get('origin')}")
        print(f"Requesting to draw sprite at: {position}. Scaling to: {scaled_position}")
        print(f"Sprite Size is {dimensions[0]} by {dimensions[1]}. Scaling to: {scaled_dimensions}")
        print(f"Scale Factor X is: {self.scale_factor_x} and Y: {self.scale_factor_y}")
        print(f"Screen Offsets: X = {offset_x} Y = {offset_y}")

    def draw_test_building(self):
        sprite_path = self.debug_sprite_path
        position = self.center_of_window()
        data = {"sprite": sprite_path, 'type': 'test', "x": position[0], "y": position[1], 'origin': str(self)}
        self.event_system.emit('test', data)

    def scale(self, coordinates):
        # Scale the position based on the current scale factors
        scaled_position = (coordinates[0] * self.scale_factor_x, coordinates[1] * self.scale_factor_y)
        return scaled_position

    def center_of_window(self):
        return self.window.get_width() // 2, self.window.get_height() // 2

    def center_of_game_window(self):
        return self.game_window.get_width() // 2, self.game_window.get_height() // 2

    def clear_screens(self):
        print("Clearing Screens")
        self.window.fill((0, 0, 0))
        self.game_window.fill((72, 61, 139))

    def render(self):
        self.draw_test_building()
        print(f"Drawing {self.game_window} to {self.window}")

    def render_game_window(self):
        offset = self.get_game_window_offset()
        self.window.blit(self.game_window, offset)

    def update(self):
        # Scene manager will call state_manager.update()
        # TODO: centralize manager calls
        self.scene_manager.update()
