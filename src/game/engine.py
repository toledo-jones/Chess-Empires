import random

from src.utilities.singleton import Singleton
from src.utilities.sprite_factory import SpriteFactory
import pygame
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
        self.sprites = convert_sprite_alphas(SpriteFactory.loaded_images)

        # Logical coordinates will all be rendered within
        self.logical_screen_dimensions = (1536, 864)
        self.aspect_ratio = (16 / 9)
        self.game_window = pygame.Surface(self.logical_screen_dimensions)

        # These are calculated after handling the initial window "resize" below.
        self.scale_factor = (None, None)

        # Scale game window to match initial starting window size.
        self.handle_window_resize(self.window.get_size())

        # Here the engine will subscribe to relevant events.
        # TODO: event system event restructuring. Should I use objects?`
        self.event_system.subscribe("draw sprite", self.draw_sprite)
        self.event_system.subscribe("test", self.draw_sprite)

        self.debug_sprite_path = random.choice(list(self.sprites.keys()))

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

    def draw_sprite(self, data):
        print("Drawing.........................................")
        # Assemble necessary data
        x, y = data.get('x'), data.get('y')
        sprite_path = data.get('sprite')
        sprite = self.sprites[sprite_path]
        dimensions = sprite.get_size()

        # # Change raw data to scaled/converted data
        offset_x, offset_y = self.get_game_window_offset()

        screen_position = convert_from_world_position((x, y), self.scale_factor, self.get_game_window_offset())
        scaled_dimensions = (50, 50)
        scaled_sprite = pygame.transform.scale(sprite, (int(scaled_dimensions[0]), int(scaled_dimensions[1])))
        centered_position = screen_position[0] - scaled_dimensions[0] // 2, screen_position[1] - scaled_dimensions[1] // 2

        # Draw the scaled sprite to the screen
        self.game_window.blit(scaled_sprite, centered_position)

        # DEBUG:
        print(f"Actual Window       =   {self.window.get_size()}")
        print(f"Logical Window      =   {self.logical_screen_dimensions}")
        print(f"Game Window         =   {self.game_window.get_size()}")
        print(f"Sprite Image        =   {sprite_path}")
        print(f"Function Called     =   {data.get('origin')}")
        print(f"Position Received   =   {screen_position}")
        print(f"Position Scaled     =   {screen_position}")
        print(f"Sprite Size         =   {dimensions[0]} x {dimensions[1]}")
        print(f"Sprite Scaled       =   {scaled_dimensions}")
        print(f"Scale Factor        =   {self.scale_factor[0]} x {self.scale_factor[1]}")
        print(f"Screen Offsets      =   {offset_x} x {offset_y}")

    def draw_test_building(self):
        sprite_path = self.debug_sprite_path
        position = self.center_of_window()
        data = {"sprite": sprite_path, 'type': 'test', "x": position[0], "y": position[1], 'origin': str(self)}
        self.event_system.emit('test', data)

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
        self.draw_test_grid()
        print(f"Drawing {self.game_window} to {self.window}")

    def draw_test_grid(self):
        SCREEN_WIDTH = self.game_window.get_width()
        SCREEN_HEIGHT = self.game_window.get_height()
        GRID_SIZE = SCREEN_WIDTH // 16
        GRID_COLOR = (0, 0, 0)

        for x in range(-SCREEN_WIDTH // 2, SCREEN_WIDTH // 2, GRID_SIZE):
            pygame.draw.line(self.game_window, GRID_COLOR, (x + SCREEN_WIDTH // 2, 0), (x + SCREEN_WIDTH // 2, SCREEN_HEIGHT), 1)

        for y in range(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2, GRID_SIZE):
            pygame.draw.line(self.game_window, GRID_COLOR, (0, y + SCREEN_HEIGHT // 2), (SCREEN_WIDTH, y + SCREEN_HEIGHT // 2), 1)

    def render_game_window(self):
        offset = self.get_game_window_offset()
        self.window.blit(self.game_window, offset)

    def update(self):
        # Scene manager will call state_manager.update()
        # TODO: centralize manager calls
        self.scene_manager.update()
