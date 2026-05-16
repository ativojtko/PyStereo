import tkinter as tk
from tkinter import ttk, messagebox, filedialog

AUTHORS = "Hana Balažovjechová, Rastislav Vojtko"
VERSION = "0.1.0"

class Stereo:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Stereo {VERSION}")
        self.root.geometry("1000x600+200+200")
        
        # Ošetrenie ikony pre prípad, že súbor chýba alebo bežíte na inom OS
        try:
            self.root.iconbitmap("stereo.ico")
        except Exception:
            pass

        self.data = []


if __name__ == "__main__":
    root = tk.Tk()
    app = Stereo(root)
    root.mainloop()
