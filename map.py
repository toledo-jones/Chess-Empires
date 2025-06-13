from __future__ import annotations

import math
import typing
from typing import Any, Dict, Set, List, Callable

import squares
from resource import *

if typing.TYPE_CHECKING:
    pass


def set_decree_cost(resource_count: Dict[str, int]) -> Dict[str, int]:
    """
    Calculates the decree cost based on the provided resource count.

    :param resource_count: A dictionary where the keys are resource names and the values are their counts.
    :return: A dictionary with the selected resource name as the key and the calculated decree cost as the value.
    """
    # Randomly select a resource from the provided resource_count
    resource: str = random.choice(list(resource_count.keys()))

    # Calculate a value 'x' by dividing the resource count by 10 and rounding it
    x: int = round(resource_count[resource] / 10)

    # Calculate the decree cost using the formula, applying a logarithmic function
    # This adjusts the cost based on the value of 'x', ensuring the cost changes non-linearly
    decree_cost: int = round(10 * math.log10(x + 7))

    # Set the decree increment constant
    constant.DECREE_INCREMENT = round(decree_cost / 3)

    # If the resource is "quarry", rename it to "stone"
    if resource == "quarry":
        resource = "stone"

    # Return the decree cost as a dictionary, using the resource name as the key
    return {resource: decree_cost}


def calculate_points_per_resource(
        resource_count: Dict[str, int], total_resources: int
) -> Dict[str, Dict[str, int]]:
    """
    Calculates the points per resource based on the provided resource count and total resources.

    :param resource_count: A dictionary where the keys are resource names and the values are their counts.
    :param total_resources: The total number of resources.
    :return: A dictionary with resource names as keys and their points and availability as values.
    """
    points_per_resource: Dict[str, Dict[str, int]] = {}

    for resource, count in resource_count.items():
        if resource == "quarry":
            resource = "stone"
        try:
            # Player can only ever hope to achieve 1/3 of available resources
            points: int = round(1 / (count / total_resources)) if count > 0 else 0
        except ZeroDivisionError:
            points = 0

        total_points_possible: int = points * round(count)
        points_per_resource[resource] = {
            "points"   : points,
            "available": total_points_possible,
        }

    return points_per_resource


def assign_resource_random_weights(points_to_fill: int) -> Tuple[int, int, int]:
    """
    Assigns random weighted values to wood, stone, and gold while ensuring the total
    sum remains equal to the given `points_to_fill`.

    The function generates three random weights that sum to 1, then applies these
    weights to distribute `points_to_fill` among wood, stone, and gold.

    :param points_to_fill: The total number of points to distribute.
    :return: A tuple containing the assigned points for wood, stone, and gold, respectively.
    """
    # Generate a random weight for the first resource
    first_weight: float = random.random()

    # Generate a second weight, ensuring that the sum of the first two is ≤ 1
    second_weight: float = random.uniform(0, 1 - first_weight)

    # The third weight is whatever remains to ensure all weights sum to 1
    third_weight: float = 1 - (first_weight + second_weight)

    # Store weights in a list
    weights: List[float] = [first_weight, second_weight, third_weight]

    # Shuffle the weights to randomize their assignment to resources
    random.shuffle(weights)

    # Assign shuffled weights to log, stone, and gold respectively
    log_weight: float = weights[0]
    stone_weight: float = weights[1]
    gold_weight: float = weights[2]

    # Calculate wood points based on its weight
    wood_points: int = round(log_weight * points_to_fill)

    # Subtract assigned wood points from the total available points
    points_to_fill -= wood_points

    # Calculate stone points based on its weight
    stone_points: int = round(stone_weight * points_to_fill)

    # Subtract assigned stone points from the remaining available points
    points_to_fill -= stone_points

    # The remaining points are assigned to gold
    gold_points: int = round(gold_weight * points_to_fill)

    # Return the assigned point values for wood, stone, and gold
    return wood_points, stone_points, gold_points


def calculate_resource_costs(
        wood_points: int,
        stone_points: int,
        gold_points: int,
        points_per_resource: Dict[str, Dict[str, int]],
) -> Tuple[int, int, int]:
    """
    Calculates the resource costs based on the provided points and points per resource.

    :param wood_points: The points assigned to wood.
    :param stone_points: The points assigned to stone.
    :param gold_points: The points assigned to gold.
    :param points_per_resource: A dictionary with resource names as keys and their points and availability as values.
    :return: A tuple containing the calculated costs for wood, stone, and gold.
    """
    try:
        # Calculate the cost for wood
        wood_cost: int = round(wood_points / points_per_resource["wood"]["points"])
        # Calculate the cost for stone
        stone_cost: int = round(stone_points / points_per_resource["stone"]["points"])
        # Calculate the cost for gold
        gold_cost: int = round(gold_points / points_per_resource["gold"]["points"])
    except ZeroDivisionError:
        # Handle division by zero by setting costs to 0
        wood_cost, stone_cost, gold_cost = 0, 0, 0

    # Return the calculated costs for wood, stone, and gold
    return wood_cost, stone_cost, gold_cost


def get_random(a=0, b=100):
    """
    Generates a random integer between a and b (inclusive).
    :param a: lower bound
    :param b: upper bound
    :return: The random integer.
    """
    # Wrapper for random.randint to allow for easy testing and modification
    return random.randint(a, b)


