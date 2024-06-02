from __future__ import annotations

import typing
import random
from chess_empires.game.entities.sprite import Sprite
from chess_empires.game.db import Input

from game.scene import Scene

if typing.TYPE_CHECKING:
    from chess_empires.game.event_manager import EventManager
    from chess_empires.game.scene_manager import SceneManager
    from chess_empires.game.state_manager import StateManager


class Title(Scene):
    def __init__(self,
                 event_manager: EventManager,
                 scene_manager: SceneManager,
                 state_manager: StateManager):
        events = {
            Input.LEFT_CLICK: self.left_click
        }
        super().__init__(event_manager, scene_manager, state_manager, events)


        menu_colors = ['black', 'white']
        self.menu = Sprite(f"assets/sprites/icons/logo/{random.choice(menu_colors)}/0.png")

    def left_click(self, data):
        print("triggered click")
        self.scene_manager.set_scene("Playing")

    def enter(self):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def exit(self):
        # Final call will always be super().exit()
        super().exit()

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def menu(self, menu: Sprite):
        self._menu = menu
