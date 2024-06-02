from __future__ import annotations

import typing
from typing import Never
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from chess_empires.game.game_manager import GameManager


class GameEvent(ABC):
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager

    @abstractmethod
    def complete(self) -> Never:
        raise NotImplementedError("Child classes must implement complete method")

    @abstractmethod
    def undo(self) -> Never:
        raise NotImplementedError("Child classes must implement undo method")

    @property
    def game_manager(self) -> GameManager:
        """
        Get the game manager instance associated with the event.

        :return: The game manager instance.
        """
        return self._game_manager

    @game_manager.setter
    def game_manager(self, game_manager: GameManager):
        """
        Set the game manager instance associated with the event.

        :param game_manager: The game manager instance.
        """
        self._game_manager = game_manager
