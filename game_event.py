from typing import Never, TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    from engine import Engine

from resource import *
from tile import Tile
from unit import *


def action_tile_has_effective_trap(
    acting_tile: "Tile", action_tile: "Tile"
) -> Optional["Trap"]:
    """
    Determines if an action tile has an effective trap from the perspective of an acting tile.

    :param acting_tile: The tile containing the color to check against.
    :param action_tile: The tile being checked for traps.

    :return: Optional[Trap]: The effective trap found, or None if no effective trap exists.

    """
    color = acting_tile.get_occupying().color
    trap = action_tile.trap

    is_protected = False

    if trap is not None:
        # Check if the trap's color doesn't match, and it protects against that color
        if (trap.color != color) and (
            action_tile.is_protected() and action_tile.protected_by == color
        ):
            is_protected = True

    return trap if not is_protected else None


class GameEvent:
    """
    Represents an event in a game context.

    This class models events that occur during gameplay, such as tile actions or moves.

    """

    def __init__(
        self,
        engine: "Engine",
        acting_tile: Optional["Tile"] = None,
        action_tile: Optional[
            Union["Tile", Tuple[Tuple[int, int], Tuple[int, int]]]
        ] = None,
    ):
        """
        Initializes a new GameEvent.

        :param engine: The game engine handling the event.
        :param acting_tile: The tile involved in the action (can be None).
        :param action_tile: The tile performing the action (can be None).
        """
        self.engine = engine
        self.acting_tile = acting_tile
        self.action_tile = action_tile

    def __repr__(self) -> Never:
        """
        Force subclasses to contain a __repr__ method.
        """
        raise NotImplementedError("Subclasses of GameEvent must implement __repr__")

    def set_king_in_check(self, is_player_checking: bool) -> bool:
        """
        Determines whether a king (either player's or enemy's) is in check.

        :param: is_player_checking (bool): If True, checks if the player's king is in check.
                                       If False, checks if the enemy's king is in check.

        :return: bool: True if the specified king is in check, False otherwise
        """
        # Update the possible moves for all pieces before checking for check.
        self.engine.update_squares()

        # Retrieve the player and enemy objects based on the current turn.
        try:
            player = self.engine.players[self.engine.get_turn()]
            enemy = self.engine.players[constant.TURNS[self.engine.get_turn()]]
        except KeyError:
            return False

        # Determine the attacking and defending sides based on is_player_checking flag.
        attacker, defender = (enemy, player) if is_player_checking else (player, enemy)

        try:
            # Iterate through each piece of the attacking side.
            for piece in attacker.pieces:
                # Skip pieces that are intercepted.
                if piece.intercepted:
                    continue

                # Check if the defender's king is in the attacking piece's capture squares.
                if defender.king.get_position() in piece.capture_squares_list:
                    # The king is in check.
                    defender.king.check = True
                    return True

            # If no attacking piece threatens the king, set check status to False.
            defender.king.check = False
            return False

        except Exception as e:
            # Catch and log any unexpected errors during execution.
            print(f"Error in set_king_in_check: {e}")
            return False

    def set_player_in_check(self) -> bool:
        """
        Determines if the current player's king is in check.

        :return: bool: True if the player's king is in check, False otherwise.
        """
        # Call the generic check function with is_player_checking set to True.
        return self.set_king_in_check(is_player_checking=True)

    def set_enemy_in_check(self) -> bool:
        """
        Determines if the enemy player's king is in check.

        :return: bool: True if the enemy's king is in check, False otherwise.
        """
        # Call the generic check function with is_player_checking set to False.
        return self.set_king_in_check(is_player_checking=False)

    def constrain_check(self):
        """
        Sloppy early implementation of check
        Undo when a move puts our king in check
        """
        if self.set_player_in_check():
            self.engine.events[-1].undo()
            self.set_player_in_check()
            del self.engine.events[-1]

    def complete(self):
        """
        Super method for completing an event.
        """
        self.engine.reset_selected()

    def undo(self):
        """
        Super method for undoing an event
        """
        pass

    def synchronize(self, engine: "Engine"):
        """
        Supports synchronizing randomized variables which occur as a result of any game event.
        This is called after the event is completed, only if the game is being played online.
        By default, this does nothing. It is assumed that the event itself will handle any synchronization.
        self.engine will be the serialized engine from the other computer. It will likely contain many values
        to update.

        :param engine: The game engine instance of the game running on this computer.
        """
        pass


class StartSpawn(GameEvent):
    """
    Represents the start of a spawning action in the game.
    """

    def __init__(self, engine, acting_tile, action_tile):
        """
        Initializes the StartSpawn event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the spawn action.
        :param action_tile: The tile where the spawn action occurs.
        """
        # Call the parent class constructor.
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color.
        self.color = self.engine.turn

        # Store the unit being spawned.
        self.spawn = self.engine.spawning

        # Store the destination position for the spawn.
        self.dest: Tuple[int, int] = self.action_tile.get_position()

        # Store the previously selected piece before spawning.
        self.previously_selected: Optional[Piece] = None

        # Store the current turn's player index.
        self.turn: str = self.engine.get_turn()

        # If there is an acting tile, store the piece occupying it.
        if acting_tile:
            self.previously_selected = self.acting_tile.get_occupying()

        # Store the current spawn count.
        self.spawn_count: int = self.engine.spawn_count

        # Store the final spawn flag.
        self.final_spawn: bool = self.engine.final_spawn

        # Store the list of all possible spawns.
        self.spawn_list = self.engine.spawn_list

        # Store the current game state.
        self.state = self.engine.state[-1]

    def __repr__(self) -> str:
        """
        Returns a string representation of the StartSpawn event.

        :return: A string representation of this event.
        """
        return "start spawn"

    def complete(self):
        """
        Completes the spawn action, placing the unit on the board and handling necessary updates.
        """
        # Call the parent class's complete method.
        super().complete()

        # Spawn the unit at the designated location.
        self.engine.spawn(self.dest[0], self.dest[1], self.spawn)

        # If the spawned unit is a king, update the king reference for the player.
        if self.spawn == "king":
            self.engine.players[self.turn].king = self.engine.get_occupying(
                self.dest[0], self.dest[1]
            )

        # Get the type of unit spawned.
        kind = self.engine.get_occupying(self.dest[0], self.dest[1]).unit_kind

        # Play the corresponding spawn sound effect.
        self.engine.sounds.play("spawn_" + kind)

        # Mark the spawn as successful.
        self.engine.spawnSuccess = True

        # Reset the spawning state.
        self.engine.spawning = None

    def undo(self):
        """
        Undoes the spawn action, reverting the game state to before the spawn occurred.
        """
        # Call the parent class's undo method.
        super().undo()

        # Get the type of unit that was spawned.
        kind = self.engine.get_occupying(self.dest[0], self.dest[1]).unit_kind

        # Play the corresponding undo spawn sound effect.
        self.engine.sounds.play("spawn_" + kind)

        # Remove the spawned unit from the board.
        self.engine.delete_piece(self.dest[0], self.dest[1])

        # Restore the previous spawn count.
        self.engine.spawn_count = self.spawn_count

        # Restore the turn order.
        self.engine.turn = self.turn

        # Restore the final spawn flag.
        self.engine.final_spawn = self.final_spawn

        # Restore the spawn list.
        self.engine.spawn_list = self.spawn_list

        # Restore the spawning unit.
        self.engine.spawning = self.engine.spawn_list[self.engine.spawn_count]

        # Reset any highlights related to unused pieces.
        self.engine.reset_unused_piece_highlight()

        # If there was a previously selected piece, restore its purchasing state.
        if self.previously_selected:
            self.previously_selected.purchasing = True

        # Restore the game state.
        self.engine.set_state(self.state)

        # Update the spawn-able squares on the board.
        self.engine.update_squares()

        # Reset the piece limit for the player whose turn it is.
        self.engine.players[self.engine.turn].reset_piece_limit()


