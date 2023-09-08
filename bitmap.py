import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

# Class that handles the image part of the GUI
class Bitmap(tk.Canvas):
    def __init__(self, master: ctk.CTk, path: str):
        super().__init__(master, background='#242424', bd=0, highlightthickness=0, relief='ridge')
        self.grid(row=0, column=1, sticky='nsew', rowspan=2, padx=10, pady=5)
        self.bind('<Configure>', lambda e : self.resize_image(e.width, e.height))
        self.update_image(path)
        self.path = path

    def update_image(self, path: str):
        self.image = Image.open(path)
        self.resize_image(self.winfo_width(), self.winfo_height())

    def resize_image(self, event_width: int, event_height: int):
        canvas_ratio = event_width / event_height
        image_ratio = self.image.width / self.image.height

        # Case 1: Canvas is wider than the image.
        if canvas_ratio > image_ratio:
            height = event_height
            width = int(height * image_ratio)
        # Case 2: Canvas is taller than the image.
        else:
            width = event_width
            height = int(width / image_ratio)

        # Place image.
        resized_image = self.image.resize((width, height))
        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.create_image(event_width / 2, event_height / 2, image=self.image_tk)