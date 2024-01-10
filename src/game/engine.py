from src.utilities.singleton import Singleton
from src.utilities.sprite_factory import SpriteFactory
from src.utilities.enums import EventType
import pygame


class GameEngine(Singleton):
    def __init__(self, screen, input_handler, event_system, scene_manager, state_manager):
        self.input_handler = input_handler
        self.event_system = event_system
        self.scene_manager = scene_manager
        self.state_manager = state_manager
        self.screen = screen
        self.sprites = SpriteFactory.loaded_images
        self.logical_screen_width = 800  # Logical game window width
        self.logical_screen_height = 600  # Logical game window height
        self.scale_factor_x = 1.0  # Initial scale factor for X-axis
        self.scale_factor_y = 1.0  # Initial scale factor for Y-axis
        self.event_system.subscribe("draw sprite",  self.draw_sprite)

    def handle_window_resize(self, new_size):
        # Handle window resize
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)

        # Update scale factors based on the new window size
        self.scale_factor_x = new_size[0] / self.logical_screen_width
        self.scale_factor_y = new_size[1] / self.logical_screen_height

    def draw_sprite(self, data):
        # Scale the position and dimensions
        x = data.get("x")
        y = data.get("y")
        position = (x, y)
        sprite_path = data.get("sprite")
        sprite = self.sprites[sprite_path]
        dimensions = sprite.get_size()
        scaled_position = self.scale_position(position)
        scaled_dimensions = self.scale_dimensions(dimensions)

        # Scale the sprite to match the scaled dimensions
        scaled_sprite = pygame.transform.scale(sprite, (int(scaled_dimensions[0]), int(scaled_dimensions[1])))

        # convert the sprite before drawing it
        converted_sprite = scaled_sprite.convert()

        # Draw the scaled sprite to the screen
        self.screen.blit(converted_sprite, scaled_position)

    def scale_position(self, position):
        # Scale the position based on the current scale factors
        scaled_position = (position[0] * self.scale_factor_x, position[1] * self.scale_factor_y)
        return scaled_position

    def scale_dimensions(self, dimensions):
        # Scale the dimensions based on the current scale factors
        scaled_dimensions = (dimensions[0] * self.scale_factor_x, dimensions[1] * self.scale_factor_y)
        return scaled_dimensions

    def render(self):
        self.scene_manager.render()

    def update(self):
        self.scene_manager.update()

    def render_logical_window(self, game_manager):
        # Render the logical game window at the fixed resolution
        logical_surface = pygame.Surface((self.logical_screen_width, self.logical_screen_height))
        game_manager.render(logical_surface)  # Render the game to the logical surface

        # Scale the logical surface to fit the actual window size
        scaled_surface = pygame.transform.scale(logical_surface, self.screen.get_size())

        # Blit the scaled surface to the actual window
        self.screen.blit(scaled_surface, (0, 0))