class Steal(GameEvent):
    """
    Represents a stealing action in the game, where a unit takes resources from another.
    """

    def __init__(self, engine, acting_tile, action_tile):
        """
        Initializes the Steal event.

        :param engine: The game engine instance.
        :param acting_tile: The tile where the stealing unit is located.
        :param action_tile: The tile where the stolen resource is located.
        """
        # Call the parent class constructor.
        super().__init__(engine, acting_tile, action_tile)

        # Store the unit that is being stolen from.
        self.stolen_from: Optional[Piece] = self.action_tile.get_occupying()

        # Store the unit that is performing the theft.
        self.thief: Optional[Piece] = self.acting_tile.get_occupying()

        # Store the type of resource being stolen.
        self.resource_stolen: str = self.engine.stealing[0]

        # Store the amount of the resource being stolen.
        self.amount: int = self.engine.stealing[1]

    def __repr__(self) -> str:
        """
        Returns a string representation of the Steal event.

        :return: A string representing the event.
        """
        return "steal"

    def complete(self):
        """
        Completes the stealing action, deducting the resource from the victim
        and adding it to the thief's player.
        """
        # Call the parent class's complete method.
        super().complete()

        # Play the capture sound effect.
        self.engine.sounds.play("capture")

        # Reduce the thief's remaining actions by 1.
        self.thief.actions_remaining -= 1

        # Add the stolen resource to the thief's player.
        self.engine.players[self.engine.turn].steal(self.resource_stolen, self.amount)

        # Remove the stolen resource from the victim's player.
        self.engine.players[constant.TURNS[self.engine.turn]].invert_steal(
            self.resource_stolen, self.amount
        )

        # If stealing costs an action, mark it as used.
        if constant.STEALING_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        """
        Undoes the stealing action, returning resources to the original owner
        and resetting the game state.
        """
        # Call the parent class's undo method.
        super().undo()

        # Restore the thief's action since the steal is undone.
        self.thief.actions_remaining += 1

        # Play the capture sound effect again to indicate undoing the steal.
        self.engine.sounds.play("capture")

        # Restore the stolen resource to the victim.
        self.engine.players[self.engine.turn].invert_steal(
            self.resource_stolen, self.amount
        )

        # Remove the stolen resource from the thief's player.
        self.engine.players[constant.TURNS[self.engine.turn]].steal(
            self.resource_stolen, self.amount
        )

        # If stealing costs an action, undo the action usage.
        if constant.STEALING_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()

        # Count the number of unused pieces on the board.
        unused_pieces = self.engine.count_unused_pieces()

        # Reset any highlights related to unused pieces.
        self.engine.reset_unused_piece_highlight()

        # Restore the unused piece highlight for all unused pieces.
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Arm(GameEvent):
    """
    Represents an bomb arming action for the war tower to become ready to detonate.
    """

    def __init__(self, engine, acting_tile, action_tile):
        """
        Initializes the Arm event.

        :param engine: The game engine instance.
        :param acting_tile: The tile where the war tower is located.
        :param action_tile: The tile where the arming action occurs (not actively used).
        """
        # Call the parent class constructor.
        super().__init__(engine, acting_tile, action_tile)

        # Store the war tower that is being armed.
        self.war_tower: Optional[Piece] = self.acting_tile.get_occupying()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Arm event.

        :return: A string representing the event.
        """
        return "arm"

    def complete(self):
        """
        Completes the arming action, marking the war tower as ready to detonate.
        """
        # Call the parent class's complete method.
        super().complete()

        # Play the arming sound effect.
        self.engine.sounds.play("move")

        # Reduce the war tower's available actions by 1.
        self.war_tower.actions_remaining -= 1

        # Mark the war tower as armed.
        self.war_tower.armed = True

        # Perform player action for arming war tower
        self.engine.players[self.engine.turn].do_action()

    def undo(self):
        """
        Undoes the arming action, resetting the war tower's state.
        """
        # Call the parent class's undo method.
        super().undo()

        # Restore the war tower's available action.
        self.war_tower.actions_remaining += 1

        # Play the unarming sound effect.
        self.engine.sounds.play("move")

        # Mark the war tower as not armed.
        self.war_tower.armed = False

        # Count unused pieces to restore their highlights.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        # Restore highlights for all unused pieces.
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        #  cost an action, undo that action usage.
        self.engine.players[self.engine.turn].undo_action()


class Mine(GameEvent):
    """
    Represents a mining action where a unit extracts resources from a tile.
    """

    def __init__(self, engine, acting_tile, action_tile):
        """
        Initializes the Mine event.

        :param engine: The game engine instance.
        :param acting_tile: The tile where the miner is located.
        :param action_tile: The tile containing the resource to be mined.
        """
        # Call the parent class constructor.
        super().__init__(engine, acting_tile, action_tile)

        # Store the unit that is performing the mining.
        self.miner: Optional[Piece] = self.acting_tile.get_occupying()

        # Store the resource that is being mined.
        self.mined: Resource = self.action_tile.get_resource()

        # Track any additional mining yield, initially set to zero.
        self.additional_mining: int = 0

        # Store any piece that may be removed due to mining.
        self.piece_removed: Optional[Piece] = None

        # Store the harvested yield from mining.
        self.harvest_yield: Optional[int] = None

        # Store the player performing the mining action.
        self.player = self.engine.players[self.engine.turn]

        # Store sprite information for visual representation.
        self.sprite_id: int = self.mined.sprite_id
        self.sprite_offset: Tuple[int, int] = self.mined.sprite_offset

    def __repr__(self) -> str:
        """
        Returns a string representation of the Mine event.

        :return: A string representing the event.
        """
        return "mine"

    def complete(self):
        """
        Completes the mining action by extracting resources, updating game state,
        and playing sound effects.
        """
        # Call the parent class's complete method.
        super().complete()

        # Perform the mining action and store the harvest yield.
        self.harvest_yield = self.mined.harvest(str(self.miner))

        # Add the mined resources to the player's inventory.
        self.player.mine(str(self.mined), self.harvest_yield)

        # Reduce the miner's available actions by 1.
        self.miner.actions_remaining -= 1

        # Play the appropriate mining sound effect.
        kind = constant.RESOURCE_KEY[str(self.mined)]
        self.engine.sounds.play("mine_" + kind)

        # Check if the resource is fully depleted.
        if self.mined.remaining == 0:
            row, col = self.mined.row, self.mined.col

            # Handle different types of mining sites.
            if isinstance(self.mined, Quarry):
                # Replace Quarry with SunkenQuarry.
                self.engine.create_resource(row, col, SunkenQuarry(row, col))

                # If a piece was occupying the mined tile, remove it.
                occupying_piece = self.engine.get_occupying(row, col)
                if occupying_piece:
                    self.piece_removed = occupying_piece
                    self.engine.delete_piece(row, col)

            elif isinstance(self.mined, SunkenQuarry):
                # Replace SunkenQuarry with DepletedQuarry.
                self.engine.create_resource(row, col, DepletedQuarry(row, col))

            else:
                # Remove the depleted resource entirely.
                self.engine.delete_resource(row, col)

        # If mining costs an action, mark it as used.
        if constant.MINING_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        """
        Undoes the mining action, restoring resources and game state.
        """
        # Call the parent class's undo method.
        super().undo()

        # Restore the miner's action since the mining is undone.
        self.miner.actions_remaining += 1

        # Retrieve the mined resource's position.
        row, col = self.mined.row, self.mined.col

        # Restore the harvested resources to their original state.
        self.mined.undo_harvest(self.harvest_yield)

        # Remove the mined resources from the player's inventory.
        self.engine.players[self.engine.turn].un_mine(
            str(self.mined), self.harvest_yield
        )

        # Play the appropriate mining sound effect.
        kind = constant.RESOURCE_KEY[str(self.mined)]
        self.engine.sounds.play("mine_" + kind)

        # Restore the mined resource to the game board.
        self.engine.create_resource(row, col, self.mined)

        # If a piece was removed due to mining, restore it.
        if self.piece_removed:
            self.engine.create_piece(row, col, self.piece_removed)

        # Correct any interception issues caused by undoing mining.
        self.engine.correct_interceptions()

        # Count unused pieces to restore their highlights.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()

        # If mining originally cost an action, undo that action usage.
        if constant.MINING_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()

        # Restore highlights for all unused pieces.
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Pray(GameEvent):
    """
    Represents a prayer action where a unit prays on another unit to grant benefits.
    """

    def __init__(self, engine, acting_tile, action_tile):
        """
        Initializes the Pray event.

        :param engine: The game engine instance.
        :param acting_tile: The tile where the praying piece is located.
        :param action_tile: The tile containing the piece being prayed upon.
        """
        # Call the parent class constructor.
        super().__init__(engine, acting_tile, action_tile)

        # Store the unit performing the prayer.
        self.praying_piece: Optional[Piece] = self.acting_tile.get_occupying()

        # Store the unit that is being prayed upon.
        self.prayed_on: Optional[Building] = self.action_tile.get_occupying()

        # Store any additional prayer effects, initially set to zero.
        self.additional_prayer: int = 0

        # If the praying piece is a monk, apply additional prayer effects.
        if str(self.praying_piece) == "monk":
            self.additional_prayer = constant.ADDITIONAL_PRAYER_FROM_MONK

    def __repr__(self) -> str:
        """
        Returns a string representation of the Pray event.

        :return: A string representing the event.
        """
        return "pray"

    def complete(self):
        """
        Completes the prayer action, applying its effects and updating the game state.
        """
        # Call the parent class's complete method.
        super().complete()

        # Play the prayer sound effect.
        self.engine.sounds.play("pray")

        # Reduce the praying piece's available actions by 1.
        self.praying_piece.actions_remaining -= 1

        # Apply the prayer effect to the prayed-on piece.
        self.engine.players[self.engine.turn].pray(
            self.prayed_on, self.additional_prayer
        )

        # If praying costs an action, mark it as used.
        if constant.PRAYING_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        """
        Undoes the prayer action, reverting any effects and restoring game state.
        """
        # Call the parent class's undo method.
        super().undo()

        # Retrieve the praying piece's current position and reset actions.
        praying_piece = self.engine.get_occupying(
            self.praying_piece.row, self.praying_piece.col
        )
        praying_piece.actions_remaining += 1

        # Play the prayer sound effect.
        self.engine.sounds.play("pray")

        # Revert the prayer effect.
        self.engine.players[self.engine.turn].un_pray(
            self.prayed_on, self.additional_prayer
        )

        # If praying originally cost an action, undo that action usage.
        if constant.PRAYING_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()

        # Restore unused piece highlights.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Persuade(GameEvent):
    """
    Represents the persuade action, where one unit attempts to convert an enemy unit to its side.
    """

    def __init__(self, engine, acting_tile, action_tile):
        """
        Initializes the Persuade event.

        :param engine: The game engine instance.
        :param acting_tile: The tile containing the persuading unit.
        :param action_tile: The tile containing the unit being persuaded.
        """
        # Call the parent class constructor.
        super().__init__(engine, acting_tile, action_tile)

        # Store the persuading unit.
        self.persuader: Optional[Piece] = self.acting_tile.get_occupying()

        # Store the unit being persuaded.
        self.persuaded: Optional[Piece] = self.action_tile.get_occupying()

        # Store the persuaded unit's original action count.
        self.persuaded_actions: int = self.persuaded.actions_remaining

        # Store the persuaded unit's original color (team).
        self.persuaded_color: str = self.persuaded.color

    def __repr__(self) -> str:
        """
        Returns a string representation of the Persuade event.

        :return: A string representing the event.
        """
        return "persuade"

    def complete(self):
        """
        Completes the persuade action, converting the target unit to the persuader's team.
        """
        # Call the parent class's complete method.
        super().complete()

        # Reduce the persuader's available actions by 1.
        self.persuader.actions_remaining -= 1

        # Reduce the persuaded unit's available actions by 1.
        self.persuaded.actions_remaining -= 1

        # Remove the persuaded unit from its original player's pieces.
        self.engine.players[self.persuaded.color].pieces.remove(self.persuaded)

        # Add the persuaded unit to the persuader's player's pieces.
        self.engine.players[self.persuader.color].pieces.append(self.persuaded)

        # Change the persuaded unit's color to match the persuader's.
        self.persuaded.color = self.persuader.color

        # Reset any selected unit in the engine.
        self.engine.reset_selected()

        # Reset highlighting for unused pieces.
        self.engine.reset_unused_piece_highlight()

        # Update unit interactions after the persuasion.
        self.engine.intercept_pieces()
        self.engine.correct_interceptions()

        # Highlight all remaining unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # If persuasion costs an action, mark it as used.
        if constant.PERSUADE_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        """
        Undoes the persuade action, restoring the original state of the units.
        """
        # Call the parent class's undo method.
        super().undo()

        # Restore the persuader's available action.
        self.persuader.actions_remaining += 1

        # Restore the persuaded unit's original action count.
        self.persuaded.actions_remaining = self.persuaded_actions

        # Remove the persuaded unit from the new player's pieces.
        self.engine.players[self.persuader.color].pieces.remove(self.persuaded)

        # Restore the persuaded unit to its original player's pieces.
        self.engine.players[self.persuaded_color].pieces.append(self.persuaded)

        # Restore the persuaded unit's original color (team).
        self.persuaded.color = self.persuaded_color

        # Reset any selected unit in the engine.
        self.engine.reset_selected()

        # Reset highlighting for unused pieces.
        self.engine.reset_unused_piece_highlight()

        # Correct unit interactions after restoring state.
        self.engine.correct_interceptions()

        # Highlight all unused pieces except the one that was persuaded.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            if piece is not self.persuaded:
                piece.unused_piece_highlight = True

        # If persuasion originally cost an action, undo that action usage.
        if constant.PERSUADE_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()


class Decree(GameEvent):
    """
    Represents the Decree action, which allows a unit to issue a decree, altering game rules and consuming resources.
    """

    def __init__(self, engine, acting_tile, action_tile):
        """
        Initializes the Decree event.

        :param engine: The game engine instance.
        :param acting_tile: The tile containing the piece issuing the decree.
        :param action_tile: The target tile (not actively used in this event).
        """
        # Call the parent class constructor.
        super().__init__(engine, acting_tile, action_tile)

        # Store the piece issuing the decree.
        self.piece = self.acting_tile.get_occupying()

        # Store the current player issuing the decree.
        self.player = self.engine.players[self.engine.turn]

        # Get the decree cost from the engine.
        self.cost: int = self.engine.get_decree_cost()

        # Identify the resource type required to issue a decree.
        self.resource: str = list(constant.DECREE_COST.keys())[-1]

        # Track any disabled monoliths (if rituals get banned).
        self.disabled_monoliths: Optional[List] = None

    def __repr__(self) -> str:
        """
        Returns a string representation of the Mine event.

        :return: A string representing the event.
        """
        return "decree"

    def complete(self):
        """
        Completes the Decree action, consuming resources, altering rituals, and affecting monoliths.
        """
        # Call the parent class's complete method.
        super().complete()

        # Reduce the piece's available actions by 1.
        self.piece.actions_remaining -= 1

        # Deduct the decree cost from the player's resource pool.
        current_resource = getattr(self.player, self.resource)
        setattr(self.player, self.resource, current_resource - self.cost)

        # Increment the decree count in the engine.
        self.engine.decrees += 1

        # Toggle the ritual ban state.
        self.engine.rituals_banned = not self.engine.rituals_banned

        # Close any open menus in the game.
        self.engine.close_menus()

        # Reset the selected unit in the engine.
        self.engine.reset_selected()

        # Disable or enable monoliths based on the new ritual ban state.
        if self.engine.rituals_banned:
            self.disabled_monoliths = self.engine.disable_monoliths()
        else:
            self.engine.enable_monoliths()

        # Reset highlighting for unused pieces.
        self.engine.reset_unused_piece_highlight()

        # Highlight all remaining unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Mark an action as used.
        self.player.do_action()

    def undo(self):
        """
        Undoes the Decree action, restoring the previous game state.
        """
        # Call the parent class's undo method.
        super().undo()

        # Restore the piece's available action.
        self.piece.actions_remaining += 1

        # Refund the decree cost to the player's resource pool.
        current_resource = getattr(self.player, self.resource)
        setattr(self.player, self.resource, current_resource + self.cost)

        # Decrement the decree count in the engine.
        self.engine.decrees -= 1

        # Revert the ritual ban state.
        self.engine.rituals_banned = not self.engine.rituals_banned

        # Reset the selected unit in the engine.
        self.engine.reset_selected()

        # Disable or enable monoliths based on the restored ritual ban state.
        if self.engine.rituals_banned:
            self.disabled_monoliths = self.engine.disable_monoliths()
        else:
            self.engine.enable_monoliths()

        # Reset highlighting for unused pieces.
        self.engine.reset_unused_piece_highlight()

        # Highlight all remaining unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Undo the action usage.
        self.engine.players[self.engine.turn].undo_action()


class ChangeTurn(GameEvent):
    """
    Represents the event of changing turns in the game, handling all necessary state updates.
    """

    def __repr__(self) -> str:
        """Returns the string representation of the event."""
        return "change turn"

    def __init__(self, engine):
        """
        Initializes the ChangeTurn event, storing relevant state information before the turn change.

        :param engine: The game engine instance.
        """
        # Call the parent class constructor.
        super().__init__(engine)

        # Store the engine reference.
        self.engine = self.engine

        # Save the previously selected piece/tile before changing turn.
        self.prev = self.engine.update_previously_selected()

        # Save the current spawn success status.
        self.spawn_success = self.engine.spawn_success

        # Store the current open menus.
        self.menus = self.engine.menus

        # Store the current game state before turn change.
        self.state = self.engine.state[-1]

        # Store the list of pieces that have been used.
        self.used_pieces = self.engine.count_used_pieces()

        # Save whether a piece is currently in the process of spawning.
        self.spawning = self.engine.spawning

        # Store the current player's remaining actions.
        self.player_actions_remaining = self.engine.players[
            self.engine.turn
        ].get_actions_remaining()

        # Store the player's piece limit before the turn changes.
        self.player_piece_limit = self.engine.players[
            self.engine.turn
        ].get_piece_limit()

        # Store the player's prayer value before the turn changes.
        self.player_prayer = self.engine.players[self.engine.turn].get_prayer()

        # Store pieces that were used and intercepted.
        self.used_and_intercepted_pieces = self.engine.used_and_intercepted_pieces

        # Save the list of protected tiles.
        self.protected_tiles = self.engine.protected_tiles[:]

        # Save a list of squares that were destroyed by War Towers during the turn
        self.destroyed_squares: list[Tile] = None

        # save a list of pieces that were destroyed by war towers during this turn
        self.destroyed_pieces: list[Unit] = None

        # Save a list of destroyed portals during the turn end step
        self.destroyed_portals: list[tuple[Tile, Tile]] = []

    def complete(self):
        """
        Completes the turn change, resetting game state and advancing to the next player.
        """
        from engine import generate_available_rituals, generate_stealing_offsets

        # Call the parent class's complete method.
        super().complete()

        # Play the turn change sound.
        self.engine.sounds.play("change_turn")

        # Reset selected pieces and actions.
        self.engine.reset_selected()
        self.engine.reset_piece_actions_remaining()

        # Reset spawn success and game state attributes.
        self.engine.spawn_success = False
        self.engine.pieces_checking = []
        self.engine.pins = []
        self.engine.check = False
        self.engine.menus = []

        # Switch to the next player's turn.
        self.engine.turn = constant.TURNS[self.engine.turn]

        # Update the turn count displays.
        self.engine.turn_count_display += 0.5
        self.engine.turn_count_actual += 1

        # Reset intercepted and used pieces.
        self.engine.used_and_intercepted_pieces = []

        # Reset the new player's prayer.
        self.engine.players[self.engine.turn].reset_prayer()

        # Reset and update the player's action and piece limits.
        self.engine.reset_player_actions_remaining(self.engine.turn)
        self.engine.update_additional_actions()
        self.engine.reset_piece_limit(self.engine.turn)
        self.engine.update_piece_limit()

        # Handle intercepted pieces.
        self.engine.intercept_pieces()

        # Reset highlights for unused pieces.
        self.engine.reset_unused_piece_highlight()

        # Update side menu to show the correct icon
        if self.engine.get_current_state().side_bar:
            self.engine.get_current_state().side_bar.update_icon()

        # Disable monoliths if rituals are banned.
        if self.engine.rituals_banned:
            self.engine.disable_monoliths()

        # Update protected tiles.
        self.engine.tick_protected_tiles(self.engine.protected_tiles)

        self.destroyed_squares, self.destroyed_pieces = self.engine.tick_war_towers()

        for tile in self.destroyed_squares:
            if tile.portal:
                try:
                    self.destroyed_portals.append((tile, tile.connected_portal))
                    tile.connected_portal.portal = True
                    tile.connected_portal.connected_portal = None
                    tile.connected_portal = None
                except AttributeError:
                    self.destroyed_portals.append((tile, None))
                tile.portal = False

        # Debug mode: Always append the full ritual set.
        if constant.DEBUG_RITUALS:
            self.engine.monolith_rituals.append(constant.MONOLITH_RITUALS)
            self.engine.prayer_stone_rituals.append(constant.PRAYER_STONE_RITUALS)
            self.engine.magician_rituals.append(constant.MAGICIAN_RITUALS)
        else:
            # Generate new available rituals for each category if needed.
            if self.engine.turn_count_actual == len(self.engine.monolith_rituals) - 1:
                self.engine.monolith_rituals.append(
                    generate_available_rituals(
                        constant.MONOLITH_RITUALS,
                        constant.MAX_MONOLITH_RITUALS_PER_TURN,
                    )
                )
            if (
                self.engine.turn_count_actual
                == len(self.engine.prayer_stone_rituals) - 1
            ):
                self.engine.prayer_stone_rituals.append(
                    generate_available_rituals(
                        constant.PRAYER_STONE_RITUALS,
                        constant.MAX_PRAYER_STONE_RITUALS_PER_TURN,
                    )
                )
            if self.engine.turn_count_actual == len(self.engine.magician_rituals) - 1:
                self.engine.magician_rituals.append(
                    generate_available_rituals(
                        constant.MAGICIAN_RITUALS,
                        constant.MAX_MAGICIAN_RITUALS_PER_TURN,
                    )
                )

        # Generate trade and stealing offsets if needed.
        if self.engine.turn_count_actual == len(self.engine.trade_conversions) - 1:
            self.engine.trade_conversions.append(
                self.engine.trade_handler.get_conversions()
            )

        if self.engine.turn_count_actual == len(self.engine.piece_stealing_offsets) - 1:
            self.engine.piece_stealing_offsets.append(
                generate_stealing_offsets(constant.STEALING_KEY["piece"])
            )
        if (
            self.engine.turn_count_actual
            == len(self.engine.building_stealing_offsets) - 1
        ):
            self.engine.building_stealing_offsets.append(
                generate_stealing_offsets(constant.STEALING_KEY["building"])
            )
        if (
            self.engine.turn_count_actual
            == len(self.engine.trader_stealing_offsets) - 1
        ):
            self.engine.trader_stealing_offsets.append(
                generate_stealing_offsets(constant.STEALING_KEY["trader"])
            )
        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Check if the current player is in check.
        self.set_player_in_check()

        if self.engine.turn_count_actual != 0:
            self.engine.set_winner()

    def undo(self):
        """
        Undoes the turn change, restoring the previous game state.
        """
        # Play the turn change sound.
        self.engine.sounds.play("change_turn")

        self.engine.un_tick_war_towers(self.destroyed_squares, self.destroyed_pieces)

        # Revert to the previous player's turn.
        self.engine.turn = constant.TURNS[self.engine.turn]

        # Update turn counters.
        self.engine.turn_count_display -= 0.5
        self.engine.turn_count_actual -= 1

        # Restore previous game state variables.
        self.engine.menus = self.menus
        self.engine.spawn_success = self.spawn_success
        self.engine.spawning = self.spawning

        # Restore the game state.
        self.engine.set_state(str(self.state))

        # Restore used and intercepted pieces.
        self.engine.used_and_intercepted_pieces = self.used_and_intercepted_pieces

        # Reset used pieces' actions.
        for used_piece in self.used_pieces:
            used_piece.actions_remaining = 0

        # Update side menu to show the correct icon
        if self.engine.get_current_state().side_bar:
            self.engine.get_current_state().side_bar.update_icon()

        # Reset unused piece highlights.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()

        # Disable monoliths if rituals are still banned.
        if self.engine.rituals_banned:
            self.engine.disable_monoliths()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight unused pieces again.
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Restore player's actions, piece limits, and prayer values.
        self.engine.players[self.engine.turn].set_actions_remaining(
            self.player_actions_remaining
        )
        self.engine.players[self.engine.turn].set_piece_limit(self.player_piece_limit)
        self.engine.players[self.engine.turn].set_prayer(self.player_prayer)

        # Restore protected tiles and undo their protection effects.
        self.engine.protected_tiles = self.protected_tiles
        self.engine.un_tick_protected_tiles(self.protected_tiles)

        for tile, connected_portal in self.destroyed_portals:
            tile.portal = True
            tile.connected_portal = connected_portal
            if tile.connected_portal:
                tile.connected_portal.portal = True
                tile.connected_portal.connected_portal = tile

        # Restore the board state for protected tiles.
        for tile in self.protected_tiles:
            self.engine.board[tile.row][tile.col] = tile


class SpawnResource(GameEvent):
    """
    Represents the action of spawning a resource in the game.
    This event handles creating a resource, deducting costs, and updating game state.
    """

    def __init__(self, engine, acting_tile, action_tile):
        """
        Initializes the SpawnResource event, storing relevant state information.

        :param engine: The game engine instance.
        :param acting_tile: The tile where the spawning action is performed.
        :param action_tile: The tile where the resource will be spawned.
        """
        # Call the parent class constructor with required parameters.
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color (turn).
        self.color = self.engine.turn

        # Store the resource type being spawned.
        self.spawn = self.engine.spawning

        # Store the destination coordinates for the new resource.
        self.dest: Tuple[int, int] = self.action_tile.get_position()

        # Store the entity responsible for spawning.
        self.spawner = self.acting_tile.get_occupying()

    def __repr__(self) -> str:
        """
        Returns the string representation of the event.

        :return: A string describing the event.
        """
        return "spawn resource"

    def complete(self):
        """
        Completes the resource spawn event by creating the resource, updating costs, and modifying game state.
        """
        # Call the parent class's complete method.
        super().complete()

        # Create the resource object at the destination.
        resource = self.engine.RESOURCES[self.spawn](self.dest[0], self.dest[1])

        # Add the resource to the game engine.
        self.engine.create_resource(self.dest[0], self.dest[1], resource)

        # Play the resource mining sound effect.
        self.engine.sounds.play("mine_stone")

        # Reduce the spawner's remaining actions.
        self.spawner.actions_remaining -= 1

        # Mark the spawning action as successful.
        self.engine.spawn_success = True

        # Clear any active menus.
        self.engine.menus = []

        # Reset selected piece/tile.
        self.engine.reset_selected()

        # Deduct an action from the player if quarrying costs an action.
        if constant.QUARRY_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

    def undo(self):
        """
        Undoes the resource spawn event, restoring the previous game state.
        """
        # Call the parent class's undo method.
        super().undo()

        # Restore the spawner's remaining actions.
        self.spawner.actions_remaining += 1

        # Play the resource mining sound effect again.
        self.engine.sounds.play("mine_stone")

        # Remove the resource from the game engine.
        self.engine.delete_resource(self.dest[0], self.dest[1])

        # Get the list of unused pieces.
        unused_pieces = self.engine.count_unused_pieces()

        # Reset unused piece highlighting.
        self.engine.reset_unused_piece_highlight()

        # Restore the player's action if it was deducted.
        if constant.QUARRY_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()

        # Reapply highlighting to all unused pieces.
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class PortalSpawn(GameEvent):
    """
    This represents the event of spawning a unit at a portal, handling all necessary updates.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the PortalSpawn event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the spawn action.
        :param action_tile: The tile where the spawn action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color.
        self.color = self.engine.turn

        # Store the unit being spawned.
        self.spawn = self.engine.spawning

        # Store the destination position for the spawn.
        self.dest = self.action_tile.get_position()

        # Store the position of the connected portal.
        self.portal_end = self.action_tile.connected_portal.get_position()

        # Store the trap at the portal end position.
        self.trap = self.engine.board[self.portal_end[0]][self.portal_end[1]].trap

        # Store the tile at the portal end position.
        self.trapped_tile = self.engine.board[self.portal_end[0]][self.portal_end[1]]

        # Initialize protection status.
        self.is_protected = False

        # Check if the trapped tile is protected by the current player.
        if (
            self.trapped_tile.is_protected()
            and self.trapped_tile.protected_by == self.color
        ):
            self.is_protected = True

        # Nullify the trap if it belongs to the current player or the tile is protected.
        if self.trap is not None and (
            self.trap.color == self.color or self.is_protected
        ):
            self.trap = None

        # Initialize the deleted piece.
        self.deleted_piece = None

        # Store the piece occupying the acting tile.
        self.spawner = self.acting_tile.get_occupying()

        # Initialize additional piece limit and actions.
        self.additional_piece_limit = 0
        self.additional_actions = 0

        # Store the cost of the piece being spawned.
        self.piece_cost = engine.PIECE_COSTS[self.engine.spawning]

    def __repr__(self) -> str:
        """
        Returns a string representation of the PortalSpawn event.

        :return: A string representation of this event.
        """
        return "spawn"

    def complete(self):
        """
        Completes the spawn action, placing the unit on the board and handling necessary updates.
        """
        super().complete()

        # Spawn the unit at the designated location.
        self.engine.spawn(self.dest[0], self.dest[1], self.spawn)

        # Reduce the spawner's remaining actions by 1.
        self.spawner.actions_remaining -= 1

        # Mark the spawn as successful.
        self.engine.spawn_success = True

        # Clear any active menus.
        self.engine.menus = []

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Deduct an action from the player.
        self.engine.players[self.engine.turn].do_action()

        # Deduct the cost of the piece from the player's resources.
        self.engine.players[self.engine.turn].purchase(self.piece_cost)

        # Update additional actions if applicable.
        if constant.ACTIONS_UPDATE_ON_SPAWN:
            self.additional_actions = self.engine.get_occupying(
                self.dest[0], self.dest[1]
            ).get_additional_actions()
            self.engine.players[self.engine.turn].add_additional_actions(
                self.additional_actions
            )

        # Update additional piece limit.
        self.additional_piece_limit = self.engine.get_occupying(
            self.dest[0], self.dest[1]
        ).get_additional_piece_limit()

        # Play the spawn sound effect.
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().unit_kind
        self.engine.sounds.play("spawn_" + kind)

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Add additional piece limit to the player.
        self.engine.players[self.engine.turn].add_additional_piece_limit(
            self.additional_piece_limit
        )

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Swap the pieces at the destination and portal end positions.
        self.engine.swap(
            self.dest[0], self.dest[1], self.portal_end[0], self.portal_end[1]
        )

        # Handle the trap if it exists.
        if self.trap:
            self.deleted_piece = self.engine.get_occupying(
                self.portal_end[0], self.portal_end[1]
            )
            self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
            self.engine.un_trap(self.portal_end[0], self.portal_end[1])

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        """
        Undoes the spawn action, reverting the game state to before the spawn occurred.
        """
        super().undo()

        # Restore the spawner's remaining actions.
        self.spawner.actions_remaining += 1

        # Restore the deleted piece if it exists.
        if self.deleted_piece:
            self.engine.create_piece(
                self.portal_end[0], self.portal_end[1], self.deleted_piece
            )
            self.engine.set_trap(self.portal_end[0], self.portal_end[1], self.trap)

        # Swap the pieces back to their original positions.
        self.engine.swap(
            self.portal_end[0], self.portal_end[1], self.dest[0], self.dest[1]
        )

        # Play the spawn sound effect.
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().unit_kind
        self.engine.sounds.play("spawn_" + kind)

        # Refund the cost of the piece to the player.
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)

        # Remove the spawned piece from the board.
        self.engine.delete_piece(self.dest[0], self.dest[1])

        # Undo the action deduction.
        self.engine.players[self.engine.turn].undo_action()

        # Remove additional actions if applicable.
        if constant.ACTIONS_UPDATE_ON_SPAWN:
            self.engine.players[self.engine.turn].remove_additional_actions(
                self.additional_actions
            )

        # Remove additional piece limit from the player.
        self.engine.players[self.engine.turn].remove_additional_piece_limit(
            self.additional_piece_limit
        )

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class SpawnTrap(GameEvent):
    """
    Represents the event of spawning a trap on the game board.

    This event handles creating a trap, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the SpawnTrap event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the spawn action.
        :param action_tile: The tile where the trap will be spawned.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color.
        self.color = self.engine.turn

        # Store the unit being spawned.
        self.spawn = self.engine.spawning

        # Store the destination position for the spawn.
        self.dest = self.action_tile.get_position()

        # Store the piece occupying the acting tile.
        self.spawner = self.acting_tile.get_occupying()

        # Store the cost of the piece being spawned.
        self.piece_cost = engine.PIECE_COSTS[self.engine.spawning]

    def __repr__(self) -> str:
        """
        Returns a string representation of the SpawnTrap event.

        :return: A string representation of this event.
        """
        return "trap"

    def complete(self):
        """
        Completes the trap spawn action, placing the trap on the board and handling necessary updates.
        """
        super().complete()

        # Set the trap at the designated location.
        self.engine.set_trap(
            self.dest[0],
            self.dest[1],
            self.engine.PIECES["trap"](self.dest[0], self.dest[1], self.color),
        )

        # Play the spawn building sound effect.
        self.engine.sounds.play("spawn_building")

        # Reduce the spawner's remaining actions by 1.
        self.spawner.actions_remaining -= 1

        # Mark the spawn as successful.
        self.engine.spawn_success = True

        # Clear any active menus.
        self.engine.menus = []

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Deduct an action from the player if trap costs an action.
        if constant.TRAP_COSTS_ACTION:
            self.engine.players[self.engine.turn].do_action()

        # Deduct the cost of the piece from the player's resources.
        self.engine.players[self.engine.turn].purchase(self.piece_cost)

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        """
        Undoes the trap spawn action, reverting the game state to before the spawn occurred.
        """
        super().undo()

        # Restore the spawner's remaining actions.
        self.spawner.actions_remaining += 1

        # Play the spawn building sound effect.
        self.engine.sounds.play("spawn_building")

        # Refund the cost of the piece to the player.
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)

        # Remove the trap from the board.
        self.engine.un_trap(self.dest[0], self.dest[1])

        # Undo the action deduction if trap costs an action.
        if constant.TRAP_COSTS_ACTION:
            self.engine.players[self.engine.turn].undo_action()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class TrapSpawn(GameEvent):
    """
    Represents the event of spawning a piece onto a trap on the game board.

    This event handles creating a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the TrapSpawn event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the spawn action.
        :param action_tile: The tile where the piece will be spawned.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color.
        self.color = self.engine.turn

        # Store the unit being spawned.
        self.spawn = self.engine.spawning

        # Store the destination position for the spawn.
        self.dest = self.action_tile.get_position()

        # Store the piece occupying the acting tile.
        self.spawner = self.acting_tile.get_occupying()

        # Initialize additional piece limit and actions.
        self.additional_piece_limit = 0
        self.additional_actions = 0

        # Store the cost of the piece being spawned.
        self.piece_cost = engine.PIECE_COSTS[self.engine.spawning]

        # Store the trap at the action tile.
        self.trap = action_tile.trap

        # Initialize protection status.
        self.is_protected = False

        # Check if the action tile is protected by the current player.
        if (
            self.action_tile.is_protected()
            and self.action_tile.protected_by == self.color
        ):
            self.is_protected = True

    def __repr__(self) -> str:
        """
        Returns a string representation of the TrapSpawn event.

        :return: A string representation of this event.
        """
        return "spawn"

    def complete(self):
        """
        Completes the spawn action, placing the unit on the board and handling necessary updates.
        """
        super().complete()

        # Spawn the unit at the designated location.
        self.engine.spawn(self.dest[0], self.dest[1], self.spawn)

        # Get the type of unit spawned.
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().unit_kind

        # Play the corresponding spawn sound effect.
        self.engine.sounds.play("spawn_" + kind)

        # Deduct an action from the player if the spawned unit is not a trap.
        if self.spawn != "trap":
            self.engine.players[self.engine.turn].do_action()

        # Reduce the spawner's remaining actions by 1.
        self.spawner.actions_remaining -= 1

        # Mark the spawn as successful.
        self.engine.spawn_success = True

        # Clear any active menus.
        self.engine.menus = []

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Deduct the cost of the piece from the player's resources.
        self.engine.players[self.engine.turn].purchase(self.piece_cost)

        # If the tile is not protected, remove the trap and delete the piece.
        if not self.is_protected:
            self.engine.un_trap(self.dest[0], self.dest[1])
            self.engine.delete_piece(self.dest[0], self.dest[1])

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        """
        Undoes the spawn action, reverting the game state to before the spawn occurred.
        """
        super().undo()

        # Restore the spawner's remaining actions.
        self.spawner.actions_remaining += 1

        # Refund the cost of the piece to the player.
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)

        # Undo the action deduction if the spawned unit is not a trap.
        if self.spawn != "trap":
            self.engine.players[self.engine.turn].undo_action()

        # If the tile is not protected, restore the trap.
        if not self.is_protected:
            self.engine.set_trap(self.dest[0], self.dest[1], self.trap)

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Spawn(GameEvent):
    """
    Represents the event of spawning a piece on the game board.

    This event handles creating a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the Spawn event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the spawn action.
        :param action_tile: The tile where the piece will be spawned.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color.
        self.color = self.engine.turn

        # Store the unit being spawned.
        self.spawn = self.engine.spawning

        # Store the destination position for the spawn.
        self.dest = self.action_tile.get_position()

        # Store the piece occupying the acting tile.
        self.spawner = self.acting_tile.get_occupying()

        # Initialize additional piece limit and actions.
        self.additional_piece_limit = 0
        self.additional_actions = 0

        # Store the cost of the piece being spawned.
        self.piece_cost = engine.PIECE_COSTS[self.engine.spawning]

    def __repr__(self) -> str:
        """
        Returns a string representation of the Spawn event.

        :return: A string representation of this event.
        """
        return "spawn"

    def complete(self):
        """
        Completes the spawn action, placing the unit on the board and handling necessary updates.
        """
        super().complete()

        # Spawn the unit at the designated location.
        self.engine.spawn(self.dest[0], self.dest[1], self.spawn)

        # Get the type of unit spawned.
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().unit_kind

        # Play the corresponding spawn sound effect.
        self.engine.sounds.play("spawn_" + kind)

        # Reduce the spawner's remaining actions by 1.
        self.spawner.actions_remaining -= 1

        # Mark the spawn as successful.
        self.engine.spawn_success = True

        # Clear any active menus.
        self.engine.menus = []

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Deduct an action from the player if the spawned unit is not a trap.
        if self.spawn != "trap":
            self.engine.players[self.engine.turn].do_action()

        # Deduct the cost of the piece from the player's resources.
        self.engine.players[self.engine.turn].purchase(self.piece_cost)

        # Update additional actions if applicable.
        if constant.ACTIONS_UPDATE_ON_SPAWN:
            self.additional_actions = self.engine.get_occupying(
                self.dest[0], self.dest[1]
            ).get_additional_actions()
            self.engine.players[self.engine.turn].add_additional_actions(
                self.additional_actions
            )

        # Update additional piece limit.
        self.additional_piece_limit = self.engine.get_occupying(
            self.dest[0], self.dest[1]
        ).get_additional_piece_limit()
        self.engine.players[self.engine.turn].add_additional_piece_limit(
            self.additional_piece_limit
        )

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        """
        Undoes the spawn action, reverting the game state to before the spawn occurred.
        """
        super().undo()

        # Restore the spawner's remaining actions.
        self.spawner.actions_remaining += 1

        # Get the type of unit spawned.
        kind = self.engine.board[self.dest[0]][self.dest[1]].get_occupying().unit_kind

        # Play the corresponding spawn sound effect.
        self.engine.sounds.play("spawn_" + kind)

        # Refund the cost of the piece to the player.
        self.engine.players[self.engine.turn].un_purchase(self.piece_cost)

        # Remove the spawned piece from the board.
        self.engine.delete_piece(self.dest[0], self.dest[1])

        # Undo the action deduction if the spawned unit is not a trap.
        if self.spawn != "trap":
            self.engine.players[self.engine.turn].undo_action()

        # Remove additional actions if applicable.
        if constant.ACTIONS_UPDATE_ON_SPAWN:
            self.engine.players[self.engine.turn].remove_additional_actions(
                self.additional_actions
            )

        # Remove additional piece limit from the player.
        self.engine.players[self.engine.turn].remove_additional_piece_limit(
            self.additional_piece_limit
        )

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Upgrade(GameEvent):
    """
    Represents the event of upgrading a piece on the game board.

    This event handles creating a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the Spawn event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the spawn action.
        :param action_tile: The tile where the piece will be spawned.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color.
        self.color = self.engine.turn

        # Store the piece occupying the acting tile.
        self.spawner = self.acting_tile.get_occupying()

        # Initialize additional piece limit and actions.
        self.additional_piece_limit = 0
        self.additional_actions = 0

        # Store the cost of the piece being spawned.
        self.cost = self.engine.upgrades.upgrade_costs[str(self.spawner)][
            self.spawner.rank + 1
        ]

        # If this flag is true, replace upgrade contextual option when undoing
        self.replace_upgrade = False

    def __repr__(self) -> str:
        """
        Returns a string representation of the Upgrade event.

        :return: A string representation of this event.
        """
        return "upgrade"

    def complete(self):
        """
        Completes the upgrade action, placing the unit on the board and handling necessary updates.
        """
        super().complete()
        self.engine.players[self.engine.turn].remove_additional_piece_limit(
            self.spawner.get_additional_piece_limit()
        )

        # Spawn the unit at the designated location.
        self.spawner.upgrade()

        # Get the type of unit spawned.
        kind = self.spawner.unit_kind

        # Play the corresponding spawn sound effect.
        self.engine.sounds.play("spawn_" + kind)

        # Reduce the spawner's remaining actions by 1.
        self.spawner.actions_remaining -= 1

        # Mark the spawn as successful.
        self.engine.spawn_success = True

        # Clear any active menus.
        self.engine.menus = []

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Deduct the cost of the piece from the player's resources.
        self.engine.players[self.engine.turn].purchase(self.cost)

        # Perform the action, subtracting one from the players total turn actions.
        self.engine.players[self.engine.turn].do_action()

        # Update additional piece limit.
        self.additional_piece_limit = self.spawner.get_additional_piece_limit()
        self.engine.players[self.engine.turn].add_additional_piece_limit(
            self.additional_piece_limit
        )

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        if self.engine.is_max_upgrade(self.spawner):
            self.spawner.contextual_options.remove("purchase")
            self.replace_upgrade = True

    def undo(self):
        """
        Undoes the spawn action, reverting the game state to before the spawn occurred.
        """
        super().undo()
        # Remove additional piece limit from the player.
        self.engine.players[self.engine.turn].remove_additional_piece_limit(
            self.additional_piece_limit
        )
        # Restore the spawner's remaining actions.
        self.spawner.actions_remaining += 1

        # Get the type of unit spawned.
        kind = self.spawner.unit_kind

        # Play the corresponding spawn sound effect.
        self.engine.sounds.play("spawn_" + kind)

        # Refund the cost of the piece to the player.
        self.engine.players[self.engine.turn].un_purchase(self.cost)

        # Remove the spawned piece from the board.
        self.spawner.demote()

        # Undo the action deduction.
        self.engine.players[self.engine.turn].undo_action()

        self.additional_piece_limit = self.spawner.get_additional_piece_limit()
        self.engine.players[self.engine.turn].add_additional_piece_limit(
            self.additional_piece_limit
        )

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Replace upgrade functionality if piece was at max upgrade level.
        if self.replace_upgrade:
            self.spawner.contextual_options.append("purchase")
            self.replace_upgrade = False


