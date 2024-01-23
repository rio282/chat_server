import tkinter as tk

from gui.frames.client import ClientConfigureGUI
from gui.frames.server import ServerConfigureGUI


class MenuGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        tk.Button(
            self,
            text="Client",
            command=lambda: master.switch_frame_to(ClientConfigureGUI)
        ).pack()
        tk.Button(
            self,
            text="Server",
            command=lambda: master.switch_frame_to(ServerConfigureGUI)
        ).pack()
