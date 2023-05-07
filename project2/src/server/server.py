""" Implements a multithreaded server that echos messages received from
connected clients.
"""
import socket
import threading
import sys
import os
import json
from datetime import datetime as dt

class Server():
    """ Implements the Server class.
    """
    def __init__(self, ip, port):
        """ Constructor method. Takes two arguments: ip address and port.
        The ip address is a string in the form of an IPv4 address.
        (Example: "127.0.0.1") The port is an integer representing an
         operating system port on which the server application listens for
         incomming connections. (Example: 5500) The port used must not already be
         used by another application.
        """
        self.ip = ip
        self.user = None
        self.port = port
        self._listen(ip, port)
        self._accept_connection()
    # Listen for incoming connections
    def _listen(self, ip, port):
        """ Creates a server socket and starts listening on assigned
        IP Address and Port.
        """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if os.name == 'nt':
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            else:
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.server.bind((ip, port))
            print(f'Listening on IP Address: {ip} and Port: {port} ')
            self.server.listen(4)
        except Exception as e:
            print(f'Problem listening for incoming connection: {e}')
            self.server.close()
            sys.exit(0)
    def _check_user(self, username, password):
        with open("./userdata.json", "r") as file:
            userdata = json.loads(file.read())
        for user in userdata["userdata"]:
            if user["username"] == username and user["password"] == password:
                self.user = user
                return True
        return False
    # Accept incoming connection
    def _accept_connection(self):
        """ Accepts incoming client connections and hands off request processing
        to new thread.
        """
        try:
            with self.server:
                while True:
                    print(f'Waiting for incoming client connection...')
                    client, address = self.server.accept()
                    print(f'Accepted client connection from IP Address: {address[0]} and {address[1]}')
                    client_handler = threading.Thread(target=self._process_client_requests, args=(client, self.server))
                    client_handler.start()
        except Exception as e:
            print(f'Problem accepting connection: {e}')
    # Process connection in separate thread

    def _process_client_requests(self, client, server):
        """ Processes communication between client and server.
        """
        try:
            with client:
                logged_in = False
                while not logged_in:
                    request = client.recv(1024)
                    if not request:
                        break
                    credentials = request.decode('utf-8')
                    username, password = credentials.split(',')
                    logged_in = self._check_user(username, password)
                    if not logged_in:
                        return_message = json.dumps({"error": "no such username or password, please try again"})
                        client.send(bytearray(return_message, 'utf-8'))
                    else:
                        return_message = json.dumps({"success": "you are logged in as " + self.user['username']})
                        client.send(bytearray(return_message, 'utf-8'))

                continue_session = True
                while continue_session:
                    request = client.recv(1024)
                    if not request:
                        break
                    message = request.decode('utf-8')
                    arguments = message.split(',')
                    amount = None if len(arguments) <= 1 else arguments[1][0]
                    message = arguments[0]
                    continue_session = self.process_message(client, server, message, amount)

        except Exception as e:
            print(f'Problem processing client requests: {e}')

    def process_message(self, client, server, option, amount=None):
        match option:
            case "1":
                self.check_balance(client)
                return True
            case "2":
                self.add_money(client, amount)
                return True
            case "3":
                self.withdraw_money(client, amount)
                return True
            case "4":
                self.see_history(client)
                return True
            case "5":
                return False

    def check_balance(self, client):
        return_message = json.dumps({"user": self.user['username'], "balance": self.user['Current balance']})
        self.save_history(f"Checked Balance {dt.now().strftime('%m/%d/%Y %H:%M:%S')}")
        self.save_data()
        client.send(bytearray(return_message, 'utf-8'))

    def add_money(self, client, amount):
        pass

    def withdraw_money(self, client, amount):
        pass

    def see_history(self, client):
        return_message = json.dumps({"user": self.user['username'], "history": self.user['transaction']})
        client.send(bytearray(return_message, 'utf-8'))

    def save_history(self, transaction):
        self.user['transaction'].append(transaction)

    def save_data(self):

        with open("./userdata.json", "r") as file:
            tmp_userdata = json.loads(file.read())

        for idx, user in enumerate(tmp_userdata['userdata']):
            if self.user['username'] == user['username']:
                tmp_userdata['userdata'][idx] = self.user

        with open("./userdata.json", "w") as file:
            json.dump(tmp_userdata, file)

