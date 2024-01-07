from assets.src.game.scenes.base_scene import BaseScene
from assets.src.utilities.class_discovery import discover_classes


class SceneFactory:
    _registry = {}

    @classmethod
    def register(cls, scene_class):
        cls._registry[scene_class.__name__.lower()] = scene_class

    @classmethod
    def create(cls, scene_name, *args, **kwargs):
        scene_class = cls._registry.get(scene_name.lower(), DefaultScene)
        return scene_class(*args, **kwargs)


class DefaultScene:
    pass


# Automatically discover and register scene classes
scene_classes = discover_classes("assets.src.game.scenes", BaseScene)
for scene_class in scene_classes:
    SceneFactory.register(scene_class)
