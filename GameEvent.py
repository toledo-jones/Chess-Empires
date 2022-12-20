from Piece import *
from Resource import *
from Tile import Tile
from Building import *


class GameEvent:
    def __init__(self):
        pass

    def complete(self, engine):
        pass


class StartSpawn(GameEvent):
    def __init__(self, color, spawn, dest, spawn_count, final_spawn, prev):
        #
        #   Call parent Initialization
        #

        super().__init__()

        #
        #   Set arguments to class members
        #

        # Color is the color of the piece being spawned
        self.color = color

        self.spawn = spawn

        # (x, y) coordinate of the piece being spawned
        self.dest = dest
        # Record the spawn count in case we have to undo
        # Spawn count is the index of the pieces we are spawning of the first 4 spawns in the game, for each player
        # (This should be done in the __init__)
        self.spawn_count = spawn_count

        # Track the final spawn
        # (This should be done in the __init__)
        self.final_spawn = final_spawn

        # Track previously selected piece
        # (This should be done in the __init__)
        self.prev = prev

    def complete(self, engine):
        #
        #   Execute start spawn GameEvent in Engine
        #
        engine.spawn(self.dest[0], self.dest[1], self.spawn)
        self.play_random_sound_effect(engine.get_occupying(self.dest[0], self.dest[1]))
        #
        # Set the spawn success flag to true so the engine knows to move on to the next spawn
        #
        engine.spawnSuccess = True

        #
        # Set the piece spawning back to none so the engine draws the next piece properly
        #
        engine.spawning = None

        #
        # Execute Parent Complete
        #
        super().complete(engine)

    def undo(self, engine):
        self.play_random_sound_effect(engine.get_occupying(self.dest[0], self.dest[1]))
        #
        #  Copy board and store as a new 2 dimensional array
        #

        # Delete the piece spawned at the destination (x,y)
        engine.delete_piece(self.dest[0], self.dest[1])

        #
        engine.spawn_count = self.spawn_count

        #
        engine.final_spawn = self.final_spawn

        #
        engine.spawning = Constant.STARTING_PIECES[engine.spawn_count]

        #
        try:
            self.prev.purchasing = True
        except AttributeError:
            print("Attribute Error")
            print(" -- Line 103, GameEvent")

        #
        engine.set_state('start spawn')

        #
        engine.update_spawn_squares()
        engine.players[engine.turn].reset_piece_limit()

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
    def __init__(self, color, spawn, dest, spawner):
        #
        #
        #
        super().__init__()

        #
        self.color = color

        #
        self.spawn = spawn

        #
        self.dest = dest

        #
        self.spawner = spawner

        #
        self.dest = dest

    def complete(self, engine):
        #
        #   Copy the Board object from Engine
        #
        resource = engine.RESOURCES[self.spawn](self.dest[0], self.dest[1])
        engine.create_resource(self.dest[0], self.dest[1], resource)
        self.play_random_sound_effect()

        self.spawner.actions_remaining -= 1

        engine.spawn_success = True

        engine.menus = []

        engine.reset_selected()
        engine.players[engine.turn].do_action()
        super().complete(engine)

    def undo(self, engine):
        self.spawner.actions_remaining += 1
        self.play_random_sound_effect()
        cost = Constant.PIECE_COSTS[self.spawn]
        engine.players[engine.turn].un_purchase(cost)
        engine.delete_resource(self.dest[0], self.dest[1])
        unused_pieces = engine.count_unused_pieces()
        engine.reset_unused_piece_highlight()
        engine.players[engine.turn].undo_action()

        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.harvesting_rock) - 1)
        Constant.HARVESTING_ROCK_SOUNDS[i].set_volume(.1)
        Constant.HARVESTING_ROCK_SOUNDS[i].play()


