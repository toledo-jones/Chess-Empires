from game.entities.units.unit import Unit


class Acrobat(Unit):
    def __init__(self, column, row, color):
        super().__init__(column, row, color)

    def __str__(self):
        return 'acrobat'
