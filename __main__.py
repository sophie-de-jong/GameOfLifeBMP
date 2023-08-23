# Python modules.
from tkinter import filedialog, messagebox
import tkinter as tk
import threading
import typing
import random
import shutil
import os

# Third party modules.
from selenium import webdriver
from selenium.common import exceptions

# Personal modules.
import bitmap

# Text was too big to put directly into the function where it is called.
BITMAP_SIZE_WARNING = '{} is a large bitmap and can result in slow performance. Recommended bitmap size is 400x300 pixels or smaller.\n\nAre you sure you wish to continue?'

# Used as a decorator to run the function in a thread.
# This is needed so that the GUI window can still be interacted with
# while the Game of Life or any other task is running.
def use_thread(func) -> typing.Callable:
    def run(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return run

# Object to store a group of tkinter checkboxes.
class CheckPanel(tk.Frame):
    CHECKBOX_DEFAULT = -1

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(**kwargs)

        # Place the text above the checkboxes.
        tk.Label(self, text=text).grid(row=0, column=0)

        # Initialize a list to hold all of the IntVar objects.
        self.options = []

        for i in range(9):
            self.options.append(tk.IntVar(value=CheckPanel.CHECKBOX_DEFAULT))

            tk.Checkbutton(
                master=self,
                text=str(i),
                variable=self.options[i],
                onvalue=i,
                offvalue=CheckPanel.CHECKBOX_DEFAULT,
                height=2,
                width=5
            ).grid(row=i + 1, column=0)

    # Used in App.get_rulestring()
    def __str__(self) -> str:
        return ''.join(str(i.get()) for i in self.options if i.get() >= 0)
    
    # Get a checkbox intvar by number.
    def get_checkbox(self, i: int) -> tk.IntVar:
        return self.options[i]
    
    # Manually randomize all the checkboxes.
    def set_random(self) -> None:
        for i, intvar in enumerate(self.options):
            intvar.set(random.choice((CheckPanel.CHECKBOX_DEFAULT, i)))

    # Manually clear all the checkboxes.
    def set_clear(self) -> None:
        for intvar in self.options:
            intvar.set(CheckPanel.CHECKBOX_DEFAULT)

    # Disable this widget to prevent the user from interacting in inconvenient circumstances.
    def disable(self) -> None:
        for checkbutton in self.winfo_children():
            checkbutton.configure(state=tk.DISABLED)

    # Opposite of CheckPanel.disable().
    def enable(self) -> None:
        for checkbutton in self.winfo_children():
            checkbutton.configure(state=tk.NORMAL)

# Object to store a group of tkinter buttons.
class ButtonPanel(tk.Frame):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.buttons = {}
        self.labels = {}

    # Get a button by name.
    def get_button(self, name: str) -> tk.Button:
        return self.buttons[name]
    
    # Get a label by name.
    def get_label(self, name: str) -> tk.Label:
        return self.labels[name]

    # Add a new button to the panel.
    # Each button gets stored in a dictionary with the name argument being its key
    # and the tkinter button being the value. This allows retrieving specific buttons
    # we may need throughout the program by indexing into this object.
    def add_button(self, name: str, **kwargs) -> None:
        button = tk.Button(self, **kwargs)
        self.buttons[name] = button
        button.pack()

    # Add a new label (or text) to the panel.
    def add_label(self, name: str, **kwargs) -> None:
        label = tk.Label(self, **kwargs)
        self.labels[name] = label
        label.pack()

    # Disable this widget to prevent the user from interacting in inconvenient circumstances.
    def disable(self) -> None:
        for widget in self.winfo_children():
            widget.configure(state=tk.DISABLED)

    # Opposite of ButtonPanel.disable().
    def enable(self) -> None:
        for widget in self.winfo_children():
            widget.configure(state=tk.NORMAL)

# Main class that runs the program.
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        
        # Window configuration.
        self.title('Game of Life Launcher')
        self.geometry('250x700')

        # Initialize all four frames. Each frame is stored in a dictionary
        # with its spatial position as key, allowing for intuitive retrieval
        # of frames within the code.
        self.frame = {
            'top':    ButtonPanel(borderwidth=5),
            'bottom': ButtonPanel(borderwidth=5),
            'left':   CheckPanel(text='Alive neighbours\nneeded to be born', borderwidth=5),
            'right':  CheckPanel(text='Alive neighbours\nneeded to survive', borderwidth=5)
        }

        # Add each button to the button panels.
        self.frame['top'].add_button('run', text='Run', command=self.run_game, width=100, height=3)
        self.frame['top'].add_button('file', text='Select a file...', command=self.get_filename, width=100, height=2)
        self.frame['top'].add_label('text', text='\nCustom rules:\n')
        self.frame['bottom'].add_button('default', text='Default', command=self.default_rulestring, width=100)
        self.frame['bottom'].add_button('random', text='Random', command=self.random_rulestring,  width=100)
        self.frame['bottom'].add_button('reverse', text='Black/White Reversal: On', command=self.toggle_reversal, width=100)

        # Pack each panel to the canvas.
        for side, panel in self.frame.items():
            panel.pack(side=side, fill=tk.BOTH)

        # Set checkbox initial values to default of B23/S3.
        self.default_rulestring()

        self.is_reversed = True

        # Flag variable to check if the game is running.
        self.is_running = False
        
        # Initialize filename variable.
        self.filename = ''

    def get_rulestring(self) -> str:
        return f'B{self.frame["left"]!s}/S{self.frame["right"]!s}'
    
    # Fallback methods.
    # Each one uses a thread so that the main GUI window still works when these functions
    # are running.
    @use_thread
    def get_filename(self) -> str:
        # Prompt the user to open a file.
        filename = filedialog.askopenfilename(
            title='Open a bitmap file',
            filetypes=(('bitmap files', '*.bmp'),),
        )

        # If the user closed the window instead of choosing a file, return.
        if not filename:
            return

        # Edit the button text and update the filename variable.
        self.frame['top'].get_button('file').configure(text=os.path.basename(filename))
        self.filename = filename

    @use_thread
    def toggle_reversal(self) -> None:
        self.is_reversed = not self.is_reversed
        text = 'Black/White Reversal: ' + ('On' if self.is_reversed else 'Off')
        self.frame['bottom'].get_button('reverse').configure(text=text)

    @use_thread
    def random_rulestring(self) -> None:
        self.frame['left'].set_random()
        self.frame['right'].set_random()

    @use_thread
    def default_rulestring(self) -> None:
        self.frame['left'].set_clear()
        self.frame['right'].set_clear()

        # Default B3/S23.
        self.frame['left'].get_checkbox(3).set(3)
        self.frame['right'].get_checkbox(2).set(2)
        self.frame['right'].get_checkbox(3).set(3)

    @use_thread
    def stop_game(self) -> None:
        # Modify game running flag.
        self.is_running = False

        # Revert stop button back to run button.
        self.frame['top'].get_button('run').configure(
            text='Run', 
            command=self.run_game
        )
        
        # Enable frames again.
        for label in self.frame.values():
            label.enable()

    @use_thread
    def run_game(self) -> None:
        # Let the user know if they forgot to select a file.
        if not self.filename:
            messagebox.showerror('No file selected', 'Please select a file before proceeding.')
            return

        # Set game running flag to True.
        self.is_running = True

        # Get rulestring and create a Game of Life object.
        rulestring = self.get_rulestring()
        game = bitmap.GameOfLife(self.filename, rulestring, is_reversed=self.is_reversed)

        # Warn user if the file is too large.
        volume = game.width * game.height * game.bit_depth
        if volume > 4e6:
            confirm = messagebox.askquestion('File exceeds size threshold', BITMAP_SIZE_WARNING.format(os.path.basename(self.filename)))
            # Cancel the process if the user doesn't reply with yes.
            if confirm != 'yes':
                return

        # Disable frames in order to not mess up settings as the Game of Life is running.
        for label in self.frame.values():
            label.disable()

        # Modify run button to stop button.
        self.frame['top'].get_button('run').configure(
            text='Stop', 
            command=self.stop_game, 
            state=tk.NORMAL
        )

        # Get directory of current file.
        directory = os.path.dirname(__file__)

        # Copy input bitmap and initialize the result.bmp file.
        shutil.copyfile(self.filename, directory + '/result.bmp')

        # Open Firefox with the HTML.
        try:
            driver = webdriver.Firefox()
            driver.get(f'file:///{directory}/webviewer.html')

        # Selenium cannot find Firefox or does not have permissions to access it.
        except exceptions.NoSuchDriverException:
            messagebox.showerror('Unable to locate Firefox', 'Please install Firefox before proceeding.')
            return

        # Keep calculating generations of the Game of Life until the user presses
        # the stop button or closed the browser window.
        while self.is_running:
            # Play one iteration of the Game of Life and save it to a file.
            game.tick()
            game.save_as('result.bmp')

            # Try to refresh the browser and stop running if the user closed the window.
            try:
                driver.refresh()
            except exceptions.WebDriverException:
                self.is_running = False

        # Close browser window manually and stop the Game of Life process.
        driver.quit()
        self.stop_game()

# Main code.
# Run the application.
if __name__ == '__main__':
    App().mainloop()
