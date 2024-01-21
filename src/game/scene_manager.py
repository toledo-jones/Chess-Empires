from src.game.scenes.base_scene import BaseScene
from utilities.factories.scene_factory import SceneFactory
from src.utilities.singleton import Singleton


class SceneManager(Singleton):
    def __init__(self, event_system, state_manager):
        self._current_scene = None
        self.event_system = event_system
        self.state_manager = state_manager

    def set_scene(self, scene_name, *args, **kwargs):
        # Use the SceneFactory to dynamically create the scene
        new_scene = SceneFactory.create(scene_name, self.event_system, self, self.state_manager, *args, **kwargs)
        print(f"New Scene is instance of BaseScene:{isinstance(new_scene, BaseScene)}")
        if isinstance(new_scene, BaseScene):  # Ensure it's an instance of BaseScene
            if self._current_scene:
                self._current_scene.exit()  # Optional: Call exit method of the current scene

            self._current_scene = new_scene
            self._current_scene.enter()
            print(f"Created New Scene: {new_scene}")
        else:
            print(f"Error: Unable to create scene '{scene_name}'.")

    @property
    def current_scene(self):
        return self._current_scene

    def update(self):
        if self.current_scene is not None:
            self._current_scene.update()
            self.state_manager.update()

    def enter(self):
        if self.current_scene is not None:
            self._current_scene.enter()
            self.state_manager.enter()

    def render(self):
        if self.current_scene is not None:
            self._current_scene.render()
            self.state_manager.render()
