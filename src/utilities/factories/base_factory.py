from src.utilities.class_discovery import discover_classes


class BaseFactory:
    _registry = {}
    _default_class = None

    @classmethod
    def register(cls, _class):
        cls._registry[_class.__name__.lower()] = _class

    @classmethod
    def create(cls, name, *args, **kwargs):
        _class = cls._registry.get(name.lower(), cls._default_class)
        return _class(*args, **kwargs)


class DefaultClass:
    pass


# Automatically discover and register classes
def auto_register(factory, package, base_class):
    classes = discover_classes(package, base_class)
    for _class in classes:
        factory.register(_class)

