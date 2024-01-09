from assets.src.utilities.singleton import Singleton


class GameEngine(Singleton):
    def __init__(self, input_handler, event_system, scene_manager, state_manager):
        self.input_handler = input_handler
        self.event_system = event_system
        self.scene_manager = scene_manager
        self.state_manager = state_manager


    def update(self):
        pass

    def render(self, screen):
        pass
