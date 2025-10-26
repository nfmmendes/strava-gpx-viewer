import numpy as np
from threading import Thread

### For embedding in Qt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
import matplotlib.cm as cm
from PyQt6.QtWidgets import QPushButton, QToolTip
from map_viewer import MapViewer

from advanced_dashboard_viewer import AdvancedDashboardViewer
from chart_range_selector import ChartRangeSelector

class ChartDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QGridLayout(self)
        self._redraw = False

        canvas_factory = lambda w, h : FigureCanvas(Figure(figsize = (6,2.5)))
        
        self._speed_chart_canvas = canvas_factory(14, 3.2)
        self._stats_time_chart_canvas = canvas_factory(4, 3.2)
        self._elevation_distance_chart_canvas = canvas_factory(4, 3.2)

        self._grade_detailed_chart_button = QPushButton("Open advanced dashboard")
        self._grade_detailed_chart_button.setFixedSize(200, 30)
        self._grade_detailed_chart_button.clicked.connect(self.open_grade_detailed_chart)
        self._grade_detailed_chart_button.setVisible(False)

        layout.addWidget(NavigationToolbar(self._speed_chart_canvas, self, coordinates = False), 0, 0)
        layout.addWidget(self._grade_detailed_chart_button, 0, 1)
        layout.addWidget(self._speed_chart_canvas, 1, 0, 1, 2)
        layout.addWidget(NavigationToolbar(self._elevation_distance_chart_canvas, self), 2, 0) 
        layout.addWidget(self._elevation_distance_chart_canvas, 3, 0) 
        layout.addWidget(NavigationToolbar(self._stats_time_chart_canvas, self), 2, 1) 
        layout.addWidget(self._stats_time_chart_canvas, 3, 1)

        ChartDashboard.setStyleSheet(self, """QToolTip { 
                                padding: 10px; 
                                background-color: white; 
                                border: black solid 1px
                   }""")
                
    def _speed_chart_hover(self, event):
        x, y = event.xdata, event.ydata
        text = ""

        self._speed_chart_canvas.setToolTip(None)
        
        if x == None or y == None:
            QToolTip.hideText()
            return
        
        row_closest = self._speed_chart_data.loc[(self._speed_chart_data.KM - x).abs().idxmin()]
        text = f"<b> Distance (Km): </b> {round(row_closest.KM, 2)} <br>\
                 <b> Grade (%): </b> {round(100*row_closest['Elevation Gain']/row_closest.Distance, 1)} <br>\
                 <b> Instant speed (Km/h): </b> {round(3.6*row_closest.Distance/row_closest['Delta Time'], 2)}\
                 <b> Average speed (Km/h): </b> {round(row_closest['Avg Speed'], 2)}"
        
        if text:
           self._speed_chart_canvas.setToolTip(text)
        else:
           self._speed_chart_canvas.setToolTip(None)
           QToolTip.hideText()

    def _speed_chart_click(self ,event):
        if not event.dblclick:
            return 
        
        central_index = abs(self._speed_chart_data['KM'] - event.xdata).idxmin()
        
        start = max(central_index - 150, 0)
        end = min(central_index + 150, len(self._speed_chart_data) - 1)
        
        lat_long_df = self._speed_chart_data.iloc[start : end][['Latitude', 'Longitude']]
        points = list(zip(lat_long_df['Latitude'], lat_long_df['Longitude']))

        self._map_viewer = MapViewer()
        self._map_viewer.show_poly_line(points)

    def select_callback(self, eclick, erelease):
        start = abs(self._speed_chart_data['KM'] - eclick.xdata).idxmin()
        end = abs(self._speed_chart_data['KM'] - erelease.xdata).idxmin()
        
        lat_long_df = self._speed_chart_data.iloc[start : end][['Latitude', 'Longitude']]
        points = list(zip(lat_long_df['Latitude'], lat_long_df['Longitude']))
        
        self._map_viewer = MapViewer()
        self._map_viewer.show_poly_line(points)
        self._chart_range_selector.reset()

    def _clean_speed_chart_data(self, df):
        # Clean elevation grade data
        summarized_df = df[["Latitude", "Longitude", "KM", "Elevation Gain", 
                            "Distance", "Delta Time", "Avg Speed", "Speed rollmean"]]

        rolling_mean = summarized_df[["Distance", "Elevation Gain"]].rolling(20).mean()
        summarized_df.loc[: ,"Distance"] = rolling_mean["Distance"]
        summarized_df.loc[:, "Elevation Gain"] = rolling_mean["Elevation Gain"]

        minimum_measurements = 15
        if len(summarized_df) < minimum_measurements:
            return
        
        grades = abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]).sort_values(ascending=False)
        grade_threshold = grades.iloc[minimum_measurements - 1] - 0.02
        return summarized_df[abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]) < grade_threshold]

    def _plot_speed(self, df):
        self._speed_chart_canvas.figure.clf()
        chart = self._speed_chart_canvas.figure.subplots()

        cleaned_df = self._clean_speed_chart_data(df)
 
        (avg_line, ) = chart.plot(cleaned_df["KM"], cleaned_df["Avg Speed"], label="average")
        (instant_line, )= chart.plot(cleaned_df["KM"], cleaned_df["Speed rollmean"], label="instantaneous")
        chart.set_xlabel("Accumulated distance (Km)")
        chart.set_ylabel("Speed (Km/h)")
        avg_fill = chart.fill_between(df["KM"], df["Avg Speed"], alpha=0.3)
        instant_fill = chart.fill_between(df["KM"], df["Speed rollmean"], alpha=0.3)

        self._chart_range_selector = ChartRangeSelector(chart, self.select_callback)

        ax2 = chart.twinx()
        (elevation_line, ) = ax2.plot(cleaned_df["KM"], 100*cleaned_df["Elevation Gain"]/cleaned_df["Distance"], 
                                    color="#334455", label="Grade")
        ax2.set_ylabel("Grade (%)")

        lines, labels = chart.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        leg = ax2.legend(lines + lines2, labels + labels2, loc="upper right")

        self._speed_chart_data = cleaned_df

        chart.set_picker(True)
        ax2.set_picker(True)
        self._map_legend_to_ax = {}  # Will map legend lines to original lines.

        pickradius = 5  # Points (Pt). How close the click needs to be to trigger an event.

        for legend_line, ax_line in zip(leg.get_lines(), [avg_line, instant_line, elevation_line]):
            legend_line.set_picker(pickradius)  # Enable picking on the legend line.
            self._map_legend_to_ax[legend_line] = []
            self._map_legend_to_ax[legend_line].append(ax_line)
        for legend_line, fill_line in zip(leg.get_lines(), [avg_fill, instant_fill, None]):
            if fill_line is None:
                continue
            self._map_legend_to_ax[legend_line].append(fill_line)


        self._speed_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.1)
        self._speed_chart_canvas.figure.tight_layout()
        self._speed_chart_canvas.figure.savefig("./speed_chart.png")
        self._speed_chart_canvas.figure.canvas.mpl_connect('motion_notify_event', self._speed_chart_hover)
        self._speed_chart_canvas.figure.canvas.mpl_connect('button_press_event', self._speed_chart_click)
        self._speed_chart_canvas.figure.canvas.mpl_connect('pick_event', self.on_speed_pick)  
 
        instant_line.figure.canvas.draw()

    def on_speed_pick(self, event):
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        legend_line = event.artist

        # Do nothing if the source of the event is not a legend line.
        if legend_line not in self._map_legend_to_ax:
            return

        for el in self._map_legend_to_ax[legend_line]:
            visible = not el.get_visible()
            el.set_visible(visible)
            # Change the alpha on the line in the legend, so we can see what lines
            # have been toggled.
            legend_line.set_alpha(1.0 if visible else 0.2)

        self._speed_chart_canvas.figure.canvas.draw()


    def _plot_stats_over_time(self, df):
        self._stats_time_chart_canvas.figure.clf()
        chart = self._stats_time_chart_canvas.figure.subplots()

        speed_std_dev = df["Avg Speed"].std()
        final_avg = df.iloc[-1]["Avg Speed"]
        lb = final_avg - 3*speed_std_dev
        ub = final_avg + 3*speed_std_dev
        
        deviation = [min(1, (final_avg - x)/(final_avg - lb))/2 if x < final_avg else
                     0.5 + min(1, (x - final_avg)/(ub - final_avg))/2 for x in df["Speed"]]

        cmap = cm.coolwarm
        step_size = 20
        if len(df) > step_size:
            for i in range(step_size, len(df), step_size):
                chart.fill_between(df.iloc[i - step_size: i]["Tot. Time"].dt.total_seconds()/60, 
                                   df.iloc[i - step_size : i]["KM"],
                                   color= cmap(1 - np.array(deviation[i - step_size : i]).mean()))
        
        chart.annotate('speed: red < average < blue', xy = (0.05, 1.05), xycoords='axes fraction')

        plot, = chart.plot(df["Tot. Time"].dt.total_seconds()/60, df["KM"], label ="Distance")
        chart.set_xlabel("Time (minutes)")
        chart.set_ylabel("Distance (Km)")
        chart.grid(color = 'green', linestyle = '--', linewidth = 0.3)
        chart.legend(loc="upper left")

        positive_elevation_gain_df = df[df["Elevation Gain"] > 0]
        ax2 = chart.twinx()
        ax2.plot(positive_elevation_gain_df["Tot. Time"].dt.total_seconds()/60, 
                 positive_elevation_gain_df["Elevation Gain"].cumsum(), 
                 color="#334455", label="Elevation Gain")
        ax2.set_ylabel("Elevation gain (m)")
        ax2.legend(loc="lower right")

        self._stats_time_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)
        self._stats_time_chart_canvas.figure.savefig("./time_stats_chart.png")
        plot.figure.canvas.draw()

    def _normalized_grade(self, df, index, step_size):
        grade = (100*df.iloc[index - step_size : index]["Elevation Gain"]/df.iloc[index - step_size : index]["Distance"]).mean()
        grade = min(max(grade, -12), 12) # Keeps the gra between -12 and 12
        return (12 + grade)/24 # A value between 0 and 1

    def _plot_elevation_over_distance(self, df):
        self._elevation_distance_chart_canvas.figure.clf()
        chart = self._elevation_distance_chart_canvas.figure.subplots()

        plot, = chart.plot(df["KM"], df["Elevation"])
        chart.set_xlabel("Distance (Km)")
        chart.set_ylabel("Elevation (m)")
        self._elevation_distance_chart_canvas.figure.subplots_adjust(bottom=0.15)
        
        cmap = cm.coolwarm

        step_size = 10
        if len(df) > step_size:
            for i in range(step_size, len(df), step_size):
                chart.fill_between(df.iloc[i - step_size: i]["KM"], df.iloc[i - step_size : i]["Elevation"],\
                        color= cmap(self._normalized_grade(df, i, step_size)))

        chart.annotate('grade scale: blue < 0% < red', xy = (0.05, 1.05), xycoords='axes fraction')
        chart.grid(color = 'green', linestyle = '--', linewidth = 0.3)

        self._elevation_distance_chart_canvas.figure.savefig("./elevation_distance_chart.png")
        plot.figure.canvas.draw()

    def open_grade_detailed_chart(self):
        self._advanced_dashboard = AdvancedDashboardViewer(self._speed_chart_data)
        self._advanced_dashboard.show() 
    
    def initialize_charts(self, df):
        threads = []
        threads.append(Thread(target=self._plot_speed, args=[df]))
        threads.append(Thread(target=self._plot_stats_over_time, args=[df]))
        threads.append(Thread(target=self._plot_elevation_over_distance, args=[df]))
        self._grade_detailed_chart_button.setVisible(True)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

