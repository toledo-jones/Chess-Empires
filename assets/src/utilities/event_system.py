from assets.src.utilities.singleton import Singleton
import threading


class EventSystem(Singleton):
    def __init__(self):
        self.listeners = {}
        self.listeners_lock = threading.Lock()

    def subscribe(self, event_type, callback):
        with self.listeners_lock:
            if event_type not in self.listeners:
                self.listeners[event_type] = []
            self.listeners[event_type].append(callback)

    def emit(self, event_type, data):
        with self.listeners_lock:
            if event_type in self.listeners:
                for callback in self.listeners[event_type]:
                    callback(data)