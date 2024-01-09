import pygame.display

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
        self.window = pygame.display.get_surface()
        self.mouse_position = None
        self.enemy_mouse_position = None
        self.sprites = SpriteFactory.loaded_images
        self.event_system.subscribe("mouse move", self.handle_mouse_move)

    def handle_mouse_move(self, data):
        # save new position
        if self.is_player_data(data):
            self.mouse_position = data["x"], data["y"]
        else:
            self.enemy_mouse_position = data["x"], data["y"]
        print(f"GameManager: {data}")

    def is_player_data(self, data):
        return self.client.get_player_id() == data['player_id']

    def render(self):
        if self.mouse_position:
            self.window.blit(self.sprites["entities/unused/black/boat.png"].convert(), (self.mouse_position[0], self.mouse_position[1]))
        if self.enemy_mouse_position:
            self.window.blit(self.sprites["entities/unused/white/boat.png"].convert(), (self.enemy_mouse_position[0], self.enemy_mouse_position[1]))

    def start_game(self):
        pass

    def initialize_player(self):
        pass

    def update(self):
        pass
