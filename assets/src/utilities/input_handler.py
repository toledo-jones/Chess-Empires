class InputHandler:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def handle_input(self, keys_pressed):
        current_state = self.state_manager.get_current_state

        if current_state:
            current_state.handle_input(keys_pressed)

    def get_input(self):
        pass
