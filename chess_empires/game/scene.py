from __future__ import annotations

from abc import ABC, abstractmethod

import typing
from typing import Never

if typing.TYPE_CHECKING:
    from chess_empires.game.event_manager import EventManager
    from chess_empires.game.scene_manager import SceneManager
    from chess_empires.game.state_manager import StateManager
    from enum import Enum
    from typing import Callable


class Scene(ABC):
    def __init__(self,
                 event_manager: EventManager,
                 scene_manager: SceneManager,
                 state_manager: StateManager,
                 events: dict[Enum: Callable]):
        """

        :param event_manager:
        :param scene_manager:
        :param state_manager:
        """

        self.state_manager = state_manager
        self.event_manager = event_manager
        self.scene_manager = scene_manager
        self.events = events

        self.event_manager.multi_subscribe(self.events)

    @abstractmethod
    def render(self) -> Never:
        raise NotImplementedError("Subclasses must implement render method.")

    @abstractmethod
    def update(self) -> Never:
        raise NotImplementedError("Subclasses must implement update method.")

    @abstractmethod
    def enter(self) -> Never:
        raise NotImplementedError("Subclasses must implement enter method.")

    def exit(self):
        # Release the references so the scene can be garbage collected
        self.event_manager.multi_unsubscribe(self.events)
        self.scene_manager = None
        self.state_manager = None
        self.event_manager = None
        self.events = None
