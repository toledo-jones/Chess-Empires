from Unit import *
from Resource import *
from Tile import Tile


class GameEvent:
    def __init__(self, engine, acting_tile=None, action_tile=None):
        self.engine = engine
        self.acting_tile = acting_tile
        self.action_tile = action_tile

    def complete(self):
        pass

    def undo(self):
        pass


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


class StartSpawn(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.spawn = self.engine.spawning
        self.dest = self.action_tile.get_position()
        self.previously_selected = None
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
        self.play_random_sound_effect(self.engine.get_occupying(self.dest[0], self.dest[1]))
        self.engine.spawnSuccess = True
        self.engine.spawning = None

    def undo(self):
        super().undo()
        self.play_random_sound_effect(self.engine.get_occupying(self.dest[0], self.dest[1]))
        self.engine.delete_piece(self.dest[0], self.dest[1])
        self.engine.spawn_count = self.spawn_count
        self.engine.final_spawn = self.final_spawn
        self.engine.spawn_list = self.spawn_list
        self.engine.spawning = self.engine.spawn_list[self.engine.spawn_count]
        if self.previously_selected:
            self.previously_selected.purchasing = True
        self.engine.set_state(self.state)
        self.engine.update_spawn_squares()
        self.engine.players[self.engine.turn].reset_piece_limit()

    def play_random_sound_effect(self, spawned):
        if isinstance(spawned, Building):
            i = random.randint(0, len(Constant.building_spawning) - 1)
            Constant.BUILDING_SPAWNING_SOUNDS[i].set_volume(.1)
            Constant.BUILDING_SPAWNING_SOUNDS[i].play()
        elif isinstance(spawned, Piece):
            i = random.randint(0, len(Constant.piece_spawning) - 1)
            Constant.PIECE_SPAWNING_SOUNDS[i].set_volume(.1)
            Constant.PIECE_SPAWNING_SOUNDS[i].play()


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
        self.engine.players[self.engine.turn].purchase(self.piece_cost)
        self.play_random_sound_effect()
        self.spawner.actions_remaining -= 1
        self.engine.spawn_success = True
        self.engine.menus = []
        self.engine.reset_selected()
        self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.spawner.actions_remaining += 1
        self.play_random_sound_effect()
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)
        self.engine.delete_resource(self.dest[0], self.dest[1])
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.players[self.engine.turn].undo_action()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.harvesting_rock) - 1)
        Constant.HARVESTING_ROCK_SOUNDS[i].set_volume(.1)
        Constant.HARVESTING_ROCK_SOUNDS[i].play()


