import matplotlib.pyplot as plt
import mplstereonet
from plots import LineationPlot, PlanePlot, ContourPlot

class StereonetProjection:
    def __init__(self, ax, canvas, data, lineation_settings, plane_settings, contour_settings):
        self.ax = ax
        self.canvas = canvas
        self.data = data
        self.lineation_settings = lineation_settings
        self.plane_settings = plane_settings
        self.contour_settings = contour_settings
        self.plots = []     # uloženie (obj, údaje)
        self.annot = None   # aktuálny textový label
        self.highlight = None  # zvýraznený objekt

        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('button_press_event', self.on_click_outside)


    def draw(self, mode="all"):
        # Clear old state
        self.plots = []
        self.ax.cla()

        if mode == "contours":
            contour_plot = ContourPlot(
                self.ax,
                self.data,
                settings=self.contour_settings
            )

            contour_plot.draw()

            self.ax.grid()
            self.canvas.draw_idle()
            return
        
        legend_labels = {"S": False, "L": False}

        for i in self.data:
            typ = i["type"]
            # FILTER LOGIKA
            if mode == "lineations" and typ != "L":
                continue

            if mode == "planes" and typ != "S":
                continue

            dataset = i["id"]
            azimuth = i["azimuth"]
            inclination = i["inclination"]
            comment = i["comment"]

            if typ == "L":
                lineation_plot = LineationPlot(self.ax, settings=self.lineation_settings)
                obj = lineation_plot.draw(i, legend=not legend_labels["L"])
                legend_labels["L"] = True

            elif typ == "S":
                plane_plot = PlanePlot(self.ax, settings=self.plane_settings)
                obj = plane_plot.draw(i, legend=not legend_labels["S"])
                legend_labels["S"] = True

            label_text = f"{typ}{dataset} = {azimuth}/{inclination}°"
            if comment:
                label_text += f" ({comment})"

            self.plots.append((
                obj,
                typ,
                label_text
            ))

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
        #metóda na odznačenie objektu
        if self.highlight:
            obj, typ, _ = self.highlight 
            if typ == "L":
                obj.set_marker('o')
                obj.set_color('b')
                obj.set_markersize(6)
            elif typ == "S":
                obj.set_linewidth(1)
                obj.set_color('g')
            self.highlight = None

        if self.annot:
            self.annot.remove()
            self.annot = None

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


    def on_pick(self, event):
        self.reset_highlight()
        artist = event.artist
        
        for obj, typ, label in self.plots:
            if obj == artist:
                # Zvýrazni
                if typ == "L":
                    obj.set_marker('o')
                    obj.set_color('r')
                    obj.set_markersize(8)
                elif typ == "S":
                    obj.set_color('r')
                    obj.set_linewidth(3)

                self.highlight = (obj, typ, label)

                # Zobraz popis
                self.annot = self.ax.annotate(label,
                                              xy=(0, 0), xycoords='axes fraction',
                                              xytext=(0, 0), textcoords='offset points',
                                              ha='left', va='top',
                                              fontsize=8, color='black',
                                              bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black'))
                break

        self.canvas.draw_idle()


if __name__ == "__main__":
    print("This is a projection module. Run PyStereo.py to test.")
