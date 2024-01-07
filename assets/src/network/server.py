"""

Holds multiple games of Chess-Empires

"""
import json
import pickle
import socket
import threading

from assets.src.game.state_manager import StateManager
from assets.src.utilities.event_system import EventSystem
from assets.src.game.scenes import SceneFactory

class GameServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.event_system = EventSystem()
        self.state_manager = StateManager(self.event_system)
        self.current_scene = SceneFactory.create("GameScene", self.event_system, self.state_manager)
        self.data_handlers = {
            'mouse move': self.handle_mouse_movement,
            # Add more data types and corresponding handlers as needed
        }
        self.clients = {}
        self.current_player_id = 1

    def handle_mouse_movement(self, data):
        player_id = data.get('player_id')
        x = data.get('x')
        y = data.get('y')

        event_data = {'type': 'mouse move', 'player_id': player_id, 'x': x, 'y': y}
        self.event_system.emit(event_data['type'], event_data)
        print(f"Received mouse movement from Player {player_id}: x={x}, y={y}")
        print("Sending to clients...")
        self.broadcast_event_to_clients('mouse_move', event_data)
        # Update the game scene with the mouse movement data
        # self.game_scene.update_mouse_position(player_id, x, y)

    def broadcast_event_to_clients(self, event_type, event_data):
        # Iterate over connected clients and send the event data to each client
        for client_socket in self.clients.keys():
            try:
                # Serialize the event data and send it to the client
                serialized_data = pickle.dumps({'type': event_type, 'data': event_data})
                client_socket.sendall(serialized_data)
            except Exception as e:
                print(f"Error broadcasting event to client: {e}")

    def process_data(self, data):
        try:
            if isinstance(data, str):
                # If data is a string, try to convert it to a dictionary
                data_dict = json.loads(data)

            elif isinstance(data, bytes):
                # If data is bytes, assume it's pickled and decode it
                data_dict = pickle.loads(data)
            elif isinstance(data, dict):
                # If data is already a dictionary, use it directly
                data_dict = data
            else:
                print(f"Unsupported data type: {type(data)}")
                return

            data_type = data_dict.get('type')
            handler = self.data_handlers.get(data_type)
            if handler:
                handler(data_dict)
            else:
                print(f"Unsupported data type: {data_type}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
        except Exception as e:
            print(f"Error processing data: {e}")

    def handle_client(self, client_socket, _server):
        try:
            player_id = self.current_player_id
            self.current_player_id += 1

            self.clients[client_socket] = player_id

            # Send the player ID to the client
            client_socket.sendall(str(player_id).encode('utf-8'))

            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                # Process the received data, including the player ID
                self.process_data(data)

        except Exception as e:
            print(f"Error handling client: {e}")

        finally:
            # Remove the client from the dictionary when it disconnects
            del self.clients[client_socket]
            client_socket.close()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}")

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, self))
            client_thread.start()
            self.clients[client_socket] = client_thread


if __name__ == "__main__":
    server = GameServer("192.168.1.149", 5555)
    server.start()
