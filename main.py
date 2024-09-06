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

for track in gpx.tracks:
    for segment in track.segments:
        if len(segment.points) == 0:
            continue
        previous = segment.points[0]
        for point in segment.points:
            lat, long, elevation, time = point.latitude, point.longitude, point.elevation, point.time
            dist = round(calculateDistance(previous, point), 5)
            gap = (time - previous.time).seconds
            speed = 3.6*dist/gap if gap > 0 else 0
            rows.append([time, lat, long, elevation, dist, gap, speed])
            print(f'Coord: ({lat},{long})\t Elevation: {elevation} \t Time: {time.strftime("%H:%M:%S")} \t Time Gap {gap} seconds \t Distance {dist} meters \t Speed {speed}')
            previous = point

df = pd.DataFrame(columns=["Time", "Latitude", "Longitude", "Elevation", "Distance", "Delta time", "Speed"], data = rows)
