class Tile:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.occupying = None
        self.resource = None

    def render(self, board):
        to_be_rendered = []
        if self.get_resource():
            to_be_rendered.append(self.resource.render(board))
        if self.get_occupying():
            to_be_rendered.append(self.occupying.render(board))
        return to_be_rendered

    def set_occupying(self, unit):
        self.occupying = unit

    def get_occupying(self):
        return self.occupying

    def set_resource(self, resource):
        self.resource = resource

    def get_resource(self):
        return self.resource
