from src.game.scenes.scene import Scene


class GameScene(Scene):
    def __init__(self, event_manager, scene_manager, state_manager):
        super().__init__(event_manager, scene_manager, state_manager)

    def enter(self):
        pass

    def update(self):
        pass

    def render(self):
        self.event_manager.emit("draw board", data={})
