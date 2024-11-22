import gpxpy
import gpxpy.gpx
import math
from geopy import distance
import pandas as pd
import numpy as np

"""
Calculate the geodesic distance between two points based in their
coordinates. 
"""
def calculate_distance(a, b):
    p1 = (a.latitude, a.longitude, a.elevation)
    p2 = (b.latitude, b.longitude, b.elevation)

    flat_distance = distance.distance(p1[:2], p2[:2]).m

    return math.sqrt(flat_distance**2 + (p2[2] - p1[2])**2)

"""
Read the data from a gpx file and use it to fill a pandas dataframe.
"""
def get_data_frame_from_gpx_file(file_name): 
    
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
                dist = round(calculate_distance(previous, point), 5)
                accumulated_distance += dist        
                accumulated_time = time - first_time
                rows.append([time, lat, long, elevation, dist, accumulated_distance, accumulated_time])
                previous = point
            
    df = pd.DataFrame(columns=["Time", "Latitude", "Longitude", "Elevation", "Distance", "Tot. Distance", "Tot. Time"], data=rows)
    df["Delta Time"] = df["Time"].diff().dt.total_seconds()
    df.at[0, "Delta Time"] = 0
    df["Elevation Gain"] = df["Elevation"].diff()
    df.at[0, "Elevation Gain"] = 0

    return df

"""
Calculate the instantaneous speed on each measurement. 
"""
def calculate_speed_data_frame(df):

    toSeconds = lambda timeDelta: timeDelta.dt.total_seconds()
    speedEval = lambda time, distance : np.where(time > 0, 3.6*distance/time, 0)
    df["Delta Time"] = toSeconds(df["Time"].diff())
    df.at[0, "Delta Time"] = 0
    df["Elevation Gain"] = df["Elevation"].diff()
    df.at[0, "Elevation Gain"] = 0
    df["Speed"] = speedEval(df["Delta Time"], df["Distance"])
    df["Speed rollmean"] = df["Speed"].rolling(20).mean()
    df["Avg Speed"] = speedEval(toSeconds(df["Tot. Time"]), df["Tot. Distance"])
    df["KM"] = (df["Tot. Distance"]/100).astype(int)/10

