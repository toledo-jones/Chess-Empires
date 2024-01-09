from pathlib import Path
import pygame


class SpriteFactory:
    loaded_images = {}

    @classmethod
    def discover_sprite_paths(cls, base_path):
        sprite_paths = []

        # Get the current working directory
        current_directory = Path.cwd()

        # Combine the current directory with the specified relative base path
        base_path = current_directory / Path(base_path)
        base_path = base_path.resolve()

        print("Base Path:", base_path)

        for path in base_path.rglob("*"):
            if path.is_file() and path.suffix == ".png":
                sprite_paths.append(path.relative_to(base_path))


        return sprite_paths

    @classmethod
    def load_images(cls, sprite_paths, base_path):
        loaded_images = {}
        for sprite_path in sprite_paths:
            image_path = Path(base_path) / sprite_path
            image = pygame.image.load(image_path)
            loaded_images[str(sprite_path)] = image

        cls.loaded_images = loaded_images
        return loaded_images


# Remember the script thinks the /src is the "home" directory
base_path = "assets/sprites"  # Adjust the relative path as needed
all_sprite_paths = SpriteFactory.discover_sprite_paths(base_path)

if not all_sprite_paths:
    print("No sprite paths found.")
else:
    loaded_images = SpriteFactory.load_images(all_sprite_paths, Path(base_path))

