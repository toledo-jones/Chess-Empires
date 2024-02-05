import socket
import pickle
import threading
import time


class GameClient:
    def __init__(self, server_host, server_port, event_manager):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_manager = event_manager
        self.player_id = None
        self.should_stop_listening = False
        self.last_mouse_event_time = 0
        self.mouse_event_threshold = 0.05
        self.listening_thread = None
        # Subscribe to different events
        self.event_manager.subscribe("mouse move", self.handle_mouse_motion)
        self.event_manager.subscribe("click", self.handle_click)
        self.event_manager.subscribe("key press", self.handle_key_press)

        # Handle clicks, mouse motion, space, enter,

    def handle_mouse_motion(self, data):
        current_time = time.time()
        if current_time - self.last_mouse_event_time > self.mouse_event_threshold:
            # Handle mouse move event logic
            self.send_object(data)
            self.last_mouse_event_time = current_time

    def handle_click(self, data):
        # Handle click event logic
        self.send_object(data)

    def handle_key_press(self, data):
        # Handle key press event logic
        self.send_object(data)

    def connect(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            print(f"Connected to server at {self.server_host}:{self.server_port}")

            # Receive player_id from the server
            self.player_id = int(self.client_socket.recv(1024).decode('utf-8'))
            print(f"Received player_id: {self.player_id}")

        except Exception as e:
            print(f"Error connecting to server: {e}")

    def send_object(self, obj):
        try:
            serialized_obj = pickle.dumps(obj)
            self.client_socket.sendall(serialized_obj)
        except Exception as e:
            print(f"Error sending object to server: {e}")

    def send_string(self, message):
        try:
            # Append player_id to the data before sending
            data = {'player_id': self.player_id, 'message': message}
            encoded_message = pickle.dumps(data)
            self.client_socket.sendall(encoded_message)
        except Exception as e:
            print(f"Error sending string to server: {e}")

    def receive_object(self):
        try:
            data = self.client_socket.recv(4096)  # Adjust buffer size as needed
            if data:
                return pickle.loads(data)
        except Exception as e:
            print(f"Error receiving object from server: {e}")

    def close(self):
        try:
            # Close the client socket
            self.client_socket.close()
            print("Connection closed")
        except Exception as e:
            print(f"Error closing client socket: {e}")

        # Stop the listening thread
        self.stop_listening_thread()

    def listen_for_server_events(self):
        while not self.should_stop_listening:
            try:
                data = self.client_socket.recv(4096)  # Adjust buffer size as needed
                if not data:
                    # If data is empty, the socket has been closed
                    print("Server disconnected. Exiting event listener.")
                    break
                decoded_data = pickle.loads(data)
                # Extract event type and data
                event_type = decoded_data.get('type')
                event_data = decoded_data.get('data')
                player_id = event_data.get('player_id')
                if player_id != self.player_id:
                    event_data['me'] = False
                    event_type = "server " + event_data.get("type")
                print(f"Client emitting player {player_id} | {event_type}, {event_data}")
                self.event_manager.emit(event_type, event_data)
            except OSError as e:
                if "Bad file descriptor" in str(e):
                    # Socket has been closed, break out of the loop
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
        # Create a separate thread for listening to server events
        self.listening_thread = threading.Thread(target=self.listen_for_server_events)
        self.listening_thread.daemon = True  # The thread will automatically exit when the main program exits
        self.listening_thread.start()

    def stop_listening_thread(self):
        # Set the flag to signal the listening thread to exit
        self.should_stop_listening = True

        # Wait for the listening thread to complete if it exists
        if hasattr(self, 'listening_thread') and self.listening_thread:
            self.listening_thread.join()

    def get_player_id(self):
        return self.player_id
