import importlib
import inspect
import pkgutil


def discover_classes(package_name, base_class):
    classes = []
    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.walk_packages(package.__path__):
        module = importlib.import_module(f"{package_name}.{module_name}")

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, base_class) and obj != base_class:
                classes.append(obj)

    return classes
