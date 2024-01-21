from src.utilities.factories.base_factory import BaseFactory, auto_register, DefaultClass
from src.game.states.base_state import BaseState


class StateFactory(BaseFactory):
    _default_class = DefaultClass


# Automatically discover and register scene classes
auto_register(StateFactory, "game.states", BaseState)
