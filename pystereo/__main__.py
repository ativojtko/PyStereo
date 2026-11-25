import tkinter as tk
from .gui.main_window import PyStereoApp

def main():
    root = tk.Tk()
    PyStereoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()