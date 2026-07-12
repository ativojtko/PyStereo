import sys
import subprocess  # NOVÉ: Potrebné pre spustenie externého skriptu
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from plots.lineation import LineationSettings
from plots.plane import PlaneSettings
from plots.contour import ContourSettings
from plots.fisher import FisherSettings
from projection import StereonetProjection
from gui.dialogs import LineationSettingsDialog, PlaneSettingsDialog, ContourSettingsDialog, FisherSettingsDialog
from gui.panels import DataPanel, PlotPanel

__VERSION__ = "0.19.01 with Fisher modul"

class StereoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Stereo {__VERSION__}")
        self.root.geometry("1200x600+300+100")

        self.lineation_settings = LineationSettings()
        self.plane_settings = PlaneSettings()
        self.contour_settings = ContourSettings()
        self.fisher_settings = FisherSettings()

        self.data = []
        self.data_loaded = False
        self.current_file_path = None  # NOVÉ: Ukladáme celú cestu k súboru pre Fisher modul

        # Call method _create_menu() 
        self._create_menu()

        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)

        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=2)
        self.container.rowconfigure(0, weight=1)

        self.status_var = tk.StringVar()
        self.status_var.set(" No file loaded")

        # Status bar configuration
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor="w"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create data panel and plot panel
        self.data_panel = DataPanel(self.container, self)
        self.data_panel.grid(row=0, column=0, sticky="nsew")

        self.plot_panel = PlotPanel(self.container, self)
        self.plot_panel.grid(row=0, column=1, sticky="nsew")
        
    def _create_menu(self):
        """Creates the menu bar with File, Plot and Help menus, 
        and their respective options."""
        menubar = tk.Menu(self.root)

        # File menu with Open, Close and Exit options
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.load_file)
        file_menu.add_command(label="Close", command=self.close_data)
        file_menu.add_separator()
        # file_menu.add_command(label="Export Plot...", command=self.export_plot)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        # Plot menu with Lineations and Great circles options
        plot_menu = tk.Menu(menubar, tearoff=0)
        plot_menu.add_command(label="Lineations", command=self.plot_lineations)
        #plot_menu.add_command(label="Great circles", command=self.plot_great_circles)
        #plot_menu.add_command(label="Combined Plot", command=self.plot_combined)
        plot_menu.add_separator()
        #plot_menu.add_command(label="Contour Plot", command=self.plot_contours)
        plot_menu.add_command(label="Clear stereogram", command=self.plot_clear_stereogram)
        menubar.add_cascade(label="Plot", menu=plot_menu)

        # Settings menu with Lineation settings option
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Lineations", command=self.open_lineation_settings)
        settings_menu.add_command(label="Fisher", command=self.open_fisher_settings)
        # settings_menu.add_command(label="Planes", command=self.open_plane_settings)
        # settings_menu.add_command(label="Contours", command=self.open_contour_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # File menu with Statistics and options *****
        statistic_menu = tk.Menu(menubar, tearoff=0)
        statistic_menu.add_command(label="Fisher Analysis", command=self.fisher_computing) #self.load_file)
        statistic_menu.add_command(label="Mean Vector (R/n)", command=self.load_file)
        statistic_menu.add_separator()
        # file_menu.add_command(label="Export Plot...", command=self.export_plot)
        statistic_menu.add_separator()
        statistic_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="Statistics", menu=statistic_menu)


        # Configuration of the window to display this menu
        self.root.config(menu=menubar)


    def load_file(self):
        """Opens a file dialog to select a text file containing the 
        structural dataset. If a dataset is already loaded, prompts 
        the user to confirm replacing it with a new one.
        The selected file is read and parsed, and the data is stored 
        in the app's state. The data table is updated to reflect the 
        newly loaded dataset.
        """
        if self.data:
            answer = messagebox.askyesno(
                "Replace dataset",
                "A dataset is already loaded.\n\nReplace it with a new one?"
            )

            if not answer:
                return

        path = filedialog.askopenfilename(
            title="Select a text file containing data",
            filetypes=(("All files", "*.*"), \
                       ("Plain text file", "*.txt"), \
                       ("Tab separated values", "*.tsv"), \
                       ("Comma separated values", "*.csv"))
        )
        
        if not path:
            return

        # Uložíme si absolútnu cestu k súboru pre potreby štatistického modulu
        self.current_file_path = path

        # toto mi zobrazí načítané údaje
        data = self.read_data(path)
        self.set_data(data)

        filename = Path(path).name
        self.current_file = Path(path).name # toto treba doriesit
        self.status_var.set(f" {filename} | {len(data)} records loaded")

    def read_data(self, file_path):
        data = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split("\t")

                    if len(parts) < 5:
                        continue

                    try:
                        item = {
                            "id": int(parts[0]),
                            "type": parts[1],
                            "azimuth": float(parts[2]),
                            "dip": float(parts[3]),
                            "comment": parts[4]
                        }
                        data.append(item)

                    except ValueError:
                        continue
        
            #print(f"Data načítané z {file_path}: {data}")
            return data

        except Exception as e:
            messagebox.showerror("Error", f"Nepodarilo sa prečítať súbor:\n{e}")
        return []

    def set_data(self, data):
        self.data = data
        self.data_panel.refresh(data)
        self.data_loaded = True

    def dataset_selected(self, index):
        self.plot_panel.highlight(index)

    def close_data(self):
        if self.data:
            if not messagebox.askyesno("Close", "Close actual data?"):
                return
            
        self.data = []
        self.data_loaded = False
        self.current_file_path = None  # Vynulujeme cestu k súboru

        self.data_panel.refresh([])
        self.plot_panel.clear()
        self.status_var.set(" No file loaded")


