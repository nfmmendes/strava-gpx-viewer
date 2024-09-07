import gpxpy
import gpxpy.gpx
import math
from geopy import distance
import pandas as pd
import numpy as np

def calculateDistance(a, b):
    p1 = (a.latitude, a.longitude, a.elevation)
    p2 = (b.latitude, b.longitude, b.elevation)

    flat_distance = distance.distance(p1[:2], p2[:2]).m

    return math.sqrt(flat_distance**2 + (p2[2] - p1[2])**2)

# Parsing an existing file:
# -------------------------

gpx_file = open('test.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

rows = []

def getDataFrameFromGpxFile(): 

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
    
df = getDataFrameFromGpxFile()

toSeconds = lambda timeDelta: timeDelta.dt.total_seconds()

print(df["Tot. Time"].dtype)
df["Speed"] = np.where(df["Delta Time"] > 0, 3.6*df["Distance"]/df["Delta Time"], 0)
df["Avg Speed"] = np.where(toSeconds(df["Tot. Time"]) > 0, 3.6*df["Tot. Distance"]/toSeconds(df["Tot. Time"]), 0)
df["KM"] = (df["Tot. Distance"]/100).astype(int)/10

df = df.groupby(["KM"],as_index=False).last()
print(df[["KM", "Tot. Distance", "Tot. Time", "Speed", "Avg Speed"]])
