"""
ELEKTRON © 2022
Written by melektron
www.elektron.work
24.11.22, 21:34

The window that shows up at launch allowing the user to select the 
vocabulary folder to load
"""

import tkinter as tk
import crossfiledialog as filedialog
import style_config as styles


class StartWindow(tk.Tk):
    bt_open_hive: tk.Button

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # configure window basics
        self.title("Simple Digitizer - Alpha")
        self.geometry("500x300")

        self.bt_open_hive = tk.Button(
            self, text="Open vocabulary hive", font=styles.arial1, command=self.open_hive
        )
        self.bt_open_hive.pack(pady=10)

    
    def open_hive(self):
        selection = filedialog.choose_folder("Select Vocabulary Hive ...")
        print(selection)
