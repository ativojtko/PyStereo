import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from plots.lineation import LineationSettings
from plots.plane import PlaneSettings
from plots.contour import ContourSettings
from projection import StereonetProjection
from gui.dialogs import LineationSettingsDialog, PlaneSettingsDialog, ContourSettingsDialog
from gui.panels import DataPanel, PlotPanel


__VERSION__ = "0.20.0"
__AUTHOR__ = ("Rastislav Vojtko", \
              "Hana Balažovjechová", \
              "Miroslav Zverka", \
              "Marcel Vasiľák", \
              "Zuzana Lahová")
__DATE__ = '2026-07-11'

__LICENSE__ = """GNU General Public License v. 3\n
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

For more information see <http://www.gnu.org/licenses/>."""

__ADDRESS__ = """\nDepartment of Geology and Palaeontology
Faculty of Natural Sciences
Comenius University in Bratislava
Mlynská dolina, Ilkovičova 6
SK-842 15 Bratislava
Slovakia"""

__EMAIL__ = 'e-mail: rastislav.vojtko@gmail.com'


class StereoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Stereo {__VERSION__}")
        self.root.geometry("1000x600+100+100")

        # Nastavenie ikony aplikáce (Windows vs. ostatné platformy)
        if sys.platform.startswith("win"):
            try:
                self.root.iconbitmap("stereo.ico")
            except Exception:
                pass
        else:
            try:
                self.icon = tk.PhotoImage(file="stereo.png")
                self.root.iconphoto(True, self.icon)
            except Exception:
                pass
        
        self.lineation_settings = LineationSettings()
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

        # File menu with Open, Close and Exit options
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.load_file)
        file_menu.add_command(label="Close", command=self.close_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export Plot...", command=self.export_plot)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        # Plot menu with Lineations and Great circles options
        plot_menu = tk.Menu(menubar, tearoff=0)
        plot_menu.add_command(label="Lineations", command=self.plot_lineations)
        plot_menu.add_command(label="Great circles", command=self.plot_great_circles)
        plot_menu.add_command(label="Combined Plot", command=self.plot_combined)
        plot_menu.add_separator()
        plot_menu.add_command(label="Contour Plot", command=self.plot_contours)
        plot_menu.add_command(label="Clear stereogram", command=self.plot_clear_stereogram)
        menubar.add_cascade(label="Plot", menu=plot_menu)

        # Statistics
        statistics_menu = tk.Menu(menubar, tearoff=0)
        statistics_menu.add_command(label="Fisher Distribution", command=self.fisher_distribution)
        menubar.add_cascade(label="Statistics", menu=statistics_menu)

        # Settings menu with Lineation settings option
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Lineations", command=self.open_lineation_settings)
        settings_menu.add_command(label="Planes", command=self.open_plane_settings)
        settings_menu.add_command(label="Contours", command=self.open_contour_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Help menu with About option
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About...",
                              command=lambda: messagebox.showinfo(
                                  "About Stereo...",
                                  "Stereo " + __VERSION__ + "\nBuild: " + __DATE__ + "\n\n"
                                  + "\n".join(__AUTHOR__) + "\n\n"  
                                  + __LICENSE__ + "\n" + __ADDRESS__ + "\n\n"
                                  + __EMAIL__
                              ))
        menubar.add_cascade(label="Help", menu=help_menu)

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
                "Replace the current dataset",
                "The dataset is already loaded.\n\nReplace it with a new one?"
            )

            if not answer:
                return

        path = filedialog.askopenfilename(
            title="Select a text file containing data",
            filetypes=(("Plain text file", "*.txt"), \
                       ("Tab separated values", "*.tsv"), \
                       ("Comma separated values", "*.csv"), \
                       ("All files", "*.*"))
        )

        if not path:
            return
        
        data = self.read_data(path)
        self.set_data(data)

        filename = Path(path).name
        self.current_file = Path(path).name # toto treba doriesit
        self.status_var.set(f" {filename} | {len(data)} records loaded")


    def read_data(self, file_path):
        """Reads a text file containing structural data and returns a list 
        of dictionaries representing the data.
        Each line in the file should contain the following tab-separated values:"""
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
        
            print(f"Loaded {len(data)} records from {file_path}")
            return data

        except Exception as e:
            messagebox.showerror("Error", f"Unable to read the file:\n{e}")
        return []

    def set_data(self, data):
        self.data = data
        self.data_panel.refresh(data)
        self.data_loaded = True

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

    def export_plot(self):
        if not self.plot_panel.has_plots:
            messagebox.showwarning("No plot exported",
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

        try:
            self.plot_panel.canvas.draw()

            metadata = self.plot_panel.fig.text(
                0.98, 0.02,
                f"Stereo {__VERSION__}\n"
                f"{self.current_file}\n"
                f"n = {len(self.data)}\n",
                ha="right",
                va="bottom",
                fontsize=8,
                color="gray"
            )   

            self.plot_panel.fig.savefig(
                file_path,
                dpi=300,
                bbox_inches="tight",
                facecolor="white"
            )

            metadata.remove()

            messagebox.showinfo(
                "Export",
                f"Stereogram exported successfully:\n{file_path}"
            )

        except Exception as e:
            messagebox.showerror(
                "Export error",
                str(e)
            )

# Plotting methods for lineations and great circles, and clearing the stereogram
    def plot_lineations(self):
        if not self.data:
            messagebox.showwarning("No data loaded", "Please load a dataset first.")
            return
        
        self.plot_panel.redraw(self.data, mode="lineations")

    def plot_great_circles(self):
        if not self.data:
            messagebox.showwarning("No data loaded", "Please load a dataset first.")
            return
        
        self.plot_panel.redraw(self.data, mode="planes")

    def plot_combined(self):
        if not self.data:
            messagebox.showwarning("No data loaded", "Please load a dataset first.")
            return

        self.plot_panel.redraw(self.data, mode="all")

    def plot_clear_stereogram(self):
        self.plot_panel.clear()

    def plot_contours(self):
        if not self.data:
            messagebox.showwarning("No data loaded", "Please load a dataset first.")
            return

        self.plot_panel.redraw(self.data, mode="contours")


# Statistics dialog methods
    def fisher_distribution(self):
        pass


# Settings dialog methods
    def open_lineation_settings(self):
        LineationSettingsDialog(self.root, self)

    def open_plane_settings(self):
        PlaneSettingsDialog(self.root, self)

    def open_contour_settings(self):
        ContourSettingsDialog(self.root, self)


if __name__ == "__main__":
    root = tk.Tk()
    app = StereoApp(root)
    root.mainloop()
    
# End of stereo.py: (c) 2026 R. Vojtko, H. Balažovjechová, Z. Lahová
