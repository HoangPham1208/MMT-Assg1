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
        # Default set the TCP socket connection
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.semaphore = Semaphore(maximum_client_number)
        print('Centralized server is live')

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(maximum_client_number)
        self.files = []
        self.clientHost = []
        self.clientMetaData = ['host_name', 'host_password',
                               'host_addr', 'host_port', 'host_live']
        self.fileMetaData = ['host_name', 'file_name', 'date_added']
        print('Connect server at', self.host, 'with port is', self.port)

    def run(self):
        while True:
            # request = [
            #            register <hostname> <password>
            #            login <hostname> <password>
            #            discover <hostname>,
            #            ping <hostname>,
            #            fetch <fname>,
            #            publish <fname> <lname>,
            #            ]

            client, client_addr = self.server_socket.accept()
            print('Connected to', client_addr[0], 'port at', client_addr[1])

            request = pickle.loads(client.recv(Environment.PACKET_SIZE))
            # => [word_1, word_2,....]
            message_type = request[0]

            if message_type == 'register':
                print('Client', client_addr[0],
                      'want to register to use the server')
                self.semaphore.acquire()
                client_message = self.client_register(
                    request[1], request[2], client_addr[0], client_addr[1])
                client.send(pickle.dumps(client_message))
                self.semaphore.release()
            elif message_type == 'login':
                print('Client', client_addr[0], 'is logging in to the server')
                self.semaphore.acquire()
                client_message = self.client_login(request[1], request[2])
                if client_message == 'OK':
                    for client_host in self.clientHost:
                        if client_host['host_name'] == request[1]:
                            client_host['host_live'] = True
                            break
                client.send(pickle.dumps(client_message))
                self.semaphore.release()
            elif message_type == 'discover':
                print('Client', client_addr[1],
                      'requests to list files of', request[1])
                self.semaphore.acquire()
                try:
                    list_of_files = pickle.dumps(
                        self.list_of_files(request[1]))
                    client.send(list_of_files)
                except FileNotFoundError:
                    client.send(pickle.dumps(
                        'The server is not found your requested hostname'))
                self.semaphore.release()
            elif message_type == 'publish':
                print('Client with', client_addr[1], 'is want to share file')
                self.semaphore.acquire()
                # Check duplicate file name in server
                print(request)
                file_name_at_server = request[2]
                message_to_client = "File Registered Successfully."
                for index_file in self.files:
                    if index_file['file_name'] == file_name_at_server:
                        file_name_at_server = file_name_at_server.split('.')
                        print(file_name_at_server)
                        file_name_at_server = file_name_at_server[0] + \
                            ' (1).' + file_name_at_server[1]
                        message_to_client += '\n Duplicate file name in server directory. \n Name is changed to ' + \
                            file_name_at_server
                        break
                self.files.insert(0, dict(zip(self.fileMetaData, [str(
                    self.host), file_name_at_server, str(datetime.now())])))
                client.send(pickle.dumps(message_to_client))
                self.semaphore.release()
            elif message_type == 'ping':
                self.semaphore.acquire()
                host_addr = self.search_client_host_addr(request[1])
                client.send(pickle.dumps(host_addr))
                self.semaphore.release()

            else:
                break
                # print('Wrong command line')

    def search_client_host_addr(self, host_name):
        # return peer_addr to peer want to ping
        for client_host in self.clientHost:
            if client_host['host_name'] == host_name:
                return client_host['host_addr']
        return 'NOT_FOUND'

    def list_of_files(self, host_name):
        file_lists = []
        if host_name == 'localhost':
            return self.files, self.fileMetaData
        else:
            is_client_host_in_server = [
                host_name == client_host_name['host_name'] for client_host_name in self.clientHost]
            if is_client_host_in_server:
                for file in self.files:
                    if file['host_name'] == host_name:
                        file_data = [file['host_name'],
                                     file['file_name'], file['date-added']]
                        file_lists.append(
                            dict(zip(self.fileMetaData, file_data)))
                return file_lists
            raise FileNotFoundError('Hostname is not found')

    def client_register(self, client_host_name, client_password, client_addr, client_port):
        # Check the client host name list in the server
        # If there is a duplicate host name, the server refuses the register request, return 'DUP'
        # Else, add client host name and its password to the server, return 'OK'

        # SHOULD BE DONE: encrypt the password before client send and before store to the server
        # Refer assymetric encryption algorithm

        for host_name in self.clientHost:
            if client_host_name == host_name['host_name']:
                return 'DUP'

        self.clientHost.append(dict(zip(self.clientMetaData,
                                        (client_host_name, str(client_password),
                                         client_addr, client_port, False)
                                        )
                                    )
                               )
        return 'OK'

    def client_login(self, client_host_name, client_password):

        for client_host in self.clientHost:
            if (client_host['host_name'] == client_host_name):
                return 'OK' if (client_host['host_password'] == client_password) else 'WRONG_PASSWORD'
        return 'HOST_NAME_NOT_FOUND'


print("Welcome. Server is about to go live")
server = CentralizedServer(2)
server.start()
