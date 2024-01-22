import os
import sys
import traceback
import tkinter as tk

from gui.server import ServerGUI
from gui.client import ClientGUI


def clear() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def run_server() -> None:
    root = tk.Tk()
    server = ServerGUI(root)
    server.start_server()


def run_client() -> None:
    host = input("Enter server host ip: ").strip()
    port = input("Enter server host port: ").strip()
    if port == "":
        port = -1

    root = tk.Tk()
    client = ClientGUI(root, host, port)
    client.start_client()


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
