from __future__ import annotations
import typing
import settings
from src.game.entities.tile import Tile
import pygame
import random
if typing.TYPE_CHECKING:
    from src.game.event_manager import EventManager



class Board:
    def __init__(self, event_manager: EventManager):
        """
        Board object contains tile objects which represent each of the individual cells of the game board
        :param event_manager:
        """
        self.event_manager = event_manager

        # Set rows and cols for board
        self.cols = 14
        self.rows = 10

        # Set buffer for the board to be set in from the top of the screen
        window_width, window_height = settings.LOGICAL_GAME_WINDOW
        self.window_buffer = window_height // 10

        # Determine the square size based on how large the board will be after it is set in from the top of the window
        self.sq_size = (window_height - self.window_buffer) / self.rows

        # Create the board surface
        self.width = self.sq_size * self.cols
        self.height = self.sq_size * self.rows
        self.surface = pygame.Surface((self.width, self.height)).convert_alpha()

        self.tiles = [[Tile(x, y) for y in range(self.rows)] for x in range(self.cols)]

    def handle_resize_event(self, new_size):
        self.window_buffer = new_size[1] // 10
        self.sq_size = (new_size[1] - self.window_buffer) / self.rows
        self.width = self.sq_size * self.cols
        self.height = self.sq_size * self.rows
        self.surface = pygame.transform.scale(self.surface, (self.width, self.height))

    def render_tiles(self):
        for row in self.tiles:
            for tile in row:
                x = tile.column * self.sq_size
                y = tile.row * self.sq_size
                pygame.draw.rect(self.surface, tile.color, (x-1, y-1, self.sq_size+2, self.sq_size+2), 0)
                self.surface.blit(tile.image, (x-1, y-1), special_flags=pygame.BLEND_RGBA_MULT)
                # to_be_rendered = self.tiles[col][row].render(self)
                # for item in to_be_rendered:
                #     self.event_manager.emit('draw sprite', item)

