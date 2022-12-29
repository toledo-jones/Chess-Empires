import Constant


class Tile:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.occupying = None
        self.resource = None
        self.color = None
        self.protected = False
        self.protected_image = None
        self.protect_timer = 0
        self.protect_image_offset = Constant.IMAGES_IMAGE_MODIFY['w_protect']['OFFSET']
        self.protected_by = None

    def set_occupying(self, occupying):
        self.occupying = occupying

    def set_resource(self, resource):
        self.resource = resource

    def has_resource(self):
        if self.resource is not None:
            return True

    def has_occupying(self):
        if self.occupying is not None:
            return True

    def get_position(self):
        return self.row, self.col

    def get_occupying(self):
        return self.occupying

    def get_resource(self):
        return self.resource

    def remove_resource(self):
        self.resource = None

    def draw_protected_image(self, win):
        x = (self.col * Constant.SQ_SIZE) + self.protect_image_offset[0]
        y = (self.row * Constant.SQ_SIZE) + self.protect_image_offset[1]
        win.blit(self.protected_image, (x, y))

    def untick_protect_timer(self, color):
        self.protect_timer += 1
        if self.protect_timer > 0:
            self.protected = True
            self.protected_image = Constant.IMAGES[color + "_protect"]

    def tick_protect_timer(self):
        self.protect_timer -= 1
        if self.protect_timer == 0:
            self.protected = False
            self.protected_image = None

    def unprotect(self):
        self.protect_timer = 0
        self.protected = False
        self.protected_image = None
        self.protected_by = None

    def protect(self, color):
        self.protected_image = Constant.IMAGES[color + "_" + "protect"]
        self.protected = True
        self.protect_timer = 2
        self.protected_by = color

    def is_protected(self):
        return self.protected

    def is_protected_by_opposite_color(self, color):
        if color == self.protected_by:
            return False
        else:
            return True

    def draw(self, win):
        if self.has_resource():
            self.resource.draw(win)

        if self.protected:
            self.draw_protected_image(win)

        if self.has_occupying():
            self.occupying.draw_highlights(win)
            self.occupying.draw(win)
