from __future__ import annotations

from typing import List, Tuple

import Constant


def quarter() -> Tuple[
    List[Tuple[int, int]],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
]:
    """
    Divides the board into four quadrants and returns a tuple of lists containing
    the coordinates for each quadrant.

    The quadrants are based on dividing the board into four regions:
    - Top left: (x < mid_x and y < mid_y)
    - Top right: (x > mid_x and y < mid_y)
    - Bottom left: (x < mid_x and y > mid_y)
    - Bottom right: (x > mid_x and y > mid_y)

    The division is done based on the board's maximum x and y values, and the
    midpoints of the x and y axes.

    :return: A tuple of four lists, where each list contains the coordinates
             (row, col) for a specific quadrant on the board.
    """
    # Initialize the four quadrants
    top_left, top_right, bottom_left, bottom_right = [], [], [], []

    # Get the maximum board indices (x and y)
    x_max, y_max = Constant.board_max_index()

    # Precompute the mid points to avoid redundant calculations
    mid_x = x_max // 2
    mid_y = y_max // 2

    # Define the row range
    min_row, max_row = 2, y_max - 1

    # Loop through all columns (x) and rows (r) to assign coordinates to each quarter
    for col in range(x_max + 1):
        for row in range(min_row, max_row):
            # Determine which quadrant the current coordinate belongs to
            if col > mid_x and row > mid_y:
                bottom_right.append((row, col))
            elif col < mid_x and row > mid_y:
                bottom_left.append((row, col))
            elif col > mid_x and row < mid_y:
                top_right.append((row, col))
            else:  # col < mid_x and row < mid_y
                top_left.append((row, col))

    # Return the four quadrants as a tuple of lists
    return top_left, top_right, bottom_left, bottom_right


def big_center() -> List[Tuple[int, int]]:
    """
    Generates a list of coordinates for a region in the center of the board.

    The region is defined by a specific range around the center of the board,
    with a width of 6 columns and the entire height of the board.

    :return: A list of tuples representing the coordinates in the center region.
    """
    squares: List[Tuple[int, int]] = (
        []
    )  # Initialize an empty list to store the coordinates

    # Get the maximum x (columns) and y (rows) values for the board
    x_max, y_max = Constant.board_max_index()

    # Define the range for the columns (around the center with 6 columns width)
    start_col = x_max // 2 - 2  # Starting column
    end_col = x_max // 2 + 4  # Ending column (exclusive)

    # Loop through each column in the defined range and all rows
    for col in range(start_col, end_col):
        for row in range(y_max + 1):
            # Add each (row, col) coordinate to the squares list
            squares.append((row, col))

    return squares  # Return the list of coordinates


