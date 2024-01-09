import pygame


class InputHandler:
    def __init__(self, event_system, player_id):
        self.event_system = event_system
        self.player_id = player_id

    def handle_input(self, pygame_event):
        # this for handling events
        if pygame_event.type == pygame.MOUSEMOTION:
            data = {"type": 'mouse move', 'player_id': self.player_id, "x": pygame_event.pos[0], "y": pygame_event.pos[1]}
            self.event_system.emit("mouse move", data)
