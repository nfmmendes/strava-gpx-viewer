
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

### For embedding in Qt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
import matplotlib.cm as cm
from PyQt6.QtWidgets import QGridLayout, QPushButton, QToolTip

from advanced_dashboard_viewer import AdvancedDashboardViewer

class ChartDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QGridLayout(self)
        self._redraw = False

        self._speed_chart_canvas = FigureCanvas(Figure(figsize=(14, 3.2)))
        self._stats_time_chart_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))
        self._elevation_distance_chart_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))

        self._grade_detailed_chart_button = QPushButton("Open advanced dashboard")
        self._grade_detailed_chart_button.setFixedSize(200, 30)
        self._grade_detailed_chart_button.clicked.connect(self.open_grade_detailed_chart)
        self._grade_detailed_chart_button.setVisible(False)

        layout.addWidget(NavigationToolbar(self._speed_chart_canvas, self), 0, 0)
        layout.addWidget(self._grade_detailed_chart_button, 0, 1)
        layout.addWidget(self._speed_chart_canvas, 1, 0, 1, 2)
        layout.addWidget(NavigationToolbar(self._elevation_distance_chart_canvas, self), 2, 0) 
        layout.addWidget(self._elevation_distance_chart_canvas, 3, 0) 
        layout.addWidget(NavigationToolbar(self._stats_time_chart_canvas, self), 2, 1) 
        layout.addWidget(self._stats_time_chart_canvas, 3, 1)

    def hover(self, event):
        x, y = event.xdata, event.ydata

        if x == None or y == None:
            QToolTip.hideText()
            return

        text = f"<b> Distance: </b> {round(x, 2)} <br> <b> Grade: </b> {round(y, 2)}"
        win =  self._speed_chart_canvas.figure.canvas.window()

        if text:
           win.setToolTip(text)
        else:
           win.setToolTip(text)
           QToolTip.hideText()


    def plot_speed(self, df):
        self._speed_chart_canvas.figure.clf()
        chart = self._speed_chart_canvas.figure.subplots()

        # Clean elevation grade data
        summarized_df = df[["KM", "Elevation Gain", "Distance", "Delta Time", "Avg Speed"]]

        rolling_mean = summarized_df[["Distance", "Elevation Gain"]].rolling(20).mean()
        summarized_df.loc[: ,"Distance"] = rolling_mean["Distance"]
        summarized_df.loc[:, "Elevation Gain"] = rolling_mean["Elevation Gain"]

        grade_threshold = 0.5
        while len(summarized_df[abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]) > grade_threshold]) < 15:
            grade_threshold = grade_threshold - 0.02 
        cleaned_df = summarized_df[abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]) < grade_threshold]
 
        chart.plot(cleaned_df["KM"], cleaned_df["Avg Speed"], label="average")
        plot, = chart.plot(df["KM"], df["Speed rollmean"], label="instantaneous")
        chart.set_xlabel("Accumulated distance (Km)")
        chart.set_ylabel("Speed (Km/h)")
        chart.fill_between(df["KM"], df["Avg Speed"], alpha=0.3)
        chart.fill_between(df["KM"], df["Speed rollmean"], alpha=0.3)

        ax2 = chart.twinx()
        ax2.plot(cleaned_df["KM"], 100*cleaned_df["Elevation Gain"]/cleaned_df["Distance"], 
                 color="#334455", label="Grade")
        ax2.set_ylabel("Grade (%)")

        lines, labels = chart.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper right")

        self._speed_chart_data = cleaned_df

        self._speed_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)
        self._speed_chart_canvas.figure.savefig("./speed_chart.png")
        self._speed_chart_canvas.figure.canvas.mpl_connect('motion_notify_event', self.hover)

        plot.figure.canvas.draw()

    def plot_stats_over_time(self, df):
        self._stats_time_chart_canvas.figure.clf()
        chart = self._stats_time_chart_canvas.figure.subplots()

        speed_std_dev = df["Avg Speed"].std()
        final_avg = df.iloc[-1]["Avg Speed"]
        lb = final_avg - 3*speed_std_dev
        ub = final_avg + 3*speed_std_dev
        
        deviation = [min(1, (final_avg - x)/(final_avg - lb))/2 if x < final_avg else\
                     0.5 + min(1, (x - final_avg)/(ub - final_avg))/2 for x in df["Speed"]]

        cmap = cm.coolwarm
        step_size = 20
        if len(df) > step_size:
            for i in range(step_size, len(df), step_size):
                chart.fill_between(df.iloc[i - step_size: i]["Tot. Time"].dt.total_seconds()/60, df.iloc[i - step_size : i]["KM"],\
                        color= cmap(1 - np.array(deviation[i - step_size : i]).mean()))
        
        chart.annotate('speed: red < average < blue', xy = (0.05, 1.05), xycoords='axes fraction')

        plot, = chart.plot(df["Tot. Time"].dt.total_seconds()/60, df["KM"], label ="Distance")
        chart.set_xlabel("Time (minutes)")
        chart.set_ylabel("Distance (Km)")
        chart.grid(color = 'green', linestyle = '--', linewidth = 0.3)
        chart.legend(loc="upper left")

        ax2 = chart.twinx()
        ax2.plot(df[df["Elevation Gain"] > 0]["Tot. Time"].dt.total_seconds()/60, 
                 df[df["Elevation Gain"] > 0]["Elevation Gain"].cumsum(), 
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

    def plot_elevation_over_distance(self, df):
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
        self.plot_speed(df)
        self.plot_stats_over_time(df)
        self.plot_elevation_over_distance(df)
        self._grade_detailed_chart_button.setVisible(True)
