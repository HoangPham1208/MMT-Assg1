import os
import shutil
import pickle
import socket
from threading import *
import platform
import subprocess
import Environment
from P2PFetching import *


class AdminManager:
    def __init__(self):
        self.file_path = ""
        self.peer_port = Environment.SERVER_PORT

        print("Started Administrator")
        print(
            """
Command line support: \n
login <hostname> <password>
showListHostname
discover <host_name>
ping <host_name>
"""
        )

    def AdminServer_start(self):
        while True:
            request = input("Input your request: ")
            request = request.split()
            message_type = request[0]

            if message_type == "login":
                self.login(request[1], request[2])
            elif message_type == "discover":
                self.discover(request[1])
            elif message_type == "showListHostname":
                self.showListHostname()
            # elif message_type == "ping":
            #     print(self.ping(socket.gethostbyname(request[1])))
            elif message_type == "ping":
                result = self.ping(request[1])
                print(result)
            else:
                print("Wrong command line. Exited!")
                break

    def login(self, host_name, host_password):
        # check host_name
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT)
        )
        login_stream = ["login", host_name, host_password]
        data_stream = pickle.dumps(login_stream)
        client_connection.send(data_stream)

        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        if client_state[0] == "OK":
            print("Login success!")
            self.peer_port = client_state[1]
            return True
        elif client_state[0] == "WRONG_PASSWORD":
            print("Login fail because of wrong password!")
        else:
            print("Host name is not found in the server")
        return False

    def showListHostname(self):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(("localhost", Environment.SERVER_PORT))
        discover_request = ["list_host_name"]
        client_connection.send(pickle.dumps(discover_request))
        client_state = pickle.loads(client_connection.recv(Environment.PACKET_SIZE))
        print(client_state)

    def discover(self, host_name):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(("localhost", Environment.SERVER_PORT))
        discover_request = ["discover", host_name]
        client_connection.send(pickle.dumps(discover_request))
        client_state = pickle.loads(client_connection.recv(Environment.PACKET_SIZE))

        if client_state is not list:
            print(client_state)
        else:
            peer_files = client_state
            peer_file_metadata = client_state[0].key()

            if len(peer_files) == 0:
                print("The host doesn't has any files")
            else:
                print("Host_Name  Host_Port    File_Name    Date_Added")
                [
                    print(
                        file[peer_file_metadata[0]],
                        " ",
                        file[peer_file_metadata[1]],
                        " ",
                        file[peer_file_metadata[2]],
                        " ",
                        file[peer_file_metadata[3]],
                    )
                    for file in peer_files
                ]
        client_connection.close()
        return client_state

    def ping(self, host_name, port_name):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect((host_name, port_name))
        ping_request = ["ping", host_name, port_name]
        client_connection.send(pickle.dumps(ping_request))
        client_state = pickle.loads(client_connection.recv(Environment.PACKET_SIZE))

        # if (host_name != 'localhost') and (client_state == 'NOT_FOUND'):
        #     return 'The host name is not found in the server'

        param = "-n" if platform.system().lower() == "windows" else "-c"

        # Building the command. Ex: "ping -c 4 google.com"
        command = ["ping", param, "4", host_name]

        return subprocess.call(command) == 0

    # AN code ...
    # def ping(self, host_name):
    #     try:
    #         # Establish a socket connection to the CentralizedServer
    #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_connection:
    #             client_connection.connect(
    #                 (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT)
    #             )
    #             ping_request = ["ping", host_name]
    #             client_connection.send(pickle.dumps(ping_request))
    #             client_state = pickle.loads(
    #                 client_connection.recv(Environment.PACKET_SIZE)
    #             )

    #             param = "-n" if platform.system().lower() == "windows" else "-c"
    #             command = ["ping", param, "4", host_name]

    #             result = subprocess.call(command) == 0
    #             return "Host is reachable" if result else "Host is not reachable"
    #     except Exception as e:
    #         return str(e)


if __name__ == "__main__":
    peer = AdminManager()
    peer.AdminServer_start()
