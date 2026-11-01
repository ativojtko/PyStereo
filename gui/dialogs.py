import tkinter as tk
from tkinter import ttk


class LineationSettingsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.app = app
        self.title("Lineation Settings")
        self.geometry("400x400")
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
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # --- Appearance Frame ---
        app_frame = ttk.LabelFrame(main_frame, text=" Marker Style ", padding=12)
        app_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(app_frame, text="Marker:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(
            app_frame,
            textvariable=self.marker_var,
            values=["o", "^", "s", "x", "d"],
            width=15,
            state="readonly"
        ).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(app_frame, text="Size:").grid(row=1, column=0, sticky="w", pady=5)
        size_frame = ttk.Frame(app_frame)
        size_frame.grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Scale(
            size_frame,
            from_=2,
            to=20,
            variable=self.size_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.size_label = ttk.Label(size_frame, text="", width=4)
        self.size_label.pack(side="right", padx=(5, 0))
        self.size_var.trace_add("write", lambda *_: self.size_label.configure(text=f"{self.size_var.get():.0f}"))
        self.size_label.configure(text=f"{self.size_var.get():.0f}")

        ttk.Label(app_frame, text="Colour:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(app_frame, textvariable=self.color_var, width=18).grid(row=2, column=1, sticky="ew", pady=5)

        app_frame.columnconfigure(1, weight=1)

        # --- Edge & Transparency Frame ---
        edge_frame = ttk.LabelFrame(main_frame, text=" Outline & Transparency ", padding=12)
        edge_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(edge_frame, text="Alpha:").grid(row=0, column=0, sticky="w", pady=5)
        alpha_frame = ttk.Frame(edge_frame)
        alpha_frame.grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Scale(
            alpha_frame,
            from_=0.1,
            to=1.0,
            variable=self.alpha_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.alpha_label = ttk.Label(alpha_frame, text="", width=4)
        self.alpha_label.pack(side="right", padx=(5, 0))
        self.alpha_var.trace_add("write", lambda *_: self.alpha_label.configure(text=f"{self.alpha_var.get():.2f}"))
        self.alpha_label.configure(text=f"{self.alpha_var.get():.2f}")

        ttk.Label(edge_frame, text="Edge Colour:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(edge_frame, textvariable=self.edgecolor_var, width=18).grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(edge_frame, text="Edge Width:").grid(row=2, column=0, sticky="w", pady=5)
        width_frame = ttk.Frame(edge_frame)
        width_frame.grid(row=2, column=1, sticky="ew", pady=5)
        ttk.Scale(
            width_frame,
            from_=0.0,
            to=5.0,
            variable=self.edgewidth_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.ewidth_label = ttk.Label(width_frame, text="", width=4)
        self.ewidth_label.pack(side="right", padx=(5, 0))
        self.edgewidth_var.trace_add("write", lambda *_: self.ewidth_label.configure(text=f"{self.edgewidth_var.get():.1f}"))
        self.ewidth_label.configure(text=f"{self.edgewidth_var.get():.1f}")

        edge_frame.columnconfigure(1, weight=1)

        # --- Buttons Frame (Defaults, Cancel, Apply, OK) ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(5, 0))

        # 1. Defaults vľavo
        ttk.Button(
            btn_frame,
            text="Defaults",
            command=self.restore_defaults,
            width=9
        ).pack(side="left")

        # 2. OK, Apply a Cancel vpravo
        ttk.Button(
            btn_frame,
            text="OK",
            command=self.ok,
            width=9
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            btn_frame,
            text="Apply",
            command=self.on_apply,
            width=9
        ).pack(side="right", padx=(0, 0))

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            width=9
        ).pack(side="right", padx=(0, 5))

    def restore_defaults(self):
        # Vytvorí čerstvú inštanciu nastavení s defaultnými hodnotami z dataclassu
        default_settings = type(self.app.lineation_settings)()

        self.marker_var.set(default_settings.marker)
        self.size_var.set(default_settings.markersize)
        self.color_var.set(default_settings.color)
        self.alpha_var.set(default_settings.alpha)
        self.edgecolor_var.set(default_settings.markeredgecolor)
        self.edgewidth_var.set(default_settings.markeredgewidth)

    def on_apply(self):
        settings = self.app.lineation_settings

        settings.marker = self.marker_var.get()
        settings.markersize = self.size_var.get()
        settings.color = self.color_var.get()
        settings.alpha = self.alpha_var.get()
        settings.markeredgecolor = self.edgecolor_var.get()
        settings.markeredgewidth = self.edgewidth_var.get()

        if self.app.data:
            self.app.plot_lineations()

        return True

    def ok(self):
        if self.on_apply():
            self.destroy()

    def cancel(self):
        self.destroy()


class PlaneSettingsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.app = app
        self.title("Plane Settings")
        self.geometry("400x320")
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
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        frame = ttk.LabelFrame(main_frame, text=" Plane Rendering ", padding=12)
        frame.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Colour:").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.color_var, width=18).grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Line Style:").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Combobox(
            frame,
            textvariable=self.linestyle_var,
            values=["-", "--", "-.", ":"],
            state="readonly",
            width=15
        ).grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Line Width:").grid(row=2, column=0, sticky="w", pady=6)
        lw_frame = ttk.Frame(frame)
        lw_frame.grid(row=2, column=1, sticky="ew", pady=6)
        ttk.Scale(
            lw_frame,
            from_=0.5,
            to=5.0,
            variable=self.linewidth_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.lw_label = ttk.Label(lw_frame, text="", width=4)
        self.lw_label.pack(side="right", padx=(5, 0))
        self.linewidth_var.trace_add("write", lambda *_: self.lw_label.configure(text=f"{self.linewidth_var.get():.1f}"))
        self.lw_label.configure(text=f"{self.linewidth_var.get():.1f}")

        ttk.Label(frame, text="Alpha:").grid(row=3, column=0, sticky="w", pady=6)
        alpha_frame = ttk.Frame(frame)
        alpha_frame.grid(row=3, column=1, sticky="ew", pady=6)
        ttk.Scale(
            alpha_frame,
            from_=0.1,
            to=1.0,
            variable=self.alpha_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.alpha_label = ttk.Label(alpha_frame, text="", width=4)
        self.alpha_label.pack(side="right", padx=(5, 0))
        self.alpha_var.trace_add("write", lambda *_: self.alpha_label.configure(text=f"{self.alpha_var.get():.2f}"))
        self.alpha_label.configure(text=f"{self.alpha_var.get():.2f}")

        ttk.Label(frame, text="Segments:").grid(row=4, column=0, sticky="w", pady=6)
        seg_frame = ttk.Frame(frame)
        seg_frame.grid(row=4, column=1, sticky="ew", pady=6)
        ttk.Scale(
            seg_frame,
            from_=10,
            to=200,
            variable=self.segments_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.seg_label = ttk.Label(seg_frame, text="", width=4)
        self.seg_label.pack(side="right", padx=(5, 0))
        self.segments_var.trace_add("write", lambda *_: self.seg_label.configure(text=f"{int(self.segments_var.get())}"))
        self.seg_label.configure(text=f"{int(self.segments_var.get())}")

        frame.columnconfigure(1, weight=1)

        # --- Buttons Frame (Defaults, Cancel, Apply, OK) ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(5, 0))

        # 1. Defaults vľavo
        ttk.Button(
            btn_frame,
            text="Defaults",
            command=self.restore_defaults,
            width=9
        ).pack(side="left")

        # 2. OK, Apply a Cancel vpravo
        ttk.Button(
            btn_frame,
            text="OK",
            command=self.ok,
            width=9
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            btn_frame,
            text="Apply",
            command=self.on_apply,
            width=9
        ).pack(side="right", padx=(0, 0))

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            width=9
        ).pack(side="right", padx=(0, 5))

    def restore_defaults(self):
        default_settings = type(self.app.plane_settings)()

        self.color_var.set(default_settings.color)
        self.linewidth_var.set(default_settings.linewidth)
        self.linestyle_var.set(default_settings.linestyle)
        self.alpha_var.set(default_settings.alpha)
        self.segments_var.set(default_settings.segments)

    def on_apply(self):
        settings = self.app.plane_settings

        settings.color = self.color_var.get()
        settings.linewidth = self.linewidth_var.get()
        settings.linestyle = self.linestyle_var.get()
        settings.alpha = self.alpha_var.get()
        settings.segments = int(self.segments_var.get())

        if self.app.data:
            self.app.plot_great_circles()

        return True

    def ok(self):
        if self.on_apply():
            self.destroy()

    def cancel(self):
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
