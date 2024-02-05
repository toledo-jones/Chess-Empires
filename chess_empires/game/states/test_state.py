from chess_empires.game.states.state import State


class TestState(State):
    def __init__(self, event_manager, state_manager):
        super().__init__(event_manager, state_manager)
        self.event_manager.subscribe("mouse move", self.handle_local_mouse_move)
        self.event_manager.subscribe("server mouse move", self.handle_server_mouse_move)
        self.mouse_position = None
        self.enemy_mouse_position = None
        self.offset = None

    def update(self):
        pass

    def enter(self):
        pass

    def draw_sprite(self, sprite, x, y):
        data = {"sprite": sprite, "type": 'draw sprite', "x": x, "y": y, 'origin': str(self)}
        self.event_manager.emit('draw sprite', data)

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
