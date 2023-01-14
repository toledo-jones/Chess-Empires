from Resource import *


class Map:
    def __init__(self, engine):
        self.engine = engine
        self.w_starting_squares, self.b_starting_squares = Constant.starting_squares()
        self.starting_squares = self.w_starting_squares + self.b_starting_squares
        self.top_left, self.top_right, self.bottom_left, self.bottom_right = Constant.quarter_squares()
        self.quarters = [self.top_left, self.top_right, self.bottom_left, self.bottom_right]
        self.center_squares = Constant.center_squares()
        self.edge_squares = Constant.edge_squares()

        self.left_triangle, self.right_triangle = Constant.left_and_right_triangle_sections()
        self.triangle_sections = [self.left_triangle, self.right_triangle]

    def spawn_gold_randomly(self, squares):
        square = random.choice(squares)
        r, c = square[0], square[1]
        self.spawn_gold(r, c)

    def spawn_wood(self, r, c):
        self.engine.create_resource(r, c, Wood(r, c))

    def spawn_gold(self, r, c):
        self.engine.create_resource(r, c, Gold(r, c))

    def spawn_quarry(self, r, c):
        self.engine.create_resource(r, c, Quarry(r, c))

    def spawn_depleted_quarry(self, r, c):
        self.engine.create_resource(r, c, DepletedQuarry(r, c))

    def spawn_sunken_quarry(self, r, c):
        self.engine.create_resource(r, c, SunkenQuarry(r, c))

    def play_resource_sound_effect(self):
        i = random.randint(0, len(Constant.generate_resources) - 1)
        Constant.GENERATE_RESOURCES_SOUNDS[i].set_volume(.1)
        Constant.GENERATE_RESOURCES_SOUNDS[i].play()

    # Override this to give each map unique resource generation
    def generate_resources(self):
        self.play_resource_sound_effect()


class Default(Map):
    def __init__(self, engine):
        super().__init__(engine)

    def generate_resources(self):
        super().generate_resources()
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                in_center_square = (r, c) in Constant.center_squares()
                in_edge_square = (r, c) in Constant.edge_squares()
                in_starting_square = (r, c) in self.starting_squares
                rand = random.randint(0, 100)
                if in_starting_square:
                    pass
                elif in_edge_square:
                    if rand in range(10, 100):
                        self.engine.create_resource(r, c, Wood(r, c))
                    if rand in range(80, 100):
                        self.engine.create_resource(r, c, Wood(r, c))
                else:
                    if rand in range(1, 30):
                        if self.engine.has_no_resource(r, c):
                            self.engine.create_resource(r, c, Wood(r, c))
                            c2 = c + 1
                            if Constant.tile_in_bounds(r, c2):
                                self.engine.create_resource(r, c2, Wood(r, c2))
                            if rand > 5:
                                c2 = c - 1
                                if Constant.tile_in_bounds(r, c2):
                                    self.engine.create_resource(r, c2, Wood(r, c2))
                    if rand in range(80, 100):
                        self.engine.create_resource(r, c, Wood(r, c))
                        c2 = c + 1
                        if Constant.tile_in_bounds(r, c2):
                            self.engine.create_resource(r, c2, Wood(r, c2))
                        c2 = c - 1
                        if Constant.tile_in_bounds(r, c2):
                            self.engine.create_resource(r, c2, Wood(r, c2))
                        r2 = r + 1
                        if Constant.tile_in_bounds(r2, c):
                            self.engine.create_resource(r2, c, Wood(r2, c))
                        if rand == 99:
                            r2 = r - 1
                            if Constant.tile_in_bounds(r2, c):
                                self.engine.create_resource(r2, c, Wood(r2, c))
        rand = random.randint(3, self.engine.rows - 4)
        for c in range(self.engine.cols):
            self.engine.delete_resource(rand, c)
        rand = random.randint(0, len(self.top_left) - 1)
        r, c = self.top_left[rand][0], self.top_left[rand][1]
        self.engine.delete_resource(r, c)
        self.engine.create_resource(r, c, Gold(r, c))
        rand = random.randint(0, len(self.top_right) - 1)
        r, c = self.top_right[rand][0], self.top_right[rand][1]
        self.engine.delete_resource(r, c)
        self.engine.create_resource(r, c, Gold(r, c))
        rand = random.randint(0, len(self.bottom_left) - 1)
        r, c = self.bottom_left[rand][0], self.bottom_left[rand][1]
        self.engine.delete_resource(r, c)
        self.engine.create_resource(r, c, Gold(r, c))
        rand = random.randint(0, len(self.bottom_right) - 1)
        r, c = self.bottom_right[rand][0], self.bottom_right[rand][1]
        self.engine.delete_resource(r, c)
        self.engine.create_resource(r, c, Gold(r, c))
        # gen 1 wood resource inside each player's starting square
        for sq in range(len(self.w_starting_squares) - 1):
            rand = random.randint(0, (len(self.w_starting_squares) - 1))
            r, c = self.w_starting_squares[rand]
            if self.engine.is_empty(r, c):
                self.engine.create_resource(r, c, Wood(r, c))
                break
        for sq in range(len(self.b_starting_squares) - 1):
            rand = random.randint(0, (len(self.b_starting_squares) - 1))
            r, c = self.b_starting_squares[rand]
            if self.engine.is_empty(r, c):
                self.engine.create_resource(r, c, Wood(r, c))
                break


