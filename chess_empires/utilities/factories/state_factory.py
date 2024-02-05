from chess_empires.utilities.factories.base_factory import BaseFactory, auto_register, DefaultClass
from chess_empires.game.states.state import State


class StateFactory(BaseFactory):
    _default_class = DefaultClass


# Automatically discover and register scene classes
auto_register(StateFactory, "game.states", State)
