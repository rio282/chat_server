import tkinter as tk
from tkinter import scrolledtext, filedialog
from threading import Thread

from gui.utils import center_master
from sock.client import Client


class ClientGUI:
    def __init__(self, master: tk.Tk, host: str, port: int):
        self.master = master
        self.host = host
        self.port = port

        # user related stuff
        self.chosen_file = None

        # gui
        self.message_entry = None
        self.send_button = None
        self.choose_files_button = None
        self.send_file_button = None
        self.disconnect_button = None

        # client instance
        self.client = None
        self.create_gui()

    def create_gui(self) -> None:
        self.master.title("Client GUI")

        # create gui components
        self.message_entry = tk.Entry(self.master, width=75)
        self.message_entry.bind("<Return>", self.send_message)
        self.send_button = tk.Button(self.master, text="Send Message", command=self.send_message)

        self.choose_files_button = tk.Button(self.master, text="Choose file...", command=self.choose_file_by_browsing)
        self.send_file_button = tk.Button(self.master, text="Send File", command=self.send_file)

        self.disconnect_button = tk.Button(self.master, text="Disconnect", command=self.disconnect_and_close)

        # padding
        self.message_entry.pack(pady=10)
        self.send_button.pack(pady=10)
        self.choose_files_button.pack(pady=10)
        self.send_file_button.pack(pady=10)
        self.disconnect_button.pack(pady=10)

        center_master(self.master)

    def start_client(self) -> None:
        # start client
        self.client = Client(self.host, self.port)

        # TODO: make a gui for this
        self.client.connect()

        # start gui
        self.master.mainloop()

    def send_message(self, event=None) -> None:
        message = self.message_entry.get().strip()
        if message.lower() == "exit":
            self.master.destroy()
            return

        self.message_entry.delete(0, tk.END)
        self.client.send_message(message)

    def send_file(self) -> None:
        file_path = self.chosen_file
        self.chosen_file = None
        if file_path and file_path.strip() != "":
            self.client.send_file(file_path)

    def choose_file_by_browsing(self) -> None:
        file = filedialog.askopenfilename(
            initialdir="/",
            title="Select a file",
            filetypes=(("all files", "*.*"), ("Text files", "*.txt"))
        )
        self.chosen_file = file

    def disconnect_and_close(self) -> None:
        self.client.close()
        self.master.destroy()
