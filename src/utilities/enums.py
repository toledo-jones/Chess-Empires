from enum import Enum


class SceneName(Enum):
    MAIN_MENU = "main_menu"
    GAME_SCENE = "game_scene"
    PAUSE_SCENE = "pause_scene"
    WIN_LOSE_SCENE = "win_lose_scene"


class StateName(Enum):
    MINING = "mining"
    SPAWNING = "spawning"
    STEALING = "stealing"


class EventType(Enum):
    DRAW_SPRITE = "draw_sprite"
    MOUSE_MOVE = "mouse_move"
    KEY_PRESSED = "keys"
    SELECT = "select"
