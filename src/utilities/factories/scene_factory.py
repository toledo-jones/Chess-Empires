from src.utilities.factories.base_factory import BaseFactory, auto_register, DefaultClass
from src.game.scenes.base_scene import BaseScene


class SceneFactory(BaseFactory):
    _default_class = DefaultClass


# Automatically discover and register scene classes
auto_register(SceneFactory, "game.scenes", BaseScene)
