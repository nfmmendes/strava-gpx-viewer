import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout

class SpeedDetailedDashboard(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        layout = QVBoxLayout(self)
        self._redraw = False

        new_df = data_frame[["Elevation Gain", "Distance", "Delta Time"]].copy(deep = True)
        new_df["Speed"] = np.where(new_df["Delta Time"] > 0, 3.6*new_df["Distance"]/new_df["Delta Time"], 0)

        zero_quantile, quantile_999 = new_df["Speed"].quantile([0.0, 0.999])
        new_df = new_df[new_df["Speed"].between(zero_quantile, quantile_999)]

        new_df["Grade"] = 100*new_df["Elevation Gain"]/new_df["Distance"]
        quantile_001, quantile_999 = new_df["Grade"].quantile([0.001, 0.999])
        new_df = new_df[new_df["Grade"].between(quantile_001, quantile_999)]

        self._speed_grade_canvas = FigureCanvas(Figure(figsize = (4,3.2)))
        self._speed_elevation_grade_canvas = FigureCanvas(Figure(figsize = (4, 3.2)))
        
        layout.addWidget(self._speed_grade_canvas)
        layout.addWidget(self._speed_elevation_grade_canvas)

        xy = np.vstack([new_df["Grade"],new_df["Speed"]])
        z = gaussian_kde(xy)(xy)

        chart = self._speed_grade_canvas.figure.subplots()
        chart.scatter(new_df["Grade"], new_df["Speed"], c=z, s=10)
        chart.set_xlabel("Grade (%)")
        chart.set_ylabel("Speed (Km/h)")

        new_df["Pos Elevation Gain"] = [ 0 if x < 0 else x for x in new_df["Elevation Gain"]]
        new_df["Tot. Elevation Gain"] =  new_df["Pos Elevation Gain"].cumsum()
        new_df["Grade Mult. Elevation"] = new_df["Grade"]*new_df["Tot. Elevation Gain"]/100
        
        xy = np.vstack([new_df["Grade Mult. Elevation"], new_df["Speed"]])
        z = gaussian_kde(xy)(xy)
 

        chart = self._speed_elevation_grade_canvas.figure.subplots()
        chart.scatter(new_df["Grade Mult. Elevation"], new_df["Speed"], c = z, s = 10)
        chart.set_xlabel("Grade X Total Elevation Gain (m)")
        chart.set_ylabel("Speed (Km/h)")

