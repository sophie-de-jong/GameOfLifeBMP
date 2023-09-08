import customtkinter as ctk
import random

import game_of_life

# Class that handles all the buttons and tab GUI.
class ButtonMenu(ctk.CTkTabview):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)
        self.app = master
        self.grid(row=0, column=0, sticky='nsew')

        # Tabs.
        self.add('General')
        self.add('Options')
        self.add('Export')

        # Rulestring.
        self.rulestring = ctk.StringVar(value=game_of_life.RULESTRINGS['Default'])
        self.rulestring.trace('w', self.check_entry)

        # Widgets.
        self.create_widgets()

    def create_widgets(self):
        # General Tab.
        general_frame    = ctk.CTkFrame(self.tab('General'))
        self.run_button  = ctk.CTkButton(general_frame, text='Run', command=self.app.run_game_of_life)
        self.file_button = ctk.CTkButton(general_frame, text='Select a file...', command=self.app.open_image)
        general_frame   .pack(expand=True, fill='both')
        self.run_button .pack(expand=True, fill='both', padx=3, pady=3)
        self.file_button.pack(expand=True, fill='both', padx=3, pady=3) 

        # Options Tab.
        options_frame      = ctk.CTkFrame(self.tab('Options'))
        self.rule_select   = ctk.CTkComboBox(options_frame, variable=self.rulestring, border_color='green', values=game_of_life.RULESTRINGS, command=self.update_entry)
        self.invert_button = ctk.CTkButton(options_frame, text='Invert', command=self.invert_rulestring)
        self.random_button = ctk.CTkButton(options_frame, text='Random', command=self.random_rulestring)
        options_frame     .pack(expand=True, fill='both') 
        self.rule_select  .pack(fill='x', padx=3, pady=3)
        self.invert_button.pack(expand=True, fill='both', padx=3, pady=3)
        self.random_button.pack(expand=True, fill='both', padx=3, pady=3)

    def update_entry(self, *_) -> None:
        rulestring = game_of_life.RULESTRINGS.get(self.rulestring.get())
        if rulestring: 
            self.rule_select.set(rulestring)

    def check_entry(self, *_):
        rulestring = self.rulestring.get()
        B_str, S_str = game_of_life.split_rulestring(rulestring)
        has_valid_chars = set(rulestring) <= set('BS012345678/')
        has_letters = rulestring.count('B') == 1 and rulestring.count('S') == 1
        has_digits = (B_str.isdigit() or not B_str) and (S_str.isdigit() or not S_str)

        if has_valid_chars and has_letters and has_digits:
            self.rule_select.configure(border_color='green')
        else:
            self.rule_select.configure(border_color='red')

    def random_rulestring(self):
        B, S = 'B', 'S'
        for i in range(random.randrange(10)):
            B += random.choice(('', str(i)))
            S += random.choice(('', str(i)))
        self.rulestring.set(f'{B}/{S}')

    def invert_rulestring(self):
        rulestring = self.rulestring.get()
        rule_split = game_of_life.split_rulestring(rulestring)
        B_prime, S_prime = (set('012345678') - set(s) for s in rule_split)
        B = 'B' + ''.join(sorted(str(8 - int(i)) for i in S_prime))
        S = 'S' + ''.join(sorted(str(8 - int(i)) for i in B_prime))
        self.rulestring.set(f'{B}/{S}')
