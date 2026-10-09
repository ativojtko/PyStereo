from dataclasses import dataclass, asdict


@dataclass
class LineationSettings:
    marker: str = "o"              # Tvar bodu (o = krúžok, ^ = trojuholník, s = štvorec)
    markersize: float = 7.0        # Veľkosť bodu
    color: str = "red"             # Farba
    alpha: float = 1.0             # Priehľadnosť (0.0 = úplne priehľadné, 1.0 = nepriehľadné)
    markeredgecolor: str = "black" # Farba obrysu bodu
    markeredgewidth: float = 1.0   # Hrúbka obrysu
    #label: str = "Lineation"       # Názov do legendy
    picker: int = 6                # Tolerancia pre výber (v pixeloch)


class LineationPlot:
    def __init__(self, ax, settings=None):
        self.ax = ax
        self.settings = settings if settings is not None else LineationSettings()

    def draw(self, item, legend=False):
        azimuth = item["azimuth"]
        dip = item["dip"]

        obj, = self.ax.line(
            dip,
            azimuth,
            **asdict(self.settings)
        )

        return obj


# End of lineation.py: (c) 2026 RVOJTKO
