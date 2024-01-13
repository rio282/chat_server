import socket
import select
from settings import load_settings


def hash_peername(peername) -> hash:
    return hash(str(peername))


class Server:
    def __init__(self):
        settings = load_settings()
        if settings == {}:
            raise Exception("Settings not found.")

        # load settings into vars
        max_clients = settings.get("max_clients")
        self.host = settings.get("host")
        self.port = settings.get("port")
        self.buffer_size = settings.get("buffer_size")
        self.encoding_format = settings.get("encoding_format")

        # run
        self.client_peer_hashes = {}
        self._create_socket(max_clients)

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
        return "Unknown"

    def set_client_username(self, hashed_peername) -> None:
        pass

    def serve(self) -> None:
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            readable, _, _ = select.select(self.sockets, [], [])
            for sock in readable:
                if sock == self.server_socket:
                    client_socket, addr = self.server_socket.accept()
                    self.handle_new_client(client_socket, addr)
                else:
                    try:
                        data = sock.recv(self.buffer_size)
                        if data:
                            username = self.lookup_client_by_peername(sock.getpeername())
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
                print(f"{username} connected to the server! ")
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
        print(f"{client} left the server. :(")
