import tkinter as tk
from socket import error as SOCKET_ERROR

from gui.frames.menu import MenuGUI
from gui.utils import center_master


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame_to(MenuGUI)

    def switch_frame_to(self, frame_class, **frame_class_constructor_params):
        try:
            new_frame = frame_class(self, **frame_class_constructor_params)
        except Exception as e:
            if isinstance(e, (SOCKET_ERROR, OSError)):
                return
            raise

        # destroy previous
        if self._frame:
            self._frame.destroy()

        # build ui
        self._frame = new_frame
        self._frame.pack(expand=True, fill=tk.BOTH)

        # sexy
        self.title(frame_class.__name__)
        center_master(self)
