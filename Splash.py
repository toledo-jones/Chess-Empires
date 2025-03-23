import os
import random
import time

import pygame


class SplashScreen:
    # Constants for splash screen
    LOGO_COLORS = {0: "w", 1: "b"}
    LOGO_FOLDER = "files/images"
    DISPLAY_TIME = 2.0  # Time  for splash screen to show

    def __init__(
        self,
        window: pygame.Surface,
        logo_size: tuple = (400, 400),
    ):
        """
        Creates a splash screen object
        """

        self.window = window
        self.logo_size = logo_size
        self.logo_color = self.LOGO_COLORS[random.randint(0, 1)]
        self.logo_image = self.load_logo()

        # Calculate the position of the logo (centered)
        self.logo_position = (
            self.window.get_width() // 2 - self.logo_size[0] // 2,
            self.window.get_height() // 3 - self.logo_size[1] // 2,
        )

    def load_logo(self) -> pygame.Surface:
        """Load the logo image with a random color."""
        logo_path = os.path.join(self.LOGO_FOLDER, f"{self.logo_color}_game_name.png")

        try:
            logo = pygame.image.load(logo_path)
            logo = pygame.transform.scale(logo, self.logo_size)
            return logo
        except pygame.error as e:
            raise FileNotFoundError(f"Logo file not found at {logo_path}")

    def display(self):
        """Display the splash screen and wait for a specified amount of time."""
        self.window.fill((72, 61, 139))  # Fill with background color

        self.window.blit(self.logo_image, self.logo_position)
        pygame.display.update()