#TODO: refactoring, improve code quality, add type hints, add docstrings, add unit tests and GUI for settings
from dataclasses import dataclass


@dataclass
class ContourSettings:
    # ---- contour appearance ----
    cmap: str = "binary"
    alpha: float = 1.0
    levels: int = 8

    # ---- contour lines ----
    show_lines: bool = False
    linecolor: str = "black"
    linewidth: float = 3.0
    linestyle: str = "-"

    # ---- data points ----
    show_points: bool = True
    point_color: str = "black"
    point_marker: str = "o"
    point_size: float = 7.0

    # ---- density method ----
    measurement: str = "lines"
    method: str = "exponential_kamb"
    sigma: float = 3.0
    gridsize: int = 100


class ContourPlot:
    def __init__(self, ax, data, settings=None):
        self.ax = ax
        self.data = data
        self.settings = (
            settings if settings is not None
            else ContourSettings()
        )

    def draw(self):
        plunges = []
        bearings = []

        # Extract lineation data
        for item in self.data:
            if item["type"] == "L":
                plunges.append(item["inclination"])
                bearings.append(item["azimuth"])

        # Nothing to plot
        if not plunges:
            return

        settings = self.settings

        # Density calculation parameters
        density_kwargs = {
            "measurement": settings.measurement,
            "levels": settings.levels,
        }

        # Method-specific parameters
        if settings.method == "schmidt":
            density_kwargs["method"] = "schmidt"
        else:
            density_kwargs.update({
                "method": settings.method,
                "sigma": settings.sigma,
                "gridsize": settings.gridsize,
            })

        # Filled density contours
        self.ax.density_contourf(
            plunges,
            bearings,
            cmap=settings.cmap,
            alpha=settings.alpha,
            **density_kwargs,
        )

        # Optional contour lines
        if settings.show_lines:
            self.ax.density_contour(
                plunges,
                bearings,
                colors=settings.linecolor,
                linewidths=settings.linewidth,
                linestyles=settings.linestyle,
                **density_kwargs,
            )

        # Optional original data points
        if settings.show_points:
            self.ax.line(
                plunges,
                bearings,
                color=settings.point_color,
                marker=settings.point_marker,
                linestyle="None",
                markersize=settings.point_size,
            )
