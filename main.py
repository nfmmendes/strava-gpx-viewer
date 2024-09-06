import gpxpy
import gpxpy.gpx
import math
from geopy import distance
import pandas as pd

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
            speed = 3.6*dist/gap if gap > 0 else 0
            accumulated_distance += dist
            accumulated_time = time - first_time
            avg_speed = 3.6*accumulated_distance/accumulated_time.seconds if accumulated_time.seconds > 0 else 0
            rows.append([time, lat, long, elevation, dist, gap, speed, avg_speed, accumulated_distance, accumulated_time])
            previous = point

df = pd.DataFrame(columns=["Time", "Latitude", "Longitude", "Elevation", "Distance", "Delta time", "Speed", "Avg Speed", "Tot Distance", "Tot. Time"], data = rows)
df["KM"] = (df["Tot Distance"]/100).astype(int)/10
df = df.groupby(["KM"],as_index=False).last()
print(df[["KM", "Tot Distance", "Tot. Time", "Speed", "Avg Speed"]])
