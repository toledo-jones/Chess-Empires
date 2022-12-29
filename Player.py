from Behavior import *


class Player:
    def __init__(self, color):
        self.color = color

        self.gold = Constant.STARTING_GOLD
        self.wood = Constant.STARTING_WOOD
        self.stone = Constant.STARTING_STONE

        self.prayer = Constant.STARTING_PRAYER

        self.actions_remaining = Constant.DEFAULT_ACTIONS_REMAINING

        self.king_position = None

        self.pieces = []

        self.captured_pieces = []

        self.starting_pieces = []

        self.total_additional_actions_this_turn = 0

        self.piece_limit = Constant.DEFAULT_PIECE_LIMIT

    def __repr__(self):
        return self.color

    def begin_turn(self, engine):
        # only implemented for AI
        pass

    def steal(self, kind, value):
        if kind == 'wood':
            self.wood += value
        elif kind == 'gold':
            self.gold += value
        elif kind == 'stone':
            self.stone += value

    def invert_steal(self, kind, value):
        if kind == 'wood':
            self.wood -= value
        elif kind == 'gold':
            self.gold -= value
        elif kind == 'stone':
            self.stone -= value

    def get_harvest(self, resource, offset, additional_mining):
        harvest = resource.yield_per_harvest + offset + additional_mining
        if harvest < 0:
            harvest = 0
        return harvest

    def mine(self, resource, offset, additional_mining):
        harvest = self.get_harvest(resource, offset, additional_mining)
        player_resource = Constant.RESOURCE_KEY[str(resource)]
        current_resource = getattr(self, player_resource)
        setattr(self, player_resource, current_resource + harvest)

    def un_mine(self, resource, offset, additional_mining):
        harvest = self.get_harvest(resource, offset, additional_mining)
        player_resource = Constant.RESOURCE_KEY[str(resource)]
        current_resource = getattr(self, player_resource)
        setattr(self, player_resource, current_resource - harvest)

    def pray(self, building, additional_prayer):
        self.prayer += (building.yield_when_prayed + additional_prayer)

    def un_pray(self, building, additional_prayer):
        self.prayer -= (building.yield_when_prayed + additional_prayer)

    def reset_prayer(self):
        if Constant.DEBUG_START:
            self.prayer = Constant.DEBUG_STARTING_PRAYER
        else:
            self.prayer = Constant.STARTING_PRAYER

    def get_prayer(self):
        return self.prayer

    def do_ritual(self, cost):
        self.prayer -= cost

    def undo_ritual(self, cost):
        self.prayer += cost

    def set_prayer(self, prayer):
        self.prayer = prayer

    def purchase(self, cost):
        self.wood -= cost['log']
        self.gold -= cost['gold']
        self.stone -= cost['stone']

    def un_purchase(self, cost):
        self.wood += cost['log']
        self.gold += cost['gold']
        self.stone += cost['stone']

    def get_current_population(self):
        count = 0
        for piece in self.pieces:
            count += piece.get_population_value()
        return count

    def can_add_piece(self, piece):
        population = self.get_current_population()
        if Constant.PIECE_POPULATION[piece] + population <= self.piece_limit:
            return True
        elif Constant.ADDITIONAL_PIECE_LIMIT[piece] + self.piece_limit > self.piece_limit:
            return True
        elif Constant.PIECE_POPULATION[piece] == 0:
            return True

    def get_piece_limit(self):
        return self.piece_limit

    def set_piece_limit(self, limit):
        self.piece_limit = limit

    def add_additional_piece_limit(self, limit):
        self.piece_limit += limit

    def remove_additional_piece_limit(self, limit):
        self.piece_limit -= limit

    def reset_actions_remaining(self):
        self.actions_remaining = Constant.DEFAULT_ACTIONS_REMAINING

    def set_actions_remaining(self, actions):
        self.actions_remaining = actions

    def get_actions_remaining(self):
        return self.actions_remaining

    def add_additional_actions(self, actions):
        self.actions_remaining += actions

    def remove_additional_actions(self, actions):
        self.actions_remaining -= actions

    def reset_piece_limit(self):
        self.piece_limit = Constant.DEFAULT_PIECE_LIMIT

    def can_do_action(self):
        if self.actions_remaining != 0:
            return True

    def do_action(self):
        self.actions_remaining -= 1

    def undo_action(self):
        self.actions_remaining += 1


class AI(Player):
    def __init__(self, color):
        super().__init__(color)
        self.BEHAVIORS = {'random': Random}

        rand = random.choice(list(self.BEHAVIORS))

        self.behavior = self.BEHAVIORS[rand]()

    def begin_turn(self, engine):
        engine.set_state('ai playing')
        engine.state[-1].complete_turn()

    def update_all_possible_moves(self, engine):
        self.behavior.all_possible_moves(self.pieces, engine)

    def fulfill_move_parameters(self, engine, selected_move):
        pieces = list(selected_move.keys())

        piece = pieces[0]
        move = selected_move[piece]
        move_kind = move[0]
        row, col = move[1]
        action_tile = engine.board[row][col]
        acting_tile = engine.board[piece.row][piece.col]
        return self.behavior.fulfill_move_parameters[move_kind](engine, acting_tile, action_tile)

    def determine_most_desired_action(self, desired_actions):
        selected_move = None
        for move_kind in self.behavior.move_priority:
            for piece in desired_actions:
                if desired_actions[piece] is not None:
                    if move_kind == desired_actions[piece][0]:
                        selected_move = {piece: desired_actions[piece]}
                        break
            if selected_move:
                break
        return selected_move

    def update_desired_actions(self, engine):
        # Select one legal move for each piece
        desired_actions = self.behavior.desired_actions(engine)
        return desired_actions

    def harvest_resources(self, engine):
        return self.behavior.harvest_resources(engine)
