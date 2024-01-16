from src.utilities.singleton import Singleton
from src.utilities.sprite_factory import SpriteFactory


class GameManager(Singleton):
    def __init__(self, input_handler, event_system, scene_manager, state_manager, client, engine):
        self.input_handler = input_handler
        self.event_system = event_system
        self.scene_manager = scene_manager
        self.state_manager = state_manager
        self.engine = engine
        self.client = client
        self.mouse_position = None
        self.enemy_mouse_position = None
        self.sprites = SpriteFactory.loaded_images
        self.event_system.subscribe("mouse move", self.handle_mouse_move)

    def render(self):
        self.engine.render()
        self.scene_manager.render()
        self.state_manager.render()

        # After all other images are rendered output the logical screen to the main screen
        self.engine.render_game_window()

    def handle_mouse_move(self, data):
        # save new position
        if self.is_player_data(data):
            self.mouse_position = data["x"], data["y"]
        else:
            self.enemy_mouse_position = data["x"], data["y"]

    def is_player_data(self, data):
        return self.client.get_player_id() == data['player_id']

    def start_game(self):
        pass

    def initialize_player(self):
        pass

    def update(self):
        self.engine.update()
        self.scene_manager.update()
        self.state_manager.update()