def center() -> List[Tuple[int, int]]:
    """
    Returns the coordinates of the 2x2 center square area on the board.

    This function calculates the center of the board and returns the coordinates
    of the four squares in the center. The center is determined based on the
    maximum x and y values of the board, and the function returns the coordinates
    of the 2x2 area starting from the center.

    :return: A list of tuples where each tuple contains the (row, col) coordinates
             of a square in the center 2x2 area.
    """
    # Initialize an empty list to hold the coordinates of the center squares
    squares = []

    # Get the maximum x and y values of the board (the dimensions of the board)
    x, y = Constant.board_max_index()

    # Loop over the columns and rows to get the 2x2 center squares
    # The range is centered around x // 2 and y // 2
    for c in range(x // 2, x // 2 + 2):
        for r in range(y // 2, y // 2 + 2):
            # Append the (row, col) coordinates to the squares list
            square = (r, c)
            squares.append(square)

    # Return the list of coordinates for the center squares
    return squares


def quarter_triangle_a():
    bottom_left = []
    bottom_right = []
    top_left = []
    top_right = []
    # x, y equal max val col, row
    x, y = Constant.board_max_index()

    for r in range(6, y + 1):
        for c in range(0, r - 2):
            bottom_left.append((r, c))

    for r in range(6, y + 1):
        for c in range(x, x - (r - 2), -1):
            bottom_right.append((r, c))

    for r in range(0, 6):
        for c in range(6 - r, -1, -1):
            top_left.append((r, c))

    return bottom_left, bottom_right, top_left, top_right


def quarter_triangle_b():
    bottom_right = []
    top_left = []
    top_right = []
    # x, y equal max val col, row
    x, y = Constant.board_max_index()

    for r in range(6, y + 1):
        for c in range(x, x - (r - 2), -1):
            bottom_right.append((r, c))

    for r in range(0, 6):
        for c in range(6 - r, -1, -1):
            top_left.append((r, c))

    for r in range(0, 6):
        for c in range(x, x - (6 - r), -1):
            top_right.append((r, c))

    return bottom_right, top_left, top_right


def quarter_triangle_c():
    bottom_left = []
    bottom_right = []
    top_right = []
    # x, y equal max val col, row
    x, y = Constant.board_max_index()

    for r in range(6, y + 1):
        for c in range(0, r - 2):
            bottom_left.append((r, c))

    for r in range(6, y + 1):
        for c in range(x, x - (r - 2), -1):
            bottom_right.append((r, c))

    for r in range(0, 6):
        for c in range(x, x - (6 - r), -1):
            top_right.append((r, c))

    return bottom_left, bottom_right, top_right


def quarter_triangle_d():
    bottom_left = []
    top_left = []
    top_right = []
    # x, y equal max val col, row
    x, y = Constant.board_max_index()

    for r in range(5, y + 1):
        for c in range(0, r - 2):
            bottom_left.append((r, c))

    for r in range(0, 5):
        for c in range(5 - r, -1, -1):
            top_left.append((r, c))

    for r in range(0, 5):
        for c in range(x, x - (5 - r), -1):
            top_right.append((r, c))

    return bottom_left, top_left, top_right


def left_and_right_triangle_top():
    left_triangle = []
    right_triangle = []
    # x, y equal max val col, row
    y, x = Constant.board_max_index()

    # Top-left triangle (unchanged)
    for r in range(0, 7):  # Iterate over the rows starting from 0 to 6 (top)
        for c in range(
            0, 7 - r
        ):  # Left triangle: columns from 0 to (7 - r) for each row
            left_triangle.append((r, c))

    # Top-right triangle (cleaner and more efficient version)
    for r in range(0, 7):  # Iterate over the rows starting from 0 to 6 (top)
        # Define the maximum column to skip for each row (row r)
        skip_columns = set(range(7, 7 + r))  # Skip columns from 7 to 7+r-1 for each row

        # I don't understand why this needs to be done this way but I'm too lazy to figure it out
        for c in range(13, 6, -1):  # Iterate from column 13 to 7
            if c not in skip_columns:
                right_triangle.append((r, c))

    return left_triangle, right_triangle


def left_and_right_triangle_bottom():
    left_triangle = []
    right_triangle = []
    # x, y equal max val col, row
    x, y = Constant.board_max_index()

    for r in range(4, y + 1):
        for c in range(0, r - 2):
            left_triangle.append((r, c))

    for r in range(4, y + 1):
        for c in range(x, x - (r - 2), -1):
            right_triangle.append((r, c))

    return left_triangle, right_triangle


def top_and_bottom():
    top_squares = []
    bottom_squares = []

    # x, y equal max val col, row
    x, y = Constant.board_max_index()
    for c in range(3, x - 2):
        for r in range(1, 3):
            square = (r, c)
            top_squares.append(square)
        for r in range(y - 2, y):
            square = (r, c)
            bottom_squares.append(square)
    return top_squares, bottom_squares


def edge():
    squares = []
    # Get the maximum column and row indices (board size)
    x, y = Constant.board_max_index()

    # Top 2 rows
    for c in range(0, x + 1):
        for r in range(0, 2):  # Only the first 2 rows (0, 1)
            square = (r, c)
            squares.append(square)

    # Bottom 2 rows
    for c in range(0, x + 1):
        for r in range(y - 1, y + 1):  # Last 2 rows (y-2, y-1)
            square = (r, c)
            squares.append(square)

    return squares


def top_pyramid():
    squares = []
    x, y = Constant.board_max_index()
    height_of_island = min(x, y) // 2 - 1

    # Loop through rows
    for r in range(0, height_of_island):
        # Loop through columns
        for c in range(0, x + 1):
            # Check if the square is within the pyramid shape
            if c >= r and c < x - r + 1:
                squares.append((r, c))
            elif c >= x - r and c < r - 1:
                squares.append((r, c))

    return squares


def bottom_pyramid():
    squares = []
    x, y = Constant.board_max_index()
    height_of_pyramid = y // 2 + 1

    # Loop through rows in reverse order
    for r in range(y, height_of_pyramid, -1):
        for c in range(0, x + 1):
            # Check conditions to determine whether to append the square
            if (
                r == y
                or (r == y - 1 and 0 < c <= x - 1)
                or (r == y - 2 and 1 < c <= x - 2)
            ):
                squares.append((r, c))

    return squares


def center_circle():
    squares = []
    x, y = Constant.board_max_index()
    x += 1
    radius = 5
    increment = 0
    reached_peak = False
    for r in range(y // 2 - radius, y // 2 + radius):
        for c in range(x // 2 - increment, x // 2 + increment):
            square = (r, c)
            squares.append(square)
        if increment == radius:
            reached_peak = True
        if not reached_peak:
            increment += 1
        else:
            increment -= 1

    return squares


def quarter_triangle():
    bottom_left = []
    bottom_right = []
    top_left = []
    top_right = []
    x, y = Constant.board_max_index()

    # D TYPE:
    for r in range(5, y + 1):
        for c in range(0, r - 2):
            bottom_left.append((r, c))

    for r in range(y - 3, y + 1):
        for c in range(x, x - (r - 3), -1):
            bottom_right.append((r, c))

    for r in range(0, 5):
        for c in range(5 - r, -1, -1):
            top_left.append((r, c))

    for r in range(0, 5):
        for c in range(x, x - (5 - r), -1):
            top_right.append((r, c))

    return bottom_left, bottom_right, top_left, top_right


def quarter_triangle_e():
    bottom_left = []
    bottom_right = []
    top_left = []
    top_right = []
    x, y = Constant.board_max_index()

    for r in range(y - 3, y + 1):
        for c in range(0, r - 5):
            bottom_left.append((r, c))

    for r in range(y - 3, y + 1):
        for c in range(x, x - (r - 5), -1):
            bottom_right.append((r, c))

    for r in range(0, 4):
        for c in range(3 - r, -1, -1):
            top_left.append((r, c))

    for r in range(0, 4):
        for c in range(x, x - (4 - r), -1):
            top_right.append((r, c))

    return bottom_left, bottom_right, top_left, top_right


def top_third() -> list[tuple[int, int]]:
    """
    Returns a list of squares that are in the top 1/3 of the board.

    Args:
        rows (int): Total number of rows in the board.
        cols (int): Total number of columns in the board.

    Returns:
        list[tuple[int, int]]: List of (r, c) pairs in the top third.
    """
    cols, rows = Constant.board_max_index()
    top_limit = rows // 3  # Define upper bound for the top third
    return [(r, c) for r in range(top_limit) for c in range(cols)]


def bottom_third() -> list[tuple[int, int]]:
    """
    Returns a list of squares that are in the bottom 1/3 of the board.

    Args:
        rows (int): Total number of rows in the board.
        cols (int): Total number of columns in the board.

    Returns:
        list[tuple[int, int]]: List of (r, c) pairs in the bottom third.
    """
    cols, rows = Constant.board_max_index()
    bottom_start = rows - (rows // 3)  # Define lower bound for the bottom third
    return [(r, c) for r in range(bottom_start, rows) for c in range(cols)]


def left_right():
    left_squares, right_squares = [], []
    x, y = Constant.board_max_index()
    for r in range(0, y + 1):
        for c in range(0, 3):
            square = (r, c)
            left_squares.append(square)
        for c in range(x - 2, x + 1):
            square = (r, c)
            right_squares.append(square)
    return left_squares, right_squares


def alt_starting_a():
    w_starting_squares, b_starting_squares = [], []
    x, y = Constant.board_max_index()
    y_center = y // 2
    for c in range(1, 3):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            w_starting_squares.append(square)
    for c in range(x - 2, x):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            b_starting_squares.append(square)
    return w_starting_squares, b_starting_squares


def alt_starting():
    w_starting_squares, b_starting_squares = [], []
    x, y = Constant.board_max_index()
    y_center = y // 2
    for c in range(2, 4):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            w_starting_squares.append(square)
    for c in range(x - 3, x - 1):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            b_starting_squares.append(square)
    return w_starting_squares, b_starting_squares


def starting():
    w_starting_squares, b_starting_squares = [], []
    x, y = Constant.board_max_index()
    y_center = y // 2
    for c in range(0, 5):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            w_starting_squares.append(square)
    for c in range(x - 4, x + 1):
        for r in range(y_center - 2, y_center + 4):
            square = (r, c)
            b_starting_squares.append(square)
    return w_starting_squares, b_starting_squares


def outside_corner():
    c, r = Constant.board_max_index()
    squares = [(0, 0), (0, c), (r, c), (r, 0)]
    return squares


def find_center(squares: list[tuple[int, int]]) -> tuple[int, int]:
    """
    Calculates the center (centroid) of a list of (r, c) coordinate pairs.

    Args:
        squares (list[tuple[int, int]]): List of (row, column) pairs.

    Returns:
        tuple[float, float]: The center coordinates as (avg_r, avg_c).
    """
    if not squares:
        raise ValueError(
            "You must pass a list of square tuples [(row, col)] to Map.find_center"
        )

    total_r = sum(r for r, c in squares)
    total_c = sum(c for r, c in squares)
    count = len(squares)

    return total_r // count, total_c // count
