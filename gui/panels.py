import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from projection import StereonetProjection


class DataPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        columns = ("id", "type", "azimuth", "inclination", "comment")

        # Kontajner pre tabuľku a scrollbary
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True)

        # Grid konfigurácia
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview
        self.tree = ttk.Treeview(table_frame, columns=columns,
                                 show="headings")

        # Scrollbary
        self.scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                       command=self.tree.yview)

        self.xscrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL,
                                        command=self.tree.xview)

        # Prepojenie scrollov
        self.tree.configure(yscrollcommand=self.scrollbar.set,
                            xscrollcommand=self.xscrollbar.set)

        # Hlavičky
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Type")
        self.tree.heading("azimuth", text="Azimuth")
        self.tree.heading("inclination", text="Inclination")
        self.tree.heading("comment", text="Comment", anchor="w")

        # Stĺpce
        self.tree.column("id", width=40, minwidth=40, stretch=tk.NO, anchor="center")
        self.tree.column("type", width=60, minwidth=60, stretch=tk.NO, anchor="center")
        self.tree.column("azimuth", width=70, minwidth=60, stretch=tk.NO, anchor="e")
        self.tree.column("inclination", width=70, minwidth=60, stretch=tk.NO, anchor="e")
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
                    row["inclination"],
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
            self.projection = StereonetProjection(
                self.ax, 
                self.canvas, 
                data, 
                self.app.lineation_settings,
                self.app.plane_settings,
                self.app.contour_settings
                )
        else:
            self.projection.data = data
            self.projection.plots.clear()
            self.projection.lineation_settings = self.app.lineation_settings
            self.projection.plane_settings = self.app.plane_settings
            self.projection.contour_settings = self.app.contour_settings

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
