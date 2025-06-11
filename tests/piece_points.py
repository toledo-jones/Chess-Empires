from __future__ import annotations

import typing

from player import Player
from state import Pause

if typing.TYPE_CHECKING:
    from unit import *

from engine import Engine
import constant
from tile import Tile


def test_piece_points() -> dict[str, int]:
    """
    Tests the value of pieces by the number of open squares they control on a board, of which they can capture a piece.
    :return: dictionary mapping piece names
            to their point values based on the number of controlled squares. {piece: points}
    """"""
    :return: 
    """
    # Example:
    #     PIECE_POINT_VALUES = {
    #     "king": 0,
    #     "gold_general": 0,
    #     "quarry_1": 6,
    #     "pawn": 12,
    #     "ferz": 12,
    #     "builder": 13,
    #     "monk": 16,
    #     "pikeman": 20,
    #     "castle": 20,
    #     "stable": 50,
    #     "barracks": 50,
    #     "fortress": 50,
    #     "queen": 95,
    #     "rook": 63,
    #     "bishop": 45,
    #     "knight": 12,
    #     "jester": 40,
    #     "rogue_rook": 90,
    #     "rogue_bishop": 50,
    #     "rogue_knight": 25,
    #     "rogue_pawn": 12,
    #     "elephant": 40,
    #     "ram": 40,
    #     "unicorn": 60,
    #     "monolith": 50,
    #     "prayer_stone": 26,
    #     "duke": 95,
    #     "oxen": 80,
    #     "champion": 75,
    #     "wall": 9,
    #     "persuader": 30,
    #     "doe": 50,
    #     "trader": 12,
    #     "circus": 50,
    #     "trapper": 14,
    #     "trap": 4,
    #     "lion": 90,
    #     "fire_spinner": 33,
    #     "acrobat": 75,
    #     "magician": 30,
    #     "cavalry": 28,
    #     "assassin": 33,
    # }
    # Empty dictionary to hold piece names and their point values. {"piece_name": points}
    piece_points = {}

    # The test board will be 9x9. The piece will be placed in the center at (4, 4).
    rows: int = 9
    cols: int = 9

    # Initialize the game board with Tile objects
    board: list[list[Tile]] = [
        [Tile(x, y) for y in range(cols)] for x in range(rows)
    ]

    # Create the engine to manage piece interactions on the board. We will not use any drawing or GUI features here.
    engine: Engine = Engine(window=None, board=board)

    # Create players to hold the pieces. We will not use any player-specific features here.
    engine.players = {"w": Player("w"), "b": Player("b")}

    # Iterate through all the pieces defined in the engine and calculate their point values.
    for piece_name in engine.PIECES:
        # Manually set the turn to white for this test. This is completely arbitrary, as we are not playing a game.
        engine.turn = "w"

        # Spawn the piece at the center of the board (4, 4) to test its capture squares.
        tested_piece = engine.spawn(4, 4, piece_name)

        # Update the squares to calculate the capture squares for the piece.
        engine.turn = "b"

        # Point value starts at 0
        piece_point_value = 0

        # Go through each square on the board and check how many squares the piece can capture.
        for row in range(rows):
            for col in range(cols):

                if (row, col) == (4, 4):
                    # Skip the square where the piece is currently placed.
                    continue

                # Spawn a pawn at the current square to test the piece's capture squares.
                engine.spawn(row, col, "pawn")

                # Update the squares to see if the piece can capture the pawn.
                engine.update_squares()

                # If the piece can capture the pawn, increment the point value.
                if tested_piece.capture_squares_list:
                    # Increment point value
                    piece_point_value += 1

                # Delete the pawn from the board after checking.
                engine.delete_piece(row, col)

        # After checking all squares, store the piece name and its point value in the dictionary.
        piece_points[piece_name] = piece_point_value

        # Delete the piece from the board after testing.
        engine.delete_piece(4, 4)

    hard_coded_points = {
        'monk'        : 4,
        'jester'      : 6,
        'prayer_stone': 4,
        'monolith'    : 8,
        'wall'        : 6,
        'persuader'   : 8,
        'trader'      : 4,
        'trap'        : 1,
        'magician'    : 8,
        "war_tower"   : 32,
    }
    for key, value in hard_coded_points.items():
        piece_points[key] = value
    unassigned_points: dict[str, None] = {}
    for key, value in piece_points.items():
        if piece_points[key] == 0:
            unassigned_points[key] = None
    print(f"Unassigned points: {unassigned_points}")

    for key, value in unassigned_points.items():
        total = 0
        pieces_spawnable = constant.SPAWN_LISTS[key]
        for piece in pieces_spawnable:
            total += piece_points[piece]

        total_points = total // len(pieces_spawnable)
        piece_points[key] = int(total_points)

    return piece_points


if __name__ == "__main__":
    points = test_piece_points()
    print(f"{points}")
