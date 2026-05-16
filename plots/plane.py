from dataclasses import dataclass, asdict


@dataclass
class PlaneSettings:
    color: str = "green"      # Farba
    linewidth: float = 1.5    # Hrúbka čiary
    linestyle: str = "-"      # Štýl čiary (napríklad "-", "--", "-.", ":")
    segments: int = 50        # Počet segmentov pre vykreslenie krivky (vyššie číslo = hladšia krivka)
    alpha: float = 1.0        # Priehľadnosť (0.0 = úplne priehľadné, 1.0 = nepriehľadné)
    #label: str = "Planes"     # Názov do legendy
    picker: int = 3           # Tolerancia pre výber (v pixeloch)


class PlanePlot:
    def __init__(self, ax, settings=None):
        self.ax = ax
        self.settings = settings if settings is not None else PlaneSettings()

    def draw(self, item, legend=False):
        azimuth = item["azimuth"]
        dip = item["dip"]
        strike = (azimuth - 90) % 360
        obj, = self.ax.plane(
            strike, 
            dip,
            **asdict(self.settings)
        )   
        
        return obj
    

# End of plane.py: (c) 2026 RVOJTKO
    