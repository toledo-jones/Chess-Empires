import random
import typing

if typing.TYPE_CHECKING:
    from engine import Engine
    from player import Player

import constant


class Trades:
    """
    A class that handles the trading mechanics in the game.

    This class manages the resources involved in trades, defines the
    conversion rates for giving and receiving resources, and calculates
    the amounts of resources exchanged based on those rates.
    """

    def __init__(self, engine: "Engine") -> None:
        """
        Initializes the Trades object.

        :param engine: The game engine that contains the current trade conversions and turn count.
        """
        self.engine = (
            engine  # The engine object that handles game state and conversions
        )

        self.resources: tuple[str, str, str] = (
            "wood",
            "gold",
            "stone",
        )  # Resources involved in trades

        # Upper and lower bounds for giving resources
        self.give_upper_bound, self.give_lower_bound = (
            constant.TRADING_GIVE_BOUNDS[0],
            constant.TRADING_GIVE_BOUNDS[1],
        )

        # Upper and lower bounds for receiving resources
        self.receive_upper_bound, self.receive_lower_bound = (
            constant.TRADING_RECEIVE_BOUNDS[0],
            constant.TRADING_RECEIVE_BOUNDS[1],
        )

    def get_conversions(self) -> dict[str, tuple[float, float]]:
        """
        Generates the conversion rates for all trade resources.

        :return: A dictionary with resource names as keys and conversion
                 rates (give, receive) as values.
        """
        conversions: dict[str, tuple[float, float]] = {}

        # Generate conversion rates for each resource
        for resource in self.resources:
            conversions[resource] = (
                random.uniform(
                    self.give_lower_bound, self.give_upper_bound
                ),  # Give conversion rate
                random.uniform(
                    self.receive_lower_bound, self.give_upper_bound
                ),  # Receive conversion rate
            )

        return conversions

    def get_receive_conversion(self, give_amount: int, receive_resource: str) -> int:
        """
        Calculates how much of a resource a player will receive based on the
        amount they are giving and the conversion rate.

        :param give_amount: The amount of the resource being given in the trade.
        :param receive_resource: The resource that will be received in the trade.
        :return: The amount of the received resource after applying the conversion rate.
        """
        # Retrieve the receiving conversion rate for the given resource
        receive_rate: float = self.engine.trade_conversions[
            self.engine.turn_count_actual
        ][receive_resource][1]

        # Calculate the amount received based on the given amount and the rate
        receive_amount: int = round(give_amount * receive_rate)

        # Ensure a minimum value of 1 is returned if the amount is 0
        if receive_amount == 0:
            receive_amount = 1

        return receive_amount

    def get_give_conversion(self, give_resource: str, player: "Player") -> int:
        """
        Calculates how much of a resource a player needs to give based on the
        conversion rate and the amount available to the player.

        :param give_resource: The resource that is being given in the trade.
        :param player: The player whose resource amount is being used for the trade.
        :return: The amount of the given resource after applying the conversion rate.
        """
        # Get the available amount of the given resource from the player
        amount: int = getattr(player, give_resource)

        # Retrieve the give conversion rate for the given resource
        give_rate: float = self.engine.trade_conversions[self.engine.turn_count_actual][
            give_resource
        ][0]

        # Calculate the amount to give based on the available amount and the rate
        give_amount: float = amount * give_rate

        # Ensure a minimum value of 1 is returned if the amount is 0
        if give_amount == 0:
            give_amount = 1

        return round(give_amount)