class Spawn(GameEvent):
    def __init__(self, color, spawn, dest, spawner):
        #
        #
        #
        super().__init__()

        #
        self.color = color

        #
        self.spawn = spawn

        #
        self.dest = dest

        #
        self.spawner = spawner

        #
        self.dest = dest

    def complete(self, engine):
        #
        #   Copy the Board object from Engine
        #
        engine.spawn(self.dest[0], self.dest[1], self.spawn)
        self.spawner.actions_remaining -= 1

        engine.spawn_success = True

        engine.menus = []
        engine.reset_selected()
        engine.players[engine.turn].do_action()

        if Constant.ACTIONS_UPDATE_ON_SPAWN:
            self.additional_actions = engine.get_occupying(self.dest[0], self.dest[1]).get_additional_actions()
            engine.players[engine.turn].add_additional_actions(self.additional_actions)

        self.additional_piece_limit = engine.get_occupying(self.dest[0], self.dest[1]).get_additional_piece_limit()
        self.play_random_sound_effect(engine.board[self.dest[0]][self.dest[1]].get_occupying())

        engine.intercept_pieces()
        engine.players[engine.turn].add_additional_piece_limit(self.additional_piece_limit)
        engine.reset_unused_piece_highlight()
        unused_pieces = engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        super().complete(engine)

    def undo(self, engine):
        self.spawner.actions_remaining += 1
        self.play_random_sound_effect(engine.board[self.dest[0]][self.dest[1]].get_occupying())
        cost = Constant.PIECE_COSTS[self.spawn]
        engine.players[engine.turn].un_purchase(cost)
        engine.delete_piece(self.dest[0], self.dest[1])
        engine.players[engine.turn].undo_action()
        if Constant.ACTIONS_UPDATE_ON_SPAWN:
            engine.players[engine.turn].remove_additional_actions(self.additional_actions)
        engine.players[engine.turn].remove_additional_piece_limit(self.additional_piece_limit)
        engine.reset_unused_piece_highlight()
        engine.correct_interceptions()
        unused_pieces = engine.count_unused_pieces()
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
    def __init__(self, stolen_from, thief, resource_stolen, amount):
        #
        #   Call Parent __init__ Method
        #
        super().__init__()

        #
        #   Store the Resource() Object as Mined
        #   Store the Piece() Object as Miner
        #
        self.stolen_from = stolen_from
        self.thief = thief
        self.resource_stolen = resource_stolen
        self.amount = amount

        #
        #   Store the List of Values which dictate the offset when mining each material.
        #   Offset is +1, -1 or 0. This is how much is added to the default value when mining.
        #


    def complete(self, engine):
        self.play_random_sound_effect()
        self.thief.actions_remaining -= 1

        engine.players[engine.turn].steal(self.resource_stolen, self.amount)
        engine.players[Constant.TURNS[engine.turn]].invert_steal(self.resource_stolen, self.amount)

        if Constant.STEALING_COSTS_ACTION:
            engine.players[engine.turn].do_action()

    def undo(self, engine):
        thief = engine.get_occupying(self.thief.row, self.thief.col)
        thief.actions_remaining += 1
        self.play_random_sound_effect()
        engine.players[engine.turn].invert_steal(self.resource_stolen, self.amount)
        engine.players[Constant.TURNS[engine.turn]].steal(self.resource_stolen, self.amount)
        #
        #   undo stealing
        #

        if Constant.STEALING_COSTS_ACTION:
            engine.players[engine.turn].undo_action()
        unused_pieces = engine.count_unused_pieces()
        engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.pray) - 1)
        Constant.PRAY_SOUNDS[i].set_volume(.5)
        Constant.PRAY_SOUNDS[i].play()



