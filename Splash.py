import pygame
import random
import os
import time
import typing


class SplashScreen:
    def __init__(
            self,
            window: pygame.Surface,
            logo_folder: str,
            logo_colors: typing.Dict[int, str],
            logo_size: tuple = (400, 400), display_time: float = 2.0
    ):
        """
        Creates a splash screen object
        """

        self.window = window
        self.logo_folder = logo_folder
        self.logo_colors = logo_colors
        self.logo_size = logo_size
        self.display_time = display_time
        self.logo_color = self.logo_colors[random.randint(0, 1)]
        self.logo_image = self.load_logo()

        # Calculate the position of the logo (centered)
        self.logo_position = (
            self.window.get_width() // 2 - self.logo_size[0] // 2,
            self.window.get_height() // 2 - self.logo_size[1] // 2
        )

    def load_logo(self) -> pygame.Surface:
        """Load the logo image with a random color."""
        logo_path = os.path.join(self.logo_folder, f"{self.logo_color}_game_name.png")

        try:
            logo = pygame.image.load(logo_path)
            logo = pygame.transform.scale(logo, self.logo_size)
            return logo
        except pygame.error as e:
            print(f"Error loading logo: {e}")
            raise FileNotFoundError(f"Logo file not found at {logo_path}")

    def display(self):
        """Display the splash screen and wait for a specified amount of time."""
        self.window.fill((72, 61, 139))  # Fill with background color

        self.window.blit(self.logo_image, self.logo_position)
        pygame.display.update()

        # Wait for the splash screen to display for the specified time
        time.sleep(self.display_time)
