import matplotlib.pyplot as plt
import mplstereonet
from plots import LineationPlot, PlanePlot, PolePlot, ContourPlot

class StereonetProjection:
    def __init__(self, ax, canvas, data, lineation_settings, pole_settings, plane_settings, contour_settings):
        self.ax = ax
        self.canvas = canvas
        self.data = data
        self.lineation_settings = lineation_settings
        self.plane_settings = plane_settings
        self.contour_settings = contour_settings
        self.pole_settings = pole_settings
        self.plots = []     # uloženie (obj, údaje)
        self.highlight = None  # zvýraznený objekt

        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('button_press_event', self.on_click_outside)


    def draw(self, mode="all"):
        # Clear old state
        self.plots = []
        self.highlight = None
        self.ax.cla()

        if mode in ("contour_lineations", "contour_poles"):
            mesurment_type = "P" if mode == "contour_poles" else "L"
            
            contour_plot = ContourPlot(
                self.ax,
                self.data,
                mesurment_type=mesurment_type,
                settings=self.contour_settings
            )

            contour_plot.draw()

            self.ax.grid()
            self.canvas.draw_idle()
            return
        
        legend_labels = {"S": False, "L": False, "P": False}

        for index, item in enumerate(self.data):
            typ = item["type"]
            # FILTER LOGIKA, pridali sme póly
            if mode == "lineations" and typ != "L":
                continue

            if mode == "poles" and typ != "P":
                continue

            if mode == "planes" and typ != "S":
                continue

            if typ == "L":
                lineation_plot = LineationPlot(self.ax, settings=self.lineation_settings)
                obj = lineation_plot.draw(item, legend=not legend_labels["L"])
                legend_labels["L"] = True

            elif typ == "P":
                pole_plot = PolePlot(self.ax, settings=self.pole_settings)
                obj = pole_plot.draw(item, legend=not legend_labels["P"])
                legend_labels["P"] = True

            elif typ == "S":
                plane_plot = PlanePlot(self.ax, settings=self.plane_settings)
                obj = plane_plot.draw(item, legend=not legend_labels["S"])
                legend_labels["S"] = True

            self.plots.append((obj, typ, index))

        self.ax.grid()

        handles, labels = self.ax.get_legend_handles_labels()
        if handles:
            self.ax.legend(
                loc='lower left',
                bbox_to_anchor=(0.0, 0.0),
                frameon=False,
                fontsize=9
            )

        self.canvas.draw_idle()


    def reset_highlight(self):
        if self.highlight is not None:
            obj, typ, _ = self.highlight

            if typ in ("L", "P"):
                settings = (
                    self.lineation_settings
                    if typ == "L"
                    else self.pole_settings
                    
                )
                obj.set_color(settings.color)
                obj.set_markersize(settings.markersize)

            elif typ == "S":
                obj.set_color(self.plane_settings.color)
                obj.set_linewidth(self.plane_settings.linewidth)

            self.highlight = None

        self.canvas.draw_idle()

    def on_click_outside(self, event):
        if event.inaxes != self.ax:
            self.reset_highlight()
            return

        # Skontroluj, či kliknutie nie je na existujúci objekt
        for obj, _, _ in self.plots:
            contains, _ = obj.contains(event)
            if contains:
                return  # klik bol na objekt → nič nerob

        # Ak klik nebol na žiadny objekt, resetný výber
        self.reset_highlight()

    def highlight_record(self, index):
        self.reset_highlight()

        for obj, typ, record_index in self.plots:
            if record_index == index:
                self.highlight = (obj, typ, record_index)
                obj.set_color("red")

                if typ == "L":
                    obj.set_markersize(
                        self.lineation_settings.markersize + 2
                    )
                elif typ == "P":
                    obj.set_markersize(
                        self.pole_settings.markersize + 2
                    )
                elif typ == "S":
                    obj.set_linewidth(
                        self.plane_settings.linewidth + 2
                    )

                self.canvas.draw_idle()
                return


    def on_pick(self, event):
        for obj, typ, index in self.plots:
            if obj is event.artist:
                self.highlight_record(index)
                return


if __name__ == "__main__":
    print("This is a projection module. Run PyStereo.py to test.")
