import gpxpy
import gpxpy.gpx
import math
from geopy import distance

def calculateDistance(a, b):
    p1 = (a.latitude, a.longitude, a.elevation)
    p2 = (b.latitude, b.longitude, b.elevation)

    flat_distance = distance.distance(p1[:2], p2[:2]).m

    return math.sqrt(flat_distance**2 + (p2[2] - p1[2])**2)

# Parsing an existing file:
# -------------------------

gpx_file = open('test.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
        if len(segment.points) == 0:
            continue
        previous = segment.points[0]
        for point in segment.points:
            print(f'Coord: ({point.latitude},{point.longitude})\t Elevation: {point.elevation} \t Time: {point.time.strftime("%H:%M:%S")} \t Time Gap {(point.time - previous.time).seconds} seconds \t Distance {round(calculateDistance(previous, point),2)} meters')
            previous = point

for waypoint in gpx.waypoints:
    print(f'waypoint {waypoint.name} -> ({waypoint.latitude},{waypoint.longitude})')

for route in gpx.routes:
    print('Route:')
    for point in route.points:
        print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevtion}')
