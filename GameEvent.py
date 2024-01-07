from Unit import *
from Resource import *
from Tile import Tile


class GameEvent:
    def __init__(self, engine, acting_tile=None, action_tile=None):
        self.engine = engine
        self.acting_tile = acting_tile
        self.action_tile = action_tile

    def action_tile_has_effective_trap(self, acting_tile, action_tile):
        color = acting_tile.get_occupying().color
        trap = action_tile.trap
        is_protected = False
        if trap is not None:
            if trap.color is not color:
                if action_tile.is_protected():
                    if action_tile.protected_by == color:
                        is_protected = True
            if not is_protected:
                return trap

    def complete(self):
        self.engine.reset_selected()

    def undo(self):
        pass
        self.engine.reset_selected()


class StartSpawn(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.spawn = self.engine.spawning
        self.dest = self.action_tile.get_position()
        self.previously_selected = None
        self.turn = self.engine.get_turn()
        if acting_tile:
            self.previously_selected = self.acting_tile.get_occupying()
        self.spawn_count = self.engine.spawn_count
        self.final_spawn = self.engine.final_spawn
        self.spawn_list = self.engine.spawn_list
        self.state = self.engine.state[-1]

    def __repr__(self):
        return 'start spawn'

    def complete(self):
        super().complete()
        self.engine.spawn(self.dest[0], self.dest[1], self.spawn)
        kind = self.engine.get_occupying(self.dest[0], self.dest[1]).get_unit_kind()
        self.engine.sounds.play('spawn_' + kind)
        self.engine.spawnSuccess = True
        self.engine.spawning = None

    def undo(self):
        super().undo()
        kind = self.engine.get_occupying(self.dest[0], self.dest[1]).get_unit_kind()
        self.engine.sounds.play('spawn_' + kind)
        self.engine.delete_piece(self.dest[0], self.dest[1])
        self.engine.spawn_count = self.spawn_count
        self.engine.turn = self.turn
        self.engine.final_spawn = self.final_spawn
        self.engine.spawn_list = self.spawn_list
        self.engine.spawning = self.engine.spawn_list[self.engine.spawn_count]
        self.engine.reset_unused_piece_highlight()
        if self.previously_selected:
            self.previously_selected.purchasing = True
        self.engine.set_state(self.state)
        self.engine.update_spawn_squares()
        self.engine.players[self.engine.turn].reset_piece_limit()


class Steal(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)

        self.stolen_from = self.action_tile.get_occupying()
        self.thief = self.acting_tile.get_occupying()
        self.resource_stolen = self.engine.stealing[0]
        self.amount = self.engine.stealing[1]

    def __repr__(self):
        return 'steal'

    def complete(self):
        super().complete()
        self.engine.sounds.play('capture')
        self.thief.actions_remaining -= 1
        self.engine.players[self.engine.turn].steal(self.resource_stolen, self.amount)
        self.engine.players[Constant.TURNS[self.engine.turn]].invert_steal(self.resource_stolen, self.amount)
        if Constant.STEALING_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.thief.actions_remaining += 1
        self.engine.sounds.play('capture')
        self.engine.players[self.engine.turn].invert_steal(self.resource_stolen, self.amount)
        self.engine.players[Constant.TURNS[self.engine.turn]].steal(self.resource_stolen, self.amount)
        if Constant.STEALING_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Mine(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.miner = self.acting_tile.get_occupying()
        self.mined = self.action_tile.get_resource()
        self.additional_mining = 0
        self.piece_removed = None
        self.harvest_yield = None
        self.player = self.engine.players[self.engine.turn]
        self.sprite_id = self.mined.sprite_id
        self.sprite_offset = self.mined.sprite_offset

    def __repr__(self):
        return 'mine'

    def complete(self):
        super().complete()
        self.harvest_yield = self.mined.harvest(str(self.miner))
        self.player.mine(str(self.mined), self.harvest_yield)
        self.miner.actions_remaining -= 1
        kind = Constant.RESOURCE_KEY[str(self.mined)]
        self.engine.sounds.play('mine_' + kind)

        if self.mined.remaining == 0:
            if isinstance(self.mined, Quarry):
                self.engine.create_resource(self.mined.row, self.mined.col,
                                            SunkenQuarry(self.mined.row, self.mined.col))
                if self.engine.get_occupying(self.mined.row, self.mined.col):
                    self.piece_removed = self.engine.get_occupying(self.mined.row, self.mined.col)
                    self.engine.delete_piece(self.mined.row, self.mined.col)
            elif isinstance(self.mined, SunkenQuarry):
                self.engine.create_resource(self.mined.row, self.mined.col,
                                            DepletedQuarry(self.mined.row, self.mined.col))
            else:
                self.engine.delete_resource(self.mined.row, self.mined.col)
        if Constant.MINING_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.miner.actions_remaining += 1
        row = self.mined.row
        col = self.mined.col
        self.mined.unharvest(self.harvest_yield)
        self.engine.players[self.engine.turn].un_mine(str(self.mined), self.harvest_yield)
        kind = Constant.RESOURCE_KEY[str(self.mined)]
        self.engine.sounds.play('mine_' + kind)
        self.engine.create_resource(row, col, self.mined)
        if self.piece_removed:
            self.engine.create_piece(self.mined.row, self.mined.col, self.piece_removed)
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        if Constant.MINING_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Pray(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.praying_piece = self.acting_tile.get_occupying()
        self.prayed_on = self.action_tile.get_occupying()
        self.additional_prayer = 0
        if str(self.praying_piece) == 'monk':
            self.additional_prayer = Constant.ADDITIONAL_PRAYER_FROM_MONK

    def __repr__(self):
        return 'pray'

    def complete(self):
        super().complete()
        self.engine.sounds.play('pray')
        self.praying_piece.actions_remaining -= 1

        self.engine.players[self.engine.turn].pray(self.prayed_on, self.additional_prayer)
        if Constant.PRAYING_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        praying_piece = self.engine.get_occupying(self.praying_piece.row, self.praying_piece.col)
        praying_piece.actions_remaining += 1
        self.engine.sounds.play('pray')
        self.engine.players[self.engine.turn].un_pray(self.prayed_on, self.additional_prayer)
        if Constant.PRAYING_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Persuade(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.persuader = self.acting_tile.get_occupying()
        self.persuaded = self.action_tile.get_occupying()
        self.persuaded_actions = self.persuaded.actions_remaining
        self.persuaded_color = self.persuaded.color

    def __repr__(self):
        return 'persuade'

    def complete(self):
        super().complete()
        self.persuader.actions_remaining -= 1
        self.persuaded.actions_remaining -= 1
        self.engine.players[self.persuaded.color].pieces.remove(self.persuaded)
        self.engine.players[self.persuader.color].pieces.append(self.persuaded)
        self.persuaded.color = self.persuader.color
        self.engine.reset_selected()
        self.engine.reset_unused_piece_highlight()
        self.engine.intercept_pieces()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        if Constant.PERSUADE_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.persuader.actions_remaining += 1
        self.persuaded.actions_remaining = self.persuaded_actions
        self.engine.players[self.persuader.color].pieces.remove(self.persuaded)
        self.engine.players[self.persuaded_color].pieces.append(self.persuaded)
        self.persuaded.color = self.persuaded_color
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            if piece is not self.persuaded:
                piece.unused_piece_highlight = True
        if Constant.PERSUADE_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()


class Decree(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.piece = self.acting_tile.get_occupying()
        self.player = self.engine.players[self.engine.turn]
        self.cost = self.engine.get_decree_cost()
        self.disabled_monoliths = None

    def complete(self):
        super().complete()
        self.piece.actions_remaining -= 1
        self.player.gold -= self.cost
        self.engine.decrees += 1
        self.engine.rituals_banned = not self.engine.rituals_banned
        self.engine.close_menus()
        self.engine.reset_selected()
        if self.engine.rituals_banned:
            self.disabled_monoliths = self.engine.disable_monoliths()
        else:
            self.engine.enable_monoliths()
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.player.do_action()

    def undo(self):
        super().undo()
        self.piece.actions_remaining += 1
        self.player.gold += self.cost
        self.engine.decrees -= 1
        self.engine.rituals_banned = not self.engine.rituals_banned
        self.engine.reset_selected()
        if self.engine.rituals_banned:
            self.disabled_monoliths = self.engine.disable_monoliths()
        else:
            self.engine.enable_monoliths()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


class ChangeTurn(GameEvent):
    def __init__(self, engine):
        super().__init__(engine)
        self.engine = self.engine
        self.prev = self.engine.update_previously_selected()
        self.spawn_success = self.engine.spawn_success
        self.menus = self.engine.menus
        self.state = self.engine.state[-1]
        self.used_pieces = self.engine.count_used_pieces()
        self.spawning = self.engine.spawning
        self.player_actions_remaining = self.engine.players[self.engine.turn].get_actions_remaining()
        self.player_piece_limit = self.engine.players[self.engine.turn].get_piece_limit()
        self.player_prayer = self.engine.players[self.engine.turn].get_prayer()
        self.used_and_intercepted_pieces = self.engine.used_and_intercepted_pieces
        self.protected_tiles = self.engine.protected_tiles[:]

    def complete(self):

        super().complete()
        self.engine.sounds.play('change_turn')
        self.engine.reset_selected()
        self.engine.reset_piece_actions_remaining()
        self.engine.spawn_success = False
        self.engine.pieces_checking = []
        self.engine.pins = []
        self.engine.check = False
        self.engine.menus = []
        self.engine.turn = Constant.TURNS[self.engine.turn]
        self.engine.turn_count_display += .5
        self.engine.turn_count_actual += 1
        self.engine.used_and_intercepted_pieces = []
        self.engine.players[self.engine.turn].reset_prayer()
        self.engine.reset_player_actions_remaining(self.engine.turn)
        self.engine.update_additional_actions()
        self.engine.reset_piece_limit(self.engine.turn)
        self.engine.update_piece_limit()
        self.engine.intercept_pieces()
        self.engine.reset_unused_piece_highlight()
        if self.engine.rituals_banned:
            self.engine.disable_monoliths()
        self.engine.tick_protected_tiles(self.engine.protected_tiles)
        if Constant.DEBUG_RITUALS:
            self.engine.monolith_rituals.append(Constant.MONOLITH_RITUALS)
            self.engine.prayer_stone_rituals.append(Constant.PRAYER_STONE_RITUALS)
            self.engine.magician_rituals.append(Constant.MAGICIAN_RITUALS)

        else:
            if self.engine.turn_count_actual == len(self.engine.monolith_rituals) - 1:
                self.engine.monolith_rituals.append(self.engine.generate_available_rituals(Constant.MONOLITH_RITUALS,
                                                                                           Constant.MAX_MONOLITH_RITUALS_PER_TURN))
            if self.engine.turn_count_actual == len(self.engine.prayer_stone_rituals) - 1:
                self.engine.prayer_stone_rituals.append(
                    self.engine.generate_available_rituals(Constant.PRAYER_STONE_RITUALS,
                                                           Constant.MAX_PRAYER_STONE_RITUALS_PER_TURN))
            if self.engine.turn_count_actual == len(self.engine.magician_rituals) - 1:
                self.engine.magician_rituals.append(self.engine.generate_available_rituals(Constant.MAGICIAN_RITUALS,
                                                                                           Constant.MAX_MAGICIAN_RITUALS_PER_TURN))

        if self.engine.turn_count_actual == len(self.engine.trade_conversions) - 1:
            self.engine.trade_conversions.append(self.engine.trade_handler.get_conversions())
        if self.engine.turn_count_actual == len(self.engine.piece_stealing_offsets) - 1:
            self.engine.piece_stealing_offsets.append(
                self.engine.generate_stealing_offsets(Constant.STEALING_KEY['piece']))
        if self.engine.turn_count_actual == len(self.engine.building_stealing_offsets) - 1:
            self.engine.building_stealing_offsets.append(
                self.engine.generate_stealing_offsets(Constant.STEALING_KEY['building']))
        if self.engine.turn_count_actual == len(self.engine.trader_stealing_offsets) - 1:
            self.engine.trader_stealing_offsets.append(
                self.engine.generate_stealing_offsets(Constant.STEALING_KEY['trader']))
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
    def undo(self):
        self.engine.sounds.play('change_turn')
        self.engine.turn = Constant.TURNS[self.engine.turn]
        self.engine.turn_count_display -= .5
        self.engine.turn_count_actual -= 1
        self.engine.menus = self.menus
        self.engine.spawn_success = self.spawn_success
        self.engine.spawning = self.spawning
        self.engine.set_state(str(self.state))
        self.engine.used_and_intercepted_pieces = self.used_and_intercepted_pieces
        for used_piece in self.used_pieces:
            used_piece.actions_remaining = 0
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        if self.engine.rituals_banned:
            self.engine.disable_monoliths()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].set_actions_remaining(self.player_actions_remaining)
        self.engine.players[self.engine.turn].set_piece_limit(self.player_piece_limit)
        self.engine.players[self.engine.turn].set_prayer(self.player_prayer)
        self.engine.protected_tiles = self.protected_tiles
        self.engine.untick_protected_tiles(self.protected_tiles)
        for tile in self.protected_tiles:
            self.engine.board[tile.row][tile.col] = tile


class SpawnResource(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.spawn = self.engine.spawning
        self.dest = self.action_tile.get_position()
        self.spawner = self.acting_tile.get_occupying()
        self.piece_cost = Constant.PIECE_COSTS[self.engine.spawning]

    def __repr__(self):
        return 'spawn resource'

    def complete(self):
        super().complete()
        resource = self.engine.RESOURCES[self.spawn](self.dest[0], self.dest[1])
        self.engine.create_resource(self.dest[0], self.dest[1], resource)
        if Constant.QUARRY_COSTS_RESOURCE:
            self.engine.players[self.engine.turn].purchase(self.piece_cost)
        self.engine.sounds.play('mine_stone')
        self.spawner.actions_remaining -= 1
        self.engine.spawn_success = True
        self.engine.menus = []
        self.engine.reset_selected()
        if Constant.QUARRY_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.spawner.actions_remaining += 1
        self.engine.sounds.play('mine_stone')
        if Constant.QUARRY_COSTS_RESOURCE:
            self.engine.players[self.engine.turn].un_purchase(self.piece_cost)
        self.engine.delete_resource(self.dest[0], self.dest[1])
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        if Constant.QUARRY_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class PortalSpawn(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.spawn = self.engine.spawning
        self.dest = self.action_tile.get_position()
        self.portal_end = self.action_tile.connected_portal.get_position()

        self.trap = self.engine.board[self.portal_end[0]][self.portal_end[1]].trap
        self.trapped_tile = self.engine.board[self.portal_end[0]][self.portal_end[1]]
        self.is_protected = False
        if self.trapped_tile.is_protected():
            if self.trapped_tile.protected_by == self.color:
                self.is_protected = True
        if self.trap is not None and self.trap.color is self.color or self.is_protected:
            self.trap = None
        self.deleted_piece = None
        self.spawner = self.acting_tile.get_occupying()
        self.additional_piece_limit = 0
        self.additional_actions = 0
        self.piece_cost = Constant.PIECE_COSTS[self.engine.spawning]

    def __repr__(self):
        return 'spawn'

    def complete(self):
        super().complete()
        self.engine.spawn(self.dest[0], self.dest[1], self.spawn)
        self.spawner.actions_remaining -= 1
        self.engine.spawn_success = True
        self.engine.menus = []
        self.engine.reset_selected()
        self.engine.players[self.engine.turn].do_action()
        self.engine.players[self.engine.turn].purchase(self.piece_cost)
        if Constant.ACTIONS_UPDATE_ON_SPAWN:
            self.additional_actions = self.engine.get_occupying(self.dest[0], self.dest[1]).get_additional_actions()
            self.engine.players[self.engine.turn].add_additional_actions(self.additional_actions)
        self.additional_piece_limit = self.engine.get_occupying(self.dest[0], self.dest[1]).get_additional_piece_limit()
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().get_unit_kind()
        self.engine.sounds.play('spawn_' + kind)
        self.engine.intercept_pieces()
        self.engine.players[self.engine.turn].add_additional_piece_limit(self.additional_piece_limit)
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.swap(self.dest[0], self.dest[1], self.portal_end[0], self.portal_end[1])

        if self.trap:
            self.deleted_piece = self.engine.get_occupying(self.portal_end[0], self.portal_end[1])
            self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
            self.engine.untrap(self.portal_end[0], self.portal_end[1])

        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        super().undo()
        self.spawner.actions_remaining += 1

        if self.deleted_piece:
            self.engine.create_piece(self.portal_end[0], self.portal_end[1], self.deleted_piece)
            self.engine.set_trap(self.portal_end[0], self.portal_end[1], self.trap)

        self.engine.swap(self.portal_end[0], self.portal_end[1], self.dest[0], self.dest[1])
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().get_unit_kind()
        self.engine.sounds.play('spawn_' + kind)
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)
        self.engine.delete_piece(self.dest[0], self.dest[1])
        self.engine.players[self.engine.turn].undo_action()
        if Constant.ACTIONS_UPDATE_ON_SPAWN:
            self.engine.players[self.engine.turn].remove_additional_actions(self.additional_actions)
        self.engine.players[self.engine.turn].remove_additional_piece_limit(self.additional_piece_limit)
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class SpawnTrap(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.spawn = self.engine.spawning
        self.dest = self.action_tile.get_position()
        self.spawner = self.acting_tile.get_occupying()
        self.piece_cost = Constant.PIECE_COSTS[self.engine.spawning]
        # Create a trap onto a square

    def __repr__(self):
        return 'trap'

    def complete(self):
        super().complete()
        self.engine.set_trap(self.dest[0], self.dest[1],
                             self.engine.PIECES['trap'](self.dest[0], self.dest[1], self.color))
        self.engine.sounds.play('spawn_building')
        self.spawner.actions_remaining -= 1
        self.engine.spawn_success = True
        self.engine.menus = []
        self.engine.reset_selected()
        if Constant.TRAP_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()
        self.engine.players[self.engine.turn].purchase(self.piece_cost)
        self.engine.intercept_pieces()
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        super().undo()
        self.spawner.actions_remaining += 1
        self.engine.sounds.play('spawn_building')
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)
        self.engine.untrap(self.dest[0], self.dest[1])
        if Constant.TRAP_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()
        self.engine.correct_interceptions()
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class TrapSpawn(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.spawn = self.engine.spawning
        self.dest = self.action_tile.get_position()
        self.spawner = self.acting_tile.get_occupying()
        self.additional_piece_limit = 0
        self.additional_actions = 0
        self.piece_cost = Constant.PIECE_COSTS[self.engine.spawning]
        self.trap = action_tile.trap
        self.is_protected = False
        if self.action_tile.is_protected():
            if self.action_tile.protected_by == self.color:
                self.is_protected = True

        # Spawn a piece onto a trap

    def __repr__(self):
        return 'spawn'

    def complete(self):
        super().complete()
        self.engine.spawn(self.dest[0], self.dest[1], self.spawn)
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().get_unit_kind()
        self.engine.sounds.play('spawn_' + kind)
        if not self.spawn == 'trap':
            self.engine.players[self.engine.turn].do_action()
        self.spawner.actions_remaining -= 1
        self.engine.spawn_success = True
        self.engine.menus = []
        self.engine.reset_selected()
        self.engine.players[self.engine.turn].purchase(self.piece_cost)
        if not self.is_protected:
            self.engine.untrap(self.dest[0], self.dest[1])
            self.engine.delete_piece(self.dest[0], self.dest[1])
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        super().undo()
        self.spawner.actions_remaining += 1
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)
        if not self.spawn == 'trap':
            self.engine.players[self.engine.turn].undo_action()
        if not self.is_protected:
            self.engine.set_trap(self.dest[0], self.dest[1], self.trap)
        self.engine.correct_interceptions()
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Spawn(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.spawn = self.engine.spawning
        self.dest = self.action_tile.get_position()
        self.spawner = self.acting_tile.get_occupying()
        self.additional_piece_limit = 0
        self.additional_actions = 0
        self.piece_cost = Constant.PIECE_COSTS[self.engine.spawning]

    def __repr__(self):
        return 'spawn'

    def complete(self):
        super().complete()
        self.engine.spawn(self.dest[0], self.dest[1], self.spawn)
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().get_unit_kind()
        self.engine.sounds.play('spawn_' + kind)
        self.spawner.actions_remaining -= 1
        self.engine.spawn_success = True
        self.engine.menus = []
        self.engine.reset_selected()
        if not self.spawn == 'trap':
            self.engine.players[self.engine.turn].do_action()

        self.engine.players[self.engine.turn].purchase(self.piece_cost)

        if Constant.ACTIONS_UPDATE_ON_SPAWN:
            self.additional_actions = self.engine.get_occupying(self.dest[0], self.dest[1]).get_additional_actions()
            self.engine.players[self.engine.turn].add_additional_actions(self.additional_actions)
        self.additional_piece_limit = self.engine.get_occupying(self.dest[0], self.dest[1]).get_additional_piece_limit()
        self.engine.intercept_pieces()
        self.engine.players[self.engine.turn].add_additional_piece_limit(self.additional_piece_limit)
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        super().undo()
        self.spawner.actions_remaining += 1
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().get_unit_kind()
        self.engine.sounds.play('spawn_' + kind)
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)
        self.engine.delete_piece(self.dest[0], self.dest[1])
        if not self.spawn == 'trap':
            self.engine.players[self.engine.turn].undo_action()

        if Constant.ACTIONS_UPDATE_ON_SPAWN:
            self.engine.players[self.engine.turn].remove_additional_actions(self.additional_actions)
        self.engine.players[self.engine.turn].remove_additional_piece_limit(self.additional_piece_limit)
        self.engine.correct_interceptions()
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class PortalMove(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.moved = self.acting_tile.get_occupying()
        self.start = self.moved.row, self.moved.col
        self.end = self.action_tile.row, self.action_tile.col
        self.portal_end = self.action_tile.connected_portal.get_position()
        self.trap = self.engine.board[self.portal_end[0]][self.portal_end[1]].trap
        self.trapped_tile = self.engine.board[self.portal_end[0]][self.portal_end[1]]
        self.is_protected = False
        if self.trapped_tile.is_protected():
            if self.trapped_tile.protected_by == self.color:
                self.is_protected = True
        if self.trap is not None and self.trap.color is self.color or self.is_protected:
            self.trap = None
        self.deleted_piece = None

    def __repr__(self):
        return 'move'

    def complete(self):
        super().complete()
        self.moved.actions_remaining -= 1
        self.engine.move(self.start[0], self.start[1], self.end[0], self.end[1])
        self.engine.swap(self.end[0], self.end[1], self.portal_end[0], self.portal_end[1])

        if self.trap:
            self.deleted_piece = self.engine.get_occupying(self.portal_end[0], self.portal_end[1])
            self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
            self.engine.untrap(self.portal_end[0], self.portal_end[1])

        self.engine.sounds.play('move')
        self.engine.reset_selected()
        self.engine.reset_unused_piece_highlight()
        self.engine.intercept_pieces()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.moved.actions_remaining += 1

        if self.deleted_piece:
            self.engine.create_piece(self.portal_end[0], self.portal_end[1], self.deleted_piece)
            self.engine.set_trap(self.portal_end[0], self.portal_end[1], self.trap)

        self.engine.swap(self.portal_end[0], self.portal_end[1], self.end[0], self.end[1])
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.engine.sounds.play('move')
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


class PortalCapture(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.moved = self.acting_tile.get_occupying()
        self.start = self.moved.row, self.moved.col
        self.end = self.action_tile.get_position()
        self.portal_end = self.action_tile.connected_portal.get_position()
        self.captured = self.action_tile.get_occupying()
        self.trap = self.engine.board[self.portal_end[0]][self.portal_end[1]].trap
        self.trapped_tile = self.engine.board[self.portal_end[0]][self.portal_end[1]]
        self.is_protected = False
        if self.trapped_tile.is_protected():
            if self.trapped_tile.protected_by == self.color:
                self.is_protected = True
        if self.trap is not None and self.trap.color is self.color or self.is_protected:
            self.trap = None
        self.deleted_piece = None

    def complete(self):
        super().complete()
        self.moved.actions_remaining -= 1

        self.engine.sounds.play('capture')
        self.engine.capture(self.start[0], self.start[1], self.end[0], self.end[1])
        self.engine.swap(self.end[0], self.end[1], self.portal_end[0], self.portal_end[1])
        if self.trap:
            self.deleted_piece = self.engine.get_occupying(self.portal_end[0], self.portal_end[1])
            self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
            self.engine.untrap(self.portal_end[0], self.portal_end[1])
        self.engine.players[self.engine.turn].do_action()
        self.engine.reset_unused_piece_highlight()
        self.engine.intercept_pieces()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        super().undo()
        self.moved.actions_remaining += 1
        if self.deleted_piece:
            self.engine.create_piece(self.portal_end[0], self.portal_end[1], self.deleted_piece)
            self.engine.set_trap(self.portal_end[0], self.portal_end[1], self.trap)
        self.engine.sounds.play('capture')
        self.engine.swap(self.portal_end[0], self.portal_end[1], self.end[0], self.end[1])
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.engine.create_piece(self.end[0], self.end[1], self.captured)
        self.engine.reset_selected()
        self.engine.players[self.engine.turn].undo_action()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class TrapMove(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.moved = self.acting_tile.get_occupying()
        self.color = self.moved.color
        self.start = self.moved.row, self.moved.col
        self.end = self.action_tile.get_position()
        self.trap = self.action_tile.trap
        self.is_protected = False
        if self.action_tile.is_protected:
            if self.action_tile.protected_by == self.color:
                self.is_protected = True

    def __repr__(self):
        return 'move'

    def complete(self):
        super().complete()
        self.moved.actions_remaining -= 1
        self.engine.move(self.start[0], self.start[1], self.end[0], self.end[1])
        self.engine.untrap(self.end[0], self.end[1])
        self.engine.delete_piece(self.end[0], self.end[1])
        self.engine.sounds.play('capture')
        self.engine.reset_selected()
        self.engine.reset_unused_piece_highlight()
        self.engine.intercept_pieces()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.moved.actions_remaining += 1
        self.engine.create_piece(self.end[0], self.end[1], self.moved)
        self.engine.set_trap(self.end[0], self.end[1], self.trap)
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.engine.sounds.play('move')
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


class TrapCapture(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.moved = self.acting_tile.get_occupying()
        self.start = self.moved.row, self.moved.col
        self.end = self.action_tile.get_position()
        self.captured = self.action_tile.get_occupying()
        self.trap = self.action_tile.trap

    def complete(self):
        super().complete()
        self.moved.actions_remaining -= 1
        self.engine.sounds.play('capture')
        self.engine.capture(self.start[0], self.start[1], self.end[0], self.end[1])
        self.engine.delete_piece(self.end[0], self.end[1])
        self.engine.untrap(self.end[0], self.end[1])
        self.engine.players[self.engine.turn].do_action()
        self.engine.reset_unused_piece_highlight()
        self.engine.intercept_pieces()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        super().undo()
        self.moved.actions_remaining += 1
        self.engine.sounds.play('capture')
        self.engine.create_piece(self.end[0], self.end[1], self.moved)
        self.engine.reset_selected()
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.engine.create_piece(self.end[0], self.end[1], self.captured)
        self.engine.set_trap(self.end[0], self.end[1], self.trap)
        self.engine.players[self.engine.turn].undo_action()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Capture(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.moved = self.acting_tile.get_occupying()
        self.start = self.moved.row, self.moved.col
        self.end = self.action_tile.get_position()
        self.captured = self.action_tile.get_occupying()

    def complete(self):
        super().complete()
        self.moved.actions_remaining -= 1
        self.engine.sounds.play('capture')
        self.engine.capture(self.start[0], self.start[1], self.end[0], self.end[1])
        self.engine.players[self.engine.turn].do_action()
        self.engine.reset_unused_piece_highlight()
        self.engine.intercept_pieces()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        super().undo()
        self.moved.actions_remaining += 1
        self.engine.sounds.play('capture')
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.engine.create_piece(self.end[0], self.end[1], self.captured)
        self.engine.players[self.engine.turn].undo_action()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Move(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.moved = self.acting_tile.get_occupying()
        self.start = self.moved.row, self.moved.col
        self.end = self.action_tile.get_position()

    def __repr__(self):
        return 'move'

    def complete(self):
        super().complete()
        self.moved.actions_remaining -= 1
        self.engine.move(self.start[0], self.start[1], self.end[0], self.end[1])
        self.engine.sounds.play('move')
        self.engine.reset_selected()
        self.engine.reset_unused_piece_highlight()
        self.engine.intercept_pieces()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.moved.actions_remaining += 1
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.engine.sounds.play('move')
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


class RitualEvent(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.engine = engine
        self.ritual_building = self.acting_tile.get_occupying()
        self.deleted_monks = []
        self.cost_type = self.engine.state[-1].cost_type
        self.ritual_cost = Constant.PRAYER_COSTS[str(self)][self.cost_type]

        if self.cost_type == 'gold':
            self.monk_cost = 0
        else:
            self.monk_cost = Constant.PRAYER_COSTS[str(self)]['monk']

        self.turn = self.engine.turn
        self.player = self.engine.players[self.turn]

    def complete(self):
        super().complete()
        self.engine.sounds.play('ritual')
        self.player.do_ritual(self.ritual_cost, self.cost_type)
        self.player.do_action()
        self.sacrifice_random_monks()
        self.ritual_building.actions_remaining -= 1

    def undo(self):
        super().undo()
        self.engine.sounds.play('ritual')
        self.player.undo_ritual(self.ritual_cost, self.cost_type)
        self.ritual_building.actions_remaining += 1
        self.respawn_deleted_monks()
        self.player.undo_action()

    def respawn_deleted_monks(self):
        if self.monk_cost != 0:
            for monk in self.deleted_monks:
                row = monk.row
                col = monk.col
                actions_remaining = monk.actions_remaining
                self.engine.create_piece(row, col, Monk(row, col, self.turn))
                self.engine.get_occupying(row, col).actions_remaining = actions_remaining

    def sacrifice_random_monks(self):
        if self.monk_cost != 0:
            count = []
            for piece in self.player.pieces:
                if isinstance(piece, Monk):
                    count.append(piece)

            random.shuffle(count)

            for i in range(self.monk_cost):
                try:
                    self.deleted_monks.append(count[i])
                    self.engine.delete_piece(count[i].row, count[i].col)
                except IndexError:
                    print("Index Error, 584 GameEvent.py")
                    print("Not enough monks to sacrifice")
                    pass


class GoldGeneralEvent(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.row, self.col = self.action_tile.get_position()
        self.portal_end = None
        self.trap = None
        self.portal_end_trap = None

    def __repr__(self):
        return 'gold_general'

    def complete(self):
        super().complete()
        piece = self.engine.PIECES[str(self)](self.row, self.col, self.turn)
        # Spawn on Trap
        if self.action_tile_has_effective_trap(self.acting_tile, self.action_tile):
            self.trap = self.engine.board[self.row][self.col].trap
            self.engine.board[self.row][self.col].untrap()
            return
        self.engine.create_piece(self.row, self.col, piece)
        # spawn On portal
        if self.engine.board[self.row][self.col].portal:
            connected_portal = self.engine.board[self.row][self.col].connected_portal
            self.engine.swap(self.row, self.col, connected_portal.row, connected_portal.col)
            self.portal_end = connected_portal.get_position()
            is_protected = False
            if self.action_tile_has_effective_trap(self.acting_tile, connected_portal):
                self.portal_end_trap = connected_portal.trap
                self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
                self.engine.untrap(self.portal_end[0], self.portal_end[1])

    def undo(self):
        super().undo()

        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        if self.trap:
            self.engine.set_trap(self.row, self.col, self.trap)
            return

        if self.engine.board[self.row][self.col].portal:
            if self.portal_end_trap:
                self.engine.set_trap(self.portal_end[0], self.portal_end[1], self.portal_end_trap)
                return
            connected_portal = self.engine.board[self.row][self.col].connected_portal
            self.engine.swap(self.row, self.col, connected_portal.row, connected_portal.col)
        self.engine.delete_piece(self.row, self.col)


class Teleport(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.selected_first, self.selected_second = action_tile
        self.dest_row, self.dest_col = self.selected_second
        self.portal_end = None
        self.portal_end_trap = None
        self.deleted_piece = None
        self.row, self.col = self.selected_first
        self.color = self.engine.board[self.row][self.col].get_occupying().color
        self.previously_selected = self.acting_tile.get_position()
        self.is_protected = False
        self.portal_end_is_protected = False

        self.trap = None
        self.portal_end_trap = None
        self.portal_end_tile = None

        if self.action_tile_has_effective_trap(self.acting_tile, self.engine.board[self.dest_row][self.dest_col]):
            self.trap = self.engine.board[self.dest_row][self.dest_col].trap

        if self.engine.board[self.dest_row][self.dest_col].portal:
            connected_portal = self.engine.board[self.dest_row][self.dest_col].connected_portal
            self.portal_end = connected_portal.get_position()
            if self.action_tile_has_effective_trap(self.acting_tile, connected_portal):
                self.portal_end_trap = connected_portal.trap

    def __repr__(self):
        return 'teleport'

    def complete(self):
        super().complete()
        self.engine.move(self.row, self.col, self.dest_row, self.dest_col)
        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = 0
        self.engine.intercept_pieces()

        if self.trap:
            self.deleted_piece = self.engine.get_occupying(self.dest_row, self.dest_col)
            self.engine.delete_piece(self.dest_row, self.dest_col)
            self.engine.untrap(self.dest_row, self.dest_col)
            return
        if self.engine.board[self.dest_row][self.dest_col].portal:
            self.engine.swap(self.dest_row, self.dest_col, self.portal_end[0], self.portal_end[1])
            if self.portal_end_trap:
                self.deleted_piece = self.engine.get_occupying(self.portal_end[0], self.portal_end[1])
                self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
                self.engine.untrap(self.portal_end[0], self.portal_end[1])
                return

    def undo(self):
        super().undo()
        if self.trap:
            self.engine.create_piece(self.dest_row, self.dest_col, self.deleted_piece)
            self.engine.set_trap(self.dest_row, self.dest_col, self.trap)
        elif self.engine.board[self.dest_row][self.dest_col].portal:
            self.engine.swap(self.portal_end[0], self.portal_end[1], self.dest_row, self.dest_col)
            if self.portal_end_trap:
                self.engine.create_piece(self.portal_end[0], self.portal_end[1], self.deleted_piece)
                self.engine.swap(self.portal_end[0], self.portal_end[1], self.dest_row, self.dest_col)
                self.engine.set_trap(self.portal_end[0], self.portal_end[1], self.portal_end_trap)
        self.engine.move(self.dest_row, self.dest_col, self.row, self.col)
        self.engine.get_occupying(self.row, self.col).actions_remaining = 1
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Swap(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.selected_first, self.selected_second = action_tile
        self.dest_row, self.dest_col = self.selected_second
        self.row, self.col = self.selected_first
        self.first_is_portal = False
        self.second_is_portal = False
        self.first_portal_end_trap = None
        self.second_portal_end_trap = None
        self.first_deleted_piece = None
        self.second_deleted_piece = None
        self.first_trap = None
        self.second_trap = None
        self.first_tile = self.engine.board[self.row][self.col]
        self.second_tile = self.engine.board[self.dest_row][self.dest_col]

        # TRAP ON FIRST TILE
        if self.action_tile_has_effective_trap(self.first_tile, self.second_tile):
            self.second_trap = self.second_tile.trap
        elif self.second_tile.portal:
            self.second_is_portal = True
            connected_portal = self.second_tile.connected_portal
            if self.action_tile_has_effective_trap(self.first_tile, connected_portal):
                self.second_portal_end_trap = connected_portal.trap

        # TRAP ON SECOND TILE
        if self.action_tile_has_effective_trap(self.second_tile, self.first_tile):
            self.first_trap = self.first_tile.trap
        elif self.first_tile.portal:
            self.first_is_portal = True
            connected_portal = self.first_tile.connected_portal
            if self.action_tile_has_effective_trap(self.second_tile, connected_portal):
                self.first_portal_end_trap = connected_portal.trap
        self.first_actions = self.engine.get_occupying(self.row, self.col).actions_remaining
        self.second_actions = self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining
        self.previously_selected = self.acting_tile.get_position()

    def __repr__(self):
        return 'swap'

    def complete(self):
        super().complete()
        self.engine.swap(self.row, self.col, self.dest_row, self.dest_col)

        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = 0
        self.engine.get_occupying(self.row, self.col).actions_remaining = 0
        # Here I have to figure out if each piece is swapped to a portal square
        if self.first_trap:
            self.first_deleted_piece = self.engine.get_occupying(self.row, self.col)
            self.engine.delete_piece(self.row, self.col)
            self.engine.untrap(self.row, self.col)
        elif self.first_is_portal:
            connected_portal = self.engine.board[self.row][self.col].connected_portal
            self.engine.swap(self.row, self.col, connected_portal.row, connected_portal.col)
            if self.first_portal_end_trap:
                self.first_deleted_piece = self.engine.get_occupying(connected_portal.row, connected_portal.col)
                self.engine.delete_piece(connected_portal.row, connected_portal.col)
                self.engine.untrap(connected_portal.row, connected_portal.col)
        if self.second_trap:
            self.second_deleted_piece = self.engine.get_occupying(self.dest_row, self.dest_col)
            self.engine.delete_piece(self.dest_row, self.dest_col)
            self.engine.untrap(self.dest_row, self.dest_col)
        elif self.second_is_portal:
            connected_portal = self.engine.board[self.dest_row][self.dest_col].connected_portal
            self.engine.swap(self.dest_row, self.dest_col, connected_portal.row, connected_portal.col)
            if self.second_portal_end_trap:
                self.second_deleted_piece = self.engine.get_occupying(connected_portal.row, connected_portal.col)
                self.engine.delete_piece(connected_portal.row, connected_portal.col)
                self.engine.untrap(connected_portal.row, connected_portal.col)

        self.engine.intercept_pieces()

    def undo(self):
        super().undo()
        if self.first_trap:
            self.engine.create_piece(self.row, self.col, self.first_deleted_piece)
            self.engine.set_trap(self.row, self.col, self.first_trap)
        elif self.first_is_portal:
            connected_portal = self.engine.board[self.row][self.col].connected_portal
            if self.first_portal_end_trap:
                self.engine.create_piece(connected_portal.row, connected_portal.col, self.first_deleted_piece)
                self.engine.set_trap(connected_portal.row, connected_portal.col, self.first_portal_end_trap)
            self.engine.swap(self.row, self.col, connected_portal.row, connected_portal.col)

        if self.second_trap:
            self.engine.create_piece(self.dest_row, self.dest_col, self.second_deleted_piece)
            self.engine.set_trap(self.dest_row, self.dest_col, self.second_trap)
        elif self.second_is_portal:
            connected_portal = self.engine.board[self.dest_row][self.dest_col].connected_portal
            if self.second_portal_end_trap:
                self.engine.create_piece(connected_portal.row, connected_portal.col, self.second_deleted_piece)
                self.engine.set_trap(connected_portal.row, connected_portal.col, self.second_portal_end_trap)
            self.engine.swap(self.dest_row, self.dest_col, connected_portal.row, connected_portal.col)
        self.engine.swap(self.dest_row, self.dest_col, self.row, self.col)
        self.engine.get_occupying(self.row, self.col).actions_remaining = self.first_actions
        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = self.second_actions
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Smite(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.row, self.col = self.action_tile.get_position()
        self.deleted_piece = self.engine.get_occupying(self.row, self.col)

    def __repr__(self):
        return 'smite'

    def complete(self):
        super().complete()
        self.engine.delete_piece(self.row, self.col)

    def undo(self):
        super().undo()
        self.engine.create_piece(self.row, self.col, self.deleted_piece)
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Trade(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.player = self.engine.players[self.engine.turn]
        self.give = self.engine.trading[0]
        self.receive = self.engine.trading[1]
        self.give_resource, self.give_amount = self.give[0], self.give[1]
        self.receive_resource, self.receive_amount = self.receive[0], self.receive[1]
        self.give_resource = Constant.RESOURCE_KEY[self.give_resource]
        self.receive_resource = Constant.RESOURCE_KEY[self.receive_resource]
        self.piece = self.acting_tile.get_occupying()

    def complete(self):
        super().complete()
        self.piece.actions_remaining -= 1
        amount = getattr(self.player, self.give_resource)

        # Debug
        print(f"Giving {self.give_amount} {self.give_resource} to {self.player}")

        setattr(self.player, self.give_resource, amount - self.give_amount)
        amount = getattr(self.player, self.receive_resource)

        # Debug
        print(f"Receiving {self.receive_amount} {self.receive_resource} from {self.player}")

        setattr(self.player, self.receive_resource, amount + self.receive_amount)
        self.engine.trading = []
        self.engine.piece_trading = None

    def undo(self):
        super().undo()
        self.piece.actions_remaining += 1
        amount = getattr(self.player, self.give_resource)
        setattr(self.player, self.give_resource, amount + self.give_amount)
        amount = getattr(self.player, self.receive_resource)
        setattr(self.player, self.receive_resource, amount - self.receive_amount)
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class DestroyResource(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.row, self.col = self.action_tile.get_position()
        self.deleted_resource = self.engine.get_resource(self.row, self.col)

    def __repr__(self):
        return 'destroy_resource'

    def complete(self):
        super().complete()
        self.engine.delete_resource(self.row, self.col)

    def undo(self):
        super().undo()
        self.engine.create_resource(self.row, self.col, self.deleted_resource)

        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class CreateResource(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.row, self.col = self.action_tile.get_position()
        self.resource = self.engine.ritual_summon_resource
        self.created_resource = self.engine.RESOURCES[self.resource](self.row, self.col)

    def __repr__(self):
        return 'create_resource'

    def complete(self):
        super().complete()

        self.engine.create_resource(self.row, self.col, self.created_resource)

    def undo(self):
        super().undo()
        self.engine.delete_resource(self.row, self.col)
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class LineDestroy(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.row, self.col = self.action_tile.get_position()
        self.selected_range = self.engine.line_destroy_selected_range
        self.destroyed_squares = self.record_destroyed_squares()
        self.destroyed_pieces = self.record_destroyed_pieces()

    def __repr__(self):
        return 'line_destroy'

    def record_destroyed_pieces(self):
        destroyed_pieces = []
        for tile in self.destroyed_squares:
            if tile.get_occupying():
                destroyed_pieces.append(tile.get_occupying())

        return destroyed_pieces

    def record_destroyed_squares(self):
        destroyed_squares = []
        for row in self.selected_range[0]:
            for col in self.selected_range[1]:
                if not self.engine.board[row][col].is_protected():
                    destroyed_squares.append(self.engine.board[row][col])

        return destroyed_squares

    def destroy_squares(self):
        for row in self.selected_range[0]:
            for col in self.selected_range[1]:
                if not self.engine.board[row][col].is_protected():
                    self.engine.board[row][col] = Tile(row, col)
                else:
                    break
            if self.engine.board[row][col].is_protected():
                break

    def remove_destroyed_pieces_from_player_list(self):
        for piece in self.destroyed_pieces:
            self.engine.players[piece.get_color()].pieces.remove(piece)

    def restore_destroyed_pieces_to_player_list(self):
        for piece in self.destroyed_pieces:
            self.engine.players[piece.color].pieces.append(piece)

    def replace_destroyed_squares(self):
        for tile in self.destroyed_squares:
            self.engine.board[tile.row][tile.col] = tile

    def complete(self):
        super().complete()
        self.destroy_squares()
        self.remove_destroyed_pieces_from_player_list()
        self.engine.intercept_pieces()
        self.engine.line_destroy_selected_range = None

    def undo(self):
        super().undo()
        self.restore_destroyed_pieces_to_player_list()
        self.replace_destroyed_squares()
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Protect(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.row, self.col = self.action_tile.get_position()
        self.protect_information = action_tile.get_protect_values()
        self.replace_protect = False

    def __repr__(self):
        return 'protect'

    def complete(self):
        super().complete()
        if self.engine.board[self.row][self.col] in self.engine.protected_tiles:
            self.replace_protect = True
            self.engine.protected_tiles.remove(self.engine.board[self.row][self.col])
        self.engine.board[self.row][self.col].protect(self.turn)
        self.engine.protected_tiles.append(self.engine.board[self.row][self.col])
        self.engine.intercept_pieces()

    def undo(self):
        super().undo()

        self.engine.board[self.row][self.col].unprotect()
        self.engine.protected_tiles.remove(self.engine.board[self.row][self.col])
        if self.replace_protect:
            self.action_tile.replace_values(self.protect_information)
            self.engine.protected_tiles.append(self.engine.board[self.row][self.col])
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Portal(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.selected_first, self.selected_second = action_tile
        self.dest_row, self.dest_col = self.selected_second
        self.row, self.col = self.selected_first
        self.previously_selected = self.acting_tile.get_position()
        self.first_saved_portal = None
        self.second_saved_portal = None

    def __repr__(self):
        return 'portal'

    def complete(self):
        super().complete()
        if self.engine.board[self.row][self.col].portal:
            tile = self.engine.board[self.row][self.col]
            self.first_saved_portal = (tile.portal_color, tile.connected_portal)
        self.engine.board[self.row][self.col].create_portal(self.turn, self.engine.board[self.dest_row][self.dest_col])
        if self.engine.board[self.dest_row][self.dest_col].portal:
            tile = self.engine.board[self.dest_row][self.dest_col]
            self.second_saved_portal = (tile.portal_color, tile.connected_portal)
        self.engine.board[self.dest_row][self.dest_col].create_portal(self.turn, self.engine.board[self.row][self.col])
        self.engine.intercept_pieces()

    def undo(self):
        super().undo()
        self.engine.board[self.row][self.col].delete_portal()
        if self.first_saved_portal:
            portal = self.first_saved_portal
            self.engine.board[self.row][self.col].create_portal(portal[0], portal[1])
        self.engine.board[self.dest_row][self.dest_col].delete_portal()
        if self.second_saved_portal:
            portal = self.second_saved_portal
            self.engine.board[self.dest_row][self.dest_col].create_portal(portal[0], portal[1])
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class AITurn(GameEvent):
    def __init__(self, engine, ai_turn_actions):
        super().__init__(engine)
        self.ai_turn_actions = ai_turn_actions

    def __repr__(self):
        return 'ai turn'

    def undo(self):
        for action in reversed(self.ai_turn_actions):
            action.undo()
            del action