class Map:
    """
    A class representing a game map with various resources and pieces.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the Map with the given engine.

        :param engine: The game engine.
        """
        # Store the game engine
        self.engine: Any = engine

        # Define possible movement directions
        self.directions: list[Tuple[int, int]] = [
            constant.UP,
            constant.RIGHT,
            constant.LEFT,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.DOWN_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_LEFT,
        ]

        self.points_per_resource: Dict[str, Dict[str, int]] = {}

        # Initialize a dictionary to store piece costs
        self.PIECE_COSTS: Dict[str, dict[str, int]] = {}

    def place_trees_around_point(
            self,
            center: Tuple[int, int],
            radius: int,
    ) -> List[Tuple[int, int]]:
        """
        Places trees around a central point in a somewhat random but controlled pattern.

        :param center: The (row, col) coordinates of the central point.
        :param radius: The maximum distance from the center where trees can be placed.
        :return: A list of (row, col) pairs representing tree placements.
        """
        # Unpack the center coordinates
        center_row, center_col = center

        # Initialize a set to store placed tree coordinates
        placed_trees: Set[Tuple[int, int]] = set()

        # Get the maximum column and row indices (board size)
        max_col, max_row = constant.board_max_index()

        # Calculate the number of trees to place based on the radius
        tree_count: int = radius * radius

        # Place trees until the desired count is reached
        while len(placed_trees) < tree_count:
            # Generate random offsets within the given radius
            offset_row: int = random.randint(-radius, radius)
            offset_col: int = random.randint(-radius, radius)

            # Calculate the new tree position
            tree_row: int = center_row + offset_row
            tree_col: int = center_col + offset_col

            # Ensure the tree is within bounds and not a duplicate
            if 0 <= tree_row < max_row and 0 <= tree_col < max_col:
                placed_trees.add((tree_row, tree_col))

        # Spawn wood clover at each placed tree position
        for tree in placed_trees:
            self.spawn_wood_clover(tree[0], tree[1])

        # Spawn a quarry at the center position
        self.spawn_quarry(center[0], center[1])

        # Return the list of placed tree coordinates
        return list(placed_trees)

    def set_piece_values(self, resource_count: Dict[str, int]):
        """
        Sets the values for game pieces based on the provided resource count.

        :param resource_count: A dictionary where the keys are resource names and the values are their counts.
        """
        # Calculate the total number of resources
        total_resources: int = sum(resource_count.values())

        # Calculate points per resource
        self.points_per_resource: Dict[str, Dict[str, int]] = calculate_points_per_resource(
                resource_count, total_resources
        )

        # Set Decree Cost
        constant.DECREE_COST = set_decree_cost(resource_count)

        # Define initial piece costs
        initial_piece_costs: Dict[str, Any] = self.engine.PIECE_COSTS

        # Assign costs to pieces
        self.assign_piece_costs(initial_piece_costs, self.points_per_resource)

    def assign_piece_costs(
            self,
            initial_piece_costs: Dict[str, Any],
            points_per_resource: Dict[str, Dict[str, int]],
    ):
        """
        Assigns costs to game pieces based on initial piece costs and points per resource.

        :param initial_piece_costs: A dictionary with initial piece costs.
        :param points_per_resource: A dictionary with resource names as keys and
        their points and availability as values.
        """
        for piece, costs in initial_piece_costs.items():
            points_to_fill: int = constant.PIECE_POINT_VALUES[piece]

            # Assign random weights for resources
            wood_points, stone_points, gold_points = assign_resource_random_weights(
                    points_to_fill * 3
            )

            # Calculate resource costs based on available points
            wood_cost, stone_cost, gold_cost = calculate_resource_costs(
                    wood_points, stone_points, gold_points, points_per_resource
            )

            # Assign costs to the piece
            self.PIECE_COSTS[piece] = {
                "log"  : wood_cost,
                "stone": stone_cost,
                "gold" : gold_cost,
            }

        self.engine.PIECE_COSTS = self.PIECE_COSTS

    def spawn_gold_nearby(self, row: int, col: int):
        """
        Spawns gold in a nearby tile around the specified (row, col) coordinates.

        :param row: The row coordinate of the center point.
        :param col: The column coordinate of the center point.
        """
        # List of possible directions (up, down, left, right, etc.)
        direction: Tuple[int, int] = random.choice(self.directions)

        # Calculate new potential coordinates
        new_row: int = row + direction[0]
        new_col: int = col + direction[1]

        # Check if the new coordinates are within bounds and legal
        if self.engine.tile_in_bounds(new_row, new_col):
            # Spawn gold at the new coordinates
            self.spawn_gold(new_row, new_col)
        else:
            # If not legal, try again or choose a different direction
            self.spawn_gold_nearby(row, col)

    def populate_randomly(
            self,
            row: int,
            col: int,
            choices: Optional[List[Callable[[int, int], None]]] = None,
            directions: Optional[List[Tuple[int, int]]] = None,
    ):
        """
        Randomly spawns a resource at (row, col) and a neighboring tile, recursively continuing in some cases.

        :param row: The row coordinate where the resource will be spawned.
        :param col: The column coordinate where the resource will be spawned.
        :param choices: A list of resource spawning functions to choose from.
        :param directions: A list of possible directions to spawn resources in
        """
        # Randomly choose a resource spawning function
        choice: Callable[[int, int], None] = random.choice(choices)
        # Randomly choose a direction
        direction: Tuple[int, int] = random.choice(directions)
        # Spawn the resource at the given coordinates
        choice(row, col)

        # Calculate new coordinates based on the chosen direction
        new_row: int = row + direction[0]
        new_col: int = col + direction[1]
        # Spawn a resource at the new coordinates
        random.choice(choices)(new_row, new_col)

        # Recursively continue spawning resources with a certain probability
        if get_random() > 80:
            self.populate_randomly(new_row, new_col, choices, directions)

    def spawn_wood_nearby(self, row: int, col: int):
        """
        Spawns wood in a nearby tile around the specified (row, col) coordinates.

        :param row: The row coordinate of the center point.
        :param col: The column coordinate of the center point.
        """
        # List of possible directions (up, down, left, right, etc.)
        direction: Tuple[int, int] = random.choice(self.directions)

        # Calculate new potential coordinates
        new_row: int = row + direction[0]
        new_col: int = col + direction[1]

        # Spawn wood at the new coordinates
        self.spawn_wood(new_row, new_col)

    def spawn_wood_clover(self, row: int, col: int, distance: int = 1):
        """
        Spawns wood in a clover pattern around the specified (row, col) coordinates.

        :param row: The row coordinate of the center point.
        :param col: The column coordinate of the center point.
        :param distance: The distance from the center to spawn wood.
        """
        # List of possible directions (up, down, left, right)
        directions: Tuple[Tuple[int, int], ...] = (
            constant.UP,
            constant.RIGHT,
            constant.LEFT,
            constant.DOWN,
        )

        # Spawn wood at the center point
        self.spawn_wood(row, col)

        # Iterate over all distances from 1 to the specified distance
        for d in range(1, distance + 1):
            for direction in directions:
                new_row: int = row + direction[0] * d
                new_col: int = col + direction[1] * d
                if self.engine.tile_in_bounds(new_row, new_col):
                    # Spawn wood at the new coordinates
                    self.spawn_wood(new_row, new_col)

    def spawn_wood_line(self, row: int, col: int, distance: int):
        """
        Spawns wood in a line pattern around the specified (row, col) coordinates.

        :param row: The row coordinate of the center point.
        :param col: The column coordinate of the center point.
        :param distance: The distance from the center to spawn wood.
        """
        # List of possible directions (up, down, left, right)
        directions: Tuple[Tuple[int, int], ...] = (
            constant.UP,
            constant.RIGHT,
            constant.LEFT,
            constant.DOWN,
        )

        # Spawn wood at the center point
        self.spawn_wood(row, col)

        # Iterate over all distances from 0 to the specified distance
        for direction in directions:
            for d in range(distance):
                new_row: int = row + direction[0] * d
                new_col: int = col + direction[1] * d
                if self.engine.tile_in_bounds(new_row, new_col):
                    # Spawn wood at the new coordinates
                    self.spawn_wood(new_row, new_col)

    def spawn_wood_nearby_pattern(self, row: int, col: int):
        """
        Spawns wood in a nearby pattern around the specified (row, col) coordinates.

        :param row: The row coordinate of the center point.
        :param col: The column coordinate of the center point.
        """
        # List of possible patterns
        patterns: Tuple[Callable[[int, int, int], None], ...] = (
            self.spawn_wood_clover,
            self.spawn_wood_line,
        )

        # Randomly select a distance between 1 and 3
        distance: int = random.randint(1, 3)

        # Randomly select a pattern
        choice: Callable[[int, int, int], None] = random.choice(patterns)

        # Spawn wood in the selected pattern
        choice(row, col, distance)

    def generate_stone(self, min_quarries: int = 11):
        """
        Generates stone quarries on the board, ensuring a minimum number of quarries.

        :param min_quarries: The minimum number of quarries to generate.
        """
        # Initialize a set to store quarry positions
        quarry_positions: Set[Tuple[int, int]] = set()

        # Pass 1: Controlled Placement
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                # Mark the tile as not containing a quarry
                self.engine.board[row][col].can_contain_quarry = False

                # Count how many quarries are in the 3x3 neighborhood
                neighbors: List[Tuple[int, int]] = [
                    (neighbor_row, neighbor_col)
                    for neighbor_row in range(
                            max(0, row - 1), min(self.engine.rows, row + 2)
                    )
                    for neighbor_col in range(
                            max(0, col - 1), min(self.engine.cols, col + 2)
                    )
                    if (neighbor_row, neighbor_col) in quarry_positions
                ]

                # Allow placement only if there are fewer than 3 quarries in the neighborhood
                if len(neighbors) < 3:
                    random_value: int = random.randint(0, 100)
                    if random_value > 60:  # Adjust probability as needed
                        self.engine.board[row][col].can_contain_quarry = True
                        quarry_positions.add((row, col))

        # Pass 2: Ensure Minimum Quarries
        while len(quarry_positions) < min_quarries:
            row: int = random.randint(0, self.engine.rows - 1)
            col: int = random.randint(0, self.engine.cols - 1)

            # Check the 3x3 region around this tile
            neighbors: List[Tuple[int, int]] = [
                (neighbor_row, neighbor_col)
                for neighbor_row in range(
                        max(0, row - 1), min(self.engine.rows, row + 2)
                )
                for neighbor_col in range(
                        max(0, col - 1), min(self.engine.cols, col + 2)
                )
                if (neighbor_row, neighbor_col) in quarry_positions
            ]

            if (row, col) not in quarry_positions and len(neighbors) < 3:
                self.engine.board[row][col].can_contain_quarry = True
                quarry_positions.add((row, col))

    def clear_nearby_resources(self, center: Tuple[int, int], radius: int):
        """
        Clears nearby resources within a specified radius from a central point on the board.

        :param center: The (row, col) coordinates of the center point.
        :param radius: The maximum distance from the center point to clear resources.
        """
        # Unpack the center coordinates
        center_row: int = center[0]
        center_col: int = center[1]

        # Get the maximum column and row indices (board size)
        max_col, max_row = constant.board_max_index()

        # Iterate over a square region defined by the radius
        for row in range(center_row - radius, center_row + radius + 1):
            for col in range(center_col - radius, center_col + radius + 1):
                # Ensure the coordinates are within bounds
                if 0 <= row < max_row and 0 <= col < max_col:
                    # Check if the square contains a resource to clear
                    self.engine.delete_resource(row, col)

    def spawn_gold_randomly(self, squares_list: List[Tuple[int, int]]):
        """
        Spawns gold randomly in one of the provided squares.

        :param squares_list: A list of (row, col) coordinates where gold can be spawned.
        """
        # Randomly select a square from the list
        square: Tuple[int, int] = random.choice(squares_list)

        # Unpack the selected square coordinates
        row: int = square[0]
        col: int = square[1]

        # Spawn gold at the selected coordinates
        self.spawn_gold(row, col)

    def spawn_wood(self, row: int, col: int):
        """
        Spawns wood at the specified (row, col) coordinates.

        :param row: The row coordinate where wood will be spawned.
        :param col: The column coordinate where wood will be spawned.
        """
        # Create a wood resource at the specified coordinates
        self.engine.create_resource(row, col, Wood(row, col))

    def delete_resources_in_sequential_cols(
            self, boundaries: List[int] = None, iterations: int = 1
    ) -> None:
        """
        Deletes resources in sequential columns within the specified boundaries.

        :param boundaries: A list containing the start and end column indices. Defaults to the entire board width.
        :param iterations: The number of sequential columns to delete.
        """
        # Set default boundaries if none are provided
        if boundaries is None:
            boundaries = [0, constant.BOARD_WIDTH_SQ]

        # Create a sequence of column indices within the specified boundaries
        column_sequence: List[int] = [i for i in range(boundaries[0], boundaries[1])]

        # Randomly select 'iterations' number of sequential columns to delete
        start_index: int = random.randint(0, len(column_sequence) - iterations)
        columns_to_delete: List[int] = column_sequence[
                                       start_index: start_index + iterations
                                       ]

        # Delete resources in the selected columns sequentially
        for col in columns_to_delete:
            for row in range(self.engine.rows):
                self.engine.delete_resource(row, col)

    def delete_resources_in_random_row(
            self, boundaries: List[int] = None, iterations: int = 1
    ) -> None:
        """
        Deletes resources in random rows within the specified boundaries.

        :param boundaries: A list containing the start and end row indices. Defaults to the entire board height.
        :param iterations: The number of random rows to delete.
        """
        # If no boundaries are provided, default to the entire board height range.
        if boundaries is None:
            boundaries = [0, constant.BOARD_HEIGHT_SQ]
        else:
            # Adjust the second boundary value to be based on BOARD_HEIGHT_SQ.
            boundaries[-1] = constant.BOARD_HEIGHT_SQ - boundaries[-1]

        # Create a list of row indices within the specified boundaries.
        boundary_sequence: List[int] = [
            i for i in range(boundaries[0] - 1, boundaries[1])
        ]

        # Randomly select a subset of rows to delete, based on the 'iterations' count.
        rows_to_delete: List[int] = random.sample(boundary_sequence, iterations)

        # Iterate through each row selected for deletion.
        for row in rows_to_delete:
            # For each selected row, delete the resources in all columns (from 0 to cols).
            for col in range(self.engine.cols):
                # Call the engine to delete the resource at the current row and column.
                self.engine.delete_resource(row, col)

    def spawn_gold(self, row: int, col: int):
        """
        Spawns gold at the specified (row, col) coordinates.

        :param row: The row coordinate where gold will be spawned.
        :param col: The column coordinate where gold will be spawned.
        """
        # Create a gold resource at the specified coordinates
        self.engine.create_resource(row, col, Gold(row, col))

    def spawn_quarry(self, row: int, col: int):
        """
        Spawns a quarry at the specified (row, col) coordinates.

        :param row: The row coordinate where the quarry will be spawned.
        :param col: The column coordinate where the quarry will be spawned.
        """
        # Create a quarry resource at the specified coordinates
        self.engine.create_resource(row, col, Quarry(row, col))
        try:
            # Mark the tile as able to contain stone
            self.engine.board[row][col].can_contain_stone = True
        except IndexError:
            pass

    def spawn_depleted_quarry(self, row: int, col: int):
        """
        Spawns a depleted quarry at the specified (row, col) coordinates.

        :param row: The row coordinate where the depleted quarry will be spawned.
        :param col: The column coordinate where the depleted quarry will be spawned.
        """
        try:
            # Create a depleted quarry resource at the specified coordinates
            self.engine.create_resource(row, col, DepletedQuarry(row, col))
            # Mark the tile as able to contain stone
            self.engine.board[row][col].can_contain_stone = True
        except IndexError:
            pass

    def spawn_sunken_quarry(self, row: int, col: int):
        """
        Spawns a sunken quarry at the specified (row, col) coordinates.

        :param row: The row coordinate where the sunken quarry will be spawned.
        :param col: The column coordinate where the sunken quarry will be spawned.
        """
        # Create a sunken quarry resource at the specified coordinates
        self.engine.create_resource(row, col, SunkenQuarry(row, col))
        # Mark the tile as able to contain stone
        self.engine.board[row][col].can_contain_stone = True

    def generate_resources(self):
        """
        Generates resources on the map.
        """
        pass

    def spawn_stone_or_quarry(self, row: int, col: int):
        """
        Randomly spawns either stone or a quarry at the specified (row, col) coordinates.

        :param row: The row coordinate where the resource will be spawned.
        :param col: The column coordinate where the resource will be spawned.
        """
        # Randomly choose between spawning a quarry or a depleted quarry
        resource_type: Callable[[int, int], None] = random.choice(
                [self.spawn_quarry, self.spawn_depleted_quarry]
        )
        # Spawn the chosen resource type
        resource_type(row, col)

    def spawn_wood_clover_randomly(self, section: List[Tuple[int, int]]):
        """
        Randomly spawns wood or a clover pattern in the given section.

        :param section: A list of (row, col) coordinates where resources can be spawned.
        """
        # Randomly choose a coordinate from the section
        choice: Tuple[int, int] = random.choice(section)
        row: int = choice[0]
        col: int = choice[1]
        # 50% chance to spawn wood, otherwise spawn a clover pattern
        if random.random() > 0.5:
            self.spawn_wood(row, col)
        else:
            self.spawn_wood_clover(row, col)

    def spawn_sunken_quarry_randomly(self, section: List[Tuple[int, int]]):
        """
        Randomly spawns a sunken quarry in the given section.

        :param section: A list of (row, col) coordinates where resources can be spawned.
        """
        # Randomly choose a coordinate from the section
        choice: Tuple[int, int] = random.choice(section)
        row: int = choice[0]
        col: int = choice[1]
        # 30% chance to spawn a sunken quarry
        if random.random() > 0.3:
            self.spawn_depleted_quarry(row, col)


