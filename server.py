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
        self.current_player_id: int = 0

    def get_client_socket_by_player_id(self, player_id: int) -> typing.Optional[socket.socket]:
        """
        Retrieves the client socket associated with the given player ID.

        :param player_id: The player ID of the target client.
        :return: The socket of the target client, or None if not found.
        """
        with self.clients_lock:
            for client_socket, pid in self.clients.items():
                if pid == player_id:
                    return client_socket
        return None

    def broadcast_event_to_clients(self, event_type: str, event_data: typing.Any, sender_id: int):
        """
        Broadcasts an event to all connected clients except the sender.

        :param event_type: The type of event to broadcast.
        :param event_data: The data associated with the event.
        :param sender_id: The player ID of the client that sent the event.
        """
        for client_socket, player_id in list(self.clients.items()):
            if player_id != sender_id:
                try:
                    if client_socket.fileno() != -1:
                        serialized_data: bytes = pickle.dumps(event_data)
                        client_socket.sendall(serialized_data)
                except Exception as e:
                    print(f"Error broadcasting event to client: {e}")

    def process_data(self, data: typing.Union[str, bytes, typing.Any], sender_id: int):
        """
        Processes the data received from clients and broadcasts it to all clients except the sender.

        :param data: The data received from the client.
        :param sender_id: The player ID of the client that sent the data.
        """
        try:
            print(f"Raw data received: {data}")

            if isinstance(data, str):
                data_obj = json.loads(data)
            elif isinstance(data, bytes):
                try:
                    data_obj = pickle.loads(data)
                except pickle.UnpicklingError as e:
                    print(f"Error unpickling data: {e}")
                    return
            else:
                data_obj = data

            print("Processed data:", data_obj)
            self.broadcast_event_to_clients(type(data_obj).__name__, data_obj, sender_id)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")

        except Exception as e:
            import traceback
            print(f"Error processing data: {e}")
            traceback.print_exc()

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
                self.process_data(data, player_id)

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
    server = GameServer("192.168.1.114", 5555)
    server.start()
