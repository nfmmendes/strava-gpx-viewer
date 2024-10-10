
import pandas as pd
import matplotlib.pyplot as plt

### For embedding in Qt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QGridLayout, QPushButton

class ChartDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QGridLayout(self)
        self._redraw = False

        self._speed_chart_canvas = FigureCanvas(Figure(figsize=(14, 3.2)))
        self._stats_time_chart_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))
        self._elevation_distance_chart_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))

        self._speed_detailed_chart_button = QPushButton("Open advanced dashboard")
        self._speed_detailed_chart_button.setFixedSize(200, 30)

        layout.addWidget(NavigationToolbar(self._speed_chart_canvas, self), 0, 0)
        layout.addWidget(self._speed_detailed_chart_button, 0, 1)
        layout.addWidget(self._speed_chart_canvas, 1, 0, 1, 2)
        layout.addWidget(NavigationToolbar(self._elevation_distance_chart_canvas, self), 2, 0) 
        layout.addWidget(self._elevation_distance_chart_canvas, 3, 0) 
        layout.addWidget(NavigationToolbar(self._stats_time_chart_canvas, self), 2, 1) 
        layout.addWidget(self._stats_time_chart_canvas, 3, 1)

 
    def plot_speed(self, df):
        self._speed_chart_canvas.figure.clf()
        chart = self._speed_chart_canvas.figure.subplots()

        chart.plot(df["KM"], df["Avg Speed"], label="average")
        plot, = chart.plot(df["KM"], df["Speed ma"], label="instantaneous")
        chart.set_xlabel("Accumulated distance (Km)")
        chart.set_ylabel("Speed (Km/h)")
        chart.fill_between(df["KM"], df["Avg Speed"], alpha=0.3)
        chart.fill_between(df["KM"], df["Speed ma"], alpha=0.3)

        # Clean elevation grade data
        summarized_df = df[["KM", "Elevation Gain", "Distance"]].rolling(20).mean()
        grade_threshold = 0.5
        while len(summarized_df[abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]) > grade_threshold]) < 15:
            grade_threshold = grade_threshold - 0.02 
        cleaned_df = summarized_df[abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]) < grade_threshold]
 
        ax2 = chart.twinx()
        ax2.plot(cleaned_df["KM"], 100*cleaned_df["Elevation Gain"]/cleaned_df["Distance"], 
                 color="#334455", label="Grade")
        ax2.set_ylabel("Grade (%)")

        lines, labels = chart.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper right")

        self._speed_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)
        self._speed_chart_canvas.figure.savefig("./speed_chart.png")
        plot.figure.canvas.draw()

    def plot_stats_over_time(self, df):
        self._stats_time_chart_canvas.figure.clf()
        chart = self._stats_time_chart_canvas.figure.subplots()

        plot, = chart.plot(df["Tot. Time"].dt.total_seconds()/60, df["KM"])
        chart.set_xlabel("Time (minutes)")
        chart.set_ylabel("Distance (Km)")
        chart.grid(color = 'green', linestyle = '--', linewidth = 0.5)

        ax2 = chart.twinx()
        ax2.plot(df[df["Elevation Gain"] > 0]["Tot. Time"].dt.total_seconds()/60, 
                 df[df["Elevation Gain"] > 0]["Elevation Gain"].cumsum(), 
                 color="#334455", label="Elevation Gain")
        ax2.set_ylabel("Elevation gain (m)")
        ax2.legend(loc="lower right")

        self._stats_time_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)
        self._stats_time_chart_canvas.figure.savefig("./time_stats_chart.png")
        plot.figure.canvas.draw()

    def plot_elevation_over_distance(self, df):
        self._elevation_distance_chart_canvas.figure.clf()
        chart = self._elevation_distance_chart_canvas.figure.subplots()

        plot, = chart.plot(df["KM"], df["Elevation"])
        chart.set_xlabel("Distance (Km)")
        chart.set_ylabel("Elevation (m)")
        self._elevation_distance_chart_canvas.figure.subplots_adjust(bottom=0.15)
        chart.fill_between(df["KM"], df["Elevation"])

        self._elevation_distance_chart_canvas.figure.savefig("./elevation_distance_chart.png")
        plot.figure.canvas.draw()

    def initialize_charts(self, df):
        self.plot_speed(df)
        self.plot_stats_over_time(df)
        self.plot_elevation_over_distance(df)
