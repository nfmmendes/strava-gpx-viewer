import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from gpx_processor import getDataFrameFromGpxFile
from gpx_processor import calculateSpeedDataFrame

### For embedding in Qt
from matplotlib.backends.qt_compat import QtWidgets
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QFileDialog, QGridLayout
from chart_dashboard import ChartDashboard

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

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

        self._dashboard = ChartDashboard()

        layout.addWidget(self._open_file_button)
        layout.addLayout(stats_grid_layout) 
        layout.addWidget(self._dashboard) 
        self.showMaximized()

    def openFileDialog(self):
        fname = QFileDialog.getOpenFileName(self,"Open File", "",
                                            "GPX Files (*.gpx)",)

        if len(fname) > 1: 
            df = getDataFrameFromGpxFile(fname[0])
            calculateSpeedDataFrame(df)
            self.initializeStats(df)
            self._dashboard.initializeCharts(df)

    def initializeStats(self, df):
        self._total_distance_label.setText(str(round(df.iloc[-1]["Tot. Distance"]/1000,2)))
        self._total_time_label.setText(str(df.iloc[-1]["Tot. Time"]))
        self._average_speed_label.setText(str(round(df.iloc[-1]["Avg Speed"], 2)))
        self._total_elevation_label.setText(str(round(df[df["Elevation Gain"] > 0]["Elevation Gain"].sum(),2)))
        QApplication.processEvents()
