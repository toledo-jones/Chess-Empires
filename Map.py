from Resource import *


class Map:
    def __init__(self, engine):
        self.engine = engine
        self.w_starting_squares, self.b_starting_squares = Constant.starting_squares()
        self.default_start_squares = Constant.starting_squares()
        self.starting_squares = self.w_starting_squares + self.b_starting_squares
        self.top_left, self.top_right, self.bottom_left, self.bottom_right = Constant.quarter_squares()
        self.quarters = [self.top_left, self.top_right, self.bottom_left, self.bottom_right]
        self.center_squares = Constant.center_squares()
        self.edge_squares = Constant.edge_squares()

        self.left_triangle, self.right_triangle = Constant.left_and_right_triangle_sections()
        self.triangle_sections = [self.left_triangle, self.right_triangle]
        self.directions = (
            Constant.UP, Constant.RIGHT, Constant.LEFT, Constant.DOWN, Constant.UP_RIGHT, Constant.DOWN_RIGHT,
            Constant.UP_LEFT, Constant.DOWN_LEFT)

    def get_random(self):
        rand = random.randint(0, 100)
        return rand

    def spawn_wood_nearby(self, row, col):
        direction = random.choice(self.directions)
        r = row + direction[0]
        c = col + direction[1]
        if Constant.tile_in_bounds(r, c):
            self.spawn_wood(r, c)

    def spawn_wood_clover(self, row, col, distance=None):
        directions = (Constant.UP, Constant.RIGHT, Constant.LEFT, Constant.DOWN)
        self.spawn_wood(row, col)
        for direction in directions:
            r = row+direction[0]
            c = col+direction[1]
            if Constant.tile_in_bounds(r, c):
                self.spawn_wood(r, c)

    def spawn_wood_line(self, row, col, distance):
        directions = (Constant.UP, Constant.RIGHT, Constant.LEFT, Constant.DOWN)
        self.spawn_wood(row, col)
        for direction in directions:
            for d in range(distance):
                r = row + direction[0] * d
                c = col + direction[1] * d
                if Constant.tile_in_bounds(r, c):
                    self.spawn_wood(r, c)

    def spawn_wood_nearby_pattern(self, row, col):
        patterns = self.spawn_wood_clover, self.spawn_wood_line,
        distance = random.randint(1, 3)
        choice = random.choice(patterns)
        choice(row, col, distance)

    def generate_stone(self):
        for row in range(self.engine.rows):
            for col in range(self.engine.cols):
                self.engine.board[row][col].can_contain_quarry = False
                rand = random.randint(0, 100)
                if rand > 60:
                    self.engine.board[row][col].can_contain_quarry = True

    def spawn_gold_randomly(self, squares):
        square = random.choice(squares)
        r, c = square[0], square[1]
        self.spawn_gold(r, c)

    def spawn_wood(self, r, c):
        self.engine.create_resource(r, c, Wood(r, c))

    def delete_resources_in_random_row(self, boundaries=None, iterations=1):

        if boundaries is None:
            boundaries = [0, Constant.BOARD_HEIGHT_SQ]
        else:
            boundaries[-1] = Constant.BOARD_HEIGHT_SQ - boundaries[-1]
        boundary_sequence = []
        for i in range(boundaries[0]-1 , boundaries[1]):
            boundary_sequence.append(i)
        rows_to_delete = random.sample(boundary_sequence, iterations)

        for row in rows_to_delete:
            for c in range(self.engine.cols):
                self.engine.delete_resource(row, c)

    def spawn_gold(self, r, c):
        self.engine.create_resource(r, c, Gold(r, c))

    def spawn_quarry(self, r, c):
        self.engine.create_resource(r, c, Quarry(r, c))
        self.engine.board[r][c].can_contain_stone = True

    def spawn_depleted_quarry(self, r, c):
        self.engine.create_resource(r, c, DepletedQuarry(r, c))
        self.engine.board[r][c].can_contain_stone = True

    def spawn_sunken_quarry(self, r, c):
        self.engine.create_resource(r, c, SunkenQuarry(r, c))
        self.engine.board[r][c].can_contain_stone = True

    def generate_resources(self):
        self.engine.sounds.play('create_resource')


class Default(Map):
    def __init__(self, engine):
        super().__init__(engine)

    def generate_resources(self):
        super().generate_resources()

        # Edge squares with Trees
        for square in self.edge_squares:
            rand = self.get_random()
            r, c = square[0], square[1]
            if rand > 30:
                self.spawn_wood(r, c)

        # Middle Squares fill with Tree patterns
        for square in Constant.big_center_squares():
            rand = self.get_random()
            r, c = square[0], square[1]
            if rand > 45:
                self.spawn_wood(r, c)

        # 1 tree in each players starting square
        for square_set in self.default_start_squares:
            square = random.choice(square_set)
            r, c = square[0], square[1]
            self.spawn_wood(r, c)

        self.delete_resources_in_random_row([4, 3], 2)

        # 4 gold on map, 1 in each corner
        for square_set in Constant.quarter_squares():
            square = random.choice(square_set)
            r, c = square[0], square[1]
            self.spawn_gold(r,c)


