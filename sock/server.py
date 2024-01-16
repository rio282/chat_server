import socket
import select

from settings import load_settings
from sock.utils import get_downloads_path
from sock.headers import FILE as file_header
from sock.headers import READY_FOR_FILE as server_ready_for_file


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

        # run
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
        for client_socket in self.sockets:
            if client_socket != self.server_socket:
                self.send_message(client_socket, message)

    def handle_file_transfer(self, client_socket, file_name, file_size) -> None:
        try:
            received_data = b""
            remaining_bytes = file_size

            # inform client that we're ready for the file data
            self.send_message(client_socket, server_ready_for_file)

            while remaining_bytes > 0:
                chunk = client_socket.recv(min(self.buffer_size, remaining_bytes))
                if not chunk:
                    raise ConnectionAbortedError("Connection closed during file transfer")

                received_data += chunk
                remaining_bytes -= len(chunk)

            # write to file
            with open(file=f"{get_downloads_path()}/{file_name}", mode="wb") as file:
                file.write(received_data)
            print(f"File received successfully.")
        except Exception as e:
            print(f"Error during file transfer: {e}")

    def serve(self) -> None:
        print(f"Server listening on {self.host}:{self.port} for {self.max_clients} clients")
        while True:
            readable, _, _ = select.select(self.sockets, [], [])
            for sock in readable:
                if sock == self.server_socket:
                    client_socket, addr = self.server_socket.accept()
                    self.handle_new_client(client_socket, addr)
                else:
                    try:
                        data = sock.recv(self.buffer_size)
                        username = self.lookup_client_by_peername(sock.getpeername())
                        if data:
                            if data.startswith(file_header.encode(self.encoding_format)):
                                print("Received file header!")

                                # retrieve file info
                                file_info = data.split(b" ")[1:][::-1]

                                file_name = file_info.pop().decode(self.encoding_format).replace("\\", "/")
                                if "/" in file_name:
                                    file_name = file_name.split("/").pop()
                                file_size = int(file_info.pop())

                                # handle transfer
                                self.handle_file_transfer(sock, file_name, file_size)
                            else:
                                if not data.startswith(b"file_content "):
                                    print(f"{username} says: {data.decode(self.encoding_format)}")
                        else:
                            raise ConnectionAbortedError()
                    except (ConnectionResetError, ConnectionAbortedError):
                        self.handle_client_disconnect(sock)
                    except Exception as e:
                        print(f"Error: {e}")
                        self.handle_client_disconnect(sock)

    def handle_new_client(self, client_socket, addr) -> None:
        try:
            username = client_socket.recv(self.buffer_size).decode(self.encoding_format)
            if username:
                self._add_client(client_socket, addr, username)
                print(f"{username} connected to the server! ({len(self.sockets) - 1}/{self.max_clients})")
            else:
                print(f"Didn't receive username from: {addr[0]}:{addr[1]}")
                client_socket.close()
        except Exception as e:
            print(f"Error handling new client: {e}")
            client_socket.close()

    def handle_client_disconnect(self, sock) -> None:
        client = self.lookup_client_by_peername(sock.getpeername())
        sock.close()
        self.sockets.remove(sock)
        print(f"{client} left the server. ({len(self.sockets) - 1}/{self.max_clients})")
