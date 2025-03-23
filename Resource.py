import random
from typing import Optional, Tuple

import Constant


class Resource:
    """Represents a resource on the game board that can be harvested."""

    def __init__(self, row: int, col: int, owner: Optional[str] = None) -> None:
        """
        Initializes a resource object.

        :param row: The row position of the resource.
        :param col: The column position of the resource.
        :param owner: The owner of the resource (if any).
        """
        # Row position of the resource
        self.row: int = row

        # Column position of the resource
        self.col: int = col

        # Owner of the resource, if applicable
        self.owner: Optional[str] = owner

        # Sprite offset for rendering
        self.sprite_offset: Optional[Tuple[int, int]] = None

        # Determine resource key based on predefined constants
        self.key: Optional[str] = Constant.RESOURCE_YIELD_KEY.get(str(self))

        # Initialize harvesting-related attributes if key is valid
        if self.key is not None:
            # Total available yield
            self.remaining: int = self.get_total_yield()

            # Variance in yield per harvest
            self.harvest_yield_variance: list[int] = []
            self.harvest_yield_variance.append(self.get_harvest_yield_variance())

            # Index tracking harvest attempts
            self.harvest_history: int = -1

        # Set sprite offset if not already defined
        if self.sprite_offset is None:
            self.sprite_offset = self.get_resource_offset()

    def get_harvest_yield_variance(self) -> int:
        """
        Determines the variance in resource yield during harvesting.

        :return: Randomized variance value within predefined bounds.
        """
        # Fetch the variance range for the resource type
        variance_range = Constant.HARVEST_YIELD_VARIANCE[self.key]

        # Randomly return a variance within the range
        return random.randint(variance_range[0], variance_range[1])

    def harvest(self, piece: str) -> int:
        """
        Harvests the resource and updates the remaining yield.

        :param piece: The type of unit harvesting the resource.
        :return: The actual harvested yield.
        """
        # Extend variance history if all previous values are used
        if self.harvest_history == len(self.harvest_yield_variance) - 1:
            self.harvest_history += 1
            self.harvest_yield_variance.append(self.get_harvest_yield_variance())

        # Determine base harvest amount
        base_harvest = Constant.BASE_YIELD_PER_HARVEST[piece][self.key]

        # Apply variance
        harvest_yield = base_harvest + self.harvest_yield_variance[self.harvest_history]

        # Ensure harvested amount does not exceed remaining resource
        if self.remaining < harvest_yield:
            harvest_yield = self.remaining

        # Deduct harvested amount from resource
        self.remaining -= harvest_yield
        return harvest_yield

    def undo_harvest(self, harvest: int) -> None:
        """
        Reverts a harvest operation by restoring the resource yield.

        :param harvest: The amount to restore.
        """
        # Restore the resource yield
        self.remaining += harvest

    def get_total_yield(self) -> int:
        """
        Calculates the total available yield for this resource.

        :return: The total resource yield after applying variance.
        """
        # Base yield amount
        base_yield = Constant.BASE_TOTAL_YIELD[self.key]

        # Yield variance range
        variance_range = Constant.TOTAL_YIELD_VARIANCE[self.key]

        # Random variance
        total_variation = random.randint(variance_range[0], variance_range[1])

        # Return the total yield
        return base_yield + total_variation

    def get_resource_offset(self) -> Tuple[int, int]:
        """
        Calculates the offset for positioning the resource sprite.

        :return: The x and y offset for positioning the resource sprite.
        """
        # Retrieve the size of the resource image as a tuple (width, height)
        image_size = Constant.RESOURCES_IMAGE_MODIFY[str(self)]["SCALE"]

        # Get the size of the square where the image will be placed
        square_size = Constant.SQ_SIZE

        # Calculate the horizontal offset to center the image within the square
        offset_x = (square_size - image_size[0]) // 2

        # Calculate the vertical offset to center the image within the square
        offset_y = (square_size - image_size[1]) // 2

        # Generate a small random offset within approximately ±1/10th of the square size
        random_offset_x = random.randint(-square_size // 10, square_size // 10)
        random_offset_y = random.randint(-square_size // 10, square_size // 10)

        # Apply the random offset to the calculated position
        offset_x += random_offset_x
        offset_y += random_offset_y

        # Return the final computed offsets as a tuple (x, y)
        return offset_x, offset_y

    def get_position(self) -> Tuple[int, int]:
        """
        Retrieves the position of the resource on the board.

        :return: A tuple containing the row and column of the resource.
        """
        # Return the position of the resource (row, col)
        return self.row, self.col

    def get_color(self) -> Optional[str]:
        """
        Retrieves the owner (color) of the resource.

        :return: The owner of the resource, if any.
        """
        # Return the owner of the resource
        return self.owner

    def draw(self, win) -> None:
        """
        Draws the resource sprite on the window.

        :param win: The window to draw the sprite on.
        """
        # Retrieve the sprite associated with the resource
        sprite = Constant.RESOURCES[str(self)]

        # Calculate the x and y position of the resource based on its grid location
        x = self.col * Constant.SQ_SIZE + self.sprite_offset[0]
        y = self.row * Constant.SQ_SIZE + self.sprite_offset[1]

        # Draw the resource sprite at the calculated position on the window
        win.blit(sprite, (x, y))


class Gold(Resource):
    def __repr__(self) -> str:
        """
        String representation of the gold resource.

        :return: The string representation of the gold resource.
        """
        # Return a string representation of the gold resource
        return "gold_tile" + "_" + str(self.get_sprite_id())

    def __init__(self, row: int, col: int, owner: Optional[str] = None) -> None:
        """
        Initializes a gold resource object.

        :param row: The row position of the gold resource.
        :param col: The column position of the gold resource.
        :param owner: The owner of the gold resource (if any).
        """
        # Set the sprite ID for the gold resource
        self.sprite_id: int = 1

        # Initialize the base Resource class
        super().__init__(row, col, owner)

    def get_sprite_id(self) -> int:
        """
        Retrieves the sprite ID of the gold resource.

        :return: The sprite ID for the gold resource.
        """
        # Return the sprite ID for the gold resource
        return self.sprite_id


class Wood(Resource):
    def __repr__(self) -> str:
        """
        String representation of the wood resource.

        :return: The string representation of the wood resource.
        """
        # Return a string representation of the wood resource
        return "tree_tile" + "_" + str(self.get_sprite_id())

    def __init__(self, row: int, col: int, owner: Optional[str] = None) -> None:
        """
        Initializes a wood resource object.

        :param row: The row position of the wood resource.
        :param col: The column position of the wood resource.
        :param owner: The owner of the wood resource (if any).
        """
        # Set a random sprite ID for the wood resource between 1 and 8
        sprite_id: int = random.randint(1, 8)
        self.sprite_id = sprite_id

        # Initialize the base Resource class
        super().__init__(row, col, owner)

    def get_sprite_id(self) -> int:
        """
        Retrieves the sprite ID of the wood resource.

        :return: The sprite ID for the wood resource.
        """
        # Return the sprite ID for the wood resource
        return self.sprite_id


class Quarry(Resource):
    def __repr__(self) -> str:
        """
        String representation of the quarry resource.

        :return: The string representation of the quarry resource.
        """
        # Return a string representation of the quarry resource
        return "quarry" + "_" + str(self.get_sprite_id())

    def __init__(self, row: int, col: int, owner: Optional[str] = None) -> None:
        """
        Initializes a quarry resource object.

        :param row: The row position of the quarry resource.
        :param col: The column position of the quarry resource.
        :param owner: The owner of the quarry resource (if any).
        """
        # Set the sprite ID for the quarry resource
        self.sprite_id: int = 1

        # Initialize the base Resource class
        super().__init__(row, col, owner)

    def get_sprite_id(self) -> int:
        """
        Retrieves the sprite ID of the quarry resource.

        :return: The sprite ID for the quarry resource.
        """
        # Return the sprite ID for the quarry resource
        return self.sprite_id


class SunkenQuarry(Resource):
    def __repr__(self) -> str:
        """
        String representation of the sunken quarry resource.

        :return: The string representation of the sunken quarry resource.
        """
        # Return a string representation of the sunken quarry resource
        return "sunken_quarry" + "_" + str(self.get_sprite_id())

    def __init__(self, row: int, col: int, owner: Optional[str] = None) -> None:
        """
        Initializes a sunken quarry resource object.

        :param row: The row position of the sunken quarry resource.
        :param col: The column position of the sunken quarry resource.
        :param owner: The owner of the sunken quarry resource (if any).
        """
        # Set the sprite ID for the sunken quarry resource
        self.sprite_id: int = 1

        # Initialize the base Resource class
        super().__init__(row, col, owner)

    def get_sprite_id(self) -> int:
        """
        Retrieves the sprite ID of the sunken quarry resource.

        :return: The sprite ID for the sunken quarry resource.
        """
        # Return the sprite ID for the sunken quarry resource
        return self.sprite_id


class DepletedQuarry(Resource):
    def __repr__(self) -> str:
        """
        String representation of the depleted quarry resource.

        :return: The string representation of the depleted quarry resource.
        """
        # Return a string representation of the depleted quarry resource
        return "depleted_quarry" + "_" + str(self.get_sprite_id())

    def __init__(self, row: int, col: int, owner: Optional[str] = None) -> None:
        """
        Initializes a depleted quarry resource object.

        :param row: The row position of the depleted quarry resource.
        :param col: The column position of the depleted quarry resource.
        :param owner: The owner of the depleted quarry resource (if any).
        """
        # Set the sprite ID for the depleted quarry resource
        self.sprite_id: int = 1

        # Initialize the base Resource class
        super().__init__(row, col, owner)

    def get_sprite_id(self) -> int:
        """
        Retrieves the sprite ID of the depleted quarry resource.

        :return: The sprite ID for the depleted quarry resource.
        """
        # Return the sprite ID for the depleted quarry resource
        return self.sprite_id
