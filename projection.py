import matplotlib.pyplot as plt
import mplstereonet


class StereonetProjection:
    def __init__(self, ax, canvas, data):
        self.ax = ax
        self.canvas = canvas
        self.data = data
        #self.fig = plt.figure(figsize=(8, 5))

        self.plots = []     # uloženie (obj, údaje)
        self.annot = None   # aktuálny textový label
        self.highlight = None  # zvýraznený objekt

        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('button_press_event', self.on_click_outside)


    def draw(self, mode="all"):
        # vyčisti starý stav
        self.plots = []
        self.ax.cla()

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
            dip = i["dip"]
            comment = i["comment"]

            if typ == "S":
                strike = (azimuth - 90) % 360
                obj, = self.ax.plane(
                    strike, dip,
                    'g',
                    linewidth=2,
                    picker=3,
                    label='Plocha' if not legend_labels["S"] else ""
                )
                legend_labels["S"] = True

            elif typ == "L":
                obj, = self.ax.line(
                    dip, azimuth,
                    'bo',
                    markersize=6,
                    picker=6,
                    label='Lineácia' if not legend_labels["L"] else ""
                )
                legend_labels["L"] = True

            self.plots.append((
                obj,
                typ,
                f"{typ} č.{dataset} | azimuth={azimuth}, dip={dip}"
            ))

        self.ax.grid()

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
            elif typ == "P":
                obj.set_linewidth(2)
                obj.set_color('g')
            self.highlight = None

        if self.annot:
            self.annot.remove()
            self.annot = None

        self.canvas.draw()

    def on_click_outside(self, event):

        # Skontroluj, či kliknutie nie je na existujúci objekt
        for obj, _, _ in self.plots:
            contains, _ = obj.contains(event)
            if contains:
                return  # klik bol na objekt → nič nerob

        # Ak klik nebol na žiadny objekt, resetni výber
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
                                              xy=(1, 1), xycoords='axes fraction',
                                              xytext=(10, -30), textcoords='offset points',
                                              ha='left', va='top',
                                              fontsize=10, color='black',
                                              bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black'))
                break

        self.fig.canvas.draw()
        

    def show(self):
        plt.show()

if __name__ == "__main__":
    # Testovacie dáta
    hodnoty = [[1, 'L', 90, 60, "heude"],
                [2, 'P', 180, 30, 'bbb'],
           [3, 'L', 270, 15, 'ccc'],
           [3, 'P', 270, 15, 'ccc'],
           [4, 'P', 315, 45, 'ddd']]

    plotter = StereonetProjection(hodnoty)
    plotter.draw()
    plotter.show()