class PortalMove(GameEvent):
    """
    Represents the event of moving a piece through a portal on the game board.

    This event handles moving a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the PortalMove event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the move action.
        :param action_tile: The tile where the move action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color.
        self.color = self.engine.turn

        # Store the piece being moved.
        self.moved = self.acting_tile.get_occupying()

        # Store whether this is the piece's first move.
        self.first_move = self.moved.first_move

        # Store the starting position of the move.
        self.start = self.moved.row, self.moved.col

        # Store the ending position of the move.
        self.end = self.action_tile.row, self.action_tile.col

        # Store the position of the connected portal.
        self.portal_end = self.action_tile.connected_portal.get_position()

        # Store the trap at the portal end position.
        self.trap = self.engine.board[self.portal_end[0]][self.portal_end[1]].trap

        # Store the tile at the portal end position.
        self.trapped_tile = self.engine.board[self.portal_end[0]][self.portal_end[1]]

        # Initialize protection status.
        self.is_protected = False

        # Check if the trapped tile is protected by the current player.
        if (
            self.trapped_tile.is_protected()
            and self.trapped_tile.protected_by == self.color
        ):
            self.is_protected = True

        # Nullify the trap if it belongs to the current player or the tile is protected.
        if self.trap is not None and (
            self.trap.color == self.color or self.is_protected
        ):
            self.trap = None

        # Initialize the deleted piece.
        self.deleted_piece = None

    def __repr__(self) -> str:
        """
        Returns a string representation of the PortalMove event.

        :return: A string representation of this event.
        """
        return "portal move"

    def complete(self):
        """
        Completes the move action, updating the game state accordingly.
        """
        super().complete()

        # Reduce the moved piece's remaining actions by 1.
        self.moved.actions_remaining -= 1

        # Mark the piece's first move as completed.
        self.moved.first_move = False

        # Move the piece to the new position.
        self.engine.move(self.start[0], self.start[1], self.end[0], self.end[1])

        # Swap the pieces at the destination and portal end positions.
        self.engine.swap(
            self.end[0], self.end[1], self.portal_end[0], self.portal_end[1]
        )

        # Handle the trap if it exists.
        if self.trap:
            self.deleted_piece = self.engine.get_occupying(
                self.portal_end[0], self.portal_end[1]
            )
            self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
            self.engine.un_trap(self.portal_end[0], self.portal_end[1])

        # Play the move sound effect.
        self.engine.sounds.play("move")

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Mark an action as used.
        self.engine.players[self.engine.turn].do_action()

    def undo(self):
        """
        Undoes the move action, restoring the game state to before the move occurred.
        """
        super().undo()

        # Restore the moved piece's remaining actions.
        self.moved.actions_remaining += 1

        # Restore the piece's first move status.
        self.moved.first_move = self.first_move

        # Restore the deleted piece if it exists.
        if self.deleted_piece:
            self.engine.create_piece(
                self.portal_end[0], self.portal_end[1], self.deleted_piece
            )
            self.engine.set_trap(self.portal_end[0], self.portal_end[1], self.trap)

        # Swap the pieces back to their original positions.
        self.engine.swap(
            self.portal_end[0], self.portal_end[1], self.end[0], self.end[1]
        )

        # Move the piece back to the starting position.
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])

        # Play the move sound effect.
        self.engine.sounds.play("move")

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Undo the action usage.
        self.engine.players[self.engine.turn].undo_action()


class PortalCapture(GameEvent):
    """
    Represents the event of capturing a piece through a portal on the game board.

    This event handles capturing a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the PortalCapture event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the capture action.
        :param action_tile: The tile where the capture action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color.
        self.color = self.engine.turn

        # Store the piece being moved.
        self.moved = self.acting_tile.get_occupying()

        # Store whether this is the piece's first move.
        self.first_move = self.moved.first_move

        # Store the starting position of the move.
        self.start = self.moved.row, self.moved.col

        # Store the ending position of the move.
        self.end = self.action_tile.get_position()

        # Store the position of the connected portal.
        self.portal_end = self.action_tile.connected_portal.get_position()

        # Store the piece being captured.
        self.captured = self.action_tile.get_occupying()

        # Store the trap at the portal end position.
        self.trap = self.engine.board[self.portal_end[0]][self.portal_end[1]].trap

        # Store the tile at the portal end position.
        self.trapped_tile = self.engine.board[self.portal_end[0]][self.portal_end[1]]

        # Initialize protection status.
        self.is_protected = False

        # Check if the trapped tile is protected by the current player.
        if (
            self.trapped_tile.is_protected()
            and self.trapped_tile.protected_by == self.color
        ):
            self.is_protected = True

        # Nullify the trap if it belongs to the current player or the tile is protected.
        if self.trap is not None and (
            self.trap.color == self.color or self.is_protected
        ):
            self.trap = None

        # Initialize the deleted piece.
        self.deleted_piece = None

    def __repr__(self) -> str:
        """
        Returns a string representation of the PortalCapture event.

        :return: A string representation of this event.
        """
        return "portal capture"

    def complete(self):
        """
        Completes the capture action, updating the game state accordingly.
        """
        super().complete()

        # Reduce the moved piece's remaining actions by 1.
        self.moved.actions_remaining -= 1

        # Mark the piece's first move as completed.
        self.moved.first_move = False

        # Play the capture sound effect.
        self.engine.sounds.play("capture")

        # Capture the piece at the destination.
        self.engine.capture(self.start[0], self.start[1], self.end[0], self.end[1])

        # Swap the pieces at the destination and portal end positions.
        self.engine.swap(
            self.end[0], self.end[1], self.portal_end[0], self.portal_end[1]
        )

        # Handle the trap if it exists.
        if self.trap:
            self.deleted_piece = self.engine.get_occupying(
                self.portal_end[0], self.portal_end[1]
            )
            self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
            self.engine.un_trap(self.portal_end[0], self.portal_end[1])

        # Mark an action as used.
        self.engine.players[self.engine.turn].do_action()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        """
        Undoes the capture action, restoring the game state to before the capture occurred.
        """
        super().undo()

        # Restore the moved piece's remaining actions.
        self.moved.actions_remaining += 1

        # Restore the piece's first move status.
        self.moved.first_move = self.first_move

        # Restore the deleted piece if it exists.
        if self.deleted_piece:
            self.engine.create_piece(
                self.portal_end[0], self.portal_end[1], self.deleted_piece
            )
            self.engine.set_trap(self.portal_end[0], self.portal_end[1], self.trap)

        # Play the capture sound effect.
        self.engine.sounds.play("capture")

        # Swap the pieces back to their original positions.
        self.engine.swap(
            self.portal_end[0], self.portal_end[1], self.end[0], self.end[1]
        )

        # Move the piece back to the starting position.
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])

        # Restore the captured piece.
        self.engine.create_piece(self.end[0], self.end[1], self.captured)

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Undo the action usage.
        self.engine.players[self.engine.turn].undo_action()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class TrapMove(GameEvent):
    """
    Represents the event of moving a piece onto a trap on the game board.

    This event handles moving a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the TrapMove event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the move action.
        :param action_tile: The tile where the move action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the piece being moved.
        self.moved = self.acting_tile.get_occupying()

        # Store whether this is the piece's first move.
        self.first_move = self.moved.first_move

        # Store the color of the piece being moved.
        self.color = self.moved.color

        # Store the starting position of the move.
        self.start = self.moved.row, self.moved.col

        # Store the ending position of the move.
        self.end = self.action_tile.get_position()

        # Store the trap at the action tile.
        self.trap = self.action_tile.trap

        # Initialize protection status.
        self.is_protected = False

        # Check if the action tile is protected by the current player.
        if (
            self.action_tile.is_protected
            and self.action_tile.protected_by == self.color
        ):
            self.is_protected = True

    def __repr__(self) -> str:
        """
        Returns a string representation of the TrapMove event.

        :return: A string representation of this event.
        """
        return "trap move"

    def complete(self):
        """
        Completes the move action, updating the game state accordingly.
        """
        super().complete()

        # Reduce the moved piece's remaining actions by 1.
        self.moved.actions_remaining -= 1

        # Mark the piece's first move as completed.
        self.moved.first_move = False

        # Move the piece to the new position.
        self.engine.move(self.start[0], self.start[1], self.end[0], self.end[1])

        # Remove the trap at the destination position.
        self.engine.un_trap(self.end[0], self.end[1])

        # Delete the piece at the destination position.
        self.engine.delete_piece(self.end[0], self.end[1])

        # Play the capture sound effect.
        self.engine.sounds.play("capture")

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Mark an action as used.
        self.engine.players[self.engine.turn].do_action()

    def undo(self):
        """
        Undoes the move action, restoring the game state to before the move occurred.
        """
        super().undo()

        # Restore the moved piece's remaining actions.
        self.moved.actions_remaining += 1

        # Restore the piece's first move status.
        self.moved.first_move = self.first_move

        # Create the piece at the destination position.
        self.engine.create_piece(self.end[0], self.end[1], self.moved)

        # Set the trap at the destination position.
        self.engine.set_trap(self.end[0], self.end[1], self.trap)

        # Move the piece back to the starting position.
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])

        # Play the move sound effect.
        self.engine.sounds.play("move")

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Undo the action usage.
        self.engine.players[self.engine.turn].undo_action()


class TrapCapture(GameEvent):
    """
    Represents the event of capturing a piece on a trap on the game board.

    This event handles capturing a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the TrapCapture event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the capture action.
        :param action_tile: The tile where the capture action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the piece being moved.
        self.moved = self.acting_tile.get_occupying()

        # Store whether this is the piece's first move.
        self.first_move = self.moved.first_move

        # Store the starting position of the move.
        self.start = self.moved.row, self.moved.col

        # Store the ending position of the move.
        self.end = self.action_tile.get_position()

        # Store the piece being captured.
        self.captured = self.action_tile.get_occupying()

        # Store the trap at the action tile.
        self.trap = self.action_tile.trap

    def __repr__(self) -> str:
        """
        Returns a string representation of the TrapCapture event.

        :return: A string representation of this event.
        """
        return "trap capture"

    def complete(self):
        """
        Completes the capture action, updating the game state accordingly.
        """
        super().complete()

        # Reduce the moved piece's remaining actions by 1.
        self.moved.actions_remaining -= 1

        # Mark the piece's first move as completed.
        self.moved.first_move = False

        # Play the capture sound effect.
        self.engine.sounds.play("capture")

        # Capture the piece at the destination.
        self.engine.capture(self.start[0], self.start[1], self.end[0], self.end[1])

        # Delete the piece at the destination position.
        self.engine.delete_piece(self.end[0], self.end[1])

        # Remove the trap at the destination position.
        self.engine.un_trap(self.end[0], self.end[1])

        # Mark an action as used.
        self.engine.players[self.engine.turn].do_action()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        """
        Undoes the capture action, restoring the game state to before the capture occurred.
        """
        super().undo()

        # Restore the moved piece's remaining actions.
        self.moved.actions_remaining += 1

        # Restore the piece's first move status.
        self.moved.first_move = self.first_move

        # Play the capture sound effect.
        self.engine.sounds.play("capture")

        # Create the piece at the destination position.
        self.engine.create_piece(self.end[0], self.end[1], self.moved)

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Move the piece back to the starting position.
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])

        # Restore the captured piece.
        self.engine.create_piece(self.end[0], self.end[1], self.captured)

        # Set the trap at the destination position.
        self.engine.set_trap(self.end[0], self.end[1], self.trap)

        # Undo the action usage.
        self.engine.players[self.engine.turn].undo_action()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Capture(GameEvent):
    """
    Represents the event of capturing a piece on the game board.

    This event handles capturing a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the Capture event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the capture action.
        :param action_tile: The tile where the capture action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the piece being moved.
        self.moved = self.acting_tile.get_occupying()

        # Store whether this is the piece's first move.
        self.first_move = self.moved.first_move

        # Store the starting position of the move.
        self.start = self.moved.row, self.moved.col

        # Store the ending position of the move.
        self.end = self.action_tile.get_position()

        # Store the piece being captured.
        self.captured = self.action_tile.get_occupying()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Capture event.

        :return: A string representation of this event.
        """
        return "capture"

    def complete(self):
        """
        Completes the capture action, updating the game state accordingly.
        """
        super().complete()

        # Reduce the moved piece's remaining actions by 1.
        self.moved.actions_remaining -= 1

        # Mark the piece's first move as completed.
        self.moved.first_move = False

        # Play the capture sound effect.
        self.engine.sounds.play("capture")

        # Capture the piece at the destination.
        self.engine.capture(self.start[0], self.start[1], self.end[0], self.end[1])

        # Mark an action as used.
        self.engine.players[self.engine.turn].do_action()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

    def undo(self):
        """
        Undoes the capture action, restoring the game state to before the capture occurred.
        """
        super().undo()

        # Restore the moved piece's remaining actions.
        self.moved.actions_remaining += 1

        # Restore the piece's first move status.
        self.moved.first_move = self.first_move

        # Play the capture sound effect.
        self.engine.sounds.play("capture")

        # Move the piece back to the starting position.
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])

        # Restore the captured piece.
        self.engine.create_piece(self.end[0], self.end[1], self.captured)

        # Undo the action usage.
        self.engine.players[self.engine.turn].undo_action()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Move(GameEvent):
    """
    Represents the event of moving a piece on the game board.

    This event handles moving a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the Move event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the move action.
        :param action_tile: The tile where the move action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the piece being moved.
        self.moved = self.acting_tile.get_occupying()

        # Store whether this is the piece's first move.
        self.first_move = self.moved.first_move

        # Store the starting position of the move.
        self.start = self.moved.row, self.moved.col

        # Store the ending position of the move.
        self.end = self.action_tile.get_position()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Move event.

        :return: A string representation of this event.
        """
        return "move"

    def complete(self):
        """
        Completes the move action, updating the game state accordingly.
        """
        super().complete()

        # Reduce the moved piece's remaining actions by 1.
        self.moved.actions_remaining -= 1

        # Mark the piece's first move as completed.
        self.moved.first_move = False

        # Move the piece to the new position.
        self.engine.move(self.start[0], self.start[1], self.end[0], self.end[1])

        # Play the move sound effect.
        self.engine.sounds.play("move")

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Mark an action as used.
        self.engine.players[self.engine.turn].do_action()

    def undo(self):
        """
        Undoes the move action, restoring the game state to before the move occurred.
        """
        super().undo()

        # Restore the moved piece's remaining actions.
        self.moved.actions_remaining += 1

        # Restore the piece's first move status.
        self.moved.first_move = self.first_move

        # Move the piece back to the starting position.
        self.engine.move(self.end[0], self.end[1], self.start[0], self.start[1])

        # Play the move sound effect.
        self.engine.sounds.play("move")

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Undo the action usage.
        self.engine.players[self.engine.turn].undo_action()


