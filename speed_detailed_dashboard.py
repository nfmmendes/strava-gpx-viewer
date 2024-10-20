import threading
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout

class SpeedDetailedDashboard(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        layout = QGridLayout(self)
        self._redraw = False
        
        new_df = data_frame[["Elevation Gain", "Distance", "Delta Time"]].copy(deep = True)
        new_df["Speed"] = np.where(new_df["Delta Time"] > 0, 3.6*new_df["Distance"]/new_df["Delta Time"], 0)
        new_df["Grade"] = 100*new_df["Elevation Gain"]/new_df["Distance"]

        new_df = self._filter_data(new_df)

        self._speed_grade_canvas = FigureCanvas(Figure(figsize = (6,3)))
        self._speed_elevation_grade_canvas = FigureCanvas(Figure(figsize = (6, 3)))
        self._speed_over_time_canvas = FigureCanvas(Figure(figsize = (4, 6)))
        self._speed_over_distance_canvas = FigureCanvas(Figure(figsize = (4, 6)))
        
        layout.addWidget(self._speed_grade_canvas, 0, 0)
        layout.addWidget(self._speed_elevation_grade_canvas, 0, 1)
        layout.addWidget(self._speed_over_time_canvas, 1, 0, 1, 2)
        layout.addWidget(self._speed_over_distance_canvas, 2, 0, 1, 2)
        layout.setRowStretch(0, 10)
        layout.setRowStretch(1, 8)
        layout.setRowStretch(2, 8)
        
        new_df["Pos Elevation Gain"] = [ 0 if x < 0 else x for x in new_df["Elevation Gain"]]
        new_df["Grade_X_Elevation"] = new_df["Grade"]*new_df["Pos Elevation Gain"].cumsum()/100
        
        chart_grade = self._speed_grade_canvas.figure.subplots()
        chart_elevation = self._speed_elevation_grade_canvas.figure.subplots()

        t1 = threading.Thread(target = self._render_density_chart, args = [chart_grade, new_df["Grade"], new_df["Speed"]])
        t2 = threading.Thread(target = self._render_density_chart, args = [chart_elevation, new_df["Grade_X_Elevation"], new_df["Speed"]])

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        chart_grade.set_xlabel("Grade (%)")
        chart_grade.set_ylabel("Speed (Km/h)")
        self._speed_grade_canvas.figure.subplots_adjust(bottom=0.15, hspace=0.2)

        chart_elevation.set_xlabel("Grade X Total Elevation Gain (m)")
        chart_elevation.set_ylabel("Speed (Km/h)")
        self._speed_elevation_grade_canvas.figure.subplots_adjust(bottom=0.15)

        new_df = self._define_speed_cuts(new_df)

        chart = self._speed_over_time_canvas.figure.subplots()
        chart.bar([f"[{x.left},{x.right})" for x in new_df.index] , new_df["Delta Time"]/60)
        chart.set_xlabel("Speed intervals (Km/h)")
        chart.set_ylabel("Time (m)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.margins(y = 0.3)
        self._speed_over_time_canvas.figure.subplots_adjust(bottom=0.2)

        chart = self._speed_over_distance_canvas.figure.subplots()
        chart.bar([f"[{x.left},{x.right})" for x in new_df.index] , new_df["Distance"]/1000)
        chart.set_xlabel("Speed intervals (Km/h)")
        chart.set_ylabel("Distance (Km)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.margins(y = 0.3)
        self._speed_over_distance_canvas.figure.subplots_adjust(bottom=0.2, hspace=0.2)
            
    def _define_speed_cuts(self, new_df):
        intervals = np.arange(10, 50.00001, 5)
        intervals = np.append(0, intervals)
        intervals = np.append(intervals, np.arange(50.0001, 100, 10))
        intervals = np.append(intervals, np.array([np.inf]))
        cuts = pd.cut(new_df["Speed"], intervals)
        new_df = new_df[["Distance", "Delta Time"]].groupby(cuts, observed = True).sum()

        return new_df


    def _filter_data(self, df):
        zero_quantile, quantile_995 = df["Speed"].quantile([0.0, 0.995])
        new_df = df[df["Speed"].between(zero_quantile, quantile_995)]

       
        quantile_005, quantile_995 = new_df["Grade"].quantile([0.001, 0.995])
        new_df = new_df[new_df["Grade"].between(quantile_005, quantile_995)]

        return new_df

    def _render_density_chart(self, chart, col_x, col_y):
        xy = np.vstack([col_x, col_y])
        z = gaussian_kde(xy)(xy)
        
        chart.scatter(col_x, col_y, c = z, s = 10)

