import random
import pygame
import Constant



class Resource:
    def __init__(self, row, col, owner=None):
        self.row = row
        self.col = col
        self.owner = owner
        self.sprite_offset = None
        self.key = Constant.RESOURCE_YIELD_KEY[str(self)]
        if self.key is not None:
            self.remaining = self.get_total_yield()
            self.harvest_yield_variance = []
            self.harvest_yield_variance.append(self.get_harvest_yield_variance())
            self.harvest_history = -1   # index of all times this resource has been harvested.
        if self.sprite_offset is None:
            self.sprite_offset = self.get_resource_offset()

    def get_harvest_yield_variance(self):
        variance = Constant.HARVEST_YIELD_VARIANCE[self.key]
        variation = random.randint(variance[0], variance[1])
        return variation

    def harvest(self, piece):
        if self.harvest_history == len(self.harvest_yield_variance) - 1:
            self.harvest_history += 1
            self.harvest_yield_variance.append(self.get_harvest_yield_variance())
        base_harvest = Constant.BASE_YIELD_PER_HARVEST[piece][self.key]
        harvest_yield = base_harvest + self.harvest_yield_variance[self.harvest_history]
        if self.remaining < harvest_yield:
            harvest_yield = self.remaining
        self.remaining -= harvest_yield
        return harvest_yield

    def unharvest(self, harvest):
        self.remaining += harvest

    def get_total_yield(self):
        total = Constant.BASE_TOTAL_YIELD[self.key]
        variance = Constant.TOTAL_YIELD_VARIANCE[self.key]
        variation = random.randint(variance[0], variance[1])
        total += variation
        return total

    import random

    def get_resource_offset(self):
        # Retrieve the size of the resource image as a tuple (width, height)
        image_size = Constant.RESOURCES_IMAGE_MODIFY[str(self)]['SCALE']

        # Get the size of the square where the image will be placed
        square_size = Constant.SQ_SIZE

        # Calculate the horizontal offset to center the image within the square
        offset_x = (square_size - image_size[0]) // 2

        # Calculate the vertical offset to center the image within the square
        offset_y = (square_size - image_size[1]) // 2

        # Generate a small random offset within approximately ±1/10th of the square size
        random_offset_x = random.randint(-square_size // 10, square_size // 10)
        random_offset_y = random.randint(-square_size // 10, square_size // 10)

        # Apply the random offset to the calculated position
        offset_x += random_offset_x
        offset_y += random_offset_y

        # Return the final computed offsets as a tuple (x, y)
        return offset_x, offset_y

        # if random.randint(1, 2) > 1:
        #     offset = Constant.RESOURCES_IMAGE_MODIFY[str(self)]['OFFSET']
        #     r = offset[0] + random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
        #     z = offset[1] + random.randint(Constant.SQ_SIZE // -10, Constant.SQ_SIZE // 10)
        #     r = offset[0]
        #     z = offset[1]
        #     return r, z
        # else:
        #     return Constant.RESOURCES_IMAGE_MODIFY[str(self)]['OFFSET']

    def get_position(self):
        return self.row, self.col

    def get_color(self):
        return self.owner

    def draw(self, win):
        sprite = Constant.RESOURCES[str(self)]
        x = self.col * Constant.SQ_SIZE + self.sprite_offset[0]
        y = self.row * Constant.SQ_SIZE + self.sprite_offset[1]
        win.blit(sprite, (x, y))


class Gold(Resource):
    def __repr__(self):
        return 'gold_tile' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        self.sprite_id = 1
        super().__init__(row, col, owner)

    def get_sprite_id(self):
        return self.sprite_id


class Wood(Resource):
    def __repr__(self):
        return 'tree_tile' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        sprite_id = random.randint(1, 8)
        self.sprite_id = sprite_id
        super().__init__(row, col, owner)

    def get_sprite_id(self):
        return self.sprite_id


class Quarry(Resource):
    def __repr__(self):
        return 'quarry' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        self.sprite_id = 1
        super().__init__(row, col, owner)

    def get_sprite_id(self):
        return self.sprite_id


class SunkenQuarry(Resource):
    def __repr__(self):
        return 'sunken_quarry' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        self.sprite_id = 1
        super().__init__(row, col, owner)

    def get_sprite_id(self):
        return self.sprite_id


class DepletedQuarry(Resource):
    def __repr__(self):
        return 'depleted_quarry' + "_" + str(self.get_sprite_id())

    def __init__(self, row, col, owner=None):
        self.sprite_id = 1
        super().__init__(row, col, owner)

    def get_sprite_id(self):
        return self.sprite_id

