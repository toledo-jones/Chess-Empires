from chess_empires.utilities.singleton import Singleton
import threading


class EventManager(Singleton):
    def __init__(self):
        self.listeners = {}
        self.listeners_lock = threading.Lock()

    def multi_subscribe(self, events: dict):
        for key in events.keys():
            stored_key = str(key)
            self.subscribe(stored_key, events[key])

    def subscribe(self, event_type, callback):
        event_type = str(event_type)
        # with self.listeners_lock:
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        # self.release_lock()

    def unsubscribe(self, event_type, callback):
        event_type = str(event_type)
        # with self.listeners_lock:
        if event_type in self.listeners:
            if callback in self.listeners[event_type]:
                self.listeners[event_type].remove(callback)
                if not self.listeners[event_type]:
                    del self.listeners[event_type]
        # self.release_lock()

    def emit(self, event_type, data):
        event_type = str(event_type)
        # with self.listeners_lock:
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(data)
        # self.release_lock()

    def multi_unsubscribe(self, events: dict):
        for key in events.keys():
            stored_key = str(key)
            self.unsubscribe(stored_key, events[key])

    def acquire_lock(self):
        print("acquiring lock")
        self.listeners_lock.acquire(timeout=1)

    def release_lock(self):
        print("Release Lock?")
        if self.listeners_lock.locked():
            print("Yes... releasing... ")
            self.listeners_lock.release()
        else:
            print("No")
