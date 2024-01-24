from src.utilities.factories.base_factory import BaseFactory, auto_register, DefaultClass
from src.game.scenes.scene import Scene


class SceneFactory(BaseFactory):
    _default_class = DefaultClass


# Automatically discover and register scene classes
auto_register(SceneFactory, "game.scenes", Scene)
