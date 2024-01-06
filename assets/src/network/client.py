import socket
import pickle


class GameClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            print(f"Connected to server at {self.server_host}:{self.server_port}")
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
            encoded_message = message.encode('utf-8')
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