class OctoBalanced(Map):
    """
    A class representing a balanced map with resources placed in an octagonal pattern.
    """

    def __init__(self, engine: Any):
        """
        Initializes the OctoBalanced map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map in a balanced manner.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Get the top third section of the map
        top_third: List[Tuple[int, int]] = squares.top_third()

        # Find the center of the top third section
        center: Tuple[int, int] = squares.find_center(top_third)

        # Place trees around the center point in the top third section
        self.place_trees_around_point(center, 2)

        # Get the bottom third section of the map
        bottom_third: List[Tuple[int, int]] = squares.bottom_third()

        # Find the center of the bottom third section
        center = squares.find_center(bottom_third)

        # Place trees around the center point in the bottom third section
        self.place_trees_around_point(center, 2)

        # Iterate over the left and right sections of the map
        for square_set in squares.left_right():
            # Randomly select 1 unique square from the square_set
            selected_squares: List[Tuple[int, int]] = random.sample(square_set, 1)

            # Loop over the selected squares and spawn gold
            for square in selected_squares:
                row, col = square[0], square[1]

                # Spawn gold at the selected square
                self.spawn_gold(row, col)

                # Spawn gold nearby the selected square
                self.spawn_gold_nearby(row, col)


class HyperBalanced(Map):
    """
    A class representing a hyper-balanced map with resources placed in a balanced manner.
    """

    def __init__(self, engine: Any):
        """
        Initializes the HyperBalanced map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map in a balanced manner.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Get the top third section of the map
        top_third: List[Tuple[int, int]] = squares.top_third()

        # Find the center of the top third section
        center: Tuple[int, int] = squares.find_center(top_third)

        # Place trees around the center point in the top third section
        self.place_trees_around_point(center, 2)

        # Get the bottom third section of the map
        bottom_third: List[Tuple[int, int]] = squares.bottom_third()

        # Find the center of the bottom third section
        center = squares.find_center(bottom_third)

        # Place trees around the center point in the bottom third section
        self.place_trees_around_point(center, 2)

        # Iterate over the top and bottom sections of the map
        for square_set in squares.top_and_bottom():
            # Randomly select 1 unique square from the square_set
            selected_squares: List[Tuple[int, int]] = random.sample(square_set, 1)

            # Loop over the selected squares and spawn gold
            for square in selected_squares:
                row, col = square[0], square[1]

                # Spawn gold at the selected square
                self.spawn_gold(row, col)

                # Spawn gold nearby the selected square
                self.spawn_gold_nearby(row, col)


