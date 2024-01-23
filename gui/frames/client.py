import os
import random
import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
from tkinter.messagebox import showinfo, showerror
from threading import Thread

from sock.utils import is_valid_ipv4, is_valid_port
from settings import load_settings
from sock.client import Client


class TkWait:
    def __init__(self, master, milliseconds):
        self.duration = milliseconds
        self.master = master

    def __enter__(self):
        self.resume = tk.BooleanVar(value=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.master.after(self.duration, self.resume.set, True)
        self.master.wait_variable(self.resume)


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
        self.create_gui()

        # client instance
        self.client = None
        try:
            self.start_client()
        except Exception:
            raise

    def create_gui(self) -> None:
        # create gui components
        self.message_entry = tk.Entry(self, width=75)
        self.message_entry.bind("<Return>", self.send_message)
        self.send_button = tk.Button(self, text="Send Message", command=self.send_message)

        self.choose_files_button = tk.Button(self, text="Choose file...", command=self.choose_file_by_browsing)
        self.send_file_button = tk.Button(self, text="Send File", command=self.send_file)

        self.disconnect_button = tk.Button(self, text="Disconnect", command=self.disconnect_and_close)

        # padding
        self.message_entry.pack(pady=10)
        self.send_button.pack(pady=10)
        self.choose_files_button.pack(pady=10)
        self.send_file_button.pack(pady=10)
        self.disconnect_button.pack(pady=10)

    def start_client(self) -> None:
        try:
            self.client = Client(self.username, self.host, self.port)
            self.client.connect()
        except Exception as error_message:
            showerror("Server Information", str(error_message))
            self.disconnect_and_close()
            raise

    def send_message(self, event=None) -> None:
        message = self.message_entry.get().strip()
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
        self.master.switch_frame_to(ClientConfigureGUI)


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

        self.progressbar = ttk.Progressbar(self, mode="indeterminate")

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
                f"Invalid username '{username}'. Reserved usernames are: {', '.join(self.reserved_usernames)}"
            )
            return

        # everything is ok
        self.connect_button["state"] = tk.DISABLED
        self.progressbar.pack(padx=20, pady=20)

        # fake loading lol
        with TkWait(self, random.randint(50, 500)) as wait:
            self.progressbar.start(10)
        self.progressbar.pack_forget()

        # switch frame (freezes app because of client connect lol)
        self.master.switch_frame_to(ClientGUI, username=username, host=host, port=int(port))
