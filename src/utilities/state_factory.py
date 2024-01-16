from src.game.states.base_state import BaseState
from src.utilities.class_discovery import discover_classes


class StateFactory:
    _registry = {}

    @classmethod
    def register(cls, _state_class):
        cls._registry[_state_class.__name__.lower()] = _state_class

    @classmethod
    def create(cls, state_name, *args, **kwargs):
        state_class = cls._registry.get(state_name.lower(), DefaultState)
        return state_class(*args, **kwargs)


class DefaultState:
    pass


# Automatically discover and register state classes
state_classes = discover_classes("game.states", BaseState)
for state_class in state_classes:
    StateFactory.register(state_class)
