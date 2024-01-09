from abc import ABC, abstractmethod
import pygame

class BaseScene(ABC):
    def __init__(self, event_system, scene_manager, state_manager):
        self.state_manager = state_manager
        self.event_system = event_system
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

