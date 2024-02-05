import importlib
import inspect
import pkgutil
import os


def discover_classes(package_name, base_class):
    classes = []
    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.walk_packages(package.__path__):
        module = importlib.import_module(f"{package_name}.{module_name}")

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, base_class) and obj != base_class:
                classes.append(obj)

    return classes

def discover_classes(package_name, base_class):
    classes = []
    package = importlib.import_module(package_name)

    for root, dirs, files in os.walk(package.__path__[0]):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = os.path.join(root, file)
                module_path = os.path.relpath(module_path, package.__path__[0])
                module_path = module_path.replace(os.path.sep, ".")[:-3]
                module = importlib.import_module(f"{package_name}.{module_path}")

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, base_class) and obj != base_class:
                        classes.append(obj)

    return classes
