from ...game.states import StateFactory


class GameScene:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        example_state = StateFactory.create("MiningState")

    def update(self, keys_pressed):
        self.states[current_state].handle_input(keys_pressed)

    def render(self):
        self.states[current_state].draw()