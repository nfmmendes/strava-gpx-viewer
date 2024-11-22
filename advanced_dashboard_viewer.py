from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from grade_detailed_dashboard import GradeDetailedDashboard
from speed_detailed_dashboard import SpeedDetailedDashboard

"""
Window to hold advanced dashboards about the speed and grade data. 
"""
class AdvancedDashboardViewer(QWidget):
    def __init__(self, data_frame):
        super().__init__()
        layout = QVBoxLayout(self)
        self._redraw = False

        tab_widget = QTabWidget()
        tab_widget.addTab(GradeDetailedDashboard(data_frame), "Grade")
        tab_widget.addTab(SpeedDetailedDashboard(data_frame), "Speed")

        layout.addWidget(tab_widget)
        
        self.resize(1024, 900)

