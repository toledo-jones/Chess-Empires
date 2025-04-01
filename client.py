import socket
import pickle
import threading
import struct
import typing
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from engine import Engine


class GameClient:
    """
    Manages the client-side connection to the game server.
    """

    def __init__(self, server_host: str, server_port: int, engine: "Engine"):
        """
        Initializes the GameClient with the specified server host, port, and event manager.

        :param server_host: The host address of the server.
        :param server_port: The port number of the server.
        :param engine: Game Engine for handling events and updating game state
        """
        self.server_host: str = server_host
        self.server_port: int = server_port
        self.client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_id: typing.Optional[int] = None
        self.should_stop_listening: bool = False
        self.listening_thread: typing.Optional[threading.Thread] = None
        self.engine: "Engine" = engine

    def connect(self):
        """
        Connects to the game server and receives the player ID.
        """
        try:
            # Connect to the server
            self.client_socket.connect((self.server_host, self.server_port))
            print(f"Connected to server at {self.server_host}:{self.server_port}")

            # Receive player_id from the server
            self.player_id = int(self.client_socket.recv(1024).decode('utf-8'))
            print(f"Received player_id: {self.player_id}")

        except Exception as e:
            print(f"Error connecting to server: {e}")

    def send_object(self, obj: typing.Any):
        """
        Sends a serialized object to the server.

        :param obj: The object to send.
        """

        # Serialize the object and send it to the server
        serialized_obj: bytes = pickle.dumps(obj)
        self.client_socket.sendall(serialized_obj)

    def send_string(self, message: str):
        """
        Sends a string message to the server.

        :param message: The message to send.
        """
        try:
            # Append player_id to the data before sending
            data: dict = {'player_id': self.player_id, 'message': message}
            encoded_message: bytes = pickle.dumps(data)
            self.client_socket.sendall(encoded_message)
        except Exception as e:
            print(f"Error sending string to server: {e}")

    def receive_object(self) -> typing.Optional[typing.Any]:
        """
        Receives a serialized object from the server.

        :return: The deserialized object received from the server.
        """
        try:
            # Receive the length of the incoming message
            raw_message_length = self.receive_all(4)
            if not raw_message_length:
                return None
            message_length = struct.unpack('>I', raw_message_length)[0]
            # Receive the actual message data
            data = self.receive_all(message_length)
            if data:
                return pickle.loads(data)
        except Exception as e:
            print(f"Error receiving object from server: {e}")
        return None

    def receive_all(self, n: int) -> Optional[bytes]:
        """
        Helper function to receive n bytes or return None if EOF is hit.
        """
        data = bytearray()
        while len(data) < n:
            packet = self.client_socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def close(self):
        """
        Closes the client socket and stops the listening thread.
        """
        try:
            # Close the client socket
            self.client_socket.close()
            print("Connection closed")
        except Exception as e:
            print(f"Error closing client socket: {e}")

        # Stop the listening thread
        self.stop_listening_thread()

    def listen_for_server_events(self):
        """
        Listens for events from the server and processes them.
        """
        while not self.should_stop_listening:
            try:
                # Receive object from the server
                decoded_data = self.receive_object()
                if decoded_data is None:
                    # If data is None, the socket has been closed
                    print("Server disconnected. Exiting event listener.")
                    break

                print(f"Executing event: {decoded_data}")
                if isinstance(decoded_data, dict):
                    # Handle the dictionary data if necessary
                    print("Received a dictionary:", decoded_data)
                else:
                    # Assume decoded_data is the expected object type
                    self.engine.add_network_event(decoded_data)
            except OSError as e:
                if "Bad file descriptor" in str(e):
                    # Socket has been closed, break out of the loop
                    print("Socket closed. Exiting event listener.")
                    break
                else:
                    print(f"Error handling server event: {e}")
            except EOFError:
                # Handle EOFError (pickle-related)
                print("EOFError: Server disconnected. Exiting event listener.")
                break
            except Exception as e:
                print(f"Error handling server event: {e}")

    def start_listening_thread(self):
        """
        Starts a separate thread for listening to server events.
        """
        # Create a separate thread for listening to server events
        self.listening_thread = threading.Thread(target=self.listen_for_server_events)
        self.listening_thread.daemon = True  # The thread will automatically exit when the main program exits
        self.listening_thread.start()

    def stop_listening_thread(self):
        """
        Stops the listening thread.
        """
        # Set the flag to signal the listening thread to exit
        self.should_stop_listening = True

        # Wait for the listening thread to complete if it exists
        if hasattr(self, 'listening_thread') and self.listening_thread:
            self.listening_thread.join()

    def get_player_id(self) -> typing.Optional[int]:
        """
        Returns the player ID.

        :return: The player ID.
        """
        return self.player_id
