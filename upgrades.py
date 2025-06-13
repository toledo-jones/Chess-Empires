from __future__ import annotations

import typing
import constant
from typing import Optional
from map import assign_resource_random_weights, calculate_resource_costs

if typing.TYPE_CHECKING:
    from unit import Unit
    from map import Map


class Upgrades:
    """
    A class that handles the upgrade mechanics in the game.

    This class manages the resources required for upgrades, defines the costs of an upgrade for each upgrade-able piece
    at each turn that it can be upgraded. It also calculates the amounts of resources required for each upgrade
    """

    def __init__(self, engine) -> None:
        """
        Initializes the Upgrades object.
        """
        # The engine object that handles game state and upgrades.
        self.engine = engine

        # Dictionary to hold the upgrade costs for each piece.
        self.upgrade_costs: dict[str, dict[int, dict[str, int]]] = {}

        # list of available pieces for upgrades.
        self.upgrade_able_pieces: list[str] = [
            "castle",
            "stable",
            "barracks",
            "fortress",
            "circus",
        ]

        # Map will hold information about resources. This will be injected by the engine when it is assigned.
        self.map: Optional["Map"] = None

    def generate_upgrade_costs(self) -> None:
        # Generate initial list of upgrade costs for each piece.
        for piece in self.upgrade_able_pieces:
            self.upgrade_costs[piece] = self.generate_upgrade_cost(piece)

    def generate_upgrade_cost(self, piece: str) -> dict[int, dict[str, int]]:
        upgrade_cost: dict[int, dict[str, int]] = {}
        for rank, spawn_list in constant.SPAWN_LISTS[piece].items():
            if rank == -1:
                continue
            total = 0
            for piece in spawn_list:
                total += constant.PIECE_POINT_VALUES[piece]

            total_points = total // len(spawn_list)

            points_to_fill = int(total_points)

            points_per_resource = self.map.points_per_resource
            # Assign random weights for resources
            wood_points, stone_points, gold_points = assign_resource_random_weights(
                points_to_fill * 3
            )

            # Calculate resource costs based on available points
            wood_cost, stone_cost, gold_cost = calculate_resource_costs(
                wood_points, stone_points, gold_points, points_per_resource
            )

            upgrade_cost[rank] = {
                "log": wood_cost,
                "stone": stone_cost,
                "gold": gold_cost,
            }
        return upgrade_cost
