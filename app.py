# Python modules.
import threading
import typing
import shutil
import os

# Third party modules.
import customtkinter as ctk
from tkinter import messagebox, filedialog

# Personal modules.
import game_of_life
from button_menu import ButtonMenu
from info_menu import InfoMenu
from bitmap import Bitmap

# Text was too big to put directly into the function where it is called.
BITMAP_SIZE_WARNING = '{} is a large bitmap and can result in slow performance. Recommended bitmap size is 400x400 pixels or smaller.\n\nAre you sure you wish to continue?'
TUTORIAL_IMAGE_PATH = 'gui/tutorialimage.bmp'

class App(ctk.CTk):
    def __init__(self, title: str, size: tuple[int, int]) -> None:
        # Window setup.
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0], size[1])
        self.init_parameters()

        # Layout.
        self.rowconfigure(0, weight=3, uniform='a')
        self.rowconfigure(1, weight=2, uniform='a')
        self.columnconfigure(0, weight=2, uniform='b')
        self.columnconfigure(1, weight=6, uniform='b')

        # Image path.
        self.image_path = TUTORIAL_IMAGE_PATH
        self.is_running = False

        # Widgets.
        self.button_menu = ButtonMenu(self)
        self.info_menu = InfoMenu(self)
        self.info_menu.update_file_name(TUTORIAL_IMAGE_PATH)
        self.bitmap = Bitmap(self, path=TUTORIAL_IMAGE_PATH)

        # Run app.
        self.mainloop()

    def init_parameters(self):
        self.run_game = ctk.BooleanVar(value=False)
        self.run_game.trace('w', lambda: self.run_game_of_life if self.run_game.get() else self.stop_game_of_life)

    def open_image(self) -> None:
        # Prompt the user to open a file.
        self.image_path = filedialog.askopenfilename(
            title='Open a bitmap file',
            filetypes=(('bitmap files', '*.bmp'),),
        )

        # If the user closed the window instead of choosing a file, return.
        if not self.image_path:
            return

        # Edit the button text and update the image.
        self.button_menu.file_button.configure(text=os.path.basename(self.image_path))
        self.bitmap.update_image(self.image_path)
        self.info_menu.update_file_name(self.image_path)

    def run_game_of_life(self):
        # Get rulestring and create a Game of Life object.
        rulestring = self.button_menu.rulestring.get()
        game = game_of_life.GameOfLife(self.image_path, rulestring)

        # Warn user if the file is too large.
        volume = game.width * game.height * game.bit_depth
        if volume > 4e6:
            confirm = messagebox.askquestion('File exceeds size threshold', BITMAP_SIZE_WARNING.format(os.path.basename(self.filename)))
            # Cancel the process if the user doesn't reply with yes.
            if confirm != 'yes':
                return

        # Disable frames in order to not mess up settings as the Game of Life is running.
        for widget in self.button_menu.winfo_children():
            widget.configure(state='disabled')

        # Modify run button to stop button.
        self.button_menu.run_button.configure(text='Stop', command=self.stop_game_of_life, state='enabled')

        # Get directory of current file.
        directory = os.path.dirname(__file__)

        # Copy input bitmap and initialize the result.bmp file.
        shutil.copyfile(self.image_path, directory + '/result.bmp')

        # Keep calculating generations of the Game of Life until the user presses
        # the stop button or closed the browser window.
        self.is_running = True
        while self.is_running:
            # Play one iteration of the Game of Life and save it to a file.
            game.tick()
            game.save_as('result.bmp')
            self.bitmap.update_image('result.bmp')

    def stop_game_of_life(self):
        # Enable frames in order to not mess up settings as the Game of Life is running.
        for widget in self.button_menu.winfo_children():
            widget.configure(state='enable')

        # Modify run button to stop button.
        self.button_menu.run_button.configure(text='Run', command=self.stop_game_of_life, state='enabled')
        self.is_running = False

# Driver code.
if __name__ == '__main__':
    App('Game of Life BMP', (1000, 600))