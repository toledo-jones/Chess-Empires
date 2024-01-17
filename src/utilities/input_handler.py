import pygame
from src.utilities.helpers import convert_to_world_position


class InputHandler:
    def __init__(self, event_system, player_id):
        self.event_system = event_system
        self.player_id = player_id
        self.event_system.subscribe("window resize", self.handle_window_resize)

        # These values are all set by the engine initialing and whenever the user resizes the window.
        self.game_window_offset = None
        self.scale_factor = None
        self.game_window_size = None
        self.window_size = None

    def handle_window_resize(self, data):
        self.scale_factor = data.get('scale factor')
        self.game_window_size = data.get('game window')
        self.game_window_offset = data.get('offset')

    def handle_input(self, pygame_event):
        # Handle events in our custom event system
        if pygame_event.type == pygame.MOUSEMOTION:
            # Mouse data is converted to world position using the attributes
            screen_position = pygame_event.pos
            x, y = convert_to_world_position(screen_position, self.scale_factor, self.game_window_offset)
            data = {"type": 'mouse move', 'player_id': self.player_id, "x": x, "y": y, 'me': True, 'origin': str(self)}
            self.event_system.emit("mouse move", data)
