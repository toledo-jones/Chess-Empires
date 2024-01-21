from abc import ABC, abstractmethod


class Unit(ABC):
    def __init__(self, col, row, color):
        self.col = col
        self.row = row
        self.color = color
        self.sprite_path = f'entities/units/{str(color)}/{str(self)}.png'
        self.offset = None

    def render(self, board):
        x = (self.col * board.sq_size) + self.offset[0]
        y = (self.row * board.sq_size) + self.offset[1]
        data = {'sprite': self.sprite_path, 'x': x, 'y': y}
        return data

    @abstractmethod
    def __str__(self):
        raise NotImplementedError("Subclasses must implement __str__ method.")

