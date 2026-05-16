import tkinter as tk
from tkinter import ttk, messagebox, filedialog

AUTHORS = "Hana Balažovjechová, Rastislav Vojtko"
VERSION = "0.2.0"

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

        self._create_menu()

    def _create_menu(self):
        """Vytvorí hornú lištu s ponukami."""
        menubar = tk.Menu(self.root)
        
        # Vytvorenie položky File a jej podmenu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open dataset...") 

        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.file_quit)  # Ukončí aplikáciu
        
        # Pridanie položky "File" do hlavnej lišty
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Pridanie položky "Help" (voliteľné)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About...", 
                              command=lambda: messagebox.showinfo("About...", "Stereo " + \
                                                    VERSION + "\n\n2026\n\nAuthors: " + AUTHORS))
        menubar.add_cascade(label="Help", menu=help_menu)

        # Konfigurácia okna, aby zobrazilo toto menu
        self.root.config(menu=menubar)

    def file_quit(self, event=None):
        #a = messagebox.askquestion("Question", "Are you sure to quit?")
        #if a == 'yes':
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = Stereo(root)
    root.mainloop()
