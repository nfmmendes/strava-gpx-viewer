import threading
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QGridLayout

class SpeedDetailedDashboard(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        layout = QGridLayout(self)
        self._redraw = False
       
        self._tick_label_size = 8

        new_df = data_frame[["Elevation Gain", "Distance", "Delta Time"]].copy(deep = True)
        new_df["Speed"] = np.where(new_df["Delta Time"] > 0, 3.6*new_df["Distance"]/new_df["Delta Time"], 0)
        new_df["Grade"] = 100*new_df["Elevation Gain"]/new_df["Distance"]

        new_df = self._filter_data(new_df)

        canvas_factory = lambda w, h : FigureCanvas(Figure(figsize = (6,2.5)))

        self._speed_grade_canvas = canvas_factory(6, 2.5)
        self._speed_frequence_canvas = canvas_factory(6, 2.5)
        self._speed_elevation_grade_canvas = canvas_factory(6, 3)
        self._speed_over_time_canvas = canvas_factory(4, 6)
        self._speed_over_distance_canvas = canvas_factory(4, 6)
        
        layout.addWidget(self._speed_grade_canvas, 0, 0)
        layout.addWidget(self._speed_elevation_grade_canvas, 0, 1)
        layout.addWidget(self._speed_frequence_canvas, 1, 0, 1, 2)
        layout.addWidget(self._speed_over_time_canvas, 2, 0, 1, 2)
        layout.addWidget(self._speed_over_distance_canvas, 3, 0, 1, 2)
        layout.setRowStretch(0, 10)
        layout.setRowStretch(1, 8)
        layout.setRowStretch(2, 8)
        layout.setRowStretch(3, 8)
        
        new_df["Pos Elevation Gain"] = [ 0 if x < 0 else x for x in new_df["Elevation Gain"]]
        new_df["Grade_X_Elevation"] = new_df["Grade"]*new_df["Pos Elevation Gain"].cumsum()/100
        
        chart_grade = self._speed_grade_canvas.figure.subplots()
        chart_elevation = self._speed_elevation_grade_canvas.figure.subplots()
        
        self._render_interval_charts(self._define_speed_cuts(new_df))
        self._render_speed_frequence_chart(new_df)

        t1 = threading.Thread(target = self._render_density_chart, args = [chart_grade, new_df["Grade"], new_df["Speed"]])
        t2 = threading.Thread(target = self._render_density_chart, args = [chart_elevation, new_df["Grade_X_Elevation"], new_df["Speed"]])
 
        chart_grade.set_xlabel("Grade (%)")
        chart_grade.set_ylabel("Speed (Km/h)")
        chart_grade.tick_params(axis='x', which='major', labelsize=self._tick_label_size)
        self._speed_grade_canvas.figure.subplots_adjust(bottom=0.18, hspace=0.2)

        chart_elevation.set_xlabel("Grade X Accumulated Elevation Gain (m)")
        chart_elevation.set_ylabel("Speed (Km/h)")
        chart_elevation.tick_params(axis='x', which='major', labelsize= self._tick_label_size)
        self._speed_elevation_grade_canvas.figure.subplots_adjust(bottom=0.18)

        t1.start()
        t2.start()


    def _render_speed_frequence_chart(self, new_df):
        chart = self._speed_frequence_canvas.figure.subplots()

        count_series = round(new_df['Speed'], 1).value_counts()
        count_series = count_series[count_series > 10]

        chart.bar(x = count_series.index, height = count_series.values, width=0.1)
        chart.set_xlabel("Speed")
        chart.set_ylabel("Frequence")
        self._speed_frequence_canvas.figure.subplots_adjust(bottom=0.25)


    def _render_interval_charts(self, new_df):
        
        chart = self._speed_over_time_canvas.figure.subplots()
        chart.bar([f"[{x.left} , {x.right})" for x in new_df.index] , new_df["Delta Time"]/60)
        chart.set_xlabel("Speed intervals (Km/h)")
        chart.set_ylabel("Time (m)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.margins(y = 0.3)
        chart.tick_params(axis='x', which='major', labelsize= self._tick_label_size)
        self._speed_over_time_canvas.figure.subplots_adjust(bottom=0.25)

        chart = self._speed_over_distance_canvas.figure.subplots()
        chart.bar([f"[{x.left} , {x.right})" for x in new_df.index] , new_df["Distance"]/1000)
        chart.set_xlabel("Speed intervals (Km/h)")
        chart.set_ylabel("Distance (Km)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.margins(y = 0.3)
        chart.tick_params(axis='x', which='major', labelsize= self._tick_label_size)
        self._speed_over_distance_canvas.figure.subplots_adjust(bottom=0.25, hspace=0.25)       
            
    def _define_speed_cuts(self, df):
        intervals = np.arange(10, 50.00001, 5)
        intervals = np.append(0, intervals)
        intervals = np.append(intervals, np.arange(50.0001, 100, 10))
        intervals = np.append(intervals, np.array([np.inf]))
        cuts = pd.cut(df["Speed"], intervals)
        return df[["Distance", "Delta Time"]].copy(deep= True).groupby(cuts, observed = True).sum()


    def _filter_data(self, df):
        zero_quantile, quantile_995 = df["Speed"].quantile([0.0, 0.995])
        new_df = df[df["Speed"].between(zero_quantile, quantile_995)]

        quantile_005, quantile_995 = new_df["Grade"].quantile([0.001, 0.995])
        new_df = new_df[new_df["Grade"].between(quantile_005, quantile_995)]

        return new_df

    def _render_density_chart(self, chart, col_x, col_y):
        xy = np.vstack([col_x, col_y])
        z = gaussian_kde(xy)(xy)
        
        chart.scatter(col_x, col_y, c = z, s = 3)
        chart.get_figure().canvas.draw()
