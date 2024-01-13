import os
import sys
import traceback
from sock.server import Server
from sock.client import Client
from settings import _convert_to_correct_type


def clear() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def run_server() -> None:
    server = Server()
    server.serve()


def run_client() -> None:
    host = input("Enter server host ip: ").strip()
    if host == "":
        host = "localhost"

    port = input("Enter server host port: ").strip()
    if port == "":
        port = 12345

    client = Client(host, _convert_to_correct_type(port))
    client.connect()
    client.run()


def exit_program() -> None:
    sys.exit(0)


def main() -> None:
    try:
        prompt = """===[ Hub ]===
(1) Client
(2) Server
(3) Exit
-----------
Choice: """

        # check what we need to run
        run_type = input(prompt)
        if run_type == "1":
            run_client()
        elif run_type == "2":
            run_server()
        elif run_type == "3":
            exit_program()

        clear()
        main()
    except Exception as exception:
        print("\nError:", exception)
        traceback.print_exc()


if __name__ == "__main__":
    main()
