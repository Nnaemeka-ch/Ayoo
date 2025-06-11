# main.py

import tkinter as tk
from game import Okwe
from gui import setup_ui

def main():
    root = tk.Tk()
    game = Okwe(root)
    setup_ui(game)
    root.mainloop()

if __name__ == "__main__":
    main()
