import customtkinter as ctk
from typing import Callable

class Panel(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame):
        super().__init__(master, fg_color='#4a4a4a')
        self.pack(fill='x', pady=4, ipady=8)

class ButtonPanel(Panel):
    def __init__(self, master: ctk.CTkFrame, text: str, command):
        super().__init__(master)
        button = ctk.CTkButton(text=text, )