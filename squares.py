from __future__ import annotations

from typing import List, Tuple

import constant


def complete() -> List[Tuple[int, int]]:
    """
    Returns a list of all squares on the board.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square.
    """
    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Generate the list of coordinates for all squares
    return [(row, col) for row in range(max_row + 1) for col in range(max_col + 1)]


def custom(squares_list: list[list[str]]) -> list[tuple[int, int]]:
    """
    Converts a list of strings representing squares into a list of tuples.

    [[" ", " ", ... "x"]]

    Marking one of the squares with "x" will add it to the list of tuples.
    This is useful for map design when algorithms are too cumbersome to implement.

    Keep in mind these strings will have to be manually adjusted if the board size ever changes.
    Current height is 11 and current width is 14.
    :param squares_list: A list of lists containing string representations of squares.
    :return: A list of tuples where each tuple represents the coordinates (row, col) of a square.
    """
    #     The argument `squares_list` is a list of lists, where each inner list contains strings marked like this:
    # [
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    # ]
    squares = []
    for row in range(len(squares_list)):
        for col in range(len(squares_list[row])):
            if squares_list[row][col] == "x":
                squares.append((row, col))
    return squares


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
    x_max, y_max = constant.board_max_index()

    # Precompute the mid-points to avoid redundant calculations
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
    x_max, y_max = constant.board_max_index()

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
    x, y = constant.board_max_index()

    # Loop over the columns and rows to get the 2x2 center squares
    # The range is centered around x // 2 and y // 2
    for c in range(x // 2, x // 2 + 2):
        for r in range(y // 2, y // 2 + 2):
            # Append the (row, col) coordinates to the squares list
            square = (r, c)
            squares.append(square)

    # Return the list of coordinates for the center squares
    return squares


def quarter_triangle_a() -> Tuple[
    List[Tuple[int, int]],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
]:
    """
    Divides the board into four triangular regions and returns a tuple of lists containing
    the coordinates for each region.

    The regions are based on dividing the board into four triangular areas:
    - Bottom left
    - Bottom right
    - Top left
    - Top right

    :return: A tuple of four lists, where each list contains the coordinates
             (row, col) for a specific triangular region on the board.
    """
    # Initialize the four triangular regions
    bottom_left: List[Tuple[int, int]] = []
    bottom_right: List[Tuple[int, int]] = []
    top_left: List[Tuple[int, int]] = []
    top_right: List[Tuple[int, int]] = []

    # Get the maximum board indices (col and row)
    max_col, max_row = constant.board_max_index()

    # Populate the bottom left region
    for row in range(6, max_row + 1):
        for col in range(0, row - 2):
            bottom_left.append((row, col))

    # Populate the bottom right region
    for row in range(6, max_row + 1):
        for col in range(max_col, max_col - (row - 2), -1):
            bottom_right.append((row, col))

    # Populate the top left region
    for row in range(0, 6):
        for col in range(6 - row, -1, -1):
            top_left.append((row, col))

    return bottom_left, bottom_right, top_left, top_right


def quarter_triangle_b() -> (
        Tuple[List[Tuple[int, int]], List[Tuple[int, int]], List[Tuple[int, int]]]
):
    """
    Divides the board into three triangular regions and returns a tuple of lists containing
    the coordinates for each region.

    The regions are based on dividing the board into three triangular areas:
    - Bottom right
    - Top left
    - Top right

    :return: A tuple of three lists, where each list contains the coordinates
             (row, col) for a specific triangular region on the board.
    """
    # Initialize the three triangular regions
    bottom_right: List[Tuple[int, int]] = []
    top_left: List[Tuple[int, int]] = []
    top_right: List[Tuple[int, int]] = []

    # Get the maximum board indices (col and row)
    max_col, max_row = constant.board_max_index()

    # Populate the bottom right region
    for row in range(6, max_row + 1):
        for col in range(max_col, max_col - (row - 2), -1):
            bottom_right.append((row, col))

    # Populate the top left region
    for row in range(0, 6):
        for col in range(6 - row, -1, -1):
            top_left.append((row, col))

    # Populate the top right region
    for row in range(0, 6):
        for col in range(max_col, max_col - (6 - row), -1):
            top_right.append((row, col))

    return bottom_right, top_left, top_right


def quarter_triangle_c() -> (
        Tuple[List[Tuple[int, int]], List[Tuple[int, int]], List[Tuple[int, int]]]
):
    """
    Divides the board into three triangular regions and returns a tuple of lists containing
    the coordinates for each region.

    The regions are based on dividing the board into three triangular areas:
    - Bottom left
    - Bottom right
    - Top right

    :return: A tuple of three lists, where each list contains the coordinates
             (row, col) for a specific triangular region on the board.
    """
    # Initialize the three triangular regions
    bottom_left: List[Tuple[int, int]] = []
    bottom_right: List[Tuple[int, int]] = []
    top_right: List[Tuple[int, int]] = []

    # Get the maximum board indices (col and row)
    max_col, max_row = constant.board_max_index()

    # Populate the bottom left region
    for row in range(6, max_row + 1):
        for col in range(0, row - 2):
            bottom_left.append((row, col))

    # Populate the bottom right region
    for row in range(6, max_row + 1):
        for col in range(max_col, max_col - (row - 2), -1):
            bottom_right.append((row, col))

    # Populate the top right region
    for row in range(0, 6):
        for col in range(max_col, max_col - (6 - row), -1):
            top_right.append((row, col))

    return bottom_left, bottom_right, top_right


def quarter_triangle_d() -> (
        Tuple[List[Tuple[int, int]], List[Tuple[int, int]], List[Tuple[int, int]]]
):
    """
    Divides the board into three triangular regions and returns a tuple of lists containing
    the coordinates for each region.

    The regions are based on dividing the board into three triangular areas:
    - Bottom left
    - Top left
    - Top right

    :return: A tuple of three lists, where each list contains the coordinates
             (row, col) for a specific triangular region on the board.
    """
    # Initialize the three triangular regions
    bottom_left: List[Tuple[int, int]] = []
    top_left: List[Tuple[int, int]] = []
    top_right: List[Tuple[int, int]] = []

    # Get the maximum board indices (col and row)
    max_col, max_row = constant.board_max_index()

    # Populate the bottom left region
    for row in range(5, max_row + 1):
        for col in range(0, row - 2):
            bottom_left.append((row, col))

    # Populate the top left region
    for row in range(0, 5):
        for col in range(5 - row, -1, -1):
            top_left.append((row, col))

    # Populate the top right region
    for row in range(0, 5):
        for col in range(max_col, max_col - (5 - row), -1):
            top_right.append((row, col))

    return bottom_left, top_left, top_right


def left_and_right_triangle_top() -> (
        Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]
):
    """
    Divides the top part of the board into two triangular regions and returns a tuple of lists containing
    the coordinates for each region.

    The regions are based on dividing the top part of the board into two triangular areas:
    - Top left
    - Top right

    :return: A tuple of two lists, where each list contains the coordinates
             (row, col) for a specific triangular region on the board.
    """
    # Initialize the two triangular regions
    left_triangle: List[Tuple[int, int]] = []
    right_triangle: List[Tuple[int, int]] = []

    # Populate the top left region
    for row in range(0, 7):  # Iterate over the rows starting from 0 to 6 (top)
        for col in range(
                0, 7 - row
        ):  # Left triangle: columns from 0 to (7 - row) for each row
            left_triangle.append((row, col))

    # Populate the top right region
    for row in range(0, 7):  # Iterate over the rows starting from 0 to 6 (top)
        skip_columns = set(
                range(7, 7 + row)
        )  # Skip columns from 7 to 7+row-1 for each row
        for col in range(13, 6, -1):  # Iterate from column 13 to 7
            if col not in skip_columns:
                right_triangle.append((row, col))

    return left_triangle, right_triangle


def left_and_right_triangle_bottom() -> (
        Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]
):
    """
    Divides the bottom part of the board into two triangular regions and returns a tuple of lists containing
    the coordinates for each region.

    The regions are based on dividing the bottom part of the board into two triangular areas:
    - Bottom left
    - Bottom right

    :return: A tuple of two lists, where each list contains the coordinates
             (row, col) for a specific triangular region on the board.
    """
    # Initialize the two triangular regions
    left_triangle: List[Tuple[int, int]] = []
    right_triangle: List[Tuple[int, int]] = []

    # Get the maximum board indices (col and row)
    max_col, max_row = constant.board_max_index()

    # Populate the bottom left region
    for row in range(4, max_row + 1):
        for col in range(0, row - 2):
            left_triangle.append((row, col))

    # Populate the bottom right region
    for row in range(4, max_row + 1):
        for col in range(max_col, max_col - (row - 2), -1):
            right_triangle.append((row, col))

    return left_triangle, right_triangle