class PortalSpawn(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.color = self.engine.turn
        self.spawn = self.engine.spawning
        self.dest = self.action_tile.get_position()
        self.portal_end = self.action_tile.connected_portal.get_position()
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
        self.play_random_sound_effect(self.engine.board[self.dest[0]][self.dest[1]].get_occupying())
        self.engine.intercept_pieces()
        self.engine.players[self.engine.turn].add_additional_piece_limit(self.additional_piece_limit)
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.swap(self.dest[0], self.dest[1], self.portal_end[0], self.portal_end[1])
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        super().undo()
        self.spawner.actions_remaining += 1
        self.engine.swap(self.portal_end[0], self.portal_end[1], self.dest[0], self.dest[1])
        self.play_random_sound_effect(self.engine.board[self.dest[0]][self.dest[1]].get_occupying())
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

    def play_random_sound_effect(self, spawned):
        if isinstance(spawned, Building):
            i = random.randint(0, len(Constant.building_spawning) - 1)
            Constant.BUILDING_SPAWNING_SOUNDS[i].set_volume(.1)
            Constant.BUILDING_SPAWNING_SOUNDS[i].play()
        elif isinstance(spawned, Piece):
            i = random.randint(0, len(Constant.piece_spawning) - 1)
            Constant.PIECE_SPAWNING_SOUNDS[i].set_volume(.1)
            Constant.PIECE_SPAWNING_SOUNDS[i].play()


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
        setattr(self.player, self.give_resource, amount  - self.give_amount)
        amount = getattr(self.player, self.receive_resource)
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
        self.play_random_sound_effect(self.engine.board[self.dest[0]][self.dest[1]].get_occupying())
        self.engine.intercept_pieces()
        self.engine.players[self.engine.turn].add_additional_piece_limit(self.additional_piece_limit)
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        super().undo()
        self.spawner.actions_remaining += 1
        self.play_random_sound_effect(self.engine.board[self.dest[0]][self.dest[1]].get_occupying())
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)
        self.engine.delete_piece(self.dest[0], self.dest[1])
        self.engine.players[self.engine.turn].undo_action()
        if Constant.ACTIONS_UPDATE_ON_SPAWN:
            self.engine.players[self.engine.turn].remove_additional_actions(self.additional_actions)
        self.engine.players[self.engine.turn].remove_additional_piece_limit(self.additional_piece_limit)
        self.engine.correct_interceptions()
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self, spawned):
        if isinstance(spawned, Building):
            i = random.randint(0, len(Constant.building_spawning) - 1)
            Constant.BUILDING_SPAWNING_SOUNDS[i].set_volume(.1)
            Constant.BUILDING_SPAWNING_SOUNDS[i].play()
        elif isinstance(spawned, Piece):
            i = random.randint(0, len(Constant.piece_spawning) - 1)
            Constant.PIECE_SPAWNING_SOUNDS[i].set_volume(.1)
            Constant.PIECE_SPAWNING_SOUNDS[i].play()


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
        self.play_random_sound_effect()
        self.thief.actions_remaining -= 1
        self.engine.players[self.engine.turn].steal(self.resource_stolen, self.amount)
        self.engine.players[Constant.TURNS[self.engine.turn]].invert_steal(self.resource_stolen, self.amount)
        if Constant.STEALING_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.thief.actions_remaining += 1
        self.play_random_sound_effect()
        self.engine.players[self.engine.turn].invert_steal(self.resource_stolen, self.amount)
        self.engine.players[Constant.TURNS[self.engine.turn]].steal(self.resource_stolen, self.amount)
        if Constant.STEALING_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.pray) - 1)
        Constant.PRAY_SOUNDS[i].set_volume(.5)
        Constant.PRAY_SOUNDS[i].play()


class Mine(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.miner = self.acting_tile.get_occupying()
        self.mined = self.action_tile.get_resource()
        self.additional_mining = 0
        if str(self.miner) == 'rogue_pawn':
            self.additional_mining = Constant.ADDITIONAL_MINING_FROM_ROGUE[Constant.RESOURCE_KEY[str(self.mined)]]
        self.miningOffset = self.mined.offsetIndex[-1]
        self.offsetIndex = self.mined.offsetIndex[:]
        self.sprite_id = self.mined.sprite_id
        self.sprite_offset = self.mined.offset

    def __repr__(self):
        return 'mine'

    def complete(self):
        super().complete()
        self.engine.players[self.engine.turn].mine(self.mined, self.miningOffset, self.additional_mining)
        self.mined.remaining -= 1
        self.miner.actions_remaining -= 1
        try:
            del self.mined.offsetIndex[-1]
        except IndexError:
            self.mined.offsetIndex = [0]
        self.play_random_sound_effect(str(self.mined))
        if self.mined.remaining == 0:
            if isinstance(self.mined, Quarry):
                self.engine.create_resource(self.mined.row, self.mined.col, SunkenQuarry(self.mined.row, self.mined.col))
            elif isinstance(self.mined, SunkenQuarry):
                self.engine.create_resource(self.mined.row, self.mined.col, DepletedQuarry(self.mined.row, self.mined.col))
            else:
                self.engine.delete_resource(self.mined.row, self.mined.col)
        if Constant.MINING_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        self.miner.actions_remaining += 1
        row = self.mined.row
        col = self.mined.col
        self.mined.remaining += 1
        self.engine.players[self.engine.turn].un_mine(self.mined, self.miningOffset, self.additional_mining)
        self.play_random_sound_effect(str(self.mined))
        resource = self.engine.RESOURCES[str(self.mined)](row, col)
        resource.offset = self.sprite_offset
        self.engine.create_resource(row, col, resource)
        self.engine.get_resource(row, col).remaining = self.mined.remaining
        self.engine.get_resource(row, col).offsetIndex.append(self.miningOffset)
        self.engine.get_resource(row, col).sprite_id = self.sprite_id
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        if Constant.MINING_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self, kind):
        if kind == 'quarry_1' or kind == 'gold_1' or kind == 'sunken_quarry_1':

            i = random.randint(0, len(Constant.harvesting_rock) - 1)
            Constant.HARVESTING_ROCK_SOUNDS[i].set_volume(.1)
            Constant.HARVESTING_ROCK_SOUNDS[i].play()
        else:
            i = random.randint(0, len(Constant.harvesting_wood) - 1)
            Constant.HARVESTING_WOOD_SOUNDS[i].set_volume(.1)
            Constant.HARVESTING_WOOD_SOUNDS[i].play()


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
        self.play_random_sound_effect()
        self.praying_piece.actions_remaining -= 1

        self.engine.players[self.engine.turn].pray(self.prayed_on, self.additional_prayer)
        if Constant.PRAYING_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        super().undo()
        praying_piece = self.engine.get_occupying(self.praying_piece.row, self.praying_piece.col)
        praying_piece.actions_remaining += 1
        self.play_random_sound_effect()
        self.engine.players[self.engine.turn].un_pray(self.prayed_on, self.additional_prayer)
        if Constant.PRAYING_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.pray) - 1)
        Constant.PRAY_SOUNDS[i].set_volume(.5)
        Constant.PRAY_SOUNDS[i].play()


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


