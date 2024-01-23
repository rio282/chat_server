import os
import tkinter as tk
from tkinter import scrolledtext, filedialog
from tkinter.messagebox import showinfo
from threading import Thread

from gui.utils import is_valid_ipv4, is_valid_port
from settings import load_settings
from sock.client import Client


class ClientGUI(tk.Frame):
    def __init__(self, master, username: str, host: str, port: int):
        tk.Frame.__init__(self, master)

        self.master = master
        self.username = username
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

        self.start_client()

    def create_gui(self) -> None:
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

    def start_client(self) -> None:
        self.client = Client(self.username, self.host, self.port)
        self.client.connect()

    def send_message(self, event=None) -> None:
        message = self.message_entry.get().strip()
        if message.lower() == "exit":
            self.master.destroy()
            return

        self.message_entry.delete(0, tk.END)
        self.client.send_message(message)

    def send_file(self) -> None:
        if not self.chosen_file:
            showinfo("Client GUI", "No file selected.")
            return

        file_path = self.chosen_file
        if file_path.strip() != "":
            self.client.send_file(file_path)
            self.chosen_file = None

    def choose_file_by_browsing(self) -> None:
        file = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select a file",
            filetypes=(("all files", "*.*"), ("Text files", "*.txt"))
        )
        self.chosen_file = file

    def disconnect_and_close(self) -> None:
        self.client.close()
        self.master.destroy()


class ClientConfigureGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.reserved_usernames = ["", "server"]

        settings = load_settings()

        self.host_entry = tk.Entry(self)
        self.host_entry.insert(0, settings.get("host"))
        self.host_entry.pack(pady=5)

        self.port_entry = tk.Entry(self)
        self.port_entry.insert(0, settings.get("port"))
        self.port_entry.pack(pady=5)

        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        self.connect_button = tk.Button(self, text="Connect", command=self.connect, pady=10)
        self.connect_button.pack()

    def connect(self, event=None) -> None:
        host = self.host_entry.get()
        if not is_valid_ipv4(host):
            showinfo("Error", "Invalid host.")
            return

        port = self.port_entry.get()
        if not is_valid_port(port):
            showinfo("Error", "Invalid port.")
            return

        username = self.username_entry.get().strip()
        if username.lower() in self.reserved_usernames:
            showinfo(
                "Error",
                f"Invalid username {username}. Reserved usernames are: {', '.join(self.reserved_usernames)}"
            )
            return

        self.master.switch_frame_to(ClientGUI, username=username, host=host, port=int(port))
