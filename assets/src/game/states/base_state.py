class BaseState:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def handle_input(self, keys_pressed):
        raise NotImplementedError("Subclasses must implement handle_input method.")

    def draw(self):
        raise NotImplementedError("Subclasses must implement draw method.")
