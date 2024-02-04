from src.utilities.singleton import Singleton
from src.game.entities.board import Board


class GameManager(Singleton):
    def __init__(self, event_manager, scene_manager, state_manager, client, engine):
        self.event_manager = event_manager
        self.scene_manager = scene_manager
        self.state_manager = state_manager
        self.engine = engine
        self.client = client
        self.board = Board(self.event_manager)

        self.engine.board = self.board

    def render(self):
        self.engine.render()
        self.scene_manager.render()
        self.state_manager.render()

        # After all other images are rendered output the logical screen to the main screen
        self.engine.render_game_window()

    def is_player_data(self, data):
        return self.client.get_player_id() == data['player_id']

    def start_game(self):
        self.scene_manager.set_scene('GameScene')
        self.state_manager.set_state('TestState')

    def initialize_player(self):
        pass

    def update(self):
        self.engine.update()
        self.scene_manager.update()
        self.state_manager.update()
