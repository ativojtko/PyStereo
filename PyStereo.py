import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from plots.lineation import LineationSettings
from plots.pole import PoleSettings
from plots.plane import PlaneSettings
from plots.contour import ContourSettings
from projection import StereonetProjection
from gui.dialogs import LineationSettingsDialog, PlaneSettingsDialog, ContourSettingsDialog, RotationDialog
from gui.panels import DataPanel, PlotPanel
from file_io import write_data, read_data, write_plot
import calculations

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


__VERSION__ = "0.23.1"
__AUTHOR__ = ("Hana Balažovjechová", \
              "Rastislav Vojtko", \
              "Miroslav Zverka", \
              "Marcel Vasiľák", \
              "Zuzana Lahová")

__LOCATION__ = "https://github.com/ativojtko/PyStereo"

__DATE__ = '2026-11-08'

__LICENSE__ = """MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__ADDRESS__ = """\nDepartment of Geology and Palaeontology
Faculty of Natural Sciences
Comenius University in Bratislava
Mlynská dolina, Ilkovičova 6
SK-842 15 Bratislava
Slovakia"""

__EMAIL__ = """
e-mails:
hana.balazovjechova@gmail.com
rastislav.vojtko@gmail.com
"""

class PyStereoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"PyStereo {__VERSION__}")
        self.root.geometry("1000x600+100+100")

        # Nastavenie ikony aplikáce (Windows vs. ostatné platformy)
        if sys.platform.startswith("win"):
            try:
                self.root.iconbitmap(str(ASSETS_DIR / "stereo.ico"))
            except Exception:
                pass
        else:
            try:
                self.icon = tk.PhotoImage(file=str(ASSETS_DIR / "stereo.png"))
                self.root.iconphoto(True, self.icon)
            except Exception:
                pass
        
        self.lineation_settings = LineationSettings()
        self.pole_settings = PoleSettings()
        self.plane_settings = PlaneSettings()
        self.contour_settings = ContourSettings()

        self.data = []
        self.data_loaded = False

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

        # File menu with Open, Close, Export Plot and Exit options
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self.load_file)
        file_menu.add_command(label="Close", accelerator="Ctrl+W", command=self.close_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export Plot...", accelerator="Ctrl+E", command=self.export_plot)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        # Plot menu
        plot_menu = tk.Menu(menubar, tearoff=0)
        plot_menu.add_command(label="Lineations", command=lambda: self.plot_data("lineations"))
        plot_menu.add_command(label="Poles", command=lambda: self.plot_data("poles"))
        plot_menu.add_command(label="Great circles", command=lambda: self.plot_data("planes"))
        plot_menu.add_command(label="Combined Plot",command=lambda: self.plot_data("all"))
        plot_menu.add_separator()

        # Podmenu pre kontúrové diagramy
        contour_menu = tk.Menu(plot_menu, tearoff=0)
        plot_menu.add_cascade( label="Contour Plot", menu=contour_menu)  
        contour_menu.add_command(label="Lineations", command=lambda: self.plot_data("contour_lineations"))
        contour_menu.add_command(label="Poles", command=lambda: self.plot_data("contour_poles"))
            
        plot_menu.add_command(label="Clear stereogram", command=self.plot_clear_stereogram)
        menubar.add_cascade(label="Plot", menu=plot_menu)

        # Calculations
        calculations_menu = tk.Menu(menubar, tearoff=0)
        calculations_menu.add_command(label="Planes to poles", command=self.planes_to_poles)
        calculations_menu.add_command(label="Poles to planes", command=self.poles_to_planes)
        calculations_menu.add_separator()
        calculations_menu.add_command(label="Rotate Elements", command=self.rotation)
        menubar.add_cascade(label="Calculations", menu=calculations_menu)

        # Statistics
        #statistics_menu = tk.Menu(menubar, tearoff=0)
        #statistics_menu.add_command(label="Mean vector", command=lambda: messagebox.showinfo("Mean vector", "This feature is not yet implemented."))
        #statistics_menu.add_command(label="Fisher Distribution", command=lambda: messagebox.showinfo("Fisher Distribution", "This feature is not yet implemented."))
        #statistics_menu.add_command(label="Bingham Distribution", command=lambda: messagebox.showinfo("Bingham Distribution", "This feature is not yet implemented."))
        #menubar.add_cascade(label="Statistics", menu=statistics_menu)

        # Settings menu with Lineation settings option
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Lineations", command=self.open_lineation_settings)
        settings_menu.add_command(label="Poles",command=self.open_pole_settings)
        settings_menu.add_command(label="Planes", command=self.open_plane_settings)
        settings_menu.add_command(label="Contours", command=self.open_contour_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Help menu with About option
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="License", command=lambda: messagebox.showinfo(
                                          "License",
                                            __LICENSE__
                              ))
        help_menu.add_command(label="About...",
                                      command=lambda: messagebox.showinfo(
                                          "About PyStereo...",
                                          "PyStereo " + __VERSION__ + "\n" + __LOCATION__ + "\nBuild: " 
                                          + __DATE__ + "\n\n" + "\n".join(__AUTHOR__) + "\n\n" 
                                          + __ADDRESS__ + "\n\n" + __EMAIL__
                                      ))
        menubar.add_cascade(label="Help", menu=help_menu)

        # Configuration of the window to display this menu
        self.root.config(menu=menubar)

        # Bindings
        # Bindings for File menubar items
        self.root.bind("<Control-o>", lambda event: self.load_file())
        self.root.bind("<Control-O>", lambda event: self.load_file())
        self.root.bind("<Control-w>", lambda event: self.close_data())
        self.root.bind("<Control-W>", lambda event: self.close_data())
        self.root.bind("<Control-e>", lambda event: self.export_plot())
        self.root.bind("<Control-E>", lambda event: self.export_plot())
        self.root.bind("<Control-q>", lambda event: self.root.destroy())
        self.root.bind("<Control-Q>", lambda event: self.root.destroy())
    
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
                "Replace the current dataset",
                "The dataset is already loaded.\n\nReplace it with a new one?"
            )

            if not answer:
                return

        path = filedialog.askopenfilename(
            title="Select a text file containing data",
            filetypes=(("Comma separated values", "*.csv"), \
                       ("Tab separated values", "*.tsv"), \
                       ("Plain text file", "*.txt"), \
                       ("All files", "*.*"))
        )

        if not path:
            return
        # zmena, tu zavoláme nový modul file_io ktorý nahradi starnú metodu self.read_data(path)
        # pribudol nový zoznam invalid rows ktorý uchova informáciu o chybných riadkoch
        # prečistí starý graf
        try:
            data, invalid_rows = read_data(path)
        except Exception as error:
            messagebox.showerror("Error", f"Unable to read the file:\n{error}")
            return

        self.invalid_rows = invalid_rows
        self.set_data(data)
        self.plot_panel.clear()
        self.current_file = Path(path).name
        self.status_var.set(
            f" {self.current_file} | {len(data)} records loaded"
            f" | {len(invalid_rows)} invalid rows skipped"
        )

    # overíme si či meranie obsahuje požadované dáta 
    def require_data(self, measurement_type=None):
        if not self.data:
            messagebox.showwarning(
                "No data loaded",
                "Please load a dataset first."
            )
            return False

        if measurement_type is not None:
            if not any(item["type"] == measurement_type for item in self.data):
                messagebox.showwarning(
                    "No measurements found",
                    f"The dataset contains no measurements of type {measurement_type}."
                )
                return False

        return True
    
    def set_data(self, data):
        self.data = data
        self.data_panel.refresh(data)
        self.data_loaded = bool(data) # zmena, nová funkcia read_data moze vratit aj prázdny zoznam data pri všetkých chybných riadkoch

    def dataset_selected(self, index):
        self.plot_panel.highlight(index)

    def close_data(self):
        if self.data:
            if not messagebox.askyesno("Close dataset", "Close the current dataset?"):
                return
            
        self.data = []
        self.data_loaded = False

        self.data_panel.refresh([])
        self.plot_panel.clear()
        self.status_var.set("No file loaded")

    def save_file(self, file_path, writer, *args):
        try:
            writer(file_path, *args)
        except Exception as error:
            messagebox.showerror("Export error", str(error))
            return False

        messagebox.showinfo(
            "Export",
            f"File saved successfully:\n\n{file_path}"
        )
        return True

    def export_plot(self):
        if self.plot_panel.current_mode is None:
            messagebox.showwarning(
                "No plot exported",
                "Create a stereogram first."
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("EPS files", "*.eps"),
                ("All files", "*.*")
            ],
            title="Export stereogram"
        )

        if not file_path:
            return

        caption = (
            f"PyStereo {__VERSION__}\n"
            f"{self.current_file}\n"
            f"n = {len(self.data)}\n"
        )
        return self.save_file(file_path, write_plot, self.plot_panel.fig, caption)

    # Vyberie súbor a uloží pripravené merania so zvolenou presnosťou.
    def export_data(self, data, name, decimal_places=2):
        file_path = filedialog.asksaveasfilename(
            title=f"Save {name}",
            initialfile=f"{Path(self.current_file).stem}-{name}.tsv",
            defaultextension=".tsv",
            filetypes=[
                ("Tab-separated files", "*.tsv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return False

        return self.save_file(
            file_path, write_data, data, decimal_places
        )
    
    def confirm_data_change(self, action):
        if not self.data:
            return True

        return messagebox.askyesno(
            f"{action} dataset",
            f"{action} the current dataset?"
        )
# Plotting methods for lineations and great circles, and clearing the stereogram

# spojila som všetky funkcie plot do jednej, vždy sa urči podla mode co sa má zobrazit
    def plot_data(self, mode="all"):
        if self.require_data():
            self.plot_panel.redraw(self.data, mode=mode)

    def plot_clear_stereogram(self):
        self.plot_panel.clear()



# Calculations dialog methods

    # Prevedie plochy na póly a odovzdá výsledok na uloženie.
    def planes_to_poles(self):
        if not self.require_data("S"):
            return

        data = calculations.convert_planes_to_poles(self.data)
        return self.export_data(data, "poles")

    # Prevedie póly na plochy a odovzdá výsledok na uloženie.
    def poles_to_planes(self):
        if not self.require_data("P"):
            return

        data = calculations.convert_poles_to_planes(self.data)
        return self.export_data(data, "planes")

    # Bez hodnôt otvorí dialóg, so zadanými hodnotami otočí merania a exportuje ich.
    def rotation(self, angle=None, axis=None, decimal_places=2):
        if not self.require_data():
            return False

        if angle is None:
            RotationDialog(self.root, self)
            return False

        data = calculations.rotate_dataset(self.data, angle, axis)
        return self.export_data(data, "rotated", decimal_places)

# Statistics dialog methods
    def fisher_distribution(self):
        pass


# Settings dialog methods
    def open_lineation_settings(self):
        LineationSettingsDialog(self.root, self)

    def open_plane_settings(self):
        PlaneSettingsDialog(self.root, self)

    def open_pole_settings(self):
        LineationSettingsDialog(self.root,self,settings=self.pole_settings,title="Pole Settings")

    def open_contour_settings(self):
        ContourSettingsDialog(self.root, self)


if __name__ == "__main__":
    root = tk.Tk()
    app = PyStereoApp(root)
    root.mainloop()
