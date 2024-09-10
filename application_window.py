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

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        df = getDataFrameFromGpxFile()
        calculateSpeedDataFrame(df)

        summarized_df = df.groupby(["KM"],as_index=False).last()
        #print(summarized_df[["KM", "Tot. Distance", "Tot. Time", "Speed", "Avg Speed"]])

        speed_chart_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        layout.addWidget(NavigationToolbar(speed_chart_canvas, self))
        layout.addWidget(speed_chart_canvas)
  
        self._speed_chart = speed_chart_canvas.figure.subplots()
        self.plotSpeed(self._speed_chart, df)


        distance_time_chart_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        layout.addWidget(NavigationToolbar(distance_time_chart_canvas, self))
        layout.addWidget(distance_time_chart_canvas)
  
        self._distance_time_chart = distance_time_chart_canvas.figure.subplots()
        self.plotDistanceOverTime(self._distance_time_chart, df)


    def plotSpeed(self, chart, df):
        chart.plot(df["KM"], df["Avg Speed"], label="Average speed")
        chart.plot(df["KM"], df["Speed ma"], label="Instantaneous speed")
        chart.legend(loc="upper left")
        chart.set_xlabel("Accumulated distance")
        chart.set_ylabel("Km/h")

    def plotDistanceOverTime(self, chart, df):
        chart.plot(df["Tot. Time"].dt.total_seconds()/60, df["KM"])
        chart.set_xlabel("Time")
        chart.set_ylabel("Distance")


