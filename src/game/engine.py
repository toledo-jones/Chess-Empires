from src.utilities.singleton import Singleton
from src.utilities.sprite_factory import SpriteFactory
import pygame


class GameEngine(Singleton):

    def __init__(self, screen, input_handler, event_system, scene_manager, state_manager):
        self.input_handler = input_handler
        self.event_system = event_system
        self.scene_manager = scene_manager
        self.state_manager = state_manager
        self.screen = screen
        self.sprites = SpriteFactory.loaded_images
        logical_screen_dimensions = (1280, 640)
        self.aspect_ratio = (16 / 9)
        self.logical_screen = pygame.Surface(logical_screen_dimensions)
        self.scale_factor_x, self.scale_factor_y = self.calculate_scale_factor(self.logical_screen, self.screen)
        self.handle_window_resize(self.screen.get_size())
        self.event_system.subscribe("draw sprite", self.draw_sprite)

    def calculate_scale_factor(self, logical_screen, screen):
        scale_factor_x = logical_screen.get_width() / screen.get_width()
        scale_factor_y = logical_screen.get_height() / screen.get_height()
        return scale_factor_x, scale_factor_y

    def get_logical_screen_offset(self):
        # Get the current screen size
        screen_width, screen_height = self.screen.get_size()

        # Calculate the offset for the logical screen
        offset_x = (screen_width - self.logical_screen.get_width()) // 2
        offset_y = (screen_height - self.logical_screen.get_height()) // 2

        return offset_x, offset_y

    def scale_logical_screen(self, new_size):
        # Get the dimensions of the logical screen
        logical_width, logical_height = self.logical_screen.get_size()

        # Calculate the new dimensions while preserving the aspect ratio
        new_width = int(min(new_size[0], new_size[1] * self.aspect_ratio))
        new_height = int(new_width / self.aspect_ratio)

        # Check if scaling down is necessary
        if new_size[0] < logical_width or new_size[1] < logical_height:
            # Scale down the logical screen
            self.logical_screen = pygame.transform.scale(self.logical_screen, (new_width, new_height))
        else:
            # Check if scaling up is possible
            if new_size[0] > logical_width or new_size[1] > logical_height:
                # Scale up the logical screen
                self.logical_screen = pygame.transform.scale(self.logical_screen, (new_width, new_height))

        # Update scale factors based on the new logical screen size
        self.scale_factor_x, self.scale_factor_y = self.calculate_scale_factor(self.logical_screen, self.screen)

    def handle_window_resize(self, new_size):
        # Handle window resize
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)


        # Update scale factors based on the new window size
        self.scale_factor_x, self.scale_factor_y = self.calculate_scale_factor(self.logical_screen, self.screen)

    def handle_window_resize(self, new_size):
        # Handle window resize
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)

        # Scale down logical screen if needed
        self.scale_logical_screen(new_size)

        # Update scale factors based on the new window size
        self.scale_factor_x, self.scale_factor_y = self.calculate_scale_factor(self.logical_screen, self.screen)

    def draw_sprite(self, data):
        # Assemble necessary data
        position = data.get('x'), data.get('y')
        sprite_path = data.get('sprite')
        sprite = self.sprites[sprite_path]
        dimensions = sprite.get_size()

        # Change raw data to scaled/converted data
        scaled_position = self.scale(position)
        scaled_dimensions = self.scale(dimensions)
        scaled_sprite = pygame.transform.scale(sprite, (int(scaled_dimensions[0]), int(scaled_dimensions[1])))
        converted_sprite = scaled_sprite.convert()

        # Draw the scaled sprite to the screen
        self.logical_screen.blit(converted_sprite, scaled_position)

        # DEBUG:
        print("-------------------------------------------")
        print(f"Screen Size is: {self.screen.get_size()}")
        print(f"Sprite image is: {sprite_path}")
        print(f"Requesting to draw sprite at: {position}. Scaling to: {scaled_position}")
        print(f"Sprite Size is {dimensions[0]} by {dimensions[1]}. Scaling to: {scaled_dimensions}")
        print(f"Scale Factor X is: {self.scale_factor_x} and Y: {self.scale_factor_y}")

    def draw_test_building(self):
        sprite_path = "entities/buildings/white/barracks.png"
        position = self.center_of_logical_screen()
        data = {"sprite": sprite_path, "x": position[0], "y": position[1]}
        # print("Drawing Building:")
        self.draw_sprite(data)

    def scale(self, coordinates):
        # Scale the position based on the current scale factors
        scaled_position = (coordinates[0] * self.scale_factor_x, coordinates[1] * self.scale_factor_y)
        return scaled_position

    def center_of_screen(self):
        return self.screen.get_width() // 2, self.screen.get_height() // 2

    def center_of_logical_screen(self):
        return self.logical_screen.get_width() // 2, self.logical_screen.get_height() // 2

    def clear_screens(self):
        self.screen.fill((1, 0, 0))
        self.logical_screen.fill((72, 61, 139))

    def render(self):
        self.draw_test_building()
        # Continue rendering
        self.scene_manager.render()
        offset = self.get_logical_screen_offset()
        self.screen.blit(self.logical_screen, offset)

    def update(self):
        # Scene manager will call state_manager.update()
        # Possibly centralize these calls?
        self.scene_manager.update()