class Default(Map):
    """
    A class representing a default map with resources placed in a balanced manner.
    """

    def __init__(self, engine: Any):
        """
        Initializes the Default map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map in a balanced manner.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Edge squares with Trees
        for square in squares.edge():
            # Generate a random number
            rand: int = get_random()
            # Unpack the square coordinates
            row, col = square[0], square[1]
            # Spawn wood if the random number is greater than 35
            if rand > 35:
                self.spawn_wood(row, col)

        # Iterate over the top and bottom sections of the map
        for square_set in squares.top_and_bottom():
            # Randomly select 3 unique squares from the square_set
            selected_squares: List[Tuple[int, int]] = random.sample(square_set, 3)
            for square in selected_squares:
                row, col = square[0], square[1]
                # Spawn wood clover at the selected square
                self.spawn_wood_clover(row, col)

        # Iterate over the top and bottom sections of the map again
        for square_set in squares.top_and_bottom():
            # Randomly select 1 unique square from the square_set
            selected_squares: List[Tuple[int, int]] = random.sample(square_set, 1)
            for square in selected_squares:
                row, col = square[0], square[1]
                # Spawn gold at the selected square
                self.spawn_gold(row, col)
                # Spawn gold nearby the selected square
                self.spawn_gold_nearby(row, col)


class IslandsModified(Map):
    """
    A class representing a modified islands map with varied resource spawning.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the IslandsModified map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with varied spawning patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Varying the resource spawning on the top pyramid
        for square in squares.top_pyramid():
            # Generate a random number between 0 and 6
            rand: int = random.randint(0, 6)
            if rand > 2:
                # Spawn wood with a higher chance
                self.spawn_wood(square[0], square[1])
                if rand > 3:
                    # Vary the nearby wood spawning
                    self.spawn_wood_nearby(square[0], square[1])
                elif rand == 1:
                    # Occasionally, spawn a different resource like stone or quarry
                    self.spawn_stone_or_quarry(square[0], square[1])

        # Varying the resource spawning on the bottom pyramid
        for square in squares.bottom_pyramid():
            # Generate a random number between 0 and 6
            rand: int = random.randint(0, 6)
            if rand > 2:
                # Spawn wood with a higher chance
                self.spawn_wood(square[0], square[1])
                if rand > 3:
                    # Vary the nearby wood spawning
                    self.spawn_wood_nearby(square[0], square[1])
                elif rand == 1:
                    # Occasionally, spawn a different resource like stone or quarry
                    self.spawn_stone_or_quarry(square[0], square[1])

        # Get the board width from constants
        board_width: int = constant.BOARD_WIDTH_SQ

        # Calculate the approximate center of the board
        approximate_center: int = board_width // 2

        # Define boundaries around the center
        boundaries: List[int] = [approximate_center - 3, approximate_center + 3]

        # Delete resources in sequential columns within the defined boundaries
        self.delete_resources_in_sequential_cols(boundaries, iterations=2)

        # Vary resource spawning in the quarters with additional randomness
        for section in squares.quarter():
            # Randomly choose a coordinate from the section
            row: int
            col: int
            row, col = random.choice(section)
            # Spawn gold at the selected coordinates
            self.spawn_gold(row, col)


