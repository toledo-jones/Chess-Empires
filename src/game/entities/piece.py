from abc import ABC, abstractmethod
from game.entities.sprite import Sprite


class Piece(Sprite, ABC):
    """
    Abstract base class representing a game piece.

    Subclasses must implement the abstract method __str__.
    """
    def __init__(self, column: int, row: int, color: str) -> None:
        """
        Initializes a Unit instance.

        :param column: The column position of the unit.
        :param row: The row position of the unit.
        :param color: The color of the unit, either 'white' or 'black'.
        """
        self.column: int = column
        self.row: int = row
        self.color: str = color
        self.sprite_path = self.path()
        super().__init__(self.sprite_path)


        self.offset: None or tuple[int, int] = None

    @abstractmethod
    def path(self) -> str:
        """
        Abstract method to be implemented by subclasses.

        :return: A string representation of the path
        """
        raise NotImplementedError("Subclasses must implement path method.")

    @property
    def color(self) -> str:
        """
        Gets the color of the unit.

        :return: The color of the unit, either 'white' or 'black'.
        """
        return self._color

    @color.setter
    def color(self, color: str) -> None:
        """
        Sets the color of the unit.

        :param color: The color to set, either 'white' or 'black'.
        """
        self._color = color





    @property
    def column(self) -> int:
        """
        Gets the column position of the unit.

        :return: The column position of the unit on the game board.
        """
        return self._column

    @column.setter
    def column(self, column: int) -> None:
        """
        Sets the column position of the unit.

        :param column: The column position to set on the game board.
        """
        self._column = column

    @property
    def row(self) -> int:
        """
        Gets the row position of the unit.

        :return: The row position of the unit on the game board.
        """
        return self._row

    @row.setter
    def row(self, row: int) -> None:
        """
        Sets the row position of the unit.

        :param row: The row position to set on the game board.
        """
        self._row = row

    @abstractmethod
    def __str__(self) -> str:
        """
        Abstract method to be implemented by subclasses.

        :return: A string representation of the unit.
        """
        raise NotImplementedError("Subclasses must implement __str__ method.")