class PortalMove(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.moved = self.acting_tile.get_occupying()
        self.start = self.moved.row, self.moved.col
        self.end = self.action_tile.row, self.action_tile.col
        self.portal_end = self.action_tile.connected_portal.get_position()

    def __repr__(self):
        return 'move'

    def complete(self):
        super().complete()
        self.moved.actions_remaining -= 1
        self.engine.move(self.start[0], self.start[1], self.end[0], self.end[1])
        self.engine.swap(self.end[0], self.end[1], self.portal_end[0], self.portal_end[1])
        self.play_random_sound_effect()
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
        self.engine.swap(self.portal_end[0], self.portal_end[1], self.end[0], self.end[1])
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.play_random_sound_effect()
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.moves) - 1)
        Constant.MOVE_SOUNDS[i].set_volume(.1)
        Constant.MOVE_SOUNDS[i].play()


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
        self.play_random_sound_effect()
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
        self.play_random_sound_effect()
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.moves) - 1)
        Constant.MOVE_SOUNDS[i].set_volume(.1)
        Constant.MOVE_SOUNDS[i].play()


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


class PortalCapture(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.moved = self.acting_tile.get_occupying()
        self.start = self.moved.row, self.moved.col
        self.end = self.action_tile.get_position()
        self.portal_end = self.action_tile.connected_portal.get_position()
        self.captured = self.action_tile.get_occupying()

    def complete(self):
        super().complete()
        self.moved.actions_remaining -= 1
        self.play_random_sound_effect()
        self.engine.capture(self.start[0], self.start[1], self.end[0], self.end[1])
        self.engine.swap(self.end[0], self.end[1], self.portal_end[0], self.portal_end[1])
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
        self.play_random_sound_effect()
        self.engine.swap(self.portal_end[0], self.portal_end[1], self.end[0], self.end[1])
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.engine.create_piece(self.end[0], self.end[1], self.captured)
        self.engine.players[self.engine.turn].undo_action()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.captures) - 1)
        Constant.CAPTURE_SOUNDS[i].set_volume(.1)
        Constant.CAPTURE_SOUNDS[i].play()


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
        self.play_random_sound_effect()
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
        self.play_random_sound_effect()
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.engine.create_piece(self.end[0], self.end[1], self.captured)
        self.engine.players[self.engine.turn].undo_action()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.captures) - 1)
        Constant.CAPTURE_SOUNDS[i].set_volume(.1)
        Constant.CAPTURE_SOUNDS[i].play()


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
        self.protected_tiles = self.engine.protected_tiles

    def complete(self):
        super().complete()
        self.play_random_sound_effect()
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
        protected_tiles = self.protected_tiles
        self.engine.tick_protected_tiles(protected_tiles)
        if Constant.DEBUG_RITUALS:
            self.engine.monolith_rituals.append(Constant.MONOLITH_RITUALS)
        else:
            if self.engine.turn_count_actual == len(self.engine.monolith_rituals) - 1:
                self.engine.monolith_rituals.append(self.engine.generate_available_rituals(Constant.MONOLITH_RITUALS, Constant.MAX_MONOLITH_RITUALS_PER_TURN))
        if self.engine.turn_count_actual == len(self.engine.trade_conversions) - 1:
            self.engine.trade_conversions.append(self.engine.trade_handler.get_conversions())
        if self.engine.turn_count_actual == len(self.engine.piece_stealing_offsets) - 1:
            self.engine.piece_stealing_offsets.append(self.engine.generate_stealing_offsets(Constant.STEALING_KEY['piece']))
        if self.engine.turn_count_actual == len(self.engine.building_stealing_offsets) - 1:
            self.engine.building_stealing_offsets.append(self.engine.generate_stealing_offsets(Constant.STEALING_KEY['building']))
        if self.engine.turn_count_actual == len(self.engine.trader_stealing_offsets) - 1:
            self.engine.trader_stealing_offsets.append(self.engine.generate_stealing_offsets(Constant.STEALING_KEY['trader']))
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        self.play_random_sound_effect()
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

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.change_turn) - 1)
        Constant.CHANGE_TURN_SOUNDS[i].set_volume(.1)
        Constant.CHANGE_TURN_SOUNDS[i].play()


