import sys
import tkinter as tk
from tkinter import ttk

from gui.frames.client import ClientConfigureGUI
from gui.frames.server import ServerConfigureGUI


class MenuGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        center_frame = tk.Frame(self)
        center_frame.grid(row=0, column=0)

        self.welcome_label = ttk.Label(
            center_frame,
            text="Welcome!",
            font=("Helvetica", 24)
        )
        self.client_button = ttk.Button(
            center_frame,
            text="Client",
            command=lambda: master.switch_frame_to(ClientConfigureGUI),
            width=10
        )
        self.server_button = ttk.Button(
            center_frame,
            text="Server",
            command=lambda: master.switch_frame_to(ServerConfigureGUI),
            width=10
        )
        self.exit_button = ttk.Button(
            center_frame,
            text="Exit",
            command=sys.exit,
            width=5
        )

        self.welcome_label.pack(pady=0)
        self.client_button.pack(pady=2)
        self.server_button.pack(pady=2)
        self.exit_button.pack(pady=2)

        # center shit
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
