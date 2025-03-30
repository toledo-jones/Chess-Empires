import socket
import threading
import json
import pickle
import typing


class GameServer:
    """
    Holds multiple games of Chess-Empires and manages client connections.
    """

    def __init__(self, host: str, port: int):
        """
        Initializes the GameServer with the specified host and port.

        :param host: The host address for the server.
        :param port: The port number for the server.
        """
        self.host: str = host
        self.port: int = port
        self.clients_lock: threading.Lock = threading.Lock()
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: dict[socket.socket, int] = {}
        self.client_threads: dict[socket.socket, threading.Thread] = {}
        self.data_handlers: dict[str, typing.Callable] = {
            'mouse move': self.handle_mouse_movement,
        }
        self.current_player_id: int = 1

    def handle_mouse_movement(self, data: dict):
        """
        Handles mouse movement data from clients.

        :param data: The data received from the client.
        """
        # Broadcast the mouse movement event to all clients
        self.broadcast_event_to_clients('mouse move', data)

    def broadcast_event_to_clients(self, event_type: str, event_data: dict):
        """
        Broadcasts an event to all connected clients.

        :param event_type: The type of event to broadcast.
        :param event_data: The data associated with the event.
        """
        # Iterate over connected clients and send the event data to each client
        for client_socket in list(self.clients.keys()):
            try:
                # Check if the socket is still valid
                if client_socket.fileno() != -1:
                    # Serialize the event data and send it to the client
                    serialized_data: bytes = pickle.dumps({'type': event_type, 'data': event_data})
                    client_socket.sendall(serialized_data)
            except Exception as e:
                print(f"Error broadcasting event to client: {e}")

    def process_data(self, data: typing.Union[str, bytes, dict]):
        """
        Processes the data received from clients.

        :param data: The data received from the client.
        """
        try:
            if isinstance(data, str):
                # If data is a string, try to convert it to a dictionary
                data_dict: dict = json.loads(data)
            elif isinstance(data, bytes):
                # If data is bytes, assume it's pickled and decode it
                data_dict: dict = pickle.loads(data)
            elif isinstance(data, dict):
                # If data is already a dictionary, use it directly
                data_dict = data
            else:
                print(f"Unsupported data type: {type(data)}")
                return

            data_type: str = data_dict.get('type')
            handler: typing.Optional[typing.Callable] = self.data_handlers.get(data_type)
            if handler:
                handler(data_dict)
            else:
                print(f"Unsupported data type: {data_type}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
        except Exception as e:
            print(f"Error processing data: {e}")

    def handle_client(self, client_socket: socket.socket, client_address: tuple[str, int]):
        """
        Handles communication with a connected client.

        :param client_socket: The socket object for the client.
        :param client_address: The address of the client.
        """
        try:
            player_id: int = self.current_player_id
            self.current_player_id += 1

            with self.clients_lock:
                self.clients[client_socket] = player_id

            # Send the player ID to the client
            client_socket.sendall(str(player_id).encode('utf-8'))

            while True:
                data: bytes = client_socket.recv(1024)
                if not data:
                    break

                # Process the received data, including the player ID
                self.process_data(data)

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            # Remove the client from the dictionary when it disconnects
            with self.clients_lock:
                if client_socket in self.clients:
                    del self.clients[client_socket]
                    client_socket.close()
                    print(f"Closed connection for {client_address}")

    def start(self):
        """
        Starts the game server and listens for incoming client connections.
        """
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}")

            client_thread: threading.Thread = threading.Thread(target=self.handle_client,
                                                               args=(client_socket, client_address))
            client_thread.start()
            self.client_threads[client_socket] = client_thread


if __name__ == "__main__":
    server = GameServer("192.168.1.149", 5555)
    server.start()