class RitualEvent(GameEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.engine = engine
        self.ritual_building = self.acting_tile.get_occupying()
        self.deleted_monks = []
        self.ritual_cost = Constant.PRAYER_COSTS[str(self)]['prayer']
        self.monk_cost = Constant.PRAYER_COSTS[str(self)]['monk']
        self.turn = self.engine.turn
        self.player = self.engine.players[self.turn]

    def complete(self):
        super().complete()
        self.play_random_sound_effect()
        self.ritual_building.actions_remaining -= 1

    def undo(self):
        super().undo()
        self.play_random_sound_effect()
        self.ritual_building.actions_remaining += 1

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.rituals) - 1)
        Constant.PRAYER_RITUAL_SOUNDS[i].set_volume(.5)
        Constant.PRAYER_RITUAL_SOUNDS[i].play()

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
        self.row, self.col = self.action_tile.get_position()

    def __repr__(self):
        return 'gold_general'

    def complete(self):
        super().complete()
        piece = self.engine.PIECES[str(self)](self.row, self.col, self.turn)
        self.engine.create_piece(self.row, self.col, piece)
        if self.engine.board[self.row][self.col].portal:
            connected_portal = self.engine.board[self.row][self.col].conneceted_portal
            self.engine.swap(self.row, self.col, connected_portal.row, connected_portal.col)
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self):
        super().undo()
        if self.engine.board[self.row][self.col].portal:
            connected_portal = self.engine.board[self.row][self.col].conneceted_portal
            self.engine.swap(self.row, self.col, connected_portal.row, connected_portal.col)
        self.engine.delete_piece(self.row, self.col)
        self.respawn_deleted_monks()
        self.player.undo_ritual(self.ritual_cost)
        self.player.undo_action()
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Smite(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.row, self.col = self.action_tile.get_position()
        self.deleted_piece = str(self.engine.get_occupying(self.row, self.col))
        self.piece_actions_remaining = self.engine.get_occupying(self.row, self.col).actions_remaining

    def __repr__(self):
        return 'smite'

    def complete(self):
        super().complete()
        self.engine.delete_piece(self.row, self.col)
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self):
        super().undo()
        self.respawn_deleted_monks()
        piece = self.engine.PIECES[self.deleted_piece](self.row, self.col, Constant.TURNS[self.turn])
        self.engine.create_piece(self.row, self.col, piece)
        self.engine.get_occupying(self.row, self.col).actions_remaining = self.piece_actions_remaining
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


class DestroyResource(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.row, self.col = self.action_tile.get_position()
        self.deleted_resource_offset_index = self.engine.get_resource(self.row, self.col).offsetIndex
        self.deleted_resource = str(self.engine.get_resource(self.row, self.col))

    def __repr__(self):
        return 'destroy_resource'

    def complete(self):
        super().complete()
        self.engine.delete_resource(self.row, self.col)
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self):
        super().undo()
        self.respawn_deleted_monks()
        resource = self.engine.RESOURCES[self.deleted_resource](self.row, self.col)
        self.engine.create_resource(self.row, self.col, resource)
        self.engine.get_resource(self.row, self.col).offsetIndex = self.deleted_resource_offset_index
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


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
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self):
        super().undo()
        self.respawn_deleted_monks()
        self.engine.delete_resource(self.row, self.col)
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