class Minimal(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.player_wood = 9
        self.w_starting_squares, self.b_starting_squares = Constant.alt_starting_squares()
        self.directions = (Constant.UP, Constant.DOWN, Constant.LEFT, Constant.RIGHT)

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
        n_row, n_col = choice[0] + row, choice[1]+col
        for direction in self.directions:
            r = n_row + direction[0]
            c = n_col + direction[1]
            if Constant.tile_in_bounds(r, c):
                self.spawn_wood(r, c)
        self.spawn_gold(row, col)

    def generate_resources(self):

        self.generate_wood(self.b_starting_squares)
        self.generate_wood(self.w_starting_squares)
        choices = [self.spawn_quarry, self.spawn_sunken_quarry, self.spawn_depleted_quarry]
        for square in self.edge_squares:
            rand = random.randint(0, 100)
            if rand > 70:
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
                if rand > 70:
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)
        choices = [self.spawn_quarry, self.spawn_sunken_quarry]
        for square in self.edge_squares:
            rand = random.randint(0, 100)
            if rand > 89:
                random.choice(choices)(square[0], square[1])

        for square in self.top_right_squares:
            rand = random.randint(0, 100)
            if rand > 60:
                r, c = square[0], square[1]
                self.spawn_gold(r, c)


class SparseTriangleTrees(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.quarter_triangle_sections = Constant.quarter_triangle_sections_b()

    def generate_resources(self):
        super().generate_resources()
        for section in self.quarter_triangle_sections:
            for square in section:
                rand = random.randint(0, 100)
                if rand > 40:
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)
        choices = [self.spawn_quarry, self.spawn_sunken_quarry]
        for square in self.edge_squares:
            rand = random.randint(0, 100)
            if rand > 91:
                random.choice(choices)(square[0], square[1])
        w_starting_squares, b_starting_squares = Constant.alt_starting_squares()

        choice = random.choice(w_starting_squares)
        r, c = choice[0], choice[1]
        self.spawn_gold(r, c)

        choice = random.choice(b_starting_squares)
        r, c = choice[0], choice[1]
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
                if rand > 40:
                    row, col = square[0], square[1]
                    self.spawn_wood(row, col)
        choices = [self.spawn_quarry, self.spawn_sunken_quarry]
        for square in self.edge_squares:
            rand = random.randint(0, 100)
            if rand > 88:
                random.choice(choices)(square[0], square[1])

        for square in self.top_left:
            rand = random.randint(0, 100)
            if rand > 75:
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

        square = random.choice(self.w_starting_squares)
        r, c = square[0], square[1]
        self.spawn_gold(r, c)
        for row in range(r-1, r+1):
            rand = random.randint(0, 100)
            if rand > 50:
                self.spawn_gold(row + 1, c + 1)
            else:
                self.spawn_gold(row, c)

        square = random.choice(self.b_starting_squares)
        r, c = square[0], square[1]
        self.spawn_quarry(r, c)
        for row in range(r-2, r+2):
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
            if random.randint(0, 100) > 40:
                self.spawn_wood(r, c)

        row = random.randint(0, Constant.BOARD_HEIGHT_SQ)
        for c in range(self.engine.cols):
            if self.engine.has_resource(row, c):
                self.engine.delete_resource(row, c)

        for section in self.quarters:
            self.spawn_gold_randomly(section)


