import folium
import io
import PyQt6.QtWebEngineWidgets as qtweb

class MapViewer:

    def __init__(self):
        pass

    def show_marker(self, lat, long):
        m = folium.Map(location=[lat, long], zoom_start=13)
        
        folium.Marker(location=[lat, long]).add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)

        self._web_viewer = qtweb.QWebEngineView()
        self._web_viewer.setHtml(data.getvalue().decode())
        self._web_viewer.resize(640, 480)
        self._web_viewer.show()

    def show_poly_line(self, points, zoom = 15):
        half = int(len(points)/2)
        self._map = folium.Map(
                location=[points[half][0], points[half][1]], zoom_start= zoom
        )
        folium.PolyLine(points, color='red', weight=4.5, opacity=.5).add_to(self._map)

        data = io.BytesIO()
        self._map.save(data, close_file=False)

        self._web_viewer = qtweb.QWebEngineView()
        self._web_viewer.setHtml(data.getvalue().decode())
        self._web_viewer.resize(800, 640)
        self._web_viewer.show()
