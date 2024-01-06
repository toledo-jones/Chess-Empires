import importlib
import inspect
import pkgutil
from base_state import BaseState
from ...utilities.class_discovery import discover_classes


class StateFactory:
    _registry = {}

    @classmethod
    def register(cls, state_class):
        cls._registry[state_class.__name__.lower()] = state_class

    @classmethod
    def create(cls, state_name):
        return cls._registry.get(state_name.lower(), DefaultState)()


class DefaultState:
    pass


def discover_states():
    inner_state_classes = []
    for _, module_name, _ in pkgutil.walk_packages(__path__):
        module = importlib.import_module(f"{__name__}.{module_name}")
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseState) and obj != BaseState:
                inner_state_classes.append(obj)
    return inner_state_classes


# Automatically discover and register state classes
state_classes = discover_classes("game.states", BaseState)
for state_class in state_classes:
    StateFactory.register(state_class)
