from chess_empires.game.states.state import State
from chess_empires.utilities.singleton import Singleton
from utilities.factories.state_factory import StateFactory


class StateManager(Singleton):
    def __init__(self, event_manager):
        self._current_state = None
        self.event_manager = event_manager

    def set_state(self, state_name, *args, **kwargs):
        # Use the SceneFactory to dynamically create the scene
        new_state = StateFactory.create(state_name, self.event_manager, self, *args, **kwargs)

        print(f"New Scene is instance of BaseScene:{isinstance(new_state, State)}")
        if isinstance(new_state, State):  # Ensure it's an instance of BaseState
            if self._current_state:
                self._current_state.exit()  # Optional: Call exit method of the current scene

            self._current_state = new_state
            self._current_state.enter()
            print(f"Created New State: {new_state}")

        else:
            print(new_state)
            print(f"Error: Unable to create state '{state_name}'.")

    @property
    def current_state(self):
        return self._current_state

    def update(self):
        if self.current_state:
            self._current_state.update()

    def enter(self):
        if self.current_state:
            self._current_state.enter()

    def render(self):
        if self.current_state:
            self._current_state.render()
