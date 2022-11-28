"""
ELEKTRON © 2022
Written by melektron
www.elektron.work
24.11.22, 21:18

simple_digitizer - a simple, quick gui tool using Tkinter 
to enter vocabulary and store it in an ordered format.

"""

import tkinter as tk
import start_window


def main() -> int:
    win = start_window.StartWindow()
    win.mainloop()

    return 0


if __name__ == "__main__":
    exit(main())