def top_and_bottom() -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Returns the coordinates of squares in the top and bottom parts of the board.

    The top part includes squares in the first two rows, and the bottom part includes squares in the last two rows.

    :return: A tuple containing two lists of tuples. The first list contains the coordinates
    (row, col) of the top squares,
             and the second list contains the coordinates (row, col) of the bottom squares.
    """
    # Initialize lists for top and bottom squares
    top_squares: List[Tuple[int, int]] = []
    bottom_squares: List[Tuple[int, int]] = []

    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Populate the top squares
    for col in range(3, max_col - 2):
        for row in range(1, 3):
            square: Tuple[int, int] = (row, col)
            top_squares.append(square)

    # Populate the bottom squares
    for col in range(3, max_col - 2):
        for row in range(max_row - 2, max_row):
            square: Tuple[int, int] = (row, col)
            bottom_squares.append(square)

    return top_squares, bottom_squares


def edge(distance: int = 2) -> List[Tuple[int, int]]:
    """
    Returns the coordinates of squares along the edges of the board.

    The edges include the first `distance` rows and the last `distance` rows.

    :param distance: The number of rows from the top and bottom to include as edges.
    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square along the edges.
    """
    # Initialize the list for edge squares
    squares: List[Tuple[int, int]] = []

    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Populate the top edge squares
    for col in range(0, max_col + 1):
        for row in range(0, distance):  # The first `distance` rows
            square: Tuple[int, int] = (row, col)
            squares.append(square)

    # Populate the bottom edge squares
    for col in range(0, max_col + 1):
        for row in range(max_row - distance + 1, max_row + 1):  # The last `distance` rows
            square: Tuple[int, int] = (row, col)
            squares.append(square)

    return squares


def top_pyramid() -> List[Tuple[int, int]]:
    """
    Returns the coordinates of squares in a pyramid shape at the top of the board.

    The pyramid shape is defined by a height that is half the minimum of the board's width and height.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square in the top pyramid.
    """
    # Initialize the list for pyramid squares
    squares: List[Tuple[int, int]] = []

    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Calculate the height of the pyramid
    height_of_pyramid: int = min(max_col, max_row) // 2 - 1

    # Populate the pyramid squares
    for row in range(0, height_of_pyramid):
        for col in range(0, max_col + 1):
            # Check if the square is within the pyramid shape
            if row <= col < max_col - row + 1:
                squares.append((row, col))
            elif max_col - row <= col < row - 1:
                squares.append((row, col))

    return squares


def bottom_pyramid() -> List[Tuple[int, int]]:
    """
    Returns the coordinates of squares in a pyramid shape at the bottom of the board.

    The pyramid shape is defined by a height that is half the board's height plus one.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square in the bottom pyramid.
    """
    # Initialize the list for pyramid squares
    squares: List[Tuple[int, int]] = []

    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Calculate the height of the pyramid
    height_of_pyramid: int = max_row // 2 + 1

    # Loop through rows in reverse order
    for row in range(max_row, height_of_pyramid, -1):
        for col in range(0, max_col + 1):
            # Check conditions to determine whether to append the square
            if (
                    row == max_row
                    or (row == max_row - 1 and 0 < col <= max_col - 1)
                    or (row == max_row - 2 and 1 < col <= max_col - 2)
            ):
                squares.append((row, col))

    return squares


def center_circle() -> List[Tuple[int, int]]:
    """
    Returns the coordinates of squares in a circular shape at the center of the board.

    The circle is defined by a radius of 5 squares.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square in the center circle.
    """
    # Initialize the list for circle squares
    squares: List[Tuple[int, int]] = []

    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()
    max_col += 1

    # Define the radius of the circle
    radius: int = 5
    increment: int = 0
    reached_peak: bool = False

    # Loop through rows to form the circle
    for row in range(max_row // 2 - radius, max_row // 2 + radius):
        for col in range(max_col // 2 - increment, max_col // 2 + increment):
            square: Tuple[int, int] = (row, col)
            squares.append(square)
        if increment == radius:
            reached_peak = True
        if not reached_peak:
            increment += 1
        else:
            increment -= 1

    return squares


def quarter_triangle() -> Tuple[
    List[Tuple[int, int]],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
]:
    """
    Divides the board into four triangular regions and returns a tuple of lists containing
    the coordinates for each region.

    The regions are based on dividing the board into four triangular areas:
    - Bottom left
    - Bottom right
    - Top left
    - Top right

    :return: A tuple of four lists, where each list contains the coordinates
             (row, col) for a specific triangular region on the board.
    """
    # Initialize the four triangular regions
    bottom_left: List[Tuple[int, int]] = []
    bottom_right: List[Tuple[int, int]] = []
    top_left: List[Tuple[int, int]] = []
    top_right: List[Tuple[int, int]] = []

    # Get the maximum board indices (col and row)
    max_col, max_row = constant.board_max_index()

    # Populate the bottom left region
    for row in range(5, max_row + 1):
        for col in range(0, row - 2):
            bottom_left.append((row, col))

    # Populate the bottom right region
    for row in range(max_row - 3, max_row + 1):
        for col in range(max_col, max_col - (row - 3), -1):
            bottom_right.append((row, col))

    # Populate the top left region
    for row in range(0, 5):
        for col in range(5 - row, -1, -1):
            top_left.append((row, col))

    # Populate the top right region
    for row in range(0, 5):
        for col in range(max_col, max_col - (5 - row), -1):
            top_right.append((row, col))

    return bottom_left, bottom_right, top_left, top_right


def quarter_triangle_e() -> Tuple[
    List[Tuple[int, int]],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
]:
    """
    Divides the board into four triangular regions and returns a tuple of lists containing
    the coordinates for each region.

    The regions are based on dividing the board into four triangular areas:
    - Bottom left
    - Bottom right
    - Top left
    - Top right

    :return: A tuple of four lists, where each list contains the coordinates
             (row, col) for a specific triangular region on the board.
    """
    # Initialize the four triangular regions
    bottom_left: List[Tuple[int, int]] = []
    bottom_right: List[Tuple[int, int]] = []
    top_left: List[Tuple[int, int]] = []
    top_right: List[Tuple[int, int]] = []

    # Get the maximum board indices (col and row)
    max_col, max_row = constant.board_max_index()

    # Populate the bottom left region
    for row in range(max_row - 3, max_row + 1):
        for col in range(0, row - 5):
            bottom_left.append((row, col))

    # Populate the bottom right region
    for row in range(max_row - 3, max_row + 1):
        for col in range(max_col, max_col - (row - 5), -1):
            bottom_right.append((row, col))

    # Populate the top left region
    for row in range(0, 4):
        for col in range(3 - row, -1, -1):
            top_left.append((row, col))

    # Populate the top right region
    for row in range(0, 4):
        for col in range(max_col, max_col - (4 - row), -1):
            top_right.append((row, col))

    return bottom_left, bottom_right, top_left, top_right


def top_third() -> List[Tuple[int, int]]:
    """
    Returns a list of squares that are in the top 1/3 of the board.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square in the top third.
    """
    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Define upper bound for the top third
    top_limit: int = max_row // 3

    # Generate the list of coordinates for the top third
    return [(row, col) for row in range(top_limit) for col in range(max_col)]


def bottom_third() -> List[Tuple[int, int]]:
    """
    Returns a list of squares that are in the bottom 1/3 of the board.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square in the bottom third.
    """
    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Define lower bound for the bottom third
    bottom_start: int = max_row - (max_row // 3)

    # Generate the list of coordinates for the bottom third
    return [
        (row, col) for row in range(bottom_start, max_row) for col in range(max_col)
    ]


def left_right() -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Returns the coordinates of squares in the leftmost and rightmost columns of the board.

    :return: A tuple containing two lists of tuples. The first list contains the coordinates (row, col)
    of the left squares,
             and the second list contains the coordinates (row, col) of the right squares.
    """
    # Initialize lists for left and right squares
    left_squares: List[Tuple[int, int]] = []
    right_squares: List[Tuple[int, int]] = []

    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Populate the left squares
    for row in range(0, max_row + 1):
        for col in range(0, 3):
            left_squares.append((row, col))

    # Populate the right squares
    for row in range(0, max_row + 1):
        for col in range(max_col - 2, max_col + 1):
            right_squares.append((row, col))

    return left_squares, right_squares


