import os
import pickle
import socket
from threading import *

import Environment
import P2PFetching


class PeerManager:
    def __init__(self):
        self.file_path = ''
        self.peer_port = Environment.SERVER_PORT + 1
        print("Started P2P file sharing system")
        
    def P2PServer_start(self):
        while True:
            request = input("""
                            Command line support \n
                            publish <local_file_path> <peer_repository_name> \n
                            fetch <peer_repository_name> \n
                            discover <host_name> \n
                            ping <host_name> \n """)
            request = request.split()
            message_type = request[0]
            
            if message_type == 'publish':
                self.peer_port = 3456
                self.file_path = request[1]
                self.fetch()
                P2PFetching.p2p_fetching_start(socket.gethostname(), self.peer_port)
            elif message_type == 'fetch':
                self.fetch()
            elif message_type == 'discover':
                self.discover(request[1])
            elif message_type == 'ping':
                self.ping()
            else:
                continue
    
    def publish(self):
        peer_connection = socket.socket()
        peer_connection.connect(('localhost', self.peer_port))
        published_stream = ['publish', self.file_path, self.peer_port]
        data_stream = pickle.dumps(published_stream)
        peer_connection.send(data_stream)
        peer_state = peer_connection.recv(Environment.PACKET_SIZE)
        print(peer_state.decode())
        peer_connection.close()

    def discover(self, host_name = 'localhost'):
        peer_connection = socket.socket()
        peer_connection.connect((host_name, self.peer_port))
        discover_request = ['request', host_name]
        peer_connection.send(pickle.dumps(discover_request))
        peer_state = pickle.loads(peer_connection.recv(Environment.PACKET_SIZE))
        
        peer_files = peer_state[0]
        peer_file_metadata = peer_state[1]
        if len(peer_files) == 0:
            print('The host doesn\'t has any files')
        else:
            print('Peer_Port  Host_Name  File_Name    Date_Added')
            [print(file[peer_file_metadata[0]], ' ', \
                   file[peer_file_metadata[1]], ' ', \
                   file[peer_file_metadata[2]], ' ', \
                   file[peer_file_metadata[3]]       \
                   ) 
                for file in peer_files
            ]
        
        peer_connection.close()

    def ping(self, host_name):
        pass
    def fetch(self, repository_path):
        pass

peer = PeerManager()
peer.P2PServer_start()