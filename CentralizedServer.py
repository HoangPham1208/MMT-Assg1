import Environment

import socket
import pickle
import platform
import subprocess
from datetime import datetime
from threading import *


class CentralizedServer(Thread):
    def __init__(self, maximum_client_number):
        Thread.__init__(self)
        self.host = Environment.SERVER_HOST_NAME
        self.port = Environment.SERVER_PORT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Default set the TCP socket connection
        self.semaphore = Semaphore(maximum_client_number)
        print('Centralized server is live')
        
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(maximum_client_number)
        self.files = []
        self.clientHostName = []
        self.fileMetaData = ['peerId', 'hostName', 'fileName', 'dateAdded']
        print('Connect server at', self.host, 'with port is', self.port)
    
    def run(self):
        while True:
            client, client_addr = self.server_socket.accept()
            print('Connected to', client_addr[0], 'port at', client_addr[1])
            
            # request = [discover <hostname>, 
            #            ping <hostname>,
            #            fetch <fname>, 
            #            publish <fname> <lname>,
            #            ]            
            request = pickle.loads(client.recv(Environment.PACKET_SIZE))
            # => [word_1, word_2,....]
            message_type = request[0]
            host_name = request[1]
            
            if message_type == 'discover':
                print('Client', client_addr[1], 'requests to list files of', request[1])
                self.semaphore.acquire()
                try:
                    list_of_files = pickle.dumps(self.list_of_files(host_name))
                    client.send(list_of_files)
                except FileNotFoundError:
                    client.send('The server is not found your requested hostname')
                self.semaphore.release()
            elif message_type == 'publish':
                print('Client with', client_addr, 'is want to share file')
                self.semaphore.acquire()
                
                # Check duplicate file name in server
                peer_file_info = request[2]
                message_to_client = "File Registered Successfully."
                for index_file in self.files:
                    if index_file['fileName'] == peer_file_info:
                        peer_file_info = request[2].split('.')
                        print(peer_file_info)
                        peer_file_info = peer_file_info[0] + ' (1).' + peer_file_info[1]
                        message_to_client += '\n Duplicate file name in server directory. \n Name is changed to ' + peer_file_info
                        break
                self.files.insert(0, \
                    dict(zip(self.fileMetaData, [str(self.host), host_name, peer_file_info, str(datetime.now())])))
                print(self.files)
                client.send(bytes(message_to_client, 'utf-8'))
                self.semaphore.release()
            elif message_type == 'ping':
                self.semaphore.acquire()
                isHostLive = self.ping(host_name)
                print("The host is online") if isHostLive else print("The host is offline")
                self.semaphore.release()
            else:
                break
                #print('Wrong command line')
                
                
    def ping(self, host_name):
        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', host_name]

        return subprocess.call(command) == 0
                        
    
    def list_of_files(self, host_name):
        file_lists = []
        if host_name == 'localhost':
            return self.files, self.fileMetaData
        else:
            is_client_host_in_server = [host_name == client_host_name for client_host_name in self.clientHostName]
            if is_client_host_in_server:
                for file in self.files:
                    if file['host_name'] == host_name:
                        file_metadata = [file['peer_id'], file['host_name'], \
                                        file['file_name'], file['date-added']]
                        file_lists.push(dict(zip(self.fileMetaData, file_metadata)))
                return file_lists
            raise FileNotFoundError('Hostname is not found')
    
print("Welcome. Server is about to go live")
server = CentralizedServer(2)
server.start()        
            