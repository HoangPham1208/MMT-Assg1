import socket

SERVER_PORT = 3456
SERVER_HOST_NAME = "localhost" # change when testing on different machines
PACKET_SIZE = 1024*5
MAX_CLIENT_NUMBER = 5
PEER_HOST = socket.gethostbyname(socket.gethostname())
