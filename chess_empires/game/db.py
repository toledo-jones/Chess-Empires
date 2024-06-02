from __future__ import annotations

from functools import total_ordering
import typing
from enum import Enum, auto

from chess_empires.game.game_event import GameEvent

if typing.TYPE_CHECKING:
    pass

from functools import total_ordering
from enum import Enum, auto, EnumMeta


class CustomEnumMeta(EnumMeta):
    def __new__(cls, clsname, bases, classdict):
        new_cls = super().__new__(cls, clsname, bases, classdict)
        new_cls.__eq__ = lambda self, other: (
                isinstance(other, new_cls) and self.value == other.value
        )
        new_cls.__lt__ = lambda self, other: (
                isinstance(other, new_cls) and self.value < other.value
        )
        return new_cls


@total_ordering
class CustomEnum(Enum, metaclass=CustomEnumMeta):
    pass


class EventTypes(CustomEnum):
    GAME_EVENT = auto()


class Render(CustomEnum):
    BOARD = auto()
    HUD = auto()
    SPRITE = auto()
    INSPECTOR = auto()


class Input(CustomEnum):
    MOUSE_MOVE = auto()
    LEFT_CLICK = auto()
    RIGHT_CLICK = auto()
