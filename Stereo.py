import tkinter as tk
from tkinter import ttk, messagebox, filedialog

AUTHORS = "Hana Balažovjechová, Rastislav Vojtko"
VERSION = "0.6.0"

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
        self._init_gui()

    def _create_menu(self):
        """Vytvorí hornú lištu s ponukami."""
        menubar = tk.Menu(self.root)
        
        # Vytvorenie položky File a jej podmenu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open dataset...", command=self.open_read) 

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

        # Configuration of window to draw this menu
        self.root.config(menu=menubar)

    def _init_gui(self):
        """Vytvorenie tabuľky a zvyšku rozhrania."""
        table_frame = tk.Frame(self.root)
        table_frame.pack(side=tk.TOP, fill='both', expand=True, padx=10, pady=10)

        columns = ('dataset', 'dipdir', 'dip', 'comments')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Nastavenie stĺpcov
        self.tree.heading('dataset', text='Dataset')
        self.tree.heading('dipdir', text='DipDir')
        self.tree.heading('dip', text='Dip')
        self.tree.heading('comments', text='Comments', anchor='w')

        self.tree.column('dataset', width=80, minwidth=50, stretch=tk.NO, anchor='center')
        self.tree.column('dipdir', width=80, minwidth=50, stretch=tk.NO, anchor='center')
        self.tree.column('dip', width=80, minwidth=50, stretch=tk.NO, anchor='center')
        self.tree.column('comments', width=300, minwidth=100, stretch=tk.YES, anchor='w')

        self.tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def obnov_tabulku(self):
        """Prekreslenie Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for riadok in self.data:
            self.tree.insert('', tk.END, values=riadok)
            
    def open_read(self):
        """Otvorí dialógové okno na výber súboru a následne ho načíta."""
        fn_path = filedialog.askopenfilename(
            title="Vyberte textový súbor s dátami",
            filetypes=(("Textové súbory", "*.txt"), ("Comma separated values", "*.csv"), ("Všetky súbory", "*.*"))
        )
        
        if fn_path: # Ak používateľ nezrušil výber
            print(f"Vybraný súbor: {fn_path}")
            uploaded_data = self.read_data(fn_path)
            if uploaded_data is not None:
                self.data = uploaded_data
                print(f"Načítané dáta: {self.data}")
                #self.obnov_tabulku()

    def read_data(self, file_path):
        """Načítá data ze zvoleného souboru a vrátí je jako seznam."""
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                data = []
                for line in lines:
                    line = line.strip()
                    if line:  # Ignoruje prázdné řádky
                        parts = line.split()
                        if len(parts) == 2:  # Očekáváme 2 hodnoty (trend a plunge)
                            try:
                                trend = float(parts[0])
                                plunge = float(parts[1])
                                data.append((trend, plunge))
                            except ValueError:
                                print(f"Neplatný formát čísla v řádku: {line}")
                        else:
                            print(f"Neplatný formát řádku (očekávány 2 hodnoty): {line}")
                return data
        except Exception as e:
            messagebox.showerror("Chyba", f"Nepodařilo se načíst soubor: {e}")
            return None


    def file_quit(self, event=None):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = Stereo(root)
    root.mainloop()
