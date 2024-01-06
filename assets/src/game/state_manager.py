class StateManager:
    def __init__(self):
        self.current_state = None

    def set_state(self, new_state):
        self.current_state = new_state

    @property
    def get_current_state(self):
        return self.current_state
