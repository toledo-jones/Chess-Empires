from abc import ABC, abstractmethod

class BaseScene(ABC):
    def __init__(self, event_system, state_manager):
        self.state_manager = state_manager
        self.event_system = event_system

    @abstractmethod
    def handle_input(self, keys_pressed):
        raise NotImplementedError("Subclasses must implement handle_input method.")

    @abstractmethod
    def render(self):
        raise NotImplementedError("Subclasses must implement render method.")

    @abstractmethod
    def update(self):
        raise NotImplementedError("Subclasses must implement update method.")

    @abstractmethod
    def enter(self):
        raise NotImplementedError("Subclasses must implement enter method.")

