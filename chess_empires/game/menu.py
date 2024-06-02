from __future__ import annotations

import typing
from abc import ABC
import pygame

if typing.TYPE_CHECKING:
    pass


class Menu(ABC):
    def __init__(self, size: tuple[int, int]):
        self.size = size
        self.surface = pygame.Surface(size)
        super().__init__(self.surface)

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @size.setter
    def size(self, size: tuple[int, int]):
        self._size = size

