import os
import random

import pygame

import Constant


class Menu:
    def __init__(self, win, engine):
        self.win = win
        self.engine = engine
        self.pieces = {'w': Constant.W_PIECES | Constant.W_BUILDINGS, 'b': Constant.B_PIECES | Constant.B_BUILDINGS}
        self.menu_boundary_buffer = Constant.SQ_SIZE

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
        self.menu_width = self.ritual_width + self.vertical_buffer_between_pieces +  self.bar_end_width * 16 + self.bar_width
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
        self.engine.ritual = None
        self.casting = self.ritual_clicked()
        if self.casting is not None:
            if self.engine.is_legal_ritual(self.casting):
                self.engine.menus = []
                self.engine.ritual = self.casting
            else:
                self.engine.state[-1].reset_state()

    def right_click(self):
        self.engine.spawning = None
        self.engine.state[-1].reset_state()

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
            self.menu.blit(self.rituals[self.engine.turn+"_"+ritual], (0, y_buffer_piece))
            y_buffer_piece += self.ritual_height

        self.win.blit(self.menu, (self.menu_position_x, self.menu_position_y))

class ResourceMenu(Menu):

    def __init__(self, row, col, win, engine):
        self.row = row
        self.col = col
        rand = str(random.randint(1, 4))
        self.spawn_list = ['gold_tile_1', 'quarry_1', 'tree_tile_'+rand, 'sunken_quarry_1']
        super().__init__(win, engine)
        self.horizontal_buffer = Constant.SQ_SIZE
        self.vertical_buffer_between_pieces = Constant.SQ_SIZE // 4
        self.font_size = round(Constant.SQ_SIZE / 2)
        self.font = pygame.font.Font(os.path.join("resources/fonts", "font.ttf"), self.font_size)
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
            self.engine.state[-1].reset_state()

    def right_click(self):
        self.engine.ritual_summon_resource = None
        self.engine.state[-1].reset_state()

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
        self.font = pygame.font.Font(os.path.join("resources/fonts", "font.ttf"), self.font_size)
        self.test_text = self.font.render("10", True, Constant.RED)
        self.menu_width = Constant.SQ_SIZE + (
                    3 * self.horizontal_buffer_between_costs + self.test_text.get_width())
        self.menu_height = len(spawn_list) * Constant.SPAWNING_MENU_HEIGHT_BUFFER + (self.vertical_buffer_between_pieces)
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
        self.square = pygame.Surface((self.menu_width, round(1/len(self.spawn_list) * self.menu_height)))
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
        if self.spawning is not None:
            if self.engine.is_legal_spawn(self.spawning):
                self.engine.menus = []
                self.engine.spawning = self.spawning
                self.engine.get_occupying(self.spawner.row, self.spawner.col).purchasing = True
                self.engine.get_occupying(self.spawner.row, self.spawner.col).pre_selected = False
            else:
                self.engine.spawning = None
                self.engine.state[-1].reset_state()

    def right_click(self):
        self.engine.spawning = None
        self.engine.state[-1].reset_state()

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

        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
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
        spawn_list = Constant.STABLE_MENU_SPAWN_LIST
        self.spawner = spawner
        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'stable'


class FortressMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.FORTRESS_MENU_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'fortress'


class BuilderMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.BUILDER_MENU_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'builder'


class CastleMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.CASTLE_MENU_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'castle'


