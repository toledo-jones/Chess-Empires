import pygame


class InputHandler:
    def __init__(self, event_system):
        self.event_system = event_system

    def handle_input(self, pygame_event):
        # Process pygame events
        # this or
        if pygame_event.type == pygame.QUIT:
            return {"event_type": "quit"}

        # this for handling events
        if pygame_event.type == pygame.MOUSEMOTION:
            data = {"type": 'mouse move', "x": pygame_event.pos[0], "y": pygame_event.pos[1]}
            self.event_system.emit("mouse move", data)



