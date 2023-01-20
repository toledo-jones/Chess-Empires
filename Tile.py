import Constant


class Tile:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.can_contain_quarry = False
        self.occupying = None
        self.resource = None
        self.color = None
        self.protected = False
        self.protected_image = None
        self.protect_timer = 0
        self.portal_image = None
        self.protect_image_offset = Constant.IMAGES_IMAGE_MODIFY['w_protect']['OFFSET']
        self.portal_image_offset = Constant.IMAGES_IMAGE_MODIFY['w_portal']['OFFSET']
        self.protected_by = None

        self.trap = None
        self.portal = False
        self.portal_color = None
        self.connected_portal = None

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

    def draw_portal_image(self, win):
        x = (self.col * Constant.SQ_SIZE) + self.protect_image_offset[0]
        y = (self.row * Constant.SQ_SIZE) + self.protect_image_offset[1]
        win.blit(self.portal_image, (x, y))

    def draw_protected_image(self, win):
        x = (self.col * Constant.SQ_SIZE) + self.protect_image_offset[0]
        y = (self.row * Constant.SQ_SIZE) + self.protect_image_offset[1]
        win.blit(self.protected_image, (x, y))

    def untick_protect_timer(self, engine, color):
        self.protect_timer += 1
        if self.protect_timer > 0:
            self.protected = True
            self.protected_image = Constant.IMAGES[color + "_protect"]
            engine.protected_tiles.append(self)

    def tick_protect_timer(self, engine):
        self.protect_timer -= 1
        if self.protect_timer == 0:
            self.protected = False
            self.protected_image = None
            engine.protected_tiles.remove(self)

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

    def create_portal(self, color, connected_portal):
        self.portal_image = Constant.IMAGES[color + "_" + "portal"]
        self.portal_color = color
        self.portal = True
        self.connected_portal = connected_portal

    def delete_portal(self):
        self.portal_image = None
        self.portal = False

    def is_protected(self):
        return self.protected

    def is_portal(self):
        return self.portal

    def is_protected_by_opposite_color(self, color):
        if color == self.protected_by:
            return False
        else:
            return True

    def has_trap(self):
        if self.trap:
            return True

    def untrap(self):
        self.trap = None

    def set_trap(self, trap):
        self.trap = trap

    def draw(self, win):
        if self.has_resource():
            self.resource.draw(win)

        if self.protected:
            self.draw_protected_image(win)

        if self.portal:
            self.draw_portal_image(win)

        if self.trap:
            self.trap.draw(win)

        if self.has_occupying():
            self.occupying.draw_highlights(win)
            self.occupying.draw(win)
