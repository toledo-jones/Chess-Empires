import Constant
from GameEvent import *


class Behavior:
    def __init__(self):
        self.directions = (Constant.RIGHT, Constant.LEFT, Constant.UP, Constant.DOWN,
                          Constant.UP_RIGHT, Constant.UP_LEFT, Constant.DOWN_RIGHT,
                          Constant.DOWN_LEFT)
        self.possible_moves = None
        self.can_perform_move = {'pray': self.can_pray, 'steal': self.can_steal, 'mine': self.can_mine, 'spawn': self.can_spawn, 'move': self.can_move, 'capture': self.can_capture}
        self.fulfill_move_parameters = {'pray': self.pray, 'steal': self.steal, 'mine': self.mine, 'spawn': self.spawn, 'move': self.move, 'capture': self.capture}

    def all_possible_moves(self, pieces, engine):
        engine.update_all_squares()
        possible_moves = {}
        for piece in pieces:
            if piece.actions_remaining > 0:
                possible_moves[piece] = piece.possible_moves()
        self.possible_moves = possible_moves

    def can_pray(self, piece, engine):
        return True

    def can_steal(self, piece, engine):
        return True

    def can_mine(self, piece, engine):
        return True

    def can_spawn(self, piece, engine):
        for spawn in Constant.SPAWN_LISTS[str(piece)]:
            if engine.is_legal_spawn(spawn):
                return True

    def can_move(self, piece, engine):
        return True

    def can_capture(self, piece, engine):
        return True


class Random(Behavior):
    def __init__(self):
        super().__init__()
        self.piece_choices = None
        self.starting_square = None
        self.piece_placements = None
        self.move_priority = ['pray', 'steal', 'mine', 'capture', 'spawn', 'move']

    def pray(self, engine, acting_tile, action_tile):
        return Pray(engine, acting_tile, action_tile)

    def steal(self, engine, acting_tile, action_tile):
        desired_resource = self.desired_to_steal(engine, acting_tile)
        piece = action_tile.get_occupying()
        type_stolen_from = None
        if isinstance(piece, Building):
            type_stolen_from = 'building'
        elif isinstance(piece, Piece):
            type_stolen_from = 'piece'
        amount = engine.stealing_values(desired_resource, type_stolen_from)
        engine.stealing = (desired_resource, amount)
        return Steal(engine, acting_tile, action_tile)

    def spawn(self, engine, acting_tile, action_tile):
        desired_spawn = self.desired_spawn(engine, acting_tile)
        if not desired_spawn:
            return None
        engine.spawning = desired_spawn
        if engine.spawning == 'quarry_1':
            return SpawnResource(engine, acting_tile, action_tile)
        return Spawn(engine, acting_tile, action_tile)

    def capture(self, engine, acting_tile, action_tile):
        return Capture(engine, acting_tile, action_tile)

    def move(self, engine, acting_tile, action_tile):
        return Move(engine, acting_tile, action_tile)

    def mine(self, engine, acting_tile, action_tile):
        return Mine(engine, acting_tile, action_tile)

    def select_starting_square(self, engine):
        if self.starting_square is None:
            w_starting_squares, b_starting_squares = Constant.starting_squares()
            w_candidates = self.analyze_starting_squares(engine, w_starting_squares)
            b_candidates = self.analyze_starting_squares(engine, b_starting_squares)
            choice = None
            if w_candidates:
                rand = random.randint(0, len(w_candidates) - 1)
                choice = w_candidates[rand]
            elif b_candidates:
                rand = random.randint(0, len(b_candidates) - 1)
                choice = b_candidates[rand]
            if not engine.is_legal_starting_square(choice[0], choice[1]):
                return self.select_starting_square(engine)
            self.starting_square = choice
            return choice
        else:
            if not engine.is_legal_starting_square(self.starting_square[0], self.starting_square[1]):
                self.starting_square = None
                return self.select_starting_square(engine)
            return self.starting_square

    def analyze_starting_squares(self, engine, list_of_squares):
        candidates = []
        for square in list_of_squares:
            row, col = square[0], square[1]
            if engine.get_occupying(row, col):
                candidates = []
                break
            elif engine.is_empty(row, col):
                engine.create_piece(row, col, engine.PIECES['castle'](row, col, engine.turn))
                engine.get_occupying(row, col).update_spawn_squares(engine)
                spawn_squares_list = engine.get_occupying(row, col).spawn_squares_list
                if len(spawn_squares_list) >= 7:
                    for sq in spawn_squares_list:
                        for direction in self.directions:
                            check_row = sq[0] + direction[0]
                            check_col = sq[1] + direction[1]
                            # Always spawn near gold
                            if engine.has_gold(check_row, check_col):
                                candidates.append((row, col))
                engine.delete_piece(row, col)
        return candidates

    def select_starting_pieces(self):
        if self.piece_choices is None:
            starting_pieces = Constant.SELECTABLE_STARTING_PIECES
            number_of_starting_pieces = Constant.NUMBER_OF_STARTING_PIECES - 3
            # Force AI to choose a few pawns
            choices = ['pawn', 'pawn', 'builder']

            for _ in range(number_of_starting_pieces):
                rand = random.randint(0, len(starting_pieces) - 1)
                selection = starting_pieces[rand]
                choices.append(selection)

            choices.append('king')
            self.piece_choices = choices
            return choices
        else:
            return self.piece_choices

    def starting_piece_placements(self, spawn_list, spawn_squares_list):
            placements = []
            for _ in spawn_list:
                rand = random.randint(0, len(spawn_squares_list) - 1)
                placement = spawn_squares_list[rand]
                placements.append(placement)
                del spawn_squares_list[rand]
            self.piece_placements = placements
            return placements

    def desired_to_steal(self, engine, acting_tile):
        return 'gold'

    def desired_spawn(self, engine, acting_tile):
        spawner = acting_tile.get_occupying()
        spawn_list = Constant.SPAWN_LISTS[str(spawner)]
        legal_spawns = []
        for spawn in spawn_list:
            if engine.is_legal_spawn(spawn):
                 legal_spawns.append(spawn)
        if not legal_spawns:
            return None
        return random.choice(list(legal_spawns))

    def desired_actions(self, engine):
        actions = {}
        pieces = list(self.possible_moves.keys())
        random.shuffle(pieces)
        move = None
        for piece in pieces:
            if self.possible_moves[piece]['capture']:
                for capture in self.possible_moves[piece]['capture']:
                    captured_piece = engine.get_occupying(capture[0], capture[1])
                    if str(captured_piece) == 'king':
                        move = ('capture', capture)
                        actions[piece] = move
                        return actions
        if not move:
            for piece in pieces:
                move = None
                if piece.actions_remaining < 0:
                    pass
                else:
                    move_kinds = list(self.possible_moves[piece].keys())
                    random.shuffle(move_kinds)
                    for move_kind in move_kinds:
                        if self.possible_moves[piece][move_kind]:
                            if self.can_perform_move[move_kind](piece, engine):
                                move = (move_kind, random.choice(list(self.possible_moves[piece][move_kind])))
                                break
                actions[piece] = move
        return actions