class RitualEvent(GameEvent):
    """
    Represents a ritual event in the game.

    This event handles performing a ritual, updating game state, and managing resources.
    """

    def __init__(
        self,
        engine: "Engine",
        acting_tile: "Tile",
        action_tile: Union["Tile", Tuple[Tuple[int, int], Tuple[int, int]]],
    ):
        """
        Initializes the RitualEvent.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the ritual action.
        :param action_tile: The tile where the ritual action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the game engine instance.
        self.engine = engine

        # Store the building performing the ritual.
        self.ritual_building = self.acting_tile.get_occupying()

        # Initialize the list of deleted monks.
        self.deleted_monks = []

        # Try to get the cost type from the current state.
        try:
            self.cost_type = self.engine.get_current_state().cost_type
        except AttributeError:
            self.cost_type = None

        # Initialize the ritual cost.
        self.ritual_cost = None

        # Set the ritual cost if the cost type is available.
        if self.cost_type:
            self.ritual_cost = self.engine.RITUAL_COSTS[str(self)][self.cost_type]

        # Set the monk cost based on the cost type.
        if self.cost_type == "gold" or not self.cost_type:
            self.monk_cost = 0
        else:
            self.monk_cost = self.engine.RITUAL_COSTS[str(self)]["monk"]

        # Store the current turn and player.
        self.turn = self.engine.turn
        self.player = self.engine.players[self.turn]

    def complete(self):
        """
        Completes the ritual action, updating the game state accordingly.
        """
        super().complete()

        # Play the ritual sound effect.
        self.engine.sounds.play("ritual")

        # Perform the ritual for the player.
        self.player.do_ritual(self.ritual_cost, self.cost_type)

        # Mark an action as used.
        self.player.do_action()

        # Sacrifice random monks if required.
        self.sacrifice_random_monks()

        # Reduce the ritual building's remaining actions by 1.
        self.ritual_building.actions_remaining -= 1

    def undo(self):
        """
        Undoes the ritual action, restoring the game state to before the ritual occurred.
        """
        super().undo()

        # Play the ritual sound effect.
        self.engine.sounds.play("ritual")

        # Undo the ritual for the player.
        self.player.undo_ritual(self.ritual_cost, self.cost_type)

        # Restore the ritual building's remaining actions.
        self.ritual_building.actions_remaining += 1

        # Respawn the deleted monks if required.
        self.respawn_deleted_monks()

        # Undo the action usage.
        self.player.undo_action()

    def respawn_deleted_monks(self):
        """
        Respawns the monks that were sacrificed during the ritual.
        """
        if self.monk_cost != 0:
            for monk in self.deleted_monks:
                # Get the monk's position and remaining actions.
                row = monk.row
                col = monk.col
                actions_remaining = monk.actions_remaining

                # Create a new monk at the same position.
                self.engine.create_piece(row, col, Monk(row, col, self.turn))

                # Restore the monk's remaining actions.
                self.engine.get_occupying(row, col).actions_remaining = (
                    actions_remaining
                )

    def sacrifice_random_monks(self):
        """
        Sacrifices a random selection of monks for the ritual.
        """
        if self.monk_cost != 0:
            count = []

            # Collect all monks belonging to the player.
            for piece in self.player.pieces:
                if isinstance(piece, Monk):
                    count.append(piece)

            # Shuffle the list of monks.
            random.shuffle(count)

            # Sacrifice the required number of monks.
            for i in range(self.monk_cost):
                try:
                    # Add the monk to the list of deleted monks.
                    self.deleted_monks.append(count[i])

                    # Delete the monk from the board.
                    self.engine.delete_piece(count[i].row, count[i].col)
                except IndexError:
                    pass


class GoldGeneralEvent(RitualEvent):
    """
    Represents the event of summoning a Gold General in the game.

    This event handles summoning a Gold General, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the GoldGeneralEvent.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the ritual action.
        :param action_tile: The tile where the ritual action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player's color.
        self.color = self.engine.turn

        # Store the position of the action tile.
        self.row, self.col = self.action_tile.get_position()

        # Initialize the portal end position and traps.
        self.portal_end = None
        self.trap = None
        self.portal_end_trap = None

    def __repr__(self) -> str:
        """
        Returns a string representation of the GoldGeneralEvent.

        :return: A string representation of this event.
        """
        return "gold_general"

    def complete(self):
        """
        Completes the ritual action, updating the game state accordingly.
        """
        super().complete()

        # Create the Gold General piece.
        piece = self.engine.PIECES[str(self)](self.row, self.col, self.turn)

        # Check if the action tile has an effective trap.
        if action_tile_has_effective_trap(self.acting_tile, self.action_tile):
            # Store and remove the trap.
            self.trap = self.engine.board[self.row][self.col].trap
            self.engine.board[self.row][self.col].undo_trap()
            return

        # Create the piece on the board.
        self.engine.create_piece(self.row, self.col, piece)

        # Check if the action tile has a portal.
        if self.engine.board[self.row][self.col].portal:
            # Get the connected portal.
            connected_portal = self.engine.board[self.row][self.col].connected_portal

            # Swap the pieces between the portals.
            self.engine.swap(
                self.row, self.col, connected_portal.row, connected_portal.col
            )

            # Store the portal end position.
            self.portal_end = connected_portal.get_position()

            # Check if the connected portal has an effective trap.
            if action_tile_has_effective_trap(self.acting_tile, connected_portal):
                # Store and remove the trap at the portal end.
                self.portal_end_trap = connected_portal.trap
                self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
                self.engine.un_trap(self.portal_end[0], self.portal_end[1])

    def undo(self):
        """
        Undoes the ritual action, restoring the game state to before the ritual occurred.
        """
        super().undo()

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True

        # Restore the trap if it was removed.
        if self.trap:
            self.engine.set_trap(self.row, self.col, self.trap)
            return

        # Check if the action tile has a portal.
        if self.engine.board[self.row][self.col].portal:
            # Restore the trap at the portal end if it was removed.
            if self.portal_end_trap:
                self.engine.set_trap(
                    self.portal_end[0], self.portal_end[1], self.portal_end_trap
                )
                return

            # Get the connected portal.
            connected_portal = self.engine.board[self.row][self.col].connected_portal

            # Swap the pieces back to their original positions.
            self.engine.swap(
                self.row, self.col, connected_portal.row, connected_portal.col
            )

        # Delete the piece from the board.
        self.engine.delete_piece(self.row, self.col)


