import os
import sys
import traceback
from sock.server import Server
from sock.client import Client


def clear() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def run_server() -> None:
    server = Server()
    server.serve()


def run_client() -> None:
    client = Client("localhost", 12345)
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
        if run_type == "2":
            run_server()
        if run_type == "3":
            exit_program()
        else:
            clear()
            main()
    except Exception as exception:
        print("\nError:", exception)
        traceback.print_exc()


if __name__ == "__main__":
    main()
