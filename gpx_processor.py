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

def getDataFrameFromGpxFile(file_name): 
    
    gpx_file = open(file_name, 'r')
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
                accumulated_distance += dist        
                accumulated_time = time - first_time
                rows.append([time, lat, long, elevation, dist, accumulated_distance, accumulated_time])
                previous = point
            
    return pd.DataFrame(columns=["Time", "Latitude", "Longitude", "Elevation", "Distance", "Tot. Distance", "Tot. Time"], data=rows)

def calculateSpeedDataFrame(df):

    toSeconds = lambda timeDelta: timeDelta.dt.total_seconds()
    df["Delta Time"] = toSeconds(df["Time"].diff())
    df.at[0, "Delta Time"] = 0
    df["Elevation Gain"] = df["Elevation"].diff()
    df.at[0, "Elevation Gain"] = 0
    df["Speed"] = np.where(df["Delta Time"] > 0, 3.6*df["Distance"]/df["Delta Time"], 0)
    df["Speed ma"] = df["Speed"].rolling(20).mean()
    df["Avg Speed"] = np.where(toSeconds(df["Tot. Time"]) > 0, 3.6*df["Tot. Distance"]/toSeconds(df["Tot. Time"]), 0)
    df["KM"] = (df["Tot. Distance"]/100).astype(int)/10

