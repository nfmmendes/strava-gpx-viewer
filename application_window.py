import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from gpx_processor import getDataFrameFromGpxFile
from gpx_processor import calculateSpeedDataFrame

### For embedding in Qt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QFileDialog, QGridLayout

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        #summarized_df = df.groupby(["KM"],as_index=False).last()
        #print(summarized_df[["KM", "Tot. Distance", "Tot. Time", "Speed", "Avg Speed"]])

        self._speed_chart_canvas = FigureCanvas(Figure(figsize=(14, 3.2)))
        self._distance_time_chart_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))
        self._elevation_distance_chart_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))

        self._open_file_button = QPushButton("Open gpx file")
        self._open_file_button.setFixedSize(100, 32)
        self._open_file_button.clicked.connect(self.openFileDialog)

        self._total_distance_label = QLabel("")
        self._total_time_label = QLabel("")
        self._average_speed_label = QLabel("")
        self._total_elevation_label = QLabel("")

        stats_grid_layout = QGridLayout()
        stats_grid_layout.addWidget(QLabel("Total distance: "), 0, 0)
        stats_grid_layout.addWidget(self._total_distance_label, 0, 1)
        stats_grid_layout.addWidget(QLabel("Total time: "), 1, 0)
        stats_grid_layout.addWidget(self._total_time_label, 1, 1)
        stats_grid_layout.addWidget(QLabel("Average speed: "), 2, 0)
        stats_grid_layout.addWidget(self._average_speed_label, 2, 1)
        stats_grid_layout.addWidget(QLabel("Elevation: "), 3, 0)
        stats_grid_layout.addWidget(self._total_elevation_label, 3, 1)

        bottom_charts = QtWidgets.QGridLayout()
        bottom_charts.addWidget(NavigationToolbar(self._elevation_distance_chart_canvas, self), 0, 0) 
        bottom_charts.addWidget(self._elevation_distance_chart_canvas, 1, 0)
        bottom_charts.addWidget(NavigationToolbar(self._distance_time_chart_canvas, self), 0, 1)
        bottom_charts.addWidget(self._distance_time_chart_canvas, 1, 1)
        
        layout.addWidget(self._open_file_button)
        layout.addLayout(stats_grid_layout) 
        layout.addWidget(NavigationToolbar(self._speed_chart_canvas, self))
        layout.addWidget(self._speed_chart_canvas)
        layout.addLayout(bottom_charts) 
        self.showMaximized()

    def openFileDialog(self):
        fname = QFileDialog.getOpenFileName(self,"Open File", "",
                                            "GPX Files (*.gpx)",)

        if len(fname) > 1: 
            df = getDataFrameFromGpxFile(fname[0])
            calculateSpeedDataFrame(df)
            self.initializeStats(df)
            self.initializeCharts(df)

    def initializeStats(self, df):
        self._total_distance_label.setText(str(round(df.iloc[-1]["Tot. Distance"]/1000,2)))
        self._total_time_label.setText(str(df.iloc[-1]["Tot. Time"]))
        self._average_speed_label.setText(str(round(df.iloc[-1]["Avg Speed"], 2)))
        self._total_elevation_label.setText(str(round(df[df["Elevation Gain"] > 0]["Elevation Gain"].sum(),2)))
        QApplication.processEvents()

    def plotSpeed(self, chart, df):
        chart.plot(df["KM"], df["Avg Speed"], label="Average speed")
        plot, = chart.plot(df["KM"], df["Speed ma"], label="Instantaneous speed")
        chart.legend(loc="lower left")
        chart.set_xlabel("Accumulated distance")
        chart.set_ylabel("Km/h")

        # Clean elevation grade data
        summarized_df = df[["KM", "Elevation Gain", "Distance"]].rolling(20).mean()
        grade_threshold = 0.5
        while len(summarized_df[abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]) > grade_threshold]) < 15:
            grade_threshold = grade_threshold - 0.02 
        cleaned_df = summarized_df[abs(summarized_df["Elevation Gain"]/summarized_df["Distance"]) < grade_threshold]
        
        
        ax2 = chart.twinx()
        ax2.plot(cleaned_df["KM"], 100*cleaned_df["Elevation Gain"]/cleaned_df["Distance"], color="#334455")
        ax2.set_ylabel("Grade")
        ax2.legend(["Grade %"], loc="upper right")

        self._speed_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)
        plot.figure.canvas.draw()

    def plotDistanceOverTime(self, chart, df):
        plot, = chart.plot(df["Tot. Time"].dt.total_seconds()/60, df["KM"])
        chart.set_xlabel("Time")
        chart.set_ylabel("Distance")
        self._distance_time_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)
        plot.figure.canvas.draw()

    def plotElevationOverDistance(self, chart, df):
        plot, = chart.plot(df["KM"], df["Elevation"])
        chart.set_xlabel("Distance")
        chart.set_ylabel("Elevation")
        self._elevation_distance_chart_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)
        plot.figure.canvas.draw()

    def initializeCharts(self, df):
        self._speed_chart = self._speed_chart_canvas.figure.subplots()
        self.plotSpeed(self._speed_chart, df)
        
        self._distance_time_chart = self._distance_time_chart_canvas.figure.subplots()
        self.plotDistanceOverTime(self._distance_time_chart, df)
        
        self._elevation_distance_chart = self._elevation_distance_chart_canvas.figure.subplots()
        self.plotElevationOverDistance(self._elevation_distance_chart, df)