# Plotting methods for lineations and great circles, and clearing the stereogram
    def plot_lineations(self):
        if not self.data:
            messagebox.showwarning("No data", "Load data first.")
            return
        
        self.plot_panel.redraw(self.data, mode="lineations")
        
    def plot_clear_stereogram(self):
        self.plot_panel.clear()


# *************************************

# *** GRAFICKÉ ZOBRAZENIE REPORTU S AUTOMATICKÝM UKLADANÍM A TLAČIDLOM NA OTVORENIE PRIEČINKA ***
    def fisher_computing(self):
        """
        Spustí statistics/Fisher_analysis_v01_05.py na pozadí,
        zachytí jeho textový výstup v UTF-8, zobrazí ho v novom okne aplikácie,
        AUTOMATICKY ho uloží do root/output/ a pridá tlačidlo na otvorenie tohto priečinka.
        """
        import subprocess
        from tkinter import scrolledtext

        koren_aplikacie = Path(__file__).resolve().parent
        cesta_k_skriptu = koren_aplikacie / "statistics" / "Fisher_analysis_v01_05.py"

        if not cesta_k_skriptu.exists():
            messagebox.showerror(
                "Chyba systému", 
                f"Štatistický modul nebol nájdený na očakávanej ceste:\n{cesta_k_skriptu}"
            )
            return

        prikaz = [sys.executable, cesta_k_skriptu.as_posix()]

        if self.data_loaded and getattr(self, 'current_file_path', None):
            cesta_dat = Path(self.current_file_path).resolve().as_posix()
            prikaz.append(cesta_dat)
        else:
            messagebox.showwarning(
                "Upozornenie", 
                "V hlavnom programe nie sú načítané žiadne dáta.\n\n"
                "Fisherov modul sa teraz pokúsi spustiť so svojím vlastným záložným súborom."
            )

        try:
            # Zachytenie výstupu v UTF-8
            proces = subprocess.run(
                prikaz, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                encoding='utf-8',
                errors='replace'
            )
            
            vysledny_text = proces.stdout
            if proces.stderr:
                vysledny_text += "\n\n!!! CHYBOVÉ SYSTÉMOVÉ HLÁSENIE MODULU !!!\n" + proces.stderr

            if not vysledny_text.strip():
                vysledny_text = "Modul nevrátil žiadny textový výstup. Skontrolujte kód Fisherovho skriptu."

            # --- AUTOMATICKÉ UKLADANIE DO ROOT/OUTPUT/NAZOV_Fisher.txt ---
            # OPRAVENÉ: Čisté a bezpečné vytiahnutie názvu súboru bez preklepov
            if getattr(self, 'current_file_path', None):
                povodny_nazov = Path(self.current_file_path).stem
            else:
                povodny_nazov = "fisher_report"

            priecinok_output = koren_aplikacie / "output"
            
            # Ak priečinok root/output neexistuje, vytvoríme ho
            if not priecinok_output.exists():
                priecinok_output.mkdir(parents=True, exist_ok=True)
                
            novy_nazov_suboru = f"{povodny_nazov}_Fisher.txt"
            cesta_automatickeho_reportu = priecinok_output / novy_nazov_suboru
            
            try:
                with open(cesta_automatickeho_reportu, "w", encoding="utf-8") as f:
                    f.write(vysledny_text)
                self.status_var.set(f" Report uložený do: output/{novy_nazov_suboru}")
            except Exception as auto_err:
                print(f"[VAROVANIE] Nepodarilo sa automaticky zapísať report na disk: {auto_err}")

            # 1. VYTVORENIE NOVÉHO OKNA V TKINTERI (800x650 px)
            okno_reportu = tk.Toplevel(self.root)
            okno_reportu.title("Výsledný Report Fisherovej Analýzy")
            okno_reportu.geometry("800x650")
            okno_reportu.transient(self.root)

            lbl = tk.Label(okno_reportu, text="Štatistické vyhodnotenie lineácií", font=("Arial", 11, "bold"), pady=5)
            lbl.pack()

            # ScrolledText pole s Courier New pre presné zarovnanie čiar
            text_area = scrolledtext.ScrolledText(
                okno_reportu, 
                wrap=tk.WORD, 
                font=("Courier New", 10), 
                bg="#1e1e1e", 
                fg="#ffffff"
            )
            text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            text_area.insert(tk.INSERT, vysledny_text)
            text_area.configure(state='disabled')

            # 2. VNÚTORNÁ FUNKCIA PRE OTVORENIE PRIEČINKA OUTPUT V PRIESKUMNÍKOVI
            def otvor_priecinok_output():
                import os
                try:
                    cesta_systemova = os.path.normpath(str(priecinok_output))
                    if os.path.exists(cesta_systemova):
                        os.startfile(cesta_systemova)
                    else:
                        messagebox.showerror("Chyba", "Priečinok s reportmi zatiaľ neexistuje.")
                except Exception as err:
                    messagebox.showerror("Chyba systému", f"Nepodarilo sa otvoriť priečinok:\n{err}")

            # 3. VNÚTORNÁ FUNKCIA PRE MANUÁLNE UKLADANIE TEXTU DO SÚBORU
            def ulozit_ako_txt():
                cesta_na_ulozenie = filedialog.asksaveasfilename(
                    title="Uložiť Fisherov report ako textový súbor",
                    initialfile=novy_nazov_suboru,
                    defaultextension=".txt",
                    filetypes=(("Textové súbory", "*.txt"), ("Všetky súbory", "*.*"))
                )
                
                if cesta_na_ulozenie:
                    try:
                        with open(cesta_na_ulozenie, "w", encoding="utf-8") as f:
                            f.write(vysledny_text)
                        messagebox.showinfo("Úspech", "Report bol úspešne uložený.")
                    except Exception as err:
                        messagebox.showerror("Chyba zápisu", f"Nepodarilo sa uložiť súbor:\n{err}")

            # 4. SPODNÝ PANEL PRE TLAČIDLÁ (Zoradené 3 vedľa seba)
            button_frame = tk.Frame(okno_reportu)
            button_frame.pack(pady=10)

            # Tlačidlo na okamžité otvorenie adresára s reportmi
            btn_open_folder = ttk.Button(button_frame, text="Otvoriť priečinok s reportmi", command=otvor_priecinok_output)
            btn_open_folder.pack(side=tk.LEFT, padx=10)

            # Tlačidlo na manuálne uloženie kópie
            btn_save = ttk.Button(button_frame, text="Uložiť kópiu ako...", command=ulozit_ako_txt)
            btn_save.pack(side=tk.LEFT, padx=10)

            # Tlačidlo na zatvorenie
            btn_close = ttk.Button(button_frame, text="Zatvoriť report", command=okno_reportu.destroy)
            btn_close.pack(side=tk.LEFT, padx=10)

        except Exception as e:
            messagebox.showerror(
                "Chyba spracovania", 
                f"Nepodarilo sa zachytiť textový výstup Fisher analýzy:\n{e}"
            )
   
# *************************************

# Settings dialog methods
    def open_lineation_settings(self):
        LineationSettingsDialog(self.root, self)

    def open_fisher_settings(self):
        FisherSettingsDialog(self.root, self)
##
##    def open_plane_settings(self):
##        PlaneSettingsDialog(self.root, self)
##
##    def open_contour_settings(self):
##        ContourSettingsDialog(self.root, self)

# Spustenie aplikácie (ak spúšťate tento súbor priamo)
if __name__ == "__main__":
    root = tk.Tk()
    app = StereoApp(root)
    root.mainloop()
    
