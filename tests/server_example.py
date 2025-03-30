# server_example.py
from server import GameServer

if __name__ == "__main__":
    server = GameServer("127.0.0.1", 5555)
    server.start()
