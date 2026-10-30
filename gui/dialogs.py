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
    DENSITY_METHODS = {
        "Exponential Kamb": "exponential_kamb",
        "Linear Kamb": "linear_kamb",
        "Kamb": "kamb",
        "Schmidt": "schmidt",
    }

    def __init__(self, parent, app):
        super().__init__(parent)

        self.app = app

        self.title("Contour Settings")
        self.geometry("370x650")
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

        self.method_var = tk.StringVar(
            value=self._method_label(settings.method)
        )
        self.sigma_var = tk.DoubleVar(value=settings.sigma)
        self.gridsize_var = tk.IntVar(value=settings.gridsize)

        self._build_ui()
        self._update_sigma_state()

    def _method_label(self, method):
        for label, value in self.DENSITY_METHODS.items():
            if value == method:
                return label

        return "Exponential Kamb"

    def _build_ui(self):
        ttk.Label(self, text="Colour Map").pack(pady=(8, 3))

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
                "Reds",
            ],
            state="readonly",
        ).pack()

        ttk.Label(self, text="Density Method").pack(pady=(10, 3))

        self.method_combo = ttk.Combobox(
            self,
            textvariable=self.method_var,
            values=list(self.DENSITY_METHODS.keys()),
            state="readonly",
        )
        self.method_combo.pack()
        self.method_combo.bind(
            "<<ComboboxSelected>>",
            self._update_sigma_state,
        )

        ttk.Label(self, text="Contour Levels").pack(pady=(10, 3))

        ttk.Scale(
            self,
            from_=3,
            to=30,
            variable=self.levels_var,
            orient="horizontal",
        ).pack(fill="x", padx=20)

        self.levels_label = ttk.Label(self, text="")
        self.levels_label.pack()

        ttk.Label(self, text="Smoothing (sigma)").pack(
            pady=(10, 3)
        )

        self.sigma_scale = ttk.Scale(
            self,
            from_=1,
            to=5,
            variable=self.sigma_var,
            orient="horizontal",
        )
        self.sigma_scale.pack(fill="x", padx=20)

        self.sigma_label = ttk.Label(self, text="")
        self.sigma_label.pack()

        ttk.Label(self, text="Grid Resolution").pack(
            pady=(10, 3)
        )

        ttk.Scale(
            self,
            from_=50,
            to=200,
            variable=self.gridsize_var,
            orient="horizontal",
        ).pack(fill="x", padx=20)

        self.gridsize_label = ttk.Label(self, text="")
        self.gridsize_label.pack()

        self.gridsize_var.trace_add(
            "write",
            self._update_gridsize_label,
        )
        self.sigma_var.trace_add(
            "write",
            self._update_sigma_label,
        )
        self.levels_var.trace_add(
            "write",
            self._update_levels_label,
        )
        self._update_gridsize_label()
        self._update_sigma_label()
        self._update_levels_label()

        ttk.Label(self, text="Alpha").pack(pady=(10, 3))

        ttk.Scale(
            self,
            from_=0.1,
            to=1.0,
            variable=self.alpha_var,
            orient="horizontal",
        ).pack(fill="x", padx=20)

        ttk.Checkbutton(
            self,
            text="Show Points",
            variable=self.show_points_var,
        ).pack(pady=(10, 3))

        ttk.Label(self, text="Point Size").pack(pady=(5, 3))

        ttk.Scale(
            self,
            from_=1,
            to=10,
            variable=self.point_size_var,
            orient="horizontal",
        ).pack(fill="x", padx=20)

        ttk.Button(
            self,
            text="Apply",
            command=self.apply,
        ).pack(pady=15)

    def _update_sigma_state(self, event=None):
        method = self.DENSITY_METHODS.get(
            self.method_var.get()
        )

        if method in ("exponential_kamb", "linear_kamb", "kamb"):
            self.sigma_scale.configure(state="normal")
        else:
            self.sigma_scale.configure(state="disabled")

    def _update_sigma_label(self, *args):
        self.sigma_label.configure(
            text=f"{self.sigma_var.get():.1f}"
        )

    def _update_gridsize_label(self, *args):
        self.gridsize_label.configure(
            text=f"{int(self.gridsize_var.get())}"
        )

    def _update_levels_label(self, *args):
        self.levels_label.configure(
            text=f"{self.levels_var.get()}"
        )

    def apply(self):
        settings = self.app.contour_settings

        settings.cmap = self.cmap_var.get()
        settings.levels = int(self.levels_var.get())
        settings.alpha = self.alpha_var.get()

        settings.show_points = self.show_points_var.get()
        settings.point_size = self.point_size_var.get()

        settings.method = self.DENSITY_METHODS[
            self.method_var.get()
        ]
        settings.sigma = self.sigma_var.get()
        settings.gridsize = int(self.gridsize_var.get())

        if self.app.data:
            self.app.plot_contours()

        self.destroy()
