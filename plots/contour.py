#TODO: refactoring, this is a copy of the contour plot in the stereonet, but it should be more general and not rely on the stereonet data structure
from dataclasses import dataclass


@dataclass
class ContourSettings:
    # ---- contour appearance ----
    cmap: str = "binary"
    alpha: float = 1.0
    levels: int = 9

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


class ContourPlot:
    def __init__(self, ax, data, settings=None):
        self.ax = ax
        self.data = data
        self.settings = (
            settings if settings else ContourSettings()
        )

    def draw(self):
        plunges = []
        bearings = []

        # Extract lineation data
        for item in self.data:
            if item["type"] == "L":
                plunges.append(item["dip"])
                bearings.append(item["azimuth"])

        # Nothing to plot
        if not plunges:
            return

        # Filled density contours
        self.ax.density_contourf(
            plunges,
            bearings,
            measurement=self.settings.measurement,
            levels=self.settings.levels,
            cmap=self.settings.cmap,
            alpha=self.settings.alpha
        )

        # Optional contour lines
        if self.settings.show_lines:
            self.ax.density_contour(
                plunges,
                bearings,
                measurement=self.settings.measurement,
                levels=self.settings.levels,
                colors=self.settings.linecolor,
                linewidths=self.settings.linewidth,
                linestyles=self.settings.linestyle
            )

        # Optional original data points
        if self.settings.show_points:
            self.ax.line(
                plunges,
                bearings,
                color=self.settings.point_color,
                marker=self.settings.point_marker,
                linestyle='None',
                markersize=self.settings.point_size
            )

# End of contour.py: (c) 2026 R. Vojtko, H. Balažovjechová
