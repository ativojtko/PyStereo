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


__VERSION__ = "0.21.0"
__AUTHOR__ = ("Hana Balažovjechová", \
              "Rastislav Vojtko", \
              "Miroslav Zverka", \
              "Marcel Vasiľák", \
              "Zuzana Lahová")

__LOCATION__ = "https://github.com/ativojtko/PyStereo"

__DATE__ = '2026-10-14'

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


class StereoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"PyStereo {__VERSION__}")
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

        # Calculations
        calculations_menu = tk.Menu(menubar, tearoff=0)
        calculations_menu.add_command(label="Planes to poles", command=self.planes_to_poles)
        calculations_menu.add_command(label="Poles to planes", command=lambda: messagebox.showinfo("Poles to planes", "This feature is not yet implemented."))
        calculations_menu.add_separator()
        calculations_menu.add_command(label="Rotation...", command=lambda: messagebox.showinfo("Rotation around an arbitrary axis", "This feature is not yet implemented."))
        menubar.add_cascade(label="Calculations", menu=calculations_menu)

        # Statistics
        statistics_menu = tk.Menu(menubar, tearoff=0)
        statistics_menu.add_command(label="Mean vector", command=lambda: messagebox.showinfo("Mean vector", "This feature is not yet implemented."))
        statistics_menu.add_command(label="Fisher Distribution", command=lambda: messagebox.showinfo("Fisher Distribution", "This feature is not yet implemented."))
        statistics_menu.add_command(label="Bingham Distribution", command=lambda: messagebox.showinfo("Bingham Distribution", "This feature is not yet implemented."))  # Disable the option for now
        menubar.add_cascade(label="Statistics", menu=statistics_menu)

        # Settings menu with Lineation settings option
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Lineations", command=self.open_lineation_settings)
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
                    line = line.rstrip("\r\n")
                    if not line:
                        continue

                    parts = line.split("\t")


                    if len(parts) < 4:
                        continue

                    comment = parts[4] if len(parts) > 4 else ""

                    try:
                        item = {
                            "id": int(parts[0]),
                            "type": parts[1],
                            "azimuth": float(parts[2]),
                            "inclination": float(parts[3]),
                            "comment": comment
                        }
                        data.append(item)

                    except ValueError:
                        print(f"Skipping invalid line: {line}")
                        print(e)
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
                f"PyStereo {__VERSION__}\n"
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
                f"Stereogram exported successfully:\n\n{file_path}"
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


# Calculations methods
    def planes_to_poles(self):
        """Convert planes (S) to poles (L) and save them to a new file."""

        # If no self.data then message box warning
        if not self.data:
            messagebox.showwarning(
                "No data loaded",
                "Please load a dataset first."
            )
            return

        # Check whether the dataset contains any planes.
        plane_count = sum(
            item["type"] == "S" for item in self.data
        )

        if plane_count == 0:
            messagebox.showwarning(
                "No planes found",
                "The loaded dataset contains no planes to convert."
            )
            return

        # Create a new dataset without modifying the original data.
        converted_data = []

        for item in self.data:
            converted_item = item.copy()

            if item["type"] == "S":
                dipdir = float(item["azimuth"])
                dip = float(item["inclination"])

                converted_item["type"] = "L"
                converted_item["azimuth"] = (dipdir + 180.0) % 360.0
                converted_item["inclination"] = 90.0 - dip

            converted_data.append(converted_item)
        

        # Ask the user where to save the converted dataset.
        file_path = filedialog.asksaveasfilename(
            title="Save converted poles",
            initialfile=f"{Path(self.current_file).stem}-poles.tsv",
            defaultextension=".tsv",
            filetypes=[
                ("Tab-separated files", "*.tsv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                for item in converted_data:
                    file.write(
                        f'{item["id"]}\t'
                        f'{item["type"]}\t'
                        f'{item["azimuth"]:.1f}\t'
                        f'{item["inclination"]:.1f}\t'
                        f'{item["comment"]}\n'
                    )

            messagebox.showinfo(
                "Conversion complete",
                f"Converted {plane_count} planes to poles.\n\n"
                f"Output file:\n{file_path}"
            )

        except OSError as e:
            messagebox.showerror(
                "Save error",
                f"Unable to save the converted data:\n{e}"
            )


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