class Teleport(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.selected_first, self.selected_second = action_tile
        self.dest_row, self.dest_col = self.selected_second
        self.portal_end = None
        if self.engine.board[self.dest_row][self.dest_col].portal:
            self.portal_end = self.engine.board[self.dest_row][self.dest_col].connected_portal.get_position()

        self.row, self.col = self.selected_first
        self.previously_selected = self.acting_tile.get_position()

    def __repr__(self):
        return 'teleport'

    def complete(self):
        super().complete()
        self.engine.move(self.row, self.col, self.dest_row, self.dest_col)
        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = 0
        self.engine.intercept_pieces()
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()
        if self.portal_end:
            self.engine.swap(self.dest_row, self.dest_col, self.portal_end[0], self.portal_end[1])

    def undo(self):
        super().undo()
        self.respawn_deleted_monks()
        if self.portal_end:
            self.engine.swap(self.portal_end[0], self.portal_end[1], self.dest_row, self.dest_col)
        self.engine.move(self.dest_row, self.dest_col, self.row, self.col)
        self.engine.get_occupying(self.row, self.col).actions_remaining = 1
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


class Swap(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.selected_first, self.selected_second = action_tile
        self.dest_row, self.dest_col = self.selected_second
        self.row, self.col = self.selected_first
        self.first_is_portal = False
        self.second_is_portal = False
        if self.engine.board[self.row][self.col].portal:
            self.first_is_portal = True
        if self.engine.board[self.dest_row][self.dest_col].portal:
            self.second_is_portal = True
        self.previously_selected = self.acting_tile.get_position()
        self.first_actions = self.engine.get_occupying(self.row, self.col).actions_remaining
        self.second_actions = self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining

    def __repr__(self):
        return 'swap'

    def complete(self):
        super().complete()
        self.engine.swap(self.row, self.col, self.dest_row, self.dest_col)

        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = 0
        self.engine.get_occupying(self.row, self.col).actions_remaining = 0
        if self.first_is_portal:
            connected_portal = self.engine.board[self.row][self.col].connected_portal
            self.engine.swap(self.row, self.col, connected_portal.row, connected_portal.col)
        if self.second_is_portal:
            connected_portal = self.engine.board[self.dest_row][self.dest_col].connected_portal
            self.engine.swap(self.dest_row, self.dest_col, connected_portal.row, connected_portal.col)
        self.engine.intercept_pieces()
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self):
        super().undo()
        self.respawn_deleted_monks()
        if self.first_is_portal:
            connected_portal = self.engine.board[self.row][self.col].connected_portal
            self.engine.swap(self.row, self.col, connected_portal.row, connected_portal.col)
        if self.second_is_portal:
            connected_portal = self.engine.board[self.dest_row][self.dest_col].connected_portal
            self.engine.swap(self.dest_row, self.dest_col, connected_portal.row, connected_portal.col)
        self.engine.swap(self.dest_row, self.dest_col, self.row, self.col)
        self.engine.get_occupying(self.row, self.col).actions_remaining = self.first_actions
        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = self.second_actions
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


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
        self.sacrifice_random_monks()
        self.engine.intercept_pieces()
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.engine.line_destroy_selected_range = None

    def undo(self):
        super().undo()
        self.restore_destroyed_pieces_to_player_list()
        self.replace_destroyed_squares()
        self.respawn_deleted_monks()
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


class Protect(RitualEvent):
    def __init__(self, engine, acting_tile, action_tile):
        super().__init__(engine, acting_tile, action_tile)
        self.row, self.col = self.action_tile.get_position()

    def __repr__(self):
        return 'protect'

    def complete(self):
        super().complete()
        self.engine.board[self.row][self.col].protect(self.turn)
        self.engine.protected_tiles.append(self.engine.board[self.row][self.col])
        self.engine.intercept_pieces()
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self):
        super().undo()
        self.engine.board[self.row][self.col].unprotect()
        self.engine.protected_tiles.remove(self.engine.board[self.row][self.col])
        self.respawn_deleted_monks()
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


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
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

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
        self.respawn_deleted_monks()
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[self.engine.turn].undo_action()