class Minimal(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.player_wood = 9
        self.w_starting_squares, self.b_starting_squares = Constant.alt_starting_squares()
        self.directions = (Constant.UP, Constant.DOWN, Constant.LEFT, Constant.RIGHT)

    def generate_wood(self, squares):
        choice = random.choice(squares)
        row, col = choice[0], choice[1]
        for direction in self.directions:
            r = row + direction[0]
            c = col + direction[1]
            if Constant.tile_in_bounds(r, c):
                self.spawn_wood(r, c)
                self.spawn_wood_nearby(r, c)
        choice = random.choice(self.directions)
        n_row, n_col = choice[0] + row, choice[1] + col
        for direction in self.directions:
            r = n_row + direction[0]
            c = n_col + direction[1]
            if Constant.tile_in_bounds(r, c):
                self.spawn_wood(r, c)
                self.spawn_wood_nearby(r, c)
        self.spawn_gold(row, col)

    def generate_resources(self):
        super().generate_resources()

        self.generate_wood(self.b_starting_squares)
        self.generate_wood(self.w_starting_squares)
        choices = [self.spawn_quarry, self.spawn_sunken_quarry, self.spawn_depleted_quarry]
        for square in self.edge_squares:
            rand = random.randint(0, 100)
            if rand > 98:
                r, c = square[0], square[1]
                if self.engine.has_no_resource(r, c):
                    random.choice(choices)(r, c)


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

        for section in self.quarters:
            for _ in range(self.gold_in_quarters):
                square = random.choice(section)
                self.spawn_gold(square[0], square[1])


class GoldTopRight(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.quarter_triangle_sections = Constant.quarter_triangle_sections_a()
        self.top_right_squares = self.top_right_squares()

    def top_right_squares(self):
        # x, y equal max val col, row
        x, y = Constant.board_max_index()
        top_right = []
        for r in range(0, 5):
            for c in range(x, x - (5 - r), -1):
                top_right.append((r, c))

        return top_right

    def generate_resources(self):
        super().generate_resources()
        for section in self.quarter_triangle_sections:
            for square in section:
                rand = random.randint(0, 100)
                if rand > 30:
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)
        for square in self.edge_squares:
            rand = random.randint(0, 100)
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
        self.quarter_triangle_sections = Constant.quarter_triangle_sections_c()
        self.top_left = self.top_left_squares()

    def top_left_squares(self):
        top_left = []
        x, y = Constant.board_max_index()
        for r in range(0, 5):
            for c in range(5 - r, -1, -1):
                top_left.append((r, c))
        return top_left

    def generate_resources(self):
        super().generate_resources()
        for section in self.quarter_triangle_sections:
            for square in section:
                rand = random.randint(0, 100)
                if rand > 30:
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)
        choices = [self.spawn_quarry, self.spawn_sunken_quarry]
        for square in self.edge_squares:
            if square not in self.top_left:
                rand = random.randint(0, 100)
                if rand > 88:
                    random.choice(choices)(square[0], square[1])

        top_left = random.sample(self.top_left, 4)
        for square in top_left:
            r, c = square[0], square[1]
            self.spawn_gold(r, c)


class TriangleTrees(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.quarter_triangle_sections = Constant.quarter_triangle_sections_d()

    def generate_resources(self):
        super().generate_resources()
        for section in self.quarter_triangle_sections:
            for square in section:
                rand = random.randint(0, 100)
                if rand > 30:
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)

        for square in self.center_squares:
            self.spawn_gold(square[0], square[1])


