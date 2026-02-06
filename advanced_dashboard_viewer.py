from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from grade_detailed_dashboard import GradeDetailedDashboard
from speed_detailed_dashboard import SpeedDetailedDashboard
from pandas import DataFrame

"""
Window to hold advanced dashboards about the speed and grade data. 
"""
class AdvancedDashboardViewer(QWidget):
    def __init__(self, data_frame: DataFrame):
        """
        Class constructor
        
        :param data_frame: Dataframe containing the data to be used on class object initialization.
        :type data_frame: pandas.DataFrame
        """
        super().__init__()
        layout = QVBoxLayout(self)
        self._redraw = False

        tab_widget = QTabWidget()
        tab_widget.addTab(GradeDetailedDashboard(data_frame), "Grade")
        tab_widget.addTab(SpeedDetailedDashboard(data_frame), "Speed")

        layout.addWidget(tab_widget)
        
        self.resize(1024, 900)

