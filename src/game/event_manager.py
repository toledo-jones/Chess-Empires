from src.utilities.singleton import Singleton
import threading
from jsonschema import validate

# TODO: Enforce event schemas
# event_schema = {
#     "type": "object",
#     "properties": {
#         "event_type": {"type": "string"},
#         "data": {"type": "object"}
#     },
#     "required": ["event_type", "data"]
# }
#
# event_data = {"event_type": "player_move", "data": {"x": 10, "y": 20}}
#
# validate(instance=event_data, schema=event_schema)


class EventManager(Singleton):
    def __init__(self):
        self.listeners = {}
        self.listeners_lock = threading.Lock()

    def subscribe(self, event_type, callback):
        with self.listeners_lock:
            if event_type not in self.listeners:
                self.listeners[event_type] = []
            self.listeners[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        with self.listeners_lock:
            if event_type in self.listeners:
                if callback in self.listeners[event_type]:
                    self.listeners[event_type].remove(callback)
                    if not self.listeners[event_type]:
                        del self.listeners[event_type]

    def emit(self, event_type, data):
        with self.listeners_lock:
            if event_type in self.listeners:
                for callback in self.listeners[event_type]:
                    callback(data)
