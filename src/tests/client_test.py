import pickle
import socket

# Create a socket connection to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5555))

# Example data to send
data = {"type": "mouse move", "player_id": 1, "x": 100, "y": 200}

# Send the data to the server
client_socket.send(pickle.dumps(data))

# Close the client socket
client_socket.close()
