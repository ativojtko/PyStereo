import tkinter as tk
from tkinter import ttk, messagebox, filedialog

AUTHORS = "Hanka Balažovjechová, Rastislav Vojtko"

VERSION = "0.7"

class Stereo:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Stereo {VERSION}")
        self.root.iconbitmap("stereo.ico")
        self.root.geometry("1000x600+200+200")

        self.data = []

        # 1. Najskôr vytvoríme Menu
        self._create_menu()
        # 2. Potom zvyšok GUI
        self._init_gui()

    def _create_menu(self):
        """Vytvorí hornú lištu s ponukami."""
        menubar = tk.Menu(self.root)
        
        # Vytvorenie položky File a jej podmenu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open dataset...", command=self.open_read)  # Pridá funkciu na načítanie súboru

        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.file_quit)  # Ukončí aplikáciu
        
        # Pridanie položky "Súbor" do hlavnej lišty
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Pridanie položky "Pomoc" (voliteľné)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About...", 
                              command=lambda: messagebox.showinfo("About...", "Stereo " + VERSION + "\n\n2026\n\nAutori: " + AUTHORS))
        menubar.add_cascade(label="Help", menu=help_menu)

        # Konfigurácia okna, aby zobrazilo toto menu
        self.root.config(menu=menubar)


    def _init_gui(self):
        """Rozdelenie okna na ľavý a pravý panel."""
        
        # 1. HLAVNÝ KONTAJNER (aby sme mohli mať okraje)
        main_container = tk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        # 2. ĽAVÝ PANEL (Tabuľka)
        # Nastavíme mu fixnú šírku alebo mu dovolíme rásť
        self.left_panel = tk.Frame(main_container, width=350)
        self.left_panel.pack(side=tk.LEFT, fill='both', expand=True)

        # 3. PRAVÝ PANEL (Budúci Stereonet)
        # background='lightgrey' nám ho dočasne zviditeľní
        self.right_panel = tk.Frame(main_container, width=500, bg='#e0e0e0', relief=tk.SUNKEN, bd=1)
        self.right_panel.pack(side=tk.RIGHT, fill='both', expand=True, padx=(5, 0))

        # Dočasný text do pravého panela
        lbl = tk.Label(self.right_panel, text="Miesto pre Stereonet", bg="#e0e0e0", fg='red')
        lbl.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # --- Výplň ľavého panela (tvoja existujúca tabuľka) ---
        self._vytvor_tabulku(self.left_panel)

    
    def _vytvor_tabulku(self, parent):
        """Vloží Treeview do určeného rodičovského prvku."""
        columns = ('dataset', 'dipdir', 'dip', 'comments')
        
        # Frame pre Treeview a Scrollbar v rámci ľavého panela
        table_container = tk.Frame(parent)
        table_container.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(table_container, columns=columns, show='headings')
        
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Nastavenie stĺpcov
        self.tree.heading('dataset', text='Dataset')
        self.tree.heading('dipdir', text='DipDir')
        self.tree.heading('dip', text='Dip')
        self.tree.heading('comments', text='Comments')

        self.tree.column('dataset', width=50, minwidth=50, stretch=tk.NO, anchor='center')
        self.tree.column('dipdir', width=50, minwidth=50, stretch=tk.NO, anchor='center')
        self.tree.column('dip', width=50, minwidth=50, stretch=tk.NO, anchor='center')
        self.tree.column('comments', width=150, minwidth=100, stretch=tk.YES, anchor='w')

        self.tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    

    def open_read(self):
        """Otvorí dialógové okno na výber súboru a následne ho načíta."""
        fn_path = filedialog.askopenfilename(
            title="Vyberte textový súbor s dátami",
            filetypes=(("Normal text file", "*.txt"), \
                       ("Comma separated values", "*.csv"), \
                       ("All files", "*.*"))
        )
        
        if fn_path: # Ak používateľ nezrušil výber
            print(f"Vybraný súbor: {fn_path}")
            uploaded_data = self.read_data(fn_path)
            if uploaded_data is not None:
                print(f"Načítané dáta - UPLOADED: {uploaded_data}")
                self.data = uploaded_data
                print(f"Data uložené v self.data: {self.data}")
                self.obnov_tabulku()


    def read_data(self, file_path):
        """Načítá data ze zvoleného souboru a vrátí je jako seznam."""
        vysledok = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for riadok in f:
                    riadok_data = riadok.strip().split("\t")
                    vysledok.append(riadok_data)

            print(f"Data načítané z {file_path}: {vysledok}")
            return vysledok
        except Exception as e:
            messagebox.showerror("Chyba", f"Nepodarilo sa prečítať súbor:\n{e}")
            return None

    def obnov_tabulku(self):
        """Prekreslenie Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for riadok in self.data:
            self.tree.insert('', tk.END, values=riadok)

    def file_quit(self, event=None):
        a = messagebox.askquestion("Question", "Are you sure to quit?")
        if a == 'yes':
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = Stereo(root)
    root.mainloop()