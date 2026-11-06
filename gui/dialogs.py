import tkinter as tk
from tkinter import ttk, messagebox

# zmena: pirdali sme dalsie parametre settings, title, a mode
class LineationSettingsDialog(tk.Toplevel):
    def __init__(self, parent, app, settings=None, title="Lineation Settings"):
        super().__init__(parent)

        self.app = app
        # ak sme dialogu odovzdalib nastavenia, tak ich použije, inak pracuje s lineation settings
        self.settings = settings if settings is not None else app.lineation_settings 
        self.title(title)
        self.geometry("400x400")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        settings = self.settings

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
        default_settings = type(self.settings)()

        self.marker_var.set(default_settings.marker)
        self.size_var.set(default_settings.markersize)
        self.color_var.set(default_settings.color)
        self.alpha_var.set(default_settings.alpha)
        self.edgecolor_var.set(default_settings.markeredgecolor)
        self.edgewidth_var.set(default_settings.markeredgewidth)

    def on_apply(self):
        settings = self.settings

        settings.marker = self.marker_var.get()
        settings.markersize = self.size_var.get()
        settings.color = self.color_var.get()
        settings.alpha = self.alpha_var.get()
        settings.markeredgecolor = self.edgecolor_var.get()
        settings.markeredgewidth = self.edgewidth_var.get()

        # tato podmienka zabezpečí to aby sa po uloženi nastavenia prekreslil iba aktualne zobrzaeny typ merania
        if self.app.plot_panel.current_mode is not None:
            self.app.plot_panel.redraw(
                self.app.data,
                mode=self.app.plot_panel.current_mode
            )

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

        if self.app.plot_panel.current_mode is not None:
            self.app.plot_panel.redraw(
                self.app.data,
                mode=self.app.plot_panel.current_mode
            )

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
        self.geometry("400x480")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        settings = app.contour_settings

        self.cmap_var = tk.StringVar(value=settings.cmap)
        
        if isinstance(settings.levels, int):
            level_mode = "Automatic"
            levels_val = settings.levels
            manual_levels_val = "1, 2, 3, 4"
        else:
            level_mode = "Manual"
            levels_val = 5
            manual_levels_val = ", ".join(str(x) for x in settings.levels)

        self.levels_var = tk.IntVar(value=levels_val)
        self.level_mode_var = tk.StringVar(value=level_mode)
        self.manual_levels_var = tk.StringVar(value=manual_levels_val)
        
        self.alpha_var = tk.DoubleVar(value=settings.alpha)

        self.show_points_var = tk.BooleanVar(value=settings.show_points)
        self.point_size_var = tk.DoubleVar(value=settings.point_size)

        self.method_var = tk.StringVar(value=self._method_label(settings.method))
        self.sigma_var = tk.DoubleVar(value=settings.sigma)
        self.gridsize_var = tk.IntVar(value=settings.gridsize)

        self._build_ui()
        self._update_sigma_state()
        self._update_levels_mode()

    def _method_label(self, method):
        for label, value in self.DENSITY_METHODS.items():
            if value == method:
                return label
        return "Exponential Kamb"

    def _update_levels_mode(self, event=None):
        if self.level_mode_var.get() == "Automatic":
            self.manual_levels_frame.pack_forget()
            self.automatic_levels_frame.pack(fill="x", pady=1)
        else:
            self.automatic_levels_frame.pack_forget()
            self.manual_levels_frame.pack(fill="x", pady=1)

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # --- Mapping & Density Frame ---
        frame1 = ttk.LabelFrame(main_frame, text=" Density & Colourmap ", padding=6)
        frame1.pack(fill="x", pady=(0, 6))

        ttk.Label(frame1, text="Colour Map:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Combobox(
            frame1,
            textvariable=self.cmap_var,
            values=[
                "Grays", "binary", "viridis", "plasma", "inferno",
                "magma", "jet", "terrain", "cividis", "Reds"
            ],
            state="readonly",
            width=18
        ).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(frame1, text="Density Method:").grid(row=1, column=0, sticky="w", pady=2)
        self.method_combo = ttk.Combobox(
            frame1,
            textvariable=self.method_var,
            values=list(self.DENSITY_METHODS.keys()),
            state="readonly",
            width=18
        )
        self.method_combo.grid(row=1, column=1, sticky="ew", pady=2)
        self.method_combo.bind("<<ComboboxSelected>>", self._update_sigma_state)

        frame1.columnconfigure(1, weight=1)

        # --- Parameters Frame ---
        frame2 = ttk.LabelFrame(main_frame, text=" Calculation Parameters ", padding=6)
        frame2.pack(fill="x", pady=(0, 6))

        ttk.Label(frame2, text="Contour Levels:").grid(row=0, column=0, sticky="w", pady=2)
        self.level_mode_combo = ttk.Combobox(
            frame2,
            textvariable=self.level_mode_var,
            values=["Automatic", "Manual"],
            state="readonly",
            width=18
        )
        self.level_mode_combo.grid(row=0, column=1, sticky="ew", pady=2)
        self.level_mode_combo.bind("<<ComboboxSelected>>", self._update_levels_mode)

        self.levels_container = ttk.Frame(frame2)
        self.levels_container.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)

        self.automatic_levels_frame = ttk.Frame(self.levels_container)
        auto_scale_box = ttk.Frame(self.automatic_levels_frame)
        auto_scale_box.pack(fill="x", expand=True)
        ttk.Scale(
            auto_scale_box,
            from_=3,
            to=30,
            variable=self.levels_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.levels_label = ttk.Label(auto_scale_box, text="", width=4)
        self.levels_label.pack(side="right", padx=(5, 0))
        self.levels_var.trace_add("write", lambda *_: self.levels_label.configure(text=f"{int(self.levels_var.get())}"))
        self.levels_label.configure(text=f"{int(self.levels_var.get())}")

        self.manual_levels_frame = ttk.Frame(self.levels_container)
        ttk.Label(self.manual_levels_frame, text="Enter values separated by commas:", font=("", 9)).pack(anchor="w", pady=(0, 1))
        ttk.Entry(self.manual_levels_frame, textvariable=self.manual_levels_var).pack(fill="x", pady=(0, 1))
        self.levels_error_label = ttk.Label(self.manual_levels_frame, text="", foreground="red", font=("", 8))
        self.levels_error_label.pack(anchor="w")

        # Smoothing (sigma)
        ttk.Label(frame2, text="Smoothing (sigma):").grid(row=2, column=0, sticky="w", pady=2)
        sigma_box = ttk.Frame(frame2)
        sigma_box.grid(row=2, column=1, sticky="ew", pady=2)
        self.sigma_scale = ttk.Scale(
            sigma_box,
            from_=1,
            to=10,
            variable=self.sigma_var,
            orient="horizontal"
        )
        self.sigma_scale.pack(side="left", fill="x", expand=True)
        self.sigma_label = ttk.Label(sigma_box, text="", width=4)
        self.sigma_label.pack(side="right", padx=(5, 0))
        self.sigma_var.trace_add("write", lambda *_: self.sigma_label.configure(text=f"{self.sigma_var.get():.1f}"))
        self.sigma_label.configure(text=f"{self.sigma_var.get():.1f}")

        # Grid Resolution
        ttk.Label(frame2, text="Grid Resolution:").grid(row=3, column=0, sticky="w", pady=2)
        grid_box = ttk.Frame(frame2)
        grid_box.grid(row=3, column=1, sticky="ew", pady=2)
        ttk.Scale(
            grid_box,
            from_=50,
            to=200,
            variable=self.gridsize_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.gridsize_label = ttk.Label(grid_box, text="", width=4)
        self.gridsize_label.pack(side="right", padx=(5, 0))
        self.gridsize_var.trace_add("write", lambda *_: self.gridsize_label.configure(text=f"{int(self.gridsize_var.get())}"))
        self.gridsize_label.configure(text=f"{int(self.gridsize_var.get())}")

        frame2.columnconfigure(1, weight=1)

        # --- Display Options Frame ---
        frame3 = ttk.LabelFrame(main_frame, text=" Overlay & Points ", padding=6)
        frame3.pack(fill="x", pady=(0, 6))

        ttk.Label(frame3, text="Alpha:").grid(row=0, column=0, sticky="w", pady=2)
        alpha_box = ttk.Frame(frame3)
        alpha_box.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Scale(
            alpha_box,
            from_=0.1,
            to=1.0,
            variable=self.alpha_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.alpha_label = ttk.Label(alpha_box, text="", width=4)
        self.alpha_label.pack(side="right", padx=(5, 0))
        self.alpha_var.trace_add("write", lambda *_: self.alpha_label.configure(text=f"{self.alpha_var.get():.2f}"))
        self.alpha_label.configure(text=f"{self.alpha_var.get():.2f}")

        ttk.Checkbutton(
            frame3,
            text="Show Points",
            variable=self.show_points_var
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=2)

        ttk.Label(frame3, text="Point Size:").grid(row=2, column=0, sticky="w", pady=2)
        pt_box = ttk.Frame(frame3)
        pt_box.grid(row=2, column=1, sticky="ew", pady=2)
        ttk.Scale(
            pt_box,
            from_=1,
            to=20,
            variable=self.point_size_var,
            orient="horizontal"
        ).pack(side="left", fill="x", expand=True)
        self.pt_label = ttk.Label(pt_box, text="", width=4)
        self.pt_label.pack(side="right", padx=(5, 0))
        self.point_size_var.trace_add("write", lambda *_: self.pt_label.configure(text=f"{self.point_size_var.get():.1f}"))
        self.pt_label.configure(text=f"{self.point_size_var.get():.1f}")

        frame3.columnconfigure(1, weight=1)

        # --- Buttons Frame (Defaults, Cancel, Apply, OK) ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(4, 0))

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

    def _update_sigma_state(self, event=None):
        method = self.DENSITY_METHODS.get(self.method_var.get())
        if method in ("exponential_kamb", "linear_kamb", "kamb"):
            self.sigma_scale.configure(state="normal")
        else:
            self.sigma_scale.configure(state="disabled")

    def restore_defaults(self):
        default_settings = type(self.app.contour_settings)()

        self.cmap_var.set(default_settings.cmap)
        
        if isinstance(default_settings.levels, int):
            self.level_mode_var.set("Automatic")
            self.levels_var.set(default_settings.levels)
        else:
            self.level_mode_var.set("Manual")
            self.manual_levels_var.set(", ".join(str(x) for x in default_settings.levels))
            
        self._update_levels_mode()

        self.alpha_var.set(default_settings.alpha)
        self.show_points_var.set(default_settings.show_points)
        self.point_size_var.set(default_settings.point_size)
        self.method_var.set(self._method_label(default_settings.method))
        self.sigma_var.set(default_settings.sigma)
        self.gridsize_var.set(default_settings.gridsize)
        self._update_sigma_state()
        self.levels_error_label.configure(text="")

    def on_apply(self):
        settings = self.app.contour_settings

        if self.level_mode_var.get() == "Automatic":
            levels = int(self.levels_var.get())
        else:
            try:
                levels = [
                    float(value.strip())
                    for value in self.manual_levels_var.get().split(",")
                    if value.strip()
                ]

                if len(levels) < 2:
                    raise ValueError("Enter at least two contour levels.")

                if not all(value == value and abs(value) != float("inf") for value in levels):
                    raise ValueError("Levels must be finite numbers.")

                if any(current >= following for current, following in zip(levels, levels[1:])):
                    raise ValueError("Levels must be in ascending order.")

            except ValueError as error:
                self.levels_error_label.configure(text=str(error))
                return False  # Chyba pri validácii, nezatvárame / neaplikujeme

        self.levels_error_label.configure(text="")

        settings.cmap = self.cmap_var.get()
        settings.levels = levels
        settings.alpha = self.alpha_var.get()
        settings.show_points = self.show_points_var.get()
        settings.point_size = self.point_size_var.get()
        settings.method = self.DENSITY_METHODS[self.method_var.get()]
        settings.sigma = self.sigma_var.get()
        settings.gridsize = int(self.gridsize_var.get())

        if self.app.plot_panel.current_mode is not None:
            self.app.plot_panel.redraw(
                self.app.data,
                mode=self.app.plot_panel.current_mode
            )
        return True  # Úspešne aplikované

    def ok(self):
        if self.on_apply():
            self.destroy()

    def cancel(self):
        self.destroy()


# Enter the rotation axis and angle
class RotationDialog(tk.Toplevel):
    def __init__(self, parent, app, title="Rotate Structural Elements"):
        super().__init__(parent)

        self.app = app
        self.title(title)
        self.geometry("360x320")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        # Premenné
        self.trend_axis_var = tk.DoubleVar(value=0.0)
        self.plunge_axis_var = tk.DoubleVar(value=0.0)
        self.rotation_angle_var = tk.DoubleVar(value=0.0)
        self.decimal_places_var = tk.IntVar(value=2)

        self._build_ui()
        
        # Ošetrenie zatvorenia okna cez krížik (X)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # --- Rotation Axis Frame ---
        axis_frame = ttk.LabelFrame(main_frame, text=" Rotation Axis ", padding=12)
        axis_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(axis_frame, text="Trend [°]:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(axis_frame, textvariable=self.trend_axis_var, width=18, justify="right").grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(axis_frame, text="Plunge [°]:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(axis_frame, textvariable=self.plunge_axis_var, width=18, justify="right").grid(row=1, column=1, sticky="ew", pady=5)

        axis_frame.columnconfigure(1, weight=1)

        # --- Parameters Frame (Angle & Precision) ---
        param_frame = ttk.LabelFrame(main_frame, text=" Parameters ", padding=12)
        param_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(param_frame, text="Rotation Angle [°]:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(param_frame, textvariable=self.rotation_angle_var, width=18, justify="right").grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(param_frame, text="Decimal Places:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Combobox(
            param_frame,
            textvariable=self.decimal_places_var,
            values=list(range(7)),
            width=15,
            state="readonly",
            justify="right"
        ).grid(row=1, column=1, sticky="ew", pady=5)

        param_frame.columnconfigure(1, weight=1)

        # --- Buttons Frame (Defaults, Cancel, Rotate & Export) ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(5, 0))

        # 1. Defaults vľavo (obnoví nulové hodnoty / štandard)
        ttk.Button(
            btn_frame,
            text="Defaults",
            command=self.restore_defaults,
            width=9
        ).pack(side="left")

        # 2. Cancel a Rotate & Export vpravo
        ttk.Button(
            btn_frame,
            text="Rotate & Export",
            command=self.apply,
            width=14
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            width=9
        ).pack(side="right", padx=(0, 0))

    def restore_defaults(self):
        self.trend_axis_var.set(0.0)
        self.plunge_axis_var.set(0.0)
        self.rotation_angle_var.set(0.0)
        self.decimal_places_var.set(2)

    def apply(self):
        # Read numeric values from the input fields
        try:
            angle = self.rotation_angle_var.get()
            axis = (
                self.trend_axis_var.get(),
                self.plunge_axis_var.get()
            )
        except (tk.TclError, ValueError):
            messagebox.showerror(
                "Invalid input",
                "Enter numbers for the axis and rotation angle.",
                parent=self
            )
            return

        # Check the rotation axis
        trend, plunge = axis

        if not (0 <= trend < 360 and -90 <= plunge <= 90):
            messagebox.showerror(
                "Invalid axis",
                "Axis trend must be in [0, 360).\n"
                "Axis plunge must be in [-90, 90].",
                parent=self
            )
            return

        # Close only after a successful export
        if self.app.rotation(angle, axis, self.decimal_places_var.get()):
            self.destroy()

    def cancel(self):
        self.destroy()
