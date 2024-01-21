import os.path
import socket
import select
from datetime import datetime

from settings import load_settings
from sock.utils import get_downloads_path
from sock.headers import FILE as file_header
from sock.headers import READY_FOR_FILE as server_ready_for_file
from sock.headers import USERNAME as set_username


def hash_peername(peername) -> hash:
    return hash(str(peername))


class Server:
    def __init__(self):
        settings = load_settings()
        if settings == {}:
            raise Exception("Settings not found.")

        # load settings into vars
        self.max_clients = settings.get("max_clients")
        self.host = settings.get("host")
        self.port = settings.get("port")
        self.buffer_size = settings.get("buffer_size")
        self.encoding_format = settings.get("encoding_format")

        # other
        self.server_output = []

        # run
        self.running = False
        self.client_peer_hashes = {}
        self._create_socket(self.max_clients)

    def _create_socket(self, max_clients) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(max_clients)

        self.sockets = [self.server_socket]

    def _add_client(self, client_socket, addr, username) -> None:
        hashed_peername = hash_peername(addr)
        self.client_peer_hashes[hashed_peername] = username

        print(f"New connection from: {addr[0]}:{addr[1]}")
        self.sockets.append(client_socket)

    def lookup_client_by_peername(self, peername) -> str:
        hashed_peername = hash_peername(peername)
        if hashed_peername in self.client_peer_hashes.keys():
            return self.client_peer_hashes[hashed_peername]
        return "Anonymous"

    def set_client_username(self, peername, username) -> None:
        hashed_peername = hash_peername(peername)
        self.client_peer_hashes[hashed_peername] = username

    def send_message(self, client_socket, message) -> None:
        message_bytes = message.encode(self.encoding_format)
        client_socket.sendall(message_bytes)

    def broadcast_message(self, message) -> None:
        print(message)
        # FIXME
        # for client_socket in self.sockets:
        #     if client_socket != self.server_socket:
        #         self.send_message(client_socket, message)

    def get_next_server_output(self) -> str | None:
        if self.server_output:
            # return first & remove
            return self.server_output.pop(0)
        else:
            return None

    def handle_file_transfer(self, client_socket, file_name, file_size) -> None:
        try:
            # check if file already exists, so we don't overwrite
            if os.path.exists(f"{get_downloads_path()}/{file_name}"):
                file = file_name.split(".")
                file_extension = file.pop()
                file_name = f"{''.join(file)}__{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{file_extension}"

            # setup data
            received_data = b""
            remaining_bytes = file_size

            # inform client that we're ready for the file data
            self.send_message(client_socket, server_ready_for_file)

            # download
            while remaining_bytes > 0:
                chunk = client_socket.recv(min(self.buffer_size, remaining_bytes))
                if not chunk:
                    raise ConnectionAbortedError("Connection closed during file transfer")

                # update data & vars
                received_data += chunk
                remaining_bytes -= len(chunk)

                # show results
                loading_bar = f"[{'=' * int(len(received_data) / file_size * 10)}{' ' * (10 - int(len(received_data) / file_size * 10))}]"
                print(
                    f"\rDownloading file: <{file_name}> | {len(received_data)}/{file_size} bytes {loading_bar} {len(received_data) / file_size * 100:.2f}%",
                    end="",
                    flush=True
                )
            print()

            # write to file
            with open(file=f"{get_downloads_path()}/{file_name}", mode="wb") as file:
                file.write(received_data)
            print(f"File {file_name} received successfully!")
            self.send_message(client_socket, "File received successfully!")
        except Exception as e:
            print(f"Error during file transfer: {e}")

    def serve(self) -> None:
        self.running = True
        print(f"Server listening on {self.host}:{self.port} for {self.max_clients} clients")

        while self.running:
            readable, _, _ = select.select(self.sockets, [], [])
            for sock in readable:
                if sock == self.server_socket:
                    try:
                        client_socket, addr = sock.accept()
                        self.handle_new_client(client_socket, addr)
                    except OSError as e:
                        # WinError 10038: An operation was attempted on something that is not a socket
                        if e.errno == 10038:
                            break
                        else:
                            # handle other OSError cases
                            raise
                else:
                    # not server socket
                    try:
                        data = sock.recv(self.buffer_size)
                        username = self.lookup_client_by_peername(sock.getpeername())
                        if data:
                            if data.startswith(file_header.encode(self.encoding_format)):
                                print(f"Received file header from {username}!")

                                # retrieve file info
                                file_info = data.split(b" ")[1:][::-1]

                                # get file name
                                file_name = file_info.pop().decode(self.encoding_format).replace("\\", "/")
                                if "/" in file_name:
                                    file_name = file_name.split("/").pop()

                                file_size = int(file_info.pop())

                                # handle transfer
                                self.handle_file_transfer(sock, file_name, file_size)
                            else:
                                message = data.decode(self.encoding_format)
                                text = f"{username} says: {message}"

                                self.server_output.append(text)
                                self.broadcast_message(text)
                        else:
                            raise ConnectionAbortedError()
                    except (ConnectionResetError, ConnectionAbortedError):
                        self.handle_client_disconnect(sock)
                    except Exception as e:
                        print(f"Error: {e}")
                        self.handle_client_disconnect(sock)

    def stop(self) -> bool:
        if not self.running:
            return False

        # stop server from running
        self.running = False

        self.sockets.remove(self.server_socket)
        self.server_socket.close()

        # close client sockets
        for client_socket in self.sockets:
            self.send_message(client_socket, "Server closed.")
            self.handle_client_disconnect(client_socket)

        if len(self.sockets) != 0:
            return False

        # success
        print("Server closed.")
        return True

    def handle_new_client(self, client_socket, addr) -> None:
        try:
            username = client_socket.recv(self.buffer_size).decode(self.encoding_format)
            if set_username in username:
                username = username.replace(set_username, "").lstrip()
                self._add_client(client_socket, addr, username)
                self.broadcast_message(
                    f"Server: {username} connected to the server! ({len(self.sockets) - 1}/{self.max_clients})"
                )
            else:
                print(f"Didn't receive username from: {addr[0]}:{addr[1]}")
                client_socket.close()
        except Exception as e:
            print(f"Error handling new client: {e}")
            client_socket.close()

    def handle_client_disconnect(self, client_socket) -> None:
        client = self.lookup_client_by_peername(client_socket.getpeername())
        self.sockets.remove(client_socket)
        client_socket.close()
        if self.running:
            print(f"{client} left the server. ({len(self.sockets) - 1}/{self.max_clients})")
        else:
            print(f"Kicked {client} ({len(self.sockets)}/{self.max_clients}).")