def alt_starting_a() -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Generates starting squares for two players in an alternative configuration A.

    :return: A tuple containing two lists of tuples. The first list contains the coordinates (row, col)
    of the white starting squares,
             and the second list contains the coordinates (row, col) of the black starting squares.
    """
    # Initialize lists for white and black starting squares
    w_starting_squares: List[Tuple[int, int]] = []
    b_starting_squares: List[Tuple[int, int]] = []

    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Calculate the center row
    y_center: int = max_row // 2

    # Populate the white starting squares
    for col in range(1, 3):
        for row in range(y_center - 2, y_center + 4):
            square: Tuple[int, int] = (row, col)
            w_starting_squares.append(square)

    # Populate the black starting squares
    for col in range(max_col - 2, max_col):
        for row in range(y_center - 2, y_center + 4):
            square: Tuple[int, int] = (row, col)
            b_starting_squares.append(square)

    return w_starting_squares, b_starting_squares


def alt_starting() -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Generates starting squares for two players in an alternative configuration B.

    :return: A tuple containing two lists of tuples. The first list contains the coordinates (row, col) of the
    white starting squares,
             and the second list contains the coordinates (row, col) of the black starting squares.
    """
    # Initialize lists for white and black starting squares
    w_starting_squares: List[Tuple[int, int]] = []
    b_starting_squares: List[Tuple[int, int]] = []

    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Calculate the center row
    y_center: int = max_row // 2

    # Populate the white starting squares
    for col in range(2, 4):
        for row in range(y_center - 2, y_center + 4):
            square: Tuple[int, int] = (row, col)
            w_starting_squares.append(square)

    # Populate the black starting squares
    for col in range(max_col - 3, max_col - 1):
        for row in range(y_center - 2, y_center + 4):
            square: Tuple[int, int] = (row, col)
            b_starting_squares.append(square)

    return w_starting_squares, b_starting_squares


