import os
import pickle
import socket
import threading
from threading import *
import Environment


class P2PFetching(threading.Thread):
    def __init__(self, host_name, port_number, maxixum_client_number):
        threading.Thread.__init__(self)
        self.host = host_name
        self.semaphore = Semaphore(maxixum_client_number)
        self.port = port_number
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind((self.host, self.port))
        self.client_socket.listen(maxixum_client_number)

    def run(self):
        print('Ready to share file')
        while True:
            client, client_addr = self.client_socket.accept()
            print('A new connection from',
                  client_addr[0], 'port', client_addr[1])

            request = pickle.loads(client.recv(
                Environment.PACKET_SIZE))
            message_type = request[0]

            if message_type == 'fetch':
                repo_path = os.path.join(os.getcwd(), 'repo_2')
                file_name = request[1]
                file_path = os.path.join(repo_path, file_name)

                self.semaphore.acquire()
                with open(file_path, 'rb') as sharing_file:
                    while True:
                        data = sharing_file.read(Environment.PACKET_SIZE)
                        if not data:
                            sharing_file.close()
                            client.close()
                            break
                        client.send(pickle.dumps(data))
                self.semaphore.release()
                print('The file has been sent successfully')
            else:
                continue
                # print("Wrong command line message")


def p2p_fetching_start(host_name, port_number):
    peer = P2PFetching(host_name, port_number, Environment.MAX_CLIENT_NUMBER)
    peer.start()  # Start peer sharing as a thread
