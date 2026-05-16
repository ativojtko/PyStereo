import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplstereonet
from projection import StereonetProjection

VERSION = "0.13.0"
AUTHOR = ("Hanka Balažovjechová", \
          "Rastislav Vojtko", \
            "Zuzana Lahová")

class StereoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Stereo {VERSION}")
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

        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor="w"
        )

        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.data_panel = DataPanel(self.container, self)
        self.data_panel.grid(row=0, column=0, sticky="nsew")

        self.plot_panel = PlotPanel(self.container, self)
        self.plot_panel.grid(row=0, column=1, sticky="nsew")


    def _create_menu(self):
        menubar = tk.Menu(self.root)

        # File menu with Open, Close and Exit options
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.load_file)
        file_menu.add_command(label="Close", command=self.close_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export Plot...",
                                command=self.export_plot
                                )
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        # Plot menu with Lineations and Great circles options
        plot_menu = tk.Menu(menubar, tearoff=0)
        plot_menu.add_command(label="Lineations",
                              command=self.plot_lineations
                        )
        plot_menu.add_command(label="Great circles",
                              command=self.plot_great_circles
                        )
        plot_menu.add_separator()
        plot_menu.add_command(label="Clear stereogram",
                              command=self.plot_clear_stereogram
                        )
        menubar.add_cascade(label="Plot", menu=plot_menu)

        # Help menu with About option
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About...", 
                              command=lambda: messagebox.showinfo("About...", "Stereo " + VERSION + "\n\n2026\n\nAutori:\n" + "\n".join(AUTHOR)))
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
                "Replace dataset",
                "A dataset is already loaded.\n\nReplace it with a new one?"
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
        
            print(f"Data načítané z {file_path}: {data}")

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

        self.data_panel.refresh([])
        self.plot_panel.clear()
        self.status_var.set(" No file loaded")


    def export_plot(self):
        if not self.plot_panel.has_plots:
            messagebox.showwarning("No plot",
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
                f"Stereo {VERSION}\n"
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
            messagebox.showwarning("No data", "Load data first.")
            return
        
        self.plot_panel.redraw(self.data, mode="lineations")

    def plot_great_circles(self):
        if not self.data:
            messagebox.showwarning("No data", "Load data first.")
            return
        
        self.plot_panel.redraw(self.data, mode="surfaces")

    def plot_clear_stereogram(self):
        self.plot_panel.clear()


class DataPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        columns = ("id", "type", "azimuth", "dip", "comment")

        # Kontajner pre tabuľku a scrollbary
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True)

        # Grid konfigurácia
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        # Scrollbary
        self.scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )

        self.xscrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=self.tree.xview
        )

        # Prepojenie scrollov
        self.tree.configure(
            yscrollcommand=self.scrollbar.set,
            xscrollcommand=self.xscrollbar.set
        )

        # Hlavičky
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Type")
        self.tree.heading("azimuth", text="Azimuth")
        self.tree.heading("dip", text="Dip")
        self.tree.heading("comment", text="Comment", anchor="w")

        # Stĺpce
        self.tree.column("id", width=40, minwidth=40, stretch=tk.NO, anchor="center")
        self.tree.column("type", width=60, minwidth=60, stretch=tk.NO, anchor="center")
        self.tree.column("azimuth", width=70, minwidth=60, stretch=tk.NO, anchor="e")
        self.tree.column("dip", width=70, minwidth=60, stretch=tk.NO, anchor="e")
        self.tree.column("comment", width=125, minwidth=100, stretch=tk.YES, anchor="w")

        # Rozloženie cez grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.xscrollbar.grid(row=1, column=0, sticky="ew")


    def refresh(self, data):
        """
        Updates the data table with the currently loaded structural dataset.

        Existing rows are cleared before inserting new data to keep
        the table synchronised with StereoApp.data.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in data:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["type"],
                    row["azimuth"],
                    row["dip"],
                    row["comment"]
                )
            )


class PlotPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app
        
        self.fig = plt.Figure(figsize=(5,5))
        self.ax = self.fig.add_subplot(111, projection="stereonet")
        self.ax.grid(False)
        self.ax.text(0.5, 0.5, "+",
                    transform=self.ax.transAxes,
                    ha="center",
                    va="center",
                    fontsize=14
                    )

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.projection = None
        self.canvas.draw()


    def redraw(self, data, mode="all"):
        if self.projection is None:
            self.projection = StereonetProjection(self.ax, self.canvas, data)
        else:
            self.projection.data = data
            self.projection.plots.clear()

        self.ax.cla()

        self.projection.ax = self.ax
        self.projection.draw(mode=mode)

        self.ax.grid(False)
        self._setup_axes()

        self.has_plots = True
        self.canvas.draw_idle()

    
    def clear(self):
        self.ax.cla()
        self.ax.grid(False)
        self._setup_axes()

        self.has_plots = False 
        self.canvas.draw_idle()
        

    def _setup_axes(self):
        self.ax.grid(False)
        self.ax.text(
            0.5, 0.5, "+",
            transform=self.ax.transAxes,
            ha="center",
            va="center",
            fontsize=14
        )

    def highlight(self, index):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = StereoApp(root)
    root.mainloop()
    