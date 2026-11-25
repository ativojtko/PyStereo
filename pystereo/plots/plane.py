from dataclasses import dataclass, asdict


@dataclass
class PlaneSettings:
    """
    Settings for plotting planes on a stereonet.
    Attributes:
        color (str): Colour of the plane. Default is "green".
        linewidth (float): Thickeness of the great circle. Default is 1.
        linestyle (str): Style of the great circle (e.g., "-", "--", "-.", ":"). Default is "-".
        segments (int): Number of segments for drawing the curve (higher number = smoother curve). 
                        Default is 50.
        alpha (float): Transparency (0.0 = fully transparent, 1.0 = opaque). Default is 1.0.
        picker (int): Tolerance for selection (in pixels). Default is 3.
        label (str): Label for the legend. Default is "Planes". Not used in the current implementation.
    """

    color: str = "green"
    linewidth: float = 1
    linestyle: str = "-"
    segments: int = 50
    alpha: float = 1.0
    picker: int = 3
    #label: str = "Planes"
    

class PlanePlot:
    """
    Class for plotting planes on a stereonet.
    """
    def __init__(self, ax, settings=None):
        self.ax = ax
        self.settings = settings if settings is not None else PlaneSettings()

    def draw(self, item, legend=False):
        azimuth = item["azimuth"]
        inclination = item["inclination"]
        strike = (azimuth - 90) % 360
        obj, = self.ax.plane(
            strike, 
            inclination,
            **asdict(self.settings)
        )   
        
        return obj
