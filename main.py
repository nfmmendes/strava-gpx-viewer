import gpxpy
import gpxpy.gpx

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
                print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevation} on time {point.time}. Previous measurement {(point.time - previous.time).seconds} seconds ago')
                previous = point

for waypoint in gpx.waypoints:
    print(f'waypoint {waypoint.name} -> ({waypoint.latitude},{waypoint.longitude})')

for route in gpx.routes:
    print('Route:')
    for point in route.points:
        print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevtion}')
