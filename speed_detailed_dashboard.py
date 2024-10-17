import numpy as np
import pandas as pd

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout

class SpeedDetailedDashboard(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        layout = QVBoxLayout(self)
        self._redraw = False

        new_df = data_frame[["Elevation Gain", "Distance", "Delta Time"]]
        new_df["Speed"] = np.where(new_df["Delta Time"] > 0, 3.6*new_df["Distance"]/new_df["Delta Time"], 0)

        self._speed_grade_canvas = FigureCanvas(Figure(figsize=(4,3.2)))

        layout.addWidget(self._speed_grade_canvas)

        chart = self._speed_grade_canvas.figure.subplots()
        chart.scatter(100*new_df["Elevation Gain"]/new_df["Distance"], new_df["Speed"])
        chart.set_xlabel("Grade (%)")
        chart.set_ylabel("Speed (Km/h)")


