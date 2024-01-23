import re
import tkinter as tk
from typing import Tuple


def center_master(master: tk.Tk, window_dimensions: Tuple[int, int] = (800, 600)) -> None:
    # center
    master.resizable(False, False)

    # get dimensions
    window_width = window_dimensions[0]
    window_height = window_dimensions[1]
    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()

    # calc new position in screen
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))
    master.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    # set topmost
    master.lift()
    master.call("wm", "attributes", ".", "-topmost", True)
    master.after_idle(master.call, "wm", "attributes", ".", "-topmost", False)


def is_valid_ipv4(ip: str):
    if ip == "localhost":
        return True

    ipv4_pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    return bool(ipv4_pattern.match(ip))


def is_valid_port(port: int | str):
    try:
        port = int(port)
    except ValueError:
        return False

    return 0 < port < 65535
