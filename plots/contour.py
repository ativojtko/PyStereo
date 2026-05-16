#TODO: refactoring, this is a copy of the contour plot in the stereonet, but it should be more general and not rely on the stereonet data structure
class ContourPlot:
    def __init__(self, ax, data):
        self.ax = ax
        self.data = data

    def draw(self):
        plunges = []
        bearings = []

        for item in self.data:
            if item["type"] == "L":
                plunges.append(item["dip"])
                bearings.append(item["azimuth"])

        if plunges:
            self.ax.density_contourf(
                plunges,
                bearings,
                measurement="lines",
                levels=12
            )

            self.ax.line(
                plunges,
                bearings,
                color='black',
                marker='o',
                linestyle='None',
                markersize=2
            )