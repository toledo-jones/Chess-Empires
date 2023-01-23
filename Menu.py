import os
from Unit import *


class Menu:
    def __init__(self, win, engine):
        self.win = win
        self.engine = engine
        self.pieces = {'w': Constant.W_PIECES | Constant.W_BUILDINGS, 'b': Constant.B_PIECES | Constant.B_BUILDINGS}
        self.menu_boundary_buffer = round(Constant.SQ_SIZE * 1.5)

    def get_initial_menu_position(self, row, col):
        return col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2, row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2

    def correct_menu_boundary(self):
        x, y = self.initial_menu_position

        if x + self.menu_width >= Constant.BOARD_WIDTH_PX:
            x -= self.menu_width
        if Constant.BOARD_HEIGHT_PX - self.menu_height <= Constant.SQ_SIZE:
            y = Constant.SQ_SIZE // 2
        elif y + self.menu_height >= Constant.BOARD_HEIGHT_PX:
            y -= self.menu_height

            if y <= 0:
                y += self.menu_height // 2
                if y + self.menu_height >= Constant.BOARD_HEIGHT_PX:
                    y = self.menu_boundary_buffer
                elif y <= 0:
                    y = Constant.BOARD_HEIGHT_PX - (self.menu_boundary_buffer // 2) - self.menu_height
        return x, y

    def mouse_in_menu_bounds(self):
        # determine close
        mouse_position = pygame.mouse.get_pos()
        x, y = mouse_position[0], mouse_position[1]
        menu_open = True
        # check if mouse is bounds of board
        if x >= Constant.BOARD_WIDTH_PX - 1 or x == 0:
            menu_open = False
        elif y == Constant.BOARD_HEIGHT_PX - 1 or y == 0:
            menu_open = False
        # check if mouse is in bounds of menu
        else:
            if x > self.menu_position_x + self.menu_boundary_buffer_x or x < self.menu_position_x - self.menu_boundary_buffer:
                menu_open = False
            elif y > self.menu_position_y + self.menu_boundary_buffer_y or y < self.menu_position_y - self.menu_boundary_buffer:
                menu_open = False

        return menu_open


class Notification(Menu):
    def __init__(self, row, col, win, engine, message='blank'):
        super().__init__(win, engine)
        self.row = row
        self.col = col
        self.color = Constant.turn_to_color[self.engine.turn]
        self.message = Constant.NOTIFICATIONS[message]
        self.font_size = round(Constant.SQ_SIZE * .3)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)

        self.menu_width = Constant.SQ_SIZE * 3
        self.menu_height = Constant.SQ_SIZE + len(self.message) * Constant.SQ_SIZE
        self.y_buffer_between_messages = Constant.SQ_SIZE

        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer

        self.initial_menu_position = self.get_initial_menu_position(self.row, self.col)
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        self.menu = pygame.Surface((self.menu_width, self.menu_height))

        self.text = 'ok'
        self.ok_text_surface = self.font.render(self.text, True, self.color)

        self.message_text_surfaces = []
        for message in self.message:
            self.message_text_surfaces.append(self.font.render(message, True, self.color))

        self.ok_display_x = self.menu_width // 2 - self.ok_text_surface.get_width() // 2
        self.ok_display_y = self.menu_height - self.ok_text_surface.get_height()

        self.highlight_display_x = 0
        self.highlight_display_y = self.menu_height - Constant.SQ_SIZE

        self.square = pygame.Surface((self.menu_width, Constant.SQ_SIZE))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.highlight = False

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        y_buffer = 0
        for message in self.message_text_surfaces:
            text_display_x = self.menu_width // 2 - message.get_width() // 2
            self.menu.blit(message, (text_display_x, y_buffer))
            y_buffer += self.y_buffer_between_messages
        if self.highlight:
            self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
            self.menu.blit(self.square, (self.highlight_display_x, self.highlight_display_y))
        self.menu.blit(self.ok_text_surface, (self.ok_display_x, self.ok_display_y))
        self.win.blit(self.menu, (self.menu_position_x,self.menu_position_y))

    def left_click(self):
        menu_above_ok_button = len(self.message) * round(Constant.SQ_SIZE * .8)
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] < self.menu_position_x + self.menu_width:
            if self.menu_position_y + menu_above_ok_button < pos[1] < self.menu_position_y + self.menu_height:
                self.engine.close_menus()

    def right_click(self):
        self.engine.close_menus()

    def mouse_move(self):
        menu_above_ok_button = len(self.message) * round(Constant.SQ_SIZE * .8)
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] < self.menu_position_x + self.menu_width:
            if self.menu_position_y + menu_above_ok_button < pos[1] < self.menu_position_y + self.menu_height:
                self.highlight = True
                return

        self.highlight = False


class RitualMenu(Menu):
    def __init__(self, row, col, win, engine, ritual_list):
        self.ritual_list = ritual_list
        self.row = row
        self.col = col
        super().__init__(win, engine)
        self.initial_menu_position = self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2, self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 6
        self.horizontal_buffer_between_costs = round(Constant.SQ_SIZE * 1.3)
        self.bar_width = Constant.IMAGES['prayer_bar'].get_width()
        self.bar_height = Constant.IMAGES['prayer_bar'].get_height()
        self.bar_end_width = Constant.IMAGES['prayer_bar_end'].get_width()
        self.rituals = Constant.PRAYER_RITUALS
        self.ritual_width = self.rituals['w_gold_general'].get_width()
        self.ritual_height = self.rituals['w_gold_general'].get_height()
        self.menu_width = self.ritual_width + self.vertical_buffer_between_pieces + self.bar_end_width * 16 + self.bar_width
        self.menu_height = len(ritual_list) * self.ritual_height
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu = pygame.Surface((self.menu_width, self.menu_height))

        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.casting = None

        self.prayer_bar_edge = self.vertical_buffer_between_pieces + self.ritual_width
        self.prayer_bar_end_edge = self.prayer_bar_edge + self.bar_width
        self.y_buffer = self.vertical_buffer_between_pieces // 2 + self.ritual_height // 2 - self.bar_height // 2
        self.ritual_highlight_list = []
        self.square = pygame.Surface((self.menu_width, round(1 / len(self.ritual_list) * self.menu_height)))
        self.available_menu_space_for_prayer_bar = self.menu_width - self.ritual_width

        for _ in self.ritual_list:
            self.ritual_highlight_list.append(False)

    def full_length_of_prayer_bar(self, length_of_ritual):
        return self.bar_end_width * length_of_ritual + self.bar_width

    def ritual_clicked(self):
        pos = pygame.mouse.get_pos()
        mp = self.menu_position_y
        length = len(self.ritual_list)
        mh = self.menu_height

        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.ritual_list)):
                a = x / length
                b = a * mh
                c = b + mp
                d = (x + 1) / length
                e = d * mh
                f = e + mp
                r = range(round(c), round(f))
                if pos[1] in r:
                    return self.ritual_list[x]

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.ritual_list)):
                a = x / len(self.ritual_list)
                b = a * self.menu_height
                c = b + self.menu_position_y
                d = (x + 1) / len(self.ritual_list)
                e = d * self.menu_height
                f = e + self.menu_position_y
                r = range(round(c), round(f))
                if pos[1] in r:
                    self.ritual_highlight_list[x] = True
                    for z in range(len(self.ritual_highlight_list)):
                        if z is not x:
                            self.ritual_highlight_list[z] = False
        else:
            for _ in self.ritual_highlight_list:
                _ = False

    def left_click(self):
        self.casting = self.ritual_clicked()
        if self.casting is None or not self.engine.is_legal_ritual(self.casting):
            self.engine.state[-1].revert_to_playing_state()
        else:
            self.engine.menus = []
            self.engine.transfer_to_ritual_state(self.casting)

    def right_click(self):
        self.engine.state[-1].revert_to_playing_state()

    def draw(self, win):
        self.menu.fill(Constant.MENU_COLOR)
        for x in range(len(self.ritual_list)):
            a = x / len(self.ritual_list)
            b = a * self.menu_height
            if self.ritual_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        # Prayer Counter
        y_buffer_piece = 0
        y_buffer_prayer = self.y_buffer
        for ritual in self.ritual_list:
            length_of_this_prayer_bar = self.full_length_of_prayer_bar(Constant.PRAYER_COSTS[ritual]['prayer'])
            bar_end_edge = self.ritual_width + self.available_menu_space_for_prayer_bar // 2 - length_of_this_prayer_bar // 2
            bar_edge = bar_end_edge - self.bar_width
            self.menu.blit(Constant.IMAGES['prayer_bar'], (bar_edge, y_buffer_prayer))
            for z in range(Constant.PRAYER_COSTS[ritual]['prayer']):
                new_edge = bar_end_edge + self.bar_end_width * (z)
                self.menu.blit(Constant.IMAGES['prayer_bar_end'], (new_edge, y_buffer_prayer))

            y_buffer_prayer += self.y_buffer + self.ritual_height // 2
            self.menu.blit(self.rituals[self.engine.turn + "_" + ritual], (0, y_buffer_piece))
            y_buffer_piece += self.ritual_height

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))


