from pathlib import Path
import os


class SpriteFactory:
    ungrouped_paths = {}
    grouped_paths = {}

    @classmethod
    def discover_sprite_paths(cls, base_path):
        sprite_paths = []

        # Get the current working directory
        current_directory = Path.cwd()

        # Combine the current directory with the specified relative base path using os.path
        base_path = os.path.normpath(os.path.join(str(current_directory), base_path))

        for path in Path(base_path).rglob("*"):
            if path.is_file() and path.suffix == ".png":
                sprite_paths.append(path.relative_to(base_path))

        return sprite_paths

    @classmethod
    def load_images(cls, sprite_paths, base_path):
        ungrouped_paths = {}
        for sprite_path in sprite_paths:
            image_path = Path(base_path) / sprite_path
            ungrouped_paths[str(sprite_path)] = image_path

        cls.ungrouped_paths = ungrouped_paths
        return ungrouped_paths

    @classmethod
    def delineate_sprite_dictionary(cls, ungrouped_sprites: dict[str, Path]) -> dict[str, dict]:
        """
        Changes the sprite dictionary structure to be referenced like:
        sprites['entities']['units']['white']['acrobat.png']
        :param ungrouped_sprites: Dictionary of paths to pygame surfaces
        :return: A nested dictionary structure organizing different groupings of sprites
        """
        grouped_paths = {}

        # Iterate through ungrouped_sprites and build the nested dictionary structure
        for path, surface in ungrouped_sprites.items():
            directory_structure = path.split("/")
            cls.add_to_grouped_sprites(grouped_paths, directory_structure, surface)

        # Now grouped_paths contains the nested dictionary structure
        cls.grouped_paths = grouped_paths
        return grouped_paths

    @classmethod
    def add_to_grouped_sprites(cls,
                               nested_dict: dict[str, dict],
                               keys: list[str],
                               surface: any) -> None:
        """
        Recursively adds a surface to the nested dictionary structure based on the keys.
        :param nested_dict: The nested dictionary to which the surface is added
        :param keys: List of keys representing the hierarchy in the dictionary
        :param surface: The pygame.Surface associated with the given path
        :return: None
        """
        if len(keys) == 1:
            # If there is only one key left, assign the surface to that key
            nested_dict[keys[0]] = surface
        else:
            key = keys[0]
            if key not in nested_dict:
                # If the key is not present, create an empty dictionary for it
                nested_dict[key] = {}
            # Recursively call add_to_grouped_sprites with the next level of keys
            cls.add_to_grouped_sprites(nested_dict[key], keys[1:], surface)

