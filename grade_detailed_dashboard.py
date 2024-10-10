import numpy as np
import pandas as pd

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout

class GradeDetailedDashboard(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self._redraw = False

        ## Process data
        intervals = np.arange(-10, 10.00001, 2)
        intervals = np.append(np.array([-np.inf]), intervals)
        intervals = np.append(intervals, np.array([np.inf]))
        cuts = pd.cut(100*data_frame["Elevation Gain"]/data_frame["Distance"], intervals)
        
        new_chart = data_frame[["Elevation Gain", "Distance", "Delta Time"]].groupby(cuts).sum()
        new_chart["Speed"] = np.where(new_chart["Delta Time"] > 0, 3.6*new_chart["Distance"]/new_chart["Delta Time"], 0)
        new_chart = new_chart[new_chart["Distance"] > 0]

        ## Define the layout
        self._speed_grade_canvas = FigureCanvas(Figure(figsize=(4,3.2)))
        self._distance_grade_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))
        self._time_grade_canvas = FigureCanvas(Figure(figsize=(4, 3.2)))

        self.resize(800, 800)
        layout.addWidget(self._speed_grade_canvas)
        layout.addWidget(self._distance_grade_canvas)
        layout.addWidget(self._time_grade_canvas)

        self.setLayout(layout)

        ## Create charts
        chart = self._speed_grade_canvas.figure.subplots()
        chart.bar([f"[{x.left}%,{x.right}%)" for x in new_chart.index] , new_chart["Speed"])
        chart.set_xlabel("Grade intervals")
        chart.set_ylabel("Speed (Km/h)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.margins(y = 0.3)

        chart = self._distance_grade_canvas.figure.subplots()
        chart.bar([f"[{x.left}%,{x.right}%)" for x in new_chart.index] , new_chart["Distance"]/1000)
        chart.set_xlabel("Grade intervals")
        chart.set_ylabel("Distance (Km)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.margins(y = 0.2)

        chart = self._time_grade_canvas.figure.subplots()
        chart.bar([f"[{x.left}%,{x.right}%)" for x in new_chart.index] , new_chart["Delta Time"]/60)
        chart.set_xlabel("Grade intervals")
        chart.set_ylabel("Time (min)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.margins(y = 0.2)

        self._speed_grade_canvas.figure.subplots_adjust(bottom=0.2, hspace=0.2)
        self._distance_grade_canvas.figure.subplots_adjust(bottom=0.2, hspace=0.2)
        self._time_grade_canvas.figure.subplots_adjust(bottom=0.2, hspace=0.2)



