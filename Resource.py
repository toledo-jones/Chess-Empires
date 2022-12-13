import random

import Constant


class Resource:
    def __init__(self, row, col, owner=None):
        self.row = row
        self.col = col
        self.owner = owner
        self.offset = None
        if self.offset is None:
            self.offset = self.get_resource_offset()

    def get_resource_offset(self):
        if random.randint(1, 2) > 1:
            offset = Constant.RESOURCES_IMAGE_MODIFY[str(self)]['OFFSET']
            r = offset[0] + random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
            z = offset[1] + random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
            return r, z
        else:
            return Constant.RESOURCES_IMAGE_MODIFY[str(self)]['OFFSET']

    def get_position(self):
        return self.row, self.col

    def get_color(self):
        return self.owner

    def draw(self, win):
        draw_this = Constant.RESOURCES[str(self)]
        x = self.col * Constant.SQ_SIZE + self.offset[0]
        y = self.row * Constant.SQ_SIZE + self.offset[1]
        win.blit(draw_this, (x, y))


class Gold(Resource):
    def __repr__(self):
        return 'gold_tile' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        self.sprite_id = 1
        super().__init__(row, col, owner)
        self.offsetIndex = []
        self.remaining = Constant.GOLD_TOTAL_MINED + random.randint(-2, 1)
        self.yield_per_harvest = Constant.GOLD_YIELD_PER_HARVEST
        for r in range(self.remaining):
            self.offsetIndex.append(random.randint(-1, 1))

    def get_sprite_id(self):
        return self.sprite_id


class Wood(Resource):
    def __repr__(self):
        return 'tree_tile' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        sprite_id = random.randint(1, 4)
        self.sprite_id = sprite_id
        super().__init__(row, col, owner)
        self.remaining = 1
        self.offsetIndex = []
        self.yield_per_harvest = Constant.WOOD_YIELD_PER_HARVEST

        for r in range(self.remaining):
            self.offsetIndex.append(random.randint(Constant.WOOD_VARIANCE[0], Constant.WOOD_VARIANCE[1]))

    def get_sprite_id(self):
        return self.sprite_id


class Quarry(Resource):
    def __repr__(self):
        return 'quarry' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        self.sprite_id = 1
        super().__init__(row, col, owner)
        self.remaining = Constant.QUARRY_TOTAL_MINED + random.randint(-2, 1)
        self.offsetIndex = []
        self.yield_per_harvest = Constant.STONE_YIELD_PER_HARVEST
        self.owner = owner
        for r in range(self.remaining):
            self.offsetIndex.append(random.randint(Constant.STONE_VARIANCE[0], Constant.STONE_VARIANCE[1]))

    def get_sprite_id(self):
        return self.sprite_id


class SunkenQuarry(Resource):
    def __repr__(self):
        return 'sunken_quarry' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        self.sprite_id = 1
        super().__init__(row, col, owner)
        self.remaining = Constant.SUNKEN_QUARRY_TOTAL_MINED + random.randint(0, 1)
        self.offsetIndex = []
        self.yield_per_harvest = Constant.SUNKEN_QUARRY_YIELD_PER_HARVEST
        self.owner = owner
        for r in range(self.remaining):
            self.offsetIndex.append(random.randint(0, 1))

    def get_sprite_id(self):
        return self.sprite_id

class DepletedQuarry(Resource):
    def __repr__(self):
        return 'depleted_quarry' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        self.sprite_id = 1
        super().__init__(row, col, owner)
        self.remaining = Constant.DEPLETED_QUARRY_REMAINING
        self.offsetIndex = []
        self.yield_per_harvest = Constant.DEPLETED_QUARRY_YIELD_PER_HARVEST
        self.owner = owner

    def get_sprite_id(self):
        return self.sprite_id