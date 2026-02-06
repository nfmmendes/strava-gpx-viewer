import folium
import io
import PyQt6.QtWebEngineWidgets as qtweb
from folium.features import DivIcon

class MapViewer:

    def __init__(self):
        """
        Class constructor
        
        """
        pass

    def show_marker(self, lat: float, long: float) -> None:
        """
        Docstring for show_marker
        
        :param lat: Latitude of the marker.
        :type lat: float
        :param long: Longitude of the marker.
        :type long: float
        :return: None
        :rtype: None
        """
        map = folium.Map(location=[lat, long], zoom_start=13)
        
        folium.Marker(location=[lat, long]).add_to(map)

        data = io.BytesIO()
        map.save(data, close_file=False)

        self._web_viewer = qtweb.QWebEngineView()
        self._web_viewer.setHtml(data.getvalue().decode())
        self._web_viewer.resize(640, 480)
        self._web_viewer.show()

    def show_poly_line(self, points: list[tuple[float, float]], zoom: int = 15) -> None:
        """
        Show a poly line on the map with the given points.
    
        :param points: The points to be shown on the map.
        :type points: list[tuple[float, float]]
        :param zoom: The zoom level of the map.
        :type zoom: int
        :return: None
        :rtype: None
        """
        half = int(len(points)/2)
        self._map = folium.Map(
                location=points[half], zoom_start= zoom
        )
        
        folium.PolyLine(points, color='red', weight=4.5, opacity=.5).add_to(self._map)

        div = lambda text : f'<div style="font-size: 14pt; background-color: white; border-radius:4px; ">{text}</div>'
        icon_start = DivIcon(icon_size=(40,40), icon_anchor=(0,0), html=div('Start'))
        icon_end = DivIcon(icon_size=(36,36), icon_anchor=(0,0), html=div('End'))
        folium.Marker(location=points[0], icon=icon_start).add_to(self._map)
        folium.Marker(location=points[-1], icon = icon_end).add_to(self._map)
        self._map.fit_bounds([min(points), max(points)])
        
        data = io.BytesIO()
        self._map.save(data, close_file=False)

        self._web_viewer = qtweb.QWebEngineView()
        self._web_viewer.setHtml(data.getvalue().decode())
        self._web_viewer.resize(800, 640)
        self._web_viewer.show()
