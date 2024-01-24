import settings
from src.game.entities.tile import Tile
import pygame
import random


class Board:
    def __init__(self, event_manager):
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
        self.tile_pattern = [[None] * self.rows for _ in range(self.cols)]

    def set_tile_pattern(self, tree_tile_sprites):
        light_tile_sprites = tree_tile_sprites[0]
        dark_tile_sprites = tree_tile_sprites[1]
        for col in range(self.cols):
            for row in range(self.rows):
                # Alternate colors based on row and column indices
                if (row + col) % 2 == 0:
                    tile_sprites = light_tile_sprites
                else:
                    tile_sprites = dark_tile_sprites
                texture_path = random.choice(list(tile_sprites.keys()))
                tree_texture_surface = pygame.transform.scale(tile_sprites[texture_path], (self.sq_size+2, self.sq_size+2))
                self.tile_pattern[col][row] = tree_texture_surface.convert_alpha()

    def render_tiles(self, light_color, dark_color, engine):
        for col in range(self.cols):
            for row in range(self.rows):
                x = col * self.sq_size
                y = row * self.sq_size

                # Alternate colors based on row and column indices
                if (row + col) % 2 == 0:
                    color = light_color
                else:
                    color = dark_color

                pygame.draw.rect(self.surface, color, (x-1, y-1, self.sq_size+2, self.sq_size+2), 0)
                self.surface.blit(self.tile_pattern[col][row], (x-1, y-1), special_flags=pygame.BLEND_RGBA_MULT)
                to_be_rendered = self.tiles[col][row].render(self)
                for item in to_be_rendered:
                    self.event_manager.emit('draw sprite', item)

