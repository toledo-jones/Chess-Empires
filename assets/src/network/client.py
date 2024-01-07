import socket
import pickle
import threading


class GameClient:
    def __init__(self, server_host, server_port, event_system):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_system = event_system
        self.player_id = None
        # Subscribe to different events
        self.event_system.subscribe("mouse move", self.handle_mouse_motion)
        self.event_system.subscribe("click", self.handle_click)
        self.event_system.subscribe("key press", self.handle_key_press)

        # Handle clicks, mouse motion, space, enter,

    def handle_mouse_motion(self, data):
        # Handle mouse move event logic
        self.send_object(data)

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
            # Append player_id to the data before sending
            obj['player_id'] = self.player_id
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
        self.client_socket.close()
        print("Connection closed")

    def listen_for_server_events(self):
        while True:
            try:
                data = self.client_socket.recv(4096)  # Adjust buffer size as needed
                if data:
                    decoded_data = pickle.loads(data)
                    # Extract event type and data
                    event_type = decoded_data.get('type')
                    event_data = decoded_data.get('data')
                    player_id = event_data.get('player_id')
                    x = event_data.get('x')
                    y = event_data.get('y')
                    print(f"Received {event_type} from Player {player_id}: x={x}, y={y}")
                    # Handle the received event
                    self.event_system.emit(event_type, event_data)
                else:
                    print("waiting for server event...")
            except Exception as e:
                print(f"Error handling server event: {e}")

    def start_listening_thread(self):
        # Create a separate thread for listening to server events
        listening_thread = threading.Thread(target=self.listen_for_server_events)
        listening_thread.daemon = True  # The thread will automatically exit when the main program exits
        listening_thread.start()

