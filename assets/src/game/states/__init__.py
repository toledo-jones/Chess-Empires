from assets.src.game.states.base_state import BaseState
from assets.src.utilities.class_discovery import discover_classes


class StateFactory:
    _registry = {}

    @classmethod
    def register(cls, _state_class):
        cls._registry[_state_class.__name__.lower()] = _state_class

    @classmethod
    def create(cls, scene_name, *args, **kwargs):
        scene_class = cls._registry.get(scene_name.lower(), DefaultState)
        return scene_class(*args, **kwargs)


class DefaultState:
    pass


# Automatically discover and register state classes
state_classes = discover_classes("assets.src.game.states", BaseState)
for state_class in state_classes:
    StateFactory.register(state_class)