class Mine(GameEvent):
    def __init__(self, mined, miner):
        #
        #   Call Parent __init__ Method
        #
        super().__init__()

        #
        #   Store the Resource() Object as Mined
        #   Store the Piece() Object as Miner
        #
        self.mined = mined
        self.miner = miner

        #
        #   Store the List of Values which dictate the offset when mining each material.
        #   Offset is +1, -1 or 0. This is how much is added to the default value when mining.
        #
        try:
            self.miningOffset = mined.offsetIndex[-1]
        except IndexError:
            self.miningOffset = None
            print("IndexError")
            print("GameEvent.py, line 249")
        self.offsetIndex = mined.offsetIndex[:]
        self.sprite_id = self.mined.sprite_id
        self.sprite_offset = self.mined.offset

    def complete(self, engine):
        engine.players[engine.turn].mine(self.mined, self.miningOffset)
        self.mined.remaining -= 1
        self.miner.actions_remaining -= 1
        try:
            del self.mined.offsetIndex[-1]
        except IndexError:
            self.mined.offsetIndex = [0]
        self.play_random_sound_effect(str(self.mined))
        if self.mined.remaining == 0:
            if isinstance(self.mined, Quarry):
                engine.create_resource(self.mined.row, self.mined.col, SunkenQuarry(self.mined.row, self.mined.col))
            elif isinstance(self.mined, SunkenQuarry):
                engine.create_resource(self.mined.row, self.mined.col, DepletedQuarry(self.mined.row, self.mined.col))
            else:
                engine.delete_resource(self.mined.row, self.mined.col)
        if Constant.MINING_COSTS_ACTION:
            engine.players[engine.turn].do_action()
        super().complete(engine)

    def undo(self, engine):
        self.miner.actions_remaining += 1
        row = self.mined.row
        col = self.mined.col
        self.mined.remaining += 1
        engine.players[engine.turn].un_mine(self.mined, self.miningOffset)
        self.play_random_sound_effect(str(self.mined))
        resource = engine.RESOURCES[str(self.mined)](row, col)
        resource.offset = self.sprite_offset
        engine.create_resource(row, col, resource)

        engine.get_resource(row, col).remaining = self.mined.remaining
        engine.get_resource(row, col).offsetIndex.append(self.miningOffset)
        engine.get_resource(row, col).sprite_id = self.sprite_id
        unused_pieces = engine.count_unused_pieces()
        engine.reset_unused_piece_highlight()
        if Constant.MINING_COSTS_ACTION:
            engine.players[engine.turn].undo_action()

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
    def __init__(self, praying_piece, prayed_on):
        self.praying_piece = praying_piece
        self.prayed_on = prayed_on
        self.additional_prayer = 0
        if str(self.praying_piece) == 'monk':
            self.additional_prayer = Constant.ADDITIONAL_PRAYER_FROM_MONK

    def complete(self, engine):
        self.play_random_sound_effect()
        self.praying_piece.actions_remaining -= 1

        engine.players[engine.turn].pray(self.prayed_on, self.additional_prayer)
        if Constant.PRAYING_COSTS_ACTION:
            engine.players[engine.turn].do_action()

    def undo(self, engine):
        praying_piece = engine.get_occupying(self.praying_piece.row, self.praying_piece.col)
        praying_piece.actions_remaining += 1
        self.play_random_sound_effect()
        engine.players[engine.turn].un_pray(self.prayed_on, self.additional_prayer)
        if Constant.PRAYING_COSTS_ACTION:
            engine.players[engine.turn].undo_action()
        unused_pieces = engine.count_unused_pieces()
        engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.pray) - 1)
        Constant.PRAY_SOUNDS[i].set_volume(.5)
        Constant.PRAY_SOUNDS[i].play()


class Move(GameEvent):
    def __init__(self, moved, start, end):
        super().__init__()
        self.moved = moved
        self.start = start
        self.end = end

    def complete(self, engine):
        #
        #   Set remaining turn actions of moving piece to 0
        #
        self.moved.actions_remaining -= 1
        #
        #   Change the Row, Col in the piece object to correspond to the new location
        #
        engine.move(self.start[0], self.start[1], self.end[0], self.end[1])
        self.play_random_sound_effect()

        #
        #   Turn off all selections
        #
        engine.reset_selected()
        engine.reset_unused_piece_highlight()
        engine.intercept_pieces()
        engine.correct_interceptions()
        unused_pieces = engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        engine.players[engine.turn].do_action()

        super().complete(engine)

    def undo(self, engine):
        #
        #   Reset actions remaining for piece moving
        #
        self.moved.actions_remaining += 1

        #
        #   Change row, col of object on board back to the start position
        #
        engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        self.play_random_sound_effect()
        #
        #   reset all different kinds of selections
        #
        engine.reset_selected()

        #
        #   determine all pieces which are unused
        #
        unused_pieces = engine.count_unused_pieces()
        #
        #
        #
        engine.reset_unused_piece_highlight()
        engine.correct_interceptions()
        #
        #
        #
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        engine.players[engine.turn].undo_action()

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.moves) - 1)
        Constant.MOVE_SOUNDS[i].set_volume(.1)
        Constant.MOVE_SOUNDS[i].play()


