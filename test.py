import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

root = ctk.CTk()

def resize(event):
    img_tk = ImageTk.PhotoImage(img)
    canvas.create_image(event.width / 2, event.height / 2, image=img_tk)

canvas = tk.Canvas(root)
canvas.pack()
canvas.bind('<Configure>', resize)

img = Image.open('gui/bitmap.bmp')

root.mainloop()