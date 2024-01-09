from src.utilities.singleton import Singleton


class StateManager(Singleton):
    def __init__(self, event_system):
        self.current_state = None
        self.event_system = event_system

    def set_state(self, new_state):
        self.current_state = new_state

    @property
    def get_current_state(self):
        return self.current_state