class Capture(GameEvent):
    def __init__(self, moved, start, end, captured):
        super().__init__()
        self.moved = moved
        self.start = start
        self.end = end
        self.captured = captured

    def complete(self, engine):
        self.moved.actions_remaining -= 1
        self.play_random_sound_effect()
        engine.players[engine.turn].captured_pieces.append(engine.get_occupying(self.end[0], self.end[1]))
        engine.capture(self.start[0], self.start[1], self.end[0], self.end[1])
        engine.players[engine.turn].do_action()
        engine.reset_unused_piece_highlight()
        engine.intercept_pieces()
        engine.correct_interceptions()
        unused_pieces = engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        super().complete(engine)

    def undo(self, engine):
        self.moved.actions_remaining += 1
        self.play_random_sound_effect()
        del engine.players[engine.turn].captured_pieces[-1]
        engine.move(self.end[0], self.end[1], self.start[0], self.start[1])
        piece = engine.PIECES[str(self.captured)](self.end[0], self.end[1], self.captured.color)
        engine.create_piece(self.end[0], self.end[1], piece)
        engine.players[engine.turn].undo_action()
        engine.reset_unused_piece_highlight()
        engine.correct_interceptions()
        unused_pieces = engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.captures) - 1)
        Constant.CAPTURE_SOUNDS[i].set_volume(.1)
        Constant.CAPTURE_SOUNDS[i].play()


class ChangeTurn(GameEvent):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.prev = engine.update_previously_selected()
        self.spawn_success = engine.spawn_success
        self.menus = engine.menus
        self.state = engine.state[-1]
        self.used_pieces = engine.count_used_pieces()
        self.spawning = engine.spawning
        self.player_actions_remaining = self.engine.players[self.engine.turn].get_actions_remaining()
        self.player_piece_limit = self.engine.players[self.engine.turn].get_piece_limit()
        self.player_prayer = self.engine.players[self.engine.turn].get_prayer()
        self.used_and_intercepted_pieces = engine.used_and_intercepted_pieces
        self.protected_tiles = self.engine.protected_tiles

    def complete(self, engine):
        super().complete(self.engine)
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
        protected_tiles = self.protected_tiles
        self.engine.tick_protected_tiles(protected_tiles)
        if self.engine.turn_count_actual == len(self.engine.prayer_stone_rituals) - 1:
            self.engine.prayer_stone_rituals.append(self.engine.generate_available_rituals(
                Constant.PRAYER_STONE_RITUALS, Constant.MAX_PRAYER_STONE_RITUALS_PER_TURN))
        if self.engine.turn_count_actual == len(self.engine.monolith_rituals) - 1:
            self.engine.monolith_rituals.append(self.engine.generate_available_rituals(Constant.MONOLITH_RITUALS, Constant.MAX_MONOLITH_RITUALS_PER_TURN))
        if self.engine.turn_count_actual == len(self.engine.piece_stealing_offsets) - 1:
            self.engine.piece_stealing_offsets.append(self.engine.generate_stealing_offsets(Constant.STEALING_KEY['piece']))
        if self.engine.turn_count_actual == len(self.engine.building_stealing_offsets) - 1:
            self.engine.building_stealing_offsets.append(self.engine.generate_stealing_offsets(Constant.STEALING_KEY['building']))
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self, engine):
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
        engine.reset_unused_piece_highlight()
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
    def __init__(self, engine, ritual_building):
        super().__init__()
        self.engine = engine
        self.ritual_building = ritual_building
        self.deleted_monks = []
        self.ritual_cost = Constant.PRAYER_COSTS[str(self)]['prayer']
        self.monk_cost = Constant.PRAYER_COSTS[str(self)]['monk']
        self.turn = self.engine.turn
        self.player = self.engine.players[self.turn]

    def complete(self):
        self.play_random_sound_effect()
        self.ritual_building.actions_remaining -= 1

    def undo(self, engine):
        self.play_random_sound_effect()
        self.ritual_building.actions_remaining += 1

    def play_random_sound_effect(self):
        i = random.randint(0, len(Constant.rituals) - 1)
        Constant.PRAYER_RITUAL_SOUNDS[i].set_volume(.5)
        Constant.PRAYER_RITUAL_SOUNDS[i].play()

    def respawn_deleted_monks(self):
        if self.monk_cost != 0:
            for i in range(self.monk_cost):
                row = self.deleted_monks[i].row
                col = self.deleted_monks[i].col
                actions_remaining = self.deleted_monks[i].actions_remaining
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
    def __init__(self, engine, ritual_building, row, col):
        super().__init__(engine, ritual_building)
        self.row = row
        self.col = col

    def __repr__(self):
        return 'gold_general'

    def complete(self):
        super().complete()
        piece = self.engine.PIECES[str(self)](self.row, self.col, self.turn)
        self.engine.create_piece(self.row, self.col, piece)
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self, engine):
        super().undo(engine)
        self.respawn_deleted_monks()
        self.engine.delete_piece(self.row, self.col)
        self.player.undo_ritual(self.ritual_cost)
        self.player.undo_action()
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[engine.turn].undo_action()


