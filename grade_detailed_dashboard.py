import numpy as np
import pandas as pd

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget

class GradeDetailedDashboard(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self._redraw = False

        self._tick_label_size = 8

        ## Setup layout
        canvas_factory = lambda w, h : FigureCanvas(Figure(figsize = (6,2.5)))

        self._grade_frequence_canvas = canvas_factory(4, 3.2)
        self._speed_grade_canvas = canvas_factory(4,3.2)
        self._distance_grade_canvas = canvas_factory(4, 3.2)
        self._time_grade_canvas = canvas_factory(4, 3.2)

        layout.addWidget(self._grade_frequence_canvas)
        layout.addWidget(self._speed_grade_canvas)
        layout.addWidget(self._distance_grade_canvas)
        layout.addWidget(self._time_grade_canvas)

        self.setLayout(layout)
        
        self._create_charts(data_frame)

        self._grade_frequence_canvas.figure.subplots_adjust(bottom=0.25, hspace=0.2)
        self._speed_grade_canvas.figure.subplots_adjust(bottom=0.25, hspace=0.2)
        self._distance_grade_canvas.figure.subplots_adjust(bottom=0.25, hspace=0.2)
        self._time_grade_canvas.figure.subplots_adjust(bottom=0.25, hspace=0.2)

    def _process_data(self, data_frame): 
        ## Process data
        intervals = np.arange(-10, 10.00001, 2)
        intervals = np.append(np.array([-np.inf]), intervals)
        intervals = np.append(intervals, np.array([np.inf]))
        cuts = pd.cut(100*data_frame["Elevation Gain"]/data_frame["Distance"], intervals)
        
        new_data = data_frame[["Elevation Gain", "Distance", "Delta Time"]].groupby(cuts, observed = True).sum()
        new_data["Speed"] = np.where(new_data["Delta Time"] > 0, 3.6*new_data["Distance"]/new_data["Delta Time"], 0)
        new_data = new_data[new_data["Distance"] > 0]

        return new_data

    def _create_charts(self, df):
        processed_df = self._process_data(df)

        chart = self._grade_frequence_canvas.figure.subplots()
        count_series = round(100*df["Elevation Gain"]/df["Distance"], 1).value_counts()
        count_series = count_series[count_series > 10]
        chart.bar(x = count_series.index, height = count_series.values, width=0.1)
        chart.set_xlabel("Grade")
        chart.set_ylabel("Frequence")
        self._grade_frequence_canvas.figure.subplots_adjust(bottom=0.25)

        interval_label = lambda x : f"[{x.left:.0f} , {x.right:.0f})"
        chart = self._speed_grade_canvas.figure.subplots()
        chart.bar([interval_label(x) for x in processed_df.index] , processed_df["Speed"])
        chart.set_xlabel("Grade intervals (%)")
        chart.set_ylabel("Speed (Km/h)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.tick_params(axis='x', which='major', labelsize= self._tick_label_size)
        chart.margins(y = 0.3)

        chart = self._distance_grade_canvas.figure.subplots()
        chart.bar([interval_label(x) for x in processed_df.index] , processed_df["Distance"]/1000)
        chart.set_xlabel("Grade intervals (%)")
        chart.set_ylabel("Distance (Km)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.tick_params(axis='x', which='major', labelsize= self._tick_label_size)
        chart.margins(y = 0.2)

        chart = self._time_grade_canvas.figure.subplots()
        chart.bar([interval_label(x) for x in processed_df.index] , processed_df["Delta Time"]/60)
        chart.set_xlabel("Grade intervals (%)")
        chart.set_ylabel("Time (min)")
        chart.bar_label(chart.containers[0], fmt='%.2f')
        chart.tick_params(axis='x', which='major', labelsize= self._tick_label_size)
        chart.margins(y = 0.2)



