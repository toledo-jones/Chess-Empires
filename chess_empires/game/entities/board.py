from __future__ import annotations
import typing
import settings
from chess_empires.game.entities.tile import Tile
import pygame
import random

if typing.TYPE_CHECKING:
    from chess_empires.game.event_manager import EventManager


class Board:
    def __init__(self, event_manager: EventManager):
        """
        Board object contains tile objects which represent each of the individual cells of the game board
        :param event_manager: allows board to listen for game events
        """
        self.event_manager = event_manager

        # Set rows and cols for board
        self.columns = 14
        self.rows = 10

        # Set buffer for the board to be set in from the top of the screen
        window_width, window_height = settings.LOGICAL_GAME_WINDOW
        self.window_buffer = window_height // 10

        # Determine the square size based on how large the board will be after it is set in from the top of the window
        self.sq_size = (window_height - self.window_buffer) / self.rows

        # Create the board surface
        self.width = self.sq_size * self.columns
        self.height = self.sq_size * self.rows
        self.surface = pygame.Surface((self.width, self.height)).convert_alpha()

        # Create the multi dimensional list which contains all the tiles for the board
        self.tiles = [[Tile(x, y) for y in range(self.rows)] for x in range(self.columns)]

        # Perform initial scaling of the tiles.
        self.scale_tiles()

    def handle_resize_event(self, new_size: tuple[int, int]) -> None:
        """
        Called each time the window is resized so the board can be adjusted accordingly
        :param new_size: size, in pixels, of the new game window
        """
        # Calculate the new window buffer based on the new size of the game window.
        self.window_buffer = new_size[1] // 10

        # Square size the game window minus the buffer / number of rows
        self.sq_size = (new_size[1] - self.window_buffer) / self.rows

        # Total width and height of the board surface
        self.width = self.sq_size * self.columns
        self.height = self.sq_size * self.rows

        # Reset the board surface
        self.surface = pygame.transform.scale(self.surface, (self.width, self.height))

        # Scale each tile to correspond with the new sizes
        self.scale_tiles()

    def scale_tiles(self) -> None:
        """
        Scales the tile images to the proper size
        """
        for row in self.tiles:
            for tile in row:
                # Reload default surface from the path and then scale to the appropriate size
                tile.reload_surface_and_scale((self.sq_size + 2, self.sq_size + 2))

    def render_tiles(self) -> None:
        """
        Each frame renders all the tiles to the board surface
        """
        for row in self.tiles:
            for tile in row:
                x = tile.column * self.sq_size
                y = tile.row * self.sq_size
                pygame.draw.rect(self.surface, tile.color, (x - 1, y - 1, self.sq_size + 2, self.sq_size + 2), 0)
                self.surface.blit(tile.image, (x - 1, y - 1), special_flags=pygame.BLEND_RGBA_MULT)
                # to_be_rendered = self.tiles[col][row].render(self)
                # for item in to_be_rendered:
                #     self.event_manager.emit('draw sprite', item)