def starting() -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Generates starting squares for two players in the default configuration.

    :return: A tuple containing two lists of tuples. The first list contains the coordinates (row, col) o
    f the white starting squares,
             and the second list contains the coordinates (row, col) of the black starting squares.
    """
    # Initialize lists for white and black starting squares
    w_starting_squares: List[Tuple[int, int]] = []
    b_starting_squares: List[Tuple[int, int]] = []

    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Calculate the center row
    y_center: int = max_row // 2

    # Populate the white starting squares
    for col in range(0, 5):
        for row in range(y_center - 2, y_center + 4):
            square: Tuple[int, int] = (row, col)
            w_starting_squares.append(square)

    # Populate the black starting squares
    for col in range(max_col - 4, max_col + 1):
        for row in range(y_center - 2, y_center + 4):
            square: Tuple[int, int] = (row, col)
            b_starting_squares.append(square)

    return w_starting_squares, b_starting_squares


def outside_corner() -> List[Tuple[int, int]]:
    """
    Returns the coordinates of the four outside corners of the board.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of an outside corner.
    """
    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Define the coordinates of the four outside corners
    squares: List[Tuple[int, int]] = [
        (0, 0),
        (0, max_col),
        (max_row, max_col),
        (max_row, 0),
    ]

    return squares


def thin_edge() -> List[Tuple[int, int]]:
    """
    Returns the coordinates of squares along the thin edge of the board.

    The thin edge includes the first and last rows and columns.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square along the thin edge.
    """
    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Initialize the list for edge squares
    squares: List[Tuple[int, int]] = []

    # Loop through all rows and columns to find edge squares
    for row in range(max_row + 1):
        for col in range(max_col + 1):
            # Check if the square is on the edge
            if row == 0 or row == max_row or col == 0 or col == max_col:
                squares.append((row, col))

    return squares


def top_right_corner() -> List[Tuple[int, int]]:
    """
    Returns the coordinates of the top right squares of the board.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square in the top right.
    """
    # Get the maximum column and row indices (board size)
    max_col, max_row = constant.board_max_index()

    # Initialize the list for top right squares
    squares_list: List[Tuple[int, int]] = []

    # Loop through the first 5 rows
    for row in range(0, 5):
        # Loop through the columns in the top right section
        for col in range(max_col, max_col - (5 - row), -1):
            squares_list.append((row, col))

    return squares_list


def top_left_corner() -> List[Tuple[int, int]]:
    """
    Returns the coordinates of the top left squares of the board.

    :return: A list of tuples where each tuple contains the coordinates (row, col) of a square in the top left.
    """
    # Initialize the list for top left squares
    top_left: List[Tuple[int, int]] = []

    # Loop through the first 5 rows
    for row in range(0, 5):
        # Loop through the columns in the top left section
        for col in range(5 - row, -1, -1):
            top_left.append((row, col))

    return top_left


def find_center(squares: List[Tuple[int, int]]) -> Tuple[int, int]:
    """
    Calculates the center (centroid) of a list of (row, col) coordinate pairs.

    :param squares: List of (row, column) pairs.
    :return: The center coordinates as (avg_row, avg_col).
    :raises ValueError: If the list of squares is empty.
    """
    # Raise an error if the list of squares is empty
    if not squares:
        raise ValueError(
                "You must pass a list of square tuples [(row, col)] to find_center"
        )

    # Calculate the total sum of rows and columns
    total_row: int = sum(row for row, col in squares)
    total_col: int = sum(col for row, col in squares)

    # Calculate the number of squares
    count: int = len(squares)

    # Calculate and return the average row and column
    return total_row // count, total_col // count
