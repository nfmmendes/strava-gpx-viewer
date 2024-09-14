
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### For embedding in Qt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QLabel, QGridLayout

class ChartDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QGridLayout(self)

        self._speed_chart_canvas = FigureCanvas(Figure(figsize=(14, 3.2)))
        self._distance_time_chart_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))
        self._elevation_distance_chart_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))

        layout.addWidget(NavigationToolbar(self._speed_chart_canvas, self), 0, 0, 1, 2)
        layout.addWidget(self._speed_chart_canvas, 1, 0, 1, 2)
        layout.addWidget(NavigationToolbar(self._elevation_distance_chart_canvas, self), 2, 0) 
        layout.addWidget(self._elevation_distance_chart_canvas, 3, 0) 
        layout.addWidget(NavigationToolbar(self._distance_time_chart_canvas, self), 2, 1) 
        layout.addWidget(self._distance_time_chart_canvas, 3, 1)

 
    def plotSpeed(self, chart, df):
        chart.plot(df["KM"], df["Avg Speed"], label="average")
        plot, = chart.plot(df["KM"], df["Speed ma"], label="instantaneous")
        chart.legend(loc="lower left")
        chart.set_xlabel("Accumulated distance (Km)")
        chart.set_ylabel("Speed (Km/h)")

        # Clean elevation grade data
        summarized_df = df[["KM", "Elevation Gain", "Distance"]].rolling(20).mean()
        grade_threshold = 0.5
        while len(summarized_df[abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]) > grade_threshold]) < 15:
            grade_threshold = grade_threshold - 0.02 
        cleaned_df = summarized_df[abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]) < grade_threshold]
        
        
        ax2 = chart.twinx()
        ax2.plot(cleaned_df["KM"], 100*cleaned_df["Elevation Gain"]/cleaned_df["Distance"], 
                 color="#334455", label="Grade")
        ax2.set_ylabel("Grade")
        ax2.legend(loc="upper right")

        self._speed_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)
        plot.figure.canvas.draw()

    def plotDistanceOverTime(self, chart, df):
        plot, = chart.plot(df["Tot. Time"].dt.total_seconds()/60, df["KM"])
        chart.set_xlabel("Time (minutes)")
        chart.set_ylabel("Distance (Km)")
        chart.grid(color = 'green', linestyle = '--', linewidth = 0.5)
        self._distance_time_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)
        plot.figure.canvas.draw()

    def plotElevationOverDistance(self, chart, df):
        plot, = chart.plot(df["KM"], df["Elevation"])
        chart.set_xlabel("Distance (Km)")
        chart.set_ylabel("Elevation (m)")
        self._elevation_distance_chart_canvas.figure.subplots_adjust(bottom=0.15)
        chart.fill_between(df["KM"], df["Elevation"])
        plot.figure.canvas.draw()

    def initializeCharts(self, df):
        self._speed_chart = self._speed_chart_canvas.figure.subplots()
        self.plotSpeed(self._speed_chart, df)
        
        self._distance_time_chart = self._distance_time_chart_canvas.figure.subplots()
        self.plotDistanceOverTime(self._distance_time_chart, df)
        
        self._elevation_distance_chart = self._elevation_distance_chart_canvas.figure.subplots()
        self.plotElevationOverDistance(self._elevation_distance_chart, df)


