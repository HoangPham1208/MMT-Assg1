import Environment

import hashlib
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
        print("Centralized server is live")

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(maximum_client_number)
        self.files = []
        self.clientHost = []
        self.clientMetaData = [
            "host_name",
            "host_password",
            "host_addr",
            "host_port",
            "host_live",
        ]
        self.fileMetaData = ["host_name", "host_port", "file_name", "date_added"]
        admin_data = [
            "admin",
            "1",
            Environment.SERVER_HOST_NAME,
            Environment.SERVER_PORT,
        ]
        self.clientHost.append(dict(zip(self.clientMetaData, admin_data)))
        print("Connect server at", self.host, "with port is", self.port)

    def run(self):
        while True:
            # request = [
            #            register <hostname> <password>
            #            login <hostname> <password>
            #            discover <hostname>,
            #            ping <hostname>,
            #            fetch <fname> <hostname> <peerport>,
            #            publish <fname> <lname>, ex: publish C:\Users\ACER\Desktop\quicknote.txt hello.txt
            #            ]

            client, client_addr = self.server_socket.accept()
            print("Connected to", client_addr[0], "port at", client_addr[1])

            request = pickle.loads(client.recv(Environment.PACKET_SIZE))
            # => [word_1, word_2,....]
            message_type = request[0]

            if message_type == "register":
                print("Client", client_addr[0], "want to register to use the server")
                self.semaphore.acquire()
                clientPort = 15000
                if len(self.clientHost) != 1:
                    clientPort = self.clientHost[-1]["host_port"] + 1
                client_message = self.client_register(
                    request[1], request[2], client_addr[0], clientPort
                )
                client.send(pickle.dumps(client_message))
                self.semaphore.release()
            elif message_type == "login":
                print("Client", client_addr[0], "is logging in to the server")
                self.semaphore.acquire()
                client_message = self.client_login(request[1], request[2])
                if client_message[0] == "OK":
                    for client_host in self.clientHost:
                        if client_host["host_name"] == request[1]:
                            client_host["host_live"] = True
                            break
                client.send(pickle.dumps(client_message))
                self.semaphore.release()
            elif message_type == "discover":
                self.semaphore.acquire()
                try:
                    list_of_files = pickle.dumps(self.list_of_files(request[1]))
                    client.send(list_of_files)
                except FileNotFoundError:
                    client.send(
                        pickle.dumps("The server is not found your requested hostname")
                    )
                self.semaphore.release()

            elif message_type == "publish":
                print("Client with port", str(request[2]), "want to share file")
                self.semaphore.acquire()
                # Check duplicate file name in server
                print(request)
                file_name_at_server = request[1]
                # choice for rename or overwrite: '1' for overwrting , '2' for auto rename
                choice = request[3]
                if choice != "0" and choice != "1" and choice != "2":
                    print("The source file or destination directory of client is not valid!")
                    message_to_client = "Please provide a valid source file or destination directory."
                else:
                    message_to_client = "File Registered Successfully."
                    host_name = "localhost"
                    for client_host in self.clientHost:
                        if client_host["host_port"] == request[2]:
                            host_name = client_host["host_name"]
                            break
                    # for index_file in self.files:
                    #     if index_file["file_name"] == file_name_at_server:
                    #         file_name_at_server = file_name_at_server.split(".")
                    #         print(file_name_at_server)
                    #         file_name_at_server = (
                    #             file_name_at_server[0] + " (1)." + file_name_at_server[1]
                    #         )
                    #         message_to_client += (
                    #             "\n Duplicate file name in server directory. \n Name is changed to "
                    #             + file_name_at_server
                    #         )
                    #         break
                    if choice == "1": # overwriting, so we need to find file and change the datetime
                        for element in self.files:
                            if element['host_name'] == host_name and element['file_name'] == file_name_at_server:
                                element['date_added'] = str(datetime.now())
                    if choice == "2" or choice == "0":
                        self.files.insert(
                            0,
                            dict(
                                zip(
                                    self.fileMetaData,
                                    [
                                        host_name,
                                        request[2],
                                        file_name_at_server,
                                        str(datetime.now()),
                                    ],
                                )
                            ),
                        )

                client.send(pickle.dumps(message_to_client))
                print(self.files)
                self.semaphore.release()

            elif message_type == "search":
                file_name = request[1]
                print("Client", request[2], "search for file", file_name)
                self.semaphore.acquire()
                search_result = []
                for file in self.files:
                    if file["file_name"] == file_name:
                        search_result.append(file)
                client.send(pickle.dumps(search_result))
                self.semaphore.release()

            elif message_type == "ping":
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
            if client_host["host_name"] == host_name:
                return client_host["host_addr"]
        return "NOT_FOUND"

    def list_of_files(self, host_name):
        file_lists = []
        if host_name == "localhost":
            return self.files, self.fileMetaData
        else:
            is_client_host_in_server = [
                host_name == client_host_name["host_name"]
                for client_host_name in self.clientHost
            ]
            if is_client_host_in_server:
                for file in self.files:
                    if file["host_name"] == host_name:
                        file_data = [
                            file["host_name"],
                            file["host_port"],
                            file["file_name"],
                            file["date_added"],
                        ]
                        file_lists.append(dict(zip(self.fileMetaData, file_data)))

                return file_lists
            raise FileNotFoundError("Hostname is not found")

    def client_register(
        self, client_host_name, client_password, client_addr, client_port
    ):
        # Check the client host name list in the server
        # If there is a duplicate host name, the server refuses the register request, return 'DUP'
        # Else, add client host name and its password to the server, return 'OK'

        # SHOULD BE DONE: encrypt the password before client send and before store to the server
        # Refer assymetric encryption algorithm

        for host_name in self.clientHost:
            if client_host_name == host_name["host_name"]:
                return "DUP"

        self.clientHost.append(
            dict(
                zip(
                    self.clientMetaData,
                    (
                        client_host_name,
                        hashlib.sha256(
                            str(client_password).encode("utf-8")
                        ).hexdigest(),
                        client_addr,
                        client_port,
                        False,
                    ),
                )
            )
        )
        return ["OK", client_port]

    def client_login(self, client_host_name, client_password):
        for client_host in self.clientHost:
            if client_host["host_name"] == client_host_name:
                pass_encode = hashlib.sha256(
                    str(client_password).encode("utf-8")
                ).hexdigest()
                return (
                    ["OK", client_host["host_port"]]
                    if (client_host["host_password"] == pass_encode)
                    else ["WRONG_PASSWORD", 0]
                )
        return ["HOST_NAME_NOT_FOUND", 0]


print("Welcome. Server is about to go live")
server = CentralizedServer(2)
server.start()
