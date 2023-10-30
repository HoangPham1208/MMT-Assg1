import os
import pickle
import socket
from threading import *
import Environment


class P2PFetching(Thread):
    def __init__(self, host_name, port_number, maxixum_client_number):
        Thread.__init__(self)
        self.host = host_name
        self.semaphore = Semaphore(maxixum_client_number)
        self.port = port_number
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind((self.host, self.port))
        self.client_socket.listen(maxixum_client_number)

    def fetch(self):
        print('Ready to share file')
        while True:
            client, client_addr = self.client_socket.accept()
            print('A new connection from',
                  client_addr[0], 'port', client_addr[1])

            request = pickle.loads(client.recv(
                Environment.PACKET_SIZE))[0].split()
            message_type = request[0]

            if message_type == 'fetch':
                file_path = os.path.join(os.getcwd(), 'repo_2')
                file_name = request[1]
                file_path = os.path.join(file_path, file_name)

                self.semaphore.acquire()
                with open(file_path, 'rb') as sharing_file:
                    while True:
                        reader = sharing_file.read(Environment.PACKET_SIZE)
                        while reader:
                            client.send(reader)
                            reader = sharing_file.read(Environment.PACKET_SIZE)
                        sharing_file.close()
                        client.close()
                        break
                self.semaphore.release()
                print('The file has been sent successfully')
            else:
                continue
                # print("Wrong command line message")


def p2p_fetching_start(host_name, port_number):
    peer = P2PFetching(host_name, port_number, Environment.MAX_CLIENT_NUMBER)
    peer.start()  # Start peer sharing as a thread
