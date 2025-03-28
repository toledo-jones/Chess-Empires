import math

import squares
from resource import *


class Map:
    def __init__(self, engine):
        self.engine = engine
        self.w_starting_squares, self.b_starting_squares = squares.starting()
        self.default_start_squares = squares.starting()
        self.starting_squares = self.w_starting_squares + self.b_starting_squares
        self.top_left, self.top_right, self.bottom_left, self.bottom_right = (
            squares.quarter()
        )
        self.quarters = [
            self.top_left,
            self.top_right,
            self.bottom_left,
            self.bottom_right,
        ]
        self.center_squares_list = squares.center()
        self.edge_squares = squares.edge()
        self.left_triangle_bottom, self.right_triangle_bottom = (
            squares.left_and_right_triangle_bottom()
        )
        self.left_triangle_top, self.right_triangle_top = (
            squares.left_and_right_triangle_top()
        )
        self.triangle_sections = [self.left_triangle_bottom, self.right_triangle_bottom]
        self.all_triangle_sections = [
            self.left_triangle_top,
            self.left_triangle_bottom,
            self.right_triangle_top,
            self.right_triangle_bottom,
        ]
        self.directions = (
            constant.UP,
            constant.RIGHT,
            constant.LEFT,
            constant.DOWN,
            constant.UP_RIGHT,
            constant.DOWN_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_LEFT,
        )
        self.PIECE_COSTS = {}

    def set_decree_cost(self, resource_count):
        # Randomly select a resource from the provided resource_count
        resource = random.choice(list(resource_count.keys()))

        # Calculate a value 'x' by dividing the resource count by 10 and rounding it
        x = round(resource_count[resource] / 10)

        # Calculate the decree cost using the formula, applying a logarithmic function
        # This adjusts the cost based on the value of 'x', ensuring the cost changes non-linearly
        decree_cost = round(10 * math.log10(x + 7))
        constant.DECREE_INCREMENT = round(decree_cost / 3)

        if resource == "quarry":
            resource = "stone"
        # Return the decree cost as a dictionary, using the resource name as the key
        return {resource: decree_cost}

    def place_trees_around_point(
        self,
        center: tuple[int, int],
        radius: int,
    ):
        """
        Places trees around a central point in a somewhat random but controlled pattern.

        Args:
            center (tuple[int, int]): The (row, col) coordinates of the central point.
            radius (int): The maximum distance from the center where trees can be placed.

        Returns:
            list[tuple[int, int]]: A list of (r, c) pairs representing tree placements.
        """
        center_r, center_c = center
        placed_trees = set()
        cols, rows = constant.board_max_index()
        tree_count = radius * radius

        while len(placed_trees) < tree_count:
            # Generate random offsets within the given radius
            offset_r = random.randint(-radius, radius)
            offset_c = random.randint(-radius, radius)

            # Calculate the new tree position
            tree_r = center_r + offset_r
            tree_c = center_c + offset_c

            # Ensure the tree is within bounds and not a duplicate
            if 0 <= tree_r < rows and 0 <= tree_c < cols:
                placed_trees.add((tree_r, tree_c))

        for tree in placed_trees:
            self.spawn_wood_clover(tree[0], tree[1])

        self.spawn_quarry(center[0], center[1])

    def set_piece_values(self, resource_count):
        total_resources = sum(resource_count.values())

        # Calculate points per resource
        points_per_resource = self.calculate_points_per_resource(
            resource_count, total_resources
        )

        # Set Decree Cost
        constant.DECREE_COST = self.set_decree_cost(resource_count)

        # Define initial piece costs
        initial_piece_costs = self.get_initial_piece_costs()

        # Assign costs to pieces
        self.assign_piece_costs(initial_piece_costs, points_per_resource)

    def calculate_points_per_resource(self, resource_count, total_resources):
        points_per_resource = {}

        for resource, count in resource_count.items():
            if resource == "quarry":
                resource = "stone"
            try:
                # Player can only ever hope to achieve 1/3 of available resources
                # count * 1/12
                points = round(1 / (count / total_resources)) if count > 0 else 0
            except ZeroDivisionError:
                points = 0

            total_points_possible = points * round(count)
            points_per_resource[resource] = {
                "points": points,
                "available": total_points_possible,
            }

        return points_per_resource

    def get_initial_piece_costs(self):
        return constant.PIECE_COSTS

    def assign_piece_costs(self, initial_piece_costs, points_per_resource):
        for piece, costs in initial_piece_costs.items():
            points_to_fill = constant.PIECE_POINT_VALUES[piece]

            # Assign random weights for resources
            wood_points, stone_points, gold_points = (
                self.assign_resource_random_weights(points_to_fill)
            )

            # Calculate resource costs based on available points
            wood_cost, stone_cost, gold_cost = self.calculate_resource_costs(
                wood_points, stone_points, gold_points, points_per_resource
            )

            # Assign costs to the piece
            self.PIECE_COSTS[piece] = {
                "log": wood_cost,
                "stone": stone_cost,
                "gold": gold_cost,
            }

        constant.PIECE_COSTS = self.PIECE_COSTS

    def assign_resource_random_weights(
        self, points_to_fill: int
    ) -> tuple[int, int, int]:
        """
        Assigns random weighted values to wood, stone, and gold while ensuring the total
        sum remains equal to the given `points_to_fill`.

        The function generates three random weights that sum to 1, then applies these
        weights to distribute `points_to_fill` among wood, stone, and gold.

        Args:
            points_to_fill (int): The total number of points to distribute.

        Returns:
            tuple[int, int, int]: A tuple containing the assigned points for wood,
                                  stone, and gold, respectively.
        """

        # Generate a random weight for the first resource
        first_weight = random.random()

        # Generate a second weight, ensuring that the sum of the first two is ≤ 1
        second_weight = random.uniform(0, 1 - first_weight)

        # The third weight is whatever remains to ensure all weights sum to 1
        third_weight = 1 - (first_weight + second_weight)

        # Store weights in a list
        weights = [first_weight, second_weight, third_weight]

        # Shuffle the weights to randomize their assignment to resources
        random.shuffle(weights)

        # Assign shuffled weights to log, stone, and gold respectively
        log_weight, stone_weight, gold_weight = weights

        # Calculate wood points based on its weight
        wood_points = round(log_weight * points_to_fill)

        # Subtract assigned wood points from the total available points
        points_to_fill -= wood_points

        # Calculate stone points based on its weight
        stone_points = round(stone_weight * points_to_fill)

        # Subtract assigned stone points from the remaining available points
        points_to_fill -= stone_points

        # The remaining points are assigned to gold
        gold_points = round(gold_weight * points_to_fill)

        # Return the assigned point values for wood, stone, and gold
        return wood_points, stone_points, gold_points

    def calculate_resource_costs(
        self, wood_points, stone_points, gold_points, points_per_resource
    ):
        try:
            wood_cost = round(wood_points / points_per_resource["wood"]["points"])
            stone_cost = round(stone_points / points_per_resource["stone"]["points"])
            gold_cost = round(gold_points / points_per_resource["gold"]["points"])
        except ZeroDivisionError:
            wood_cost, stone_cost, gold_cost = 0, 0, 0

        return wood_cost, stone_cost, gold_cost

    # for each piece set the value based on ratio of resources and some constants like desired typing of buildings

    def get_random(self, a=0, b=100):
        return random.randint(a, b)

    def spawn_gold_nearby(self, row, col):
        # List of possible directions (up, down, left, right, etc.)
        direction = random.choice(self.directions)

        # Calculate new potential coordinates
        r = row + direction[0]
        c = col + direction[1]

        # Check if the new coordinates are within bounds and legal
        if self.engine.tile_in_bounds(r, c):
            self.spawn_gold(r, c)
        else:
            # If not legal, try again or choose a different direction
            self.spawn_gold_nearby(row, col)

    def spawn_wood_nearby(self, row, col):
        direction = random.choice(self.directions)
        r = row + direction[0]
        c = col + direction[1]
        self.spawn_wood(r, c)

    def spawn_wood_clover(self, row, col, distance=None):
        directions = (constant.UP, constant.RIGHT, constant.LEFT, constant.DOWN)
        self.spawn_wood(row, col)
        for direction in directions:
            r = row + direction[0]
            c = col + direction[1]
            if constant.tile_in_bounds(r, c):
                self.spawn_wood(r, c)

    def spawn_wood_line(self, row, col, distance):
        directions = (constant.UP, constant.RIGHT, constant.LEFT, constant.DOWN)
        self.spawn_wood(row, col)
        for direction in directions:
            for d in range(distance):
                r = row + direction[0] * d
                c = col + direction[1] * d
                if constant.tile_in_bounds(r, c):
                    self.spawn_wood(r, c)

    def spawn_wood_nearby_pattern(self, row, col):
        patterns = (
            self.spawn_wood_clover,
            self.spawn_wood_line,
        )
        distance = random.randint(1, 3)
        choice = random.choice(patterns)
        choice(row, col, distance)

    def generate_stone(self, min_quarries=11):
        quarry_positions = set()

        # Pass 1: Controlled Placement
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                self.engine.board[row][col].can_contain_quarry = False

                # Count how many quarries are in the 3x3 neighborhood
                neighbors = [
                    (r, c)
                    for r in range(max(0, row - 1), min(self.engine.rows, row + 2))
                    for c in range(max(0, col - 1), min(self.engine.cols, col + 2))
                    if (r, c) in quarry_positions
                ]

                # Allow placement only if there are fewer than 3 quarries in the neighborhood
                if len(neighbors) < 3:
                    rand = random.randint(0, 100)
                    if rand > 60:  # Adjust probability as needed
                        self.engine.board[row][col].can_contain_quarry = True
                        quarry_positions.add((row, col))

        # Pass 2: Ensure Minimum Quarries
        while len(quarry_positions) < min_quarries:
            row, col = random.randint(0, self.engine.rows - 1), random.randint(
                0, self.engine.cols - 1
            )

            # Check the 3x3 region around this tile
            neighbors = [
                (r, c)
                for r in range(max(0, row - 1), min(self.engine.rows, row + 2))
                for c in range(max(0, col - 1), min(self.engine.cols, col + 2))
                if (r, c) in quarry_positions
            ]

            if (row, col) not in quarry_positions and len(neighbors) < 3:
                self.engine.board[row][col].can_contain_quarry = True
                quarry_positions.add((row, col))

    def clear_nearby_resources(self, center: tuple[int, int], radius: int) -> None:
        """
        Clears nearby resources within a specified radius from a central point on the board.

        Args:
            center (tuple[int, int]): The (row, col) coordinates of the center point.
            radius (int): The maximum distance from the center point to clear resources.

        Returns:
            None: The function modifies the board in-place by clearing resources.
        """
        center_r, center_c = center
        cols, rows = constant.board_max_index()

        # Iterate over a square region defined by the radius
        for r in range(center_r - radius, center_r + radius + 1):
            for c in range(center_c - radius, center_c + radius + 1):
                # Ensure the coordinates are within bounds
                if 0 <= r < rows and 0 <= c < cols:
                    # Check if the square contains a resource to clear
                    self.engine.delete_resource(r, c)

    def spawn_gold_randomly(self, squares_list):
        square = random.choice(squares_list)
        r, c = square[0], square[1]
        self.spawn_gold(r, c)

    def spawn_wood(self, r, c):
        self.engine.create_resource(r, c, Wood(r, c))

    def delete_resources_in_sequential_cols(self, boundaries=None, iterations=1):
        if boundaries is None:
            boundaries = [0, constant.BOARD_WIDTH_SQ]
        else:
            pass

        column_sequence = []
        for i in range(boundaries[0], boundaries[1]):
            column_sequence.append(i)

        # Randomly select 'iterations' number of sequential columns to delete
        start_idx = random.randint(0, len(column_sequence) - iterations)
        columns_to_delete = column_sequence[start_idx : start_idx + iterations]

        # Delete resources in the selected columns sequentially
        for col in columns_to_delete:
            for r in range(self.engine.rows):
                self.engine.delete_resource(r, col)

    def delete_resources_in_random_row(self, boundaries=None, iterations=1):
        # If no boundaries are provided, default to the entire board height range.
        if boundaries is None:
            boundaries = [0, constant.BOARD_HEIGHT_SQ]
        else:
            # Adjust the second boundary value to be based on BOARD_HEIGHT_SQ.
            boundaries[-1] = constant.BOARD_HEIGHT_SQ - boundaries[-1]

        # Create a list of row indices within the specified boundaries.
        boundary_sequence = []
        for i in range(boundaries[0] - 1, boundaries[1]):
            boundary_sequence.append(i)

        # Randomly select a subset of rows to delete, based on the 'iterations' count.
        # The 'iterations' determines how many random rows to delete.
        rows_to_delete = random.sample(boundary_sequence, iterations)

        # Iterate through each row selected for deletion.
        for row in rows_to_delete:
            # For each selected row, delete the resources in all columns (from 0 to cols).
            for c in range(self.engine.cols):
                # Call the engine to delete the resource at the current row and column.
                self.engine.delete_resource(row, c)

    def spawn_gold(self, r, c):
        self.engine.create_resource(r, c, Gold(r, c))

    def spawn_quarry(self, r, c):
        self.engine.create_resource(r, c, Quarry(r, c))
        try:
            self.engine.board[r][c].can_contain_stone = True
        except IndexError:
            pass

    def spawn_depleted_quarry(self, r, c):
        try:
            self.engine.create_resource(r, c, DepletedQuarry(r, c))
            self.engine.board[r][c].can_contain_stone = True
        except IndexError:
            pass

    def spawn_sunken_quarry(self, r, c):
        self.engine.create_resource(r, c, SunkenQuarry(r, c))
        self.engine.board[r][c].can_contain_stone = True

    def generate_resources(self):
        pass

    def spawn_stone_or_quarry(self, r, c):
        """Method to randomly spawn stone or quarry in place of wood."""
        resource_type = random.choice([self.spawn_quarry, self.spawn_depleted_quarry])
        resource_type(r, c)

    def spawn_wood_clover_randomly(self, section):
        """Randomly spawn wood and clover in the given section."""
        choice = random.choice(section)
        r, c = choice[0], choice[1]
        if random.random() > 0.5:  # 50% chance to spawn wood
            self.spawn_wood(r, c)
        else:
            self.spawn_wood_clover(r, c)

    def spawn_sunken_quarry_randomly(self, section):
        """Randomly spawn a sunken quarry in the given section."""
        choice = random.choice(section)
        r, c = choice[0], choice[1]
        if random.random() > 0.3:  # 30% chance to spawn sunken quarry
            self.spawn_depleted_quarry(r, c)


