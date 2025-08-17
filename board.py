from tile import Tile


class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid: list[list[Tile]] = [
            [Tile(x, y) for y in range(self.cols)] for x in range(self.rows)
        ]

    def __getitem__(self, index):
        return self.grid[index]

    def __setitem__(self, index, value):
        self.grid[index] = value

    def __len__(self):
        return len(self.grid)

    def to_dict(self):
        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": [
                [tile.to_dict() for tile in row]
                for row in self.grid
            ]
        }

    @staticmethod
    def from_dict(data):
        rows = data["rows"]
        cols = data["cols"]
        board = Board.__new__(Board)  # bypass __init__
        board.rows = rows
        board.cols = cols
        board.grid = [
            [Tile.from_dict(tile_data) for tile_data in row]
            for row in data["grid"]
        ]
        return board