class TraderMenu(Menu):
    def __init__(self, row, col, win, engine, resource_list, amounts, trade_arrow):
        self.row = row
        self.col = col
        self.key = {'log': 'wood', 'gold_coin': 'gold', 'stone': 'stone'}
        self.resource_list = resource_list
        super().__init__(win, engine)
        self.trade_arrow = trade_arrow
        self.amounts = amounts
        self.player = self.engine.players[self.engine.turn]
        self.give_image = Constant.IMAGES['give']
        self.selected = None
        self.horizontal_buffer = Constant.SQ_SIZE
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 4
        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.font_color = Constant.turn_to_color[self.engine.turn]
        self.resource_height = Constant.IMAGES['gold_coin'].get_width()
        self.resource_width = Constant.IMAGES['gold_coin'].get_height()
        self.menu_width = self.resource_width + self.horizontal_buffer + self.resource_width + Constant.SQ_SIZE
        self.menu_height = len(self.resource_list) * (self.resource_height + self.vertical_buffer_between_pieces)
        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        self.initial_menu_position = self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2, self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.spawn_highlight_list = []
        self.square = pygame.Surface((self.menu_width, round(1 / len(self.resource_list) * self.menu_height)))
        for _ in self.resource_list:
            self.spawn_highlight_list.append(False)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def resource_selected(self):
        pos = pygame.mouse.get_pos()
        mp = self.menu_position_y
        length = len(self.resource_list)
        mh = self.menu_height

        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.resource_list)):
                a = x / length
                b = a * mh
                c = b + mp
                d = (x + 1) / length
                e = d * mh
                f = e + mp
                r = range(round(c), round(f))
                if pos[1] in r:
                    return self.resource_list[x]

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.resource_list)):
                a = x / len(self.resource_list)
                b = a * self.menu_height
                c = b + self.menu_position_y
                d = (x + 1) / len(self.resource_list)
                e = d * self.menu_height
                f = e + self.menu_position_y
                r = range(round(c), round(f))
                if pos[1] in r:
                    self.spawn_highlight_list[x] = True
                    for z in range(len(self.spawn_highlight_list)):
                        if z is not x:
                            self.spawn_highlight_list[z] = False
        else:
            for _ in self.spawn_highlight_list:
                _ = False

    def draw(self, win):
        self.menu.fill(Constant.MENU_COLOR)
        for x in range(len(self.resource_list)):
            a = x / len(self.resource_list)
            b = a * self.menu_height
            if self.spawn_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        y_buffer = 0
        for p in self.resource_list:
            self.menu.blit(Constant.IMAGES[p], (self.horizontal_buffer // 2, y_buffer))
            amount_text_surface = self.font.render(': ' + str(self.amounts[p]), True, self.font_color)
            self.menu.blit(self.trade_arrow, (self.resource_width + 2 * self.horizontal_buffer, y_buffer))
            self.menu.blit(amount_text_surface, (self.resource_width + self.horizontal_buffer, y_buffer))
            y_buffer += self.menu_height // len(self.resource_list)

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class GiveMenu(TraderMenu):
    def __init__(self, row, col, win, engine, resource_list):
        self.player = engine.players[engine.turn]
        self.amounts = {'log': engine.trade_handler.get_give_conversion('wood', self.player),
                        'gold_coin': engine.trade_handler.get_give_conversion('gold', self.player),
                        'stone': engine.trade_handler.get_give_conversion('stone', self.player)}
        self.trade_arrow = Constant.IMAGES['give']
        super().__init__(row, col, win, engine, resource_list, self.amounts, self.trade_arrow)

    def right_click(self):
        self.engine.piece_trading = None
        self.engine.state[-1].revert_to_playing_state()

    def left_click(self):
        self.selected = self.resource_selected()
        if self.selected is not None:
            amount_given = self.amounts[self.selected]
            self.engine.trading.append((self.selected, amount_given))
            self.engine.close_menus()
            resource_list = []
            resources = ['log', 'gold_coin', 'stone']
            for resource in resources:
                if resource is not self.selected:
                    resource_list.append(resource)
            row, col = Constant.convert_pos(pygame.mouse.get_pos())
            menu = ReceiveMenu(row, col, self.win, self.engine, resource_list, amount_given)
            self.engine.menus.append(menu)


class ReceiveMenu(TraderMenu):
    def __init__(self, row, col, win, engine, resource_list, amount_given):
        self.amount_given = amount_given
        self.amounts = {'log': engine.trade_handler.get_receive_conversion(self.amount_given, 'wood'),
                        'gold_coin': engine.trade_handler.get_receive_conversion(self.amount_given, 'gold'),
                        'stone': engine.trade_handler.get_receive_conversion(self.amount_given, 'stone')}
        self.trade_arrow = Constant.IMAGES['receive']
        super().__init__(row, col, win, engine, resource_list, self.amounts, self.trade_arrow)

    def left_click(self):
        self.selected = self.resource_selected()
        if self.selected is not None:
            amount = self.engine.trade_handler.get_receive_conversion(self.amount_given, self.key[self.selected])
            self.engine.menus = []
            self.engine.trading.append((self.selected, amount))
            self.engine.trade()

    def right_click(self):
        self.engine.close_menus()
        self.engine.trading = []
        row, col = Constant.convert_pos(pygame.mouse.get_pos())
        self.engine.create_trader_menu(row, col, False)


class StealingMenu(Menu):
    def __init__(self, row, col, win, engine):
        self.row = row
        self.col = col
        self.spawn_list = ['log', 'gold_coin', 'stone']
        self.key = {'log': 'wood', 'gold_coin': 'gold', 'stone': 'stone'}

        self.type_stolen_from = None

        super().__init__(win, engine)
        piece = self.engine.get_occupying(row, col)
        if isinstance(piece, Piece):
            if isinstance(piece, Trader):
                self.type_stolen_from = 'trader'
            else:
                self.type_stolen_from = 'piece'
        elif isinstance(piece, Building):
            self.type_stolen_from = 'building'

        self.amounts = {'log': self.engine.stealing_values('wood', self.type_stolen_from),
                        'gold_coin': self.engine.stealing_values('gold', self.type_stolen_from),
                        'stone': self.engine.stealing_values('stone', self.type_stolen_from)}
        self.horizontal_buffer = Constant.SQ_SIZE
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 4
        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.font_color = Constant.turn_to_color[self.engine.turn]
        self.resource_height = Constant.IMAGES['gold_coin'].get_width()
        self.resource_width = Constant.IMAGES['gold_coin'].get_height()
        self.menu_width = self.resource_width + self.horizontal_buffer + self.resource_width
        self.menu_height = len(self.spawn_list) * (self.resource_height + self.vertical_buffer_between_pieces)
        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        self.initial_menu_position = self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2, self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.spawn_highlight_list = []
        self.square = pygame.Surface((self.menu_width, round(1 / len(self.spawn_list) * self.menu_height)))
        for _ in self.spawn_list:
            self.spawn_highlight_list.append(False)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def resource_selected(self):
        pos = pygame.mouse.get_pos()
        mp = self.menu_position_y
        length = len(self.spawn_list)
        mh = self.menu_height

        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.spawn_list)):
                a = x / length
                b = a * mh
                c = b + mp
                d = (x + 1) / length
                e = d * mh
                f = e + mp
                r = range(round(c), round(f))
                if pos[1] in r:
                    return self.spawn_list[x]

    def left_click(self):
        self.engine.stealing = None
        stolen_resource = self.resource_selected()
        amount = self.amounts[stolen_resource]
        if stolen_resource:
            self.engine.menus = []
            self.engine.stealing = [self.key[stolen_resource], amount]
        else:
            self.engine.stealing = None
            self.engine.state[-1].revert_to_playing_state()

    def right_click(self):
        self.engine.ritual_summon_resource = None
        self.engine.state[-1].revert_to_playing_state()

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.spawn_list)):
                a = x / len(self.spawn_list)
                b = a * self.menu_height
                c = b + self.menu_position_y
                d = (x + 1) / len(self.spawn_list)
                e = d * self.menu_height
                f = e + self.menu_position_y
                r = range(round(c), round(f))
                if pos[1] in r:
                    self.spawn_highlight_list[x] = True
                    for z in range(len(self.spawn_highlight_list)):
                        if z is not x:
                            self.spawn_highlight_list[z] = False
        else:
            for _ in self.spawn_highlight_list:
                _ = False

    def draw(self, win):
        self.menu.fill(Constant.MENU_COLOR)
        for x in range(len(self.spawn_list)):
            a = x / len(self.spawn_list)
            b = a * self.menu_height
            if self.spawn_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        y_buffer = 0
        for p in self.spawn_list:
            self.menu.blit(Constant.IMAGES[p], (self.horizontal_buffer // 2, y_buffer))
            amount_text_surface = self.font.render(': ' + str(self.amounts[p]), True, self.font_color)
            self.menu.blit(amount_text_surface, (self.resource_width + self.horizontal_buffer, y_buffer))
            y_buffer += self.menu_height // len(self.spawn_list)

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class ResourceMenu(Menu):

    def __init__(self, row, col, win, engine):
        self.row = row
        self.col = col
        rand = str(random.randint(1, 4))
        self.spawn_list = ['gold_tile_1', 'quarry_1', 'tree_tile_' + rand, 'sunken_quarry_1']
        super().__init__(win, engine)
        self.horizontal_buffer = Constant.SQ_SIZE
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 4
        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.resource_height = Constant.RESOURCES['gold_tile_1'].get_width()
        self.resource_width = Constant.RESOURCES['gold_tile_1'].get_height()
        self.menu_width = self.resource_width + self.horizontal_buffer
        self.menu_height = len(self.spawn_list) * (self.resource_height + self.vertical_buffer_between_pieces)
        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        self.initial_menu_position = self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2, self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.spawn_highlight_list = []
        self.square = pygame.Surface((self.menu_width, round(1 / len(self.spawn_list) * self.menu_height)))
        for _ in self.spawn_list:
            self.spawn_highlight_list.append(False)

    def resource_selected(self):
        pos = pygame.mouse.get_pos()
        mp = self.menu_position_y
        length = len(self.spawn_list)
        mh = self.menu_height

        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.spawn_list)):
                a = x / length
                b = a * mh
                c = b + mp
                d = (x + 1) / length
                e = d * mh
                f = e + mp
                r = range(round(c), round(f))
                if pos[1] in r:
                    return self.spawn_list[x]

    def left_click(self):
        self.engine.ritual_summon_resource = None
        self.spawning = self.resource_selected()
        if self.spawning is not None:
            self.engine.menus = []
            self.engine.ritual_summon_resource = self.spawning
        else:
            self.engine.ritual_summon_resource = None
            self.engine.state[-1].revert_to_playing_state()

    def right_click(self):
        self.engine.ritual_summon_resource = None
        self.engine.state[-1].revert_to_playing_state()

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.spawn_list)):
                a = x / len(self.spawn_list)
                b = a * self.menu_height
                c = b + self.menu_position_y
                d = (x + 1) / len(self.spawn_list)
                e = d * self.menu_height
                f = e + self.menu_position_y
                r = range(round(c), round(f))
                if pos[1] in r:
                    self.spawn_highlight_list[x] = True
                    for z in range(len(self.spawn_highlight_list)):
                        if z is not x:
                            self.spawn_highlight_list[z] = False
        else:
            for _ in self.spawn_highlight_list:
                _ = False

    def draw(self, win):
        self.menu.fill(Constant.MENU_COLOR)
        for x in range(len(self.spawn_list)):
            a = x / len(self.spawn_list)
            b = a * self.menu_height
            if self.spawn_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        y_buffer = 0
        for p in self.spawn_list:
            self.menu.blit(Constant.RESOURCES[p], (self.horizontal_buffer // 2, y_buffer))
            y_buffer += self.menu_height // len(self.spawn_list)

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class SpawningMenu(Menu):
    def __init__(self, row, col, win, engine, spawn_list, spawner):
        self.row = row
        self.col = col
        self.spawn_list = spawn_list
        self.spawner = spawner
        super().__init__(win, engine)
        self.horizontal_buffer_between_costs = round(Constant.SQ_SIZE * 1.3)
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 4
        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.test_text = self.font.render("10", True, Constant.RED)
        self.menu_width = Constant.SQ_SIZE + (
                3 * self.horizontal_buffer_between_costs + self.test_text.get_width())
        self.menu_height = len(spawn_list) * Constant.SPAWNING_MENU_HEIGHT_BUFFER + (
            self.vertical_buffer_between_pieces)
        self.initial_menu_position = self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2, self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.spawning = None

        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        self.piece_x = self.vertical_buffer_between_pieces
        self.log_x = self.piece_x + self.horizontal_buffer_between_costs
        self.gold_x = self.log_x + self.horizontal_buffer_between_costs
        self.stone_x = self.gold_x + self.horizontal_buffer_between_costs
        self.player = self.engine.players[self.engine.turn]
        self.spawn_highlight_list = []
        self.square = pygame.Surface((self.menu_width, round(1 / len(self.spawn_list) * self.menu_height)))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        for _ in self.spawn_list:
            self.spawn_highlight_list.append(False)

    def piece_spawned(self):
        pos = pygame.mouse.get_pos()
        mp = self.menu_position_y
        length = len(self.spawn_list)
        mh = self.menu_height

        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.spawn_list)):
                a = x / length
                b = a * mh
                c = b + mp
                d = (x + 1) / length
                e = d * mh
                f = e + mp
                r = range(round(c), round(f))
                if pos[1] in r:
                    return self.spawn_list[x]

    def left_click(self):
        self.engine.spawning = None
        self.spawning = self.piece_spawned()
        if not self.spawning or not self.engine.is_legal_spawn(self.spawning):
            self.engine.spawning = None
            self.engine.state[-1].revert_to_playing_state()
        else:
            self.engine.menus = []
            self.engine.get_occupying(self.spawner.row, self.spawner.col).purchasing = True
            self.engine.get_occupying(self.spawner.row, self.spawner.col).pre_selected = False
            self.engine.transfer_to_spawning_state(self.spawning)

    def right_click(self):
        self.engine.spawning = None
        self.engine.state[-1].revert_to_playing_state()

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if self.menu_position_x < pos[0] + (self.menu_width // 3):
            for x in range(len(self.spawn_list)):
                a = x / len(self.spawn_list)
                b = a * self.menu_height
                c = b + self.menu_position_y
                d = (x + 1) / len(self.spawn_list)
                e = d * self.menu_height
                f = e + self.menu_position_y
                r = range(round(c), round(f))
                if pos[1] in r:
                    self.spawn_highlight_list[x] = True
                    for z in range(len(self.spawn_highlight_list)):
                        if z is not x:
                            self.spawn_highlight_list[z] = False
        else:
            for _ in self.spawn_highlight_list:
                _ = False

    def draw(self, win):
        self.menu.fill(Constant.MENU_COLOR)
        y_buffer = self.vertical_buffer_between_pieces
        for x in range(len(self.spawn_list)):
            a = x / len(self.spawn_list)
            b = a * self.menu_height
            if self.spawn_highlight_list[x]:
                self.menu.blit(self.square, (0, b))

        for p in self.spawn_list:
            piece_cost = Constant.PIECE_COSTS[p]

            if p == 'quarry_1':
                piece = 'quarry_1'
            else:
                piece = self.engine.turn + "_" + p

            # Log Cost
            if piece_cost['log'] != 0:
                if self.player.wood >= piece_cost['log']:
                    color = Constant.turn_to_color[self.engine.turn]
                else:
                    color = Constant.RED
                log_cost = self.font.render(str(piece_cost['log']), True, color)
                self.menu.blit(Constant.MENU_ICONS['log'], (self.log_x, y_buffer + Constant.SQ_SIZE // 4))
                self.menu.blit(log_cost,
                               ((self.log_x + (Constant.SQ_SIZE // 1.5)), (y_buffer + (Constant.SQ_SIZE // 6))))

            # Gold Cost
            if piece_cost['gold'] != 0:
                if self.player.gold >= piece_cost['gold']:
                    color = Constant.turn_to_color[self.engine.turn]
                else:
                    color = Constant.RED
                gold_cost = self.font.render(str(piece_cost['gold']), True, color)
                self.menu.blit(Constant.MENU_ICONS['gold_coin'], (self.gold_x, y_buffer + Constant.SQ_SIZE // 4))
                self.menu.blit(gold_cost,
                               ((self.gold_x + (Constant.SQ_SIZE // 1.5)), (y_buffer + (Constant.SQ_SIZE // 6))))

            # Stone Cost
            if piece_cost['stone'] != 0:
                if self.player.stone >= piece_cost['stone']:
                    color = Constant.turn_to_color[self.engine.turn]
                else:
                    color = Constant.RED
                stone_cost = self.font.render(str(piece_cost['stone']), True, color)
                self.menu.blit(Constant.MENU_ICONS['stone'], (self.stone_x, y_buffer + Constant.SQ_SIZE // 4))
                self.menu.blit(stone_cost,
                               ((self.stone_x + (Constant.SQ_SIZE // 1.5)), (y_buffer + (Constant.SQ_SIZE // 6))))

            # Menu
            if p == 'quarry_1':
                self.menu.blit(Constant.RESOURCES[p], (self.piece_x, y_buffer))
            else:
                self.menu.blit(self.pieces[self.engine.turn][piece], (self.piece_x, y_buffer))

            y_buffer += Constant.SPAWNING_MENU_HEIGHT_BUFFER

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y


class StableMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.STABLE_SPAWN_LIST
        self.spawner = spawner
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'stable'


class FortressMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.FORTRESS_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'fortress'


class BuilderMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.BUILDER_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'builder'


class CastleMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.CASTLE_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'castle'


class BarracksMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.BARRACKS_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'barracks'


class CircusMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.CIRCUS_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'circus'


class MonkMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.MONK_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'monk'


class TrapperMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.TRAPPER_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'trapper'


class KingMenu(Menu):
    def __init__(self, row, col, win, engine):
        super().__init__(win, engine)
        self.row = row
        self.col = col
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 6
        self.menu_width = Constant.SQ_SIZE + 2 * self.vertical_buffer_between_pieces
        self.menu_height = Constant.SQ_SIZE + 2 * self.vertical_buffer_between_pieces
        self.initial_menu_position = self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2, self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()

        self.piece = self.engine.turn + '_flag'
        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        self.square = pygame.Surface((self.menu_width, self.menu_height))
        self.high_light = False

    def draw(self, win):
        self.menu.fill(Constant.MENU_COLOR)
        # fill menu with art and logic
        if self.high_light:
            self.menu.blit(self.square, (0, 0))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        self.menu.blit(self.pieces[self.engine.turn][self.piece],
                       (self.vertical_buffer_between_pieces, self.vertical_buffer_between_pieces))
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y

    def right_click(self):
        self.engine.state[-1].revert_to_playing_state()

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > self.menu_position_x < self.menu_position_x + self.menu_width:
            if pos[1] > self.menu_position_y < self.menu_position_y + self.menu_height:
                self.high_light = True
        else:
            self.high_light = False

    def left_click(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > self.menu_position_x < self.menu_position_x + self.menu_width:
            if pos[1] > self.menu_position_y < self.menu_position_y + self.menu_height:
                self.engine.transfer_to_surrender_state()


class QueenMenu(Menu):
    def __init__(self, row, col, win, engine):
        super().__init__(win, engine)
        self.row = row
        self.col = col
        self.font_size = Constant.SQ_SIZE // 2
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.color = Constant.turn_to_color[self.engine.turn]
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 6
        self.menu_width = Constant.SQ_SIZE + 2 * self.vertical_buffer_between_pieces
        self.menu_height = Constant.SQ_SIZE + 2 * self.vertical_buffer_between_pieces
        self.initial_menu_position = self.col * Constant.SQ_SIZE + Constant.SQ_SIZE // 2, self.row * Constant.SQ_SIZE + Constant.SQ_SIZE // 2
        self.menu_boundary_buffer_y = self.menu_height + self.menu_boundary_buffer
        self.menu_boundary_buffer_x = self.menu_width + self.menu_boundary_buffer
        self.menu_position_x, self.menu_position_y = self.correct_menu_boundary()
        if self.engine.rituals_banned:
            self.image_string = self.engine.turn + '_decree_u'
        else:
            self.image_string = self.engine.turn + '_decree'
        self.IMAGE = Constant.IMAGES[self.image_string]
        self.cost = self.engine.get_decree_cost()
        self.cost_text_surface = self.font.render(str(self.cost), True, self.color)
        self.cost_display_x = Constant.SQ_SIZE // 2 + self.vertical_buffer_between_pieces
        self.cost_display_y = 3 * self.vertical_buffer_between_pieces
        self.gold_icon_display_x = self.vertical_buffer_between_pieces
        self.gold_icon_display_y = 4 * self.vertical_buffer_between_pieces
        self.GOLD_ICON = Constant.MENU_ICONS['gold_coin']
        self.menu = pygame.Surface((self.menu_width, self.menu_height))
        self.square = pygame.Surface((self.menu_width, self.menu_height))
        self.high_light = False

    def draw(self, win):
        self.menu.fill(Constant.MENU_COLOR)
        # fill menu with art and logic
        if self.high_light:
            self.menu.blit(self.square, (0, 0))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        self.menu.blit(self.GOLD_ICON, (self.gold_icon_display_x, self.gold_icon_display_y))
        self.menu.blit(self.cost_text_surface, (self.cost_display_x, self.cost_display_y))
        self.menu.blit(self.IMAGE, (0, 0))
        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))
        return self.menu_position_x, self.menu_position_y

    def right_click(self):
        self.engine.state[-1].revert_to_playing_state()

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > self.menu_position_x < self.menu_position_x + self.menu_width:
            if pos[1] > self.menu_position_y < self.menu_position_y + self.menu_height:
                self.high_light = True
        else:
            self.high_light = False

    def left_click(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > self.menu_position_x < self.menu_position_x + self.menu_width:
            if pos[1] > self.menu_position_y < self.menu_position_y + self.menu_height:
                if self.engine.can_decree(self.row, self.col):
                    self.engine.decree(self.row, self.col)


class PieceDescription:
    def __init__(self, win, engine, selected):
        self.win = win
        self.engine = engine
        self.selected = selected

        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h

        self.small_font_size = round(Constant.SQ_SIZE * .5)
        self.large_font_size = round(Constant.SQ_SIZE * 1.6)

        self.large_font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.large_font_size)
        self.small_font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.small_font_size)

        self.color = Constant.turn_to_color[self.engine.turn]
        self.player = self.engine.players[self.engine.turn]

        self.resources = {'wood': Constant.MENU_ICONS['log'], 'gold': Constant.MENU_ICONS['gold_coin'],
                          'stone': Constant.MENU_ICONS['stone']}
        self.icons = Constant.W_PIECES | Constant.W_BUILDINGS | Constant.B_PIECES | Constant.B_BUILDINGS | Constant.PRAYER_RITUALS | Constant.RESOURCES
        self.title_text = self.selected
        if self.title_text == 'prayer_stone':
            self.title_text = 'floating stone'
        elif self.title_text == 'quarry_1':
            self.title_text = 'quarry'
        self.title_text = self.title_text.replace('_', ' ')
        self.text_surf = self.large_font.render(self.title_text, True, self.color)

        self.title_text_width = self.text_surf.get_width()
        self.title_text_height = self.text_surf.get_height()

        self.text_display_x = self.window_width // 2 - self.title_text_width // 2
        self.text_display_y = round(self.window_height * 1 / 6) - self.title_text_height // 2

        self.menu_logo_display_y = self.text_display_y + self.title_text_height
        self.menu_logo = None

        self.description_text = Constant.DESCRIPTIONS[str(self)]
        self.description_text_surfs = []
        for line in self.description_text:
            text_surf = self.small_font.render(line, True, self.color)
            self.description_text_surfs.append(text_surf)
        self.cost_display_y = self.window_height // 2 - self.resources['wood'].get_height() // 2
        self.x_buffer_between_costs = round(Constant.SQ_SIZE * 1.5)

        self.description_text_width = self.description_text_surfs[0].get_width()
        self.description_text_height = self.description_text_surfs[0].get_height()
        self.description_text_y = round(self.window_height * 2 / 3)
        if self.selected == 'quarry_1':
            piece = 'quarry_1'
        else:
            piece = self.engine.turn + "_" + str(self)
        self.menu_logo = self.icons[piece]
        self.menu_logo_display_x = self.window_width // 2 - self.menu_logo.get_width() // 2
        self.cost = None
        self.type = None
        self.prayer_bar_end = Constant.IMAGES['prayer_bar_end']
        self.prayer_bar = Constant.IMAGES['prayer_bar']

        self.bar_end_width = self.prayer_bar_end.get_width()
        self.bar_width = self.prayer_bar.get_width()
        try:
            self.cost = Constant.PRAYER_COSTS[self.selected]['prayer']
            self.type = 'ritual'
        except KeyError:
            self.cost = Constant.PIECE_COSTS[self.selected]
            self.type = 'piece'

        self.cost_display_x = 0
        if self.type == 'piece':
            count = 0
            for cost in Constant.PIECE_COSTS[self.selected]:
                if Constant.PIECE_COSTS[self.selected][cost] != 0:
                    count += 1
            full_length = self.resources['wood'].get_width() * count + (self.x_buffer_between_costs // 2) * count
            self.cost_display_x = self.window_width // 2 - full_length // 2
        elif self.type == 'ritual':
            length_of_this_prayer_bar = self.full_length_of_prayer_bar(self.cost)
            self.cost_display_x = self.window_width // 2 - length_of_this_prayer_bar // 2

    def __repr__(self):
        return self.selected

    def draw(self):
        self.win.fill(Constant.MENU_COLOR)
        self.win.blit(self.text_surf, (self.text_display_x, self.text_display_y))
        self.win.blit(self.menu_logo, (self.menu_logo_display_x, self.menu_logo_display_y))
        y_buffer = self.description_text_y

        for line in self.description_text_surfs:
            description_text_x = self.window_width // 2 - line.get_width() // 2
            self.win.blit(line, (description_text_x, y_buffer))
            y_buffer += self.description_text_height

        if self.type == 'ritual':
            self.draw_ritual_cost()
        elif self.type == 'piece':
            self.draw_piece_cost()

    def draw_piece_cost(self):
        cost_x = self.cost_display_x
        for resource in self.cost:
            if self.cost[resource] != 0:

                if getattr(self.player, Constant.RESOURCE_KEY[resource]) >= self.cost[resource]:
                    color = self.color
                else:
                    color = Constant.RED
                text_surf = self.small_font.render(": " + str(self.cost[resource]), True, color)
                resource_position = (cost_x, self.cost_display_y)

                self.win.blit(self.resources[Constant.RESOURCE_KEY[resource]], resource_position)

                cost_text_position = (cost_x + self.resources['wood'].get_width(),
                                      self.cost_display_y - self.resources['wood'].get_height() // 3)

                self.win.blit(text_surf, cost_text_position)
                cost_x += self.x_buffer_between_costs

    def draw_ritual_cost(self):
        bar_end_edge = self.cost_display_x
        self.win.blit(self.prayer_bar, (bar_end_edge - self.bar_width, self.cost_display_y))
        for z in range(self.cost):
            new_edge = bar_end_edge + self.bar_end_width * (z)
            self.win.blit(self.prayer_bar_end, (new_edge, self.cost_display_y))

    def full_length_of_prayer_bar(self, cost):
        return self.bar_end_width * cost + self.bar_width

    def mouse_move(self):
        pass

    def right_click(self):
        pass

    def left_click(self):
        pass


class CostMenu:
    def __init__(self, win, engine, spawn_list):
        self.spawn_list = spawn_list
        self.win = win
        self.engine = engine

        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.large_font_size = round(Constant.SQ_SIZE * 1.6)
        self.large_font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.large_font_size)
        self.small_font_size = round(Constant.SQ_SIZE * .5)
        self.small_font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.small_font_size)
        self.color = Constant.turn_to_color[self.engine.turn]
        self.player = self.engine.players[self.engine.turn]
        self.pieces = {'w': Constant.W_PIECES | Constant.W_BUILDINGS,
                       'b': Constant.B_PIECES | Constant.B_BUILDINGS}
        self.MENUS = self.engine.COST_MENUS
        self.RESOURCES = {'wood': Constant.MENU_ICONS['log'], 'gold': Constant.MENU_ICONS['gold_coin'],
                          'stone': Constant.MENU_ICONS['stone']}

        self.text = str(self)
        if self.text == 'prayer_stone':
            self.text = 'floating stone'
        self.text_surf = self.large_font.render(self.text, True, self.color)
        self.text_width = self.text_surf.get_width()
        self.text_height = self.text_surf.get_height()

        self.text_display_x = self.window_width // 2 - self.text_width // 2
        self.text_display_y = round(self.window_height * 1 / 6) - self.text_height // 2

        self.x_buffer = round(Constant.SQ_SIZE * 7 / 8)
        total_width_of_pieces = (len(self.spawn_list) * self.x_buffer * 2) - self.x_buffer
        self.piece_display_x = (self.window_width - total_width_of_pieces) // 2
        self.piece_display_y = round(self.window_height * 1 / 2)

        self.menu_logo_display_x = self.window_width // 2 - Constant.SQ_SIZE // 2
        self.menu_logo_display_y = self.text_display_y + self.text_height
        self.menu_logo = None
        if str(self) != 'Costs':
            piece = self.engine.turn + "_" + str(self)
            self.menu_logo = self.pieces[self.engine.turn][piece]

        self.y_buffer_between_costs = Constant.SQ_SIZE
        self.x_buffer_between_costs = self.x_buffer // 3

        self.highlight_list = []
        for _ in self.spawn_list:
            self.highlight_list.append(False)

        total_height_of_cost_column = self.y_buffer_between_costs * 3 + self.x_buffer
        self.highlight_width = round(self.x_buffer * 1.5)
        self.highlight_dimensions = (self.highlight_width, total_height_of_cost_column)

        self.square = pygame.Surface(self.highlight_dimensions)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        piece_display_x = self.piece_display_x
        for i in range(len(self.spawn_list)):
            if pos[1] in range(self.piece_display_y, self.piece_display_y + self.highlight_dimensions[1]):
                highlight_edge = piece_display_x - ((self.highlight_width - self.x_buffer) // 2)
                if pos[0] in range(highlight_edge, highlight_edge + self.highlight_dimensions[0]):
                    self.highlight_list[i] = True
                else:
                    self.highlight_list[i] = False
            else:
                self.highlight_list[i] = False
            piece_display_x += self.x_buffer * 2

    def left_click(self):
        selected = self.piece_selected()
        if selected is not None:
            menu = PieceDescription(self.win, self.engine, selected)
            self.engine.menus.append(menu)

    def draw(self):
        self.win.fill(Constant.MENU_COLOR)
        self.win.blit(self.text_surf, (self.text_display_x, self.text_display_y))
        if self.menu_logo:
            self.win.blit(self.menu_logo, (self.menu_logo_display_x, self.menu_logo_display_y))
        piece_display_x = self.piece_display_x
        for i in range(len(self.spawn_list)):
            p = self.spawn_list[i]
            cost = Constant.PIECE_COSTS[p]
            if p == 'quarry_1':
                piece = 'quarry_1'
            else:
                piece = self.engine.turn + "_" + p
            if self.highlight_list[i]:
                self.win.blit(self.square,
                              (piece_display_x - ((self.highlight_width - self.x_buffer) // 2), self.piece_display_y))
            if piece == 'quarry_1':
                self.win.blit(Constant.RESOURCES[piece], (piece_display_x, self.piece_display_y))
            else:
                self.win.blit(self.pieces[self.engine.turn][piece], (piece_display_x, self.piece_display_y))
            log_y = self.piece_display_y + self.y_buffer_between_costs
            gold_y = log_y + self.y_buffer_between_costs
            stone_y = gold_y + self.y_buffer_between_costs
            Y_COORDS = {'wood': log_y, 'gold': gold_y, 'stone': stone_y}
            for resource in cost:
                if cost[resource] != 0:
                    if getattr(self.player, Constant.RESOURCE_KEY[resource]) >= cost[resource]:
                        color = self.color
                    else:
                        color = Constant.RED
                    text_surf = self.small_font.render(": " + str(cost[resource]), True, color)
                    resource_position = (piece_display_x - self.x_buffer_between_costs // 1.5,
                                         Y_COORDS[Constant.RESOURCE_KEY[resource]] + self.RESOURCES[
                                             Constant.RESOURCE_KEY[resource]].get_height() // 3)

                    self.win.blit(self.RESOURCES[Constant.RESOURCE_KEY[resource]], resource_position)

                    cost_text_position = (piece_display_x + self.x_buffer_between_costs,
                                          Y_COORDS[Constant.RESOURCE_KEY[resource]])

                    self.win.blit(text_surf, cost_text_position)

            piece_display_x += self.x_buffer * 2

    def piece_selected(self):
        pos = pygame.mouse.get_pos()
        piece_display_x = self.piece_display_x
        selected = None
        for i in range(len(self.spawn_list)):
            if pos[1] in range(self.piece_display_y, self.piece_display_y + self.highlight_dimensions[1]):
                highlight_edge = piece_display_x - ((self.highlight_width - self.x_buffer) // 2)
                if pos[0] in range(highlight_edge, highlight_edge + self.highlight_dimensions[0]):
                    selected = self.spawn_list[i]
            piece_display_x += self.x_buffer * 2
        return selected


class Master(CostMenu):
    def __init__(self, win, engine, spawn_list):
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return 'Costs'

    def left_click(self):
        piece_selected = self.piece_selected()
        if piece_selected is not None:
            menu = self.MENUS[piece_selected](self.win, self.engine)
            self.engine.menus.append(menu)


class BuilderCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.BUILDER_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return 'builder'


class CastleCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.CASTLE_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return 'castle'


class StableCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.STABLE_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return 'stable'


class CircusCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.CIRCUS_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return 'circus'


class MonkCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.MONK_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def left_click(self):
        piece_selected = self.piece_selected()
        if piece_selected is not None:
            menu = self.MENUS[piece_selected](self.win, self.engine)
            self.engine.menus.append(menu)

    def __repr__(self):
        return 'monk'


class FortressCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.FORTRESS_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return 'fortress'


class BarracksCosts(CostMenu):
    def __init__(self, win, engine):
        spawn_list = Constant.BARRACKS_SPAWN_LIST
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return 'barracks'


class RitualCosts(CostMenu):
    def __init__(self, win, engine, spawn_list):
        super().__init__(win, engine, spawn_list)
        self.rituals = Constant.PRAYER_RITUALS
        self.ritual_width = self.rituals['w_swap'].get_width()
        self.ritual_height = self.rituals['w_swap'].get_height()

        total_height_of_cost_column = self.y_buffer_between_costs * 3 + self.x_buffer
        self.highlight_width = self.ritual_width
        self.highlight_dimensions = (self.highlight_width, total_height_of_cost_column)

        self.square = pygame.Surface(self.highlight_dimensions)
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.prayer_bar_end = Constant.IMAGES['prayer_bar_end']
        self.prayer_bar = Constant.IMAGES['prayer_bar']

        self.bar_end_width = self.prayer_bar_end.get_width()
        self.bar_width = self.prayer_bar.get_width()

        self.bar_display_y = self.piece_display_y + self.y_buffer_between_costs * 2

    def full_length_of_prayer_bar(self, cost):
        return self.bar_end_width * cost + self.bar_width

    def draw(self):
        self.win.fill(Constant.MENU_COLOR)
        self.win.blit(self.text_surf, (self.text_display_x, self.text_display_y))
        if self.menu_logo:
            self.win.blit(self.menu_logo, (self.menu_logo_display_x, self.menu_logo_display_y))
        piece_display_x = self.piece_display_x
        for i in range(len(self.spawn_list)):
            p = self.spawn_list[i]
            cost = Constant.PRAYER_COSTS[p]
            ritual = self.engine.turn + "_" + p
            if self.highlight_list[i]:
                self.win.blit(self.square,
                              (piece_display_x, self.piece_display_y))
            self.win.blit(self.rituals[ritual], (piece_display_x, self.piece_display_y))

            length_of_this_prayer_bar = self.full_length_of_prayer_bar(cost['prayer'])

            bar_end_edge = piece_display_x + self.ritual_width // 2 - length_of_this_prayer_bar // 2

            self.win.blit(self.prayer_bar, (bar_end_edge - self.bar_width, self.bar_display_y))

            for z in range(cost['prayer']):
                new_edge = bar_end_edge + self.bar_end_width * (z)
                self.win.blit(self.prayer_bar_end, (new_edge, self.bar_display_y))

            piece_display_x += self.x_buffer * 2


class PrayerStoneCosts(RitualCosts):
    def __init__(self, win, engine):
        spawn_list = Constant.PRAYER_STONE_RITUALS
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return 'prayer_stone'


class MonolithCosts(RitualCosts):
    def __init__(self, win, engine):
        spawn_list = Constant.MONOLITH_RITUALS
        super().__init__(win, engine, spawn_list)

    def __repr__(self):
        return 'monolith'


class SideMenu:
    def __init__(self, win, engine):
        self.win = win
        self.engine = engine
        self.menu_height = Constant.SIDE_MENU_HEIGHT
        self.menu_width = Constant.SIDE_MENU_WIDTH
        self.menu = pygame.Surface((self.menu_width, self.menu_height))

    def mouse_move(self):
        pass

    def left_click(self):
        pass

    def right_click(self):
        pass


class Empty(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        self.win.blit(self.menu, (Constant.BOARD_WIDTH_SQ * Constant.SQ_SIZE, 0))


class StartMenu(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.color = Constant.INTRO_TEXT_COLOR
        self.font_size = round(Constant.SQ_SIZE / 1.3)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.ver_text = Constant.VERSION + " " + Constant.NUMBER
        self.version_text_surf = self.font.render(self.ver_text, True, self.color)
        self.version_text_display_x = self.menu_width // 2 - self.version_text_surf.get_width() // 2
        self.reset_map_image = Constant.IMAGES['resources_button']
        self.map_image_height = self.reset_map_image.get_height()
        self.map_image_width = self.reset_map_image.get_width()
        self.reset_map_display_x = self.menu_width // 2 - self.reset_map_image.get_width() // 2
        self.reset_map_display_y = self.menu_height - self.menu_height // 1 / 5
        self.choose_text = 'choose'
        self.choose_text_surf = self.font.render(self.choose_text, True, self.color)
        self.choose_text_display_x = self.menu_width // 2 - self.choose_text_surf.get_width() // 2
        self.choose_text_display_y = self.menu_height // 4
        self.your_text = 'your'
        self.your_text_display_y = self.choose_text_display_y + Constant.SQ_SIZE
        self.your_text_surf = self.font.render(self.your_text, True, self.color)

        self.faction_text_display_y = self.your_text_display_y + Constant.SQ_SIZE
        self.w_boat = Constant.IMAGES['w_boat']
        self.b_boat = Constant.IMAGES['b_boat']
        self.b_display_x = self.menu_width - round(self.menu_width ** 1 / 3)
        self.w_display_x = 0
        self.boat_display_y = Constant.SQ_SIZE * 6
        a = (self.menu_height * 1 / 5)
        self.r = round((self.menu_height - a))
        self.display_y = Constant.SQ_SIZE * 6

        self.w_piece_highlight = False
        self.b_piece_highlight = False
        self.randomize_resources_highlight = False
        self.scale = Constant.BOAT_PIECE_SCALE
        self.buffer = self.scale[0]
        self.square = pygame.Surface((round(self.scale[0] * .8), round(self.scale[1] * .8)))
        self.square_highlight_buffer = Constant.SQ_SIZE // 5
        self.w_square_display_x = 0
        self.b_square_display_x = self.b_display_x
        self.square_display_y = self.display_y + self.square_highlight_buffer + Constant.SQ_SIZE // 10
        self.resources_square = pygame.Surface((self.menu_width, round(a)))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        self.resources_square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.resources_square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        self.menu.blit(self.version_text_surf, (self.version_text_display_x, Constant.SQ_SIZE))
        self.menu.blit(self.choose_text_surf, (self.choose_text_display_x, self.choose_text_display_y))
        self.menu.blit(self.your_text_surf, (self.choose_text_display_x, self.your_text_display_y))
        self.faction_text = Constant.FACTION
        self.faction_text_surf = self.font.render(self.faction_text, True, self.color)
        self.menu.blit(self.faction_text_surf, (self.choose_text_display_x, self.faction_text_display_y))
        self.menu.blit(self.w_boat, (self.w_display_x, self.boat_display_y))
        self.menu.blit(self.b_boat, (self.b_display_x, self.boat_display_y))
        if self.b_piece_highlight:
            self.menu.blit(self.square, (self.b_square_display_x, self.square_display_y))
        elif self.w_piece_highlight:
            self.menu.blit(self.square, (self.w_square_display_x, self.square_display_y))
        elif self.randomize_resources_highlight:
            self.menu.blit(self.resources_square, (0, round(Constant.BOARD_HEIGHT_PX * 4 / 5)))
        self.menu.blit(self.reset_map_image,
                       (self.reset_map_display_x, Constant.BOARD_HEIGHT_PX - self.map_image_height))

        self.win.blit(self.menu, (Constant.BOARD_WIDTH_PX, 0))

    def left_click(self):
        starting = False
        pos = pygame.mouse.get_pos()
        if pos[0] > Constant.BOARD_WIDTH_PX:
            menu_mouse_x_position = pos[0] - Constant.BOARD_WIDTH_PX
            if pos[1] in range(self.display_y - self.buffer, self.display_y + self.buffer):
                if menu_mouse_x_position in range(self.w_display_x - self.buffer, self.w_display_x + self.buffer):
                    self.engine.turn = 'w'
                    starting = True
                elif menu_mouse_x_position in range(self.b_display_x - self.buffer, self.b_display_x + self.buffer):
                    self.engine.turn = 'b'
                    starting = True

                if starting:
                    if not Constant.DEBUG_START:
                        new_state = 'select starting pieces'
                        self.engine.set_state(new_state)
                    else:
                        new_state = 'debug'
                        self.engine.set_state(new_state)
            elif pos[1] in range(self.r, self.menu_height):
                self.engine.reset_board()
                self.engine.starting_resources()
                rand = random.randint(0, len(Constant.FACTION_NAMES) - 1)
                Constant.FACTION = Constant.FACTION_NAMES[rand]
                rand = random.randint(0, 2)
                if rand == 0:
                    Constant.INTRO_TEXT_COLOR = Constant.WHITE
                else:
                    Constant.INTRO_TEXT_COLOR = Constant.BLACK

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > Constant.BOARD_WIDTH_PX:
            menu_mouse_x_position = pos[0] - Constant.BOARD_WIDTH_PX
            if pos[1] in range(self.display_y - self.buffer, self.display_y + self.buffer):
                if menu_mouse_x_position in range(self.w_display_x - self.buffer, self.w_display_x + self.buffer):
                    self.w_piece_highlight = True

                else:
                    self.w_piece_highlight = False

                if menu_mouse_x_position in range(self.b_display_x - self.buffer, self.b_display_x + self.buffer):
                    self.b_piece_highlight = True

                else:
                    self.b_piece_highlight = False
            else:
                self.w_piece_highlight = False
                self.b_piece_highlight = False
            if pos[1] in range(self.r, self.menu_height):
                self.randomize_resources_highlight = True
            else:
                self.randomize_resources_highlight = False
        else:
            self.w_piece_highlight = False
            self.b_piece_highlight = False
            self.randomize_resources_highlight = False


class SurrenderMenu(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.fontSize = round(Constant.SQ_SIZE * 1.0)
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.fontSize)
        self.surrender_text = "Surrender?"
        self.yes_text = "yes"
        self.no_text = "no"
        self.surrender_text_surface = self.font.render(self.surrender_text, True,
                                                       Constant.turn_to_color[self.engine.turn])
        self.yes_button_address = self.engine.turn + "_" + self.yes_text
        self.no_button_address = self.engine.turn + "_" + self.no_text
        self.yes_button_image = Constant.IMAGES[self.yes_button_address]
        self.no_button_image = Constant.IMAGES[self.no_button_address]
        self.question_display_y = self.menu_height // 2 - self.surrender_text_surface.get_height() // 2
        self.question_display_x = self.menu_width // 2 - self.surrender_text_surface.get_width() // 2
        self.buffer = Constant.SQ_SIZE // 2
        self.answer_display_y = self.question_display_y + 4 * self.buffer
        self.answer_surface_height = self.yes_button_image.get_height()
        self.answer_surface_width = self.yes_button_image.get_width()
        self.yes_display_x = self.buffer
        self.no_display_x = self.menu_width - self.no_button_image.get_width() - self.buffer

        self.yes_highlight = False
        self.no_highlight = False
        self.square = pygame.Surface(Constant.YES_BUTTON_SCALE)
        self.yes_square_display_x = self.yes_display_x
        self.no_square_display_x = self.no_display_x
        self.square_display_y = self.answer_display_y

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > Constant.BOARD_WIDTH_PX:
            menu_x = pos[0] - Constant.BOARD_WIDTH_PX
            if pos[1] in range(self.answer_display_y, self.answer_display_y + self.answer_surface_height):
                if menu_x in range(self.yes_display_x, self.yes_display_x + self.answer_surface_width):
                    self.yes_highlight = True
                else:
                    self.yes_highlight = False

                if menu_x in range(self.no_display_x, self.no_display_x + self.answer_surface_width):
                    self.no_highlight = True
                else:
                    self.no_highlight = False
            else:
                self.yes_highlight = False
                self.no_highlight = False
        else:
            self.yes_highlight = False
            self.no_highlight = False

    def left_click(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > Constant.BOARD_WIDTH_PX:
            menu_x = pos[0] - Constant.BOARD_WIDTH_PX
            if pos[1] in range(self.answer_display_y,
                               self.answer_display_y + self.answer_surface_height):
                if menu_x in range(self.yes_display_x,
                                   self.yes_display_x + self.answer_surface_width):
                    self.engine.change_turn()
                    self.engine.surrendering = True
                elif menu_x in range(self.no_display_x, self.no_display_x + self.answer_surface_width):
                    self.engine.state[-1].revert_to_playing_state()

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        self.menu.blit(self.surrender_text_surface, (self.question_display_x, self.question_display_y))
        if self.yes_highlight:
            self.menu.blit(self.square, (self.yes_square_display_x, self.square_display_y))
        elif self.no_highlight:
            self.menu.blit(self.square, (self.no_square_display_x, self.square_display_y))
        self.menu.blit(self.yes_button_image, (self.yes_display_x, self.answer_display_y))
        self.menu.blit(self.no_button_image, (self.no_display_x, self.answer_display_y))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

        self.win.blit(self.menu, (Constant.BOARD_WIDTH_SQ * Constant.SQ_SIZE, 0))


class Hud(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.title_icon_width = Constant.IMAGES['w_game_name'].get_width()
        self.title_icon_height = Constant.IMAGES['w_game_name'].get_height()
        self.title_icon_display_x = self.menu_width // 2 - self.title_icon_width // 2
        self.title_icon_display_y = self.menu_height // 8 - self.title_icon_height // 2
        self.font_size = (round(Constant.SQ_SIZE * .8))
        self.font = pygame.font.Font(os.path.join("files/fonts", "font.ttf"), self.font_size)
        self.counter_icon_display_x = Constant.BOARD_WIDTH_PX + 10
        self.coin_icon_display_y = round(self.menu_height * (8 / 10))
        self.stone_icon_display_y = self.coin_icon_display_y + Constant.SQ_SIZE
        self.log_icon_display_y = self.coin_icon_display_y - Constant.SQ_SIZE
        self.prayer_icon_display_y = self.log_icon_display_y - Constant.SQ_SIZE
        self.action_icon_display_y = self.prayer_icon_display_y - Constant.SQ_SIZE
        self.units_icon_display_y = self.action_icon_display_y - Constant.SQ_SIZE
        self.turn_icon_display_y = self.units_icon_display_y - Constant.SQ_SIZE
        self.bar_end_width = Constant.IMAGES['prayer_bar_end'].get_width()
        self.bar_width = Constant.IMAGES['prayer_bar'].get_width()
        self.bar_height = Constant.IMAGES['prayer_bar'].get_height()
        self.prayer_bar_height = self.prayer_icon_display_y + round(
            Constant.MENU_ICONS['prayer'].get_height() // 2) - round(self.bar_height // 2)
        self.prayer_bar_edge = self.counter_icon_display_x + round(Constant.SQ_SIZE * 1.25)
        self.prayer_bar_end_edge = self.prayer_bar_edge + self.bar_width
        self.text_vertical_offset = self.font_size // 2 - Constant.MENU_ICONS['log'].get_height() // 2
        self.square = pygame.Surface((Constant.SIDE_MENU_WIDTH, round(Constant.SIDE_MENU_HEIGHT * .25)))
        self.title_bar_highlight = False
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        if self.title_bar_highlight:
            self.menu.blit(self.square, (0, 0))
        self.menu.blit(Constant.IMAGES[self.engine.turn + '_game_name'],
                       (self.title_icon_display_x, self.title_icon_display_y))
        self.win.blit(self.menu, (Constant.BOARD_WIDTH_PX, 0))

        # Gold Counter
        if not self.engine.players[self.engine.turn].gold == 0:
            self.win.blit(Constant.IMAGES['gold_coin'], (self.counter_icon_display_x, self.coin_icon_display_y))
            white_coin_text = self.font.render(" : " + str(self.engine.players[self.engine.turn].gold), True,
                                               Constant.turn_to_color[self.engine.turn])
            self.win.blit(white_coin_text, (
                (self.counter_icon_display_x + Constant.SQ_SIZE), self.coin_icon_display_y - self.text_vertical_offset))

        # Wood Counter
        if not self.engine.players[self.engine.turn].wood == 0:
            self.win.blit(Constant.IMAGES['log'], (self.counter_icon_display_x, self.log_icon_display_y))
            white_log_text = self.font.render(" : " + str(self.engine.players[self.engine.turn].wood), True,
                                              Constant.turn_to_color[self.engine.turn])
            self.win.blit(white_log_text, (
                (self.counter_icon_display_x + Constant.SQ_SIZE), self.log_icon_display_y - self.text_vertical_offset))

        # Stone Counter
        if not self.engine.players[self.engine.turn].stone == 0:
            self.win.blit(Constant.IMAGES['stone'], (self.counter_icon_display_x, self.stone_icon_display_y))
            white_log_text = self.font.render(" : " + str(self.engine.players[self.engine.turn].stone), True,
                                              Constant.turn_to_color[self.engine.turn])
            self.win.blit(white_log_text, (
                (self.counter_icon_display_x + Constant.SQ_SIZE),
                self.stone_icon_display_y - self.text_vertical_offset))

        # Prayer Counter
        if not self.engine.players[self.engine.turn].prayer == 0:
            self.win.blit(Constant.MENU_ICONS['prayer'],
                          (self.counter_icon_display_x, self.prayer_icon_display_y - self.text_vertical_offset))
            self.win.blit(Constant.IMAGES['prayer_bar'], (self.prayer_bar_edge, self.prayer_bar_height))
            for x in range(self.engine.players[self.engine.turn].prayer):
                new_edge = self.prayer_bar_end_edge + self.bar_end_width * (x)
                self.win.blit(Constant.IMAGES['prayer_bar_end'], (new_edge, self.prayer_bar_height))

        # Actions Remaining Counter
        self.win.blit(Constant.IMAGES['action'], (self.counter_icon_display_x, self.action_icon_display_y))
        actions_remaining_text = self.font.render(
            " : " + str(self.engine.players[self.engine.turn].get_actions_remaining()),
            True,
            Constant.turn_to_color[self.engine.turn])
        self.win.blit(actions_remaining_text,
                      ((self.counter_icon_display_x + Constant.SQ_SIZE),
                       self.action_icon_display_y - self.text_vertical_offset))

        # Unit Limit Counter
        self.win.blit(Constant.IMAGES['units'], (self.counter_icon_display_x, self.units_icon_display_y))
        t = str(self.engine.players[self.engine.turn].get_current_population()) + "/" + str(
            self.engine.players[self.engine.turn].get_piece_limit())
        units_text = self.font.render(" : " + t, True, Constant.turn_to_color[self.engine.turn])
        self.win.blit(units_text, (
            (self.counter_icon_display_x + Constant.SQ_SIZE), self.units_icon_display_y - self.text_vertical_offset))

        # Turn Counter
        self.win.blit(Constant.IMAGES['hour_glass'], (self.counter_icon_display_x, self.turn_icon_display_y))
        turn_number_text = " : " + str(self.engine.turn_count_display)
        text_surf = self.font.render(turn_number_text, True, Constant.turn_to_color[self.engine.turn])
        self.win.blit(text_surf, (
            self.counter_icon_display_x + Constant.SQ_SIZE, self.turn_icon_display_y - self.text_vertical_offset))

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > Constant.BOARD_WIDTH_PX:
            if 0 < pos[1] < Constant.BOARD_HEIGHT_PX * .25:
                self.title_bar_highlight = True
            else:
                self.title_bar_highlight = False
        else:
            self.title_bar_highlight = False

    def left_click(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > Constant.BOARD_WIDTH_PX:
            if 0 < pos[1] < Constant.BOARD_HEIGHT_PX * .25:
                self.engine.transfer_to_piece_cost_screen()
