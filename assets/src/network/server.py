"""

Holds multiple games of Chess-Empires

"""
import socket
import threading


class GameServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.game_scene = DefaultGameScene
        self.data_handlers = {
            'mouse_movement': self.handle_mouse_movement,
            # Add more data types and corresponding handlers as needed
        }

    def set_game_scene(self, game_scene):
        self.game_scene = game_scene

    def process_data(self, data):
        data_type = data.get('type')
        handler = self.data_handlers.get(data_type)
        if handler:
            handler(data)
        else:
            print(f"Unsupported data type: {data_type}")

    def handle_mouse_movement(self, data):
        player_id = data.get('player_id')
        x = data.get('x')
        y = data.get('y')

        # Update the game scene with the mouse movement data
        self.game_scene.update_mouse_position(player_id, x, y)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}")

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()
            self.clients.append(client_thread)

    @staticmethod
    def handle_client(client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received data from client: {data.decode('utf-8')}")
                # Add your game logic for handling client data here

        except Exception as e:
            print(f"Error handling client: {e}")

        finally:
            client_socket.close()


if __name__ == "__main__":
    server = GameServer("127.0.0.1", 5555)
    server.start()
