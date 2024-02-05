import pygame.sprite
from pathlib import Path


def load_surface(path: Path) -> pygame.Surface:
    """
    Load an image from the specified path and return it as a pygame surface.

    :param path: Path to the image file.
    :return: Pygame surface containing the loaded image.
    """
    try:
        surface = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Error loading image at {str(path)}: {e}")
        surface = pygame.Surface((32, 32))  # Placeholder surface in case of an error
    return surface


def rect_from_surface(surface: pygame.Surface) -> pygame.Rect:
    """
    Creates a pygame.Rect based on a surface or returns a default

    :param surface: Surface to derive rect from
    """
    if not surface:
        print(f"No surface found, setting default rect")
        return pygame.Rect(32, 32, 32)
    return surface.get_rect()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, path: Path):
        """
        Initialize a Sprite object with the specified image path.

        :param path: Path to the sprite image.
        """
        super().__init__()
        self.path = path
        self.image = load_surface(path)
        self.rect = rect_from_surface(self.image)

    def reload_surface_and_scale(self, scale: tuple[float, float]) -> pygame.Surface:
        """
        Reload default surface and then scale it
        :param scale: the x and y scaling factor
        :return: scaled surface
        """
        x = scale[0]
        y = scale[1]
        surface = load_surface(self.path)
        self.image = pygame.transform.scale(surface, (x, y))

    @property
    def rect(self):
        """
        Get the pygame.Rect for this sprite
        :return: Pygame rect with the size of this sprite
        """
        return self._rect

    @rect.setter
    def rect(self, rect: pygame.Rect) -> None:
        """
        Set the pygame.Rect for this sprite object

        :param rect:
        """
        self._rect = rect

    @property
    def image(self) -> pygame.Surface:
        """
        Get the pygame surface representing the sprite image.

        :return: Pygame surface containing the sprite image.
        """
        return self._surface

    @image.setter
    def image(self, surface: pygame.Surface) -> None:
        """
        Set the pygame surface for the sprite.

        :param surface: Pygame surface containing the sprite image.
        """
        self._surface = surface

    @property
    def path(self) -> Path:
        """
        Get the path to the sprite image.

        :return: Path to the sprite image.
        """
        return self._path

    @path.setter
    def path(self, path: Path or str):
        """
        Set the path to the sprite image.

        :param path: New path to the sprite image. Accepts Path object or str
        """
        path = Path(path)
        self._path = path
        self._surface = load_surface(path)  # Reload image when the path is changed