class UnbalancedForest(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.w_starting_squares, self.b_starting_squares = Constant.alt_starting_squares_a()
        self.center_squares = Constant.big_center_squares()

    def generate_resources(self):
        super().generate_resources()
        for square in self.center_squares:
            rand = random.randint(0, 100)
            if rand > 30:
                r, c = square[0], square[1]
                self.spawn_wood(r, c)
        self.delete_resources_in_random_row()

        square = random.choice(self.w_starting_squares)
        r, c = square[0], square[1]
        self.spawn_gold(r, c)
        for row in range(r - 1, r + 1):
            rand = random.randint(0, 100)
            if rand > 50:
                self.spawn_gold(row + 1, c + 1)
            else:
                self.spawn_gold(row, c)

        square = random.choice(self.b_starting_squares)
        r, c = square[0], square[1]
        self.spawn_quarry(r, c)
        for row in range(r - 2, r + 2):
            rand = random.randint(0, 100)
            if rand > 30:
                self.spawn_quarry(row - 1, c - 1)
            else:
                self.spawn_quarry(row, c)


class UltraBalanced(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.w_starting_squares, self.b_starting_squares = Constant.alt_starting_squares_a()
        self.center_squares = Constant.big_center_squares()

    def generate_resources(self):
        super().generate_resources()
        for square in self.center_squares:
            r, c = square[0], square[1]
            if random.randint(0, 100) > 30:
                self.spawn_wood(r, c)

        self.delete_resources_in_random_row(iterations=3)

        for section in self.quarters:
            self.spawn_gold_randomly(section)


class LeftRight(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.side_squares = Constant.left_right_squares()
        self.halfs = Constant.top_and_bottom_squares()
        self.directions = [Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT, Constant.UP_RIGHT,
                           Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT]

    def generate_resources(self):
        super().generate_resources()
        choices = (self.spawn_sunken_quarry, self.spawn_depleted_quarry)
        for section in self.side_squares:
            for square in section:
                rand = random.randint(0, 100)
                r, c = square[0], square[1]
                if rand > 25:
                    self.spawn_wood(r, c)
                    if rand > 60:
                        if Constant.tile_in_bounds(r, c + 1):
                            self.spawn_wood(r, c + 1)
                        if Constant.tile_in_bounds(r, c - 1):
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
                if Constant.tile_in_bounds(r, c):
                    self.spawn_gold(r, c)
                    break


class OnlyStoneAndGold(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.choices = [self.spawn_quarry, self.spawn_depleted_quarry, self.spawn_gold]

    def generate_resources(self):
        for square in self.edge_squares:
            rand = random.randint(0, 100)
            if rand > 40:
                r, c = square[0], square[1]
                random.choice(self.choices)(r, c)
        for section in Constant.left_right_squares():
            sample = random.sample(section, 2)
            for square in sample:
                r, c = square[0], square[1]
                self.spawn_wood_nearby_pattern(r, c)


class CenterCircle(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.circle_center_squares = Constant.center_circle_squares()
        self.directions = [Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT, Constant.UP_RIGHT,
                           Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT]
        self.choices = [self.spawn_sunken_quarry, self.spawn_quarry, self.spawn_depleted_quarry, self.spawn_wood]

    def spawn_wood_nearby(self, row, col):
        direction = random.choice(self.directions)
        r = row + direction[0]
        c = col + direction[1]
        if Constant.tile_in_bounds(r, c):
            self.spawn_wood(r, c)

    def generate_resources(self):
        for square in self.circle_center_squares:
            rand = random.randint(0, 100)
            if rand > 15:
                r, c = square[0], square[1]
                self.spawn_wood(r, c)
                if rand > 80:
                    for _ in range(2):
                        self.spawn_wood_nearby(r, c)

        gold_squares = random.sample(self.center_squares, 3)
        for square in gold_squares:
            r, c = square[0], square[1]
            self.spawn_gold(r, c)


class FourCorners(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.player_wood = 9
        self.triangle_sections = self.quarter_triangle_sections_d()
        self.directions = [Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT, Constant.UP_RIGHT,
                           Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT]
        self.choices = [self.spawn_depleted_quarry, self.spawn_quarry, self.spawn_wood]

    def quarter_triangle_sections_d(self):
        bottom_left = []
        bottom_right = []
        top_left = []
        top_right = []
        # x, y equal max val col, row
        x, y = Constant.board_max_index()

        for r in range(y - 4, y + 1):
            for c in range(0, r - 5):
                bottom_left.append((r, c))

        for r in range(y - 4, y + 1):
            for c in range(x, x - (r - 5), -1):
                bottom_right.append((r, c))

        for r in range(0, 4):
            for c in range(3 - r, -1, -1):
                top_left.append((r, c))

        for r in range(0, 4):
            for c in range(x, x - (4 - r), -1):
                top_right.append((r, c))

        return bottom_left, bottom_right, top_left, top_right

    def populate_randomly(self, row, col):
        choice = random.choice(self.choices)
        direction = random.choice(self.directions)
        rand = random.randint(0, 100)
        choice(row, col)
        row += direction[0]
        col += direction[1]
        if Constant.tile_in_bounds(row, col):
            random.choice(self.choices)(row, col)
            if rand > 80:
                self.populate_randomly(row, col)

    def generate_resources(self):
        for section in self.triangle_sections:
            self.generate_wood(section)
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                if self.engine.has_no_resource(r, c):
                    rand = random.randint(0, 100)
                    if rand > 95:
                        self.populate_randomly(r, c)

    def generate_wood(self, squares):
        super().generate_resources()
        choice = random.choice(squares)
        row, col = choice[0], choice[1]
        for direction in self.directions:
            r = row + direction[0]
            c = col + direction[1]
            if Constant.tile_in_bounds(r, c):
                self.spawn_wood(r, c)
        choice = random.choice(self.directions)
        n_row, n_col = choice[0] + row, choice[1] + col
        for direction in self.directions:
            r = n_row + direction[0]
            c = n_col + direction[1]
            if Constant.tile_in_bounds(r, c):
                self.spawn_wood(r, c)
        self.spawn_gold(row, col)


