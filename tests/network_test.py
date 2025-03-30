# client_example.py
from client import GameClient
import time


class DummyEventManager:
    def handle_event(self, event):
        print(f"Handling event: {event}")


class DummyGameManager:
    def execute_game_event(self, event):
        print(f"Executing game event: {event}")


if __name__ == "__main__":
    event_manager = DummyEventManager()
    game_manager = DummyGameManager()

    client = GameClient("192.168.1.114", 5555, event_manager)
    client.game_manager = game_manager
    client.connect()
    client.start_listening_thread()

    # Example of sending a string message to the server
    client.send_string("Hello, Server!")

    # Example of sending an object to the server
    client.send_object({"action": "move", "direction": "up"})

    # Keep the client running to listen for server events
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.close()