class Smite(RitualEvent):
    def __init__(self, engine, ritual_building, row, col):
        super().__init__(engine, ritual_building)
        self.row = row
        self.col = col
        self.deleted_piece = str(self.engine.get_occupying(self.row, self.col))

    def __repr__(self):
        return 'smite'

    def complete(self):
        super().complete()

        self.engine.delete_piece(self.row, self.col)
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self, engine):
        super().undo(engine)
        self.respawn_deleted_monks()
        piece = self.engine.PIECES[self.deleted_piece](self.row, self.col, Constant.TURNS[self.turn])
        self.engine.create_piece(self.row, self.col, piece)
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[engine.turn].undo_action()


class DestroyResource(RitualEvent):
    def __init__(self, engine, ritual_building, row, col):
        super().__init__(engine, ritual_building)
        self.row = row
        self.col = col
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

    def undo(self, engine):
        super().undo(engine)
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
        self.engine.players[engine.turn].undo_action()


class CreateResource(RitualEvent):
    def __init__(self, engine, ritual_building, row, col, resource):
        super().__init__(engine, ritual_building)
        self.row = row
        self.col = col
        self.created_resource = self.engine.RESOURCES[resource](self.row, self.col)

    def __repr__(self):
        return 'create_resource'

    def complete(self):
        super().complete()

        self.engine.create_resource(self.row, self.col, self.created_resource)
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self, engine):
        super().undo(engine)
        self.respawn_deleted_monks()
        self.engine.delete_resource(self.row, self.col)
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[engine.turn].undo_action()


class Teleport(RitualEvent):
    def __init__(self, engine, ritual_building, row, col, dest_row, dest_col):
        super().__init__(engine, ritual_building)
        self.row = row
        self.col = col
        self.dest_row = dest_row
        self.dest_col = dest_col

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

    def undo(self, engine):
        super().undo(engine)

        self.respawn_deleted_monks()
        self.engine.move(self.dest_row, self.dest_col, self.row, self.col)
        self.engine.get_occupying(self.row, self.col).actions_remaining = 1
        self.player.undo_ritual(self.ritual_cost)
        self.engine.reset_selected()
        self.engine.correct_interceptions()
        self.engine.reset_unused_piece_highlight()
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True
        self.engine.players[engine.turn].undo_action()


class Swap(RitualEvent):
    def __init__(self, engine, ritual_building, row, col, dest_row, dest_col):
        super().__init__(engine, ritual_building)
        self.row = row
        self.col = col
        self.dest_row = dest_row
        self.dest_col = dest_col
        self.first_actions = self.engine.get_occupying(row, col).actions_remaining
        self.second_actions = self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining

    def __repr__(self):
        return 'swap'

    def complete(self):
        super().complete()

        self.engine.swap(self.row, self.col, self.dest_row, self.dest_col)
        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = 0
        self.engine.get_occupying(self.row, self.col).actions_remaining = 0
        self.engine.intercept_pieces()
        self.player.do_action()
        self.player.do_ritual(self.ritual_cost)
        self.sacrifice_random_monks()

    def undo(self, engine):
        super().undo(engine)

        self.respawn_deleted_monks()
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
        self.engine.players[engine.turn].undo_action()


class LineDestroy(RitualEvent):
    def __init__(self, engine, ritual_building, row, col, selected_range):
        super().__init__(engine, ritual_building)
        self.row = row
        self.col = col
        self.selected_range = selected_range
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

    def undo(self, engine):
        super().undo(engine)
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
        self.engine.players[engine.turn].undo_action()


class Protect(RitualEvent):
    def __init__(self, engine, ritual_building, row, col):
        super().__init__(engine, ritual_building)
        self.row = row
        self.col = col

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

    def undo(self, engine):
        super().undo(engine)

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
        self.engine.players[engine.turn].undo_action()
