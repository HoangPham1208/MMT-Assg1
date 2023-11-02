import os
import shutil
import pickle
import socket
from threading import *
import platform
import subprocess
import Environment
from P2PFetching import *


class PeerManager:
    def __init__(self):
        self.file_path = ""
        self.peer_port = ""
        self.host_name = ""
        self.host_password = ""
        print("Started P2P file sharing system")
        print(
            """
Command line support: \n
register <hostname> <password>
login <hostname> <password>
publish <file_path_at_peer> <file_name_at_server>
search <file_name>
fetch <file_name> <peer_port> 
"""
        )

    def P2PServer_start(self):
        while True:
            request = input("Input your request: ")
            request = request.split()
            message_type = request[0]

            if message_type == "register":
                self.register(request[1], request[2])
            elif message_type == "login":
                if self.login(request[1], request[2]):
                    p2p_fetching_start("localhost", self.peer_port)
            elif message_type == "publish":
                self.publish(request[1], request[2])
            elif message_type == "fetch":
                self.fetch(request[1], request[2])
            elif message_type == "search":
                self.search(request[1])
            else:
                print("Wrong command line. Exited!")
                break

    def register(self, host_name, host_password):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT)
        )

        registered_stream = ["register", host_name, host_password]
        data_stream = pickle.dumps(registered_stream)
        client_connection.send(data_stream)

        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        if client_state[0] == "OK":
            self.host_name = host_name
            self.host_password = host_password
            self.peer_port = client_state[1]
            print(
                "Your registration is success! Your port name is " + str(self.peer_port)
            )
        else:
            print(
                "Your chosen host name was in the server! Please choose another name!"
            )

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
            self.host_name = host_name
            self.host_password = host_password
            self.peer_port = client_state[1]
            return True
        elif client_state[0] == "WRONG_PASSWORD":
            print("Login fail because of wrong password!")
        else:
            print("Host name is not found in the server")
        return False

    def publish(self, lname, file_name):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT)
        )
        repo_path = os.path.join(os.getcwd(), "repo_2")
        repo_path = repo_path.replace(os.path.sep, "/")
        copy_file_to_directory(lname, repo_path, file_name)
        published_stream = ["publish", file_name, self.peer_port]
        data_stream = pickle.dumps(published_stream)
        client_connection.send(data_stream)
        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        print(client_state)
        client_connection.close()

    def search(self, file_name):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT)
        )
        search_stream = ["search", file_name, self.peer_port]
        data_stream = pickle.dumps(search_stream)
        client_connection.send(data_stream)
        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        print(client_state)
        client_connection.close()

    def fetch(self, file_name, peer_port):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(("localhost", int(peer_port)))
        fetched_stream = ["fetch", file_name]
        data_stream = pickle.dumps(fetched_stream)
        client_connection.send(data_stream)

        repo_path = os.path.join(os.getcwd(), "repo_1")

        with open(os.path.join(repo_path, file_name), "wb") as download_file:
            while True:
                file_stream = client_connection.recv(Environment.PACKET_SIZE)
                if not file_stream:
                    download_file = pickle.loads(download_file)
                    download_file.close()
                    break
                download_file.write(file_stream)
        client_connection.close()
        print("The file is downloaded in your repository")


def copy_file_to_directory(source_file, destination_directory, fname):
    if not os.path.exists(destination_directory):
        # Create the directory if it doesn't exist
        os.makedirs(destination_directory)
    if os.path.isfile(source_file) and os.path.isdir(destination_directory):
        destination_path = os.path.join(destination_directory, fname)
        shutil.copy(source_file, destination_path)
        print(f"File '{source_file}' copied to '{destination_directory}'")
    else:
        print("Please provide a valid source file and destination directory.")


if __name__ == "__main__":
    peer = PeerManager()
    peer.P2PServer_start()
