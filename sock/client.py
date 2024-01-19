import socket
import sys
from multiprocessing import Process

from settings import load_settings
from sock.headers import FILE as file_header
from sock.headers import READY_FOR_FILE as server_ready_for_file
from sock.headers import USERNAME as set_username


class Client:
    def __init__(self, host: str, port: int):
        settings = load_settings()
        if settings == {}:
            raise Exception("Settings not found.")

        if not host or host == "":
            host = settings.get("host")
        if port == -1:
            port = settings.get("port")

        self.host = host
        self.port = port
        self.encoding_format = settings.get("encoding_format")
        self.buffer_size = settings.get("buffer_size")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")

            username = ""
            while username.strip().lower() in ["", "server"]:
                username = input("Username: ")

            self.send_message(f"{set_username} {username}")
        except Exception as e:
            print(f"Connection failed: {e}")
            sys.exit()

    def send_message(self, message) -> None:
        try:
            self.client_socket.sendall(message.encode(self.encoding_format))
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_message(self) -> str | None:
        data = self.client_socket.recv(self.buffer_size)
        if data:
            return data.decode(self.encoding_format)
        return None

    def send_file(self, file_path: str) -> None:
        try:
            with open(file=file_path, mode="rb") as file:
                file_data = file.read()
                file_size = len(file_data)
                file_data_sent = 0

                # inform server about incoming file
                self.send_message(f"{file_header} {file_path} {file_size}")

                # get acknowledgment from server
                acknowledgment = self.receive_message()
                if acknowledgment == server_ready_for_file:
                    # send file data in chunks
                    chunk_size = self.buffer_size
                    for i in range(0, file_size, min(file_size, chunk_size, file_size - file_data_sent)):
                        # send chunk
                        chunk = file_data[i:i + chunk_size]
                        self.client_socket.sendall(chunk)

                        # inform user
                        file_data_sent += len(chunk)
                        loading_bar = f"[{'=' * int(file_data_sent / file_size * 10)}{' ' * (10 - int(file_data_sent / file_size * 10))}]"
                        print(
                            f"\rSending file {loading_bar} {file_data_sent / file_size * 100:.2f}%",
                            end="",
                            flush=True
                        )
                    print()
                    print(f"File {file_path} sent successfully.")
                else:
                    raise ConnectionRefusedError("Server refused file")
        except Exception as e:
            print(f"Error sending file: {e}")

    def run(self) -> None:
        while True:
            message = input("Enter message (type 'exit' to quit): ").strip()
            if message.lower() == "exit":
                break
            elif message.lower().startswith("send_file "):
                self.send_file(message.replace("send_file ", ""))
            else:
                self.send_message(message)
        self.close()

    def close(self) -> None:
        self.client_socket.close()