class Teleport(RitualEvent):
    """
    Represents the event of teleporting a piece in the game.

    This event handles teleporting a piece, updating game state, and managing resources.
    """

    def __init__(
        self,
        engine: "Engine",
        acting_tile: "Tile",
        action_tile: Tuple[Tuple[int, int], Tuple[int, int]],
    ):
        """
        Initializes the Teleport event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the teleport action.
        :param action_tile: A tuple containing the source and destination positions.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the source and destination positions.
        self.selected_first, self.selected_second = action_tile
        self.dest_row, self.dest_col = self.selected_second
        self.row, self.col = self.selected_first

        # Initialize portal end position and traps.
        self.portal_end = None
        self.portal_end_trap = None
        self.deleted_piece = None

        # Store the color of the piece being teleported.
        self.color = self.engine.board[self.row][self.col].get_occupying().color

        # Store the previously selected position.
        self.previously_selected = self.acting_tile.get_position()

        # Initialize protection status.
        self.is_protected = False
        self.portal_end_is_protected = False

        # Initialize traps.
        self.trap = None
        self.portal_end_trap = None
        self.portal_end_tile = None

        # Check if the destination tile has an effective trap.
        if action_tile_has_effective_trap(
            self.acting_tile, self.engine.board[self.dest_row][self.dest_col]
        ):
            self.trap = self.engine.board[self.dest_row][self.dest_col].trap

        # Check if the destination tile has a portal.
        if self.engine.board[self.dest_row][self.dest_col].portal:
            connected_portal = self.engine.board[self.dest_row][
                self.dest_col
            ].connected_portal
            self.portal_end = connected_portal.get_position()
            if action_tile_has_effective_trap(self.acting_tile, connected_portal):
                self.portal_end_trap = connected_portal.trap

    def __repr__(self) -> str:
        """
        Returns a string representation of the Teleport event.

        :return: A string representation of this event.
        """
        return "teleport"

    def complete(self):
        """
        Completes the teleport action, updating the game state accordingly.
        """
        super().complete()

        # Move the piece to the new position.
        self.engine.move(self.row, self.col, self.dest_row, self.dest_col)

        # Set the moved piece's remaining actions to 0.
        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = 0

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Handle the trap if it exists.
        if self.trap:
            self.deleted_piece = self.engine.get_occupying(self.dest_row, self.dest_col)
            self.engine.delete_piece(self.dest_row, self.dest_col)
            self.engine.un_trap(self.dest_row, self.dest_col)
            return

        # Handle the portal if it exists.
        if self.engine.board[self.dest_row][self.dest_col].portal:
            self.engine.swap(
                self.dest_row, self.dest_col, self.portal_end[0], self.portal_end[1]
            )
            if self.portal_end_trap:
                self.deleted_piece = self.engine.get_occupying(
                    self.portal_end[0], self.portal_end[1]
                )
                self.engine.delete_piece(self.portal_end[0], self.portal_end[1])
                self.engine.un_trap(self.portal_end[0], self.portal_end[1])
                return

    def undo(self):
        """
        Undoes the teleport action, restoring the game state to before the teleport occurred.
        """
        super().undo()

        # Restore the piece and trap if it was deleted.
        if self.trap:
            self.engine.create_piece(self.dest_row, self.dest_col, self.deleted_piece)
            self.engine.set_trap(self.dest_row, self.dest_col, self.trap)
        elif self.engine.board[self.dest_row][self.dest_col].portal:
            self.engine.swap(
                self.portal_end[0], self.portal_end[1], self.dest_row, self.dest_col
            )
            if self.portal_end_trap:
                self.engine.create_piece(
                    self.portal_end[0], self.portal_end[1], self.deleted_piece
                )
                self.engine.swap(
                    self.portal_end[0], self.portal_end[1], self.dest_row, self.dest_col
                )
                self.engine.set_trap(
                    self.portal_end[0], self.portal_end[1], self.portal_end_trap
                )

        # Move the piece back to the starting position.
        self.engine.move(self.dest_row, self.dest_col, self.row, self.col)

        # Restore the moved piece's remaining actions.
        self.engine.get_occupying(self.row, self.col).actions_remaining = 1

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Swap(RitualEvent):
    """
    Represents the event of swapping two pieces in the game.

    This event handles swapping two pieces, updating game state, and managing resources.
    """

    def __init__(
        self,
        engine: "Engine",
        acting_tile: "Tile",
        action_tile: Tuple[Tuple[int, int], Tuple[int, int]],
    ):
        """
        Initializes the Swap event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the swap action.
        :param action_tile: A tuple containing the source and destination positions.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the source and destination positions.
        self.selected_first, self.selected_second = action_tile
        self.dest_row, self.dest_col = self.selected_second
        self.row, self.col = self.selected_first

        # Initialize portal end traps and deleted pieces.
        self.first_is_portal = False
        self.second_is_portal = False
        self.first_portal_end_trap = None
        self.second_portal_end_trap = None
        self.first_deleted_piece = None
        self.second_deleted_piece = None
        self.first_trap = None
        self.second_trap = None

        # Store the tiles involved in the swap.
        self.first_tile = self.engine.board[self.row][self.col]
        self.second_tile = self.engine.board[self.dest_row][self.dest_col]

        # Check for traps and portals on the first tile.
        if action_tile_has_effective_trap(self.first_tile, self.second_tile):
            self.second_trap = self.second_tile.trap
        elif self.second_tile.portal:
            self.second_is_portal = True
            connected_portal = self.second_tile.connected_portal
            if action_tile_has_effective_trap(self.first_tile, connected_portal):
                self.second_portal_end_trap = connected_portal.trap

        # Check for traps and portals on the second tile.
        if action_tile_has_effective_trap(self.second_tile, self.first_tile):
            self.first_trap = self.first_tile.trap
        elif self.first_tile.portal:
            self.first_is_portal = True
            connected_portal = self.first_tile.connected_portal
            if action_tile_has_effective_trap(self.second_tile, connected_portal):
                self.first_portal_end_trap = connected_portal.trap

        # Store the remaining actions for the pieces.
        self.first_actions = self.engine.get_occupying(
            self.row, self.col
        ).actions_remaining
        self.second_actions = self.engine.get_occupying(
            self.dest_row, self.dest_col
        ).actions_remaining

        # Store the previously selected position.
        self.previously_selected = self.acting_tile.get_position()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Swap event.

        :return: A string representation of this event.
        """
        return "swap"

    def complete(self):
        """
        Completes the swap action, updating the game state accordingly.
        """
        super().complete()

        # Swap the pieces on the board.
        self.engine.swap(self.row, self.col, self.dest_row, self.dest_col)

        # Set the moved pieces' remaining actions to 0.
        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = 0
        self.engine.get_occupying(self.row, self.col).actions_remaining = 0

        # Handle the first tile's trap or portal.
        if self.first_trap:
            self.first_deleted_piece = self.engine.get_occupying(self.row, self.col)
            self.engine.delete_piece(self.row, self.col)
            self.engine.un_trap(self.row, self.col)
        elif self.first_is_portal:
            connected_portal = self.engine.board[self.row][self.col].connected_portal
            self.engine.swap(
                self.row, self.col, connected_portal.row, connected_portal.col
            )
            if self.first_portal_end_trap:
                self.first_deleted_piece = self.engine.get_occupying(
                    connected_portal.row, connected_portal.col
                )
                self.engine.delete_piece(connected_portal.row, connected_portal.col)
                self.engine.un_trap(connected_portal.row, connected_portal.col)

        # Handle the second tile's trap or portal.
        if self.second_trap:
            self.second_deleted_piece = self.engine.get_occupying(
                self.dest_row, self.dest_col
            )
            self.engine.delete_piece(self.dest_row, self.dest_col)
            self.engine.un_trap(self.dest_row, self.dest_col)
        elif self.second_is_portal:
            connected_portal = self.engine.board[self.dest_row][
                self.dest_col
            ].connected_portal
            self.engine.swap(
                self.dest_row, self.dest_col, connected_portal.row, connected_portal.col
            )
            if self.second_portal_end_trap:
                self.second_deleted_piece = self.engine.get_occupying(
                    connected_portal.row, connected_portal.col
                )
                self.engine.delete_piece(connected_portal.row, connected_portal.col)
                self.engine.un_trap(connected_portal.row, connected_portal.col)

        # Intercept pieces.
        self.engine.intercept_pieces()

    def undo(self):
        """
        Undoes the swap action, restoring the game state to before the swap occurred.
        """
        super().undo()

        # Restore the first tile's piece and trap if it was deleted.
        if self.first_trap:
            self.engine.create_piece(self.row, self.col, self.first_deleted_piece)
            self.engine.set_trap(self.row, self.col, self.first_trap)
        elif self.first_is_portal:
            connected_portal = self.engine.board[self.row][self.col].connected_portal
            if self.first_portal_end_trap:
                self.engine.create_piece(
                    connected_portal.row, connected_portal.col, self.first_deleted_piece
                )
                self.engine.set_trap(
                    connected_portal.row,
                    connected_portal.col,
                    self.first_portal_end_trap,
                )
            self.engine.swap(
                self.row, self.col, connected_portal.row, connected_portal.col
            )

        # Restore the second tile's piece and trap if it was deleted.
        if self.second_trap:
            self.engine.create_piece(
                self.dest_row, self.dest_col, self.second_deleted_piece
            )
            self.engine.set_trap(self.dest_row, self.dest_col, self.second_trap)
        elif self.second_is_portal:
            connected_portal = self.engine.board[self.dest_row][
                self.dest_col
            ].connected_portal
            if self.second_portal_end_trap:
                self.engine.create_piece(
                    connected_portal.row,
                    connected_portal.col,
                    self.second_deleted_piece,
                )
                self.engine.set_trap(
                    connected_portal.row,
                    connected_portal.col,
                    self.second_portal_end_trap,
                )
            self.engine.swap(
                self.dest_row, self.dest_col, connected_portal.row, connected_portal.col
            )

        # Swap the pieces back to their original positions.
        self.engine.swap(self.dest_row, self.dest_col, self.row, self.col)

        # Restore the moved pieces' remaining actions.
        self.engine.get_occupying(self.row, self.col).actions_remaining = (
            self.first_actions
        )
        self.engine.get_occupying(self.dest_row, self.dest_col).actions_remaining = (
            self.second_actions
        )

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Smite(RitualEvent):
    """
    Represents the event of smiting a piece in the game.

    This event handles deleting a piece, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the Smite event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the smite action.
        :param action_tile: The tile where the smite action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the position of the action tile.
        self.row, self.col = self.action_tile.get_position()

        # Store the piece being deleted.
        self.deleted_piece = self.engine.get_occupying(self.row, self.col)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Smite event.

        :return: A string representation of this event.
        """
        return "smite"

    def complete(self):
        """
        Completes the smite action, updating the game state accordingly.
        """
        super().complete()

        # Delete the piece from the board.
        self.engine.delete_piece(self.row, self.col)

    def undo(self):
        """
        Undoes smite action, restoring the game state to before smite occurred.
        """
        super().undo()

        # Create the piece back on the board.
        self.engine.create_piece(self.row, self.col, self.deleted_piece)

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Trade(GameEvent):
    """
    Represents the Trade event, where a player trades resources with another player.

    This event handles the trading of resources, updating game state, and managing resources.
    """

    def __init__(
        self, engine: "Engine", acting_tile: "Tile", action_tile: Optional["Tile"]
    ):
        """
        Initializes the Trade event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the trade action.
        :param action_tile: The tile where the trade action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the current player.
        self.player = self.engine.players[self.engine.turn]

        # Store the resources being traded.
        self.give = self.engine.trading[0]
        self.receive = self.engine.trading[1]

        # Extract the resource type and amount for giving and receiving.
        self.give_resource, self.give_amount = self.give[0], self.give[1]
        self.receive_resource, self.receive_amount = self.receive[0], self.receive[1]

        # Map the resource keys to their respective constants.
        self.give_resource = constant.RESOURCE_KEY[self.give_resource]
        self.receive_resource = constant.RESOURCE_KEY[self.receive_resource]

        # Store the piece initiating the trade.
        self.piece = self.acting_tile.get_occupying()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Trade event.

        :return: A string representation of this event.
        """
        return "trade"

    def complete(self):
        """
        Completes the trade action, updating the game state accordingly.
        """
        super().complete()

        # Decrease the piece's remaining actions by 1.
        self.piece.actions_remaining -= 1

        # Get the current amount of the resource being given.
        amount = getattr(self.player, self.give_resource)

        # Subtract the given amount from the player's resources.
        setattr(self.player, self.give_resource, amount - self.give_amount)

        # Get the current amount of the resource being received.
        amount = getattr(self.player, self.receive_resource)

        # Add the received amount to the player's resources.
        setattr(self.player, self.receive_resource, amount + self.receive_amount)

        # Clear the trading state.
        self.engine.trading = []
        self.engine.piece_trading = None

    def undo(self):
        """
        Undoes the trade action, restoring the game state to before the trade occurred.
        """
        super().undo()

        # Increase the piece's remaining actions by 1.
        self.piece.actions_remaining += 1

        # Get the current amount of the resource being given.
        amount = getattr(self.player, self.give_resource)

        # Add the given amount back to the player's resources.
        setattr(self.player, self.give_resource, amount + self.give_amount)

        # Get the current amount of the resource being received.
        amount = getattr(self.player, self.receive_resource)

        # Subtract the received amount from the player's resources.
        setattr(self.player, self.receive_resource, amount - self.receive_amount)

        # Reset unused piece highlights.
        self.engine.reset_unused_piece_highlight()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class DestroyResource(RitualEvent):
    """
    Represents the event of destroying a resource on the game board.

    This event handles deleting a resource, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the DestroyResource event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the destroy resource action.
        :param action_tile: The tile where the destroy resource action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the position of the action tile.
        self.row, self.col = self.action_tile.get_position()

        # Store the resource being deleted.
        self.deleted_resource = self.engine.get_resource(self.row, self.col)

    def __repr__(self) -> str:
        """
        Returns a string representation of the DestroyResource event.

        :return: A string representation of this event.
        """
        return "destroy_resource"

    def complete(self):
        """
        Completes the destroy resource action, updating the game state accordingly.
        """
        super().complete()

        # Delete the resource from the board.
        self.engine.delete_resource(self.row, self.col)

    def undo(self):
        """
        Undoes destroy resource action, restoring the game state to before destroy occurred.
        """
        super().undo()

        # Create the resource back on the board.
        self.engine.create_resource(self.row, self.col, self.deleted_resource)

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class CreateResource(RitualEvent):
    """
    Represents the event of creating a resource on the game board.

    This event handles creating a resource, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the CreateResource event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating create resource action.
        :param action_tile: The tile where create resource action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the position of the action tile.
        self.row, self.col = self.action_tile.get_position()

        # Store the resource type to be created.
        self.resource = self.engine.ritual_summon_resource

        # Create the resource instance.
        self.created_resource = self.engine.RESOURCES[self.resource](self.row, self.col)

    def __repr__(self) -> str:
        """
        Returns a string representation of the CreateResource event.

        :return: A string representation of this event.
        """
        return "create_resource"

    def complete(self):
        """
        Completes create resource action, updating the game state accordingly.
        """
        super().complete()

        # Create the resource on the board.
        self.engine.create_resource(self.row, self.col, self.created_resource)

    def undo(self):
        """
        Undoes create resource action, restoring the game state to before create occurred.
        """
        super().undo()

        # Delete the resource from the board.
        self.engine.delete_resource(self.row, self.col)

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        self.engine.correct_interceptions()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class LineDestroy(RitualEvent):
    """
    Represents the event of destroying a line of tiles on the game board.

    This event handles deleting tiles and pieces, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the LineDestroy event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the line destroy action.
        :param action_tile: The tile where the line destroy action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the position of the action tile.
        self.row, self.col = self.action_tile.get_position()

        # Store the selected range for line destruction.
        self.selected_range = self.engine.line_destroy_selected_range

        # Record the squares and pieces to be destroyed.
        self.destroyed_squares = self.record_destroyed_squares()
        self.destroyed_pieces = self.record_destroyed_pieces()
        self.destroyed_portals = []

    def __repr__(self) -> str:
        """
        Returns a string representation of the LineDestroy event.

        :return: A string representation of this event.
        """
        return "line_destroy"

    def record_destroyed_pieces(self) -> list:
        """
        Records the pieces that will be destroyed.

        :return: A list of pieces to be destroyed.
        """
        destroyed_pieces = []
        for tile in self.destroyed_squares:
            if tile.get_occupying():
                destroyed_pieces.append(tile.get_occupying())

        return destroyed_pieces

    def record_destroyed_squares(self) -> list:
        """
        Records the squares that will be destroyed.

        :return: A list of squares to be destroyed.
        """
        destroyed_squares = []
        for row in self.selected_range[0]:
            for col in self.selected_range[1]:
                if not self.engine.board[row][col].is_protected():
                    destroyed_squares.append(self.engine.board[row][col])

        return destroyed_squares

    def destroy_squares(self):
        """
        Destroys the squares in the selected range.
        """
        for row in self.selected_range[0]:
            col = None
            for col in self.selected_range[1]:
                if not self.engine.board[row][col].is_protected():
                    self.engine.board[row][col] = Tile(row, col)
                else:
                    break
            if col is not None and self.engine.board[row][col].is_protected():
                break

    def remove_destroyed_pieces_from_player_list(self):
        """
        Removes the destroyed pieces from the player's list.
        """
        for piece in self.destroyed_pieces:
            self.engine.players[piece.get_color()].pieces.remove(piece)

    def restore_destroyed_pieces_to_player_list(self):
        """
        Restores the destroyed pieces to the player's list.
        """
        for piece in self.destroyed_pieces:
            self.engine.players[piece.color].pieces.append(piece)

    def replace_destroyed_squares(self):
        """
        Replaces the destroyed squares on the board.
        """
        for tile in self.destroyed_squares:
            self.engine.board[tile.row][tile.col] = tile

    def complete(self):
        """
        Completes the line destroy action, updating the game state accordingly.
        """
        super().complete()

        for tile in self.destroyed_squares:
            if tile.portal:
                try:
                    self.destroyed_portals.append((tile, tile.connected_portal))
                    tile.connected_portal.portal = True
                    tile.connected_portal.connected_portal = None
                    tile.connected_portal = None
                except AttributeError:
                    self.destroyed_portals.append((tile, None))
                tile.portal = False

        # Destroy the squares in the selected range.
        self.destroy_squares()

        # Remove the destroyed pieces from the player's list.
        self.remove_destroyed_pieces_from_player_list()

        # Intercept pieces.
        self.engine.intercept_pieces()

        # Clear the selected range for line destruction.
        self.engine.line_destroy_selected_range = None

    def undo(self):
        """
        Undoes line destroy action, restoring the game state to before destroy occurred.
        """
        super().undo()

        # Restore the destroyed pieces to the player's list.
        self.restore_destroyed_pieces_to_player_list()

        for tile, connected_portal in self.destroyed_portals:
            tile.portal = True
            tile.connected_portal = connected_portal
            if tile.connected_portal:
                tile.connected_portal.portal = True
                tile.connected_portal.connected_portal = tile

        # Replace the destroyed squares on the board.
        self.replace_destroyed_squares()

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Protect(RitualEvent):
    """
    Represents the event of protecting a tile on the game board.

    This event handles protecting a tile, updating game state, and managing resources.
    """

    def __init__(self, engine: "Engine", acting_tile: "Tile", action_tile: "Tile"):
        """
        Initializes the Protect event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the protect action.
        :param action_tile: The tile where the protect action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the position of the action tile.
        self.row, self.col = self.action_tile.get_position()

        # Store the protection information of the action tile.
        self.protect_information = action_tile.get_protect_values()

        # Flag to indicate if protection is being replaced.
        self.replace_protect = False

    def __repr__(self) -> str:
        """
        Returns a string representation of the Protect event.

        :return: A string representation of this event.
        """
        return "protect"

    def complete(self):
        """
        Completes the protect action, updating the game state accordingly.
        """
        super().complete()

        # Check if the tile is already protected and set the replacement flag.
        if self.engine.board[self.row][self.col] in self.engine.protected_tiles:
            self.replace_protect = True
            self.engine.protected_tiles.remove(self.engine.board[self.row][self.col])

        # Protect the tile and add it to the protected tiles list.
        self.engine.board[self.row][self.col].protect(self.turn)
        self.engine.protected_tiles.append(self.engine.board[self.row][self.col])

        # Intercept pieces.
        self.engine.intercept_pieces()

    def undo(self):
        """
        Undoes protect action, restoring the game state to before protect occurred.
        """
        super().undo()

        # Remove protection from the tile and remove it from the protected tiles list.
        self.engine.board[self.row][self.col].remove_protection()
        self.engine.protected_tiles.remove(self.engine.board[self.row][self.col])

        # Restore the protection if it was replaced.
        if self.replace_protect:
            self.action_tile.replace_values(self.protect_information)
            self.engine.protected_tiles.append(self.engine.board[self.row][self.col])

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class Portal(RitualEvent):
    """
    Represents the event of creating a portal between two tiles on the game board.

    This event handles creating a portal, updating game state, and managing resources.
    """

    def __init__(
        self,
        engine: "Engine",
        acting_tile: "Tile",
        action_tile: Tuple[Tuple[int, int], Tuple[int, int]],
    ):
        """
        Initializes the Portal event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the portal action.
        :param action_tile: A tuple containing the source and destination positions.
        """
        super().__init__(engine, acting_tile, action_tile)

        # Store the source and destination positions.
        self.selected_first, self.selected_second = action_tile
        self.dest_row, self.dest_col = self.selected_second
        self.row, self.col = self.selected_first

        # Store the previously selected position.
        self.previously_selected = self.acting_tile.get_position()

        # Initialize saved portal states.
        self.first_saved_portal = None
        self.second_saved_portal = None

    def __repr__(self) -> str:
        """
        Returns a string representation of the Portal event.

        :return: A string representation of this event.
        """
        return "portal"

    def complete(self):
        """
        Completes the portal creation action, updating the game state accordingly.
        """
        super().complete()

        # Check if the source tile already has a portal and save its state.
        if self.engine.board[self.row][self.col].portal:
            tile = self.engine.board[self.row][self.col]
            self.first_saved_portal = (tile.portal_color, tile.connected_portal)

        # Create a portal on the source tile.
        self.engine.board[self.row][self.col].create_portal(
            self.turn, self.engine.board[self.dest_row][self.dest_col]
        )

        # Check if the destination tile already has a portal and save its state.
        if self.engine.board[self.dest_row][self.dest_col].portal:
            tile = self.engine.board[self.dest_row][self.dest_col]
            self.second_saved_portal = (tile.portal_color, tile.connected_portal)

        # Create a portal on the destination tile.
        self.engine.board[self.dest_row][self.dest_col].create_portal(
            self.turn, self.engine.board[self.row][self.col]
        )

        # Intercept pieces.
        self.engine.intercept_pieces()

    def undo(self):
        """
        Undoes the portal creation action, restoring the game state to before the portal was created.
        """
        super().undo()

        # Remove the portal from the source tile.
        self.engine.board[self.row][self.col].remove_portal()

        # Restore the saved portal state on the source tile if it existed.
        if self.first_saved_portal:
            portal = self.first_saved_portal
            self.engine.board[self.row][self.col].create_portal(portal[0], portal[1])

        # Remove the portal from the destination tile.
        self.engine.board[self.dest_row][self.dest_col].remove_portal()

        # Restore the saved portal state on the destination tile if it existed.
        if self.second_saved_portal:
            portal = self.second_saved_portal
            self.engine.board[self.dest_row][self.dest_col].create_portal(
                portal[0], portal[1]
            )

        # Reset the selected piece/tile.
        self.engine.reset_selected()

        # Correct any interceptions.
        self.engine.correct_interceptions()

        # Highlight all unused pieces.
        unused_pieces = self.engine.count_unused_pieces()
        self.engine.reset_unused_piece_highlight()
        for piece in unused_pieces:
            piece.unused_piece_highlight = True


class ResetBoard(GameEvent):
    def __init__(
        self,
        engine: "Engine",
        acting_tile: Optional["Tile"],
        action_tile: Optional["Tile"],
    ):
        super().__init__(engine, acting_tile, action_tile)
        self.board_copy = self.engine.board[:]

    def __repr__(self) -> str:
        return "reset_board"

    def complete(self):
        super().complete()
        # Play the resource creation sound
        self.engine.sounds.play("create_resource")
        # Iterate over each row on the board
        for row in range(self.engine.rows):
            # Iterate over each column in the current row
            for col in range(self.engine.cols):
                # Reinitialize the tile at the current position
                self.engine.board[row][col] = Tile(row, col)

    def undo(self):
        super().undo()
        self.engine.board = self.board_copy[:]


class SelectMap(GameEvent):
    """
    Represents the event of selecting a map in the game.

    This event handles the selection of a map, updating game state, and managing resources.
    """

    def __init__(
        self,
        engine: "Engine",
        acting_tile: Optional["Tile"],
        action_tile: Optional["Tile"],
    ):
        """
        Initializes the SelectMap event.

        :param engine: The game engine instance.
        :param acting_tile: The tile initiating the select map action.
        :param action_tile: The tile where the select map action occurs.
        """
        super().__init__(engine, acting_tile, action_tile)

    def __repr__(self) -> str:
        """
        Returns a string representation of the SelectMap event.

        :return: A string representation of this event.
        """
        return "select map"

    def complete(self):
        """
        Completes the select map action, updating the game state accordingly.
        """
        super().complete()
        # Select a random map from the available maps
        self.engine.map = random.choice(self.engine.MAPS)(self.engine)
        # Generate stone resources on the map
        self.engine.map.generate_stone()
        # Generate other resources on the map
        self.engine.map.generate_resources()
        # Play the resource creation sound
        self.engine.sounds.play("create_resource")
        # Set the values for the pieces based on the resources
        self.engine.set_piece_values()
        # Update upgrade costs for this map
        self.engine.upgrades.map = self.engine.map
        # Generate upgrade costs based on the selected map
        self.engine.upgrades.generate_upgrade_costs()
        # Set prayer costs for map
        self.engine.map.assign_ritual_costs(self.engine.RITUAL_COSTS)

    def synchronize(self, engine):
        """
        Synchronizes the game state with the selected map.
        """
        super().synchronize(engine)
        # Synchronize the game state with the selected map
        engine.PIECE_COSTS = self.engine.PIECE_COSTS

        engine.map = self.engine.map

        engine.board = self.engine.board[:]


class TestObject:
    def __init__(self):
        self.row = 0
        self.col = 20
        self.some_stuff = True
        self.foo = 100

    def complete(self):
        pass

    def synchronize(self):
        pass

    def undo(self):
        pass

    def print_foo(self):
        print(self.foo)
        print(f"I have class attributes like: {self.row} and {self.col}")
