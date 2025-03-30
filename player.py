from typing import Dict

from behavior import *


class Player:
    """
    Represents a player in the game. Actions unique to each player should be performed inside this class
    """

    def __init__(self, color: str):
        """
        Initializes a new player with the given color.
        The player starts with a certain amount of resources (gold, wood, stone) and prayer points.
        The player also has a list of pieces, captured pieces (unimplemented) and other stored values.

        :param color: The color of the player.
        """
        # Set the color of the player
        self.color: str = color

        # Initialize the player's resources (gold, wood, stone)
        self.gold: int = constant.STARTING_GOLD
        self.wood: int = constant.STARTING_WOOD
        self.stone: int = constant.STARTING_STONE

        # Initialize the player's prayer points
        self.prayer: int = constant.STARTING_PRAYER

        # Set the number of actions the player can take this turn
        self.actions_remaining: int = constant.DEFAULT_ACTIONS_REMAINING

        # Initialize the king's position and object (optional)
        self.king_position: Optional[tuple] = None
        self.king: Optional["Unit"] = None

        # Initialize lists for the player's pieces, captured pieces, and starting pieces
        self.pieces: List["Unit"] = []
        self.captured_pieces: List["Unit"] = []
        self.starting_pieces: List["Unit"] = []

        # Set the total additional actions the player can take this turn
        self.total_additional_actions_this_turn: int = 0

        # Set the player's piece limit
        self.piece_limit: int = constant.DEFAULT_PIECE_LIMIT

    def __repr__(self) -> str:
        """
        Returns a string representation of the player.

        :return: The player's color as a string.
        """
        return self.color

    def begin_turn(self, engine: object):
        """
        Starts the player's turn. This is currently implemented for AI only.

        :param engine: The game engine that controls the turn flow.
        """
        # only implemented for AI
        pass

    def steal(self, kind: str, value: int):
        """
        Steals a specified amount of a resource from the opponent.

        :param kind: The type of resource to steal ("wood", "gold", "stone").
        :param value: The amount of the resource to steal.
        """
        if kind == "wood":
            self.wood += value
        elif kind == "gold":
            self.gold += value
        elif kind == "stone":
            self.stone += value

    def invert_steal(self, kind: str, value: int):
        """
        Reverts a steal operation, subtracting the stolen amount of a resource.

        :param kind: The type of resource to revert ("wood", "gold", "stone").
        :param value: The amount of the resource to revert.
        """
        if kind == "wood":
            self.wood -= value
        elif kind == "gold":
            self.gold -= value
        elif kind == "stone":
            self.stone -= value

    def mine(self, resource: str, harvest: int):
        """
        Mines a specific resource and adds it to the player's resources.

        :param resource: The type of resource to mine.
        :param harvest: The amount of resource to add.
        """
        player_resource = constant.RESOURCE_KEY[resource]
        current_resource = getattr(self, player_resource)
        setattr(self, player_resource, current_resource + harvest)

    def un_mine(self, resource: str, harvest: int):
        """
        Reverts a mining operation by subtracting the mined resource.

        :param resource: The type of resource to un-mine.
        :param harvest: The amount of resource to subtract.
        """
        player_resource = constant.RESOURCE_KEY[resource]
        current_resource = getattr(self, player_resource)
        setattr(self, player_resource, current_resource - harvest)

    def pray(self, building: "Building", additional_prayer: int):
        """
        Increases the player's prayer based on a building's prayer yield and an additional prayer.

        :param building: The building providing the prayer yield.
        :param additional_prayer: Additional prayer points to add.
        """
        self.prayer += building.yield_when_prayed + additional_prayer

    def un_pray(self, building: "Building", additional_prayer: int):
        """
        Decreases the player's prayer based on a building's prayer yield and an additional prayer.

        :param building: The building providing the prayer yield.
        :param additional_prayer: Additional prayer points to subtract.
        """
        self.prayer -= building.yield_when_prayed + additional_prayer

    def reset_prayer(self):
        """
        Resets the player's prayer to the default starting value or debug value.
        """
        if constant.DEBUG_START:
            self.prayer = constant.DEBUG_STARTING_PRAYER
        else:
            self.prayer = constant.STARTING_PRAYER

    def get_prayer(self) -> int:
        """
        Retrieves the player's current prayer amount.

        :return: The player's current prayer.
        """
        return self.prayer

    def do_ritual(self, cost: int, cost_type: str):
        """
        Performs a ritual, spending the specified amount of resource.

        :param cost: The amount of resource to spend.
        :param cost_type: The type of resource to use for the ritual.
        """
        if not cost_type:
            return

        resource = getattr(self, cost_type)
        setattr(self, cost_type, resource - cost)

    def undo_ritual(self, cost: int, cost_type: str):
        """
        Undoes a ritual, refunding the specified amount of resource.

        :param cost: The amount of resource to refund.
        :param cost_type: The type of resource to refund.
        """
        if not cost_type:
            return
        resource = getattr(self, cost_type)
        setattr(self, cost_type, resource + cost)

    def set_prayer(self, prayer: int):
        """
        Sets the player's prayer to a specified value.

        :param prayer: The new prayer value to set.
        """
        self.prayer = prayer

    def purchase(self, cost: Dict[str, int]):
        """
        Purchases an item by deducting the specified resources.

        :param cost: A dictionary of resource costs with keys "log", "gold", "stone".
        """
        self.wood -= cost["log"]
        self.gold -= cost["gold"]
        self.stone -= cost["stone"]

    def un_purchase(self, cost: Dict[str, int]):
        """
        Undoes a purchase by refunding the specified resources.

        :param cost: A dictionary of resource costs with keys "log", "gold", "stone".
        """
        self.wood += cost["log"]
        self.gold += cost["gold"]
        self.stone += cost["stone"]

    def get_current_population(self) -> int:
        """
        Gets the total population of the player's pieces.

        :return: The total population value of all pieces.
        """
        count = 0
        for piece in self.pieces:
            count += piece.get_population_value()
        return count

    def can_trade(self) -> bool:
        """
        Checks if the player has resources to trade.

        :return: True if the player can trade, False otherwise.
        """
        return self.gold != 0 or self.wood != 0 or self.stone != 0

    def can_add_piece(self, piece: object) -> bool:
        """
        Checks if the player can add a piece based on their current population and piece limit.

        :param piece: The piece the player is attempting to add.
        :return: True if the player can add the piece, False otherwise.
        """
        # Get the current population of the player
        population = self.get_current_population()

        # Get the population value of the piece
        piece_population = constant.PIECE_POPULATION[piece]

        # Get the additional piece limit for the piece (default to 0 if not found)
        additional_limit = constant.ADDITIONAL_PIECE_LIMIT.get(piece, 0)

        # Check if the player's current population plus the piece's population is within the piece limit
        if piece_population + population <= self.piece_limit:
            return True

        # Check if the additional piece limit allows adding the piece
        if additional_limit + self.piece_limit > self.piece_limit:
            return True

        # If the piece population is 0, it's always allowed to add
        if piece_population == 0:
            return True

        # If none of the above conditions are met, return False
        return False

    def get_piece_limit(self) -> int:
        """
        Retrieves the current piece limit of the player.

        :return: The player's current piece limit.
        """
        return self.piece_limit

    def set_piece_limit(self, limit: int):
        """
        Sets the piece limit for the player.

        :param limit: The new piece limit to be set.
        """
        self.piece_limit = limit

    def add_additional_piece_limit(self, limit: int):
        """
        Increases the player's piece limit by a specified amount.

        :param limit: The amount to increase the piece limit by.
        """
        self.piece_limit += limit

    def remove_additional_piece_limit(self, limit: int):
        """
        Decreases the player's piece limit by a specified amount.

        :param limit: The amount to decrease the piece limit by.
        """
        self.piece_limit -= limit

    def reset_actions_remaining(self):
        """
        Resets the player's remaining actions to the default value.
        """
        self.actions_remaining = constant.DEFAULT_ACTIONS_REMAINING

    def set_actions_remaining(self, actions: int):
        """
        Sets the number of remaining actions for the player.

        :param actions: The new number of remaining actions.
        """
        self.actions_remaining = actions

    def get_actions_remaining(self) -> int:
        """
        Retrieves the current number of actions remaining for the player.

        :return: The number of remaining actions.
        """
        return self.actions_remaining

    def add_additional_actions(self, actions: int):
        """
        Increases the player's remaining actions by a specified amount.

        :param actions: The amount to increase the remaining actions by.
        """
        self.actions_remaining += actions

    def remove_additional_actions(self, actions: int):
        """
        Decreases the player's remaining actions by a specified amount.

        :param actions: The amount to decrease the remaining actions by.
        """
        self.actions_remaining -= actions

    def reset_piece_limit(self):
        """
        Resets the player's piece limit to the default value.
        """
        self.piece_limit = constant.DEFAULT_PIECE_LIMIT

    def can_act(self) -> bool:
        """
        Checks if the player has any remaining actions and can act.

        :return: True if the player can act, False otherwise.
        """
        return self.actions_remaining > 0

    def do_action(self):
        """
        Performs an action by decreasing the number of remaining actions.
        """
        self.actions_remaining -= 1

    def undo_action(self):
        """
        Undoes an action by increasing the number of remaining actions.
        """
        self.actions_remaining += 1
