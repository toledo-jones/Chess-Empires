from src.game.scenes.base_scene import BaseScene
from src.utilities.class_discovery import discover_classes


class SceneFactory:
    _registry = {}

    @classmethod
    def register(cls, _scene_class):
        cls._registry[_scene_class.__name__.lower()] = _scene_class
        print(f"registering {_scene_class.__name__}")

    @classmethod
    def create(cls, scene_name, *args, **kwargs):
        print(f"attempting to create {scene_name}")
        _scene_class = cls._registry.get(scene_name.lower(), DefaultScene)
        return _scene_class(*args, **kwargs)


class DefaultScene:
    pass

# Automatically discover and register state classes
scene_classes = discover_classes("game.scenes", BaseScene)
for scene_class in scene_classes:
    SceneFactory.register(scene_class)
