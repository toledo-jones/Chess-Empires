from assets.src.game.scenes import SceneFactory
from assets.src.game.scenes import BaseScene


class SceneManager:
    def __init__(self, event_system):
        self.current_scene = None
        self.event_system = event_system
        self.current_scene = None

    def set_scene(self, scene_name, *args, **kwargs):
        # Use the SceneFactory to dynamically create the scene
        new_scene = SceneFactory.create(scene_name, self.event_system, *args, **kwargs)

        if isinstance(new_scene, BaseScene):  # Ensure it's an instance of BaseScene
            if self.current_scene:
                self.current_scene.exit()  # Optional: Call exit method of the current scene

            self.current_scene = new_scene
            self.current_scene.enter()
        else:
            print(f"Error: Unable to create scene '{scene_name}'.")

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def render(self):
        if self.current_scene:
            self.current_scene.render()