class BarracksMenu(SpawningMenu):
    def __init__(self, row, col, win, engine, spawner):
        spawn_list = Constant.BARRACKS_MENU_SPAWN_LIST
        self.spawner = spawner

        super().__init__(row, col, win, engine, spawn_list, spawner)

    def __repr__(self):
        return 'barracks'


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
        self.engine.state[-1].reset_state()

    def mouse_move(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > self.menu_position_x < self.menu_position_x+self.menu_width:
            if pos[1] > self.menu_position_y < self.menu_position_y+self.menu_height:
                self.high_light = True
        else:
            self.high_light = False


    def left_click(self):
        pos = pygame.mouse.get_pos()
        if pos[0] > self.menu_position_x < self.menu_position_x + self.menu_width:
            if pos[1] > self.menu_position_y < self.menu_position_y + self.menu_height:
                self.engine.surrendering = True

#
#   SIDE MENUS
#
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
        self.font = pygame.font.Font(os.path.join("resources/fonts", "font.ttf"), self.font_size)
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
        self.b_display_x = self.menu_width - (self.menu_width ** 1 / 3)
        self.w_display_x = self.menu_width ** 1 / 3 - self.w_boat.get_width()
        self.boat_display_y = Constant.SQ_SIZE * 6

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        self.menu.blit(self.version_text_surf, (self.version_text_display_x, Constant.SQ_SIZE))
        self.menu.blit(self.reset_map_image, (self.reset_map_display_x, Constant.BOARD_HEIGHT_PX - self.map_image_height))
        self.menu.blit(self.choose_text_surf, (self.choose_text_display_x, self.choose_text_display_y))
        self.menu.blit(self.your_text_surf, (self.choose_text_display_x, self.your_text_display_y))
        self.faction_text = Constant.FACTION
        self.faction_text_surf = self.font.render(self.faction_text, True, self.color)
        self.menu.blit(self.faction_text_surf, (self.choose_text_display_x, self.faction_text_display_y))
        self.menu.blit(self.w_boat, (self.w_display_x, self.boat_display_y))
        self.menu.blit(self.b_boat, (self.b_display_x, self.boat_display_y))
        self.win.blit(self.menu, (Constant.BOARD_WIDTH_SQ * Constant.SQ_SIZE, 0))


class SurrenderMenu(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.fontSize = round(Constant.SQ_SIZE * 1.0)
        self.font = pygame.font.Font(os.path.join("resources/fonts", "font.ttf"), self.fontSize)
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
                    self.engine.state[-1].reset_state()

    def draw(self):

        self.menu.fill(Constant.MENU_COLOR)

        self.menu.blit(self.surrender_text_surface, (self.question_display_x, self.question_display_y))
        self.menu.blit(self.yes_button_image, (self.yes_display_x, self.answer_display_y))
        self.menu.blit(self.no_button_image, (self.no_display_x, self.answer_display_y))
        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        if self.yes_highlight:
            self.menu.blit(self.square, (self.yes_square_display_x, self.square_display_y))
        elif self.no_highlight:
            self.menu.blit(self.square, (self.no_square_display_x, self.square_display_y))
        self.win.blit(self.menu, (Constant.BOARD_WIDTH_SQ * Constant.SQ_SIZE, 0))


class Hud(SideMenu):
    def __init__(self, win, engine):
        super().__init__(win, engine)
        self.title_icon_width = Constant.IMAGES['w_game_name'].get_width()
        self.title_icon_height = Constant.IMAGES['w_game_name'].get_height()
        self.title_icon_display_x = self.menu_width // 2 - self.title_icon_width // 2
        self.title_icon_display_y = self.menu_height // 8 - self.title_icon_height // 2
        self.font_size = (round(Constant.SQ_SIZE * .8))
        self.font = pygame.font.Font(os.path.join("resources/fonts", "font.ttf"), self.font_size)
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

    def draw(self):
        self.menu.fill(Constant.MENU_COLOR)
        self.menu.blit(Constant.IMAGES[self.engine.turn + '_game_name'],
                       (self.title_icon_display_x, self.title_icon_display_y))

        self.win.blit(self.menu, (Constant.BOARD_WIDTH_PX, 0))
        if self.title_bar_highlight:
            self.win.blit(self.square, (Constant.BOARD_WIDTH_PX, 0))

        self.square.set_alpha(Constant.HIGHLIGHT_ALPHA)
        self.square.fill(Constant.UNUSED_PIECE_HIGHLIGHT_COLOR)
        # Gold Counter
        if not self.engine.players[self.engine.turn].gold == 0:
            self.win.blit(Constant.IMAGES['gold_coin'], (self.counter_icon_display_x, self.coin_icon_display_y))
            white_coin_text = self.font.render(" : " + str(self.engine.players[self.engine.turn].gold), True,
                                               Constant.turn_to_color[self.engine.turn])
            self.win.blit(white_coin_text, ((self.counter_icon_display_x + Constant.SQ_SIZE), self.coin_icon_display_y-self.text_vertical_offset))

        # Wood Counter
        if not self.engine.players[self.engine.turn].wood == 0:
            self.win.blit(Constant.IMAGES['log'], (self.counter_icon_display_x, self.log_icon_display_y))
            white_log_text = self.font.render(" : " + str(self.engine.players[self.engine.turn].wood), True,
                                              Constant.turn_to_color[self.engine.turn])
            self.win.blit(white_log_text, ((self.counter_icon_display_x + Constant.SQ_SIZE), self.log_icon_display_y-self.text_vertical_offset))

        # Stone Counter
        if not self.engine.players[self.engine.turn].stone == 0:
            self.win.blit(Constant.IMAGES['stone'], (self.counter_icon_display_x, self.stone_icon_display_y))
            white_log_text = self.font.render(" : " + str(self.engine.players[self.engine.turn].stone), True,
                                              Constant.turn_to_color[self.engine.turn])
            self.win.blit(white_log_text, ((self.counter_icon_display_x + Constant.SQ_SIZE), self.stone_icon_display_y-self.text_vertical_offset))

        # Prayer Counter
        if not self.engine.players[self.engine.turn].prayer == 0:
            self.win.blit(Constant.MENU_ICONS['prayer'], (self.counter_icon_display_x, self.prayer_icon_display_y-self.text_vertical_offset))
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
                      ((self.counter_icon_display_x + Constant.SQ_SIZE), self.action_icon_display_y-self.text_vertical_offset))

        # Unit Limit Counter
        self.win.blit(Constant.IMAGES['units'], (self.counter_icon_display_x, self.units_icon_display_y))
        t = str(self.engine.players[self.engine.turn].get_current_population()) + "/" + str(
            self.engine.players[self.engine.turn].get_piece_limit())
        units_text = self.font.render(" : " + t, True, Constant.turn_to_color[self.engine.turn])
        self.win.blit(units_text, ((self.counter_icon_display_x + Constant.SQ_SIZE), self.units_icon_display_y-self.text_vertical_offset))

        # Turn Counter
        self.win.blit(Constant.IMAGES['hour_glass'], (self.counter_icon_display_x, self.turn_icon_display_y))
        turn_number_text = " : " + str(self.engine.turn_count_display)
        text_surf = self.font.render(turn_number_text, True, Constant.turn_to_color[self.engine.turn])
        self.win.blit(text_surf, (self.counter_icon_display_x + Constant.SQ_SIZE, self.turn_icon_display_y-self.text_vertical_offset))

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
                self.engine.piece_cost_screen = True