class Debug(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.set_piece_values(resource_count={"wood": 0, "stone": 0, "gold": 0})


class OctoBalanced(Map):
    def __init__(self, engine):
        super().__init__(engine)

    def generate_resources(self):
        super().generate_resources()

        top_third = squares.top_third()
        center = squares.find_center(top_third)
        self.place_trees_around_point(center, 2)

        bottom_third = squares.bottom_third()
        center = squares.find_center(bottom_third)
        self.place_trees_around_point(center, 2)
        #
        # for side in left_right_squares():
        #     for square in side:
        #         if self.get_random() > 90:
        #             self.spawn_wood_clover(square[0], square[1], 5)

        for square_set in squares.left_right():
            # Randomly select 2 unique squares from the square_set
            selected_squares = random.sample(square_set, 1)

            # Loop over the selected squares and spawn gold
            for square in selected_squares:
                r, c = square[0], square[1]
                self.spawn_gold(r, c)
                self.spawn_gold_nearby(r, c)


class HyperBalanced(Map):
    def __init__(self, engine):
        super().__init__(engine)

    def generate_resources(self):
        super().generate_resources()

        top_third = squares.top_third()
        center = squares.find_center(top_third)
        self.place_trees_around_point(center, 2)

        bottom_third = squares.bottom_third()
        center = squares.find_center(bottom_third)
        self.place_trees_around_point(center, 2)

        for square_set in squares.top_and_bottom():
            # Randomly select 2 unique squares from the square_set
            selected_squares = random.sample(square_set, 1)

            # Loop over the selected squares and spawn gold
            for square in selected_squares:
                r, c = square[0], square[1]
                self.spawn_gold(r, c)
                self.spawn_gold_nearby(r, c)


class Default(Map):
    def __init__(self, engine):
        super().__init__(engine)

    def generate_resources(self):
        super().generate_resources()

        # Edge squares with Trees
        for square in self.edge_squares:
            rand = self.get_random()
            r, c = square[0], square[1]
            if rand > 35:
                self.spawn_wood(r, c)

        for square_set in squares.top_and_bottom():
            selected_squares = random.sample(square_set, 3)
            for square in selected_squares:
                r, c = square[0], square[1]
                self.spawn_wood_clover(r, c)

        for square_set in squares.top_and_bottom():
            # Randomly select 2 unique squares from the square_set
            selected_squares = random.sample(square_set, 1)

            # Loop over the selected squares and spawn gold
            for square in selected_squares:
                r, c = square[0], square[1]
                self.spawn_gold(r, c)
                self.spawn_gold_nearby(r, c)


class IslandsModified(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.top_pyramid_squares = squares.top_pyramid()
        self.bottom_pyramid_squares = squares.bottom_pyramid()

    def generate_resources(self):
        super().generate_resources()

        # Varying the resource spawning on the top pyramid
        for square in self.top_pyramid_squares:
            rand = random.randint(0, 6)
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
        for square in self.bottom_pyramid_squares:
            rand = random.randint(0, 6)
            if rand > 2:
                # Spawn wood with a higher chance
                self.spawn_wood(square[0], square[1])
                if rand > 3:
                    # Vary the nearby wood spawning
                    self.spawn_wood_nearby(square[0], square[1])
                elif rand == 1:
                    # Occasionally, spawn a different resource like stone or quarry
                    self.spawn_stone_or_quarry(square[0], square[1])

        board_width = constant.BOARD_WIDTH_SQ
        approximate_center = board_width // 2
        boundaries = [approximate_center - 3, approximate_center + 3]
        self.delete_resources_in_sequential_cols(boundaries, iterations=2)
        # Vary resource spawning in the quarters with additional randomness
        for section in self.quarters:
            r, c = random.choice(section)
            self.spawn_gold(r, c)


class Full(Map):
    def __init__(self, engine):
        super().__init__(engine)

    def generate_resources(self):
        super().generate_resources()

        x, y = constant.board_max_index()
        clearing_threshold = 15
        wood_threshold = 80
        quarry_threshold = 10

        for r in range(0, y + 1):

            for c in range(0, x + 1):
                rng = self.get_random()
                if rng > wood_threshold:
                    self.spawn_wood_clover(r, c, 2)
                elif rng < quarry_threshold:
                    self.spawn_depleted_quarry(r, c)

        for square in self.w_starting_squares:
            if self.get_random() > clearing_threshold:
                self.engine.delete_resource(square[0], square[1])

        for square in self.b_starting_squares:
            if self.get_random() > clearing_threshold:
                self.engine.delete_resource(square[0], square[1])

        # Randomly sample squares from the white and black starting squares
        w_random_squares = random.sample(self.w_starting_squares, 2)
        b_random_squares = random.sample(self.b_starting_squares, 2)

        # Spawn gold on randomly selected white squares
        for square in w_random_squares:
            r, c = square[0], square[1]
            self.spawn_gold(r, c)

        # Spawn gold on randomly selected black squares
        for square in b_random_squares:
            r, c = square[0], square[1]
            self.spawn_gold(r, c)


class Islands(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.top_pyramid_squares = squares.top_pyramid()
        self.bottom_pyramid_squares = squares.bottom_pyramid()

    def generate_resources(self):
        super().generate_resources()
        for square in self.top_pyramid_squares:
            rand = random.randint(0, 6)
            if rand > 1:
                self.spawn_wood(square[0], square[1])
                if rand > 2:
                    self.spawn_wood_nearby(square[0], square[1])

        for square in self.bottom_pyramid_squares:
            rand = random.randint(0, 6)
            if rand > 1:
                self.spawn_wood(square[0], square[1])
                if rand > 2:
                    self.spawn_wood_nearby(square[0], square[1])

        for section in self.quarters:
            self.spawn_gold_randomly(section)


class Minimal(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.player_wood = 9
        self.w_starting_squares, self.b_starting_squares = squares.alt_starting()
        self.directions = (constant.UP, constant.DOWN, constant.LEFT, constant.RIGHT)

    def generate_wood(self, squares):
        choice = random.choice(squares)
        row, col = choice[0], choice[1]
        for direction in self.directions:
            r = row + direction[0]
            c = col + direction[1]
            self.spawn_wood(r, c)
            self.spawn_wood_nearby(r, c)
        choice = random.choice(self.directions)
        n_row, n_col = choice[0] + row, choice[1] + col
        for direction in self.directions:
            r = n_row + direction[0]
            c = n_col + direction[1]
            self.spawn_wood(r, c)
            self.spawn_wood_nearby(r, c)
        self.spawn_gold(row, col)

    def generate_resources(self):
        super().generate_resources()

        self.generate_wood(self.b_starting_squares)
        self.generate_wood(self.w_starting_squares)
        choices = [
            self.spawn_quarry,
            self.spawn_sunken_quarry,
            self.spawn_depleted_quarry,
        ]
        for square in self.edge_squares:
            rand = self.get_random()
            if rand > 98:
                r, c = square[0], square[1]
                if self.engine.has_no_resource(r, c):
                    random.choice(choices)(r, c)


class GoldForest(Map):
    def __init__(self, engine):
        super().__init__(engine)
        # Set map dimensions based on constants
        self.map_width = constant.BOARD_WIDTH_SQ
        self.map_height = constant.BOARD_HEIGHT_SQ

        # Set locations for resources
        self.center_squares_list = self.center_squares()
        self.top_right_squares_list = self.top_right_squares()
        self.tree_groups = []  # List to store tree groups
        self.gold_locations = []  # List to store gold locations

    def generate_resources(self):
        super().generate_resources()

        for section in [self.w_starting_squares, self.b_starting_squares]:
            for square in section:
                rng = self.get_random()
                if rng > 65:
                    r, c = square[0], square[1]
                    self.spawn_wood_clover(r, c)

        # Spawn gold in the random locations
        for section in self.quarters:
            square = random.choice(section)
            r, c = square[0], square[1]
            self.spawn_wood_nearby(r, c)
            self.spawn_wood_clover(r, c, 3)
            self.spawn_gold(r, c)

    # Helper functions to define map sections like `center_squares` and `top_right_squares`
    def center_squares(self):
        # Example function to return the center section of the map
        center_section = [
            (x, y)
            for x in range(self.map_height // 2 - 2, self.map_height // 2 + 3)
            for y in range(self.map_width // 2 - 2, self.map_width // 2 + 3)
        ]
        return center_section

    def top_right_squares(self):
        # Example function to return squares in the top-right corner
        top_right_section = [
            (x, y)
            for x in range(self.map_height // 2, self.map_height - 1)
            for y in range(0, self.map_width // 2)
        ]
        return top_right_section


class WoodlandQuarries(Map):

    def __init__(self, engine):
        super().__init__(engine)
        self.quarter_triangle_sections = squares.quarter_triangle()
        self.center_squares = squares.center()

    def generate_resources(self):
        super().generate_resources()

        # Spawn wood in the quarter triangle sections (randomly)
        for section in self.quarter_triangle_sections:
            for square in section:
                rand = self.get_random()
                if rand > 40:  # 60% chance to spawn wood
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)

        # Spawn quarries along the edges
        choices = [
            self.spawn_quarry,
            self.spawn_sunken_quarry,
            self.spawn_depleted_quarry,
        ]
        for square in self.edge_squares:
            rand = self.get_random()
            if rand > 90:  # 10% chance to spawn a quarry
                random.choice(choices)(square[0], square[1])

        # Spawn gold in the center square
        for square in self.center_squares:
            r, c = square[0], square[1]
            self.spawn_gold(r, c)


class ATrees(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.gold_in_quarters = 1
        self.triangle_sections = [self.left_triangle_top, self.right_triangle_top]

    def generate_resources(self):
        super().generate_resources()

        for section in self.triangle_sections:
            for square in section:
                row, col = square[0], square[1]
                self.spawn_wood(row, col)

        for square in self.center_squares_list:
            if self.get_random() > 50:
                self.spawn_wood_clover(square[0], square[1], 2)

        for section in self.quarters:
            for _ in range(self.gold_in_quarters):
                square = random.choice(section)
                self.spawn_gold(square[0], square[1])


class AngleTrees(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.gold_in_quarters = 1
        choice_a = self.left_triangle_top, self.right_triangle_bottom
        choice_b = self.right_triangle_top, self.left_triangle_bottom
        self.triangle_sections = random.choice([choice_a, choice_b])

    def generate_resources(self):
        super().generate_resources()

        for section in self.triangle_sections:
            for square in section:
                row, col = square[0], square[1]
                self.spawn_wood(row, col)

        for square in self.center_squares_list:
            if self.get_random() > 55:
                self.spawn_wood_clover(square[0], square[1], 2)

        for section in self.quarters:
            for _ in range(self.gold_in_quarters):
                square = random.choice(section)
                self.spawn_gold(square[0], square[1])


class VTrees(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.gold_in_quarters = 1

    def generate_resources(self):
        super().generate_resources()

        for section in self.triangle_sections:
            for square in section:
                row, col = square[0], square[1]
                self.spawn_wood(row, col)

        for square in self.center_squares_list:
            if self.get_random() > 55:
                self.spawn_wood_clover(square[0], square[1], 2)

        for section in self.quarters:
            for _ in range(self.gold_in_quarters):
                square = random.choice(section)
                self.spawn_gold(square[0], square[1])


class GoldTopRight(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.quarter_triangle_sections = squares.quarter_triangle_a()
        self.top_right_squares = self.top_right_squares()

    def top_right_squares(self):
        # x, y equal max val col, row
        x, y = constant.board_max_index()
        top_right = []
        for r in range(0, 5):
            for c in range(x, x - (5 - r), -1):
                top_right.append((r, c))

        return top_right

    def generate_resources(self):
        super().generate_resources()
        for section in self.quarter_triangle_sections:
            for square in section:
                rand = self.get_random()
                if rand > 30:
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)
        for square in self.edge_squares:
            rand = self.get_random()
            r, c = square[0], square[1]
            if rand > 95:
                self.spawn_quarry(r, c)

        top_right_squares = random.sample(self.top_right_squares, 4)
        for square in top_right_squares:
            r, c = square[0], square[1]
            self.spawn_gold(r, c)


class GoldTopLeft(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.quarter_triangle_sections = squares.quarter_triangle_c()
        self.top_left = self.top_left_squares()

    def top_left_squares(self):
        top_left = []
        x, y = constant.board_max_index()
        for r in range(0, 5):
            for c in range(5 - r, -1, -1):
                top_left.append((r, c))
        return top_left

    def generate_resources(self):
        super().generate_resources()
        for section in self.quarter_triangle_sections:
            for square in section:
                rand = self.get_random()
                if rand > 30:
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)
        choices = [self.spawn_quarry, self.spawn_sunken_quarry]
        for square in self.edge_squares:
            if square not in self.top_left:
                rand = self.get_random()
                if rand > 88:
                    random.choice(choices)(square[0], square[1])

        top_left = random.sample(self.top_left, 4)
        for square in top_left:
            r, c = square[0], square[1]
            self.spawn_gold(r, c)


class TriangleTrees(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.quarter_triangle_sections = squares.quarter_triangle()

    def generate_resources(self):
        super().generate_resources()
        for section in self.quarter_triangle_sections:
            for square in section:
                rand = self.get_random()
                if rand > 30:
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)

        for square in self.center_squares_list:
            self.spawn_gold(square[0], square[1])


class UnbalancedForestA(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.w_starting_squares, self.b_starting_squares = squares.alt_starting_a()
        self.center_squares = squares.big_center()

    def generate_resources(self):
        super().generate_resources()
        for square in self.center_squares:
            rand = self.get_random()
            if rand > 30:
                r, c = square[0], square[1]
                self.spawn_wood(r, c)
        self.delete_resources_in_random_row()

        square = random.choice(self.w_starting_squares)
        r, c = square[0], square[1]
        self.spawn_gold(r, c)
        for row in range(r - 1, r + 1):
            rand = self.get_random()
            if rand > 50:
                self.spawn_gold(row + 1, c + 1)
            else:
                self.spawn_gold(row, c)

        square = random.choice(self.b_starting_squares)
        r, c = square[0], square[1]
        self.spawn_quarry(r, c)
        for row in range(r - 2, r + 2):
            rand = self.get_random()
            if rand > 30:
                self.spawn_quarry(row - 1, c - 1)
            else:
                self.spawn_quarry(row, c)


class UnbalancedForestB(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.w_starting_squares, self.b_starting_squares = squares.alt_starting_a()
        self.center_squares = squares.big_center()

    def generate_resources(self):
        super().generate_resources()
        for square in self.center_squares:
            rand = self.get_random()
            if rand > 80:
                r, c = square[0], square[1]
                self.spawn_wood(r, c)
        for quarter in self.quarters:
            square = random.choice(quarter)
            (r, c) = square[0], square[1]
            self.spawn_gold(r, c)


class UltraBalanced(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.w_starting_squares, self.b_starting_squares = squares.alt_starting_a()
        self.center_squares = squares.big_center()

    def generate_resources(self):
        super().generate_resources()
        for square in self.center_squares:
            r, c = square[0], square[1]
            if self.get_random() > 30:
                self.spawn_wood(r, c)

        self.delete_resources_in_random_row(iterations=3)

        for section in self.quarters:
            self.spawn_gold_randomly(section)


class TopBottomModified(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.side_squares = squares.top_and_bottom()  # Adjusted to use top and bottom
        self.halfs = (
            squares.left_right()
        )  # These could be adjusted based on how you want them to behave
        self.directions = [
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        ]

    def generate_resources(self):
        super().generate_resources()
        choices = (self.spawn_depleted_quarry, self.spawn_wood_clover)

        for section in self.side_squares:
            for square in section:
                rand = self.get_random()
                r, c = square[0], square[1]
                if rand > 70:
                    self.spawn_wood(r, c)
                    if rand > 85:
                        self.spawn_wood(r, c + 1)
                        self.spawn_wood(r, c - 1)
                elif rand < 15:
                    # New terrain feature: sunken quarry or forest
                    random.choice(choices)(r, c)

        for section in self.halfs:
            choice = random.choice(section)
            r, c = choice[0], choice[1]
            self.spawn_wood_clover(r, c)
            self.spawn_gold(r, c)
            random.shuffle(self.directions)
            for direction in self.directions:
                r += direction[0]
                c += direction[1]
                if isinstance(
                    self.engine.get_resource(r, c), Wood
                ) or not self.engine.get_resource(r, c):
                    self.spawn_gold(r, c)
                    break

        # Add a single gold near the center with variation
        center_square = random.choice(squares.center())
        variation_range = 3  # Set a variation range around the center

        rand_offset_row = random.randint(-variation_range, variation_range)
        rand_offset_col = random.randint(-variation_range, variation_range)
        r = center_square[0] + rand_offset_row
        c = center_square[1] + rand_offset_col

        # Ensure the position is valid and spawn gold
        self.spawn_wood_nearby(r, c)
        self.spawn_wood_nearby(r, c)
        self.spawn_gold(r, c)


class LeftRightModified(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.side_squares = squares.left_right()
        self.halfs = squares.top_and_bottom()
        self.directions = [
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        ]

    def generate_resources(self):
        super().generate_resources()
        choices = (self.spawn_depleted_quarry,)

        for section in self.side_squares:
            for square in section:
                rand = self.get_random()
                r, c = square[0], square[1]
                if rand > 60:
                    self.spawn_wood(r, c)
                    if rand > 80:
                        self.spawn_wood(r, c + 1)
                        self.spawn_wood(r, c - 1)
                elif rand < 10:
                    # New terrain feature: lake or forest
                    random.choice(choices)(r, c)

        for section in self.halfs:
            choice = random.choice(section)
            r, c = choice[0], choice[1]
            self.spawn_wood_clover(r, c)
            self.spawn_gold(r, c)
            random.shuffle(self.directions)
            for direction in self.directions:
                r += direction[0]
                c += direction[1]
                self.spawn_gold(r, c)
                break


class LeftRight(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.side_squares = squares.left_right()
        self.halfs = squares.top_and_bottom()
        self.directions = [
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        ]

    def generate_resources(self):
        super().generate_resources()
        choices = (self.spawn_sunken_quarry, self.spawn_depleted_quarry)
        for section in self.side_squares:
            for square in section:
                rand = self.get_random()
                r, c = square[0], square[1]
                if rand > 25:
                    self.spawn_wood(r, c)
                    if rand > 60:
                        self.spawn_wood(r, c + 1)
                        self.spawn_wood(r, c - 1)

                elif rand < 2:
                    random.choice(choices)(r, c)
        for section in self.halfs:
            choice = random.choice(section)
            r, c = choice[0], choice[1]
            self.spawn_gold(r, c)
            random.shuffle(self.directions)
            for direction in self.directions:
                r += direction[0]
                c += direction[1]
                self.spawn_gold(r, c)
                break


class OnlyStoneAndGold(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.choices = [self.spawn_quarry, self.spawn_depleted_quarry, self.spawn_gold]

    def generate_resources(self):
        for square in self.edge_squares:
            rand = self.get_random()
            if rand > 74:
                r, c = square[0], square[1]
                random.choice(self.choices)(r, c)
        for section in squares.left_right():
            sample = random.sample(section, 2)
            for square in sample:
                r, c = square[0], square[1]
                self.spawn_wood_nearby_pattern(r, c)


class CenterCircleA(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.circle_center_squares = squares.center_circle()
        self.directions = [
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        ]
        self.choices = [
            self.spawn_sunken_quarry,
            self.spawn_quarry,
            self.spawn_depleted_quarry,
            self.spawn_wood,
        ]

    def generate_resources(self):
        for square in self.circle_center_squares:
            rand = self.get_random()
            if rand > 15:
                r, c = square[0], square[1]
                self.spawn_wood(r, c)
                if rand > 80:
                    for _ in range(2):
                        self.spawn_wood_nearby(r, c)

        gold_squares = random.sample(self.center_squares_list, 3)
        for square in gold_squares:
            r, c = square[0], square[1]
            self.spawn_gold_nearby(r, c)


class CenterCircleB(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.circle_center_squares = squares.center_circle()
        self.directions = [
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        ]
        self.choices = [
            self.spawn_sunken_quarry,
            self.spawn_quarry,
            self.spawn_depleted_quarry,
            self.spawn_wood,
        ]

    def generate_resources(self):
        for square in self.circle_center_squares:
            rand = self.get_random()
            if rand > 40:
                r, c = square[0], square[1]
                self.spawn_wood(r, c)
                if rand > 80:
                    for _ in range(2):
                        self.spawn_wood_nearby(r, c)
        self.delete_resources_in_random_row([0, 3])
        gold_squares = random.sample(self.center_squares_list, 3)
        for square in gold_squares:
            r, c = square[0], square[1]
            self.spawn_gold_nearby(r, c)


class FourCorners(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.player_wood = 9
        self.triangle_sections = squares.quarter_triangle_d()
        self.directions = [
            constant.UP,
            constant.RIGHT,
            constant.DOWN,
            constant.LEFT,
            constant.UP_RIGHT,
            constant.UP_LEFT,
            constant.DOWN_RIGHT,
            constant.DOWN_LEFT,
        ]
        self.choices = [self.spawn_depleted_quarry, self.spawn_quarry, self.spawn_wood]

    def populate_randomly(self, row, col):
        choice = random.choice(self.choices)
        direction = random.choice(self.directions)
        rand = self.get_random()
        choice(row, col)
        row += direction[0]
        col += direction[1]
        random.choice(self.choices)(row, col)
        if rand > 80:
            self.populate_randomly(row, col)

    def generate_resources(self):
        for section in self.triangle_sections:
            self.generate_wood(section)
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                if self.engine.has_no_resource(r, c):
                    rand = self.get_random()
                    if rand > 95:
                        self.populate_randomly(r, c)

    def generate_wood(self, squares_list):
        super().generate_resources()
        choice = random.choice(squares_list)
        row, col = choice[0], choice[1]
        for direction in self.directions:
            r = row + direction[0]
            c = col + direction[1]
            self.spawn_wood(r, c)
        choice = random.choice(self.directions)
        n_row, n_col = choice[0] + row, choice[1] + col
        for direction in self.directions:
            r = n_row + direction[0]
            c = n_col + direction[1]
            self.spawn_wood(r, c)
        self.spawn_gold(row, col)


class GoldCornersB(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.choices = [self.spawn_wood_nearby_pattern]

    def generate_resources(self):
        rand = random.randint(0, 1)
        for section in squares.quarter_triangle_e():
            for square in section:
                (r, c) = square[0], square[1]
                self.spawn_wood(r, c)
            if rand == 0:
                square = random.choice(section)
                (r, c) = square[0], square[1]
                self.spawn_gold(r, c)
        if rand == 1:
            for square in constant.outside_corner_squares():
                (r, c) = square[0], square[1]
                self.spawn_gold(r, c)

        center_section = random.sample(squares.big_center(), 2)
        for square in center_section:
            (r, c) = square[0], square[1]
            random.choice(self.choices)(r, c)


class GoldCornersA(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.choices = [
            self.spawn_wood,
            self.spawn_quarry,
            self.spawn_wood_nearby_pattern,
        ]

    def generate_resources(self):
        rand = random.randint(0, 1)
        for section in squares.quarter_triangle_e():
            for square in section:
                (r, c) = square[0], square[1]
                self.spawn_wood(r, c)
            if rand == 0:
                square = random.choice(section)
                (r, c) = square[0], square[1]
                self.spawn_gold(r, c)
        if rand == 1:
            for square in constant.outside_corner_squares():
                (r, c) = square[0], square[1]
                self.spawn_gold(r, c)

        center_section = random.sample(squares.big_center(), 4)
        for square in center_section:
            (r, c) = square[0], square[1]
            random.choice(self.choices)(r, c)


class EnclosedForest(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.choices = [
            self.default_start_squares,
        ]

    def generate_resources(self):
        super().generate_resources()
        for section in self.all_triangle_sections:
            for square in section:
                rng = random.uniform(0, 1)
                if rng > 0.4:
                    r, c = square[0], square[1]
                    self.spawn_wood(r, c)

        for section in self.all_triangle_sections:
            square = random.choice(section)
            r, c = square[0], square[1]
            self.spawn_gold(r, c)
