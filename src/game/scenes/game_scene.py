from src.game.scenes.base_scene import BaseScene


class GameScene(BaseScene):
    def __init__(self, event_system, scene_manager, state_manager):
        super().__init__(event_system, scene_manager, state_manager)

    def enter(self):
        pass

    def update(self):
        pass

    def render(self):
        self.event_system.emit("draw board", data={})
