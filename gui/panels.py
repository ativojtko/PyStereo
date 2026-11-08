import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from projection import StereonetProjection


class DataPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        columns = ("id", "type", "azimuth", "inclination", "comment")

        # Container for the table and scrollbars
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True)

        # Grid configuration to make the table expand with the frame
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview widget for displaying the data
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Scrollbars for the Treeview
        self.scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                       command=self.tree.yview)

        self.xscrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL,
                                        command=self.tree.xview)

        # Configure the Treeview to use the scrollbars
        self.tree.configure(yscrollcommand=self.scrollbar.set,
                            xscrollcommand=self.xscrollbar.set)

        # Headings for the columns
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Type")
        self.tree.heading("azimuth", text="Azimuth")
        self.tree.heading("inclination", text="Inclination")
        self.tree.heading("comment", text="Comment", anchor="w")

        # Columns
        self.tree.column("id", width=40, minwidth=40, stretch=tk.NO, anchor="center")
        self.tree.column("type", width=60, minwidth=60, stretch=tk.NO, anchor="center")
        self.tree.column("azimuth", width=70, minwidth=60, stretch=tk.NO, anchor="e")
        self.tree.column("inclination", width=70, minwidth=60, stretch=tk.NO, anchor="e")
        self.tree.column("comment", width=125, minwidth=100, stretch=tk.NO, anchor="w")

        # Configuration via grid packer to make the table and scrollbars expand with the frame
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.xscrollbar.grid(row=1, column=0, sticky="ew")


    def refresh(self, data):
        """
        Updates the data table with the currently loaded structural dataset.

        Existing rows are cleared before inserting new data to keep
        the table synchronised with PyStereoApp.data.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, row in enumerate(data):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    row["id"],
                    row["type"],
                    row["azimuth"],
                    row["inclination"],
                    row["comment"]
                )
            )

        self._fit_comment_column(data)

    # NOVÉ: nastaví šírku stĺpca Comment podľa najdlhšieho komentára
    def _fit_comment_column(self, data):
        font = tkfont.nametofont("TkDefaultFont")
        min_width = 125
        padding = 20
        widest = max(
            (font.measure(str(row["comment"])) for row in data),
            default=0
        )
        self.tree.column("comment", width=max(min_width, widest + padding))

    # Get the selected row, store its ID, and convert it to an integer.
    # Pass it to the dataset_selected method in the main application.
    def on_select(self, event=None):
        selected = self.tree.selection()

        if not selected:
            return

        index = int(selected[0])
        self.app.dataset_selected(index)


    # Select a row by its index
    def select_row(self, index):
        row_id = str(index)

        if self.tree.exists(row_id):
            self.tree.selection_set(row_id)


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
        self.current_mode = None
        self.canvas.mpl_connect("pick_event", self.on_pick)
        self.canvas.draw()


    def redraw(self, data, mode="all"):
        self.current_mode = mode
        if self.projection is None:
            self.projection = StereonetProjection(
                self.ax, 
                self.canvas, 
                data, 
                self.app.lineation_settings,
                self.app.pole_settings,
                self.app.plane_settings,
                self.app.contour_settings
                )
        else:
            self.projection.data = data
            self.projection.plots.clear()
            self.projection.lineation_settings = self.app.lineation_settings
            self.projection.pole_settings = self.app.pole_settings
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
        self.current_mode = None
        if self.projection is not None:
            self.projection.plots.clear()
            self.projection.highlight = None
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
        if self.projection is not None:
            self.projection.highlight_record(index)

    # Táto metóda nájde kliknutý objekt a zavolá označenie príslušného riadka
    def on_pick(self, event):
        if self.projection is None:
            return

        for obj, typ, index in self.projection.plots:
            if obj is event.artist:
                self.app.data_panel.select_row(index)
                return