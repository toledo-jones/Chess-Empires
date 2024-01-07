class EventSystem:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)

    def emit(self, event_type, data):
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(data)