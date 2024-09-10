import gpxpy
import gpxpy.gpx
import math
from geopy import distance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys


### For embedding in Qt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure

def calculateDistance(a, b):
    p1 = (a.latitude, a.longitude, a.elevation)
    p2 = (b.latitude, b.longitude, b.elevation)

    flat_distance = distance.distance(p1[:2], p2[:2]).m

    return math.sqrt(flat_distance**2 + (p2[2] - p1[2])**2)



# Parsing an existing file:
# -------------------------

def getDataFrameFromGpxFile(): 
    
    gpx_file = open('test.gpx', 'r')
    gpx = gpxpy.parse(gpx_file)
    rows = []
    accumulated_distance = 0
    
    for track in gpx.tracks:
        for segment in track.segments:
            if len(segment.points) == 0:
                continue
            previous = segment.points[0]
            first_time = segment.points[0].time
            for point in segment.points:
                lat, long, elevation, time = point.latitude, point.longitude, point.elevation, point.time
                dist = round(calculateDistance(previous, point), 5)
                gap = (time - previous.time).seconds
                accumulated_distance += dist        
                accumulated_time = time - first_time
                rows.append([time, lat, long, elevation, dist, gap, accumulated_distance, accumulated_time])
                previous = point
            
    return pd.DataFrame(columns=["Time", "Latitude", "Longitude", "Elevation", "Distance", "Delta Time", "Tot. Distance", "Tot. Time"], data=rows)

def calculateSpeedDataFrame(df):

    toSeconds = lambda timeDelta: timeDelta.dt.total_seconds()

    df["Speed"] = np.where(df["Delta Time"] > 0, 3.6*df["Distance"]/df["Delta Time"], 0)
    df["Speed ma"] = df["Speed"].rolling(20).mean()
    df["Avg Speed"] = np.where(toSeconds(df["Tot. Time"]) > 0, 3.6*df["Tot. Distance"]/toSeconds(df["Tot. Time"]), 0)
    df["KM"] = (df["Tot. Distance"]/100).astype(int)/10


df = getDataFrameFromGpxFile()
calculateSpeedDataFrame(df)

summarized_df = df.groupby(["KM"],as_index=False).last()
print(summarized_df[["KM", "Tot. Distance", "Tot. Time", "Speed", "Avg Speed"]])

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

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


