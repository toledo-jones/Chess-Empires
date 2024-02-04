import random
import pygame

from src.game.entities.sprite import Sprite

LIGHT_COLOR = pygame.Color((255, 255, 255, 255))
DARK_COLOR = (pygame.Color((66.3, 33.6, 21.4, 255)))


class Tile(Sprite):
    def __init__(self, column, row):
        self.column = column
        self.row = row
        self.texture_id = random.randint(0, 47)
        super().__init__(self.path)
        self.occupying = None
        self.resource = None

    @property
    def pattern_id(self):
        # Alternate colors based on row and column indices
        if (self.row + self.column) % 2 == 0:
            return True
        return False

    @property
    def texture(self):
        if self.pattern_id:
            return 'light'
        return 'dark'

    @property
    def color(self):
        if self.pattern_id:
            return LIGHT_COLOR
        return DARK_COLOR

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, row):
        self._row = row

    @property
    def column(self):
        return self._column

    @column.setter
    def column(self, column):
        self._column = column

    @property
    def path(self):
        # TODO: this should be calculated dynamically based on the number of images in the path
        return f'assets/sprites/board/{self.texture}/{self.texture_id}.png'

    @path.setter
    def path(self, path):
        self._path = path
