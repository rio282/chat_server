import tkinter as tk
from tkinter import ttk
from typing import Tuple


class LoadingWindow(tk.Toplevel):
    def __init__(self, master, message):
        tk.Toplevel.__init__(self, master)
        self.title("Loading...")
        self.resizable = False
        self.geometry("300x100")

        self.message_label = ttk.Label(self, text=message)
        self.message_label.pack(pady=10)

        self.progressbar = ttk.Progressbar(self, mode="indeterminate")
        self.progressbar.pack(pady=10)

        self.start()

    def start(self):
        self.progressbar.start(10)

    def stop(self):
        self.message_label["text"] = "Done."
        self.progressbar.stop()
        self.progressbar.pack_forget()


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
