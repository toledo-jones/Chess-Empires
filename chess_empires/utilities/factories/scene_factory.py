from chess_empires.utilities.factories.base_factory import BaseFactory, auto_register, DefaultClass
from chess_empires.game.scenes.scene import Scene


class SceneFactory(BaseFactory):
    _default_class = DefaultClass


# Automatically discover and register scene classes
auto_register(SceneFactory, "game.scenes", Scene)
