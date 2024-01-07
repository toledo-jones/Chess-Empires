from assets.src.game.states import StateFactory
from assets.src.game.scenes import BaseScene


class GameScene(BaseScene):
    def __init__(self, event_system, state_manager):
        super().__init__(event_system, state_manager)

        # Subscribe to input events
        self.event_system.subscribe("Jump", self.handle_jump_event)
        self.event_system.subscribe("Attack", self.handle_attack_event)

    def enter(self):
        print("Implemented enter method")

    def update(self):
        print("Implemented update method")

    def render(self):
        print("Implemented render method")

    def handle_input(self, data):
        print("Implemented handle_input method")

    def handle_jump_event(self, data):
        # Handle jump event logic
        print("Player jumped!")

    def handle_attack_event(self, data):
        # Handle attack event logic
        print("Player attacked!")
