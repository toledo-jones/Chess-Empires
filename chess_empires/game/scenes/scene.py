from abc import ABC, abstractmethod


class Scene(ABC):
    def __init__(self, event_manager, scene_manager, state_manager):
        self.state_manager = state_manager
        self.event_manager = event_manager
        self.scene_manager = scene_manager

    @abstractmethod
    def render(self):
        raise NotImplementedError("Subclasses must implement render method.")

    @abstractmethod
    def update(self):
        raise NotImplementedError("Subclasses must implement update method.")

    @abstractmethod
    def enter(self):
        raise NotImplementedError("Subclasses must implement enter method.")
