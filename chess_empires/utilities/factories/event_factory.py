from chess_empires.utilities.factories.factory import BaseFactory, auto_register, DefaultClass
from chess_empires.game.game_event import GameEvent


class EventFactory(BaseFactory):
    _default_class = DefaultClass


# Automatically discover and register scene classes
auto_register(EventFactory, "game.events", GameEvent)