class Perfect(Map):
    """
    A class representing a perfect map with specific resource spawning patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the Perfect map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

        # Define the center tiles pattern
        center_tiles: List[List[str]] = [
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
            ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
            ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
        ]

        # Define the gold tiles pattern
        gold_tiles: List[List[str]] = [
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", "x", "x", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
        ]

        # Convert the patterns to coordinates
        self.gold_tiles: List[Tuple[int, int]] = squares.custom(gold_tiles)
        self.center_trees: List[Tuple[int, int]] = squares.custom(center_tiles)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        super().generate_resources()

        # Spawn wood on the edge squares
        for square in squares.edge():
            self.spawn_wood(square[0], square[1])

        # Spawn wood nearby in the center tree squares with a 10% chance
        for square in self.center_trees:
            if random.random() > 0.90:
                self.spawn_wood_nearby_pattern(square[0], square[1])

        # Clear resources around gold tiles
        for square in self.gold_tiles:
            self.clear_nearby_resources(square, 2)

        # Spawn gold in the gold tile squares
        for square in self.gold_tiles:
            self.spawn_gold(square[0], square[1])


class Full(Map):
    """
    A class representing a full map with specific resource spawning patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the Full map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

        # Define the tree tiles pattern
        tree_tiles: List[List[str]] = [
            ["x", "x", "x", "x", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x"],
            ["x", "x", "x", "x", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x"],
            ["x", "x", "x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x"],
            ["x", "x", "x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x"],
            ["x", "x", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x"],
            ["x", "x", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x"],
            ["x", "x", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x"],
            ["x", "x", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x", "x"],
            ["x", "x", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x", "x", "x"],
            ["x", "x", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x", "x", "x"],
        ]

        # Define the center tree tiles pattern
        center_tree_tiles: List[List[str]] = [
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", "x", "x", "x", "x", " ", " ", " ", " ", " "],
        ]

        # Define the gold tiles pattern
        gold_tiles: List[List[str]] = [
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", "x", "x", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", "x", "x", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
        ]

        # Convert the patterns to coordinates
        self.tree_squares: List[Tuple[int, int]] = squares.custom(tree_tiles)
        self.gold_tiles: List[Tuple[int, int]] = squares.custom(gold_tiles)
        self.center_trees: List[Tuple[int, int]] = squares.custom(center_tree_tiles)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        super().generate_resources()

        # Spawn wood in the tree squares
        for square in self.tree_squares:
            self.spawn_wood(square[0], square[1])

        # Spawn wood in a clover pattern in the center tree squares with a 6% chance
        for square in self.center_trees:
            if random.random() > 0.94:
                self.spawn_wood_clover(square[0], square[1], random.randint(0, 2))

        # Spawn gold in the gold tile squares
        for square in self.gold_tiles:
            self.spawn_gold(square[0], square[1])


class Islands(Map):
    """
    A class representing an islands map with specific resource spawning patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the Islands map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Spawn resources in the top pyramid squares
        for square in squares.top_pyramid():
            # Generate a random number between 0 and 6
            rand: int = random.randint(0, 6)
            if rand > 1:
                # Spawn wood if the random number is greater than 1
                self.spawn_wood(square[0], square[1])
                if rand > 2:
                    # Spawn wood nearby if the random number is greater than 2
                    self.spawn_wood_nearby(square[0], square[1])

        # Spawn resources in the bottom pyramid squares
        for square in squares.bottom_pyramid():
            # Generate a random number between 0 and 6
            rand: int = random.randint(0, 6)
            if rand > 1:
                # Spawn wood if the random number is greater than 1
                self.spawn_wood(square[0], square[1])
                if rand > 2:
                    # Spawn wood nearby if the random number is greater than 2
                    self.spawn_wood_nearby(square[0], square[1])

        # Spawn gold randomly in the quarters
        for section in squares.quarter():
            self.spawn_gold_randomly(section)


class Minimal(Map):
    """
    A class representing a minimal map with specific resource spawning patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the Minimal map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

        # Initial player wood count
        self.player_wood: int = 9

        # Get the starting squares for white and black players
        self.w_starting_squares: List[Tuple[int, int]]
        self.b_starting_squares: List[Tuple[int, int]]
        self.w_starting_squares, self.b_starting_squares = squares.alt_starting()

        # Define possible movement directions
        self.directions: Tuple[Tuple[int, int], ...] = (
            constant.UP,
            constant.DOWN,
            constant.LEFT,
            constant.RIGHT,
        )

    def generate_wood(self, squares_list: List[Tuple[int, int]]):
        """
        Generates wood resources around a randomly chosen square from the provided list.

        :param squares_list: A list of (row, col) coordinates where wood can be spawned.
        """
        # Randomly choose a square from the list
        choice: Tuple[int, int] = random.choice(squares_list)
        row: int = choice[0]
        col: int = choice[1]

        # Spawn wood and nearby wood in all directions around the chosen square
        for direction in self.directions:
            new_row: int = row + direction[0]
            new_col: int = col + direction[1]
            self.spawn_wood(new_row, new_col)
            self.spawn_wood_nearby(new_row, new_col)

        # Randomly choose a direction and spawn wood and nearby wood
        choice = random.choice(self.directions)
        n_row: int = choice[0] + row
        n_col: int = choice[1] + col
        for direction in self.directions:
            new_row = n_row + direction[0]
            new_col = n_col + direction[1]
            self.spawn_wood(new_row, new_col)
            self.spawn_wood_nearby(new_row, new_col)

        # Spawn gold at the original chosen square
        self.clear_nearby_resources((row, col), radius=2)
        self.spawn_gold(row, col)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Generate wood resources for both starting squares
        self.generate_wood(self.b_starting_squares)
        self.generate_wood(self.w_starting_squares)

        # Define possible quarry spawning functions
        choices: List[Callable[[int, int], None]] = [
            self.spawn_quarry,
            self.spawn_sunken_quarry,
            self.spawn_depleted_quarry,
        ]

        # Spawn quarries randomly on the edge squares
        for square in squares.edge():
            rand: int = get_random()
            if rand > 98:
                row: int = square[0]
                col: int = square[1]
                if not self.engine.has_resource(row, col):
                    random.choice(choices)(row, col)


class GoldForest(Map):
    """
    A class representing a gold forest map with specific resource spawning patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the GoldForest map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Generate wood resources for both starting squares
        for section in squares.starting():
            for square in section:
                # Generate a random number
                rng: int = get_random()
                if rng > 65:
                    row: int = square[0]
                    col: int = square[1]
                    self.spawn_wood_clover(row, col)

        # Spawn gold in the random locations
        for section in squares.quarter():
            # Randomly choose a square from the section
            square: Tuple[int, int] = random.choice(section)
            row: int = square[0]
            col: int = square[1]
            self.spawn_wood_nearby(row, col)
            self.spawn_wood_clover(row, col, 3)
            self.spawn_gold(row, col)


class WoodlandQuarries(Map):
    """
    A class representing a woodland quarries map with specific resource spawning patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the WoodlandQuarries map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Spawn wood in the quarter triangle sections (randomly)
        for section in squares.quarter_triangle():
            for square in section:
                # Generate a random number
                rand: int = get_random()
                if rand > 40:  # 60% chance to spawn wood
                    row: int = square[0]
                    col: int = square[1]
                    self.spawn_wood(row, col)

        # Define possible quarry spawning functions
        choices: List[Callable[[int, int], None]] = [
            self.spawn_quarry,
            self.spawn_sunken_quarry,
            self.spawn_depleted_quarry,
        ]

        # Spawn quarries along the edges
        for square in squares.edge():
            # Generate a random number
            rand: int = get_random()
            if rand > 90:  # 10% chance to spawn a quarry
                row: int = square[0]
                col: int = square[1]
                random.choice(choices)(row, col)

        # Spawn gold in the center squares
        for square in squares.center():
            row: int = square[0]
            col: int = square[1]
            self.spawn_gold(row, col)


class ATrees(Map):
    """
    A class representing a map with trees and gold spawning in specific patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the ATrees map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

        # Number of gold pieces to spawn in each quarter
        self.gold_in_quarters: int = 1

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Spawn wood in the left and right triangle top sections
        for section in squares.left_and_right_triangle_top():
            for square in section:
                row: int = square[0]
                col: int = square[1]
                self.spawn_wood(row, col)

        # Spawn wood clover in the center squares with a 50% chance
        for square in squares.center():
            if get_random() > 50:
                row: int = square[0]
                col: int = square[1]
                self.spawn_wood_clover(row, col, 2)

        # Spawn gold in the quarters
        for section in squares.quarter():
            for _ in range(self.gold_in_quarters):
                square: Tuple[int, int] = random.choice(section)
                row: int = square[0]
                col: int = square[1]
                self.spawn_gold(row, col)


class AngleTrees(Map):
    """
    A class representing a map with angled tree sections and gold spawning in specific patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the AngleTrees map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

        # Number of gold pieces to spawn in each quarter
        self.gold_in_quarters: int = 1

        # Get the left and right triangle top sections
        left_triangle_top: List[Tuple[int, int]]
        right_triangle_top: List[Tuple[int, int]]
        left_triangle_top, right_triangle_top = squares.left_and_right_triangle_top()

        # Get the left and right triangle bottom sections
        left_triangle_bottom: List[Tuple[int, int]]
        right_triangle_bottom: List[Tuple[int, int]]
        left_triangle_bottom, right_triangle_bottom = (
            squares.left_and_right_triangle_bottom()
        )

        # Define two choices for triangle sections
        choice_a: Tuple[List[Tuple[int, int]], List[Tuple[int, int]]] = (
            left_triangle_top,
            right_triangle_bottom,
        )
        choice_b: Tuple[List[Tuple[int, int]], List[Tuple[int, int]]] = (
            right_triangle_top,
            left_triangle_bottom,
        )

        # Randomly select one of the choices for triangle sections
        self.triangle_sections: Tuple[List[Tuple[int, int]], List[Tuple[int, int]]] = (
            random.choice([choice_a, choice_b])
        )

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Spawn wood in the selected triangle sections
        for section in self.triangle_sections:
            for square in section:
                row: int = square[0]
                col: int = square[1]
                self.spawn_wood(row, col)

        # Spawn wood clover in the center squares with a 55% chance
        for square in squares.center():
            if get_random() > 55:
                row: int = square[0]
                col: int = square[1]
                self.spawn_wood_clover(row, col, 2)

        # Spawn gold in the quarters
        for section in squares.quarter():
            for _ in range(self.gold_in_quarters):
                square: Tuple[int, int] = random.choice(section)
                row: int = square[0]
                col: int = square[1]
                self.spawn_gold(row, col)


class VTrees(Map):
    """
    A class representing a map with trees and gold spawning in specific patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the VTrees map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

        # Number of gold pieces to spawn in each quarter
        self.gold_in_quarters: int = 1

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Spawn wood in the left and right triangle bottom sections
        for section in squares.left_and_right_triangle_bottom():
            for square in section:
                row: int = square[0]
                col: int = square[1]
                self.spawn_wood(row, col)

        # Spawn wood clover in the center squares with a 55% chance
        for square in squares.center():
            if get_random() > 55:
                row: int = square[0]
                col: int = square[1]
                self.spawn_wood_clover(row, col, 2)

        # Spawn gold in the quarters
        for section in squares.quarter():
            for _ in range(self.gold_in_quarters):
                square: Tuple[int, int] = random.choice(section)
                row: int = square[0]
                col: int = square[1]
                self.spawn_gold(row, col)


class GoldTopRight(Map):
    """
    A class representing a map with gold spawning in the top right corner and other specific patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the GoldTopRight map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Spawn wood in the quarter triangle sections (randomly)
        for section in squares.quarter_triangle_a():
            for square in section:
                # Generate a random number
                rand: int = get_random()
                if rand > 30:
                    row: int = square[0]
                    col: int = square[1]
                    self.spawn_wood(row, col)

        # Spawn quarries along the edges
        for square in squares.edge():
            # Generate a random number
            rand: int = get_random()
            row: int = square[0]
            col: int = square[1]
            if rand > 95:
                self.spawn_quarry(row, col)

        # Spawn gold in the top right corner squares
        top_right_squares: List[Tuple[int, int]] = random.sample(
                squares.top_right_corner(), 4
        )
        for square in top_right_squares:
            row: int = square[0]
            col: int = square[1]
            self.spawn_gold(row, col)


class GoldTopLeft(Map):
    def __init__(self, engine):
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Spawn wood in the quarter triangle sections (randomly)
        for section in squares.quarter_triangle_c():
            for square in section:
                # Generate a random number
                rand: int = get_random()
                if rand > 30:
                    row: int = square[0]
                    col: int = square[1]
                    self.spawn_wood(row, col)

        # Define possible quarry spawning functions
        choices: List[Callable[[int, int], None]] = [
            self.spawn_quarry,
            self.spawn_sunken_quarry,
        ]

        # Spawn quarries along the edges, excluding the top left corner
        for square in squares.edge():
            if square not in squares.top_left_corner():
                # Generate a random number
                rand: int = get_random()
                if rand > 88:
                    row: int = square[0]
                    col: int = square[1]
                    random.choice(choices)(row, col)

        # Spawn gold in the top left corner squares
        top_left: List[Tuple[int, int]] = random.sample(squares.top_left_corner(), 4)
        for square in top_left:
            row: int = square[0]
            col: int = square[1]
            self.spawn_gold(row, col)


class TriangleTrees(Map):
    """
    A class representing a map with trees and gold spawning in specific patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the TriangleTrees map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Spawn wood in the quarter triangle sections (randomly)
        for section in squares.quarter_triangle():
            for square in section:
                # Generate a random number
                rand: int = get_random()
                if rand > 30:
                    row: int = square[0]
                    col: int = square[1]
                    self.spawn_wood(row, col)

        # Spawn gold in the center squares
        for square in squares.center():
            row: int = square[0]
            col: int = square[1]
            self.spawn_gold(row, col)


class UltraBalanced(Map):
    """
    A class representing a balanced map with resources placed in a central and quarter pattern.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the UltraBalanced map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Spawn wood in the big center squares
        for square in squares.big_center():
            # Unpack the square coordinates
            row: int = square[0]
            col: int = square[1]
            # Generate a random number and spawn wood if the number is greater than 30
            if get_random() > 30:
                self.spawn_wood(row, col)

        # Spawn gold randomly in the quarter sections
        for section in squares.quarter():
            self.spawn_gold_randomly(section)


class TopBottomModified(Map):
    """
    A class representing a modified map with resources placed in top and bottom sections.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the TopBottomModified map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Define possible terrain features to spawn
        choices: Tuple[Callable[[int, int], None], Callable[[int, int], None]] = (
            self.spawn_depleted_quarry,
            self.spawn_wood_clover,
        )

        # Spawn resources in the side squares
        for section in squares.left_right():
            for square in section:
                # Generate a random number
                rand: int = get_random()
                row: int = square[0]
                col: int = square[1]
                if rand > 70:
                    self.spawn_wood(row, col)
                    if rand > 85:
                        self.spawn_wood(row, col + 1)
                        self.spawn_wood(row, col - 1)
                elif rand < 15:
                    # New terrain feature: sunken quarry or forest
                    random.choice(choices)(row, col)

        # Spawn resources in the half sections
        for section in squares.top_and_bottom():
            choice: Tuple[int, int] = random.choice(section)
            row: int = choice[0]
            col: int = choice[1]
            self.spawn_wood_clover(row, col)
            self.spawn_gold(row, col)
            random.shuffle(self.directions)
            for direction in self.directions:
                row += direction[0]
                col += direction[1]
                if isinstance(
                        self.engine.get_resource(row, col), Wood
                ) or not self.engine.get_resource(row, col):
                    self.spawn_gold(row, col)
                    break

        # Add a single gold near the center with variation
        center_square: Tuple[int, int] = random.choice(squares.center())
        variation_range: int = 3  # Set a variation range around the center

        rand_offset_row: int = random.randint(-variation_range, variation_range)
        rand_offset_col: int = random.randint(-variation_range, variation_range)
        row = center_square[0] + rand_offset_row
        col = center_square[1] + rand_offset_col

        # Ensure the position is valid and spawn gold
        self.spawn_wood_nearby(row, col)
        self.spawn_wood_nearby(row, col)
        self.spawn_gold(row, col)


class LeftRightModified(Map):
    """
    A class representing a modified map with resources placed in left and right sections.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the LeftRightModified map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Define possible terrain features to spawn
        choices: Tuple[Callable[[int, int], None]] = (self.spawn_depleted_quarry,)

        # Spawn resources in the side squares
        for section in squares.left_right():
            for square in section:
                # Generate a random number
                rand: int = get_random()
                row: int = square[0]
                col: int = square[1]
                if rand > 60:
                    self.spawn_wood(row, col)
                    if rand > 80:
                        self.spawn_wood(row, col + 1)
                        self.spawn_wood(row, col - 1)
                elif rand < 10:
                    # New terrain feature: lake or forest
                    random.choice(choices)(row, col)

        # Spawn resources in the half sections
        for section in squares.top_and_bottom():
            choice: Tuple[int, int] = random.choice(section)
            row: int = choice[0]
            col: int = choice[1]
            self.spawn_wood_clover(row, col)
            self.spawn_gold(row, col)
            random.shuffle(self.directions)
            for direction in self.directions:
                row += direction[0]
                col += direction[1]
                if isinstance(
                        self.engine.get_resource(row, col), Wood
                ) or not self.engine.get_resource(row, col):
                    self.spawn_gold(row, col)
                    break


class LeftRight(Map):
    """
    A class representing a map with resources placed in left and right sections.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the LeftRight map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Define possible terrain features to spawn
        choices: Tuple[Callable[[int, int], None], Callable[[int, int], None]] = (
            self.spawn_sunken_quarry,
            self.spawn_depleted_quarry,
        )

        # Spawn resources in the side squares
        for section in squares.left_right():
            for square in section:
                # Generate a random number
                rand: int = get_random()
                row: int = square[0]
                col: int = square[1]
                if rand > 25:
                    # Spawn wood at the current coordinates
                    self.spawn_wood(row, col)
                    if rand > 60:
                        # Spawn additional wood to the left and right of the current coordinates
                        self.spawn_wood(row, col + 1)
                        self.spawn_wood(row, col - 1)
                elif rand < 2:
                    # Spawn a random terrain feature (sunken quarry or depleted quarry)
                    random.choice(choices)(row, col)

        # Spawn resources in the half sections
        for section in squares.top_and_bottom():
            # Randomly choose a coordinate from the section
            choice: Tuple[int, int] = random.choice(section)
            row: int = choice[0]
            col: int = choice[1]
            # Spawn gold at the chosen coordinates
            self.spawn_gold(row, col)
            # Shuffle the directions to randomize the spawning pattern
            random.shuffle(self.directions)
            for direction in self.directions:
                # Update the coordinates based on the chosen direction
                row += direction[0]
                col += direction[1]
                # Spawn gold at the new coordinates
                self.spawn_gold(row, col)
                break


class OnlyStoneAndGold(Map):
    """
    A class representing a map with only stone and gold resources.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the OnlyStoneAndGold map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)
        # Define the possible resource spawning functions
        self.choices: List[Callable[[int, int], None]] = [
            self.spawn_quarry,
            self.spawn_depleted_quarry,
            self.spawn_gold,
        ]

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Iterate over the edge squares of the map
        for square in squares.edge():
            # Generate a random number
            rand: int = get_random()
            # Check if the random number is greater than 74
            if rand > 74:
                # Unpack the square coordinates
                row: int = square[0]
                col: int = square[1]
                # Randomly choose a resource spawning function and call it
                random.choice(self.choices)(row, col)

        # Iterate over the left and right sections of the map
        for section in squares.left_right():
            # Randomly sample two squares from the section
            sample: List[Tuple[int, int]] = random.sample(section, 2)
            for square in sample:
                # Unpack the square coordinates
                row: int = square[0]
                col: int = square[1]
                # Spawn wood in a nearby pattern
                self.spawn_wood_nearby_pattern(row, col)


class CenterCircleA(Map):
    """
    A class representing a map with resources placed in a circular pattern around the center.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the CenterCircleA map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Iterate over the center circle squares
        for square in squares.center_circle():
            # Generate a random number
            rand: int = get_random()
            # Check if the random number is greater than 15
            if rand > 15:
                # Unpack the square coordinates
                row: int = square[0]
                col: int = square[1]
                # Spawn wood at the coordinates
                self.spawn_wood(row, col)
                # Check if the random number is greater than 80
                if rand > 80:
                    # Spawn wood nearby twice
                    for _ in range(2):
                        self.spawn_wood_nearby(row, col)

        # Randomly sample three squares from the center squares list
        gold_squares: List[Tuple[int, int]] = random.sample(squares.center(), 3)
        for square in gold_squares:
            # Unpack the square coordinates
            row: int = square[0]
            col: int = square[1]
            # Spawn gold nearby at the coordinates
            self.spawn_gold_nearby(row, col)


class CenterCircleB(Map):
    """
    A class representing a map with resources placed in a circular pattern around the center.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the CenterCircleB map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Iterate over the center circle squares
        for square in squares.center_circle():
            # Generate a random number
            rand: int = get_random()
            # Check if the random number is greater than 40
            if rand > 40:
                # Unpack the square coordinates
                row: int = square[0]
                col: int = square[1]
                # Spawn wood at the coordinates
                self.spawn_wood(row, col)
                # Check if the random number is greater than 80
                if rand > 80:
                    # Spawn wood nearby twice
                    for _ in range(2):
                        self.spawn_wood_nearby(row, col)

        # Delete resources in random rows within the first three rows
        self.delete_resources_in_random_row([0, 3])

        # Randomly sample three squares from the center squares list
        gold_squares: List[Tuple[int, int]] = random.sample(squares.center(), 3)
        for square in gold_squares:
            # Unpack the square coordinates
            row: int = square[0]
            col: int = square[1]
            # Spawn gold nearby at the coordinates
            self.spawn_gold_nearby(row, col)


class FourCorners(Map):
    """
    A class representing a map with resources placed in four corners.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the FourCorners map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)
        # Initial player wood count
        self.player_wood: int = 9

    def generate_resources(self):
        """
        Generates wood for triangle sections and populates random locations with resources.
        """
        # Generate wood in the triangle sections
        for section in squares.quarter_triangle_d():
            self.generate_wood(section)

        # Iterate over the entire map to populate random locations with resources
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                # Check if the tile has no resource and randomly decide to populate it
                if not self.engine.has_resource(row, col) and get_random() > 95:
                    self.populate_randomly(
                            row,
                            col,
                            [
                                self.spawn_depleted_quarry,
                                self.spawn_quarry,
                                self.spawn_wood,
                            ],
                            self.directions,
                    )

    def spread_wood(self, row: int, col: int):
        """
        Spawns wood in all neighboring directions from a given coordinate.

        :param row: The row coordinate where wood will be spawned.
        :param col: The column coordinate where wood will be spawned.
        """
        # Iterate over all possible directions to spawn wood
        for direction in self.directions:
            self.spawn_wood(row + direction[0], col + direction[1])

    def generate_wood(self, squares_list: List[Tuple[int, int]]):
        """
        Generates wood clusters in a given section and places gold at the center.

        :param squares_list: A list of (row, col) coordinates where wood can be spawned.
        """
        super().generate_resources()

        # Randomly choose a square from the list
        row: int
        col: int
        row, col = random.choice(squares_list)
        # Spread wood around the chosen square
        self.spread_wood(row, col)

        # Randomly choose a direction and spread wood
        next_dir: Tuple[int, int] = random.choice(self.directions)
        self.spread_wood(row + next_dir[0], col + next_dir[1])

        # Spawn gold at the original chosen square
        self.spawn_gold(row, col)


class GoldCornersB(Map):
    """
    A class representing a map with resources placed in the corners and center.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the GoldCornersB map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)
        # Define possible resource spawning functions
        self.choices: List[Callable[[int, int], None]] = [
            self.spawn_wood_nearby_pattern
        ]

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Randomly choose between two resource placement strategies
        rand: int = random.randint(0, 1)

        # Iterate over the quarter triangle sections
        for section in squares.quarter_triangle_e():
            # Iterate over each square in the section
            for square in section:
                # Unpack the square coordinates
                row: int = square[0]
                col: int = square[1]
                # Spawn wood at the coordinates
                self.spawn_wood(row, col)
            # If rand is 0, spawn gold in a random square in the section
            if rand == 0:
                square = random.choice(section)
                row = square[0]
                col = square[1]
                self.spawn_gold(row, col)

        # If rand is 1, spawn gold in the outside corner squares
        if rand == 1:
            for square in squares.outside_corner():
                row = square[0]
                col = square[1]
                self.spawn_gold(row, col)

        # Randomly sample two squares from the big center squares list
        center_section: List[Tuple[int, int]] = random.sample(squares.big_center(), 2)
        for square in center_section:
            row = square[0]
            col = square[1]
            # Randomly choose a resource spawning function and apply it to the coordinates
            random.choice(self.choices)(row, col)


class GoldCornersA(Map):
    """
    A class representing a map with resources placed in the corners and center.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the GoldCornersA map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)
        # Define possible resource spawning functions
        self.choices: List[Callable[[int, int], None]] = [
            self.spawn_wood,
            self.spawn_quarry,
            self.spawn_wood_nearby_pattern,
        ]

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Randomly choose between two resource placement strategies
        rand: int = random.randint(0, 1)

        # Iterate over the quarter triangle sections
        for section in squares.quarter_triangle_e():
            # Iterate over each square in the section
            for square in section:
                # Unpack the square coordinates
                row: int = square[0]
                col: int = square[1]
                # Spawn wood at the coordinates
                self.spawn_wood(row, col)
            # If rand is 0, spawn gold in a random square in the section
            if rand == 0:
                square = random.choice(section)
                row = square[0]
                col = square[1]
                self.spawn_gold(row, col)

        # If rand is 1, spawn gold in the outside corner squares
        if rand == 1:
            for square in squares.outside_corner():
                row = square[0]
                col = square[1]
                self.spawn_gold(row, col)

        # Randomly sample four squares from the big center squares list
        center_section: List[Tuple[int, int]] = random.sample(squares.big_center(), 4)
        for square in center_section:
            row = square[0]
            col = square[1]
            # Randomly choose a resource spawning function and apply it to the coordinates
            random.choice(self.choices)(row, col)


class EnclosedForest(Map):
    """
    A class representing a map with resources placed in enclosed forest sections.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the EnclosedForest map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Get the left and right triangle top sections
        left_triangle_top: List[Tuple[int, int]]
        right_triangle_top: List[Tuple[int, int]]
        left_triangle_top, right_triangle_top = squares.left_and_right_triangle_top()

        # Get the left and right triangle bottom sections
        left_triangle_bottom: List[Tuple[int, int]]
        right_triangle_bottom: List[Tuple[int, int]]
        left_triangle_bottom, right_triangle_bottom = (
            squares.left_and_right_triangle_bottom()
        )

        # Combine all triangle sections into a single list
        all_triangle_sections: List[List[Tuple[int, int]]] = [
            left_triangle_top,
            right_triangle_top,
            left_triangle_bottom,
            right_triangle_bottom,
        ]

        # Iterate over each section in all triangle sections
        for section in all_triangle_sections:
            # Iterate over each square in the section
            for square in section:
                # Generate a random number between 0 and 1
                rng: float = random.uniform(0, 1)
                # If the random number is greater than 0.4, spawn wood at the square's coordinates
                if rng > 0.4:
                    row: int = square[0]
                    col: int = square[1]
                    self.spawn_wood(row, col)

        # Iterate over each section in all triangle sections
        for section in all_triangle_sections:
            # Randomly choose a square from the section
            square: Tuple[int, int] = random.choice(section)
            # Unpack the square coordinates
            row: int = square[0]
            col: int = square[1]
            # Spawn gold at the coordinates
            self.spawn_gold(row, col)


class FirstClass(Map):
    """
    A class representing a map with specific resource spawning patterns.

    :param engine: The game engine.
    """

    def __init__(self, engine: Any):
        """
        Initializes the FirstClass map with the given engine.

        :param engine: The game engine.
        """
        super().__init__(engine)

        # Define the tree squares pattern
        tree_squares: List[List[str]] = [
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", "x", "x", "x", "x", " ", " ", " ", " ", "x", "x", "x", "x", " "],
            [" ", "x", "x", "x", "x", " ", " ", "x", " ", "x", "x", "x", "x", " "],
            [" ", "x", "x", "x", "x", " ", "x", " ", " ", "x", "x", "x", "x", " "],
            [" ", "x", "x", "x", "x", " ", " ", " ", " ", "x", "x", "x", "x", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
        ]

        # Define the gold squares pattern
        gold_squares: List[List[str]] = [
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", "x", "x", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", "x", "x", " ", " ", " ", " ", " ", " ", " ", " ", "x", "x", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
        ]

        # Convert the patterns to coordinates
        self.tree_squares: List[Tuple[int, int]] = squares.custom(tree_squares)
        self.gold_squares: List[Tuple[int, int]] = squares.custom(gold_squares)
        self.edge_squares: List[Tuple[int, int]] = squares.thin_edge()

    def generate_resources(self):
        """
        Generates resources on the map with specific patterns.
        """
        # Call the parent class's generate_resources method
        super().generate_resources()

        # Iterate over the tree squares
        for square in self.tree_squares:
            # Generate a random number
            rand: int = get_random()
            # Unpack the square coordinates
            row: int = square[0]
            col: int = square[1]
            # Spawn wood at the coordinates
            self.spawn_wood(row, col)
            # If the random number is greater than 40, spawn wood nearby
            if rand > 40:
                self.spawn_wood_nearby(row, col)

        # Iterate over the edge squares
        for square in self.edge_squares:
            # Generate a random number
            rand = get_random()
            # Unpack the square coordinates
            row = square[0]
            col = square[1]
            # If the random number is greater than 15, spawn wood at the coordinates
            if rand > 15:
                self.spawn_wood(row, col)

        # Iterate over the gold squares
        for square in self.gold_squares:
            # Unpack the square coordinates
            row = square[0]
            col = square[1]
            # Spawn gold at the coordinates
            self.spawn_gold(row, col)
