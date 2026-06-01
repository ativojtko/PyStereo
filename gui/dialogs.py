import tkinter as tk
from tkinter import ttk


class LineationSettingsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.app = app
        self.title("Lineation Settings")
        self.geometry("350x450")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        settings = app.lineation_settings

        self.marker_var = tk.StringVar(value=settings.marker)
        self.size_var = tk.DoubleVar(value=settings.markersize)
        self.color_var = tk.StringVar(value=settings.color)
        self.alpha_var = tk.DoubleVar(value=settings.alpha)
        self.edgecolor_var = tk.StringVar(value=settings.markeredgecolor)
        self.edgewidth_var = tk.DoubleVar(value=settings.markeredgewidth)

        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Marker").pack(pady=5)
        ttk.Combobox(
            self,
            textvariable=self.marker_var,
            values=["o", "^", "s", "x", "d"]
        ).pack()

        ttk.Label(self, text="Size").pack(pady=5)
        ttk.Scale(
            self,
            from_=2,
            to=20,
            variable=self.size_var,
            orient="horizontal"
        ).pack(fill="x", padx=20)

        ttk.Label(self, text="Colour").pack(pady=5)
        ttk.Entry(self, textvariable=self.color_var).pack()

        ttk.Label(self, text="Alpha").pack(pady=5)

        ttk.Scale(
            self,
            from_=0.1,
            to=1.0,
            variable=self.alpha_var,
            orient="horizontal"
        ).pack(fill="x", padx=20)

        ttk.Label(self, text="Edge Colour").pack(pady=5)

        ttk.Entry(
            self,
            textvariable=self.edgecolor_var
        ).pack()

        ttk.Label(self, text="Edge Width").pack(pady=5)

        ttk.Scale(
            self,
            from_=0.0,
            to=5.0,
            variable=self.edgewidth_var,
            orient="horizontal"
        ).pack(fill="x", padx=20)

        ttk.Button(
            self,
            text="Apply",
            command=self.apply
        ).pack(pady=20) 


    def apply(self):
        settings = self.app.lineation_settings

        settings.marker = self.marker_var.get()
        settings.markersize = self.size_var.get()
        settings.color = self.color_var.get()
        settings.alpha = self.alpha_var.get()
        settings.markeredgecolor = self.edgecolor_var.get()
        settings.markeredgewidth = self.edgewidth_var.get()

        if self.app.data:
            self.app.plot_lineations()

        self.destroy()

class PlaneSettingsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.app = app

        self.title("Plane Settings")
        self.geometry("350x350")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        settings = app.plane_settings

        self.color_var = tk.StringVar(value=settings.color)
        self.linewidth_var = tk.DoubleVar(value=settings.linewidth)
        self.linestyle_var = tk.StringVar(value=settings.linestyle)
        self.alpha_var = tk.DoubleVar(value=settings.alpha)
        self.segments_var = tk.IntVar(value=settings.segments)

        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Colour").pack(pady=5)

        ttk.Entry(
            self,
            textvariable=self.color_var
        ).pack()

        ttk.Label(self, text="Line Width").pack(pady=5)

        ttk.Scale(
            self,
            from_=0.5,
            to=5.0,
            variable=self.linewidth_var,
            orient="horizontal"
        ).pack(fill="x", padx=20)

        ttk.Label(self, text="Line Style").pack(pady=5)

        ttk.Combobox(
            self,
            textvariable=self.linestyle_var,
            values=["-", "--", "-.", ":"],
            state="readonly"
        ).pack()

        ttk.Label(self, text="Alpha").pack(pady=5)

        ttk.Scale(
            self,
            from_=0.1,
            to=1.0,
            variable=self.alpha_var,
            orient="horizontal"
        ).pack(fill="x", padx=20)

        ttk.Label(self, text="Segments").pack(pady=5)

        ttk.Scale(
            self,
            from_=10,
            to=200,
            variable=self.segments_var,
            orient="horizontal"
        ).pack(fill="x", padx=20)

        ttk.Button(
            self,
            text="Apply",
            command=self.apply
        ).pack(pady=20)

    def apply(self):
        settings = self.app.plane_settings

        settings.color = self.color_var.get()
        settings.linewidth = self.linewidth_var.get()
        settings.linestyle = self.linestyle_var.get()
        settings.alpha = self.alpha_var.get()
        settings.segments = self.segments_var.get()

        if self.app.data:
            self.app.plot_great_circles()

        self.destroy()

class ContourSettingsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.app = app

        self.title("Contour Settings")
        self.geometry("350x450")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        settings = app.contour_settings
        
        self.cmap_var = tk.StringVar(value=settings.cmap)
        self.levels_var = tk.IntVar(value=settings.levels)
        self.alpha_var = tk.DoubleVar(value=settings.alpha)

        self.show_points_var = tk.BooleanVar(
            value=settings.show_points
        )

        self.point_size_var = tk.DoubleVar(
            value=settings.point_size
        )

        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Colour Map").pack(pady=5)

        ttk.Combobox(
            self,
            textvariable=self.cmap_var,
            values=[
                "Grays",
                "binary",
                "viridis",
                "plasma",
                "inferno",
                "magma",
                "jet",
                "terrain",
                "cividis",
                "Reds"
            ],
            state="readonly"
        ).pack()

        ttk.Label(self, text="Levels").pack(pady=5)

        ttk.Scale(
            self,
            from_=3,
            to=30,
            variable=self.levels_var,
            orient="horizontal"
        ).pack(fill="x", padx=20)

        ttk.Label(self, text="Alpha").pack(pady=5)

        ttk.Scale(
            self,
            from_=0.1,
            to=1.0,
            variable=self.alpha_var,
            orient="horizontal"
        ).pack(fill="x", padx=20)

        ttk.Checkbutton(
            self,
            text="Show Points",
            variable=self.show_points_var
        ).pack(pady=10)

        ttk.Label(self, text="Point Size").pack(pady=5)

        ttk.Scale(
            self,
            from_=1,
            to=10,
            variable=self.point_size_var,
            orient="horizontal"
        ).pack(fill="x", padx=20)

        ttk.Button(
            self,
            text="Apply",
            command=self.apply
        ).pack(pady=20)

    def apply(self):
        settings = self.app.contour_settings

        settings.cmap = self.cmap_var.get()
        settings.levels = int(self.levels_var.get())
        settings.alpha = self.alpha_var.get()

        settings.show_points = self.show_points_var.get()
        settings.point_size = self.point_size_var.get()

        if self.app.data:
            self.app.plot_contours()

        self.destroy()


# End of stereo.py: (c) 2026 R. Vojtko, H. Balažovjechová
