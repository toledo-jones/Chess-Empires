import Constant

from Piece import Piece
from Building import Building


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

        self.resource_key = {'gold_tile_1': 'gold', 'quarry_1': 'stone',
                             'sunken_quarry_1': 'stone', 'tree_tile_1': 'wood',
                             'tree_tile_2': 'wood', 'tree_tile_3': 'wood',
                             'tree_tile_4': 'wood'}

        self.total_additional_actions_this_turn = 0

        self.piece_limit = Constant.DEFAULT_PIECE_LIMIT

    def __repr__(self):
        return self.color

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
        player_resource = self.resource_key[str(resource)]
        current_resource = getattr(self, player_resource)
        setattr(self, player_resource, current_resource + harvest)


    def un_mine(self, resource, offset, additional_mining):
        harvest = self.get_harvest(resource, offset, additional_mining)
        player_resource = self.resource_key[str(resource)]
        current_resource = getattr(self, player_resource)
        setattr(self, player_resource, current_resource - harvest)

    def pray(self, building, additional_prayer):
        self.prayer += (building.yield_when_prayed + additional_prayer)

    def un_pray(self, building, additional_prayer):
        self.prayer -= (building.yield_when_prayed - additional_prayer)

    def reset_prayer(self):
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
