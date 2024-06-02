from __future__ import annotations

import typing

from game.scene import Scene
from chess_empires.game.db import Input, Render

if typing.TYPE_CHECKING:
    from chess_empires.game.event_manager import EventManager
    from chess_empires.game.scene_manager import SceneManager
    from chess_empires.game.state_manager import StateManager


class Playing(Scene):
    def __init__(self,
                 event_manager: EventManager,
                 scene_manager: SceneManager,
                 state_manager: StateManager):
        events = {
            Input.LEFT_CLICK: self.left_click
        }
        super().__init__(event_manager, scene_manager, state_manager, events)

    def left_click(self, data):
        self.scene_manager.set_scene('Title')

    def enter(self):
        pass

    def update(self):
        pass

    def render(self):
        self.event_manager.emit(Render.BOARD, data={})

    def exit(self):
        super().exit()
