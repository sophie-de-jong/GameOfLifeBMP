import customtkinter as ctk
from game_of_life import INV_RULESTRINGS, RULESTRINGS
import os

class InfoMenu(ctk.CTkTabview):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, state='disabled', text_color_disabled='#ffffff')
        self.grid(row=1, column=0, sticky='nsew')

        # Tabs.
        self.add('Info')

        # Info variables.
        self.generations = ctk.StringVar()
        self.secs_per_generation = ctk.StringVar()
        self.rulestring = ctk.StringVar()
        self.rulestring_type = ctk.StringVar()
        self.file_name = ctk.StringVar()

        # Update info variables.
        self.update_generations(0)
        self.update_gen_load_time(0)
        self.update_rulestring(RULESTRINGS['Default'])

        # Widgets.
        self.create_widgets()

    def update_generations(self, generations: int) -> None:
        self.generations.set(f'Generations: {generations}')

    def update_gen_load_time(self, secs_per_generation: int) -> None:
        self.secs_per_generation.set(f'Generation load time: {secs_per_generation}s')

    def update_rulestring(self, rulestring: str) -> None:
        rulestr_type = INV_RULESTRINGS.get(rulestring, 'Custom')
        self.rulestring.set(f'Rulestring: {rulestring} ({rulestr_type})')

    def update_file_name(self, path: str) -> None:
        file_name = os.path.basename(path)
        self.file_name.set(f'Bitmap file: {file_name}')

    def create_widgets(self):
        info_frame = ctk.CTkFrame(self.tab('Info'))
        label1 = ctk.CTkLabel(info_frame, textvariable=self.generations)
        label2 = ctk.CTkLabel(info_frame, textvariable=self.secs_per_generation)
        label3 = ctk.CTkLabel(info_frame, textvariable=self.rulestring)
        label4 = ctk.CTkLabel(info_frame, textvariable=self.file_name)
        info_frame.pack(expand=True, fill='both')
        label1.pack(fill='both', padx=3, pady=8)
        label2.pack(fill='both', padx=3, pady=8)
        label3.pack(fill='both', padx=3, pady=8)
        label4.pack(fill='both', padx=3, pady=8)