class LeftRight(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.side_squares = Constant.left_right_squares()
        self.halfs = Constant.top_and_bottom_squares()
        self.directions = [Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT, Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT]

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
        self.choices = [self.spawn_sunken_quarry, self.spawn_quarry, self.spawn_depleted_quarry, self.spawn_gold]

    def generate_resources(self):
        for square in self.edge_squares:
            rand = random.randint(0, 100)
            if rand > 25:
                r, c = square[0], square[1]
                random.choice(self.choices)(r, c)
        for section in self.quarters:
            square = random.choice(section)
            r, c = square[0], square[1]
            self.spawn_wood(r, c)


class CenterCircle(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.circle_center_squares = Constant.center_circle_squares()
        self.directions = [Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT, Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT]
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
        choice = random.choice(self.center_squares)
        r, c = choice[0], choice[1]
        for _ in range(3):
            direction = random.choice(self.directions)
            r += direction[0]
            c += direction[1]
            self.spawn_gold(r, c)
        section = random.choice(Constant.left_right_squares())
        for square in section:
            rand = random.randint(0, 100)
            r, c = square[0], square[1]
            if rand > 65:
                random.choice(self.choices)(r, c)
            elif rand < 9:
                self.spawn_gold(r, c)


class FourCorners(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.player_wood = 9
        self.triangle_sections = self.quarter_triangle_sections_d()
        self.directions = [Constant.UP, Constant.RIGHT, Constant.DOWN, Constant.LEFT, Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT, Constant.DOWN_LEFT]
        self.choices = [self.spawn_sunken_quarry, self.spawn_quarry, self.spawn_depleted_quarry, self.spawn_wood]


    def quarter_triangle_sections_d(self):
        bottom_left = []
        bottom_right = []
        top_left = []
        top_right = []
        # x, y equal max val col, row
        x, y = Constant.board_max_index()

        for r in range(y - 4, y + 1):
            for c in range(0, r-5):
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
            if rand > 95:
                self.populate_randomly(row, col)

    def generate_resources(self):
        for section in self.triangle_sections:
            self.generate_wood(section)
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                if self.engine.has_no_resource(r, c):
                    rand = random.randint(0, 100)
                    if rand > 90:
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
        n_row, n_col = choice[0] + row, choice[1]+col
        for direction in self.directions:
            r = n_row + direction[0]
            c = n_col + direction[1]
            if Constant.tile_in_bounds(r, c):
                self.spawn_wood(r, c)
        self.spawn_gold(row, col)


class TotallyRandom(Map):
    def __init__(self, engine):
        super().__init__(engine)
        self.choices = [self.spawn_sunken_quarry, self.spawn_quarry, self.spawn_wood, self.spawn_depleted_quarry, self.spawn_wood, self.spawn_gold]

    def generate_resources(self):
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                rand = random.randint(0, 100)
                if rand > 80:
                    random.choice(self.choices)(r, c)
                    if Constant.tile_in_bounds(r+1, c+1):
                        self.spawn_wood(r+1, c+1)