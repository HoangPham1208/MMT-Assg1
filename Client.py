import os
import pickle
import socket
from threading import *
import platform
import subprocess

import Environment
import P2PFetching


class PeerManager:
    def __init__(self):
        self.file_path = ''
        self.peer_port = Environment.SERVER_PORT
        self.host_name = ''
        self.host_password = ''
        print("Started P2P file sharing system")
        print("""
Command line support: \n
register <hostname> <password>
login <hostname> <password>
publish <file_path_at_peer> <file_name_at_server>
fetch <file_name> 
discover <host_name> 
ping <host_name>  """)

    def P2PServer_start(self):
        while True:
            request = input('Input your request: ')
            request = request.split()
            message_type = request[0]

            if message_type == 'register':
                self.register(request[1], request[2])
            elif message_type == 'login':
                pass
            elif message_type == 'publish':
                self.peer_port = Environment.SERVER_PORT
                self.file_path = request[1]
                self.publish()
            elif message_type == 'fetch':
                self.fetch(request[1])
            elif message_type == 'discover':
                self.discover(request[1])
            elif message_type == 'ping':
                print(self.ping(socket.gethostbyname(request[1])))
            else:
                print('Wrong command line. Exited!')
                break

    def register(self, host_name, host_password):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT))

        registered_stream = ['register', host_name, host_password]
        data_stream = pickle.dumps(registered_stream)
        client_connection.send(data_stream)

        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        if client_state == 'OK':
            self.host_name = host_name
            self.host_password = host_password
            print('Your registration is success!')
        else:
            print('Your chosen host name was in the server! Please choose another name!')

    def login(self, host_name, host_password):
        # check host_name
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT))

        login_stream = ['login', host_name, host_password]
        data_stream = pickle.dumps(login_stream)
        client_connection.send(data_stream)

        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        if client_state == 'OK':
            print('Login success!')
            return True
        elif client_state == 'WRONG_PASSWORD':
            print('Login fail because of wrong password!')
        else:
            print('Host name is not found in the server')
        return False

    def publish(self):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(
            (Environment.SERVER_HOST_NAME, self.peer_port))
        published_stream = ['publish', self.file_path, self.peer_port]
        data_stream = pickle.dumps(published_stream)
        client_connection.send(data_stream)
        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        print(client_state)
        client_connection.close()

    def discover(self, host_name='localhost'):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect((host_name, self.peer_port))
        discover_request = ['discover', host_name]
        client_connection.send(pickle.dumps(discover_request))
        client_state = pickle.loads(
            client_connection.recv(Environment.PACKET_SIZE))

        peer_files = client_state[0]
        peer_file_metadata = client_state[1]
        if len(peer_files) == 0:
            print('The host doesn\'t has any files')
        else:
            print('Host_Name  File_Name    Date_Added')
            [print(file[peer_file_metadata[0]], ' ',
                   file[peer_file_metadata[1]], ' ',
                   file[peer_file_metadata[2]]
                   )
                for file in peer_files
             ]

        client_connection.close()

    def ping(self, host_name):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect((host_name, self.peer_port))
        ping_request = ['ping', host_name]
        client_connection.send(pickle.dumps(ping_request))
        client_state = pickle.loads(
            client_connection.recv(Environment.PACKET_SIZE))

        # if (host_name != 'localhost') and (client_state == 'NOT_FOUND'):
        #     return 'The host name is not found in the server'

        param = '-n' if platform.system().lower() == 'windows' else '-c'

        # Building the command. Ex: "ping -c 4 google.com"
        command = ['ping', param, '4', host_name]

        return subprocess.call(command) == 0

    def fetch(self, file_name):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(('localhost', self.peer_port))
        fetched_stream = ['fetch', file_name]
        data_stream = pickle.dumps(fetched_stream)
        client_connection.send(data_stream)

        peer_file_path = os.path.join(os.getcwd(), 'repo_1')

        with open(os.path.join(peer_file_path, file_name), 'wb') as download_file:
            while True:
                file_stream = client_connection.recv(Environment.PACKET_SIZE)
                print(file_stream.decode())
                if not file_stream:
                    download_file.close()
                    break
                download_file.write(file_name)
        client_connection.close()
        print('The file is downloaded in your repository')


peer = PeerManager()
peer.P2PServer_start()
