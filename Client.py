import os
import shutil
import pickle
import socket
from threading import *
import platform
import subprocess
import Environment
from P2PFetching import *
import re  # regular expression
import tkinter as tk
from tkinter import messagebox, simpledialog


class PeerManager:
    def __init__(self):
        self.file_path = ""
        self.peer_port = ""
        self.host_name = ""
        self.host_password = ""
        # self.host_addr = Environment.PEER_HOST
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
                    p2p_fetching_start(Environment.PEER_HOST, self.peer_port)
            elif message_type == "publish":
                new_request = [
                    request[0],
                    " ".join(request[1: len(request) - 1]),
                    request[-1],
                ]
                self.publish(new_request[1], new_request[2])
            elif message_type == "fetch":
                self.fetch(request[1], request[2])
            elif message_type == "search":
                self.search(request[1])
            elif message_type == "refresh":
                self.refresh(self.host_name)
            else:
                print("Wrong command line. Exited!")
                break

    def refresh(self, host_name):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT)
        )

        refreshed_stream = ["refresh", host_name]
        data_stream = pickle.dumps(refreshed_stream)
        client_connection.send(data_stream)

        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        print(client_state)
        return client_state

    def register(self, host_name, host_password):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT)
        )

        registered_stream = ["register", host_name,
                             host_password, Environment.PEER_HOST]
        data_stream = pickle.dumps(registered_stream)
        client_connection.send(data_stream)

        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        if client_state[0] == "OK":
            self.host_name = host_name
            self.host_password = host_password
            self.peer_port = client_state[1]
            print(
                "Your registration is success! Your port name is " +
                str(self.peer_port)
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
        repo_path = os.path.join(os.getcwd(), "repo")
        repo_path = repo_path.replace(os.path.sep, "/")
        copy_data = copy_file_to_directory(lname, repo_path, file_name)
        if not copy_data[0]:
            # print("Your file path or file name is wrong! Please try again!")
            return False
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT)
        )
        published_stream = ["publish", copy_data[1],
                            self.peer_port, copy_data[2]]
        data_stream = pickle.dumps(published_stream)
        client_connection.send(data_stream)
        client_state = client_connection.recv(Environment.PACKET_SIZE)
        client_state = pickle.loads(client_state)
        print(client_state)
        client_connection.close()
        return True

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
        return client_state

    def fetch(self, file_name, host_name):
        client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connection.connect(
            (Environment.SERVER_HOST_NAME, Environment.SERVER_PORT))
        host_request = ['get_host', host_name]
        client_connection.send(pickle.dumps(host_request))
        host_info = pickle.loads(
            client_connection.recv(Environment.PACKET_SIZE))
        client_connection.close()
        
        # Handle if not get anything
        if host_info == "HOST_NOT_FOUND":
            return "HOST_NOT_FOUND"
        try:                
            client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_connection.connect(
                (host_info['host_addr'], int(host_info['host_port'])))
        except:
            return "NOT_ONLINE"
        fetched_stream = ["fetch", file_name]
        data_stream = pickle.dumps(fetched_stream)
        client_connection.send(data_stream)
        # load to Download_Files folder
        repo_path = os.path.join(os.getcwd(), "Download_Files")
        repo_path = repo_path.replace(os.path.sep, "/")
        # Handle for first time
        file_stream = client_connection.recv(Environment.PACKET_SIZE)
        
        if file_stream == "FILE_NOT_FOUND".encode(): # handle if file not found
            return "FILE_NOT_FOUND"
        
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
        # Handle for duplicate file name
        if file_name in os.listdir(repo_path):
            idx = 1
            while file_name in os.listdir(repo_path):
                split_name = file_name.rsplit(".", 1)
                match = re.search(r"\_\((\d+)\)$", split_name[0])
                if match:
                    idx = int(match.group(1))
                    file_name = (
                        re.sub(r"\_\((\d+)\)$", f"_({idx+1}).", split_name[0])
                        + split_name[1]
                    )
                else:
                    file_name = split_name[0] + f"_(1)." + split_name[1]
                idx += 1    
        with open(os.path.join(repo_path, file_name), "wb") as download_file:
            while True:
                file_stream = client_connection.recv(Environment.PACKET_SIZE)
                if not file_stream:
                    download_file.close()
                    break
                download_file.write(file_stream)
        client_connection.close()
        print("The file is downloaded in your repository")
        return True


# def copy_file_to_directory(source_file, destination_directory, fname):
#     choice = "0"
#     if not os.path.exists(destination_directory):
#         # Create the directory if it doesn't exist
#         os.makedirs(destination_directory)
#     if os.path.isfile(source_file) and os.path.isdir(destination_directory):
#         # HANDLING DUPLICATES FILE NAMES
#         # format: filename.extension
#         # duplicate files will be named as filename_(i).extension, where i is an integer
#         # ------------------------------
#         if fname in os.listdir(destination_directory):
#             print(
#                 "File name already exists. Do you want to overwrite it or auto rename the file?"
#             )
#             print("1. Overwrite")
#             print("2. Rename")
#             choice = input("Enter your choice: ")
#             if choice == "1":
#                 print("Overwriting file...")
#             elif choice == "2":
#                 idx = 1
#                 while fname in os.listdir(destination_directory):
#                     split_name = fname.rsplit(
#                         ".", 1
#                     )  # split the file name and extension
#                     match = re.search(
#                         r"\_\((\d+)\)$", split_name[0]
#                     )  # check if the file name already has a number
#                     if match:
#                         # get the index of the file
#                         idx = int(match.group(1))
#                         fname = (
#                             re.sub(r"\_\((\d+)\)$", f"_({idx+1}).", split_name[0])
#                             + split_name[1]
#                         )  # increment the index
#                     else:
#                         fname = (
#                             split_name[0] + f"_(1)." + split_name[1]
#                         )  # add the index
#                     idx += 1
#             else:
#                 print("Invalid choice. Please try again.")
#         # ------------------------------
#         destination_path = os.path.join(destination_directory, fname)
#         shutil.copy(source_file, destination_path)
#         return [True, fname, choice]
#     else:
#         return [False, fname, choice]
def copy_file_to_directory(source_file, destination_directory, fname):
    choice = "0"
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    if os.path.isfile(source_file) and os.path.isdir(destination_directory):
        if fname in os.listdir(destination_directory):
            choice = tk.messagebox.askquestion(
                "File Name Conflict",
                "File name already exists. Do you want to overwrite it?",
            )
            if choice == "yes":
                print("Overwriting file...")
            elif choice == "no":
                idx = 1
                while fname in os.listdir(destination_directory):
                    split_name = fname.rsplit(".", 1)
                    match = re.search(r"\_\((\d+)\)$", split_name[0])
                    if match:
                        idx = int(match.group(1))
                        fname = (
                            re.sub(r"\_\((\d+)\)$",
                                   f"_({idx+1}).", split_name[0])
                            + split_name[1]
                        )
                    else:
                        fname = split_name[0] + f"_(1)." + split_name[1]
                    idx += 1
            else:
                print("Invalid choice. Please try again.")
                # return [False, fname]

        destination_path = os.path.join(destination_directory, fname)
        shutil.copy(source_file, destination_path)
        return [True, fname, choice]
    else:
        return [False, fname, choice]


if __name__ == "__main__":
    peer = PeerManager()
    # peer.P2PServer_start()
