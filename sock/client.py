import socket
import sys

from settings import load_settings


class Client:
    def __init__(self, host, port):
        settings = load_settings()
        if settings == {}:
            raise Exception("Settings not found.")

        self.host = host
        self.port = port
        self.encoding_format = "utf-8"
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")

            username = ""
            while username.strip() == "":
                username = input("Username: ")

            self.send_message(username)
        except Exception as e:
            print(f"Connection failed: {e}")
            sys.exit()

    def send_message(self, message):
        try:
            self.client_socket.sendall(message.encode(self.encoding_format))
        except Exception as e:
            print(f"Error sending message: {e}")

    def run(self):
        while True:
            message = input("Enter message (type 'exit' to quit): ")
            if message.lower() == "exit":
                break
            self.send_message(message)

        self.close()

    def close(self):
        self.client_socket.close()
