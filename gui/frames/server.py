import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from threading import Thread
from tkinter.messagebox import showerror

from sock.server import Server


class ServerGUI(tk.Frame):
    def __init__(self, master: tk.Tk):
        tk.Frame.__init__(self, master)

        self.master = master
        self.text_area = None
        self.start_button = None
        self.stop_button = None
        self.create_gui()

        self.server_thread = None
        self.monitor_thread = None
        self.server = None

    def create_gui(self) -> None:
        # create gui
        self.text_area = scrolledtext.ScrolledText(
            self.master,
            wrap=tk.WORD,
            width=90,
            height=20,
            state=tk.DISABLED,
        )
        self.text_area.pack(pady=4)

        self.start_button = ttk.Button(self.master, text="Start Server", command=self.starter, state=tk.NORMAL)
        self.start_button.pack(pady=4)

        self.stop_button = ttk.Button(self.master, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=4)

    def monitor_server_output(self):
        while self.server_thread.is_alive():
            output_text = self.server.get_next_server_output()
            if output_text:
                self.update_text_area(output_text)

    def update_text_area(self, message):
        self.text_area["state"] = tk.NORMAL
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.see(tk.END)
        self.text_area["state"] = tk.DISABLED

    def starter(self):
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL

        # create server instance
        self.server = Server()

        # create server thread
        self.server_thread: Thread = Thread(target=self.server.serve)
        self.server_thread.daemon = True
        self.server_thread.start()

        # create monitor thread
        self.monitor_thread = Thread(target=self.monitor_server_output)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_server(self):
        if not self.server:
            return

        is_server_stopped = self.server.stop()
        if is_server_stopped:
            self.server_thread.join()
            self.monitor_thread.join()
            self.start_button["state"] = tk.NORMAL
            self.stop_button["state"] = tk.DISABLED
            self.update_text_area("Server closed.")
        else:
            showerror("Server Error", "Couldn't stop server. Reason: Unknown")


class ServerConfigureGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # TODO??? maybe???
        master.switch_frame_to(ServerGUI)
