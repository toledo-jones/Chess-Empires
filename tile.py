import random
from typing import Optional
import typing
if typing.TYPE_CHECKING:
    from unit import Unit, Trap
    from resource import Resource
    import pygame


import constant


class Tile:
    """
    Represents a tile on the game board.

    This class holds information about a tile's position, state, resources,
    and various properties related to highlighting, protection, and portals.
    """

    def __init__(self, row: int, col: int) -> None:
        """
        Initializes a new Tile object.

        :param row: The row position of the tile on the board.
        :param col: The column position of the tile on the board.
        """

        # Initialize the position of the tile
        self.row: int = row
        self.col: int = col

        # Set a random index for the tile
        self.index: int = random.randint(0, 46)

        # Flags for various tile properties
        # Whether the tile can contain a quarry
        self.can_contain_quarry: bool = False

        # Entity occupying the tile (if any)
        self.occupying: Optional["Unit"] = None

        # Resource type present on the tile (if any)
        self.resource: Optional["Resource"] = None

        # Color associated with the tile (if any)
        self.color: Optional[str] = None

        # Whether the tile is protected
        self.protected: bool = False

        # Whether the tile is being highlighted for checking
        self.highlight_check: bool = False

        # Whether the tile is highlighted as unused
        self.highlight_unused: bool = False

        # Whether the tile is highlighted by default
        self.highlight_default: bool = False

        # Whether the tile is self-highlighted
        self.highlight_self: bool = False

        # Protection and portal related attributes
        # Image used when the tile is protected
        self.protected_image: Optional[str] = None

        # Timer for how long the protection lasts
        self.protect_timer: int = 0

        # Image used for the portal
        self.portal_image: Optional[str] = None

        # Offset for the protected image
        self.protect_image_offset: tuple[int, int] = constant.IMAGES_IMAGE_MODIFY[
            "w_protect"
        ]["OFFSET"]

        # Offset for the portal image
        self.portal_image_offset: tuple[int, int] = constant.IMAGES_IMAGE_MODIFY[
            "w_portal"
        ]["OFFSET"]

        # Entity protecting the tile
        self.protected_by: Optional[str] = None

        # Trap and portal related attributes
        # Trap present on the tile (if any)
        self.trap: Optional["Trap"] = None

        # Whether the tile contains a portal
        self.portal: bool = False

        # Color of the portal (if any)
        self.portal_color: Optional[str] = None

        # Tile connected to the portal (if any)
        self.connected_portal: Optional["Tile"] = None

    def set_occupying(self, occupying: Optional["Unit"]) -> None:
        """
        Sets the entity occupying the tile.

        :param occupying: The entity occupying the tile (if any).
        """
        # Set the occupying entity on the tile
        self.occupying = occupying

    def set_resource(self, resource: Optional["Resource"]) -> None:
        """
        Sets the resource present on the tile.

        :param resource: The resource type to set on the tile (if any).
        """
        # Set the resource on the tile
        self.resource = resource

    def has_resource(self) -> bool:
        """
        Checks if the tile has a resource.

        :return: True if the tile has a resource, False otherwise.
        """
        # Return True if the resource is not None
        return self.resource is not None

    def has_occupying(self) -> bool:
        """
        Checks if the tile is occupied.

        :return: True if the tile is occupied, False otherwise.
        """
        # Return True if the tile is occupied
        return self.occupying is not None

    def get_position(self) -> tuple[int, int]:
        """
        Gets the position of the tile on the board.

        :return: A tuple (row, col) representing the tile's position.
        """
        # Return the position of the tile
        return self.row, self.col

    def get_occupying(self) -> Optional["Unit"]:
        """
        Gets the entity occupying the tile.

        :return: The entity occupying the tile (if any).
        """
        # Return the occupying entity
        return self.occupying

    def get_resource(self) -> Optional["Resource"]:
        """
        Gets the resource present on the tile.

        :return: The resource type present on the tile (if any).
        """
        # Return the resource present on the tile
        return self.resource

    def remove_resource(self) -> None:
        """
        Removes the resource from the tile.

        Resets the resource attribute to None.
        """
        # Remove the resource from the tile
        self.resource = None

    def draw_portal_image(self, win) -> None:
        """
        Draws the portal image on the tile at its position.

        :param win: The window surface to draw the image on.
        """
        # Calculate the position of the portal image on the tile
        x: int = (self.col * constant.SQ_SIZE) + self.protect_image_offset[0]
        y: int = (self.row * constant.SQ_SIZE) + self.protect_image_offset[1]

        # Draw the portal image at the calculated position
        win.blit(self.portal_image, (x, y))

    def replace_values(self, protect_values: dict) -> None:
        """
        Replaces the protection values for the tile.

        :param protect_values: A dictionary containing new protection values.
        """
        # Set the protected image, color, and timer
        self.protected_image: Optional[str] = protect_values["image"]
        self.protected_by: Optional[str] = protect_values["color"]
        self.protect_timer: int = protect_values["timer"]

        # Mark the tile as protected
        self.protected: bool = True

    def get_protect_values(self) -> dict:
        """
        Returns the current protection values for the tile.

        :return: A dictionary containing the protection image, color, and timer.
        """
        # Return the protection values as a dictionary
        return {
            "image": self.protected_image,
            "color": self.protected_by,
            "timer": self.protect_timer,
        }

    def draw_protected_image(self, win) -> None:
        """
        Draws the protected image on the tile at its position.

        :param win: The window surface to draw the image on.
        """
        # Calculate the position of the protected image on the tile
        x: int = (self.col * constant.SQ_SIZE) + self.protect_image_offset[0]
        y: int = (self.row * constant.SQ_SIZE) + self.protect_image_offset[1]

        # Draw the protected image at the calculated position
        win.blit(self.protected_image, (x, y))

    def un_tick_protect_timer(self, engine, color: str) -> None:
        """
        Decreases the protection timer and updates the protection status.

        If the protection timer reaches zero, the protection status is reset.

        :param engine: The game engine that controls the state of the game.
        :param color: The color associated with the protection.
        """
        # Flag to track if protection should be re-created
        re_create_protect: bool = False

        # Check if the protection timer is at zero and mark for re-creation
        if self.protect_timer == 0:
            re_create_protect = True

        # Increment the protection timer
        self.protect_timer += 1

        # Re-create protection if necessary
        if re_create_protect:
            self.protected: bool = True
            self.protected_image: Optional[str] = constant.IMAGES[color + "_protect"]
            engine.protected_tiles.append(self)

    def tick_protect_timer(self, engine) -> None:
        """
        Decreases the protection timer and removes protection if the timer reaches zero.

        :param engine: The game engine that controls the state of the game.
        """
        # Decrease the protection timer
        self.protect_timer -= 1

        # If the protection timer reaches zero, remove the protection
        if self.protect_timer == 0:
            self.protected = False
            self.protected_image = None
            engine.protected_tiles.remove(self)

    def remove_protection(self) -> None:
        """
        Removes the protection from the tile.

        Resets protection-related values to their default states.
        """
        # Reset the protection timer
        self.protect_timer = 0

        # Mark the tile as unprotected
        self.protected = False
        self.protected_image = None
        self.protected_by = None

    def protect(self, color: str) -> None:
        """
        Applies protection to the tile.

        :param color: The color that is protecting the tile.
        """
        # Set the protection image based on the color
        self.protected_image = constant.IMAGES[color + "_" + "protect"]

        # Mark the tile as protected
        self.protected = True

        # Set the protection timer
        self.protect_timer = 4

        # Set the color of the protection
        self.protected_by = color

    def create_portal(self, color: str, connected_portal: "Tile") -> None:
        """
        Creates a portal on the tile.

        :param color: The color of the portal.
        :param connected_portal: The portal this tile is connected to.
        """
        # Set the portal image based on the color
        self.portal_image = constant.IMAGES[color + "_" + "portal"]

        # Set the color of the portal
        self.portal_color = color

        # Mark the tile as having a portal
        self.portal = True

        # Set the connected portal
        self.connected_portal = connected_portal

    def remove_portal(self) -> None:
        """
        Removes the portal from the tile.

        Resets the portal-related values.
        """
        # Reset portal-related values
        self.portal_image = None
        self.portal = False

    def is_protected(self) -> bool:
        """
        Checks if the tile is protected.

        :return: True if the tile is protected, False otherwise.
        """
        return self.protected

    def is_portal(self) -> bool:
        """
        Checks if the tile is a portal.

        :return: True if the tile is a portal, False otherwise.
        """
        return self.portal

    def is_protected_by_same_color(self, color: str) -> bool:
        """
        Checks if the tile is protected by the same color.

        :param color: The color to check against.
        :return: True if the tile is protected by the same color, False otherwise.
        """
        # Check if the tile is protected
        return self.protected and color == self.protected_by

    def is_protected_by_opposite_color(self, color: str) -> bool:
        """
        Checks if the tile is protected by the opposite color.

        :param color: The color to check against.
        :return: True if the tile is protected by the opposite color, False otherwise.
        """
        return self.protected and color != self.protected_by

    def has_trap(self) -> bool:
        """
        Checks if the tile has a trap.

        :return: True if the tile has a trap, False otherwise.
        """
        # Return True if the tile has a trap, else False
        return self.trap is not None

    def undo_trap(self) -> None:
        """
        Removes the trap from the tile.
        """
        # Set the trap to None to remove it
        self.trap = None

    def set_trap(self, trap) -> None:
        """
        Sets a trap on the tile.

        :param trap: The trap object to set on the tile.
        """
        # Assign the trap to the tile
        self.trap = trap

    def draw_highlights(self, win: "pygame.Surface") -> None:
        """
        Draws highlights for the tile if it is occupying a unit.

        :param win: The window to draw the highlights on.
        """
        # If the tile is occupied, draw the occupying entity's highlights
        if self.occupying:
            self.occupying.draw_highlights(win)

    def draw(self, win: "pygame.Surface") -> None:
        """
        Draws the tile, including any resources, protection, portal, and occupying entities.

        :param win: The window to draw the tile on.
        """
        # Draw resource if the tile has one
        if self.has_resource():
            self.resource.draw(win)

        # Draw protected image if the tile is protected
        if self.protected:
            self.draw_protected_image(win)

        # Draw portal image if the tile is a portal
        if self.portal:
            self.draw_portal_image(win)

        # Draw the trap if the tile has one
        if self.trap:
            self.trap.draw(win)

        # Draw occupying entity if the tile is occupied
        if self.has_occupying():
            self.occupying.draw(win)
