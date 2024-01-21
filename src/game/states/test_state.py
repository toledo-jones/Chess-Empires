from utilities.enums import EventType
from src.game.states.base_state import BaseState


class TestState(BaseState):
    def __init__(self, event_system, state_manager):
        super().__init__(event_system, state_manager)
        self.event_system.subscribe("mouse move", self.handle_local_mouse_move)
        self.event_system.subscribe("server mouse move", self.handle_server_mouse_move)
        self.mouse_position = None
        self.enemy_mouse_position = None
        self.offset = None

    def update(self):
        pass

    def enter(self):
        pass

    def draw_sprite(self, sprite, x, y):
        data = {"sprite": sprite, "type": 'draw sprite', "x": x, "y": y, 'origin': str(self)}
        self.event_system.emit('draw sprite', data)

    def render(self):
        if self.mouse_position:
            sprite = "entities/unused/white/boat.png"
            x, y = self.mouse_position[0], self.mouse_position[1]
            self.draw_sprite(sprite, x, y)
        if self.enemy_mouse_position:
            sprite = "entities/unused/black/boat.png"
            x, y = self.enemy_mouse_position[0], self.enemy_mouse_position[1]
            self.draw_sprite(sprite, x, y)

    def handle_local_mouse_move(self, data):
        print("Received Client Mouse Move")
        self.mouse_position = data.get("x"), data.get("y")

    def handle_server_mouse_move(self, data):
        print("Received Server Mouse Move")
        self.enemy_mouse_position = data.get("x"), data.get("y")
