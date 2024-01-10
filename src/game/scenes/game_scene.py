from src.game.scenes.base_scene import BaseScene


class GameScene(BaseScene):
    def __init__(self, event_system, scene_manager, state_manager):
        super().__init__(event_system, scene_manager, state_manager)

        # Subscribe to input events
        self.event_system.subscribe("mouse move", self.handle_mouse_move)

    def enter(self):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def handle_mouse_move(self, data):
        pass